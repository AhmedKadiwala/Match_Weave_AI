# Requirements traceability

Official source checked 2026-10-15: https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md (sections 3, 4.1–4.12, 6). See docs/research/official-rules.md for retrieved source. Rule dates: register by Oct 20 noon Pacific; submit Oct 27 23:59 Pacific; access through Nov 10 23:59 Pacific. Entrant must confirm age, residence, conflicts, ownership and registration; these are not inferred.

| Requirement | Feature / file | Verification | Status |
|---|---|---|---|
| Five-stage pipeline §4.1 | backend/app, frontend/src | tests + screenshots | In progress |
| Synthetic realistic data §4.1/4.7 | backend/app/generator.py | realism and replay tests | In progress |
| Real-time intelligence and explainability | analytics.py, workflow.py | state/evidence tests | In progress |
| Multilingual narratives | publishing.py | language tests | In progress |
| Microsoft technology / multi-agent category | workflow.py | actual workflow traces | In progress |
| Public GitHub repository §4.4 | repository + README | public URL verification | Pending account access |
| Working video <2 min, public URL §4.4 | demos, DEMO_VIDEO_SCRIPT.md | actual footage + duration | Pending |
| Free access through judging §4.8 | offline bundle, Pages | browser tests; deployment verification | Build pending |
| Original/new work §4.3/4.6/4.11 | git history + fictional data | source and dependency review | Started in registration period |
| English materials §4.9 | root docs | documentation review | In progress |
| Eligibility/registration §3/4 | SUBMISSION.md | entrant confirmation/portal | Manual, cannot attest |
| Equal rubric weights §6 | SCORING_MATRIX.md | SCORECARD_FINAL.md | In progress |

Optional auto-video-eventing and cloud integration are intentionally omitted. Event-based metrics are labeled proxies; no computer vision claims.
