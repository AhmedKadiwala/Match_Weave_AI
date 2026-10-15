"""Microsoft FunctionTool for auditable, bounded metric requests."""

from agent_framework import tool

from .analytics import METRIC_TYPES, metric_events
from .models import Match


def metric_tool(match: Match, at_ms: int):
    @tool(
        name="calculate_metric",
        description="Independently count a football metric in a bounded source-event window.",
    )
    def calculate_metric(team_id: str, metric: str, start_ms: int, end_ms: int) -> dict:
        if metric not in METRIC_TYPES or team_id not in (match.home.id, match.away.id):
            raise ValueError("Unsupported metric or team")
        if not 0 <= start_ms <= end_ms <= at_ms:
            raise ValueError("Metric window exceeds current event time")
        source = metric_events(
            [e for e in match.events if start_ms <= e.match_clock_ms <= end_ms], team_id, metric
        )
        return {"count": len(source), "source_event_ids": [e.event_id for e in source]}

    return calculate_metric
