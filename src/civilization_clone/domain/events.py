"""Immutable domain event envelopes emitted by successful commands."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Self

from civilization_clone.domain.ids import CommandId, EventId, GameId
from civilization_clone.domain.types import FrozenJsonValue, JsonValue, freeze_payload


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Ordered immutable fact produced by the authoritative engine."""

    event_id: EventId
    game_id: GameId
    sequence: int
    event_type: str
    state_version: int
    payload: Mapping[str, FrozenJsonValue] = field(default_factory=dict)
    causation_command_id: CommandId | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.state_version < 0:
            raise ValueError("state_version must be non-negative")
        if not self.event_type.strip():
            raise ValueError("event_type must not be blank")
        object.__setattr__(self, "payload", freeze_payload(self.payload))

    @classmethod
    def create(
        cls,
        *,
        event_id: EventId,
        game_id: GameId,
        sequence: int,
        event_type: str,
        state_version: int,
        payload: Mapping[str, JsonValue] | None = None,
        causation_command_id: CommandId | None = None,
    ) -> Self:
        """Create an event while deeply freezing caller-owned payload data."""
        return cls(
            event_id=event_id,
            game_id=game_id,
            sequence=sequence,
            event_type=event_type,
            state_version=state_version,
            payload=freeze_payload(payload or {}),
            causation_command_id=causation_command_id,
        )
