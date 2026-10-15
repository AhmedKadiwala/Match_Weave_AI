"""Fetch six revision-pinned CC BY-SA pages for missing 2025/26 UEFA main-tournament results."""

import hashlib
import json
from urllib.parse import urlencode

from backend.app.history_wiki import parse_wiki


def fetch_wiki(get, folder):
    pages = []
    for name, competition in [("Europa", "uefa.el"), ("Conference", "uefa.conf")]:
        pages.extend(
            [
                (f"2025–26 UEFA {name} League league phase", competition, "League phase"),
                (f"2025–26 UEFA {name} League knockout phase", competition, "Knockout phase"),
                (f"2026 UEFA {name} League final", competition, "Final"),
            ]
        )
    records = []
    proof = []
    for title, competition, stage in pages:
        api = "https://en.wikipedia.org/w/api.php?" + urlencode(
            {"action": "parse", "page": title, "prop": "wikitext|revid", "format": "json"}
        )
        data = json.loads(get(api))["parse"]
        text = data["wikitext"]["*"]
        revision = data["revid"]
        source = "https://en.wikipedia.org/w/index.php?" + urlencode({"title": title, "oldid": revision})
        rows, errors = parse_wiki(text, competition, source, stage)
        records.extend(rows)
        proof.append(
            {
                "title": title,
                "revision": revision,
                "url": source,
                "history_url": "https://en.wikipedia.org/w/index.php?"
                + urlencode({"title": title, "action": "history"}),
                "license": "CC-BY-SA-4.0",
                "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "sha256_wikitext": hashlib.sha256(text.encode()).hexdigest(),
                "parsed_matches": len(rows),
                "errors": errors,
            }
        )
    (folder / "wikipedia-supplements.json").write_text(
        json.dumps(
            {
                "license": "CC-BY-SA-4.0",
                "attribution": "Wikipedia contributors; see per-page source and revision history",
                "changes": "Structured date/club/regulation-score fields extracted; no article prose, images or logos retained.",
                "sources": proof,
                "matches": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return records, proof
