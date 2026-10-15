"""Real Microsoft Agent Framework graph with model-backed agents and a fail-closed proof gate.

Deterministic mode executes the same Microsoft workflow but is explicitly NOT LLM inference.
Model agents make bounded editorial selections; arithmetic and publication remain reproducible.
"""

import asyncio
import json
import os
import time
import uuid
from typing import Literal
from urllib.parse import urlparse

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from pydantic import BaseModel, ConfigDict, Field

from .analytics import build_claims, metric_events, verify_claim
from .models import Claim, Match
from .publishing import publish
from .tools import metric_tool


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice: int = Field(ge=0, le=99)
    note: str = Field(max_length=800)


class Packet(BaseModel):
    match: Match
    at_ms: int
    audience: Literal["fan", "analyst", "broadcaster"] = "analyst"
    language: Literal["en", "hi", "es"] = "en"
    favorite_team: str | None = None
    provider: Literal["deterministic", "local"] = "deterministic"
    candidates: list[Claim] = Field(default_factory=list)
    selected: Claim | None = None
    verified: bool = False
    repairs: int = 0
    inject_failure: bool = False
    traces: list[dict] = Field(default_factory=list)


PROMPTS = {
    "match_analyst": "You are the Match Analyst. Choose the most useful numerical claim, preferring shots or score changes. Use metric_lookup if helpful. Never compute your own facts. Return JSON {choice: zero-based index, note: short explanation}.",
    "tactical_analyst": "You are the Tactical Intelligence specialist. Prefer evidence of a pressure/recovery change, with at least five observations. Avoid causal assertions. Choose from supplied candidates only. Return JSON {choice: index, note: short uncertainty-aware explanation}.",
    "narrative": "You are the Narrative editor. Select one claim for a concise football story matching the audience. Prefer a meaningful recent change over routine passing. Return JSON {choice: index, note: short editorial reason}. Do not invent events.",
    "fact_checker": "You are the independent Fact Checker. The supplied tool recount is authoritative. Choice 0 means accept, 1 means reject. Return JSON {choice: 0 or 1, note: short verification reason}. Never accept a failed recount.",
    "publisher": "You are the Personalization and Publishing specialist. Select layout: 0=lower third for fans/broadcast, 1=stat card for analysts, 2=score bug for goals. Return JSON {choice: 0,1,2, note: short audience-specific reason}. Verified facts must stay unchanged.",
}


def local_url(url: str) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("localhost", "127.0.0.1", "::1")
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Only local HTTP inference is allowed; remote/paid endpoints are disabled")
    return url


async def decide(role: str, payload: dict, packet: Packet) -> tuple[Decision | None, dict]:
    if packet.provider == "deterministic":
        return None, {"mode": "deterministic", "status": "completed", "attempts": 0}
    from agent_framework.openai import OpenAIChatCompletionClient
    from openai import AsyncOpenAI

    endpoint = local_url(os.getenv("MATCHWEAVE_LOCAL_URL", "http://127.0.0.1:5273/v1"))
    timeout = min(120, max(1, float(os.getenv("MATCHWEAVE_TIMEOUT", "45"))))
    model = os.getenv("MATCHWEAVE_MODEL", "qwen2.5-1.5b-instruct-generic-cpu:4")
    tools_called = []

    def metric_lookup(team_id: str, metric: str) -> str:
        """Recount one allowed football metric from validated, event-time-bounded source events."""
        if metric not in {
            "goals",
            "shots",
            "recoveries",
            "pressure",
            "passes_completed",
            "final_third_entries",
        }:
            return "Unsupported metric"
        bounded = [e for e in packet.match.events if e.match_clock_ms <= packet.at_ms]
        evidence = metric_events(bounded, team_id, metric)
        tools_called.append({"team_id": team_id, "metric": metric, "count": len(evidence)})
        return json.dumps({"count": len(evidence), "event_ids": [e.event_id for e in evidence]})

    errors = []
    async with AsyncOpenAI(base_url=endpoint, api_key="local-no-key", timeout=timeout, max_retries=0) as sdk:
        client = OpenAIChatCompletionClient(async_client=sdk, model=model)
        agent = client.as_agent(
            name=role,
            instructions=PROMPTS[role],
            tools=[metric_lookup] if role == "match_analyst" else [],
            default_options={
                "temperature": 0,
                "max_tokens": 160,
                **({"response_format": Decision} if role != "match_analyst" else {}),
            },
        )
        for attempt in range(2):
            try:
                response = await asyncio.wait_for(
                    agent.run(
                        json.dumps(payload, ensure_ascii=False)
                        + '\nOutput ONLY a JSON object. Example: {"choice":0,"note":"Evidence supports this choice"}'
                    ),
                    timeout=timeout,
                )
                raw = response.text
                # Accommodate fenced JSON without accepting arbitrary prefixes or executable text.
                raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                decision = Decision.model_validate_json(raw)
                return decision, {
                    "mode": "local-llm",
                    "model": model,
                    "status": "completed",
                    "attempts": attempt + 1,
                    "raw_output": raw,
                    "tool_calls": tools_called,
                    "errors": errors,
                }
            except Exception as exc:  # noqa: BLE001 - isolate provider/schema failures and record fallback
                errors.append(f"{type(exc).__name__}: {str(exc)[:180]}")
    return None, {
        "mode": "deterministic-fallback",
        "model": model,
        "status": "fallback",
        "attempts": 2,
        "errors": errors,
        "tool_calls": tools_called,
    }


