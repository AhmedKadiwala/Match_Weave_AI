"""Seeded, authored tactical scenarios with continuous possession chains."""

import math
import random

from .models import Event, EventType, Match, Player, Team

SCENARIOS = [
    (
        "comeback",
        "The comeback",
        "Two down. One extraordinary final quarter.",
        41,
        [(21, "away"), (58, "away"), (76, "home"), (85, "home"), (89, "home")],
    ),
    (
        "pressing",
        "Pressure makes the moment",
        "Harbor City turn up their press after the hour.",
        52,
        [(38, "away"), (71, "home"), (82, "home")],
    ),
    (
        "counter",
        "Control versus chaos",
        "Vale dominate the ball; Harbor break into open space.",
        63,
        [(29, "home"), (64, "away"), (79, "home")],
    ),
    (
        "defensive",
        "A game of fine margins",
        "Compact blocks, fewer entries and one decisive opening.",
        74,
        [(83, "away")],
    ),
    (
        "star",
        "The Sol Vega show",
        "One fictional forward connects the attack and finishes three moves.",
        85,
        [(18, "home"), (43, "away"), (61, "home"), (84, "home")],
    ),
]


def teams() -> tuple[Team, Team]:
    names = [
        "Eli Stone",
        "Noah Reed",
        "Arun Sethi",
        "Leo Marsh",
        "Ivo Cruz",
        "Milo Hart",
        "Kai Rivers",
        "Ravi Sen",
        "Sol Vega",
        "Theo Lane",
        "Omar Vale",
        "Finn Grey",
        "Ari Moss",
    ]
    other = [
        "Alex North",
        "Hugo Bell",
        "Dev Shah",
        "Luca Rowe",
        "Sami Hale",
        "Nico West",
        "Ezra Lake",
        "Liam Frost",
        "Remy Cole",
        "Zayn Brook",
        "Jude Ash",
        "Ben Oak",
        "Rui Finch",
    ]

    def make(tid, name, short, color, roster):
        positions = ["GK", "RB", "CB", "CB", "LB", "DM", "CM", "CM", "ST", "RW", "LW", "CM", "ST"]
        return Team(
            id=tid,
            name=name,
            short=short,
            color=color,
            players=[
                Player(id=f"{tid}-{i + 1}", team_id=tid, name=n, number=i + 1, position=positions[i])
                for i, n in enumerate(roster)
            ],
        )

    return make("harbor", "Harbor City", "HBC", "#a7ef64", names), make(
        "vale", "Vale Athletic", "VAL", "#aa9cff", other
    )


