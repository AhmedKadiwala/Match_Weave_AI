"""Actually fit and evaluate a compact model on real match results. No LLM fine-tuning claim."""

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from backend.app.history import COMPETITIONS
from backend.app.result_model import FEATURES, OUTCOMES, chronological_features, predict

ROOT = Path(__file__).resolve().parents[1]


def softmax(logits):
    scores = np.exp(logits - logits.max(axis=1, keepdims=True))
    return scores / scores.sum(axis=1, keepdims=True)


def fit(x, y, l2, epochs=500):
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    mean[0] = 0
    scale[scale < 1e-6] = 1
    normalized = (x - mean) / scale
    weights = np.zeros((x.shape[1], 3))
    targets = np.eye(3)[y]
    for epoch in range(epochs):
        probabilities = softmax(normalized @ weights)
        penalty = weights.copy()
        penalty[0] = 0
        gradient = normalized.T @ (probabilities - targets) / len(y) + l2 * penalty
        weights -= 0.12 * gradient
    return {
        "weights": weights.tolist(),
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "features": FEATURES,
        "outcomes": OUTCOMES,
        "l2": l2,
        "epochs": epochs,
    }


def metrics(y, probabilities):
    if not len(y):
        return {"matches": 0, "accuracy": None, "log_loss": None, "brier": None}
    probabilities = np.asarray(probabilities)
    y = np.asarray(y)
    return {
        "matches": len(y),
        "accuracy": round(float((probabilities.argmax(axis=1) == y).mean()), 6),
        "log_loss": round(float(-np.log(np.maximum(probabilities[np.arange(len(y)), y], 1e-12)).mean()), 6),
        "brier": round(float(((probabilities - np.eye(3)[y]) ** 2).sum(axis=1).mean()), 6),
    }


def main():
    start = time.perf_counter()
    source = ROOT / "datasets/historical/matches.json"
    matches = json.loads(source.read_text(encoding="utf-8"))
    examples = chronological_features(matches)
    scored = [row for row in examples if row["label"] is not None]
    train = [row for row in scored if row["match"]["date"] < "2024-07-01"]
    validation = [row for row in scored if "2024-07-01" <= row["match"]["date"] < "2025-07-01"]
    test = [row for row in scored if row["match"]["date"] >= "2025-07-01"]
    assert all(
        "2026-27" not in row["match"]["season"] and row["match"]["date"] <= "2026-06-30" for row in scored
    )

    def arrays(rows):
        return np.array([r["features"] for r in rows], dtype=float), np.array(
            [r["label"] for r in rows], dtype=int
        )

    x, y = arrays(train)
    _vx, vy = arrays(validation)
    trials = []
    for penalty in [0.001, 0.01, 0.1]:
        candidate = fit(x, y, penalty)
        score = metrics(vy, [predict(row["features"], candidate) for row in validation])
        trials.append({"l2": penalty, "validation": score})
    best = min(trials, key=lambda row: row["validation"]["log_loss"])["l2"]
    final_train = train + validation
    fx, fy = arrays(final_train)
    model = fit(fx, fy, best)
    model.update(
        {
            "name": "Chronological result softmax v1",
            "model_type": "multinomial logistic regression",
            "training_end_exclusive": "2025-07-01",
            "holdout_start": "2025-07-01",
            "holdout_end": "2026-06-30",
            "data_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "seed": 0,
            "license": "CC-BY-SA-4.0",
            "description": "Result/form model, not an LLM, not a tactical-event model, not betting advice.",
        }
    )
    frequencies = np.bincount(fy, minlength=3) / len(fy)
    test_probs = [predict(row["features"], model) for row in test]
    ty = np.array([r["label"] for r in test])
    report = {
        "name": model["name"],
        "data_sha256": model["data_sha256"],
        "data_window": {"start": "2021-01-01", "end": "2026-06-30", "excluded_season": "2026-27"},
        "splits": {
            "training": len(train),
            "validation": len(validation),
            "refit_training": len(final_train),
            "untouched_test": len(test),
        },
        "selection_metric": "2024/25 validation log loss; 2025/26 held out from weight fitting and hyperparameter selection",
        "trials": trials,
        "heldout": metrics(ty, test_probs),
        "frequency_baseline": metrics(ty, [frequencies for _ in test]),
        "uniform_baseline": metrics(ty, [[1 / 3] * 3 for _ in test]),
        "per_competition": {},
        "limitations": [
            "Historical backtest, not a live feed or guarantee of future accuracy.",
            "Features update after each completed match day; model weights stay fixed throughout the 2025/26 walk-forward holdout.",
            "Community/encyclopedia sources can contain errors; licenses and revisions retained.",
            "Some club aliases and missing pre-2021 history can affect estimates.",
            "No shot, pressure, player-tracking or live tactical event data is invented from final scores.",
        ],
        "features": FEATURES,
        "duration_seconds": round(time.perf_counter() - start, 3),
    }
    for competition in COMPETITIONS:
        selected = [
            (row, prob) for row, prob in zip(test, test_probs) if row["match"]["competition"] == competition
        ]
        report["per_competition"][competition] = metrics(
            [r["label"] for r, _ in selected], [p for _, p in selected]
        )
    output = ROOT / "models"
    output.mkdir(exist_ok=True)
    model["purpose"] = "evaluation: weights frozen before 2025/26 holdout"
    (output / "historical-result-evaluation.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    ax, ay = arrays(scored)
    production = fit(ax, ay, best)
    production.update(
        {
            "name": "Historical result model — all available completed matches",
            "model_type": "multinomial logistic regression",
            "purpose": "production/refit on all available results; not used for reported holdout metrics",
            "training_end_inclusive": "2026-06-30",
            "training_matches": len(scored),
            "data_sha256": model["data_sha256"],
            "license": "CC-BY-SA-4.0",
            "outcomes": OUTCOMES,
            "features": FEATURES,
        }
    )
    (output / "historical-result-model.json").write_text(json.dumps(production, indent=2), encoding="utf-8")
    report["production_training_matches"] = len(scored)
    report["evaluation_model_training_matches"] = len(final_train)
    report["duration_seconds"] = round(time.perf_counter() - start, 3)
    (ROOT / "docs/reports/historical-model.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    public = ROOT / "frontend/public/history"
    public.mkdir(parents=True, exist_ok=True)
    (public / "LICENSE.md").write_text(
        (ROOT / "datasets/historical/LICENSE.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    coverage = json.loads((ROOT / "datasets/historical/coverage.json").read_text(encoding="utf-8"))
    compact_coverage = {k: v for k, v in coverage.items() if k not in {"files", "sources"}}
    compact_coverage["sources"] = coverage["sources"]
    (public / "summary.json").write_text(
        json.dumps({"coverage": compact_coverage, "model": report}, ensure_ascii=False), encoding="utf-8"
    )
    by_competition = {key: [] for key in COMPETITIONS}
    for row in examples:
        match = row["match"]
        sample = {
            **match,
            "evaluation": "held-out walk-forward"
            if match["date"] >= "2025-07-01"
            else "training/validation period — not held out",
        }
        sample["probabilities"] = (
            dict(zip(OUTCOMES, predict(row["features"], model))) if not match.get("cancelled") else None
        )
        sample["features"] = dict(zip(FEATURES, row["features"]))
        sample["feature_cutoff"] = row["feature_cutoff"]
        by_competition[match["competition"]].append(sample)
    for code, rows in by_competition.items():
        (public / f"{code}.json").write_text(
            json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "splits": report["splits"],
                "heldout": report["heldout"],
                "frequency_baseline": report["frequency_baseline"],
                "l2": best,
                "seconds": report["duration_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
