"""Record actual local MAF runs for static replay; never invent traces."""

import argparse
import asyncio
import json
from pathlib import Path

from backend.app.generator import SCENARIOS, generate
from backend.app.workflow import run_workflow


async def record(args):
    root = Path(__file__).resolve().parents[1] / "demos"
    root.mkdir(exist_ok=True)
    for sid in [args.scenario] if args.scenario else [s[0] for s in SCENARIOS]:
        result = await run_workflow(generate(sid), args.at_ms, provider="local", inject_failure=args.failure)
        suffix = "local-recovery" if args.failure else "local-agent-run"
        (root / f"{sid}-{suffix}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            sid,
            result["execution_mode"],
            result["duration_ms"],
            [(t["agent"], t["mode"]) for t in result["traces"]],
            flush=True,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=[s[0] for s in SCENARIOS])
    parser.add_argument("--at-ms", type=int, default=4_200_000)
    parser.add_argument("--failure", action="store_true")
    asyncio.run(record(parser.parse_args()))


if __name__ == "__main__":
    main()
