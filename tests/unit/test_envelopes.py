# tests/unit/test_envelopes.py
from dataclasses import FrozenInstanceError

import pytest

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import CommandId, EventId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope


def test_command_envelope_deeply_freezes_payload() -> None:
    payload = {"path": ["north", "east"], "options": {"fast": True}}
    command = CommandEnvelope.create(
        command_id=CommandId("cmd-1"),
        game_id=GameId("game-1"),
        player_id=PlayerId("player-1"),
        expected_state_version=3,
        command_type="MoveUnit",
        payload=payload,
    )
    payload["path"] = ["south"]

    assert command.payload["path"] == ("north", "east")
    with pytest.raises(TypeError):
        command.payload["options"]["fast"] = False  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        command.command_type = "Other"  # type: ignore[misc]


def test_event_envelope_validates_monotonic_fields() -> None:
    event = EventEnvelope.create(
        event_id=EventId("evt-1"),
        game_id=GameId("game-1"),
        sequence=1,
        event_type="GameCreated",
        state_version=1,
        causation_command_id=CommandId("cmd-1"),
    )

    assert event.sequence == 1
    assert event.state_version == 1


@pytest.mark.parametrize(
    ("sequence", "state_version"),
    [(-1, 0), (0, -1)],
)
def test_event_envelope_rejects_negative_fields(sequence: int, state_version: int) -> None:
    with pytest.raises(ValueError):
        EventEnvelope(
            event_id=EventId("evt-1"),
            game_id=GameId("game-1"),
            sequence=sequence,
            event_type="GameCreated",
            state_version=state_version,
        )


def test_direct_constructor_also_freezes_payload() -> None:
    nested = {"nested": {"values": ("a", "b")}}
    command = CommandEnvelope(
        command_id=CommandId("cmd-direct"),
        game_id=GameId("game-1"),
        command_type="NoOp",
        payload=nested,
    )

    with pytest.raises(TypeError):
        command.payload["nested"]["values"] = ("changed",)  # type: ignore[index]
