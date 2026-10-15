"""Generate the browser replay from actual backend state and Microsoft workflow executions."""

import asyncio
import json
from pathlib import Path

from backend.app.analytics import state_at
from backend.app.generator import generate_all
from backend.app.workflow import run_workflow

ROOT = Path(__file__).resolve().parents[1]


async def main():
    output = ROOT / "frontend" / "public" / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    index = []
    for match in generate_all():
        snapshots = [state_at(match, minute * 60_000) for minute in range(91)]
        runs = []
        for minute in range(5, 91, 5):
            for favorite in (None, "harbor", "vale"):
                run = await run_workflow(match, minute * 60_000, favorite_team=favorite)
                run["recording_label"] = "Recorded deterministic workflow · no LLM inference"
                runs.append(run)
        recorded = ROOT / "demos" / f"{match.id}-local-agent-run.json"
        if recorded.exists():
            run = json.loads(recorded.read_text(encoding="utf-8"))
            run["recording_label"] = "Recorded Agent Run · local model; inspect per-agent fallbacks"
            runs = [r for r in runs if not (r["at_ms"] == run["at_ms"] and r["favorite_team"] is None)] + [
                run
            ]
        recovery = await run_workflow(match, 4_200_000, inject_failure=True)
        recovery_source = ROOT / "demos" / f"{match.id}-local-recovery.json"
        if recovery_source.exists():
            recovery = json.loads(recovery_source.read_text(encoding="utf-8"))
            recovery["recording_label"] = "Recorded Agent Run · injected count fault, source repair and re-verification"
        artifact = {
            "match": match.model_dump(mode="json"),
            "snapshots": snapshots,
            "runs": runs,
            "recovery_run": recovery,
            "generated_by": "python -m scripts.build_demo",
            "artifact_version": 1,
        }
        (output / f"{match.id}.json").write_text(
            json.dumps(artifact, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        meta = match.model_dump(mode="json", exclude={"events"})
        meta["event_count"] = len(match.events)
        index.append(meta)
        print(
            f"{match.id}: {len(match.events)} events, {len(snapshots)} snapshots, {len(runs)} real workflow records",
            flush=True,
        )
    (output / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    comparison = ROOT / "docs/reports/model-comparison.json"
    if comparison.exists():
        (output / "comparison.json").write_text(comparison.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
