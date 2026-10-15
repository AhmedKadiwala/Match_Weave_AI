import hashlib
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.history import normalize_match, parse_json, parse_txt, regulation_score, team_key
from backend.app.history_wiki import parse_wiki
from backend.app.main import app
from backend.app.result_model import FEATURES, chronological_features, predict

ROOT = Path(__file__).resolve().parents[2]


def fixture(day, home="Alpha FC", away="Beta FC", score=None):
    return normalize_match("en.1", "2021-22", day, home, away, score or [2, 1], "https://example.org/cc0")


def test_2026_27_and_outside_dates_are_excluded():
    with pytest.raises(ValueError):
        normalize_match("en.1", "2026-27", "2026-08-01", "A", "B", [1, 0], "source")
    assert normalize_match("en.1", "2025-26", "2026-07-01", "A", "B", [1, 0], "source") is None
    assert normalize_match("en.1", "2020-21", "2020-12-31", "A", "B", [1, 0], "source") is None
    assert team_key("Aston Villa F.C.") == team_key("Aston Villa FC (ENG)")


def test_real_json_mixed_scores_and_missing_are_not_zeroed():
    rows, errors = parse_json(
        {
            "matches": [
                {"date": "2025-08-01", "team1": "A", "team2": "B", "score": [2, 1]},
                {"date": "2025-08-02", "team1": "C", "team2": "D", "score": {}},
            ]
        },
        "en.1",
        "2025-26",
        "source",
    )
    assert not errors and rows[0]["home_goals"] == 2
    assert rows[1]["home_goals"] is None and not rows[1]["played"]


def test_txt_regulation_extra_time_penalties_and_cancelled():
    assert regulation_score("4-3 pen. 1-1 a.e.t. (1-1, 0-1)") == [1, 1]
    assert regulation_score("3-1 a.e.t. (2-1, 0-0)") == [2, 1]
    assert regulation_score("5-4 pen.") is None
    text = "Thu Mar 10 2022\n  RB Leipzig (GER) v Spartak Moskva (RUS) [cancelled]"
    rows, errors = parse_txt(text, "uefa.el", "2021-22", "source")
    assert not errors and rows[0]["cancelled"] and not rows[0]["played"]
    rows, errors = parse_txt(
        "Sun May 17 2026\n  21:00   FC Nantes  0-0  Toulouse FC", "fr.1", "2025-26", "source"
    )
    assert not errors and rows[0]["away_goals"] == 0


def test_wikipedia_plain_names_extra_time_and_license():
    text = """{{Football box
|date = {{Start date|2026|2|26|df=y}}
|team1 = Alpha {{fbaicon|ENG}}
|score = 2–1
|team2 = {{fbaicon|GER}} Beta
|aet = yes
|goals1 = {{goal|45+2|105}}
|goals2 = {{goal|80}}
}}"""
    rows, errors = parse_wiki(text, "uefa.el", "source", "Knockout phase")
    assert not errors and rows[0]["home_goals"] == 1 and rows[0]["away_goals"] == 1
    assert rows[0]["license"] == "CC-BY-SA-4.0"


def test_no_own_score_or_same_day_score_leaks_into_features():
    first = fixture("2021-08-01")
    second = fixture("2021-08-01", "Gamma", "Delta", [0, 3])
    third = fixture("2021-08-02", "Alpha FC", "Gamma", [1, 1])
    a = chronological_features([first, second, third])
    changed = {**first, "home_goals": 0, "away_goals": 7}
    b = chronological_features([changed, second, third])
    by_a = {r["match"]["id"]: r["features"] for r in a}
    by_b = {r["match"]["id"]: r["features"] for r in b}
    assert by_a[first["id"]] == by_b[first["id"]]
    assert by_a[second["id"]] == by_b[second["id"]]
    assert by_a[third["id"]] != by_b[third["id"]]


def test_complete_scope_provenance_and_season_exclusion():
    data = json.loads((ROOT / "datasets/historical/matches.json").read_text(encoding="utf-8"))
    report = json.loads((ROOT / "datasets/historical/coverage.json").read_text(encoding="utf-8"))
    assert len({r["id"] for r in data}) == len(data)
    assert all("2026-27" != r["season"] and "2021-01-01" <= r["date"] <= "2026-06-30" for r in data)
    assert all(r["status"] in {"complete-count", "windowed"} for r in report["coverage"])
    assert all(
        r["source_url"].startswith("https://") and r["license"] in {"CC0-1.0", "CC-BY-SA-4.0"} for r in data
    )
    assert sum(r["cancelled"] for r in data if "cancelled" in r) == 2
    assert report["conflicts_excluded"] == []


def test_separate_evaluation_and_all_data_fit_and_pure_python_inference():
    report = json.loads((ROOT / "docs/reports/historical-model.json").read_text())
    model = json.loads((ROOT / "models/historical-result-evaluation.json").read_text())
    production = json.loads((ROOT / "models/historical-result-model.json").read_text())
    assert model["training_end_exclusive"] == "2025-07-01"
    assert production["training_end_inclusive"] == "2026-06-30"
    assert production["training_matches"] == report["production_training_matches"] == 12372
    assert report["splits"]["untouched_test"] == 2283
    row = json.loads((ROOT / "frontend/public/history/en.1.json").read_text(encoding="utf-8"))[-1]
    expected = predict([row["features"][key] for key in FEATURES], model)
    assert abs(sum(expected) - 1) < 1e-12
    assert expected == list(row["probabilities"].values())


def test_history_api_runs_model_and_blocks_excluded_season():
    with TestClient(app) as client:
        response = client.get("/api/history/matches?competition=en.1&season=2025-26")
        assert response.status_code == 200 and response.json()["total"] == 380
        row = response.json()["matches"][0]
        prediction = client.get("/api/history/prediction/" + row["id"]).json()
        assert prediction["probabilities"] == row["probabilities"] and prediction["live_feed"] is False
        all_data = client.get("/api/history/prediction/" + row["id"] + "?model=all-data").json()
        assert "in-sample" in all_data["evaluation"]
        assert client.get("/api/history/matches?season=2026-27").status_code == 422
        assert client.get("/api/history/prediction/made-up").status_code == 404


def test_saved_accuracy_logloss_and_data_hash_are_independently_reproducible():
    report = json.loads((ROOT / "docs/reports/historical-model.json").read_text())
    actual_hash = hashlib.sha256((ROOT / "datasets/historical/matches.json").read_bytes()).hexdigest()
    assert report["data_sha256"] == actual_hash
    for name in ["historical-result-model.json", "historical-result-evaluation.json"]:
        assert json.loads((ROOT / "models" / name).read_text())["data_sha256"] == actual_hash
    correct = 0
    loss = 0
    count = 0
    for file in (ROOT / "frontend/public/history").glob("*.json"):
        if file.name == "summary.json":
            continue
        for row in json.loads(file.read_text(encoding="utf-8")):
            if row["date"] < "2025-07-01" or not row["played"]:
                continue
            target = (
                "home"
                if row["home_goals"] > row["away_goals"]
                else "draw"
                if row["home_goals"] == row["away_goals"]
                else "away"
            )
            correct += max(row["probabilities"], key=row["probabilities"].get) == target
            loss -= math.log(row["probabilities"][target])
            count += 1
    assert count == report["heldout"]["matches"]
    assert round(correct / count, 6) == report["heldout"]["accuracy"]
    assert round(loss / count, 6) == report["heldout"]["log_loss"]
