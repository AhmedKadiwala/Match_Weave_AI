# MatchWeave AI architecture

Python/FastAPI → validated synthetic event log → deterministic analytics → Microsoft Agent Framework workflow → evidence gate → persona/language publisher → JSON overlays → React/TypeScript application.

SQLite stores ingested events and actual workflow traces. Every snapshot is bounded by event time; future events cannot contribute to current statistics. The browser replays precomputed snapshots with the same backend contracts when offline. Local mode requests fresh backend state and workflows. No cloud resources, paid APIs, footage, or real club assets.

Five specialists: Match Analyst (metric evidence), Tactical Intelligence (rolling patterns), Narrative (candidate selection), Fact Checker (independent re-computation, correction), Publisher (validated audience and language templates, overlay timing). The Microsoft workflow uses typed messages and conditional correction routing. Optional local model agents choose structured claims through a local OpenAI-compatible service. Deterministic mode is explicitly labeled and never called LLM inference.

API contracts: GET /api/health, /api/matches, /api/matches/{id}, /api/matches/{id}/state?at_ms=…, /api/matches/{id}/stream; POST /api/matches/{id}/ingest; POST /api/matches/{id}/analyze; GET /api/runs/{id}. The generated schema is in /openapi.json.

Security boundary: loopback binding, explicit localhost CORS, bounded request bodies, validated enums/coordinates/references, per-client rate limit, timeout and concurrency limit for model runs, plain React text rendering. Local inference URLs are restricted to loopback, preventing accidental paid inference and remote prompt leakage. This is a local demo, not a hardened multi-tenant service.
