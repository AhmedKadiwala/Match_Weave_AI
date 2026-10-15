# Local and zero-cost deployment

## Full Windows application

Run `scripts/setup.ps1`, then `scripts/start.ps1` as shown in README. These use a repository-local virtual environment and hidden loopback servers; logs and process ownership records are under ignored `runtime/`. They never provision cloud resources or download a model automatically. `scripts/stop.ps1` stops only recorded processes whose start time still matches. A prior manually launched server is reused, not claimed as script-owned.

Manual alternative, two terminals at repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# Second terminal
cd frontend
npm.cmd run dev
```

## Static public replay with GitHub Pages

GitHub documents Pages as available on public repositories with GitHub Free: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages. It serves static files; this build does not pretend to host Python or live model inference. Published snapshots and traces are from actual backend runs. See the normal Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits. Keep assets within those limits; do not enable a paid plan, custom domain or paid runner.

Publication is not executed: no GitHub Git credential is available in this environment and the connector has no repository-creation capability. All source and workflows are prepared.

1. Sign in to GitHub and create a **new empty public** repository named `matchweave-ai`. Keep it public through judging. Do not initialize README/license remotely because they exist here.
2. In the local project folder, substitute your actual repository URL:

```powershell
git remote add origin https://github.com/YOUR_LOGIN/matchweave-ai.git
git push -u origin HEAD:main
```

3. Repository Settings → Pages → Source: **GitHub Actions**.
4. Actions → **Publish zero-cost static replay** → Run workflow on main. The workflow is manual and refuses private repositories. It uses a standard Ubuntu runner, `npm ci`, Vite build, upload-pages-artifact and deploy-pages.
5. Open the **literal URL returned by the successful deployment job**. Check every match, language, player view, evidence drawer, agent trace and JSON download in a signed-out browser. Add that verified URL to SUBMISSION.md; do not guess it from your username.
6. Keep public source, demo and video accessible free of charge through November 10, 2026, 23:59 Pacific (November 11, 13:29 IST). No automation promises uptime.

For any static host, upload exactly `frontend/dist/`. Vite uses relative asset paths, so project subpaths work. All fonts are bundled locally. No application connector, cookies, account or secret is required to view the replay.

## Troubleshooting

- **OneDrive write errors:** move the extracted project into a writable local folder such as `C:\Users\YOUR_NAME\matchweave-ai`; do not change Windows security settings.
- **Blank page:** serve dist over HTTP; do not use file://. Check that artifacts/index.json is present and the host preserves the repository subpath.
- **No local connection:** check port 8000, `/api/health`, and the exact frontend origin. CORS permits localhost/127.0.0.1 ports 5173 and 4173; the API binds loopback.
- **Model 404:** use the canonical model ID from `/v1/models`, not a shorthand alias. The tested ID is `qwen2.5-1.5b-instruct-generic-cpu:4`.
- **Slow inference:** CPU execution is expected here. The RTX 3050 was detected but no GPU execution provider was installed or claimed. Keep deterministic mode for instant replay; inspect fallback traces.
- **API 429:** one workflow at a time and 240 requests/minute/client. Wait and retry; no cloud scaling is needed.
- **Pages failure:** confirm a public repository, Actions permissions and Pages source; inspect logs. No deployment is verified until GitHub returns success.
