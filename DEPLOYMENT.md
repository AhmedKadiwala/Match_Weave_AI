# Deployment

The primary deployment path is now **Vercel frontend + Render Free backend + Google Apps Script health ping every five minutes**, as requested.

1. Read [UPLOAD_CHECKLIST.md](UPLOAD_CHECKLIST.md) before uploading.
2. Follow the exact settings in [DEPLOY_TO_VERCEL_RENDER.md](DEPLOY_TO_VERCEL_RENDER.md).
3. For local use, double-click RUN_MATCHWEAVE.cmd. The combined UI/API runs at http://127.0.0.1:8000/ and opens after readiness.

Prepared files: root render.yaml and requirements-render.txt, frontend/vercel.json, .env examples and GOOGLE_KEEP_ALIVE.gs. The hosted backend uses small dependencies, exposes /api/health, allows only configured exact frontend origins, rejects hosted local-model inference, and serves real deterministic Microsoft workflows and historical-model inference. The frontend preserves recorded replay when Render is cold.

No Vercel/Render public deployment or Apps Script trigger has been created or verified. Account actions and the actual resulting URLs are yours to complete. No paid resource, trial, database or model API is required by the prepared configuration. Five-minute health checks reduce idle spin-down but cannot guarantee uptime or remove free-tier limits.

The older optional GitHub Pages instructions are retained in docs/GITHUB_PAGES_OPTIONAL.md; they are no longer the primary requested path.
