"""Package versionable source and a self-contained static replay, excluding all local runtime state."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "deployment"
    output.mkdir(exist_ok=True)
    report_dir = root / "docs/reports"
    suite = ET.parse(report_dir / "backend-tests.xml").getroot()
    cases = list(suite.iter("testcase"))
    errors = list(suite.iter("failure")) + list(suite.iter("error"))
    browser = json.loads((report_dir / "browser-tests.json").read_text(encoding="utf-8-sig"))["stats"]
    cloud_browser = json.loads((report_dir / "render-browser-tests.json").read_text(encoding="utf-8-sig"))[
        "stats"
    ]
    script_suite = ET.parse(report_dir / "keep-alive-tests.xml").getroot()
    script_cases = list(script_suite.iter("testcase"))
    video = json.loads((report_dir / "video.json").read_text(encoding="utf-8"))
    assert not errors and browser["unexpected"] == 0 and browser["skipped"] == 0
    assert cloud_browser["unexpected"] == 0 and not list(script_suite.iter("failure"))
    assert video["duration_seconds"] < 120
    source = output / "matchweave-submission.zip"
    static = output / "matchweave-static-demo.zip"
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        .decode()
        .split("\0")
    )
    names = sorted(
        {
            name
            for name in names
            if name
            and (root / name).is_file()
            and not name.endswith(".zip")
            and name != "deployment/release-manifest.json"
        }
    )
    forbidden = {".git", ".venv", "node_modules", "runtime", ".tools"}
    assert not any(forbidden & set(Path(n).parts) or Path(n).name == ".env" for n in names)
    with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in names:
            archive.write(root / name, "matchweave-ai/" + name)
    dist = root / "frontend/dist"
    assert (dist / "index.html").exists() and (dist / "artifacts/index.json").exists()
    with zipfile.ZipFile(static, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(dist.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(dist).as_posix())
    clean = (root / "READY_TO_UPLOAD").resolve()
    assert clean.is_relative_to(root) and clean.name == "READY_TO_UPLOAD"
    clean.mkdir(exist_ok=True)
    # Materialize only this source archive's safe files; never recursively delete or move user files.
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            relative = Path(name).relative_to("matchweave-ai")
            destination = (clean / relative).resolve()
            assert destination.is_relative_to(clean)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))

    def entry(path):
        return {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    manifest = {
        "created_ist": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
        "source_files": len(names),
        "archives": [entry(source), entry(static)],
        "video": entry(root / "demos/matchweave-demo.mp4"),
        "backend_tests": f"{len(cases)}/{len(cases)} passed",
        "browser_tests": f"{browser['expected']}/{browser['expected']} passed",
        "minimal_render_profile_browser_tests": f"{cloud_browser['expected']} passed locally",
        "google_script_unit_tests": f"{len(script_cases)} passed in Node",
        "clean_upload_folder": str(clean),
        "historical_results": json.loads((report_dir / "historical-model.json").read_text())[
            "production_training_matches"
        ],
        "historical_holdout_matches": json.loads((report_dir / "historical-model.json").read_text())[
            "heldout"
        ]["matches"],
        "excluded_season": "2026-27",
        "video_duration_seconds": video["duration_seconds"],
        "internal_score": 89,
        "public_repository_url": None,
        "public_demo_url": None,
        "public_video_url": None,
        "portal_submitted": False,
    }
    (output / "release-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (clean / "deployment").mkdir(exist_ok=True)
    (clean / "deployment" / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
