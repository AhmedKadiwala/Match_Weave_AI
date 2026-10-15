# Competition submission field guide

Public source repository: https://github.com/AhmedKadiwala/Match_Weave_AI — uploaded and verified without authentication. Publication evidence: docs/reports/github-publication.json.

Publishing the repository is separate from finalizing the competition form. Complete the actual form in Innovation Studio and retain its confirmation. This guide does not claim a portal submission or a verified public website/video URL.

## What to put in each field

| Portal field | File or value |
|---|---|
| Project title | MATCHWEAVE AI — Evidence you can see. Stories made for you. |
| Project description | Use SUBMISSION.md, including its Real match lab addendum and the actual technology/capability boundaries |
| Project Code Repository Link | https://github.com/AhmedKadiwala/Match_Weave_AI after verifying the source is visible while signed out |
| Project Images/Video | demos/matchweave-demo.mp4 — actual 105-second video |
| Captions, if accepted | demos/captions.srt |
| Screenshots | docs/screenshots/01-live-intelligence.png and 07-real-match-lab.png; add other view captures as useful |
| Architecture graphic | docs/architecture.svg |
| Testing instructions | JUDGE_QUICKSTART.md and the README local setup |
| Team information | Your actual participant details; Microsoft Learn usernames only where applicable |

The MP4 in GitHub provides a copy, but does not replace uploading it in the portal. The reminder email allows uploading the file and says to include the URL if using YouTube/Vimeo; official rules §4.4 also ask for a public video URL. To cover both instructions, upload the MP4 in the portal and add an unrestricted YouTube/Vimeo viewing URL to the project description. VIDEO_DESCRIPTION.txt contains the video attribution text. Verify viewing without signing in.

## Is website hosting mandatory?

Official rules §4.8 require access to a working project via a website, functioning demo or test build. They do not require Vercel, Render, Azure hosting or a custom domain. A documented local test build is an available route. Confirm a clean clone actually runs on another machine and provide any build/testing link the portal requests. A source URL alone does not demonstrate successful installation.

Hosting is useful because judges can try the project without installing dependencies. If you choose it, push the source first, then follow DEPLOY_TO_VERCEL_RENDER.md. Include only the URLs returned by successful deployments. No deployment URL is invented here. Keep the chosen working project access free and available through the judging period.

The default local app needs Python and Node but no paid AI key. Fresh local language-model inference is optional and requires the separate Foundry process. The included recorded model traces and trained historical model support the default demo; README.md and AI_EXPLAINED.md explain the modes.

## Deadline discrepancy in the reminder

The pasted reminder says both 11:59 p.m. and 11:59 a.m. on October 27, 2026. Official rules §1 list the submission deadline as October 27, 2026 at 11:59 p.m. Pacific, equivalent to October 28 at 12:29 p.m. IST. Submit early and check the portal for any direct organizer update. No submission confirmation has been recorded.

Rules checked October 15, 2026: https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md (§§1, 4.4, 4.8).
