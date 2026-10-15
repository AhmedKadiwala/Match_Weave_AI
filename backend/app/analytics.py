"""Pure event-time calculations. No LLM is trusted with arithmetic."""
import math
from collections import Counter
from .models import Claim, Event, EventType, Match

METRIC_TYPES = {"goals": "goal", "shots": "shot", "recoveries": "recovery", "pressure": "pressure", "passes_completed": "pass", "final_third_entries": "entry"}


def metric_events(events: list[Event], team_id: str, metric: str) -> list[Event]:
    selected = [e for e in events if e.team_id == team_id]
    if metric == "final_third_entries":
        return [e for e in selected if e.event_type in (EventType.PASS, EventType.CARRY) and e.outcome == "complete" and e.start_x < 70 <= e.end_x]
    if metric == "passes_completed":
        return [e for e in selected if e.event_type == "pass" and e.outcome == "complete"]
    return [e for e in selected if e.event_type == METRIC_TYPES[metric]]


def xg_proxy(e: Event) -> float:
    distance = math.hypot(105-e.start_x, 34-e.start_y)
    angle_penalty = 1-abs(e.start_y-34)/68
    return round(max(.01, min(.7, .55*math.exp(-distance/18)*angle_penalty)), 3)


def state_at(match: Match, at_ms: int) -> dict:
    at_ms = max(0, min(at_ms, match.duration_ms))
    events = [e for e in match.events if e.match_clock_ms <= at_ms]
    counts = Counter(e.team_id for e in events if e.event_type in ("pass", "carry", "shot"))
    total = sum(counts.values())
    stats = {}
    for team in (match.home, match.away):
        own = [e for e in events if e.team_id == team.id]
        passes = [e for e in own if e.event_type == "pass"]
        shots = metric_events(events, team.id, "shots")
        recent = [e for e in own if at_ms-600_000 < e.match_clock_ms <= at_ms]
        stats[team.id] = {
            "goals": len(metric_events(events, team.id, "goals")), "shots": len(shots),
            "shots_on_target": sum(e.outcome == "on_target" for e in shots),
            "passes": len(passes), "passes_completed": sum(e.outcome == "complete" for e in passes),
            "pass_completion": round(100*sum(e.outcome == "complete" for e in passes)/len(passes), 1) if passes else 0,
            "possession": round(counts[team.id]*100/total, 1) if total else 50,
            "final_third_entries": len(metric_events(events, team.id, "final_third_entries")),
            "recoveries": len(metric_events(events, team.id, "recoveries")),
            "pressure": sum(e.event_type == "pressure" for e in own),
            "pressure_per_minute": round(sum(e.event_type == "pressure" for e in recent)/(min(at_ms, 600_000)/60_000), 2) if at_ms else 0,
            "xg_proxy": round(sum(xg_proxy(e) for e in shots), 2),
            "average_pass_distance_m": round(sum(e.event_attributes.get("distance_m", 0) for e in passes)/len(passes), 1) if passes else 0,
        }
    players = []
    for p in match.home.players+match.away.players:
        own = [e for e in events if e.player_id == p.id]
        players.append({**p.model_dump(), "involvement": sum(e.event_type not in ("metadata", "possession_change", "substitution") for e in own),
                        "passes": sum(e.event_type == "pass" for e in own), "completed": sum(e.event_type == "pass" and e.outcome == "complete" for e in own),
                        "goals": sum(e.event_type == "goal" for e in own), "shots": sum(e.event_type == "shot" for e in own),
                        "defensive": sum(e.event_type in ("recovery", "tackle", "interception", "clearance") for e in own),
                        "event_ids": [e.event_id for e in own[-12:]]})
    momentum = []
    for minute in range(5, int(at_ms/60_000)+1, 5):
        window = [e for e in events if (minute-5)*60_000 < e.match_clock_ms <= minute*60_000]
        weights = {"shot": 5, "goal": 8, "pressure": 1.5, "recovery": 1, "carry": .25}
        vals = {t.id: round(sum(weights.get(str(e.event_type), 0)*(1 if e.start_x >= 70 else .35) for e in window if e.team_id == t.id), 2) for t in (match.home, match.away)}
        momentum.append({"minute": minute, **vals})
    counters = []
    for e in events:
        if e.event_type == "possession_change" and e.start_x <= 45:
            follow = [f for f in events if e.match_clock_ms < f.match_clock_ms <= e.match_clock_ms+15_000 and f.team_id == e.team_id and f.event_attributes.get("possession_id") == e.event_attributes.get("possession_id")]
            reached = [f for f in follow if f.end_x >= 70 and f.event_type in ("carry", "pass", "shot")]
            if reached:
                counters.append({"team_id": e.team_id, "at_ms": e.match_clock_ms, "event_ids": [e.event_id]+[f.event_id for f in reached]})
    goals = [e for e in events if e.event_type == "goal"]
    return {"match_id": match.id, "at_ms": at_ms, "event_count": len(events), "stats": stats, "players": players,
            "momentum": momentum, "counterattacks": counters, "key_moments": [e.model_dump(mode="json") for e in goals],
            "latest_event": events[-1].model_dump(mode="json") if events else None,
            "method": "Possession: share of pass/carry/shot actions. Momentum: weighted attacking events / 5 min. Synthetic xG Proxy, uncalibrated."}


