# tests/integration/test_replay_transcript.py
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.persistence.replay import ReplayVerificationError, verify_replay
from civilization_clone.persistence.sqlite_store import SqliteGameStore


def _command(
    index: int,
    game_id: GameId,
    kind: str,
    player_id: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"replay-{index}"),
        game_id=game_id,
        command_type=kind,
        player_id=player_id,
        payload=payload or {},  # type: ignore[arg-type]
    )


async def _exercise(path: Path) -> None:
    game_id = GameId("replay-game")
    p1 = PlayerId("p1")
    p2 = PlayerId("p2")
    store = SqliteGameStore(path)
    manager = GameManager(store)
    await manager.create_game(
        game_id=game_id,
        seed=10101,
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    assert (await manager.process(_command(1, game_id, "JoinGame", p1, {"name": "One"}))).accepted
    assert (await manager.process(_command(2, game_id, "JoinGame", p2, {"name": "Two"}))).accepted
    assert (await manager.process(_command(3, game_id, "StartGame"))).accepted
    assert (
        await manager.process(
            _command(4, game_id, "ChooseResearch", p1, {"technology_id": "surveying"})
        )
    ).accepted
    assert (await manager.process(_command(5, game_id, "EndTurn", p1))).accepted

    live = await manager.get_engine(game_id)
    report = await manager.verify_replay(game_id)
    assert report.matched
    assert report.command_count == 5

    restored_manager = GameManager(store)
    restored = await restored_manager.get_engine(game_id)
    assert restored.state_hash() == live.state_hash()
    assert restored.event_hash() == live.event_hash()
    assert len(await restored_manager.accepted_commands(game_id)) == 5
    assert (await restored_manager.verify_replay(game_id)).matched

    transcript = await restored_manager.accepted_commands(game_id)
    with pytest.raises(ReplayVerificationError):
        verify_replay(restored, transcript[:-1])


def test_durable_accepted_commands_replay_to_live_hash(tmp_path: Path) -> None:
    asyncio.run(_exercise(tmp_path / "replay.sqlite3"))
