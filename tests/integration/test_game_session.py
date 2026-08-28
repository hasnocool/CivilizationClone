# tests/integration/test_game_session.py
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.hexgrid import neighbors
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import GameEngine


def _command(
    index: int,
    game_id: GameId,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
    version: int | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"cmd-{index}"),
        game_id=game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
        expected_state_version=version,
    )


def _setup_engine() -> tuple[GameEngine, PlayerId, PlayerId]:
    game_id = GameId("game-1")
    engine = GameEngine.create(
        game_id=game_id,
        seed=77,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    player_one = PlayerId("p1")
    player_two = PlayerId("p2")
    assert engine.process(_command(1, game_id, "JoinGame", player_one, {"name": "One"})).accepted
    assert engine.process(_command(2, game_id, "JoinGame", player_two, {"name": "Two"})).accepted
    assert engine.process(_command(3, game_id, "StartGame")).accepted
    return engine, player_one, player_two


def _legal_neighbor(engine: GameEngine, player_id: PlayerId):
    unit = next(unit for unit in engine.session.units.values() if unit.owner_id == player_id)
    for coord in neighbors(unit.position):
        tile = engine.session.world.tiles.get(coord)
        occupied = any(other.position == coord for other in engine.session.units.values())
        if tile is not None and tile.passable and not occupied:
            return unit.unit_id, coord
    raise AssertionError("expected at least one legal neighboring tile")


def _run_script() -> GameEngine:
    engine, player_one, player_two = _setup_engine()
    unit_one, destination_one = _legal_neighbor(engine, player_one)
    move_one = _command(
        4,
        engine.session.game_id,
        "MoveUnit",
        player_one,
        {"unit_id": unit_one, "q": destination_one.q, "r": destination_one.r},
    )
    assert engine.process(move_one).accepted
    assert engine.process(_command(5, engine.session.game_id, "EndTurn", player_one)).accepted

    unit_two, destination_two = _legal_neighbor(engine, player_two)
    move_two = _command(
        6,
        engine.session.game_id,
        "MoveUnit",
        player_two,
        {"unit_id": unit_two, "q": destination_two.q, "r": destination_two.r},
    )
    assert engine.process(move_two).accepted
    assert engine.process(_command(7, engine.session.game_id, "EndTurn", player_two)).accepted
    return engine


def test_two_player_script_is_deterministic() -> None:
    first = _run_script()
    second = _run_script()

    assert first.state_hash() == second.state_hash()
    assert first.event_hash() == second.event_hash()
    assert first.session.turn == 2
    assert first.session.current_player_id == PlayerId("p1")
    player_one_unit = next(
        unit for unit in first.session.units.values() if unit.owner_id == PlayerId("p1")
    )
    assert player_one_unit.movement_remaining == player_one_unit.definition.movement


def test_event_journal_is_contiguous_after_multiple_turn_commands() -> None:
    engine = _run_script()
    events = engine.event_log.snapshot()

    assert [event.sequence for event in events] == list(range(len(events)))
    assert all(
        current.state_version <= following.state_version
        for current, following in zip(events, events[1:], strict=False)
    )
