"""Parse licensed Wikipedia football boxes without copying prose, images, or shootout scores."""

import re

from .history import normalize_match


def football_boxes(text):
    pattern = re.compile(r"\{\{\s*(?:#invoke:)?Football box(?:\||\s)", re.IGNORECASE)
    for match in pattern.finditer(text):
        start = match.start()
        index = start
        depth = 0
        while index < len(text) - 1:
            if text[index : index + 2] == "{{":
                depth += 1
                index += 2
            elif text[index : index + 2] == "}}":
                depth -= 1
                index += 2
                if depth == 0:
                    yield start, text[start : index - 2]
                    break
            else:
                index += 1


def goal_minutes(value):
    minutes = []
    for body in re.findall(r"\{\{goal\|([^{}]*)\}\}", value, re.IGNORECASE):
        for token in body.split("|"):
            if re.fullmatch(r"\d+(?:\+\d+)?", token.strip()):
                minutes.append(int(token.strip().split("+")[0]))
    return minutes


def parse_wiki(text, competition, url, stage):
    rows, errors = [], []
    aliases = {}
    for _, block in football_boxes(text):
        for value in re.findall(r"^\|team[12]\s*=\s*(.*)$", block, re.MULTILINE):
            linked = re.search(r"\[\[([^]|]+)(?:\|([^]]*))?\]\]", value)
            if linked:
                aliases[(linked[2] or linked[1]).casefold()] = linked[1]
    for offset, box in football_boxes(text):
        fields = {
            key.strip().lower(): value.strip()
            for key, value in re.findall(
                r"^\|\s*([^=|\n]+?)\s*=\s*(.*?)(?=^\||\Z)", box, re.MULTILINE | re.DOTALL
            )
        }
        try:
            when = re.search(r"\{\{start date\|(\d{4})\|(\d+)\|(\d+)", fields.get("date", ""), re.IGNORECASE)
            if not when:
                raise ValueError("missing structured match date")
            date = "-".join([when[1], when[2].zfill(2), when[3].zfill(2)])

            def club(key, values=fields):
                link = re.search(r"\[\[([^]|]+)(?:\|[^]]*)?\]\]", values.get(key, ""))
                if link:
                    return link[1]
                plain = re.sub(r"\{\{[^{}]*\}\}", "", values.get(key, "")).strip()
                if not plain:
                    raise ValueError("missing club name")
                return aliases.get(plain.casefold(), plain)

            found = re.search(r"(\d+)\s*[–-]\s*(\d+)", fields.get("score", ""))
            score = list(map(int, found.groups())) if found else None
            if score and fields.get("aet", "").lower() in ("yes", "y", "1"):
                goals = [goal_minutes(fields.get("goals1", "")), goal_minutes(fields.get("goals2", ""))]
                if [len(g) for g in goals] != score:
                    raise ValueError(
                        "extra-time regulation score cannot be independently reconstructed from goal minutes"
                    )
                score = [sum(minute <= 90 for minute in g) for g in goals]
            row = normalize_match(
                competition, "2025-26", date, club("team1"), club("team2"), score, url, stage
            )
            if row:
                row["license"] = "CC-BY-SA-4.0"
                row["attribution"] = "Wikipedia contributors; linked article and its revision history"
                row["source_offset"] = offset
                rows.append(row)
        except ValueError as exc:
            errors.append({"offset": offset, "error": str(exc)})
    return rows, errors
