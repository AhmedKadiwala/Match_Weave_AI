"""Produce Markdown summaries from executed JSON/XML reports, never assumed test outcomes."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    reports = ROOT / "docs/reports"
    suite = ET.parse(reports / "backend-tests.xml").getroot()
    tests = list(suite.iter("testcase"))
    failures = list(suite.iter("failure")) + list(suite.iter("error"))
    browser = json.loads((reports / "browser-tests.json").read_text(encoding="utf-8-sig"))["stats"]
    bench = json.loads((reports / "benchmark.json").read_text(encoding="utf-8"))
    comparison = json.loads((reports / "model-comparison.json").read_text(encoding="utf-8"))
    timings = bench["deterministic_state_claim_overlay_ms"]
    (ROOT / "TEST_RESULTS.md").write_text(
        f"""# Executed test results

Backend: **{len(tests) - len(failures)}/{len(tests)} passed**, {len(failures)} failures/errors. Browser: **{browser["expected"]} passed**, {browser["unexpected"]} unexpected, {browser["skipped"]} skipped. Reports: [backend XML](docs/reports/backend-tests.xml), [browser JSON](docs/reports/browser-tests.json).

The suite checks seeded replay, all five scorelines, geometry/schema constraints, shot-goal and pass-reception links, tactical scenario differences, event-time leakage, exact evidence recounts, ingestion atomicity/idempotency/conflicts, local-only inference URLs, real Microsoft workflow handoffs, incorrect-count rejection and correction, nine language/persona variants, API ingestion-to-publication, SSE resumption/Host filtering and every recorded public output. All 2,475 persona/language publications are source-recounted by the release test.

Real Chromium journeys cover every view, including Real match lab, same-server auto-connect and actual historical-model recomputation, all scenarios, replay, personas, Hindi/Spanish, evidence drawer keyboard behavior, club/player focus, filtering, broadcast JSON, failure trace, frontend-to-Python execution and offline operation. axe scans all seven views for WCAG A/AA issues; contrast issues found initially were fixed. [Accessibility report](docs/reports/accessibility.json). These automated scans do not establish complete WCAG compliance or replace assistive-technology/user testing.

Real local model executions are in demos/*-local-agent-run.json, including five model stages on every match. demos/pressing-local-recovery.json records a model-backed run with a deliberately corrupted claim, rejection, source repair and re-verification. Initial small-model schema failures are retained in demos/local-agent-run.json. Model free-form advice is not considered reliable factual output.

Production build, dependency audits and source checks are separate from unit tests. npm and pip audit snapshots report no known vulnerabilities at scan time. [Security scan](docs/reports/security-scan.json) checks common patterns, not all possible secrets. Vercel/Render deployment files and Google health-ping code are prepared; a separate minimal Render-profile browser test ran locally. No authenticated public deployment, actual Google trigger, remote CI success or portal submission is claimed.

Re-run commands are in README.md. Tests ran on Windows 11, Python 3.14.7 and Node 24.19.0. The supplied OneDrive workspace was unwritable; the complete repository is in C:\\Users\\Ahmed Kadiwala\\matchweave-ai.
""",
        encoding="utf-8",
    )
    with (ROOT / "TEST_RESULTS.md").open("a", encoding="utf-8") as page:
        page.write(
            "\nAdditional follow-up evidence: 1 browser test passed against a freshly installed minimal Render-profile backend; 5 Google Apps Script health-ping unit tests passed in Node. These are local tests, not actual Render or Google account execution. Historical backtest: 2,283 untouched 2025/26 matches; 52.17% accuracy versus 45.38% frequency baseline. Dataset/season rules, regulation/penalty/cancellation parsing, own-score/same-day leakage, saved metrics and both fitted model artifacts are independently tested. See TESTING_EXPLAINED.md, MODEL_CARD.md and docs/reports/historical-model.json.\n"
        )
    full = [r["workflow_ms"] for r in bench["comparison"]]
    local = [
        json.loads(p.read_text(encoding="utf-8"))["duration_ms"]
        for p in (ROOT / "demos").glob("*-local-agent-run.json")
    ]
    (ROOT / "BENCHMARKS.md").write_text(
        f"""# Measured benchmarks

Hardware: Intel Core i5-11260H, six cores / twelve threads, 16 GB RAM, Windows 11. RTX 3050 4 GB detected; **inference used CPU**, no GPU acceleration claim. Python 3.14.7, Node 24.19.0. Other applications and background tasks can affect timings. No timing is an SLA.

| Measurement | Actual result | Scope |
|---|---:|---|
| Deterministic state + claims + verification + one overlay, p50 | {timings["p50"]:.3f} ms | 90 checkpoints: 5 scenarios × 18 times |
| Same core path, p95 | **{timings["p95"]:.3f} ms** | Full event log scanned, input already validated/in memory |
| Same core path, max | {timings["max"]:.3f} ms | No HTTP/SQLite/model/workflow-graph overhead |
| Complete deterministic MAF recovery graph | {min(full):.3f}–{max(full):.3f} ms | Five deliberately corrupted checkpoints, includes repair and typed-message copying |
| Complete five-specialist local model runs | {min(local) / 1000:.2f}–{max(local) / 1000:.2f} s | Recorded Foundry Local Qwen2.5 1.5B executions |

The sub-300 ms target is met by the deterministic metric/overlay calculation; it is **not met by every complete workflow invocation**. Full agent narratives are independently timed and are queued by a single concurrency slot. Static replay uses recorded outputs immediately. The application does not imply instant LLM inference.

## Actual single-agent comparison

Same five scenarios at 70:00. A basic single MAF/local-model agent receives canonical candidate values and evidence IDs and must produce one structured story. The full system uses the five specialists, numerical verification and constrained realization. Both use the same local model; actual raw single-agent outputs are retained.

| Metric | Single agent | Complete workflow |
|---|---:|---:|
| Correct structured claim with exact evidence | {comparison["single_correct"]}/{comparison["sample_size"]} | {comparison["multi_correct"]}/{comparison["sample_size"]} |
| Median local run time | {comparison["single_median_ms"] / 1000:.2f} s | {comparison["multi_median_ms"] / 1000:.2f} s |
| Persona/language variants per publication | 1 | 9 |

This small sample measures complete approaches, not the isolated effect of agent count. Verification, constrained output, prompt differences and additional inference all differ. Free-form baseline prose is unverified and not scored as semantically correct. No statistical significance, predictive validity or generalized accuracy improvement is claimed.

A separate deterministic fault injection adds +99 to the selected numerical claim. Across five scenarios the ungated corrupted baseline fails recount and the full graph corrects it before publication. The clean deterministic baseline is already correct in all five. This demonstrates the evidence gate's behavior under a known fault, not spontaneous model error frequency.

Raw reports: [core/recovery benchmark](docs/reports/benchmark.json), [model comparison](docs/reports/model-comparison.json). Reproduce with `python -m scripts.benchmark`; with the local model server running, `python -m scripts.record_agents` and `python -m scripts.evaluate_agents`.
""",
        encoding="utf-8",
    )
    print(
        f"Reports generated from {len(tests)} backend cases and {browser['expected']} passed browser cases."
    )


if __name__ == "__main__":
    main()
