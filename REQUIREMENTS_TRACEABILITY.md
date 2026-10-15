# Final requirements traceability

Reviewed 2026-10-15 against [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md), especially §§3, 4.1–4.12 and 6. [Source review and API findings](docs/research/rules-review.md). Completion describes observed local behavior; external entries remain pending.

| Requirement | Implementation | Executed check / evidence | Status |
|---|---|---|---|
| A: ingest chronological synthetic events | models.py, generator.py, store.py, main.py | test_engine atomic/chronology; test_api ingestion and SSE resumption | Local complete |
| B: interpret meaningful stats/patterns | analytics.py | scoreline, physical-carry, pass-link, tactical-difference tests; analyst screenshot | Local complete; descriptive proxies |
| C: explain why observations matter | workflow.py, publishing.py | exact event set recount, confidence labels; live/evidence screenshot and video | Local complete |
| D: render synchronized machine-readable overlays | Overlay schema, App Broadcast studio | JSON download E2E; demos/demo-overlay.json; 04-broadcast.png | Local complete |
| E: genuine audience personalization | nine persona/language variants, club/player filters | persona/language/player E2E; 03-personalized.png | Local complete |
| Original synthetic realistic data §4.1/4.7 | five seeded 90-minute logs, 9,887 events | reproducibility tests, datasets/synthetic, DATA_METHODOLOGY.md | Complete event-level simulation; no tracking calibration |
| Key moments, pressure, momentum, counterattacks | analytics.py, shot-goal links, rolling claims | tactical test; goal recaps; momentum chart | Implemented subset; no causal inference |
| Player intelligence and recaps | state players/key_moments, fan/recap views | all five authored final scores and player-focus browser test | Local complete |
| Multiple languages | publishing.py en/hi/es templates | 2,475 recorded variants verified; Hindi/Spanish E2E | Complete templates; independent linguistic review pending |
| Genuine Microsoft technology | MAF core 1.22.0, provider 1.17.0, Foundry Local 2.1.0 | demos/*-local-agent-run.json; actual model-backed repair record | Executed on CPU |
| Distinct specialists / purposeful orchestration | parallel analyst+tactical, reconciliation, narrative, verifier, publisher | five role traces, typed graph tests, actual scheduled FunctionTools | Executed; optional model-requested tools not demonstrated |
| Failure recovery and measured baseline | conditional repair, evaluate_agents.py, benchmark.py | 3/5 vs 5/5 structured-proof comparison; injected fault tests | Measured, small sample and confounds documented |
| Local zero-paid-API path | Foundry + deterministic path, loopback-only guard | remote URL rejection, offline browser test, cost inventory | No paid resource provisioned |
| Complete UX | React six views, SVG maps/charts | 9/9 browser tests, six-view axe report, 390/768/1024 screenshots | Verified locally |
| Reliability/security/error handling | Pydantic, SQLite transactions, limits, CORS/Host filters, timeouts | 27/27 backend tests; pip/npm audits; common-pattern scan | Executed scoped checks; not enterprise certification |
| Reproducible working build §4.3/4.8 | setup/start/stop scripts, locks, static bundles | clean npm ci/build; Windows script rehearsal; production smoke | Verified on current Windows machine; pristine-machine/CI pending |
| Public repository §4.4 | complete Git source, license, README, source archive | Local commit history and release manifest | Pending GitHub authentication/public URL |
| <2 min functioning-device video §4.4 | record-demo.mjs, narration, build_video.py | actual MP4, raw WebM; video.json verifies 105.0 s; frame QA | File complete; public video URL pending |
| Free judging access §4.8 | static demo ZIP + manual Pages workflow | production build and browser smoke | Local build complete; public deployment/access duration unverified |
| New/original/authorized work §4.3/4.6/4.11 | original generator, code, graphics, licenses | source review, notices, no footage/real sports API | Project evidence present; entrant ownership attestation required |
| English submission materials §4.9 | README, SUBMISSION, JUDGE_QUICKSTART, English narration/captions | source/document/video review | Prepared |
| Entrant age/residence/conflicts, ≤4 team, registration §3/4 | SUBMISSION and FINAL_MANUAL_ACTIONS | No personal attestation or portal registration executed | Entrant action required |
| Rubric §6 / honest audit | SCORING_MATRIX, SCORECARD_FINAL | linked tests/benchmarks/screens/video/security evidence | Provisional internal 89/100, below target |

Optional video auto-eventing, live partner integration, cloud provisioning and official tracking/speed metrics are not implemented or claimed. Public URLs and hackathon submission are not fabricated. Registration: Oct 20 noon Pacific; submission: Oct 27 23:59 Pacific; judging access through Nov 10 23:59 Pacific.

## Follow-up traceability

| Request | Implementation | Executed evidence | Status |
|---|---|---|---|
| Simple reliable local launch | RUN_MATCHWEAVE.cmd, run-local.ps1, serve_local.py, mounted frontend | One-server browser journey and launcher readiness check | Verified locally |
| Vercel frontend / Render backend | vercel.json, render.yaml, small requirements, config.py, auto-connect | Config/body/host/CORS tests + separate minimal environment browser test | Prepared and locally simulated; actual cloud auth/deploy pending |
| Google ping every five minutes | GOOGLE_KEEP_ALIVE.gs + trigger instructions | 5 Node unit checks | Code tested; user installs trigger |
| Big five + 3 UEFA main competitions, 2021–2025/26, no 2026/27 | history parser/fetcher, licensed source snapshots, cutoff validation | Coverage/uniqueness/exclusion tests; 12,372 scored results and 2 cancelled | Main-competition count coverage complete; no qualifiers/live feed |
| Actual real-data model training and inference | train_history.py, two fitted JSON models, history_api.py | Reproduced metrics/hashes, 2,283-match holdout, actual server recompute | Executed; not LLM fine-tuning |
| Explain uniqueness/tests and one-folder upload | WHAT_IS_UNIQUE, TESTING_EXPLAINED, START_HERE, UPLOAD_CHECKLIST | Reports, source/archive inventory | Prepared |