def build_claims(match: Match, at_ms: int) -> list[Claim]:
    claims = []
    for team in (match.home, match.away):
        for metric, reason in [("goals", "score"), ("shots", "shot_threat"), ("recoveries", "pressing"), ("pressure", "pressing"), ("final_third_entries", "territory"), ("passes_completed", "circulation")]:
            start = 0 if metric == "goals" else max(0, at_ms-600_000)
            current = [e for e in match.events if start <= e.match_clock_ms <= at_ms and e.team_id == team.id]
            # Adjacent windows are disjoint; at t=0 nothing enters the previous window.
            previous = [e for e in match.events if max(0, start-600_000) <= e.match_clock_ms < start and e.team_id == team.id]
            evidence = metric_events(current, team.id, metric)
            if evidence:
                claims.append(Claim(claim_id=f"{match.id}-{at_ms}-{team.id}-{metric}", team_id=team.id, metric=metric,
                                    value=len(evidence), previous_value=len(metric_events(previous, team.id, metric)), window_start_ms=start,
                                    window_end_ms=at_ms, source_event_ids=[e.event_id for e in evidence],
                                    confidence="high" if metric == "goals" else ("moderate" if len(evidence)>=5 else "small sample"), reason_code=reason))
    return claims


def verify_claim(match: Match, claim: Claim, at_ms: int) -> tuple[bool, str]:
    if claim.team_id not in {match.home.id, match.away.id}:
        return False, "unknown team"
    if not 0 <= claim.window_start_ms <= claim.window_end_ms <= at_ms:
        return False, "future or invalid time window"
    expected = metric_events([e for e in match.events if claim.window_start_ms <= e.match_clock_ms <= claim.window_end_ms], claim.team_id, claim.metric)
    previous = metric_events([e for e in match.events if max(0, claim.window_start_ms-600_000) <= e.match_clock_ms < claim.window_start_ms], claim.team_id, claim.metric)
    if claim.value != len(expected) or claim.previous_value != len(previous):
        return False, "numerical claim does not match events"
    if set(claim.source_event_ids) != {e.event_id for e in expected} or len(claim.source_event_ids) != len(expected):
        return False, "evidence incomplete, duplicated, or unsupported"
    reason = {"goals": "score", "shots": "shot_threat", "recoveries": "pressing", "pressure": "pressing", "final_third_entries": "territory", "passes_completed": "circulation"}[claim.metric]
    if claim.reason_code != reason:
        return False, "unsupported tactical interpretation"
    return True, "independent event recount and exact evidence set passed"
