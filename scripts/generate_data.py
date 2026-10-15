"""Run from repository root: python -m scripts.generate_data [--density 1]."""
import argparse
import json
from pathlib import Path
from backend.app.generator import generate_all
from backend.app.store import validate_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--density", type=float, default=1)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]/"datasets"/"synthetic"
    root.mkdir(parents=True, exist_ok=True)
    manifest = []
    for match in generate_all(args.density):
        validate_events(match, match.events)
        (root/f"{match.id}.json").write_text(match.model_dump_json(), encoding="utf-8")
        (root/f"{match.id}.ndjson").write_text("\n".join(e.model_dump_json() for e in match.events), encoding="utf-8")
        manifest.append({"id": match.id, "title": match.title, "seed": match.seed, "events": len(match.events)})
    (root/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
