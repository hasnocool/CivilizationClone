# tests/integration/test_application_manager.py
from __future__ import annotations

import asyncio

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig


async def _exercise_concurrent_commands() -> None:
    manager = GameManager()
    game_id = GameId("serialized-game")
    first = PlayerId("p1")
    second = PlayerId("p2")
    await manager.create_game(
        game_id=game_id,
        seed=700,
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    assert (
        await manager.process(
            CommandEnvelope.create(
                command_id=CommandId("join-1"),
                game_id=game_id,
                command_type="JoinGame",
                player_id=first,
                payload={"name": "One"},
            )
        )
    ).accepted
    assert (
        await manager.process(
            CommandEnvelope.create(
                command_id=CommandId("join-2"),
                game_id=game_id,
                command_type="JoinGame",
                player_id=second,
                payload={"name": "Two"},
            )
        )
    ).accepted
    assert (
        await manager.process(
            CommandEnvelope.create(
                command_id=CommandId("start"),
                game_id=game_id,
                command_type="StartGame",
            )
        )
    ).accepted

    engine = await manager.get_engine(game_id)
    version = engine.session.state_version
    commands = (
        CommandEnvelope.create(
            command_id=CommandId("concurrent-research-a"),
            game_id=game_id,
            command_type="ChooseResearch",
            player_id=first,
            expected_state_version=version,
            payload={"technology_id": "surveying"},
        ),
        CommandEnvelope.create(
            command_id=CommandId("concurrent-research-b"),
            game_id=game_id,
            command_type="ChooseResearch",
            player_id=first,
            expected_state_version=version,
            payload={"technology_id": "masonry"},
        ),
    )
    results = await asyncio.gather(*(manager.process(command) for command in commands))

    assert sum(result.accepted for result in results) == 1
    rejected = next(result for result in results if not result.accepted)
    assert rejected.feedback[0].code == "STALE_STATE_VERSION"


def test_per_game_mutation_stream_is_serialized() -> None:
    asyncio.run(_exercise_concurrent_commands())
