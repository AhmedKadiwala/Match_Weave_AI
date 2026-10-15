# Judge quick start

Public replay URL: **pending publication**. This source contains a working test build and prerecorded data, not a fictional hosted backend. No credentials or payment are required for the local build.

1. Run `scripts/setup.ps1` then `scripts/start.ps1` on Windows. Open http://127.0.0.1:5173. For just the static build, serve frontend/dist over HTTP after `npm run build`.
2. Start with **Pressure makes the moment**, 70:00. Compare casual fan and analyst text; choose Hindi or Spanish. The selected claim's facts stay identical. Click Explore evidence and inspect exact event IDs and count.
3. Move the timeline to 60:00, then 70:00. The pressure pattern changes. No future events contribute to earlier snapshots. Choose **The comeback**, open Match recap, and inspect the 3–2 finish and five linked goals.
4. Open Your match. Choose a fictional club and player; observe their actual event locations, passing/defensive contributions and key events.
5. Open Broadcast studio. Select a graphic layout, toggle its preview and download JSON. Inspect match ID, time interval, persona/language, verified status and source IDs.
6. Open Agent intelligence. The 70:00 default run is a **Recorded Agent Run** using Foundry Local. Expand roles to inspect actual duration, input/output, untrusted model notes, scheduled FunctionTool calls and verification. Click Inspect failure recovery to see the rejected +99 claim and corrected publication.
7. For a fresh run, click Connect local backend. Choose deterministic mode and Run workflow. For actual inference, start `python -m scripts.local_model`, select Local model and run again. Expect about 30 seconds on the documented CPU. The optional local model download is not required for the static or deterministic experience.

All claims are synthetic observations. Metrics labeled proxies are not official statistics or predictions. No footage or video inference exists. See TEST_RESULTS.md, BENCHMARKS.md and SCORECARD_FINAL.md for evidence and limitations. Portal submission and public publication have not been verified.
