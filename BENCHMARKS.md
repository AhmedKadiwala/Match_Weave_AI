# Measured benchmarks

Hardware: Intel Core i5-11260H, six cores / twelve threads, 16 GB RAM, Windows 11. RTX 3050 4 GB detected; **inference used CPU**, no GPU acceleration claim. Python 3.14.7, Node 24.19.0. Other applications and background tasks can affect timings. No timing is an SLA.

| Measurement | Actual result | Scope |
|---|---:|---|
| Deterministic state + claims + verification + one overlay, p50 | 20.894 ms | 90 checkpoints: 5 scenarios × 18 times |
| Same core path, p95 | **44.624 ms** | Full event log scanned, input already validated/in memory |
| Same core path, max | 57.809 ms | No HTTP/SQLite/model/workflow-graph overhead |
| Complete deterministic MAF recovery graph | 347.663–444.196 ms | Five deliberately corrupted checkpoints, includes repair and typed-message copying |
| Complete five-specialist local model runs | 25.57–31.03 s | Recorded Foundry Local Qwen2.5 1.5B executions |

The sub-300 ms target is met by the deterministic metric/overlay calculation; it is **not met by every complete workflow invocation**. Full agent narratives are independently timed and are queued by a single concurrency slot. Static replay uses recorded outputs immediately. The application does not imply instant LLM inference.

## Actual single-agent comparison

Same five scenarios at 70:00. A basic single MAF/local-model agent receives canonical candidate values and evidence IDs and must produce one structured story. The full system uses the five specialists, numerical verification and constrained realization. Both use the same local model; actual raw single-agent outputs are retained.

| Metric | Single agent | Complete workflow |
|---|---:|---:|
| Correct structured claim with exact evidence | 3/5 | 5/5 |
| Median local run time | 19.11 s | 29.13 s |
| Persona/language variants per publication | 1 | 9 |

This small sample measures complete approaches, not the isolated effect of agent count. Verification, constrained output, prompt differences and additional inference all differ. Free-form baseline prose is unverified and not scored as semantically correct. No statistical significance, predictive validity or generalized accuracy improvement is claimed.

A separate deterministic fault injection adds +99 to the selected numerical claim. Across five scenarios the ungated corrupted baseline fails recount and the full graph corrects it before publication. The clean deterministic baseline is already correct in all five. This demonstrates the evidence gate's behavior under a known fault, not spontaneous model error frequency.

Raw reports: [core/recovery benchmark](docs/reports/benchmark.json), [model comparison](docs/reports/model-comparison.json). Reproduce with `python -m scripts.benchmark`; with the local model server running, `python -m scripts.record_agents` and `python -m scripts.evaluate_agents`.
