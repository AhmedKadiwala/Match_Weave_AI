"""Optional one-time local model download + loopback Foundry service. No cloud inference."""
import argparse
import json
import time
from pathlib import Path
from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-0.5b")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--download-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]/"runtime"/"foundry"
    root.mkdir(parents=True, exist_ok=True)
    config = Configuration(app_name="matchweave-ai", app_data_dir=str(root), disable_nonessential_telemetry=True,
                           web=Configuration.WebService(urls="http://127.0.0.1:5273"))
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    catalog = manager.get_catalog()
    if args.list:
        print(catalog.list_models(), flush=True)
        return
    model = catalog.get_model(args.model)
    if model is None:
        raise RuntimeError("Model not found in catalog; run --list")
    print("Downloading local model if not cached:", args.model, flush=True)
    progress = [-1]
    def report(percent):
        decile = int(percent)//10
        if decile != progress[0]:
            progress[0] = decile
            print(f"Model download {percent:.0f}%", flush=True)
    model.download(report)
    if args.download_only:
        print("Local model cached.", flush=True)
        return
    model.load()
    manager.start_web_service()
    info = {"provider": "foundry-local", "model": args.model, "urls": manager.urls}
    (root/"service.json").write_text(json.dumps(info), encoding="utf-8")
    print(json.dumps(info), flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_web_service()
        model.unload()


if __name__ == "__main__":
    main()
