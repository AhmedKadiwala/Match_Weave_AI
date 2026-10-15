"""Actual single-local-agent comparison against recorded multi-agent runs. No invented gains."""

import asyncio
import json
import os
import statistics
import time
from pathlib import Path

from agent_framework.openai import OpenAIChatCompletionClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from backend.app.analytics import build_claims, verify_claim
from backend.app.generator import generate_all
from backend.app.models import Claim
from backend.app.workflow import local_url


class BaselineReply(BaseModel):
    candidate_index: int = Field(ge=0, le=99)
    claimed_value: int
    source_event_ids: list[str]
    sentence: str


async def main():
    root = Path(__file__).resolve().parents[1]
    rows = []
    async with AsyncOpenAI(
        base_url=local_url(os.getenv("MATCHWEAVE_LOCAL_URL", "http://127.0.0.1:5273/v1")),
        api_key="local-no-key",
        timeout=45,
        max_retries=0,
    ) as sdk:
        client = OpenAIChatCompletionClient(
            model=os.getenv("MATCHWEAVE_MODEL", "qwen2.5-1.5b-instruct-generic-cpu:4"), async_client=sdk
        )
        for match in generate_all():
            claims = build_claims(match, 4_200_000)
            candidates = [
                {
                    "candidate_index": i,
                    "team": c.team_id,
                    "metric": c.metric,
                    "value": c.value,
                    "source_event_ids": c.source_event_ids,
                }
                for i, c in enumerate(claims)
            ]
            agent = client.as_agent(
                name="single_agent_baseline",
                instructions='Write a short analyst story for this synthetic football moment. Choose ONE supplied candidate and copy its value and evidence IDs exactly. Output ONLY a JSON object with exactly these fields: {"candidate_index":0,"claimed_value":1,"source_event_ids":["event-id"],"sentence":"Your short story"}. Replace the example values with the supplied candidate facts. Do not output a plain string or other fields.',
                default_options={"temperature": 0, "max_tokens": 900, "response_format": BaselineReply},
            )
            start = time.perf_counter()
            correct = False
            coverage = 0
            error = None
            raw = ""
            try:
                response = await asyncio.wait_for(
                    agent.run(json.dumps({"candidates": candidates})), timeout=60
                )
                raw = response.text
                result = BaselineReply.model_validate_json(raw)
                if result.candidate_index < len(claims):
                    selected = claims[result.candidate_index].model_copy(
                        update={"value": result.claimed_value, "source_event_ids": result.source_event_ids}
                    )
                    correct = verify_claim(match, selected, 4_200_000)[0]
                    coverage = len(
                        set(result.source_event_ids) & set(claims[result.candidate_index].source_event_ids)
                    ) / len(claims[result.candidate_index].source_event_ids)
            except Exception as exc:  # noqa: BLE001 - retain actual evaluation failure
                error = f"{type(exc).__name__}: {str(exc)[:200]}"
            elapsed = (time.perf_counter() - start) * 1000
            multi = json.loads(
                (root / "demos" / f"{match.id}-local-agent-run.json").read_text(encoding="utf-8")
            )
            multi_correct = verify_claim(match, Claim.model_validate(multi["published"]["claim"]), 4_200_000)[
                0
            ]
            rows.append(
                {
                    "match_id": match.id,
                    "single_agent_ms": round(elapsed, 3),
                    "single_structured_claim_correct": correct,
                    "single_evidence_coverage": coverage,
                    "single_raw_output": raw,
                    "single_error": error,
                    "multi_agent_ms": multi["duration_ms"],
                    "multi_structured_claim_correct": multi_correct,
                    "multi_evidence_coverage": 1 if multi_correct else 0,
                    "single_variants": 1,
                    "multi_variants": len(multi["variants"]),
                    "multi_successful_model_stages": sum(t["mode"] == "local-llm" for t in multi["traces"]),
                }
            )
            print(match.id, correct, round(elapsed), multi_correct, flush=True)
    report = {
        "model": os.getenv("MATCHWEAVE_MODEL", "qwen2.5-1.5b-instruct-generic-cpu:4"),
        "sample_size": len(rows),
        "scope": "Same five scenarios at 70:00, same canonical claims as source. Basic single local MAF agent versus recorded five-specialist local MAF workflow. No statistical significance or general quality claim. Free-form baseline sentences are unverified and never published. Only structured numerical claims and exact evidence sets are scored. Multi-agent output deliberately uses constrained templates; this evaluates the complete product/gate, not agent count in isolation.",
        "single_correct": sum(r["single_structured_claim_correct"] for r in rows),
        "multi_correct": sum(r["multi_structured_claim_correct"] for r in rows),
        "single_median_ms": round(statistics.median(r["single_agent_ms"] for r in rows), 3),
        "multi_median_ms": round(statistics.median(r["multi_agent_ms"] for r in rows), 3),
        "rows": rows,
    }
    (root / "docs/reports/model-comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
