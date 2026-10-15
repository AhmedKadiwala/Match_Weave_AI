"""Loopback API: bounded ingestion, SSE replay, actual Microsoft agent runs."""

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .analytics import state_at
from .generator import SCENARIOS, generate
from .models import Event, Match
from .store import Store
from .workflow import run_workflow

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(
    title="MatchWeave AI",
    version="1.0.0",
    description="Synthetic replay and evidence-verified local AI. No paid APIs.",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver", "[::1]"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:4173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
log = logging.getLogger("matchweave")
requests_by_ip = defaultdict(deque)
model_slots = asyncio.Semaphore(1)


@lru_cache(maxsize=1)
def store():
    return Store(Path(os.getenv("MATCHWEAVE_DB", str(ROOT / "runtime" / "matchweave.db"))))


@lru_cache(maxsize=5)
def match_by_id(match_id: str) -> Match:
    if match_id not in {s[0] for s in SCENARIOS}:
        raise HTTPException(404, "Unknown synthetic match")
    source = ROOT / "datasets" / "synthetic" / f"{match_id}.json"
    return (
        Match.model_validate_json(source.read_text(encoding="utf-8"))
        if source.exists()
        else generate(match_id)
    )


@app.middleware("http")
async def limits(request: Request, call_next):
    key = request.client.host if request.client else "local"
    now = time.monotonic()
    recent = requests_by_ip[key]
    while recent and recent[0] < now - 60:
        recent.popleft()
    if len(recent) >= 240:
        return JSONResponse({"detail": "Request limit reached; retry in one minute"}, 429)
    recent.append(now)
    if request.method == "POST" and len(await request.body()) > 1_000_000:
        return JSONResponse({"detail": "Body exceeds 1 MB"}, 413)
    try:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response
    except Exception:
        log.exception("request failed")
        return JSONResponse({"detail": "Internal processing error; inspect local server logs"}, 500)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "cost_mode": "local-only",
        "framework": "Microsoft Agent Framework 1.22.0",
        "inference": "optional local Foundry / Ollama",
    }


@app.get("/api/matches")
def matches():
    return [
        {k: v for k, v in match_by_id(s[0]).model_dump(mode="json").items() if k != "events"}
        for s in SCENARIOS
    ]


@app.get("/api/matches/{match_id}")
def get_match(match_id: str):
    return match_by_id(match_id)


@app.get("/api/matches/{match_id}/state")
def state(match_id: str, at_ms: int = Query(default=4_200_000, ge=0, le=5_400_000)):
    return state_at(match_by_id(match_id), at_ms)


class IngestRequest(BaseModel):
    events: list[Event] = Field(min_length=1, max_length=500)


@app.post("/api/matches/{match_id}/ingest")
def ingest(match_id: str, body: IngestRequest):
    try:
        return store().ingest(match_by_id(match_id), body.events)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/api/matches/{match_id}/ingested-state")
def ingested_state(match_id: str):
    source = match_by_id(match_id)
    events = store().events(match_id)
    return state_at(source.model_copy(update={"events": events}), events[-1].match_clock_ms if events else 0)


class AnalyzeRequest(BaseModel):
    at_ms: int = Field(default=4_200_000, ge=0, le=5_400_000)
    provider: Literal["deterministic", "local"] = "deterministic"
    audience: Literal["fan", "analyst", "broadcaster"] = "analyst"
    language: Literal["en", "hi", "es"] = "en"
    favorite_team: Literal["harbor", "vale"] | None = None
    inject_failure: bool = False
    source: Literal["replay", "ingested"] = "replay"


@app.post("/api/matches/{match_id}/analyze")
async def analyze(match_id: str, body: AnalyzeRequest):
    match = match_by_id(match_id)
    if body.source == "ingested":
        match = match.model_copy(update={"events": store().events(match_id)})
    kwargs = body.model_dump(exclude={"source", "at_ms"})
    if model_slots.locked():
        raise HTTPException(429, "An analysis is running; retry shortly")
    async with model_slots:
        try:
            run = await asyncio.wait_for(run_workflow(match, body.at_ms, **kwargs), timeout=180)
        except TimeoutError as exc:
            raise HTTPException(504, "Workflow timed out; use deterministic mode or a smaller model") from exc
    store().save_run(run)
    return run


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    result = store().get_run(run_id)
    if result is None:
        raise HTTPException(404, "Unknown workflow run")
    return result


@app.get("/api/matches/{match_id}/stream")
async def stream(
    match_id: str, request: Request, speed: float = Query(120, ge=1, le=10_000), after: int = Query(-1, ge=-1)
):
    match = match_by_id(match_id)

    async def replay():
        previous = 0
        for e in match.events:
            if e.sequence_number <= after:
                previous = e.match_clock_ms
                continue
            if await request.is_disconnected():
                break
            await asyncio.sleep(min(10, max(0, (e.match_clock_ms - previous) / 1000 / speed)))
            previous = e.match_clock_ms
            yield f"id: {e.sequence_number}\nevent: match_event\ndata: {e.model_dump_json()}\n\n"
        yield "event: complete\ndata: {}\n\n"

    return StreamingResponse(replay(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"})
