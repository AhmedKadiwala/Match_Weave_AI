# MatchWeave AI

**Every moment has a story. Every fan gets their version.**

Start with **START_HERE.txt**. Before uploading, follow **UPLOAD_CHECKLIST.md**. Everything needed—source, data, trained weights, instructions, test reports, screenshots and video—is in this folder.

## Run on your PC

Double-click **RUN_MATCHWEAVE.cmd**. It serves the built UI and API together at **http://127.0.0.1:8000/** and opens the browser after the server is ready. Keep its terminal window open. The first launch installs/builds when needed. A localhost link is local to the running PC, not a public website. Python 3.11+ and Node 22.12+ are needed for a clean setup; tested here with Python 3.14.7 / Node 24.19.0 / Windows 11.

If a legacy backend already occupies port 8000, stop it with `powershell -ExecutionPolicy Bypass -File scripts/stop.ps1`, then launch again. Current setup and developer scripts are under scripts/.

## Deploy your requested stack

**Frontend: Vercel. Backend: Render Free. Health ping: Google Apps Script every five minutes.**

[Copy/paste deployment settings](DEPLOY_TO_VERCEL_RENDER.md) and [pre-upload checklist](UPLOAD_CHECKLIST.md). `render.yaml`, `requirements-render.txt`, `frontend/vercel.json`, environment examples and `GOOGLE_KEEP_ALIVE.gs` are included. No cloud account, public deployment or Google trigger has been created. Public URLs stay pending until verified.

Render executes real deterministic Microsoft Agent Framework workflows and the trained result model. The public frontend also replays actual recorded local LLM runs. Live Foundry inference runs on your PC with `python -m scripts.local_model`; the large model is not falsely advertised as running on Render Free. Public pages never silently connect to a visitor's localhost.

## What works

- Six original event-intelligence views plus the new **Real match lab**.
- Five seeded fictional scenarios / 9,887 synthetic events, event-time analytics, exact evidence recounting, a real five-specialist Microsoft workflow, visible rejection/repair, three audience personas and English/Hindi/Spanish templates.
- Player focus, SVG event/shot maps, momentum proxies, full-time recaps, broadcast previews and timed JSON export.
- **12,372 real scored main-competition matches plus 2 cancelled fixtures**, Jan 2021–Jun 2026. Big five + Champions League, Europa League and Conference League. **2026–27 excluded from both training and analysis.** Main-competition coverage counts are complete; qualifying rounds are excluded.
- Actual trained logistic-regression result models: one frozen before the 2025–26 test, another refitted on all completed matches. The result model is distinct from the local language model; final scores do not become invented pressure/tracking data.

![Real match lab](docs/screenshots/07-real-match-lab.png)

[What is distinctive](WHAT_IS_UNIQUE.md), [real-data methods](REAL_DATA_AND_TRAINING.md), [model card](MODEL_CARD.md), [architecture](ARCHITECTURE.md), [API](docs/API.md).

## Real evidence

See [TESTING_EXPLAINED.md](TESTING_EXPLAINED.md), [TEST_RESULTS.md](TEST_RESULTS.md) and docs/reports/ for executed outcomes. The historical model's 2,283-match untouched 2025–26 test measured 52.17% accuracy versus a 45.38% frequency baseline. Full split details, log loss, Brier score and limitations are retained. It is an exploratory historical model, not an accuracy guarantee or a live feed.

The original deterministic metric/claim/overlay benchmark measured 44.624 ms p95; full workflow and local-model latency are reported separately in [BENCHMARKS.md](BENCHMARKS.md). The source-linked multilingual publication gate is independently tested across all 2,475 recorded variants.

## Regenerate

```powershell
.\.venv\Scripts\python.exe -m scripts.generate_data
.\.venv\Scripts\python.exe -m scripts.fetch_history
.\.venv\Scripts\python.exe -m scripts.train_history
.\.venv\Scripts\python.exe -m scripts.build_demo
.\.venv\Scripts\python.exe -m pytest -q
node --test scripts/tests/keep-alive.test.cjs
cd frontend
npm.cmd ci
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

`fetch_history` refreshes upstream revisions; train directly from the included snapshot to reproduce its model. Optional actual local LLM recordings use scripts/record_agents.py and scripts/evaluate_agents.py with the Foundry server running; [local AI guide](docs/LOCAL_AI.md).

## Submission assets and boundaries

[Submission text](SUBMISSION.md), [judge instructions](JUDGE_QUICKSTART.md), [file inventory](IMPLEMENTATION_INVENTORY.md), [manual actions](FINAL_MANUAL_ACTIONS.md). The actual [105-second video](demos/matchweave-demo.mp4) documents all seven views, including Real match lab and actual model recomputation; [screenshots](docs/screenshots/) and the model report provide additional evidence. [Source/static archives](deployment/release-manifest.json) are hashed and exclude credentials, downloaded model weights and local dependencies.

Original code/synthetic data/graphics: MIT. Combined real historical data, its derived artifacts and fitted model JSON: CC BY-SA 4.0, retaining OpenFootball CC0 notices and revision-linked Wikipedia contributor attribution. [Notices](THIRD_PARTY_NOTICES.md), [data license](datasets/historical/LICENSE.md), [cost audit](COST_AUDIT.md).

No real match footage, club logos or video inference is used. Tactical synthetic metrics remain documented proxies. Model notes can be wrong; unsupported prose is not published as fact. Cloud SQLite is ephemeral. Keep the static fallback available and verify public access before submitting. The provisional competition scorecard remains an internal 89/100 assessment, not a judging result.
