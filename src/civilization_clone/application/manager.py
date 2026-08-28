"""Async application service that serializes authoritative mutations per game."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import GameId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import CommandResult, GameEngine
from civilization_clone.persistence.replay import ReplayReport, verify_replay
from civilization_clone.persistence.sqlite_store import SqliteGameStore


@dataclass(slots=True)
class GameManager:
    """Own running engines, mutation locks, persistence, replay, and event subscribers."""

    store: SqliteGameStore | None = None
    _games: dict[GameId, GameEngine] = field(default_factory=dict)
    _locks: dict[GameId, asyncio.Lock] = field(default_factory=dict)
    _subscribers: dict[GameId, set[asyncio.Queue[EventEnvelope]]] = field(
        default_factory=dict
    )
    _accepted_commands: dict[GameId, list[CommandEnvelope]] = field(default_factory=dict)
    _registry_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def create_game(
        self,
        *,
        game_id: GameId,
        seed: int,
        ruleset: RulesetRef | None = None,
        map_config: MapGenerationConfig | None = None,
    ) -> GameEngine:
        """Create one game exactly once and optionally persist its initial state."""
        async with self._registry_lock:
            if game_id in self._games:
                raise ValueError(f"game already exists: {game_id}")
            if self.store is not None and game_id in await self.store.list_games():
                raise ValueError(f"game already exists: {game_id}")
            resolved_ruleset = ruleset or RulesetRef(RulesetId("poc-core"), "1.0.0")
            engine = GameEngine.create(
                game_id=game_id,
                seed=seed,
                ruleset=resolved_ruleset,
                map_config=map_config,
            )
            self._games[game_id] = engine
            self._locks[game_id] = asyncio.Lock()
            self._subscribers.setdefault(game_id, set())
            self._accepted_commands[game_id] = []
            if self.store is not None:
                await self.store.save(engine, accepted_commands=())
            return engine

    async def get_engine(self, game_id: GameId) -> GameEngine:
        """Return a running game, lazily restoring it from durable storage when configured."""
        engine = self._games.get(game_id)
        if engine is not None:
            return engine
        async with self._registry_lock:
            engine = self._games.get(game_id)
            if engine is not None:
                return engine
            if self.store is None:
                raise KeyError(f"game not found: {game_id}")
            engine = await self.store.load(game_id)
            commands = list(await self.store.load_commands(game_id))
            self._games[game_id] = engine
            self._accepted_commands[game_id] = commands
            self._locks.setdefault(game_id, asyncio.Lock())
            self._subscribers.setdefault(game_id, set())
            return engine

    async def process(self, command: CommandEnvelope) -> CommandResult:
        """Serialize one state-changing command for its game and publish only new events."""
        engine = await self.get_engine(command.game_id)
        lock = self._locks.setdefault(command.game_id, asyncio.Lock())
        async with lock:
            before_sequence = engine.event_log.next_sequence
            result = engine.process(command)
            new_events = engine.event_log.snapshot()[before_sequence:]
            transcript = self._accepted_commands.setdefault(command.game_id, [])
            if result.accepted and new_events:
                transcript.append(command)
            if new_events and self.store is not None:
                await self.store.save(engine, accepted_commands=tuple(transcript))
            if new_events:
                self._publish(command.game_id, new_events)
            return result

    async def save(self, game_id: GameId) -> None:
        """Persist one running game using the same mutation lock as commands."""
        if self.store is None:
            raise RuntimeError("no durable game store is configured")
        engine = await self.get_engine(game_id)
        lock = self._locks.setdefault(game_id, asyncio.Lock())
        async with lock:
            transcript = tuple(self._accepted_commands.get(game_id, ()))
            await self.store.save(engine, accepted_commands=transcript)

    async def accepted_commands(self, game_id: GameId) -> tuple[CommandEnvelope, ...]:
        """Return an immutable accepted-command transcript for replay/debug tooling."""
        await self.get_engine(game_id)
        return tuple(self._accepted_commands.get(game_id, ()))

    async def verify_replay(self, game_id: GameId) -> ReplayReport:
        """Independently rebuild one running game from its accepted command transcript."""
        engine = await self.get_engine(game_id)
        lock = self._locks.setdefault(game_id, asyncio.Lock())
        async with lock:
            return verify_replay(engine, self._accepted_commands.get(game_id, ()))

    async def snapshot_events(self, game_id: GameId) -> tuple[EventEnvelope, ...]:
        """Return an immutable event snapshot for queries without mutating the engine."""
        engine = await self.get_engine(game_id)
        return engine.event_log.snapshot()

    async def subscribe(self, game_id: GameId) -> asyncio.Queue[EventEnvelope]:
        """Register an in-process event queue for a WebSocket/client subscriber."""
        await self.get_engine(game_id)
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue()
        self._subscribers.setdefault(game_id, set()).add(queue)
        return queue

    def unsubscribe(self, game_id: GameId, queue: asyncio.Queue[EventEnvelope]) -> None:
        """Remove a previously registered subscriber queue."""
        subscribers = self._subscribers.get(game_id)
        if subscribers is not None:
            subscribers.discard(queue)

    def _publish(self, game_id: GameId, events: tuple[EventEnvelope, ...]) -> None:
        for queue in tuple(self._subscribers.get(game_id, ())):
            for event in events:
                queue.put_nowait(event)
