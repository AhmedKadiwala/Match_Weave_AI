"""Real historical results and trained-model inference; 2026/27 is excluded by contract."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from .history import COMPETITIONS
from .result_model import FEATURES, OUTCOMES, predict

ROOT = Path(__file__).resolve().parents[2]
router = APIRouter(prefix="/api/history", tags=["Real historical results"])
Season = Literal["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
Competition = Literal["en.1", "es.1", "de.1", "it.1", "fr.1", "uefa.cl", "uefa.el", "uefa.conf"]


@lru_cache(maxsize=12)
def load(relative):
    source = ROOT / relative
    if not source.is_file():
        raise HTTPException(
            503, "Historical artifacts unavailable; run the documented fetch/train commands before upload."
        )
    return json.loads(source.read_text(encoding="utf-8"))


@router.get("/summary")
def summary():
    return load("frontend/public/history/summary.json")


@router.get("/matches")
def matches(
    competition: Competition = "en.1",
    season: Season = "2025-26",
    club: str = Query("", max_length=100),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0, le=20000),
):
    rows = [
        row
        for row in load(f"frontend/public/history/{competition}.json")
        if row["season"] == season
        and (not club or club.casefold() in (row["home"] + " " + row["away"]).casefold())
    ]
    return {
        "total": len(rows),
        "competition": competition,
        "season": season,
        "matches": rows[offset : offset + limit],
        "data_kind": "real-match-results",
        "excluded_season": "2026-27",
    }


@router.get("/prediction/{match_id}")
def prediction(match_id: str, model: Literal["evaluation", "all-data"] = "evaluation"):
    for code in COMPETITIONS:
        row = next((r for r in load(f"frontend/public/history/{code}.json") if r["id"] == match_id), None)
        if row:
            if row.get("cancelled"):
                raise HTTPException(409, "Cancelled fixtures are not scored or modeled as played matches.")
            weights = load(
                "models/historical-result-evaluation.json"
                if model == "evaluation"
                else "models/historical-result-model.json"
            )
            values = [row["features"][name] for name in FEATURES]
            probabilities = predict(values, weights)
            return {
                "match_id": match_id,
                "probabilities": dict(zip(OUTCOMES, probabilities)),
                "model": weights["name"],
                "model_variant": model,
                "feature_cutoff": row["feature_cutoff"],
                "evaluation": row["evaluation"]
                if model == "evaluation"
                else "all-data refit — retrospective in-sample estimate, not held-out performance",
                "source_url": row["source_url"],
                "live_feed": False,
            }
    raise HTTPException(404, "Unknown historical match")
