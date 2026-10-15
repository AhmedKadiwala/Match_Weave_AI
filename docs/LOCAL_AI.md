# No-cost local inference

The tested path is **Foundry Local SDK 2.1.0 + Qwen2.5 1.5B + Microsoft Agent Framework core 1.22.0 / OpenAI provider 1.17.0**. All five agents executed on CPU. Installed GPU hardware was detected, but GPU inference is not claimed. Foundry Local is independent of an Azure subscription; Azure resources and paid inference are not used.

```powershell
.\.venv\Scripts\python.exe -m scripts.local_model
```

The explicit command initializes the SDK, downloads the model if needed, loads it, then starts its built-in web service at http://127.0.0.1:5273. Downloads can take several minutes. It disables nonessential SDK telemetry. The model cache remains local and is not committed or redistributed. Qwen2.5 1.5B Instruct is Apache 2.0: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct. Foundry terms remain Microsoft's: https://github.com/microsoft/Foundry-Local.

The alias used for download is `qwen2.5-1.5b`. The service uses canonical ID `qwen2.5-1.5b-instruct-generic-cpu:4`. If the catalog changes, list it using `--list` and inspect `/v1/models`. The scripts deliberately do not download acceleration providers automatically.

Backend variables can be set in its terminal:

```powershell
$env:MATCHWEAVE_LOCAL_URL='http://127.0.0.1:5273/v1'
$env:MATCHWEAVE_MODEL='qwen2.5-1.5b-instruct-generic-cpu:4'
$env:MATCHWEAVE_TIMEOUT='45'
```

Only loopback HTTP endpoints are allowed. No paid API key is read. For an already installed Ollama service, use `http://127.0.0.1:11434/v1` and a locally available freely licensed model ID. Ollama support uses the same Chat Completions client but was **not executed on this machine**. The verified integration is Foundry Local.

Agents select evidence-backed claims/layouts; free-form model notes remain untrusted. JSON schemas, bounded indices, canonical recounts and templates prevent unsupported prose from reaching publication. Microsoft FunctionTool calculations are scheduled explicitly by the analysis executors and recorded with origin labels; model-requested optional tool calls are separately recorded. Do not claim autonomous model tool use when its tool_calls list is empty.

When inference is unavailable, two attempts per agent are recorded and the deterministic policy continues. The workflow's overall HTTP timeout is 180 seconds. A request that exceeds that bound returns 504; no partially verified story is published. Retry deterministic mode. A small 0.5B preliminary run is retained as failure evidence; the 1.5B model completed all five roles. Neither model is considered an authoritative football expert.
