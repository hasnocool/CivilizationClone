from __future__ import annotations

import asyncio
import json
from pathlib import Path

from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.advanced import AdvancedGameEngine
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.persistence.codec import engine_to_document
from civilization_clone.persistence.sqlite_store import SqliteGameStore


def _command(
    index: int,
    engine: AdvancedGameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"trade-migration-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


async def _exercise(path: Path) -> None:
    engine = AdvancedGameEngine.create(
        game_id=GameId("v2-trade-migration"),
        seed=144,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    assert engine.process(_command(1, engine, "JoinGame", first, {"name": "One"})).accepted
    assert engine.process(_command(2, engine, "JoinGame", second, {"name": "Two"})).accepted
    assert engine.process(_command(3, engine, "StartGame")).accepted

    document = engine_to_document(engine)
    document["save_version"] = 2
    state = document["state"]
    assert isinstance(state, dict)
    diplomacy = state["diplomacy"]
    assert isinstance(diplomacy, list)
    for relationship in diplomacy:
        assert isinstance(relationship, dict)
        relationship.pop("pending_trade", None)
        relationship.pop("completed_trades", None)
        relationship.pop("last_trade_turn", None)
    document["state_hash"] = state_hash(state)

    payload = json.dumps(document, sort_keys=True, separators=(",", ":"))
    event_rows = [
        (
            int(event["sequence"]),
            json.dumps(event, sort_keys=True, separators=(",", ":")),
        )
        for event in document["events"]
    ]
    store = SqliteGameStore(path)
    await store.initialize()
    await asyncio.to_thread(
        store._save_sync,
        str(engine.session.game_id),
        payload,
        str(document["state_hash"]),
        str(document["event_hash"]),
        event_rows,
        None,
    )

    restored = await store.load(engine.session.game_id)
    assert isinstance(restored, AdvancedGameEngine)
    assert restored.session.diplomacy
    for relationship in restored.session.diplomacy.values():
        assert relationship.pending_trade is None
        assert relationship.completed_trades == 0
        assert relationship.last_trade_turn is None


def test_v2_sqlite_save_migrates_to_trade_defaults_after_raw_hash_verification(
    tmp_path: Path,
) -> None:
    asyncio.run(_exercise(tmp_path / "v2-migration.sqlite3"))
