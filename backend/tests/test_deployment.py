import pytest
from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app, store


def render_settings():
    return Settings.from_env(
        {
            "MATCHWEAVE_DEPLOYMENT": "render",
            "RENDER_EXTERNAL_HOSTNAME": "test-api.onrender.com",
            "MATCHWEAVE_CORS_ORIGINS": "https://test-ui.vercel.app",
        }
    )


def test_render_health_host_and_exact_frontend_origin(tmp_path):
    with TestClient(
        create_app(render_settings(), frontend_dir=tmp_path), base_url="https://test-api.onrender.com"
    ) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["deployment"] == "render"
        assert health.json()["local_inference_enabled"] is False
        assert health.json()["storage"] == "ephemeral"
        assert client.get("/").json()["service"] == "MatchWeave API"
        response = client.options(
            "/api/matches/pressing/analyze",
            headers={
                "Origin": "https://test-ui.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "https://test-ui.vercel.app"
        assert (
            client.get("/api/health", headers={"Origin": "https://someone-else.vercel.app"}).headers.get(
                "access-control-allow-origin"
            )
            is None
        )
        assert client.get("/api/health", headers={"Host": "evil.onrender.com"}).status_code == 400


def test_render_runs_actual_framework_but_rejects_local_model(tmp_path, monkeypatch):
    monkeypatch.setenv("MATCHWEAVE_DB", str(tmp_path / "render.db"))
    store.cache_clear()
    with TestClient(
        create_app(render_settings(), frontend_dir=tmp_path), base_url="https://test-api.onrender.com"
    ) as client:
        assert client.post("/api/matches/pressing/analyze", json={"provider": "local"}).status_code == 400
        response = client.post(
            "/api/matches/pressing/analyze", json={"at_ms": 4200000, "inject_failure": True}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["framework"].startswith("Microsoft Agent Framework")
        assert result["repairs"] == 1 and result["status"] == "published"
        assert client.get("/api/runs/" + result["run_id"]).json() == result
    store.cache_clear()


def test_single_server_serves_ui_and_api(tmp_path):
    (tmp_path / "index.html").write_text("<title>MatchWeave test</title>", encoding="utf-8")
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts/index.json").write_text("[]")
    with TestClient(create_app(Settings.from_env({}), frontend_dir=tmp_path)) as client:
        assert "MatchWeave test" in client.get("/").text
        assert client.get("/artifacts/index.json").json() == []
        assert client.get("/api/health").json()["status"] == "ok"


def test_chunked_body_size_is_bounded_before_parsing(tmp_path):
    with TestClient(create_app(Settings.from_env({}), frontend_dir=tmp_path)) as client:

        def chunks():
            yield b"a" * 600_000
            yield b"b" * 600_000

        assert client.post("/api/matches/pressing/ingest", content=chunks()).status_code == 413


@pytest.mark.parametrize(
    "value",
    [
        "*",
        "https://*.vercel.app",
        "https://ui.vercel.app/path",
        "https://user:pass@ui.vercel.app",
        "http://public.example",
    ],
)
def test_invalid_cloud_cors_rejected(value):
    with pytest.raises(ValueError):
        Settings.from_env({"MATCHWEAVE_DEPLOYMENT": "render", "MATCHWEAVE_CORS_ORIGINS": value})
