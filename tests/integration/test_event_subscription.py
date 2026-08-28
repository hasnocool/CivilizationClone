# tests/integration/test_event_subscription.py
from __future__ import annotations

import asyncio

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig


async def _exercise_retry_subscription() -> None:
    manager = GameManager()
    game_id = GameId("subscription-game")
    first = PlayerId("p1")
    second = PlayerId("p2")
    await manager.create_game(
        game_id=game_id,
        seed=200,
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    for index, player_id in enumerate((first, second), start=1):
        result = await manager.process(
            CommandEnvelope.create(
                command_id=CommandId(f"join-{index}"),
                game_id=game_id,
                command_type="JoinGame",
                player_id=player_id,
                payload={"name": f"Player {index}"},
            )
        )
        assert result.accepted
    assert (
        await manager.process(
            CommandEnvelope.create(
                command_id=CommandId("start"),
                game_id=game_id,
                command_type="StartGame",
            )
        )
    ).accepted

    queue = await manager.subscribe(game_id)
    command = CommandEnvelope.create(
        command_id=CommandId("choose-once"),
        game_id=game_id,
        command_type="ChooseResearch",
        player_id=first,
        payload={"technology_id": "surveying"},
    )
    first_result = await manager.process(command)
    assert first_result.accepted
    event = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event.event_type == "ResearchSelected"
    assert queue.empty()

    retry_result = await manager.process(command)
    assert retry_result == first_result
    assert queue.empty()
    manager.unsubscribe(game_id, queue)


def test_idempotent_retry_does_not_republish_events() -> None:
    asyncio.run(_exercise_retry_subscription())
