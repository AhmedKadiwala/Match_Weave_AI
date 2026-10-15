"""Local-only MatchWeave HTTP API."""
from fastapi import FastAPI

app = FastAPI(title="MatchWeave AI", version="1.0.0")


@app.get("/api/health")
def health():
    return {"status": "ok", "cost_mode": "local-only"}
