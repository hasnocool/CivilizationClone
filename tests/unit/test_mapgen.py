# tests/unit/test_mapgen.py
import logging

from civilization_clone.domain.ids import GameId
from civilization_clone.engine.mapgen import MapGenerationConfig, generate_world
from civilization_clone.engine.state_hash import state_hash


def _result_hash(seed: int) -> str:
    result = generate_world(
        game_id=GameId("game-map"),
        seed=seed,
        config=MapGenerationConfig(radius=4, player_count=3),
        start_sequence=5,
        state_version=7,
    )
    return state_hash({"world": result.world.canonical_state(), "events": result.events})


def test_same_seed_produces_same_map_and_events() -> None:
    assert _result_hash(1234) == _result_hash(1234)


def test_different_seed_changes_generated_world() -> None:
    first = generate_world(game_id=GameId("game-map"), seed=1234)
    second = generate_world(game_id=GameId("game-map"), seed=5678)

    assert state_hash(first.world.canonical_state()) != state_hash(second.world.canonical_state())


def test_spawns_are_unique_passable_existing_tiles() -> None:
    result = generate_world(
        game_id=GameId("game-map"),
        seed=44,
        config=MapGenerationConfig(radius=4, player_count=4),
    )

    assert len(result.world.spawns) == 4
    assert len(set(result.world.spawns)) == 4
    assert all(result.world.tile(coord).passable for coord in result.world.spawns)


def test_generation_events_use_requested_sequence_and_state_version() -> None:
    result = generate_world(
        game_id=GameId("game-map"),
        seed=44,
        start_sequence=11,
        state_version=3,
    )

    assert [event.sequence for event in result.events] == [11, 12]
    assert [event.state_version for event in result.events] == [3, 3]
    assert [event.event_type for event in result.events] == [
        "MapGenerationStarted",
        "MapGenerated",
    ]


def test_runtime_logging_does_not_change_generated_world() -> None:
    logger = logging.getLogger("civilization_clone.test.mapgen")
    logger.handlers = [logging.NullHandler()]
    logger.propagate = False
    with_logging = generate_world(game_id=GameId("game-map"), seed=9001, logger=logger)
    without_logging = generate_world(game_id=GameId("game-map"), seed=9001)

    assert state_hash(with_logging.world.canonical_state()) == state_hash(
        without_logging.world.canonical_state()
    )
    assert state_hash(with_logging.events) == state_hash(without_logging.events)
