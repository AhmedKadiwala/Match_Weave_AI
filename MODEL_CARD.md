# Historical result model card

Model family: multinomial logistic regression, fitted locally with NumPy and served using Python math from JSON coefficients. This is a real trained result model, not an LLM fine-tune, an xG model, a video model, or a player/pressure-event predictor.

Data: 12,372 completed regulation-time results from the agreed big five leagues and three UEFA main competitions, Jan 1, 2021–Jun 30, 2026. Two cancelled fixtures have no label and are excluded from fitting. 2026–27 and qualifying rounds are excluded. Raw/pinned source metadata, licensing and coverage live under datasets/historical. Dataset/model-artifact license: CC BY-SA 4.0, with OpenFootball CC0 notices and Wikipedia contributor/revision attribution retained.

Features: fixed home/neutral indicator, rolling Elo difference, last-ten-match points/goals-for/goals-against differences, rest difference capped at 14 days, history availability and competition indicators. Club aliases are normalized; incomplete pre-2021 history uses declared priors. All fixtures on a date get their features before any results from that date update state. A fixture's own score is never one of its features.

Two artifacts:

- Evaluation weights: 10,089 completed matches before July 1, 2025. Hyperparameters selected from L2 penalties 0.001/0.01/0.1 using 2024–25 validation log loss, after fitting the candidate on 7,806 earlier training matches. Selected L2: 0.01. Weights stay frozen for the 2025–26 walk-forward test.
- All-data/production weights: refit on all 12,372 completed matches through 2025–26 after evaluation. They are not used to calculate the reported holdout scores. Retrospective inference from this artifact is explicitly in-sample.

Actual evaluation on 2,283 untouched-weight-fitting 2025–26 fixtures:

| Metric | Evaluation model | Constant training-frequency baseline |
|---|---:|---:|
| Accuracy | 52.1682% | 45.3789% |
| Multiclass log loss | 0.993249 | 1.063426 |
| Multiclass Brier score | 0.591497 | 0.642776 |

Lower log loss/Brier is better. These are actual historical measurements against a simple baseline; no significance test, market/expert comparison, future guarantee or broadly calibrated probability claim is made. Per-competition counts/metrics, candidate trials, hashes and run time are in docs/reports/historical-model.json. The default real-match UI and inference API use evaluation weights; an explicit `model=all-data` query selects the final refit and changes the evaluation label.

Reproduce training from the included snapshot: `python -m scripts.train_history`. Refreshing upstream sources first can change data hashes and learned weights. Pure-Python serving, NumPy training and season exclusion are tested. Public cloud deployment is not yet verified.

Limitations: community/encyclopedia source errors, imperfect club-alias merging, no pre-2021 history, no injuries/lineups/xG/pressing/location features, no real-time event feed and no independent external validation. Main-competition fixture counts reconcile, but score-by-score official certification has not been performed. The synthetic tactical simulator remains a separate, clearly labeled capability.
