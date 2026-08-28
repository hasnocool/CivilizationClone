from __future__ import annotations

import asyncio
import logging

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig


class ExplodingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        raise RuntimeError("diagnostic sink failed")


def _logger() -> logging.Logger:
    logger = logging.getLogger("civilization_clone.test.exploding")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(ExplodingHandler())
    return logger


async def _run(logger: logging.Logger | None) -> tuple[str, str]:
    game_id = GameId("logging-isolation-game")
    manager = GameManager(logger=logger)
    engine = await manager.create_game(
        game_id=game_id,
        seed=6060,
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    commands = (
        CommandEnvelope.create(
            command_id=CommandId("logging-join-1"),
            game_id=game_id,
            command_type="JoinGame",
            player_id=first,
            payload={"name": "One", "civilization_id": "river_compact"},
        ),
        CommandEnvelope.create(
            command_id=CommandId("logging-join-2"),
            game_id=game_id,
            command_type="JoinGame",
            player_id=second,
            payload={"name": "Two", "civilization_id": "horizon_league"},
        ),
        CommandEnvelope.create(
            command_id=CommandId("logging-start"),
            game_id=game_id,
            command_type="StartGame",
        ),
    )
    for command in commands:
        result = await manager.process(command)
        assert result.accepted
    return engine.state_hash(), engine.event_hash()


def test_broken_runtime_logger_does_not_change_command_results_or_hashes() -> None:
    without_logging = asyncio.run(_run(None))
    with_broken_logging = asyncio.run(_run(_logger()))

    assert with_broken_logging == without_logging
