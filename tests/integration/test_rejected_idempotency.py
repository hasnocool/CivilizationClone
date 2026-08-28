# tests/integration/test_rejected_idempotency.py
from __future__ import annotations

import asyncio
from pathlib import Path

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.persistence.sqlite_store import SqliteGameStore


async def _exercise(path: Path) -> None:
    game_id = GameId("rejected-idempotency")
    p1 = PlayerId("p1")
    p2 = PlayerId("p2")
    manager = GameManager(SqliteGameStore(path))
    await manager.create_game(
        game_id=game_id,
        seed=1234,
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    for index, player in enumerate((p1, p2), start=1):
        assert (
            await manager.process(
                CommandEnvelope.create(
                    command_id=CommandId(f"join-{index}"),
                    game_id=game_id,
                    command_type="JoinGame",
                    player_id=player,
                    payload={"name": str(player)},
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

    rejected_command = CommandEnvelope.create(
        command_id=CommandId("rejected-end-turn"),
        game_id=game_id,
        command_type="EndTurn",
        player_id=p1,
    )
    rejected = await manager.process(rejected_command)
    assert not rejected.accepted
    assert rejected.feedback[0].code == "MANDATORY_CHOICE_REQUIRED"

    assert (
        await manager.process(
            CommandEnvelope.create(
                command_id=CommandId("choose-research"),
                game_id=game_id,
                command_type="ChooseResearch",
                player_id=p1,
                payload={"technology_id": "surveying"},
            )
        )
    ).accepted

    restored = GameManager(SqliteGameStore(path))
    retry = await restored.process(rejected_command)
    assert not retry.accepted
    assert retry.feedback[0].code == "MANDATORY_CHOICE_REQUIRED"
    engine = await restored.get_engine(game_id)
    assert engine.session.current_player_id == p1


def test_rejected_command_idempotency_survives_restart(tmp_path: Path) -> None:
    asyncio.run(_exercise(tmp_path / "idempotency.sqlite3"))
