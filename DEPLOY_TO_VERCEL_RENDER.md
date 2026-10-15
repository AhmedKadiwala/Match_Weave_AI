# Vercel frontend + Render backend + Google Apps Script

These files prepare deployment; no public Vercel/Render URL or Apps Script trigger has been created or verified. Use actual URLs returned by your accounts. Keep Free/Hobby selected and do not add a paid resource, trial or model endpoint.

## 1. Upload the source

Create an empty public GitHub repository. The clean READY_TO_UPLOAD folder contains the source without local dependencies and has no Git metadata yet. From that folder:

```powershell
cd "C:\Users\Ahmed Kadiwala\matchweave-ai\READY_TO_UPLOAD"
git init
git add .
git commit -m "MatchWeave AI submission"
git branch -M main
git remote add origin https://github.com/YOUR_LOGIN/matchweave-ai.git
git push -u origin main
```

If you deliberately use the original already-initialized project instead, keep its existing branch/history and use `git push -u origin HEAD:main`. Do not reinitialize or force-rename an unrelated repository.

The URL is a placeholder: substitute your actual repository. If an origin already exists, inspect `git remote -v` instead of adding a duplicate. The project contains source, original synthetic scenarios, licensed historical results, trained model JSON and static replay assets. `.env`, runtime databases/model downloads and dependencies are excluded. Do not upload only `frontend/dist` as the full project.

## 2. Render — backend

New → Web Service → connect the repository → **Python** runtime → **Free** compute. Root Directory stays **blank** because imports and datasets are resolved from the repository root.

| Setting | Exact value |
|---|---|
| Build Command | `pip install -r requirements-render.txt` |
| Start Command | `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health Check Path | `/api/health` |
| `PYTHON_VERSION` | `3.14.7` |
| `MATCHWEAVE_DEPLOYMENT` | `render` |
| `MATCHWEAVE_DB` | `/tmp/matchweave/matchweave.db` |
| `MATCHWEAVE_CORS_ORIGINS` | Add the actual Vercel production origin after step 3 |

Alternatively import the root `render.yaml` Blueprint. It selects Free explicitly. No paid database or disk is configured. Render supplies `RENDER_EXTERNAL_HOSTNAME`; the app adds that exact host to its allowed-host list. Custom domains, if used later, need an explicit `MATCHWEAVE_ALLOWED_HOSTS` entry, but are unnecessary here.

After Render reports a successful deployment, open its literal service URL plus `/api/health`. Expect JSON with `status: ok`, `deployment: render`, `local_inference_enabled: false` and `storage: ephemeral`. `/docs` shows the real API. If no frontend build exists on Render, its root is an API welcome response; the public UI belongs on Vercel.

Hosted capabilities: deterministic Microsoft Agent Framework workflows, exact evidence checks, real-result history and pure-Python inference from trained weights. Recorded Foundry LLM runs remain available in the frontend. The large local Foundry runtime/weights are not installed on Render; requesting `provider: local` is rejected explicitly. Fresh cloud LLM generation is not claimed.

## 3. Vercel — frontend

New Project → import the same repository → personal **Hobby** plan.

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework | `Vite` |
| Node.js | `24.x` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment variable | `VITE_API_URL=https://YOUR-ACTUAL-RENDER-SERVICE.onrender.com` |

Use the actual Render origin, with no `/api`, query, trailing path or placeholder. Set it before building. `frontend/vercel.json` supplies the build/output configuration and static-asset headers. All fonts and replay/history artifacts are bundled, so the UI does not depend on a model service to load.

Vercel variables with `VITE_` are public, build-time values. This variable is a backend URL, not a secret. Never put a paid key there. After editing it, redeploy Vercel.

## 4. Set CORS and test the live connection

Copy the actual Vercel **production** origin into Render's `MATCHWEAVE_CORS_ORIGINS`, e.g. the literal `https://...vercel.app` returned by Vercel. Multiple authorized origins can be comma-separated; no wildcards. Save the Render environment and wait for redeployment.

Open Vercel in a signed-out browser. The UI automatically connects to the configured backend. Cold starts can take about a minute; the frontend allows 75 seconds for a remote health check and remains usable in recorded replay. A successful connection says **Render backend connected** and **HOSTED API**. Run a fresh deterministic workflow, then open Real match lab, inspect a match and run its trained evaluation model on the backend.

## 5. Apps Script — your five-minute trigger

1. Open `https://script.google.com/` and create a standalone project.
2. Replace Code.gs with the root `GOOGLE_KEEP_ALIVE.gs` file.
3. Change `BACKEND_URL` to the actual Render origin.
4. Select `pingBackend` and Run once. Approve the requested external-request scope.
5. Triggers → Add trigger → function **pingBackend** → deployment **Head** → event source **Time-driven** → **Minutes timer** → **Every 5 minutes** → Save.

You do not need to deploy a Google web app. The supplied optional `deployment/google-apps-script/appsscript.json` requests only URL fetch and sets the timezone. The function calls `/api/health` once, checks HTTP 200 and `status: ok`, and logs the result. It never launches training or model/agent inference. A placeholder URL or HTML cold-start page is treated as a failed health check, not silently reported as healthy.

## 6. What the free setup does and does not promise

Render documents idle spin-down after 15 minutes and 750 shared Free instance hours per workspace/month. Frequent health requests can reduce idle spin-down; they cannot prevent maintenance, suspension, quota exhaustion or every cold start. Free service files/SQLite can reset on restart. The immutable match/history/model/replay files remain in the source repository; newly ingested data and fresh run IDs are temporary unless exported. Keep one free backend and no paid storage/add-ons. Vercel Hobby is for personal non-commercial projects. Apps Script runs within its own account quotas.

Official references: [Render Free](https://render.com/docs/free), [Render Python](https://render.com/docs/python-version), [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite), [Vercel Hobby](https://vercel.com/docs/plans/hobby), [UrlFetchApp](https://developers.google.com/apps-script/reference/url-fetch/url-fetch-app), [five-minute triggers](https://developers.google.com/apps-script/reference/script/clock-trigger-builder).

## Troubleshooting

- **Blank Vercel page / missing JSON:** Root Directory must be `frontend`; confirm `frontend/public/artifacts` and `frontend/public/history` were uploaded. They are real generated assets, not optional scaffolding.
- **Backend setup badge:** set a valid `VITE_API_URL` and redeploy Vercel. The public page deliberately does not guess a visitor's localhost backend.
- **CORS error:** Render's allowed origin must exactly match the Vercel URL you opened. A preview URL differs from production; add only the specific preview origin if you intentionally need it.
- **Render 400 Invalid host:** confirm `RENDER_EXTERNAL_HOSTNAME` is present. Add your actual hostname to `MATCHWEAVE_ALLOWED_HOSTS` if needed; do not use `*`.
- **Render build fails importing Foundry/ONNX:** use `requirements-render.txt`, not the full Windows development requirements file.
- **Local link stops working:** double-click `RUN_MATCHWEAVE.cmd`, keep its terminal open, and use http://127.0.0.1:8000/. It opens the browser only after readiness.
- **Google trigger fails:** run `pingBackend` manually to see its error; check the exact URL, a suspended Render service, cold-start response and Apps Script authorization. Five-minute pings are not an uptime guarantee.
