# tests/unit/test_session_commands.py
import logging

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
        command_id=CommandId(f"unit-cmd-{index}"),
        game_id=game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
        expected_state_version=version,
    )


def _engine(logger: logging.Logger | None = None) -> tuple[GameEngine, PlayerId, PlayerId]:
    game_id = GameId("game-unit")
    engine = GameEngine.create(
        game_id=game_id,
        seed=88,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
        logger=logger,
    )
    p1 = PlayerId("p1")
    p2 = PlayerId("p2")
    engine.process(_command(1, game_id, "JoinGame", p1, {"name": "One"}))
    engine.process(_command(2, game_id, "JoinGame", p2, {"name": "Two"}))
    engine.process(_command(3, game_id, "StartGame"))
    return engine, p1, p2


def _unit_and_neighbor(engine: GameEngine, player_id: PlayerId):
    unit = next(unit for unit in engine.session.units.values() if unit.owner_id == player_id)
    destination = next(
        coord
        for coord in neighbors(unit.position)
        if (tile := engine.session.world.tiles.get(coord)) is not None and tile.passable
    )
    return unit.unit_id, destination


def test_command_retry_is_idempotent() -> None:
    engine, p1, _ = _engine()
    unit_id, destination = _unit_and_neighbor(engine, p1)
    command = _command(
        10,
        engine.session.game_id,
        "MoveUnit",
        p1,
        {"unit_id": unit_id, "q": destination.q, "r": destination.r},
    )

    first = engine.process(command)
    state_after = engine.state_hash()
    event_count = len(engine.event_log)
    second = engine.process(command)

    assert first == second
    assert engine.state_hash() == state_after
    assert len(engine.event_log) == event_count


def test_stale_state_version_is_safe_rejection() -> None:
    engine, p1, _ = _engine()
    unit_id, destination = _unit_and_neighbor(engine, p1)
    result = engine.process(
        _command(
            11,
            engine.session.game_id,
            "MoveUnit",
            p1,
            {"unit_id": unit_id, "q": destination.q, "r": destination.r},
            version=0,
        )
    )

    assert not result.accepted
    assert result.feedback[0].code == "STALE_STATE_VERSION"


def test_non_active_player_cannot_move_unit() -> None:
    engine, p1, p2 = _engine()
    unit_id, destination = _unit_and_neighbor(engine, p1)
    result = engine.process(
        _command(
            12,
            engine.session.game_id,
            "MoveUnit",
            p2,
            {"unit_id": unit_id, "q": destination.q, "r": destination.r},
        )
    )

    assert not result.accepted
    assert result.feedback[0].code == "MOVE_REJECTED"
    assert result.feedback[0].context["reason"] == "not_active_player"


def test_logging_does_not_change_session_or_event_results() -> None:
    logger = logging.getLogger("civilization_clone.test.v03")
    logger.handlers = [logging.NullHandler()]
    logger.propagate = False
    with_logs, p1, _ = _engine(logger)
    without_logs, _, _ = _engine()

    unit_with_logs, destination_with_logs = _unit_and_neighbor(with_logs, p1)
    unit_without_logs, destination_without_logs = _unit_and_neighbor(without_logs, p1)
    with_logs.process(
        _command(
            20,
            with_logs.session.game_id,
            "MoveUnit",
            p1,
            {
                "unit_id": unit_with_logs,
                "q": destination_with_logs.q,
                "r": destination_with_logs.r,
            },
        )
    )
    without_logs.process(
        _command(
            20,
            without_logs.session.game_id,
            "MoveUnit",
            p1,
            {
                "unit_id": unit_without_logs,
                "q": destination_without_logs.q,
                "r": destination_without_logs.r,
            },
        )
    )

    assert with_logs.state_hash() == without_logs.state_hash()
    assert with_logs.event_hash() == without_logs.event_hash()
