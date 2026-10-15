"""Shared validated event and publication contracts. Coordinates are metres, team-normalized."""
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventType(StrEnum):
    PASS = "pass"
    RECEPTION = "reception"
    CARRY = "carry"
    SHOT = "shot"
    GOAL = "goal"
    TACKLE = "tackle"
    INTERCEPTION = "interception"
    CLEARANCE = "clearance"
    RECOVERY = "recovery"
    TURNOVER = "turnover"
    POSSESSION = "possession_change"
    PRESSURE = "pressure"
    FOUL = "foul"
    SET_PIECE = "set_piece"
    SUBSTITUTION = "substitution"
    METADATA = "metadata"


class Player(BaseModel):
    id: str
    team_id: str
    name: str
    number: int
    position: str


class Team(BaseModel):
    id: str
    name: str
    short: str
    color: str
    players: list[Player]


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str = Field(pattern=r"^[a-z0-9_-]{1,80}$")
    match_id: str = Field(pattern=r"^[a-z0-9_-]{1,50}$")
    sequence_number: int = Field(ge=0)
    period: Literal[1, 2]
    match_clock_ms: int = Field(ge=0, le=5_400_000)
    team_id: str
    player_id: str | None = None
    event_type: EventType
    start_x: float = Field(ge=0, le=105)
    start_y: float = Field(ge=0, le=68)
    end_x: float = Field(ge=0, le=105)
    end_y: float = Field(ge=0, le=68)
    outcome: Literal["complete", "incomplete", "on_target", "off_target", "scored", "neutral"] = "complete"
    related_event_ids: list[str] = Field(default_factory=list, max_length=12)
    event_attributes: dict[str, Any] = Field(default_factory=dict)
    synthetic_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def period_consistency(self):
        expected = 1 if self.match_clock_ms < 2_700_000 else 2
        if self.period != expected:
            raise ValueError("period does not match event time")
        if self.event_type == EventType.GOAL and (self.outcome != "scored" or not self.related_event_ids):
            raise ValueError("goal must link to a scoring shot")
        return self


class Match(BaseModel):
    id: str
    title: str
    description: str
    seed: int
    home: Team
    away: Team
    duration_ms: int = 5_400_000
    events: list[Event]
    provenance: str = "Original synthetic data · MatchWeave generator v1 · no real match data"


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: str
    team_id: str
    metric: Literal["goals", "shots", "recoveries", "pressure", "passes_completed", "final_third_entries"]
    value: float
    previous_value: float = 0
    window_start_ms: int
    window_end_ms: int
    source_event_ids: list[str] = Field(min_length=1)
    confidence: Literal["high", "moderate", "small sample"]
    reason_code: Literal["score", "shot_threat", "pressing", "territory", "circulation"]


class Overlay(BaseModel):
    overlay_id: str
    match_id: str
    start_ms: int
    end_ms: int
    overlay_type: Literal["lower_third", "stat_card", "score_bug"]
    heading: str
    supporting_statistic: str
    source_event_ids: list[str] = Field(min_length=1)
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0.05, "y": 0.78, "width": 0.6})
    audience: Literal["fan", "analyst", "broadcaster"]
    language: Literal["en", "hi", "es"]
    verification_status: Literal["verified"] = "verified"
