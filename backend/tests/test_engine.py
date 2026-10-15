import pytest

from backend.app.analytics import build_claims, state_at, verify_claim
from backend.app.generator import SCENARIOS, generate, generate_all
from backend.app.models import Event, EventType
from backend.app.store import Store, validate_events


@pytest.fixture(scope="module")
def matches():
    return generate_all()


@pytest.mark.parametrize("scenario", [s[0] for s in SCENARIOS])
def test_reproducibility(scenario):
    assert generate(scenario).model_dump_json() == generate(scenario).model_dump_json()


def test_schema_and_scorelines(matches):
    assert sum(len(m.events) for m in matches) > 5000
    categories = set()
    for match, spec in zip(matches, SCENARIOS):
        validate_events(match, match.events)
        state = state_at(match, match.duration_ms)
        for team, side in [("harbor", "home"), ("vale", "away")]:
            assert state["stats"][team]["goals"] == sum(t == side for _, t in spec[4])
            assert (
                state["stats"][team]["shots"]
                >= state["stats"][team]["shots_on_target"]
                >= state["stats"][team]["goals"]
            )
        categories.update(e.event_type for e in match.events)
    assert categories == set(EventType)


def test_physical_carries_and_pass_links(matches):
    for m in matches:
        by_id = {e.event_id: e for e in m.events}
        for e in m.events:
            if e.event_type == "carry":
                assert e.event_attributes["distance_m"] / (e.event_attributes["duration_ms"] / 1000) <= 10
            if e.event_type == "reception":
                p = by_id[e.related_event_ids[0]]
                assert p.event_type == "pass" and p.outcome == "complete"
                assert p.event_attributes["receiver_id"] == e.player_id


def test_tactical_scenarios(matches):
    pressing = next(m for m in matches if m.id == "pressing")
    before = [
        e
        for e in pressing.events
        if 3_000_000 <= e.match_clock_ms < 3_600_000
        and e.event_type == "recovery"
        and e.team_id == "harbor"
        and e.start_x >= 70
    ]
    after = [
        e
        for e in pressing.events
        if 3_600_000 <= e.match_clock_ms < 4_200_000
        and e.event_type == "recovery"
        and e.team_id == "harbor"
        and e.start_x >= 70
    ]
    assert len(after) > len(before)
    counter = state_at(next(m for m in matches if m.id == "counter"), 5_400_000)
    assert counter["stats"]["vale"]["possession"] > 50
    assert len(counter["counterattacks"]) > 0
    star = state_at(next(m for m in matches if m.id == "star"), 5_400_000)
    assert next(p for p in star["players"] if p["id"] == "harbor-9")["goals"] == 3


def test_evidence_and_future_leakage(matches):
    for m in matches:
        for at in [0, 600_000, 2_700_000, 4_200_000, 5_400_000]:
            for claim in build_claims(m, at):
                assert verify_claim(m, claim, at)[0]
                assert not verify_claim(m, claim.model_copy(update={"value": claim.value + 1}), at)[0]
                assert not verify_claim(m, claim.model_copy(update={"source_event_ids": ["invented"]}), at)[0]
            state = state_at(m, at)
            assert state["event_count"] == sum(e.match_clock_ms <= at for e in m.events)
            assert all(e["match_clock_ms"] <= at for e in state["key_moments"])


def test_atomic_ingestion(tmp_path):
    m = generate("pressing")
    store = Store(tmp_path / "test.db")
    batch = m.events[:20]
    assert store.ingest(m, batch) == {"accepted": 20, "duplicates": 0}
    assert store.ingest(m, batch) == {"accepted": 0, "duplicates": 20}
    with pytest.raises(ValueError, match="conflicting"):
        store.ingest(m, [batch[0].model_copy(update={"end_x": 1})])
    with pytest.raises(ValueError, match="out-of-order"):
        store.ingest(m, list(reversed(m.events[20:30])))
    assert store.ingest(m, m.events[20:30])["accepted"] == 10


def test_schema_rejects_invalid_geometry():
    e = generate("defensive").events[0].model_dump()
    with pytest.raises(ValueError):
        Event(**{**e, "start_x": 106})


def test_density_limits():
    with pytest.raises(ValueError):
        generate("pressing", 0)
