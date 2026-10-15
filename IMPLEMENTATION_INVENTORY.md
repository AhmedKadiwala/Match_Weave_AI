# Deliverable inventory

Local repository: `C:\Users\Ahmed Kadiwala\matchweave-ai`. The requested OneDrive directory was empty but rejected writes; no unrelated work was overwritten. Git branch: `codex/matchweave-ai`. Each implementation phase has logical commits. Public URLs are pending authentication.

| Area | Files / assets |
|---|---|
| Validated synthetic events | backend/app/models.py, generator.py; datasets/synthetic/*.json and *.ndjson; 5 scenarios / 9,887 events |
| Ingestion/state | backend/app/store.py, analytics.py, main.py; SQLite runtime, replay/SSE/ingestion/state/analysis APIs |
| Microsoft intelligence | backend/app/workflow.py, tools.py, publishing.py; real typed five-specialist workflow, conditional repair, scheduled FunctionTools, local-model calls and deterministic fallback |
| Recorded inference/evaluation | demos/*-local-agent-run.json (5 real local runs), pressing-local-recovery.json, local-agent-run.json (preliminary failures), docs/reports/model-comparison.json |
| Product | frontend/src/App.tsx, components/Pitch.tsx, Momentum.tsx, styles.css, types.ts; six working views and original SVG graphics |
| Static replay | frontend/public/artifacts: five event/snapshot/workflow bundles, index and measured comparison; 91 snapshots/match and 54 actual workflow records/match plus recovery |
| Tests | backend/tests; frontend/tests; docs/reports/backend-tests.xml, browser-tests.json, accessibility.json |
| Performance/security | BENCHMARKS, TEST_RESULTS, SECURITY; raw benchmark/pip/npm/security reports; dependency inventory |
| Local setup | scripts/setup.ps1, start.ps1, stop.ps1; .env.example; requirements.txt/requirements-ci.txt; frontend package lock |
| Regeneration | scripts/generate_data.py, local_model.py, record_agents.py, evaluate_agents.py, build_demo.py, benchmark.py, write_reports.py |
| Deployment | frontend/dist build, deployment/matchweave-static-demo.zip, .github/workflows/pages.yml, quality.yml, DEPLOYMENT.md |
| Submission source archive | deployment/matchweave-submission.zip; excludes .git, node_modules, .venv, .env, runtime and models |
| Video | demos/matchweave-demo.mp4 (105 seconds), raw screen-recording.webm, narration-segments.json, captions.srt, capture metadata; docs/reports/video.json |
| Video production | frontend/scripts/record-demo.mjs, scripts/synthesize_narration.ps1, build_video.py; DEMO_VIDEO_SCRIPT.md |
| Graphics | docs/screenshots/01–06 plus responsive captures; docs/architecture.svg; original favicon and club shields |
| Submission/audit | README, ARCHITECTURE, REQUIREMENTS_TRACEABILITY, COST_AUDIT, SCORING_MATRIX, SCORECARD_FINAL, PHASE_PROGRESS, SUBMISSION, JUDGE_QUICKSTART, FINAL_MANUAL_ACTIONS |
| Licenses | LICENSE, THIRD_PARTY_NOTICES, docs/licenses font notices; model weights not redistributed |
| Integrity | scripts/package_release.py, deployment/release-manifest.json with SHA-256 hashes and actual report-derived counts |

Verified current results: **27 backend tests, 9 browser tests, no serious/critical six-view axe findings, no known pip/npm advisories at scan time, no common credential-pattern findings; video 105.0 seconds; deterministic core p95 44.624 ms; local model runs 25.57–31.03 seconds.** Full workflow graph latency is reported separately. Provisional internal score: **89/100**, below the requested minimum target.

Remaining external work: entrant eligibility/registration, authenticated public repository/Pages/video publication, signed-out judging-access verification and portal submission. Broader football/model/language/user studies and production controls remain quality limitations, not completed claims.
