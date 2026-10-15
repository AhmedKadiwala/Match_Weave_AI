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