def generate(scenario: str, density: float = 1.0) -> Match:
    if not 0.5 <= density <= 3:
        raise ValueError("density must be between 0.5 and 3")
    spec = next((s for s in SCENARIOS if s[0] == scenario), None)
    if spec is None:
        raise ValueError("unknown scenario")
    sid, title, desc, seed, goals = spec
    rng = random.Random(seed)
    home, away = teams()
    roster = {"harbor": home.players[:11], "vale": away.players[:11]}
    events: list[Event] = []
    t = 0
    team = "harbor"
    x, y = 52.5, 34.0
    owner = roster[team][5].id
    possession_id = 0

    def add(kind, *, tid=None, pid=None, end=None, outcome="complete", links=None, attrs=None):
        nonlocal t
        tid = tid or team
        pid = pid or (owner if tid == team else rng.choice(roster[tid][1:]).id)
        ex, ey = end or (x, y)
        sx, sy = (x, y) if tid == team else (105 - x, 68 - y)
        e = Event(
            event_id=f"{sid}-{len(events):05d}",
            match_id=sid,
            sequence_number=len(events),
            period=1 if t < 2_700_000 else 2,
            match_clock_ms=t,
            team_id=tid,
            player_id=pid,
            event_type=kind,
            start_x=round(sx, 2),
            start_y=round(sy, 2),
            end_x=round(ex, 2),
            end_y=round(ey, 2),
            outcome=outcome,
            related_event_ids=links or [],
            event_attributes={"possession_id": possession_id, **(attrs or {})},
            synthetic_metadata={
                "seed": seed,
                "generator": "v1",
                "coordinates": "attacking-normalized-metres",
            },
        )
        events.append(e)
        return e

    def switch(next_team=None, reason="turnover", high=False):
        nonlocal team, x, y, owner, possession_id, t
        prior = add(EventType.TURNOVER, outcome="incomplete")
        team = next_team or ("vale" if team == "harbor" else "harbor")
        x, y = 105 - x, 68 - y
        if high:
            # A failed short build-up has put the ball in this danger zone.
            x = max(73, min(90, x))
        owner = rng.choice(roster[team][1:]).id
        possession_id += 1
        t = min(t + 200, 5_399_000)
        recovered = add(EventType.RECOVERY, links=[prior.event_id], attrs={"reason": reason})
        add(EventType.POSSESSION, links=[recovered.event_id], attrs={"reason": reason})

    add(EventType.METADATA, attrs={"phase": "kickoff"}, outcome="neutral")
    add(EventType.POSSESSION, attrs={"reason": "kickoff"})
    goal_index = 0
    half = False
    subs: set[str] = set()
    while t < 5_390_000:
        t += max(1000, int(rng.uniform(3500, 8500) / density))
        if t >= 5_390_000:
            break
        if t >= 2_700_000 and not half:
            half = True
            add(EventType.METADATA, attrs={"phase": "second_half"}, outcome="neutral")
            x, y = 52.5, 34
            switch("vale", "second_half")
        if t >= 3_900_000:
            for tid, squad in [("harbor", home), ("vale", away)]:
                if tid not in subs:
                    incoming, outgoing = squad.players[11], roster[tid][7]
                    add(
                        EventType.SUBSTITUTION,
                        tid=tid,
                        pid=incoming.id,
                        attrs={"player_off": outgoing.id, "player_on": incoming.id},
                    )
                    roster[tid][7] = incoming
                    if owner == outgoing.id:
                        owner = incoming.id
                    subs.add(tid)
        if goal_index < len(goals) and t >= goals[goal_index][0] * 60_000:
            scoring = "harbor" if goals[goal_index][1] == "home" else "vale"
            if scoring != team:
                switch(scoring, "scoring_sequence")
            # Preceding pass and reception into the scoring area are explicit.
            x, y = min(x, 78), max(20, min(48, y))
            scorer = home.players[8].id if scoring == "harbor" else away.players[8].id
            p = add(
                EventType.PASS,
                end=(91, 34),
                attrs={"receiver_id": scorer, "distance_m": round(math.hypot(91 - x, 34 - y), 2)},
            )
            x, y, owner = 91, 34, scorer
            t += 1500
            add(EventType.RECEPTION, links=[p.event_id])
            shot = add(
                EventType.SHOT,
                end=(105, 34),
                outcome="on_target",
                attrs={"shot_speed_kmh": rng.randint(65, 100)},
            )
            t += 300
            add(EventType.GOAL, end=(105, 34), outcome="scored", links=[shot.event_id])
            x, y = 52.5, 34
            switch("vale" if team == "harbor" else "harbor", "kickoff")
            goal_index += 1
            continue
        pressing = sid == "pressing" and 3_600_000 <= t <= 4_900_000
        if pressing and team == "vale" and rng.random() < 0.30:
            # Vale's short build-up is disrupted; Harbor recover in the attacking third.
            x, y = rng.uniform(12, 30), rng.uniform(12, 56)
            add(EventType.PRESSURE, tid="harbor", end=(105 - x, 68 - y))
            add(EventType.INTERCEPTION, tid="harbor", end=(105 - x, 68 - y))
            switch("harbor", "high_press", high=True)
            continue
        r = rng.random()
        defensive = sid == "defensive"
        if r < 0.48:
            receiver = rng.choice([p for p in roster[team][1:] if p.id != owner])
            progressive = 4 if defensive else (12 if sid == "counter" and team == "harbor" else 7)
            ex = max(4, min(101, x + rng.uniform(-18, progressive)))
            ey = max(2, min(66, y + rng.uniform(-17, 17)))
            success = rng.random() < (0.91 if sid == "counter" and team == "vale" else 0.83)
            p = add(
                EventType.PASS,
                end=(ex, ey),
                outcome="complete" if success else "incomplete",
                attrs={"receiver_id": receiver.id, "distance_m": round(math.hypot(ex - x, ey - y), 2)},
            )
            x, y = ex, ey
            if success:
                t += 450
                owner = receiver.id
                add(EventType.RECEPTION, links=[p.event_id])
            else:
                switch()
        elif r < 0.68:
            ex = min(100, max(3, x + rng.uniform(-4, 17 if not defensive else 8)))
            ey = min(66, max(2, y + rng.uniform(-6, 6)))
            add(
                EventType.CARRY,
                end=(ex, ey),
                attrs={"distance_m": round(math.hypot(ex - x, ey - y), 2), "duration_ms": 3500},
            )
            x, y = ex, ey
        elif r < 0.72 and x > (83 if defensive else 70):
            add(
                EventType.SHOT,
                end=(105, rng.uniform(27, 41)),
                outcome="on_target" if rng.random() < 0.4 else "off_target",
                attrs={"shot_speed_kmh": rng.randint(55, 110)},
            )
            x, y = 90, 34
            switch(reason="shot_ended")
        elif r < 0.81:
            other = "vale" if team == "harbor" else "harbor"
            add(EventType.PRESSURE, tid=other, end=(105 - x, 68 - y))
            if rng.random() < 0.30:
                add(EventType.TACKLE, tid=other, end=(105 - x, 68 - y))
                switch(reason="tackle")
        elif r < 0.84:
            other = "vale" if team == "harbor" else "harbor"
            add(EventType.FOUL, tid=other, end=(105 - x, 68 - y))
            add(EventType.SET_PIECE, attrs={"kind": "free_kick"})
        elif r < 0.88 and x < 35:
            ex = min(95, x + rng.uniform(25, 50))
            add(EventType.CLEARANCE, end=(ex, y))
            x = ex
            switch(reason="clearance")
        else:
            # The counter scenario gives Vale longer possession chains.
            if not (sid == "counter" and team == "vale" and rng.random() < 0.65):
                add(
                    EventType.INTERCEPTION,
                    tid="vale" if team == "harbor" else "harbor",
                    end=(105 - x, 68 - y),
                )
                switch(reason="interception")
                if sid == "counter" and team == "harbor":
                    x = min(x, 40)
                    for _ in range(3):
                        ex = min(99, x + 20)
                        t += 3000
                        add(
                            EventType.CARRY,
                            end=(ex, y),
                            attrs={"duration_ms": 3000, "distance_m": ex - x, "counter_break": True},
                        )
                        x = ex
    t = 5_400_000
    add(EventType.METADATA, attrs={"phase": "full_time"}, outcome="neutral")
    return Match(id=sid, title=title, description=desc, seed=seed, home=home, away=away, events=events)


def generate_all(density: float = 1):
    return [generate(s[0], density) for s in SCENARIOS]