def trace(
    packet: Packet, role: str, start: float, summary: str, result: dict, evidence=None, validation="pending"
):
    packet.traces.append(
        {
            "agent": role,
            "task": PROMPTS.get(role, "Deterministic evidence reconciliation"),
            "input_summary": f"{packet.match.id} @ {packet.at_ms} ms; {len(packet.candidates)} candidate claims; {packet.audience}/{packet.language}",
            "output_summary": summary,
            "duration_ms": round((time.perf_counter() - start) * 1000, 3),
            "source_event_ids": evidence or [],
            "validation": validation,
            **result,
        }
    )


def candidate_payload(claims: list[Claim]):
    return [
        {
            "index": i,
            "team": c.team_id,
            "metric": c.metric,
            "value": c.value,
            "previous": c.previous_value,
            "confidence": c.confidence,
            "delta": c.value - c.previous_value,
        }
        for i, c in enumerate(claims)
    ]


class Start(Executor):
    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet]):
        data.candidates = build_claims(data.match, data.at_ms)
        await ctx.send_message(data)


class Analysis(Executor):
    def __init__(self, role):
        super().__init__(id=role)
        self.role = role

    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet]):
        data = data.model_copy(deep=True)
        start = time.perf_counter()
        if self.role == "match_analyst":
            relevant = [c for c in data.candidates if c.metric in ("goals", "shots", "passes_completed")]
        else:
            relevant = [
                c for c in data.candidates if c.metric in ("pressure", "recoveries", "final_third_entries")
            ]
        relevant = sorted(
            relevant, key=lambda c: (c.metric != "passes_completed", c.value - c.previous_value), reverse=True
        )
        decision, detail = await decide(self.role, {"candidates": candidate_payload(relevant)}, data)
        calculator = metric_tool(data.match, data.at_ms)
        scheduled = []
        for claim in relevant[:3]:
            args = {
                "team_id": claim.team_id,
                "metric": claim.metric,
                "start_ms": claim.window_start_ms,
                "end_ms": claim.window_end_ms,
            }
            tool_start = time.perf_counter()
            result = await calculator.invoke(arguments=args, skip_parsing=True)
            if result["count"] != claim.value:
                raise ValueError("Metric tool disagreed with source claim")
            scheduled.append(
                {
                    "name": "calculate_metric",
                    "origin": "executor-scheduled Microsoft FunctionTool",
                    "arguments": args,
                    "count": result["count"],
                    "evidence_count": len(result["source_event_ids"]),
                    "duration_ms": round((time.perf_counter() - tool_start) * 1000, 3),
                }
            )
        detail["scheduled_tools"] = scheduled
        idx = decision.choice if decision and decision.choice < len(relevant) else 0
        data.candidates = (
            ([relevant[idx]] + [c for i, c in enumerate(relevant) if i != idx])[:3] if relevant else []
        )
        trace(
            data,
            self.role,
            start,
            f"Ranked {len(data.candidates)} evidence-linked claims",
            detail,
            data.candidates[0].source_event_ids if data.candidates else [],
            "bounded source metrics",
        )
        await ctx.send_message(data)


class Reconcile(Executor):
    @handler
    async def process(self, packets: list[Packet], ctx: WorkflowContext[Packet]):
        data = packets[0].model_copy(deep=True)
        data.candidates = list({c.claim_id: c for p in packets for c in p.candidates}.values())
        data.traces = [t for p in packets for t in p.traces]
        await ctx.send_message(data)


class Narrative(Executor):
    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet]):
        start = time.perf_counter()
        favored = [
            c for c in data.candidates if not data.favorite_team or c.team_id == data.favorite_team
        ] or data.candidates
        # Prefer newly observed changes; never turn weak samples into causal assertions.
        favored.sort(
            key=lambda c: (
                c.metric in ("pressure", "recoveries") and c.value >= 5 and c.value > c.previous_value,
                c.metric == "goals",
                c.value - c.previous_value,
            ),
            reverse=True,
        )
        decision, detail = await decide(
            "narrative",
            {"audience": data.audience, "language": data.language, "candidates": candidate_payload(favored)},
            data,
        )
        if favored:
            data.selected = favored[decision.choice if decision and decision.choice < len(favored) else 0]
            if data.inject_failure:
                data.selected = data.selected.model_copy(update={"value": data.selected.value + 99})
        trace(
            data,
            "narrative",
            start,
            f"Selected {data.selected.claim_id if data.selected else 'no supported story'}",
            detail,
            data.selected.source_event_ids if data.selected else [],
        )
        await ctx.send_message(data)


