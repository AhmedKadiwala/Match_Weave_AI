"""Download pinned CC0 source snapshots; audit missing data, never fabricate missing results."""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backend.app.history import COMPETITIONS, SEASONS, expected_main_matches, parse_json, parse_txt

ROOT = Path(__file__).resolve().parents[1]
REPOSITORIES = ("openfootball/football.json", "openfootball/champions-league")


def get(url):
    import httpx

    response = httpx.get(
        url,
        headers={
            "User-Agent": "MatchWeaveResearch/1.1 (open-source educational project)",
            "Accept": "application/json",
        },
        timeout=30,
        follow_redirects=True,
    )
    response.raise_for_status()
    return response.content


def main():
    folder = ROOT / "datasets/historical"
    folder.mkdir(parents=True, exist_ok=True)
    sources = []
    downloads = []
    for repository in REPOSITORIES:
        commit = json.loads(get(f"https://api.github.com/repos/{repository}/commits/master"))["sha"]
        tree = json.loads(get(f"https://api.github.com/repos/{repository}/git/trees/{commit}?recursive=1"))[
            "tree"
        ]
        label = repository.split("/")[-1]
        license_url = f"https://raw.githubusercontent.com/{repository}/{commit}/LICENSE.md"
        license_body = get(license_url)
        (folder / f"{label}-LICENSE.md").write_bytes(license_body)
        sources.append(
            {"repository": repository, "commit": commit, "license": "CC0-1.0", "license_url": license_url}
        )
        for entry in tree:
            path = entry["path"]
            parts = path.split("/")
            if len(parts) != 2 or parts[0] not in SEASONS:
                continue
            season, filename = parts
            if repository.endswith("football.json") and filename in {
                key + ".json" for key in COMPETITIONS if not key.startswith("uefa")
            }:
                competition = filename.removesuffix(".json")
            elif repository.endswith("champions-league") and filename in {"cl.txt", "el.txt", "conf.txt"}:
                competition = "uefa." + filename.removesuffix(".txt")
            else:
                continue
            url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
            downloads.append((repository, label, commit, path, competition, season, url))

    def fetch(item):
        repository, label, commit, path, competition, season, url = item
        body = get(url)
        target = folder / "raw" / label / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        rows, errors = (
            parse_json(json.loads(body), competition, season, url)
            if path.endswith(".json")
            else parse_txt(body.decode("utf-8-sig"), competition, season, url)
        )
        return rows, {
            "repository": repository,
            "commit": commit,
            "path": path,
            "url": url,
            "sha256": hashlib.sha256(body).hexdigest(),
            "parsed_matches": len(rows),
            "errors": errors,
        }

    records = {}
    provenance = []
    conflicts = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        for rows, proof in pool.map(fetch, downloads):
            provenance.append(proof)
            for row in rows:
                prior = records.get(row["id"])
                if (
                    prior
                    and prior["played"]
                    and row["played"]
                    and (prior["home_goals"], prior["away_goals"]) != (row["home_goals"], row["away_goals"])
                ):
                    conflicts.append(row["id"])
                    continue
                if not prior or row["played"]:
                    records[row["id"]] = row
    supplements = [
        ("openfootball/espana", "2024-25/1-liga.txt", "es.1", "2024-25"),
        ("openfootball/italy", "2024-25/1-seriea.txt", "it.1", "2024-25"),
        ("openfootball/europe", "france/2025-26_fr1.txt", "fr.1", "2025-26"),
    ]
    for repository, path, competition, season in supplements:
        commit = json.loads(get(f"https://api.github.com/repos/{repository}/commits/master"))["sha"]
        label = repository.split("/")[-1]
        license_url = f"https://raw.githubusercontent.com/{repository}/{commit}/LICENSE.md"
        (folder / f"{label}-LICENSE.md").write_bytes(get(license_url))
        sources.append(
            {"repository": repository, "commit": commit, "license": "CC0-1.0", "license_url": license_url}
        )
        rows, proof = fetch(
            (
                repository,
                label,
                commit,
                path,
                competition,
                season,
                f"https://raw.githubusercontent.com/{repository}/{commit}/{path}",
            )
        )
        filled = 0
        for row in rows:
            prior = records.get(row["id"])
            if prior and not prior["played"] and row["played"]:
                records[row["id"]] = row
                filled += 1
        proof["supplemented_missing_scores"] = filled
        provenance.append(proof)
    from scripts.wiki_history_supplements import fetch_wiki

    wiki_rows, wiki_proof = fetch_wiki(get, folder)
    for row in wiki_rows:
        if row["id"] in records:
            raise ValueError("Unexpected overlapping supplement fixture")
        records[row["id"]] = row
    provenance.extend(wiki_proof)
    sources.append(
        {
            "source": "Wikipedia contributors",
            "license": "CC-BY-SA-4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "pages": wiki_proof,
        }
    )
    for conflict in conflicts:
        records.pop(conflict, None)
    matches = sorted(records.values(), key=lambda row: (row["date"], row["competition"], row["id"]))
    coverage = []
    for season in SEASONS:
        for competition, name in COMPETITIONS.items():
            if season == "2020-21" and competition == "uefa.conf":
                continue
            rows = [r for r in matches if r["competition"] == competition and r["season"] == season]
            played = sum(r["played"] for r in rows)
            cancelled = sum(r.get("cancelled", False) for r in rows)
            expected = expected_main_matches(competition, season)
            expected = expected - cancelled if expected is not None else None
            coverage.append(
                {
                    "competition": competition,
                    "name": name,
                    "season": season,
                    "fixtures": len(rows),
                    "scored_matches": played,
                    "expected_main_matches": expected,
                    "cancelled": cancelled,
                    "missing_scores": len(rows) - played - cancelled,
                    "status": "windowed"
                    if expected is None and rows
                    else "complete-count"
                    if played == expected
                    else "partial"
                    if rows
                    else "missing",
                    "note": "Count coverage only; not independently certified against official results. January 2021 date window applies to 2020-21. Qualifiers are outside this main-tournament coverage count.",
                }
            )
    report = {
        "data_kind": "real-match-results",
        "license": "Combined normalized dataset: CC-BY-SA-4.0; underlying OpenFootball records CC0-1.0",
        "start_date": "2021-01-01",
        "end_date": "2026-06-30",
        "excluded_seasons": ["2026-27"],
        "scope": COMPETITIONS,
        "matches": len(matches),
        "scored_matches": sum(r["played"] for r in matches),
        "sources": sources,
        "files": provenance,
        "coverage": coverage,
        "conflicts_excluded": conflicts,
        "limitations": [
            "Community-maintained results, not an official live feed.",
            "No pass, pressure, position or tracking event data is inferred from final scores.",
            "Not all requested competition-seasons are available or complete in these freely redistributable sources.",
            "UEFA regulation outcomes exclude penalty shootout scores; ambiguous extra-time/penalty records remain unscored.",
        ],
    }
    (folder / "matches.json").write_text(
        json.dumps(matches, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (folder / "coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "matches": len(matches),
                "scored": report["scored_matches"],
                "source_files": len(provenance),
                "parse_errors": sum(len(p["errors"]) for p in provenance),
                "incomplete": [
                    f"{c['competition']} {c['season']}: {c['scored_matches']}/{c['expected_main_matches']}"
                    for c in coverage
                    if c["status"] in {"partial", "missing"}
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
