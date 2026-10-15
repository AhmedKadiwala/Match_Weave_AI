# Demo video production — updated seven-view capture

Output: exactly 105 seconds (1:45), H.264 MP4, 1600x900, original local Windows speech narration, no music or match footage. Actual Chromium footage shows the running product. Local LLM traces are recorded runs; the historical-model recomputation shown in Real match lab is a fresh backend request, retained in demos/demo-real-model-prediction.json.

| Time | Actual scene |
|---|---|
| 00:00–00:12 | Product, score and differentiated match intelligence |
| 00:12–00:25 | Synthetic replay, analyst screen and shot map |
| 00:25–00:38 | Real match lab, Champions League history, actual trained-model recomputation |
| 00:38–00:52 | Exact event evidence and independent recount |
| 00:52–01:10 | Recorded Microsoft/Foundry specialist traces, tool calculations and rejected/repaired claim |
| 01:10–01:23 | Player focus, casual mode, Hindi and Spanish |
| 01:23–01:39 | Broadcast preview/layout and actual JSON download; Vercel/Render hosting concept |
| 01:39–01:45 | Full-time recap and product tagline |

Exact narration: demos/narration-segments.json. Capture metadata distinguishes recorded LLM traces from fresh historical-model inference. No publicly hosted deployment is depicted or claimed; the video records the local app. Source data attribution is in datasets/historical/LICENSE.md and VIDEO_DESCRIPTION.txt.

Recreate after starting the application:

```powershell
cd frontend
node scripts/record-demo.mjs
cd ..
powershell -ExecutionPolicy Bypass -File scripts/synthesize_narration.ps1
.\.venv\Scripts\python.exe -m scripts.build_video
```

The renderer verifies final duration; raw WebM, MP4, captions and metadata are retained. Review the result, then upload to an allowed public video host and paste the actual URL in SUBMISSION.md. No video hosting or portal submission has been executed.
