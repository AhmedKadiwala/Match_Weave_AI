# Competition submission text

Status: prepared materials, **not submitted**. The entry portal's authenticated form was not accessible; these cover the fields mandated by official rules §4.4 and the requested team fields. Confirm any additional portal-only fields before submission.

## Project title

**MATCHWEAVE AI — Evidence you can see. Stories made for you.**

## Elevator pitch

One football moment, a different story for every viewer. MatchWeave transforms original synthetic events into explainable intelligence for fans, analysts and broadcasters, using local Microsoft agents, exact evidence verification, multilingual storytelling and synchronized graphics—with no paid API.

## Full project description

Football's scoreline rarely explains the match. A casual viewer wants to understand why pressure is building; an analyst wants the comparison window and source events; a producer needs a concise graphic that can be timed and trusted. Generative text alone can confuse these needs or invent a confident explanation.

MatchWeave AI connects one source of football evidence to these different experiences. It ingests original synthetic match events, interprets them into event-time statistics and tactical proxies, explains supported changes, renders timed graphical overlays and personalizes the same approved facts by audience, club, player and language. A dark broadcast-style workspace includes live replay, an analyst control room, player-focused fan mode, a broadcast studio, an agent trace inspector and full-time recaps.

Five fictional 90-minute scenarios provide 9,887 reproducible events: a late comeback, a pressing shift, counterattack versus possession, a defensive contest and a standout forward. Events include passes/receptions, carries, shots/goals, pressure, recoveries, tackles, interceptions, clearances, fouls, set pieces, substitutions and possession changes. Every goal links to an on-target shot. Schemas, chronology, team/player references, duplicate handling and evidence are tested. These are authored event-level simulations, not real Premier League data, footage or tracking.

The intelligence system genuinely runs Microsoft Agent Framework 1.22.0. Match Analyst and Tactical Intelligence branches run in parallel, use Microsoft FunctionTool metric calculations and reconcile canonical claims. A Narrative Agent chooses the editorial anchor. The Fact Checker independently recounts its exact source-event set; a conditional repair route corrects an unsupported count and requires re-verification. Publishing adapts approved facts into three personas and English, Hindi and Spanish templates, then produces machine-readable overlay JSON. Actual inputs, outputs, model notes, durations, tools, retries and fallbacks are inspectable.

Local inference uses Microsoft Foundry Local SDK 2.1.0 and Qwen2.5 1.5B on the existing CPU. There is no Azure subscription, paid inference, credit-card trial or API-key requirement. A deterministic path runs the same real framework graph and is explicitly labeled as not LLM inference. The static build contains actual recorded executions and works without a hosted Python or model service.

Reliability is part of the product. Free-form model advice can be wrong and remains untrusted trace data; it cannot override numerical evidence. A real local single-agent comparison achieved exact structured claims and complete evidence in 3/5 checkpoints, compared with 5/5 for the full verified approach. This small sample compares complete systems, including verification and constrained rendering; it does not isolate agent count or establish generalized model accuracy. A separate injected +99 count test demonstrates correction before publication.

The deterministic state/claim/verification/overlay computation measured 44.624 ms p95 across 90 checkpoints on an i5-11260H with 16 GB RAM. Complete deterministic recovery graphs took roughly 347–444 ms; local model runs took about 26–31 seconds and are reported separately. Automated backend, browser, evidence, accessibility and dependency checks are provided with actual reports.

Potential applications include studio rundown assistance, source-linked graphics, localized fan experiences and reproducible analyst exploration. A real commercial deployment would need authorized live-data adapters, expert evaluation, stronger authentication/operations and independent language review. Proxy possession, momentum and Synthetic xG Proxy are transparent descriptive heuristics, not official statistics or validated predictions. The finished demonstration makes the verification process visible rather than hiding the boundary between observation and interpretation.

## Microsoft technologies actually used

- Microsoft Agent Framework core 1.22.0: typed workflow executors, fan-out/fan-in, conditional edges and agent calls.
- agent-framework-openai 1.17.0: real Chat Completions agents against the loopback service.
- Microsoft Foundry Local SDK 2.1.0 and its local ONNX runtime path: downloaded, loaded and executed Qwen2.5 1.5B on CPU.
- Windows System.Speech: optional local original demo narration generation.

No Azure cloud deployment, GitHub Copilot, Fabric, MCP/A2A orchestration or video inference is claimed.

## Repository, demo and video fields

| Field | Value / action |
|---|---|
| Public GitHub repository | Pending GitHub authentication; create and push the prepared repository using DEPLOYMENT.md |
| Public interactive demo | Pending verified Pages deployment; paste the literal successful deployment URL |
| Working test build | deployment/matchweave-static-demo.zip after packaging; serve extracted files over HTTP |
| Demo video | demos/matchweave-demo.mp4, 105 seconds; upload publicly or unlisted with unrestricted viewing to YouTube/Vimeo, then verify signed-out access |
| Video captions | demos/captions.srt |
| Test instructions | JUDGE_QUICKSTART.md |
| Architecture | docs/architecture.svg |
| Screenshots | docs/screenshots/01-live-intelligence.png through 06-recap.png, plus responsive captures |
| Category target | Best Multi-Agent System / Orchestration; overall Grand Prize consideration |

## Entrant fields — complete personally

Legal entrant/representative name, country/residence, adult eligibility, organization (if applicable), team name, up to four actual team members, contact details, Microsoft Learn profiles and optional learning-path completion: **not supplied or attested**. Do not invent teammates or learning activity. Confirm ownership, third-party permissions, conflict exclusions and registration directly in the portal.

## Final checklist

- [x] New original project, source, synthetic events and original graphics created for this brief.
- [x] Five challenge stages and real Microsoft technology implemented.
- [x] English description/testing materials and three output languages prepared.
- [x] Actual working-device screenshots and browser footage prepared by the capture workflow.
- [x] Functional local test build and zero-paid-API path.
- [ ] Entrant confirms eligibility, ownership, registration and any additional portal fields.
- [ ] Public GitHub URL verified.
- [ ] Public demo or downloadable test build URL verified.
- [ ] Video file reviewed, hosted and its public URL verified.
- [ ] All final field values entered and submitted; confirmation saved.
- [ ] Free unrestricted judging access maintained through November 10 at 23:59 Pacific.

Registration deadline: **October 20 noon Pacific / October 21 at 00:30 IST**. Submission deadline: **October 27 at 23:59 Pacific / October 28 at 12:29 IST**. Judging access ends **November 10 at 23:59 Pacific / November 11 at 13:29 IST**. Verify portal notices against the [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md).
