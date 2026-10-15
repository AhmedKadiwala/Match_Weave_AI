# API contracts

Start `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`. Interactive OpenAPI: `/docs`; machine schema: `/openapi.json`. Pydantic event schema is exported to event-schema.json. No API key is needed or accepted for paid inference.

| Method / path | Contract |
|---|---|
| GET /api/health | Local runtime health and genuine framework attribution |
| GET /api/matches | Five fictional match metadata/rosters |
| GET /api/matches/{id} | Complete seeded event log |
| GET /api/matches/{id}/state?at_ms=4200000 | Deterministic state bounded by event time |
| GET /api/matches/{id}/stream?speed=120&after=-1 | SSE match_event stream, sequence IDs, complete sentinel; `after` supports resumption |
| POST /api/matches/{id}/ingest | `{events:[Event,…]}`; up to 500 events, atomic, duplicate-idempotent, conflicting/out-of-order batches rejected |
| GET /api/matches/{id}/ingested-state | Current state from SQLite ingestion, separate from authored replay |
| POST /api/matches/{id}/analyze | at_ms, provider deterministic/local, audience fan/analyst/broadcaster, language en/hi/es, favorite_team harbor/vale/null, source replay/ingested, inject_failure boolean |
| GET /api/runs/{run_id} | Persisted actual workflow trace, approved story and nine persona/language variants |

```powershell
$request = @{ at_ms=4200000; provider='deterministic'; audience='analyst'; language='en'; inject_failure=$true } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/matches/pressing/analyze' -ContentType 'application/json' -Body $request
```

Ingest data into an empty local SQLite stream using source `ingested`, then analyze that stream. Replay APIs always refer to the authored scenario log and do not silently merge new data into it. Event-time windows exclude future observations. Rate limit: 240 requests/minute/client, one workflow at a time. Invalid input → 422; unknown resource → 404; ingest conflict → 409; oversized POST (>1 MB) → 413; busy/rate limit → 429; workflow deadline → 504. Logs retain local diagnostic detail, not credentials.

An overlay carries ID, match ID, start/end match ms, type, heading, supporting statistic, exact source IDs, position metadata, audience, language and verification status. Treat a source-derived overlay as ready only when verified. Templates contain no executable HTML; the UI renders text with React escaping.
