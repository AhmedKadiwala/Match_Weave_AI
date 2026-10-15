import pytest
from backend.app.generator import generate
from backend.app.analytics import verify_claim
from backend.app.models import Claim, Overlay
from backend.app.workflow import run_workflow, local_url


async def test_real_framework_and_failure_recovery():
    match = generate("pressing")
    result = await run_workflow(match, 4_200_000, inject_failure=True)
    assert result["framework"].startswith("Microsoft Agent Framework")
    assert result["status"] == "published"
    assert result["repairs"] == 1
    assert {"match_analyst", "tactical_analyst", "narrative", "fact_checker", "publisher"} <= {t["agent"] for t in result["traces"]}
    assert [t["validation"] for t in result["traces"] if t["agent"] == "fact_checker"] == ["rejected", "passed"]
    claim = Claim.model_validate(result["published"]["claim"])
    assert verify_claim(match, claim, 4_200_000)[0]
    assert len(result["variants"]) == 9
    assert len({v["text"] for v in result["variants"]}) == 9
    for variant in result["variants"]:
        assert variant["claim"] == result["published"]["claim"]
        Overlay.model_validate(variant["overlay"])
        assert "99" not in variant["text"]


async def test_no_evidence_no_publication():
    result = await run_workflow(generate("defensive"), 0)
    assert result["status"] == "withheld"
    assert result["published"] is None


async def test_favorite_team_and_persona():
    result = await run_workflow(generate("comeback"), 5_400_000, favorite_team="vale", language="es", audience="fan")
    assert result["published"]["claim"]["team_id"] == "vale"
    assert result["published"]["language"] == "es"
    assert result["published"]["audience"] == "fan"


@pytest.mark.parametrize("url", ["https://api.openai.com/v1", "http://example.com", "http://127.0.0.1@evil.com", "file:///etc/passwd"])
def test_remote_inference_disabled(url):
    with pytest.raises(ValueError):
        local_url(url)
