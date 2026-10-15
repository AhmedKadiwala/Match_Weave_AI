# How MatchWeave uses AI without a paid AI API

An API is a way for programs to communicate. A paid cloud AI API is one way to run a model; a model can also run on your own computer. MatchWeave uses local model execution and a separately trained statistical model.

## 1. Language-model inference on your computer

Microsoft Foundry Local loads the pretrained Qwen2.5 1.5B language model. Microsoft Agent Framework coordinates specialist agent calls, parallel analysis, shared results and conditional repair. The client sends requests to a loopback HTTP endpoint, normally `http://127.0.0.1:5273/v1`. No paid cloud-model key is required.

Actual local inference was executed and recorded. The model was used to select constrained claims and graphic layouts. Its free-form notes remain untrusted; canonical event calculations, numerical verification and templates control published output. We did not train or fine-tune Qwen on football scores. Tools scheduled by workflow executors are labeled separately from any model-requested tool calls; autonomous tool use is not claimed without a corresponding trace.

Start the app using README.md, then run this in a second terminal:

```powershell
.\.venv\Scripts\python.exe -m scripts.local_model
```

After the model service is ready, choose the local model in Agent intelligence and run a workflow. This optional command downloads model weights if needed. Recorded traces can be inspected without starting the model.

## 2. A model actually trained on football results

The historical pipeline trains multinomial logistic regression on pre-match features such as Elo difference, recent results/goals, rest and home advantage. Its output is a probability for home win, draw and away win. Inference runs locally or on the Python backend from included JSON weights; it does not need a cloud AI API or NumPy at serving time.

The frozen evaluation model fits 10,089 results before July 2025. A chronological test on 2,283 matches from 2025–26 measured 52.17% accuracy against a 45.38% constant-frequency baseline. A separate final artifact is fitted on all 12,372 completed results. The reported holdout score does not come from that all-data refit. See MODEL_CARD.md for splits, leakage prevention, metrics and limitations.

## 3. What each mode means

| Mode | What happens now | Fresh language-model inference? |
|---|---|---|
| Recorded replay | Displays retained outputs and traces from actual earlier local model runs | No |
| Deterministic workflow | Executes the real Microsoft workflow with calculations, source checks and policy choices | No |
| Local model workflow | Executes agents against the model currently running on the PC | Yes |
| Historical prediction | Runs fitted statistical coefficients against pre-match features | No LLM; fresh statistical-model inference |

The Render configuration runs deterministic workflows and historical model inference. It does not host the Foundry language model. English, Hindi and Spanish publication uses constrained templates; unrestricted generated translations are not claimed.

## A presentation explanation

“MatchWeave runs AI without paying a cloud model provider. Microsoft Foundry Local runs our language model on the computer, and Microsoft Agent Framework coordinates the specialist workflow. We also trained a separate match-result model on real historical football data. Every published numerical story is checked against its supporting events. Recorded replay, fresh local inference and deterministic verification are clearly labeled.”

Evidence: docs/LOCAL_AI.md, demos/*-local-agent-run.json, demos/pressing-local-recovery.json, models/, MODEL_CARD.md and docs/reports/historical-model.json.
