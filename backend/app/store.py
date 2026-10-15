"""Atomic ingestion: idempotent duplicates, reject conflicts, chronological reference checks."""
import json
import sqlite3
from pathlib import Path
from .models import Event, Match


def validate_events(match: Match, events: list[Event]) -> None:
    ids: dict[str, Event] = {}
    players = {p.id: p for p in match.home.players+match.away.players}
    last = (-1, -1)
    for e in events:
        if e.match_id != match.id or e.team_id not in (match.home.id, match.away.id):
            raise ValueError("invalid match or team reference")
        if e.player_id and (e.player_id not in players or players[e.player_id].team_id != e.team_id):
            raise ValueError("invalid player reference")
        if e.event_id in ids or (e.match_clock_ms, e.sequence_number) <= last:
            raise ValueError("duplicate or out-of-order event")
        if any(ref not in ids for ref in e.related_event_ids):
            raise ValueError("unknown or future related event")
        if e.event_type == "goal":
            shot = ids[e.related_event_ids[0]]
            if shot.event_type != "shot" or shot.team_id != e.team_id or shot.outcome != "on_target" or shot.player_id != e.player_id:
                raise ValueError("goal lacks same-player on-target shot")
            if any(x.event_type == "goal" and shot.event_id in x.related_event_ids for x in ids.values()):
                raise ValueError("shot counted as goal more than once")
        ids[e.event_id] = e
        last = e.match_clock_ms, e.sequence_number


class Store:
    def __init__(self, path: Path | str):
        self.path = str(path)
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS events (match_id TEXT, event_id TEXT, sequence INTEGER, body TEXT, PRIMARY KEY(match_id,event_id))")
            c.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, body TEXT)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def ingest(self, match: Match, batch: list[Event]) -> dict:
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            existing = [Event.model_validate_json(row[0]) for row in c.execute("SELECT body FROM events WHERE match_id=? ORDER BY sequence", (match.id,))]
            known = {e.event_id: e for e in existing}
            accepted = []
            duplicates = 0
            for e in batch:
                if e.event_id in known:
                    if e != known[e.event_id]:
                        raise ValueError("conflicting duplicate")
                    duplicates += 1
                else:
                    accepted.append(e)
                    known[e.event_id] = e
            validate_events(match, existing+accepted)
            c.executemany("INSERT INTO events VALUES (?,?,?,?)", [(e.match_id, e.event_id, e.sequence_number, e.model_dump_json()) for e in accepted])
            return {"accepted": len(accepted), "duplicates": duplicates}

    def save_run(self, run: dict):
        with self.connect() as c:
            c.execute("INSERT INTO runs VALUES (?,?)", (run["run_id"], json.dumps(run, ensure_ascii=False)))

    def events(self, match_id: str) -> list[Event]:
        with self.connect() as c:
            return [Event.model_validate_json(r[0]) for r in c.execute("SELECT body FROM events WHERE match_id=? ORDER BY sequence", (match_id,))]

    def get_run(self, run_id: str):
        with self.connect() as c:
            row = c.execute("SELECT body FROM runs WHERE run_id=?", (run_id,)).fetchone()
            return json.loads(row[0]) if row else None