class Verify(Executor):
    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet]):
        start = time.perf_counter()
        valid, reason = (
            verify_claim(data.match, data.selected, data.at_ms)
            if data.selected
            else (False, "no supported claim")
        )
        decision, detail = await decide(
            "fact_checker",
            {
                "independent_recount_passed": valid,
                "reason": reason,
                "claim": data.selected.model_dump() if data.selected else None,
            },
            data,
        )
        # A model cannot overrule failed source verification. False model rejection falls back to the proof.
        data.verified = valid
        if decision and decision.choice != (0 if valid else 1):
            detail["advisory_disagreement"] = "Deterministic source recount takes precedence"
        trace(
            data,
            "fact_checker",
            start,
            reason,
            detail,
            data.selected.source_event_ids if data.selected else [],
            "passed" if valid else "rejected",
        )
        await ctx.send_message(data)


class Repair(Executor):
    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet]):
        start = time.perf_counter()
        correct = next(
            (
                c
                for c in build_claims(data.match, data.at_ms)
                if data.selected and c.claim_id == data.selected.claim_id
            ),
            None,
        )
        data.selected = correct
        data.repairs += 1
        trace(
            data,
            "evidence_repair",
            start,
            "Replaced rejected claim from canonical source events",
            {"mode": "deterministic", "status": "corrected", "attempts": 1},
            correct.source_event_ids if correct else [],
            "reverify required",
        )
        await ctx.send_message(data)


class Publisher(Executor):
    @handler
    async def process(self, data: Packet, ctx: WorkflowContext[Packet, dict]):
        start = time.perf_counter()
        if not data.selected or not data.verified:
            await ctx.yield_output(
                {
                    "published": None,
                    "variants": [],
                    "traces": data.traces,
                    "repairs": data.repairs,
                    "status": "withheld",
                }
            )
            return
        decision, detail = await decide(
            "publisher",
            {"audience": data.audience, "language": data.language, "metric": data.selected.metric},
            data,
        )
        layouts = ["lower_third", "stat_card", "score_bug"]
        layout = (
            layouts[decision.choice]
            if decision and decision.choice < 3
            else ("stat_card" if data.audience == "analyst" else "lower_third")
        )
        variants = [
            publish(data.match, data.selected, a, lang, layout)
            for a in ("fan", "analyst", "broadcaster")
            for lang in ("en", "hi", "es")
        ]
        selected = next(
            v for v in variants if v["audience"] == data.audience and v["language"] == data.language
        )
        trace(
            data,
            "publisher",
            start,
            f"Published 9 fact-consistent persona/language variants; {layout}",
            detail,
            data.selected.source_event_ids,
            "verified before publication",
        )
        await ctx.yield_output(
            {
                "published": selected,
                "variants": variants,
                "traces": data.traces,
                "repairs": data.repairs,
                "status": "published",
            }
        )


def create_workflow():
    start = Start(id="validated_context")
    analyst, tactic = Analysis("match_analyst"), Analysis("tactical_analyst")
    reconcile, narrative = Reconcile(id="evidence_reconciliation"), Narrative(id="narrative")
    verify, repair, publisher = (
        Verify(id="fact_checker"),
        Repair(id="evidence_repair"),
        Publisher(id="publisher"),
    )
    return (
        WorkflowBuilder(
            start_executor=start,
            max_iterations=20,
            name="MatchWeave evidence workflow",
            output_from=[publisher],
        )
        .add_fan_out_edges(start, [analyst, tactic])
        .add_fan_in_edges([analyst, tactic], reconcile)
        .add_edge(reconcile, narrative)
        .add_edge(narrative, verify)
        .add_edge(verify, publisher, condition=lambda d: d.verified or not d.selected or d.repairs >= 1)
        .add_edge(
            verify, repair, condition=lambda d: not d.verified and d.selected is not None and d.repairs < 1
        )
        .add_edge(repair, verify)
        .build()
    )


async def run_workflow(
    match: Match,
    at_ms: int,
    *,
    provider="deterministic",
    audience="analyst",
    language="en",
    favorite_team=None,
    inject_failure=False,
) -> dict:
    start = time.perf_counter()
    packet = Packet(
        match=match,
        at_ms=at_ms,
        provider=provider,
        audience=audience,
        language=language,
        favorite_team=favorite_team,
        inject_failure=inject_failure,
    )
    events = await create_workflow().run(packet)
    outputs = events.get_outputs()
    if not outputs:
        raise RuntimeError("Workflow completed without a publication decision")
    output = outputs[-1]
    return {
        "run_id": uuid.uuid4().hex,
        "match_id": match.id,
        "at_ms": at_ms,
        "framework": "Microsoft Agent Framework 1.22.0",
        "provider_requested": provider,
        "favorite_team": favorite_team,
        "execution_mode": "local-llm"
        if any(t["mode"] == "local-llm" for t in output["traces"])
        else "deterministic",
        "duration_ms": round((time.perf_counter() - start) * 1000, 3),
        **output,
    }
