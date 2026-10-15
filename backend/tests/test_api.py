import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MATCHWEAVE_DB", str(tmp_path/"api.db"))
    store.cache_clear()
    with TestClient(app) as c:
        yield c
    store.cache_clear()


def test_replay_api(client):
    assert len(client.get("/api/matches").json()) == 5
    assert client.get("/api/matches/missing").status_code == 404
    assert client.get("/api/matches/pressing/state?at_ms=-1").status_code == 422
    assert client.get("/api/matches/comeback/state?at_ms=5400000").json()["stats"]["harbor"]["goals"] == 3


def test_ingestion_to_workflow(client):
    events = client.get("/api/matches/pressing").json()["events"][:100]
    assert client.post("/api/matches/pressing/ingest", json={"events":events}).json()["accepted"] == 100
    assert client.post("/api/matches/pressing/ingest", json={"events":events}).json()["duplicates"] == 100
    assert client.get("/api/matches/pressing/ingested-state").json()["event_count"] == 100
    result = client.post("/api/matches/pressing/analyze", json={"at_ms":events[-1]["match_clock_ms"], "source":"ingested", "inject_failure":True})
    assert result.status_code == 200
    run = result.json()
    assert run["repairs"] == 1
    assert client.get(f"/api/runs/{run['run_id']}").json() == run


def test_reject_bad_requests(client):
    assert client.post("/api/matches/pressing/analyze", json={"language":"xx"}).status_code == 422
    assert client.post("/api/matches/pressing/ingest", json={"events":[]}).status_code == 422
    assert client.post("/api/matches/pressing/ingest", content="x"*1_000_001).status_code == 413
    assert client.get("/api/runs/not-a-run").status_code == 404


def test_cors(client):
    assert client.get("/api/health", headers={"Origin":"https://evil.example"}).headers.get("access-control-allow-origin") is None
