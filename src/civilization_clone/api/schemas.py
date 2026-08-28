"""Pydantic v2 transport schemas for the public /api/v1 surface."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateGameRequest(BaseModel):
    """Create one deterministic game and its map."""

    model_config = ConfigDict(extra="forbid")

    game_id: str = Field(min_length=1)
    seed: int
    map_radius: int = Field(default=4, ge=2)
    player_count: int = Field(default=2, ge=2, le=4)
    water_percent: int = Field(default=20, ge=0, le=60)
    resource_percent: int = Field(default=18, ge=0, le=60)


class CommandRequest(BaseModel):
    """Transport representation of one engine command."""

    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    command_type: str = Field(min_length=1)
    player_id: str | None = None
    expected_state_version: int | None = Field(default=None, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)
    client_timestamp: str | None = None


class FeedbackResponse(BaseModel):
    code: str
    message: str
    severity: str
    context: dict[str, str]


class EventResponse(BaseModel):
    event_id: str
    sequence: int
    event_type: str
    state_version: int
    payload: dict[str, Any]


class CommandResponse(BaseModel):
    accepted: bool
    state_version: int
    events: list[EventResponse]
    feedback: list[FeedbackResponse]


class GameCreatedResponse(BaseModel):
    game_id: str
    seed: int
    state_version: int
    status: str


class HealthResponse(BaseModel):
    status: str = "ok"
