# Executed test results

Backend: **27/27 passed**, 0 failures/errors. Browser: **9 passed**, 0 unexpected, 0 skipped. Reports: [backend XML](docs/reports/backend-tests.xml), [browser JSON](docs/reports/browser-tests.json).

The suite checks seeded replay, all five scorelines, geometry/schema constraints, shot-goal and pass-reception links, tactical scenario differences, event-time leakage, exact evidence recounts, ingestion atomicity/idempotency/conflicts, local-only inference URLs, real Microsoft workflow handoffs, incorrect-count rejection and correction, nine language/persona variants, API ingestion-to-publication, SSE resumption/Host filtering and every recorded public output. All 2,475 persona/language publications are source-recounted by the release test.

Real Chromium journeys cover every view, all scenarios, replay, personas, Hindi/Spanish, evidence drawer keyboard behavior, club/player focus, filtering, broadcast JSON, failure trace, frontend-to-Python execution and offline operation. axe scans six views for WCAG A/AA issues; contrast issues found initially were fixed. [Accessibility report](docs/reports/accessibility.json). These automated scans do not establish complete WCAG compliance or replace assistive-technology/user testing.

Real local model executions are in demos/*-local-agent-run.json, including five model stages on every match. demos/pressing-local-recovery.json records a model-backed run with a deliberately corrupted claim, rejection, source repair and re-verification. Initial small-model schema failures are retained in demos/local-agent-run.json. Model free-form advice is not considered reliable factual output.

Production build, dependency audits and source checks are separate from unit tests. npm and pip audit snapshots report no known vulnerabilities at scan time. [Security scan](docs/reports/security-scan.json) checks common patterns, not all possible secrets. GitHub CI/Pages workflows are prepared but have not run remotely; no public URL, remote CI success or portal submission is claimed.

Re-run commands are in README.md. Tests ran on Windows 11, Python 3.14.7 and Node 24.19.0. The supplied OneDrive workspace was unwritable; the complete repository is in C:\Users\Ahmed Kadiwala\matchweave-ai.
