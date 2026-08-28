"""Immutable command envelopes for all future state mutations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Self

from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.domain.types import FrozenJsonValue, JsonValue, freeze_payload


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    """Transport-independent request to mutate authoritative game state."""

    command_id: CommandId
    game_id: GameId
    command_type: str
    payload: Mapping[str, FrozenJsonValue] = field(default_factory=dict)
    player_id: PlayerId | None = None
    expected_state_version: int | None = None
    client_timestamp: str | None = None

    def __post_init__(self) -> None:
        if not self.command_type.strip():
            raise ValueError("command_type must not be blank")
        if self.expected_state_version is not None and self.expected_state_version < 0:
            raise ValueError("expected_state_version must be non-negative")
        object.__setattr__(self, "payload", freeze_payload(self.payload))

    @classmethod
    def create(
        cls,
        *,
        command_id: CommandId,
        game_id: GameId,
        command_type: str,
        payload: Mapping[str, JsonValue] | None = None,
        player_id: PlayerId | None = None,
        expected_state_version: int | None = None,
        client_timestamp: str | None = None,
    ) -> Self:
        """Create an envelope while deeply freezing caller-owned payload data."""
        return cls(
            command_id=command_id,
            game_id=game_id,
            command_type=command_type,
            payload=freeze_payload(payload or {}),
            player_id=player_id,
            expected_state_version=expected_state_version,
            client_timestamp=client_timestamp,
        )
