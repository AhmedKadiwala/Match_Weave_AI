# Real data: what is included and what is actually trained

Confirmed scope: **Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, Europa League and Conference League**. Window: **January 1, 2021 to June 30, 2026**. **2026–27 is excluded from training and analysis.** These are historical main-competition matches; qualifying rounds and unrelated domestic cups are not included. The 2020–21 folder contributes only January–June 2021 fixtures, not 2020 matches.

## Actual downloaded coverage

- **12,372 scored regulation-time results**, plus **2 explicitly cancelled fixtures** kept without fake 0–0 scores.
- The full 2025–26 main competitions contain 380 Premier League, 380 La Liga, 306 Bundesliga, 380 Serie A, 306 Ligue 1, 189 Champions League, 189 Europa League and 153 Conference League scored matches.
- Every requested season's main-competition counts are present, with the intentional partial 2020–21 date window. Count agreement is not an independent certification of every source score.
- `datasets/historical/coverage.json` lists all competition/season counts, source revisions, hashes, parsing results and cancellations. No 2026–27 file is downloaded or normalized.

Sources: OpenFootball CC0 datasets, supplemented with CC BY-SA 4.0 Wikipedia result records for missing 2025–26 Europa/Conference data. La Liga/Serie A/Ligue 1 gaps in generated JSON were filled from their corresponding pinned OpenFootball text sources. Wikipedia extra-time results are converted to regulation scores only when goal-minute totals reconcile; penalty shootout tallies are never treated as regulation goals. Attribution and licensing are retained per record and in [the data license](datasets/historical/LICENSE.md).

## Actual training

This addition trains a **small multinomial logistic-regression result model** on real matches. It does **not** fine-tune Qwen, train a large language model, or learn tactical pressure from final scores. Features are pre-match rating difference, recent results/goals, rest, available history, home advantage/neutral final and competition indicators. No final score from the match being predicted is an input.

Two distinct fitted models prevent evaluation leakage:

| Artifact | Fitting data | Purpose |
|---|---|---|
| `models/historical-result-evaluation.json` | 10,089 completed matches strictly before July 2025 | Honest frozen-model 2025–26 walk-forward backtest; used by the default UI/model endpoint |
| `models/historical-result-model.json` | All 12,372 completed matches through 2025–26 | Final all-data refit requested for the project; retrospective predictions from it are in-sample and not presented as test performance |

Hyperparameter selection uses 7,806 training matches from Jan 2021–Jun 2024 and 2,283 validation matches from Jul 2024–Jun 2025. **2,283 completed 2025–26 matches remain untouched by evaluation-model weight fitting or hyperparameter selection.** Features for each match day are created before any of that day's results update team state. During the holdout, previous completed days update form/ratings, while fitted weights stay fixed.

Held-out result-model metrics: **52.17% accuracy**, **0.99325 log loss**, **0.59150 Brier score**. Constant training-frequency baseline: **45.38% accuracy**, **1.06343 log loss**, **0.64278 Brier**. These compare a small exploratory model to a simple baseline, not to expert/market systems or state-of-the-art methods. They do not establish future accuracy. Per-competition metrics and all split counts are in `docs/reports/historical-model.json`.

## Use it

Open **Real match lab** in the app. Select competition, season and club; inspect every match, source and result estimate; export the filtered data. The detail panel exposes pre-match features and whether the estimate is from the holdout. When connected to Render/local backend, **Run trained model on backend** actually recomputes the evaluation-model probabilities from its JSON weights using Python. An explicit API `?model=all-data` uses the final refit and labels the result in-sample.

```powershell
.\.venv\Scripts\python.exe -m scripts.fetch_history
.\.venv\Scripts\python.exe -m scripts.train_history
cd frontend
npm.cmd run build
```

Fetching checks the current upstream revisions and can change the data hash if sources change. To reproduce this exact training snapshot, use the included normalized/source data and run only `train_history`. Training runs locally with NumPy; serving uses standard Python math and needs no NumPy, local model download or paid key on Render.

## What real results cannot provide

Final scores do not contain passes, pressing actions, shot locations or player tracking. The synthetic event simulator remains separate and labeled because the hackathon explicitly asks for synthetic realistic events. Real-result data is never converted into invented pressure events or mislabeled as a live feed. This project now has both a genuine historical model/explorer and the original evidence-linked synthetic event workflow.
