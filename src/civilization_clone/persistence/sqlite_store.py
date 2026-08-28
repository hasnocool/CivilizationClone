"""Async-safe SQLite persistence using explicit worker-thread boundaries."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from civilization_clone.domain.ids import GameId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.session import GameEngine
from civilization_clone.persistence.codec import engine_from_document, engine_to_document
from civilization_clone.persistence.replay import command_from_data, command_to_data


class ReplayDivergenceError(RuntimeError):
    """Raised when durable checkpoints disagree with deterministic engine state."""


@dataclass(frozen=True, slots=True)
class SqliteGameStore:
    """Durable POC save/event/command store that never blocks an async event loop."""

    path: Path

    async def initialize(self) -> None:
        """Create persistence tables without blocking the caller's event loop."""
        await asyncio.to_thread(self._initialize_sync)

    async def save(
        self,
        engine: GameEngine,
        *,
        accepted_commands: tuple[CommandEnvelope, ...] | None = None,
    ) -> None:
        """Persist one snapshot plus immutable deterministic events/commands."""
        document = engine_to_document(engine)
        payload = json.dumps(document, sort_keys=True, separators=(",", ":"))
        event_rows = [
            (
                int(event["sequence"]),
                json.dumps(event, sort_keys=True, separators=(",", ":")),
            )
            for event in document["events"]
        ]
        command_rows = None
        if accepted_commands is not None:
            command_rows = [
                (
                    index,
                    str(command.command_id),
                    json.dumps(command_to_data(command), sort_keys=True, separators=(",", ":")),
                )
                for index, command in enumerate(accepted_commands)
            ]
        await asyncio.to_thread(
            self._save_sync,
            str(engine.session.game_id),
            payload,
            str(document["state_hash"]),
            str(document["event_hash"]),
            event_rows,
            command_rows,
        )

    async def load(self, game_id: GameId) -> GameEngine:
        """Restore one game and verify snapshot/event hashes and event continuity."""
        row, durable_events = await asyncio.to_thread(self._load_sync, str(game_id))
        if row is None:
            raise KeyError(f"game not found: {game_id}")
        payload, expected_state_hash, expected_event_hash = row
        document = json.loads(payload)
        engine = engine_from_document(document)
        if engine.state_hash() != expected_state_hash:
            raise ReplayDivergenceError("restored state hash diverged from durable checkpoint")
        if engine.event_hash() != expected_event_hash:
            raise ReplayDivergenceError("restored event hash diverged from durable checkpoint")

        snapshot_events = document.get("events", [])
        if len(snapshot_events) != len(durable_events):
            raise ReplayDivergenceError("durable event count differs from save snapshot")
        for expected_sequence, (sequence, serialized) in enumerate(durable_events):
            if sequence != expected_sequence:
                raise ReplayDivergenceError("durable event sequence is not contiguous")
            durable_event = json.loads(serialized)
            if durable_event != snapshot_events[expected_sequence]:
                raise ReplayDivergenceError(
                    f"durable event diverged at sequence {expected_sequence}"
                )
        return engine

    async def load_commands(self, game_id: GameId) -> tuple[CommandEnvelope, ...]:
        """Load the immutable accepted-command transcript in deterministic order."""
        rows = await asyncio.to_thread(self._load_commands_sync, str(game_id))
        commands: list[CommandEnvelope] = []
        for expected_sequence, (sequence, serialized) in enumerate(rows):
            if sequence != expected_sequence:
                raise ReplayDivergenceError("durable command sequence is not contiguous")
            data = json.loads(serialized)
            if not isinstance(data, dict):
                raise ReplayDivergenceError("durable command payload is not an object")
            commands.append(command_from_data(data))
        return tuple(commands)

    async def event_count(self, game_id: GameId) -> int:
        """Return the number of durable events for one game."""
        return await asyncio.to_thread(self._event_count_sync, str(game_id))

    async def list_games(self) -> tuple[GameId, ...]:
        """Return durable game ids in stable order."""
        values = await asyncio.to_thread(self._list_games_sync)
        return tuple(GameId(value) for value in values)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=10.0)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize_sync(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS game_saves (
                    game_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    state_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS game_events (
                    game_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY (game_id, sequence),
                    FOREIGN KEY (game_id) REFERENCES game_saves(game_id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS game_commands (
                    game_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    command_id TEXT NOT NULL,
                    command_json TEXT NOT NULL,
                    PRIMARY KEY (game_id, sequence),
                    UNIQUE (game_id, command_id),
                    FOREIGN KEY (game_id) REFERENCES game_saves(game_id)
                        ON DELETE RESTRICT
                );
                """
            )

    def _save_sync(
        self,
        game_id: str,
        payload: str,
        state_hash: str,
        event_hash: str,
        event_rows: list[tuple[int, str]],
        command_rows: list[tuple[int, str, str]] | None,
    ) -> None:
        self._initialize_sync()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO game_saves(game_id, payload, state_hash, event_hash)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(game_id) DO UPDATE SET
                    payload=excluded.payload,
                    state_hash=excluded.state_hash,
                    event_hash=excluded.event_hash
                """,
                (game_id, payload, state_hash, event_hash),
            )
            for sequence, event_json in event_rows:
                existing = connection.execute(
                    "SELECT event_json FROM game_events WHERE game_id=? AND sequence=?",
                    (game_id, sequence),
                ).fetchone()
                if existing is None:
                    connection.execute(
                        "INSERT INTO game_events(game_id, sequence, event_json) VALUES (?, ?, ?)",
                        (game_id, sequence, event_json),
                    )
                elif existing[0] != event_json:
                    raise ReplayDivergenceError(
                        f"attempted to rewrite immutable event {game_id}:{sequence}"
                    )

            if command_rows is not None:
                durable_count_row = connection.execute(
                    "SELECT COUNT(*) FROM game_commands WHERE game_id=?",
                    (game_id,),
                ).fetchone()
                durable_count = int(durable_count_row[0]) if durable_count_row is not None else 0
                if durable_count > len(command_rows):
                    raise ReplayDivergenceError("accepted command transcript moved backwards")
                for sequence, command_id, command_json in command_rows:
                    existing = connection.execute(
                        """
                        SELECT command_id, command_json
                        FROM game_commands
                        WHERE game_id=? AND sequence=?
                        """,
                        (game_id, sequence),
                    ).fetchone()
                    if existing is None:
                        connection.execute(
                            """
                            INSERT INTO game_commands(game_id, sequence, command_id, command_json)
                            VALUES (?, ?, ?, ?)
                            """,
                            (game_id, sequence, command_id, command_json),
                        )
                    elif existing[0] != command_id or existing[1] != command_json:
                        raise ReplayDivergenceError(
                            f"attempted to rewrite immutable command {game_id}:{sequence}"
                        )

    def _load_sync(
        self,
        game_id: str,
    ) -> tuple[tuple[str, str, str] | None, list[tuple[int, str]]]:
        self._initialize_sync()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload, state_hash, event_hash FROM game_saves WHERE game_id=?",
                (game_id,),
            ).fetchone()
            events = connection.execute(
                """
                SELECT sequence, event_json
                FROM game_events
                WHERE game_id=?
                ORDER BY sequence ASC
                """,
                (game_id,),
            ).fetchall()
        typed_row = None if row is None else (str(row[0]), str(row[1]), str(row[2]))
        typed_events = [(int(sequence), str(event_json)) for sequence, event_json in events]
        return typed_row, typed_events

    def _load_commands_sync(self, game_id: str) -> list[tuple[int, str]]:
        self._initialize_sync()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sequence, command_json
                FROM game_commands
                WHERE game_id=?
                ORDER BY sequence ASC
                """,
                (game_id,),
            ).fetchall()
        return [(int(sequence), str(command_json)) for sequence, command_json in rows]

    def _event_count_sync(self, game_id: str) -> int:
        self._initialize_sync()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM game_events WHERE game_id=?",
                (game_id,),
            ).fetchone()
        return int(row[0]) if row is not None else 0

    def _list_games_sync(self) -> list[str]:
        self._initialize_sync()
        with self._connect() as connection:
            rows: list[tuple[Any, ...]] = connection.execute(
                "SELECT game_id FROM game_saves ORDER BY game_id ASC"
            ).fetchall()
        return [str(row[0]) for row in rows]
