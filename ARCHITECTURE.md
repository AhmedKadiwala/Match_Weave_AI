# MatchWeave AI architecture

Python/FastAPI → validated synthetic event log → deterministic analytics → Microsoft Agent Framework workflow → evidence gate → persona/language publisher → JSON overlays → React/TypeScript application.

SQLite stores ingested events and actual workflow traces. Every snapshot is bounded by event time; future events cannot contribute to current statistics. The browser replays precomputed snapshots with the same backend contracts when offline. Local mode requests fresh backend state and workflows. No cloud resources, paid APIs, footage, or real club assets.

Five specialists: Match Analyst (metric evidence), Tactical Intelligence (rolling patterns), Narrative (candidate selection), Fact Checker (independent re-computation, correction), Publisher (validated audience and language templates, overlay timing). The Microsoft workflow uses typed messages and conditional correction routing. Optional local model agents choose structured claims through a local OpenAI-compatible service. Deterministic mode is explicitly labeled and never called LLM inference.

API contracts: GET /api/health, /api/matches, /api/matches/{id}, /api/matches/{id}/state?at_ms=…, /api/matches/{id}/stream; POST /api/matches/{id}/ingest; POST /api/matches/{id}/analyze; GET /api/runs/{id}. The generated schema is in /openapi.json.

Security boundary: loopback binding, explicit localhost CORS, bounded request bodies, validated enums/coordinates/references, per-client rate limit, timeout and concurrency limit for model runs, plain React text rendering. Local inference URLs are restricted to loopback, preventing accidental paid inference and remote prompt leakage. This is a local demo, not a hardened multi-tenant service.

## Real-result model and hosted deployment extension

The new Real match lab uses licensed match results, not synthetic events. Its endpoints are /api/history/summary, /api/history/matches and /api/history/prediction/{id}. Training runs locally; two JSON weight artifacts separate frozen pre-2025/26 evaluation from the all-data refit. Hosted serving uses standard Python math. Source/result/feature/license metadata and actual held-out reports are preserved.

The same frontend can run on Vercel while the small Python backend runs on Render Free. Settings.from_env configures exact allowed hosts and frontend origins; Render disables PC-local model inference. The combined local launcher serves frontend/dist and API on one port and opens only after readiness. Static replay/history outputs remain available while the cloud backend is cold. Deployment files and Google health-ping code are prepared; cloud execution has not been claimed.
