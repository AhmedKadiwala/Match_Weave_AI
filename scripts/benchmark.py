"""Measured local CPU timings, evidence quality and a transparent fault-injection comparison."""
import asyncio
import json
import platform
import statistics
import time
from pathlib import Path
from backend.app.analytics import build_claims, state_at, verify_claim
from backend.app.generator import generate_all
from backend.app.publishing import publish
from backend.app.workflow import run_workflow


async def main():
    timings = []
    rows = []
    for match in generate_all():
        for minute in range(5, 91, 5):
            start = time.perf_counter()
            state = state_at(match, minute*60_000)
            claims = build_claims(match, minute*60_000)
            if claims:
                assert verify_claim(match, claims[0], minute*60_000)[0]
                publish(match, claims[0], "analyst", "en")
            timings.append((time.perf_counter()-start)*1000)
            assert state["event_count"] <= len(match.events)
        # Deterministic baseline: one editorial selection, no verification.
        start = time.perf_counter()
        claim = build_claims(match, 4_200_000)[0]
        baseline_ms = (time.perf_counter()-start)*1000
        corrupted = claim.model_copy(update={"value":claim.value+99})
        full = await run_workflow(match, 4_200_000, inject_failure=True)
        rows.append({"match_id":match.id, "baseline_ms":round(baseline_ms, 3), "workflow_ms":full["duration_ms"],
                     "clean_baseline_correct":verify_claim(match, claim, 4_200_000)[0],
                     "fault_baseline_correct":verify_claim(match, corrupted, 4_200_000)[0],
                     "verified_workflow_correct":verify_claim(match, __import__('backend.app.models', fromlist=['Claim']).Claim.model_validate(full['published']['claim']), 4_200_000)[0],
                     "repairs":full["repairs"], "baseline_persona_language_variants":1, "workflow_variants":len(full["variants"])})
    report = {"hardware":"Intel CPU / 16 GB RAM / Windows; Foundry Qwen CPU timings reported separately", "platform":platform.platform(),
              "python":platform.python_version(), "measurements":len(timings), "deterministic_state_claim_overlay_ms":{
                  "p50":round(statistics.median(timings), 3), "p95":round(sorted(timings)[int(.95*(len(timings)-1))], 3), "max":round(max(timings), 3)},
              "comparison_type":"Controlled deterministic ablation, not evidence of LLM superiority. Same injected +99 count fault. Clean baseline may already be correct.", "comparison":rows}
    Path("docs/reports").mkdir(parents=True, exist_ok=True)
    Path("docs/reports/benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
