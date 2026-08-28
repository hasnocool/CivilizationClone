from __future__ import annotations

import asyncio
from pathlib import Path

from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import GameEngine
from civilization_clone.persistence.sqlite_store import SqliteGameStore


def _command(
    index: int,
    engine: GameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"persist-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _engine() -> tuple[GameEngine, PlayerId, PlayerId, CommandEnvelope]:
    engine = GameEngine.create(
        game_id=GameId("persist-game"),
        seed=808,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    join_first = _command(
        1,
        engine,
        "JoinGame",
        first,
        {"name": "One", "civilization_id": "river_compact"},
    )
    assert engine.process(join_first).accepted
    assert engine.process(
        _command(
            2,
            engine,
            "JoinGame",
            second,
            {"name": "Two", "civilization_id": "horizon_league"},
        )
    ).accepted
    assert engine.process(_command(3, engine, "StartGame")).accepted
    return engine, first, second, join_first


async def _round_trip(path: Path) -> None:
    engine, _, second, retry_command = _engine()
    store = SqliteGameStore(path)
    await store.initialize()
    await store.save(engine)

    loaded = await store.load(engine.session.game_id)
    assert loaded.state_hash() == engine.state_hash()
    assert loaded.event_hash() == engine.event_hash()
    assert str(loaded.session.players[second].civilization_id) == "horizon_league"
    assert await store.event_count(engine.session.game_id) == len(engine.event_log)

    before_hash = loaded.state_hash()
    retry = loaded.process(retry_command)
    assert retry.accepted
    assert loaded.state_hash() == before_hash


def test_sqlite_save_reload_preserves_hashes_idempotency_and_civilization(tmp_path: Path) -> None:
    asyncio.run(_round_trip(tmp_path / "games.sqlite3"))
