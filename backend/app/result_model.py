"""Small trained result model: chronological pre-match features; pure-Python serving."""

import math
from collections import defaultdict, deque
from datetime import date
from itertools import groupby

from .history import COMPETITIONS

BASE_FEATURES = [
    "intercept",
    "home_advantage",
    "rating_gap_400",
    "recent_points_gap_3",
    "recent_attack_gap_3",
    "recent_defence_gap_3",
    "rest_gap_14",
    "home_history_10",
    "away_history_10",
]
FEATURES = BASE_FEATURES + [f"competition_{code}" for code in COMPETITIONS]
OUTCOMES = ["home", "draw", "away"]


def chronological_features(matches):
    ratings = defaultdict(lambda: 1500.0)
    form = defaultdict(lambda: deque(maxlen=10))
    last_date = {}
    result = []
    ordered = sorted(matches, key=lambda m: (m["date"], m["id"]))
    for day, fixtures in groupby(ordered, key=lambda m: m["date"]):
        fixtures = list(fixtures)
        when = date.fromisoformat(day)
        for match in fixtures:
            home, away = match["home_key"], match["away_key"]

            def mean(team, index, prior):
                values = form[team]
                return sum(row[index] for row in values) / len(values) if values else prior

            def rest(team, current_day=when):
                return min(14, (current_day - last_date[team]).days) if team in last_date else 7

            neutral = match.get("stage", "").lower() in {"final", "finals, final"}
            values = [
                1.0,
                float(not neutral),
                (ratings[home] - ratings[away]) / 400,
                (mean(home, 2, 1.35) - mean(away, 2, 1.35)) / 3,
                (mean(home, 0, 1.35) - mean(away, 0, 1.35)) / 3,
                (mean(home, 1, 1.35) - mean(away, 1, 1.35)) / 3,
                (rest(home) - rest(away)) / 14,
                min(len(form[home]), 10) / 10,
                min(len(form[away]), 10) / 10,
            ]
            values.extend(float(match["competition"] == code) for code in COMPETITIONS)
            label = None
            if match["played"]:
                label = (
                    0
                    if match["home_goals"] > match["away_goals"]
                    else 1
                    if match["home_goals"] == match["away_goals"]
                    else 2
                )
            result.append(
                {
                    "match": match,
                    "features": values,
                    "label": label,
                    "feature_cutoff": day,
                    "feature_rule": "Only matches strictly earlier than this calendar date; same-day results withheld until all features are built.",
                }
            )
        # All matches on a given day receive features before any of that day's scores update state.
        for match in fixtures:
            if not match["played"]:
                continue
            home, away = match["home_key"], match["away_key"]
            gh, ga = match["home_goals"], match["away_goals"]
            h = 1 if gh > ga else 0.5 if gh == ga else 0
            neutral = match.get("stage", "").lower() in {"final", "finals, final"}
            expected = 1 / (1 + 10 ** (-(ratings[home] - ratings[away] + (0 if neutral else 55)) / 400))
            change = 20 * (h - expected)
            ratings[home] += change
            ratings[away] -= change
            form[home].append((gh, ga, 3 if h == 1 else 1 if h == 0.5 else 0))
            form[away].append((ga, gh, 3 if h == 0 else 1 if h == 0.5 else 0))
            last_date[home] = last_date[away] = when
    return result


def predict(features, model):
    scaled = [(x - mean) / scale for x, mean, scale in zip(features, model["mean"], model["scale"])]
    logits = [
        sum(value * weight for value, weight in zip(scaled, column)) for column in zip(*model["weights"])
    ]
    maximum = max(logits)
    probs = [math.exp(z - maximum) for z in logits]
    total = sum(probs)
    return [p / total for p in probs]
