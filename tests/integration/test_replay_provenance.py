from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import GameEngine
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.persistence.codec import engine_to_document
from civilization_clone.persistence.replay import ReplayVerificationError
from civilization_clone.persistence.sqlite_store import SqliteGameStore


def _command(
    index: int,
    game_id: GameId,
    kind: str,
    player_id: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"legacy-provenance-{index}"),
        game_id=game_id,
        command_type=kind,
        player_id=player_id,
        payload=payload or {},  # type: ignore[arg-type]
    )


async def _write_legacy_snapshot(store: SqliteGameStore, engine: GameEngine) -> None:
    document = engine_to_document(engine)
    document["save_version"] = 1
    document.pop("replay_complete", None)
    state = document["state"]
    assert isinstance(state, dict)
    for player in state.get("players", []):
        assert isinstance(player, dict)
        player.pop("civilization_id", None)
    document["state_hash"] = state_hash(state)

    payload = json.dumps(document, sort_keys=True, separators=(",", ":"))
    event_rows = [
        (
            int(event["sequence"]),
            json.dumps(event, sort_keys=True, separators=(",", ":")),
        )
        for event in document["events"]
    ]
    await asyncio.to_thread(
        store._save_sync,
        str(engine.session.game_id),
        payload,
        str(document["state_hash"]),
        str(document["event_hash"]),
        event_rows,
        None,
    )


async def _exercise(path: Path) -> None:
    game_id = GameId("legacy-provenance-game")
    first = PlayerId("p1")
    second = PlayerId("p2")
    engine = GameEngine.create(
        game_id=game_id,
        seed=707,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.8.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    assert engine.process(_command(1, game_id, "JoinGame", first, {"name": "One"})).accepted
    assert engine.process(_command(2, game_id, "JoinGame", second, {"name": "Two"})).accepted
    assert engine.process(_command(3, game_id, "StartGame")).accepted

    store = SqliteGameStore(path)
    await store.initialize()
    await _write_legacy_snapshot(store, engine)

    manager = GameManager(store)
    restored = await manager.get_engine(game_id)
    assert all(
        str(player.civilization_id) == "river_compact"
        for player in restored.session.players.values()
    )
    assert not await store.replay_complete(game_id)
    with pytest.raises(ReplayVerificationError, match="predates"):
        await manager.verify_replay(game_id)

    selected = await manager.process(
        _command(4, game_id, "ChooseResearch", first, {"technology_id": "surveying"})
    )
    assert selected.accepted

    restarted = GameManager(store)
    await restarted.get_engine(game_id)
    assert not await store.replay_complete(game_id)
    with pytest.raises(ReplayVerificationError, match="predates"):
        await restarted.verify_replay(game_id)


def test_legacy_migration_never_claims_complete_replay_history(tmp_path: Path) -> None:
    asyncio.run(_exercise(tmp_path / "legacy.sqlite3"))
