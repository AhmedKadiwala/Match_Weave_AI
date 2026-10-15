# Remaining manual actions

1. Follow UPLOAD_CHECKLIST.md: push/upload this complete source repository to GitHub.
2. Choose the working-project access route. A functioning local test build with README setup instructions is an alternative to a hosted website under official rules §4.8. Validate a clean clone on another machine if using that route. See COMPETITION_SUBMISSION_GUIDE.md.
3. If hosting: deploy the backend on Render Free, then frontend/ on Vercel Hobby with VITE_API_URL set to the actual backend URL. Set MATCHWEAVE_CORS_ORIGINS on Render to the actual Vercel production origin and verify signed-out browser access.
4. If using Render and the optional ping: paste GOOGLE_KEEP_ALIVE.gs into Google Apps Script, set its real backend URL, run pingBackend once, and create your Time-driven > Every 5 minutes trigger. No Google trigger has been installed here.
5. Inspect the seven views, historical match sources/estimates, fresh deterministic workflows, model recompute and overlay export through your chosen working-project route. Public deployment has not been claimed as successful.
6. Review/upload the actual 105-second demo video and captions, include the Real match lab screenshot/model report, paste actual public URLs into SUBMISSION.md, complete real entrant/team/eligibility details and submit through the portal.
7. Maintain free, unrestricted judging access through Nov 10, 2026, 23:59 Pacific (Nov 11, 13:29 IST). Registration closes Oct 20 noon Pacific (Oct 21, 00:30 IST); submission closes Oct 27, 23:59 Pacific (Oct 28, 12:29 IST).

Everything is under C:\Users\Ahmed Kadiwala\matchweave-ai. The original OneDrive workspace continues to reject writes; no security setting was weakened to bypass it. The ML dataset excludes 2026–27 as confirmed. No paid API key, Foundry model on Render, or invented public URL is needed.
