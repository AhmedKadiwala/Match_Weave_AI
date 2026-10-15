import json
from pathlib import Path

import pytest

from backend.app.analytics import verify_claim
from backend.app.generator import generate_all
from backend.app.models import Claim, Overlay
from backend.app.tools import metric_tool

ROOT = Path(__file__).resolve().parents[2]


def test_every_recorded_publication_has_exact_evidence():
    for match in generate_all():
        artifact = json.loads(
            (ROOT / "frontend/public/artifacts" / f"{match.id}.json").read_text(encoding="utf-8")
        )
        assert artifact["match"]["events"] == match.model_dump(mode="json")["events"]
        for run in artifact["runs"] + [artifact["recovery_run"]]:
            for story in run["variants"]:
                claim = Claim.model_validate(story["claim"])
                assert verify_claim(match, claim, run["at_ms"])[0]
                overlay = Overlay.model_validate(story["overlay"])
                assert overlay.source_event_ids == claim.source_event_ids
                assert overlay.start_ms == run["at_ms"]


async def test_metric_function_tool_is_real_and_event_bounded():
    match = generate_all()[0]
    calculator = metric_tool(match, 4_200_000)
    result = await calculator.invoke(
        arguments={"team_id": "vale", "metric": "goals", "start_ms": 0, "end_ms": 4_200_000},
        skip_parsing=True,
    )
    assert result["count"] == 2
    assert calculator.invocation_count == 1
    with pytest.raises(ValueError):
        await calculator.invoke(
            arguments={"team_id": "vale", "metric": "goals", "start_ms": 0, "end_ms": 5_400_000},
            skip_parsing=True,
        )
