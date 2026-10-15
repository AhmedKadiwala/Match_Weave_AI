# Demo video production

Target and output: **105 seconds (1:45), strictly under two minutes**, 1600×900 H.264 MP4, original local synthetic narration, no music. All screen footage is a real Chromium recording of the working application. The local model executions displayed are explicitly recorded runs, not live inference happening during capture. captions.srt contains the English narration.

| Time | Actual shot / action | Voiceover focus |
|---|---|---|
| 00:00–00:12 | Live intelligence, score, original product interface | Football beyond the score; different audiences share facts |
| 00:12–00:30 | Replay 60:00 onward, analyst control room and shot map | Five synthetic scenarios, event-derived proxies, transparent methods |
| 00:30–00:50 | Evidence drawer, exact event records, independent recount | What changed, why it may matter, sample limits and no causal overclaim |
| 00:50–01:10 | Recorded Foundry/MAF run, tool detail, rejected count and corrected run | Five specialists, actual handoffs, proof before publication |
| 01:10–01:28 | Player focus, casual persona, Hindi and Spanish | Club/player preferences; constrained multilingual realization |
| 01:28–01:40 | Broadcast preview, layout selection and actual JSON download | Timed source-linked graphic payload; backend-independent replay |
| 01:40–01:45 | Full-time recap and score | Product tagline |

Exact original narration text: demos/narration-segments.json. Re-record with your own voice if desired; preserve the timing and factual limitations. The supplied synthesized voice is the installed Windows voice, not a cloned person.

## Reproduce the real capture

Start the application, then:

```powershell
cd frontend
node scripts/record-demo.mjs
cd ..
powershell -ExecutionPolicy Bypass -File scripts/synthesize_narration.ps1
.\.venv\Scripts\python.exe -m scripts.build_video
```

The first command records 105 seconds of actual UI interaction and saves raw WebM plus capture metadata. The speech script writes original narration WAVs to ignored runtime/narration. The Python command uses local FFmpeg to align segments, mux the screen recording and verify the final duration. No footage is downloaded or simulated. Keep a copy of the raw recording for verification. Video proof is in docs/reports/video.json once rendering succeeds.

Before upload, watch the MP4, check all narration against the current app and confirm readable evidence. Upload to a platform allowed by the rules (YouTube/Vimeo/Facebook Video/Youku); ensure judges can view signed out and without payment. Do not claim portal submission until it is confirmed. The video file alone does not complete the required public video URL field.
