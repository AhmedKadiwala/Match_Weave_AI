# Cost audit

Budget: $0 / ₹0 additional spend. No accounts, cards, API keys or cloud provisioning are required by the application.

| Dependency | Execution / billing assumption | Risk and control |
|---|---|---|
| Python, FastAPI, Pydantic, Uvicorn, SQLite | Open source, local | Existing hardware/electricity/network only; no new paid service |
| Microsoft Agent Framework core | MIT, local orchestration | No hosted client or Azure credential; paid endpoints prohibited |
| Foundry Local | Local runtime; no Azure subscription | Download model once; obey runtime/model terms; no cloud fallback |
| Qwen2.5 0.5B (optional) | Apache 2.0 local weights | Small model, limited accuracy; evidence gate mandatory |
| Ollama (optional alternative) | MIT local runtime | Download only freely licensed models; loopback API only |
| React, Vite, TypeScript, Lucide | MIT / ISC / Apache 2.0 | npm install requires internet, not payment |
| pytest, Ruff, Playwright, pip-audit | Open source local checks | Browser download uses disk/network; CI opt-in |
| GitHub Pages (planned) | Free for public source repositories | Published-site limits apply; no paid plan needed; not yet published |
| GitHub Actions (planned) | Public repository standard hosted runner | No larger/paid runners, no cron; manual Pages publishing workflow |
| Synthetic data and SVG graphics | Original project assets | No licensed sports data or imagery |

No promotional credits or free trials. Static deployment is optional. Application startup never downloads models or provisions resources. Existing Codex access is user-authorized. Free service policies may change: verify before public publication. No recurring service fee is introduced.

Complete installed inventory: docs/dependency-inventory.json (70 Python distributions and 129 npm lockfile entries at audit time). Exact versions: requirements.txt and frontend/package-lock.json. Fontsource fonts use SIL OFL 1.1; original license notices are retained in docs/licenses. Windows built-in speech synthesis and FFmpeg are optional local video-production tools; no music or licensed footage is purchased. Existing device, power and internet connectivity are assumed available; there is no new cloud charge or service subscription. GitHub Pages free-public availability was checked against official documentation on 2026-10-15. No paid platform was activated.

## Requested hosted stack and real-data extension

Vercel Hobby hosts the static frontend; Render Free hosts the small Python backend; Google Apps Script can GET /api/health every five minutes with the supplied code. These are prepared and locally simulated, not authenticated public deployments. No card, paid plan, paid database, paid API or local-model weight download is configured on Render. Render SQLite is intentionally ephemeral; source/history/model/replay files remain reproducible from the repository. Free quotas/limits still apply; the ping is not an uptime guarantee.

Real results are downloaded from CC0 OpenFootball repositories plus CC BY-SA 4.0 Wikipedia supplements, with attribution/revision metadata retained. There is no paid football API. Statistical model training uses the already installed local NumPy package; hosted inference uses standard Python math. See datasets/historical/LICENSE.md. The 2026–27 season is excluded. Existing device power/connectivity assumptions remain; no new paid resource was provisioned.

Sources checked: https://render.com/docs/free, https://vercel.com/docs/plans/hobby, https://developers.google.com/apps-script/reference/script/clock-trigger-builder, https://github.com/openfootball/football.json, https://foundation.wikimedia.org/wiki/Legal:Text_of_the_Creative_Commons_Attribution-ShareAlike_4.0_International_License/en.
