"""Licensed result data ingestion. Real scores never become invented pressure/tracking events."""

import hashlib
import re
import unicodedata
from datetime import date

COMPETITIONS = {
    "en.1": "Premier League",
    "es.1": "La Liga",
    "de.1": "Bundesliga",
    "it.1": "Serie A",
    "fr.1": "Ligue 1",
    "uefa.cl": "Champions League",
    "uefa.el": "Europa League",
    "uefa.conf": "Conference League",
}
SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2020, 2026))
MIN_DATE, MAX_DATE = date(2021, 1, 1), date(2026, 6, 30)
MONTHS = {
    name: i + 1
    for i, name in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
}
ALIASES = {
    "internazionale milano": "inter milan",
    "internazionale": "inter milan",
    "inter": "inter milan",
    "sporting cp": "sporting portugal",
    "sporting clube portugal": "sporting portugal",
    "paris saint germain": "paris saint germain",
    "manchester utd": "manchester united",
    "atletico madrid": "atletico madrid",
}


def team_key(name: str) -> str:
    name = re.sub(r"\s*\([A-Z]{3}\)\s*$", "", name)
    name = "".join(c for c in unicodedata.normalize("NFKD", name.casefold()) if not unicodedata.combining(c))
    name = name.replace("a.f.c.", "afc").replace("f.c.", "fc").replace("s.k.", "sk")
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    tokens = [t for t in name.split() if t not in {"fc", "cf", "afc", "ac", "as", "ssc", "club", "de"}]
    key = " ".join(tokens)
    return ALIASES.get(key, key)


def normalize_match(competition, season, played_date, home, away, score, source_url, stage="", line=None):
    if competition not in COMPETITIONS or season not in SEASONS:
        raise ValueError("Competition/season outside the configured scope; 2026-27 is excluded")
    when = date.fromisoformat(played_date)
    if not MIN_DATE <= when <= MAX_DATE:
        return None
    season_year = int(season[:4])
    if not date(season_year, 7, 1) <= when <= date(season_year + 1, 6, 30):
        raise ValueError("Match date does not belong to its declared season")
    if not home or not away or team_key(home) == team_key(away):
        raise ValueError("Invalid home/away club names")
    if score is not None and (
        not isinstance(score, list)
        or len(score) != 2
        or any(not isinstance(s, int) or isinstance(s, bool) or not 0 <= s <= 25 for s in score)
    ):
        raise ValueError("Invalid regulation score")
    key = "|".join([competition, season, played_date, team_key(home), team_key(away)])
    return {
        "id": "real-" + hashlib.sha256(key.encode()).hexdigest()[:20],
        "competition": competition,
        "competition_name": COMPETITIONS[competition],
        "season": season,
        "date": played_date,
        "home": home,
        "away": away,
        "home_key": team_key(home),
        "away_key": team_key(away),
        "home_goals": score[0] if score is not None else None,
        "away_goals": score[1] if score is not None else None,
        "played": score is not None,
        "stage": stage,
        "source_url": source_url,
        "source_line": line,
        "license": "CC0-1.0",
        "data_kind": "real-match-result",
        "event_data_available": False,
    }


def parse_json(data, competition, season, url):
    records, errors = [], []
    for i, item in enumerate(data.get("matches", [])):
        score = item.get("score", {})
        score = score.get("ft") if isinstance(score, dict) else score
        try:
            row = normalize_match(
                competition,
                season,
                item["date"],
                item["team1"],
                item["team2"],
                score,
                url,
                item.get("round", ""),
                i + 1,
            )
            if row:
                records.append(row)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"line": i + 1, "error": str(exc)})
    return records, errors


def regulation_score(text):
    """Football.TXT: distinguish penalty shootouts, extra-time totals and 90-minute score."""
    text = text.strip()
    score = re.match(r"(\d+)\s*[-–]\s*(\d+)", text)
    if not score:
        return None
    primary = list(map(int, score.groups()))
    if "a.e.t." in text:
        bracket = re.search(r"a\.e\.t\.\s*\((\d+)-(\d+)", text)
        return list(map(int, bracket.groups())) if bracket else None
    if "pen." in text:
        # Reject ambiguous shootout-only lines instead of treating penalties as regulation goals.
        return None
    return primary


def parse_txt(text, competition, season, url):
    records, errors = [], []
    current_date = None
    stage = ""
    season_year = int(season[:4])
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.startswith("▪"):
            stage = line.lstrip("▪ ").strip()
            continue
        day = re.match(
            r"^\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?\s*$", line
        )
        if day:
            month = MONTHS[day[1]]
            year = int(day[3]) if day[3] else season_year + (month < 7)
            current_date = date(year, month, int(day[2])).isoformat()
            continue
        if line.lstrip().startswith("#"):
            continue
        fixture = None
        if " v " in line:
            stripped = re.sub(r"^\s*(?:\d{1,2}:\d{2}\s+)?", "", line)
            home, tail = stripped.split(" v ", 1)
            scored = re.match(r"^(.+?)\s+(\d+-\d+.*|\[cancelled\])\s*$", tail.strip())
            fixture = (
                home.strip(),
                scored[1].strip() if scored else tail.strip(),
                scored[2].strip() if scored else "",
            )
        else:
            legacy = re.match(r"^\s*(?:\d{1,2}:\d{2}\s+)?(.+?)\s{2,}(\d+-\d+.*?)\s{2,}(.+?)\s*$", line)
            if legacy:
                fixture = (legacy[1].strip(), legacy[3].strip(), legacy[2].strip())
            else:
                continue
        if not current_date:
            errors.append({"line": line_no, "error": "unparsed fixture/date"})
            continue
        try:
            row = normalize_match(
                competition,
                season,
                current_date,
                fixture[0],
                fixture[1],
                regulation_score(fixture[2]),
                url,
                stage,
                line_no,
            )
            if row:
                row["cancelled"] = "[cancelled]" in fixture[2]
                records.append(row)
        except ValueError as exc:
            errors.append({"line": line_no, "error": str(exc)})
    return records, errors


def expected_main_matches(competition, season):
    if season == "2020-21":
        return None  # intentionally only Jan 2021 onwards
    if competition in {"en.1", "es.1", "it.1"}:
        return 380
    if competition == "de.1":
        return 306
    if competition == "fr.1":
        return 380 if season < "2023-24" else 306
    if competition in {"uefa.cl", "uefa.el"}:
        return 189 if season >= "2024-25" else (125 if competition == "uefa.cl" else 141)
    if competition == "uefa.conf":
        return 153 if season >= "2024-25" else 141
    return None
