"""Repository secret-pattern scan. Report limitations; never print matching secret values."""

import json
import re
import subprocess
from pathlib import Path

PATTERNS = {
    "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "github-token": r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})",
    "aws-access-id": r"AKIA[0-9A-Z]{16}",
    "paid-model-key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}",
}


def main():
    files = (
        subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
        .decode()
        .split("\0")
    )
    scanned = 0
    findings = []
    for filename in set(files):
        path = Path(filename)
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".mp4", ".webm", ".woff2", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            continue
        scanned += 1
        for name, pattern in PATTERNS.items():
            if re.search(pattern, text):
                findings.append({"file": filename, "pattern": name})
    result = {
        "files_scanned": scanned,
        "findings": findings,
        "scope": "Common credential patterns in versionable text only; not a penetration test or comprehensive secret detector. Local runtime, caches, model weights and .env are ignored and not packaged.",
    }
    Path("docs/reports/security-scan.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(findings))


if __name__ == "__main__":
    main()
