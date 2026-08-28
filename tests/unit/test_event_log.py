# tests/unit/test_event_log.py
import pytest

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import EventId, GameId
from civilization_clone.engine.event_log import EventLog, EventLogError
from civilization_clone.engine.state_hash import state_hash


def event(game_id: GameId, sequence: int, state_version: int) -> EventEnvelope:
    return EventEnvelope.create(
        event_id=EventId(f"evt-{sequence}"),
        game_id=game_id,
        sequence=sequence,
        event_type="TestEvent",
        state_version=state_version,
        payload={"value": sequence},
    )


def test_event_log_is_append_only_and_ordered() -> None:
    game_id = GameId("game-1")
    journal = EventLog(game_id)
    journal.append(event(game_id, 0, 1))
    journal.append(event(game_id, 1, 1))
    journal.append(event(game_id, 2, 2))

    assert journal.next_sequence == 3
    assert [item.sequence for item in journal.snapshot()] == [0, 1, 2]


def test_event_log_rejects_wrong_game_or_sequence() -> None:
    journal = EventLog(GameId("game-1"))
    with pytest.raises(EventLogError, match="game_id"):
        journal.append(event(GameId("game-2"), 0, 0))
    with pytest.raises(EventLogError, match="sequence"):
        journal.append(event(GameId("game-1"), 1, 0))


def test_event_log_rejects_state_version_regression() -> None:
    game_id = GameId("game-1")
    journal = EventLog(game_id)
    journal.append(event(game_id, 0, 3))
    with pytest.raises(EventLogError, match="state_version"):
        journal.append(event(game_id, 1, 2))


def test_same_events_produce_same_journal_hash() -> None:
    game_id = GameId("game-1")
    first = EventLog(game_id)
    second = EventLog(game_id)
    for sequence in range(4):
        first.append(event(game_id, sequence, sequence + 1))
        second.append(event(game_id, sequence, sequence + 1))

    assert state_hash(first.snapshot()) == state_hash(second.snapshot())
