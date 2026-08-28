"""Authoritative game session and serialized command processor."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from civilization_clone.domain.economy import SettlementState
from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.feedback import FeedbackSeverity, UserFeedback
from civilization_clone.domain.gameplay import (
    ControllerType,
    GameSession,
    PlayerState,
    UnitDefinition,
    UnitState,
)
from civilization_clone.domain.ids import (
    CommandId,
    EventId,
    GameId,
    PlayerId,
    SettlementId,
    UnitId,
)
from civilization_clone.domain.map import HexCoord
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.types import JsonValue
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.economy import production_order, resolve_player_economy
from civilization_clone.engine.event_log import EventLog
from civilization_clone.engine.hexgrid import distance, neighbors
from civilization_clone.engine.mapgen import MapGenerationConfig, generate_world
from civilization_clone.engine.movement import apply_move, validate_move
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.engine.turns import advance_turn
from civilization_clone.engine.visibility import update_visibility, visible_coords


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Stable result returned for an engine command, including retries."""

    accepted: bool
    state_version: int
    events: tuple[EventEnvelope, ...] = ()
    feedback: tuple[UserFeedback, ...] = ()


@dataclass(slots=True)
class GameEngine:
    """Single-game serialized command processor for deterministic local execution."""

    session: GameSession
    event_log: EventLog
    logger: logging.Logger | None = None
    _processed: dict[CommandId, CommandResult] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        game_id: GameId,
        seed: int,
        ruleset: RulesetRef,
        map_config: MapGenerationConfig | None = None,
        logger: logging.Logger | None = None,
    ) -> "GameEngine":
        journal = EventLog(game_id)
        created = EventEnvelope.create(
            event_id=EventId(f"{game_id}-event-0"),
            game_id=game_id,
            sequence=0,
            event_type="GameCreated",
            state_version=0,
            payload={
                "seed": seed,
                "ruleset_id": ruleset.ruleset_id,
                "ruleset_version": ruleset.version,
            },
        )
        journal.append(created)
        generated = generate_world(
            game_id=game_id,
            seed=seed,
            config=map_config,
            start_sequence=journal.next_sequence,
            state_version=0,
            logger=logger,
        )
        journal.extend(generated.events)
        session = GameSession(game_id=game_id, ruleset=ruleset, seed=seed, world=generated.world)
        return cls(session=session, event_log=journal, logger=logger)

    def process(self, command: CommandEnvelope) -> CommandResult:
        """Validate, apply, journal, and return one state-changing command."""
        if command.game_id != self.session.game_id:
            return self._rejected("WRONG_GAME", "Command targets a different game.")
        cached = self._processed.get(command.command_id)
        if cached is not None:
            return cached
        if (
            command.expected_state_version is not None
            and command.expected_state_version != self.session.state_version
        ):
            result = self._rejected(
                "STALE_STATE_VERSION",
                "The game changed before this command could be applied.",
                {"current_state_version": str(self.session.state_version)},
            )
            self._processed[command.command_id] = result
            return result

        handlers = {
            "JoinGame": self._join_game,
            "StartGame": self._start_game,
            "MoveUnit": self._move_unit,
            "FoundSettlement": self._found_settlement,
            "SetWorkedTile": self._set_worked_tile,
            "QueueProduction": self._queue_production,
            "CancelProduction": self._cancel_production,
            "EndTurn": self._end_turn,
        }
        handler = handlers.get(command.command_type)
        if handler is None:
            result = self._rejected("UNKNOWN_COMMAND", "That command type is not supported.")
        else:
            result = handler(command)
        if not result.accepted:
            error_code = result.feedback[0].code if result.feedback else "COMMAND_REJECTED"
            self._log(command, "command rejected", error_code=error_code)
        self._processed[command.command_id] = result
        return result

    def state_hash(self) -> str:
        return state_hash(self.session.canonical_state())

    def event_hash(self) -> str:
        return state_hash(self.event_log.snapshot())

    def _emit(
        self,
        event_type: str,
        payload: dict[str, JsonValue],
        command_id: CommandId,
    ) -> EventEnvelope:
        sequence = self.event_log.next_sequence
        event = EventEnvelope.create(
            event_id=EventId(f"{self.session.game_id}-event-{sequence}"),
            game_id=self.session.game_id,
            sequence=sequence,
            event_type=event_type,
            state_version=self.session.state_version,
            payload=payload,
            causation_command_id=command_id,
        )
        self.event_log.append(event)
        return event

    def _join_game(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.SETUP:
            return self._rejected("GAME_ALREADY_STARTED", "Players cannot join after start.")
        if command.player_id is None:
            return self._rejected("PLAYER_REQUIRED", "A player identity is required.")
        if command.player_id in self.session.players:
            return self._rejected("PLAYER_EXISTS", "That player has already joined.")
        if len(self.session.player_order) >= self.session.max_players:
            return self._rejected("GAME_FULL", "The game has no open player slots.")
        raw_name = command.payload.get("name", command.player_id)
        if not isinstance(raw_name, str) or not raw_name.strip():
            return self._rejected("INVALID_PLAYER_NAME", "Player name must be non-empty text.")
        raw_controller = command.payload.get("controller", ControllerType.HUMAN.value)
        try:
            controller = ControllerType(str(raw_controller))
        except ValueError:
            return self._rejected("INVALID_CONTROLLER", "Unsupported player controller type.")
        player = PlayerState(command.player_id, raw_name.strip(), controller)
        self.session.players[command.player_id] = player
        self.session.player_order.append(command.player_id)
        self.session.state_version += 1
        event = self._emit("PlayerJoined", {"player_id": command.player_id}, command.command_id)
        self._log(command, "command accepted", event.event_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _start_game(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.SETUP:
            return self._rejected("GAME_ALREADY_STARTED", "The game is already active.")
        if len(self.session.player_order) < 2:
            return self._rejected("NOT_ENOUGH_PLAYERS", "At least two players are required.")
        founder = UnitDefinition("founder", movement=2, vision_radius=1, can_found=True)
        for index, player_id in enumerate(self.session.player_order):
            spawn = self.session.world.spawns[index]
            unit_id = UnitId(f"unit-{self.session.next_unit_index}")
            self.session.next_unit_index += 1
            self.session.units[unit_id] = UnitState.spawn(
                unit_id=unit_id,
                owner_id=player_id,
                definition=founder,
                position=spawn,
            )
            self._update_player_visibility(player_id)
        self.session.status = GameStatus.ACTIVE
        self.session.phase = GamePhase.PLAYER_TURN
        self.session.turn = 1
        self.session.active_player_index = 0
        self.session.state_version += 1
        events = [self._emit("GameStarted", {"player_count": len(self.session.player_order)}, command.command_id)]
        for unit_id in sorted(self.session.units):
            unit = self.session.units[unit_id]
            events.append(
                self._emit(
                    "UnitSpawned",
                    {
                        "unit_id": unit.unit_id,
                        "owner_id": unit.owner_id,
                        "definition_id": unit.definition.definition_id,
                        "q": unit.position.q,
                        "r": unit.position.r,
                    },
                    command.command_id,
                )
            )
        events.append(self._emit("TurnStarted", {"turn": 1, "player_id": self.session.current_player_id}, command.command_id))
        self._log(command, "game started", events[-1].event_id)
        return CommandResult(True, self.session.state_version, tuple(events))

    def _move_unit(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.ACTIVE or command.player_id is None:
            return self._rejected("GAME_NOT_ACTIVE", "The game has not started.")
        raw_unit_id = command.payload.get("unit_id")
        q = command.payload.get("q")
        r = command.payload.get("r")
        if not isinstance(raw_unit_id, str) or not isinstance(q, int) or not isinstance(r, int):
            return self._rejected("INVALID_MOVE", "MoveUnit requires unit_id, q, and r.")
        if isinstance(q, bool) or isinstance(r, bool):
            return self._rejected("INVALID_MOVE", "Move coordinates must be integers.")
        unit_id = UnitId(raw_unit_id)
        destination = HexCoord(q, r)
        reason = validate_move(self.session, command.player_id, unit_id, destination)
        if reason is not None:
            return self._rejected("MOVE_REJECTED", "That unit cannot move there.", {"reason": reason})
        origin, cost = apply_move(self.session, unit_id, destination)
        self._update_player_visibility(command.player_id)
        self.session.state_version += 1
        event = self._emit(
            "UnitMoved",
            {"unit_id": unit_id, "from_q": origin.q, "from_r": origin.r, "to_q": destination.q, "to_r": destination.r, "movement_cost": cost},
            command.command_id,
        )
        return CommandResult(True, self.session.state_version, (event,))

    def _found_settlement(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may found a settlement.")
        raw_unit_id = command.payload.get("unit_id")
        if not isinstance(raw_unit_id, str):
            return self._rejected("INVALID_FOUNDING", "FoundSettlement requires unit_id.")
        unit_id = UnitId(raw_unit_id)
        unit = self.session.units.get(unit_id)
        if unit is None or unit.owner_id != player_id or not unit.definition.can_found:
            return self._rejected("INVALID_FOUNDING", "That unit cannot found this settlement.")
        if any(distance(unit.position, settlement.center) < 3 for settlement in self.session.settlements.values()):
            return self._rejected("SETTLEMENT_TOO_CLOSE", "Another settlement is too close.")
        settlement_id = SettlementId(f"settlement-{self.session.next_settlement_index}")
        self.session.next_settlement_index += 1
        territory = {coord for coord in (unit.position, *neighbors(unit.position)) if coord in self.session.world.tiles}
        settlement = SettlementState(settlement_id=settlement_id, owner_id=player_id, center=unit.position, territory=territory)
        self.session.settlements[settlement_id] = settlement
        del self.session.units[unit_id]
        self._update_player_visibility(player_id)
        self.session.state_version += 1
        event = self._emit("SettlementFounded", {"settlement_id": settlement_id, "player_id": player_id, "q": settlement.center.q, "r": settlement.center.r}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _set_worked_tile(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may manage tiles.")
        settlement = self._owned_settlement(command, player_id)
        if settlement is None:
            return self._rejected("SETTLEMENT_NOT_FOUND", "Settlement is not owned by this player.")
        q = command.payload.get("q")
        r = command.payload.get("r")
        worked = command.payload.get("worked", True)
        if not isinstance(q, int) or isinstance(q, bool) or not isinstance(r, int) or isinstance(r, bool) or not isinstance(worked, bool):
            return self._rejected("INVALID_WORKED_TILE", "q, r, and worked are required.")
        coord = HexCoord(q, r)
        tile = self.session.world.tiles.get(coord)
        if coord not in settlement.territory or coord == settlement.center or tile is None or not tile.passable:
            return self._rejected("INVALID_WORKED_TILE", "Tile is not a workable controlled tile.")
        if worked and coord not in settlement.worked_tiles:
            if len(settlement.worked_tiles) >= settlement.population:
                return self._rejected("WORKED_TILE_LIMIT", "Population limits worked tiles.")
            settlement.worked_tiles.add(coord)
        elif not worked:
            settlement.worked_tiles.discard(coord)
        self.session.state_version += 1
        event = self._emit("WorkedTileChanged", {"settlement_id": settlement.settlement_id, "q": coord.q, "r": coord.r, "worked": worked}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _queue_production(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may queue production.")
        settlement = self._owned_settlement(command, player_id)
        if settlement is None:
            return self._rejected("SETTLEMENT_NOT_FOUND", "Settlement is not owned by this player.")
        raw_kind = command.payload.get("kind")
        definition_id = command.payload.get("definition_id")
        if not isinstance(raw_kind, str) or not isinstance(definition_id, str):
            return self._rejected("INVALID_PRODUCTION", "kind and definition_id are required.")
        order = production_order(raw_kind, definition_id)
        if order is None:
            return self._rejected("INVALID_PRODUCTION", "Unknown production item.")
        if order.kind.value == "building" and definition_id in settlement.buildings:
            return self._rejected("ALREADY_BUILT", "That building is already complete.")
        settlement.production_queue.append(order)
        self.session.state_version += 1
        event = self._emit("ProductionQueued", {"settlement_id": settlement.settlement_id, "kind": order.kind.value, "definition_id": order.definition_id, "cost": order.cost}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _cancel_production(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may cancel production.")
        settlement = self._owned_settlement(command, player_id)
        if settlement is None:
            return self._rejected("SETTLEMENT_NOT_FOUND", "Settlement is not owned by this player.")
        index = command.payload.get("index", 0)
        if not isinstance(index, int) or isinstance(index, bool) or index < 0 or index >= len(settlement.production_queue):
            return self._rejected("INVALID_PRODUCTION", "Production queue index is out of range.")
        removed = settlement.production_queue.pop(index)
        if index == 0:
            settlement.production_storage = 0
        self.session.state_version += 1
        event = self._emit("ProductionCancelled", {"settlement_id": settlement.settlement_id, "kind": removed.kind.value, "definition_id": removed.definition_id}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _end_turn(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.ACTIVE or command.player_id != self.session.current_player_id:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may end the turn.")
        ended_turn = self.session.turn
        ended_player = command.player_id
        assert ended_player is not None
        self.session.state_version += 1
        events = [self._emit("PlayerEndedTurn", {"turn": ended_turn, "player_id": ended_player}, command.command_id)]
        for outcome in resolve_player_economy(self.session, ended_player):
            events.append(self._emit(outcome.event_type, outcome.payload, command.command_id))
        self._update_player_visibility(ended_player)
        wrapped, next_player = advance_turn(self.session)
        if wrapped:
            events.append(self._emit("TurnEnded", {"turn": ended_turn}, command.command_id))
        events.append(self._emit("TurnStarted", {"turn": self.session.turn, "player_id": next_player}, command.command_id))
        self._log(command, "turn and economy advanced", events[-1].event_id)
        return CommandResult(True, self.session.state_version, tuple(events))

    def _active_player(self, command: CommandEnvelope) -> PlayerId | None:
        if self.session.status is not GameStatus.ACTIVE or command.player_id != self.session.current_player_id:
            return None
        return command.player_id

    def _owned_settlement(self, command: CommandEnvelope, player_id: PlayerId) -> SettlementState | None:
        raw_id = command.payload.get("settlement_id")
        if not isinstance(raw_id, str):
            return None
        settlement = self.session.settlements.get(SettlementId(raw_id))
        return settlement if settlement is not None and settlement.owner_id == player_id else None

    def _update_player_visibility(self, player_id: PlayerId) -> None:
        player = self.session.players[player_id]
        origins = [(unit.position, unit.definition.vision_radius) for unit in self.session.units.values() if unit.owner_id == player_id]
        origins.extend((settlement.center, 1) for settlement in self.session.settlements.values() if settlement.owner_id == player_id)
        current: set[HexCoord] = set()
        for position, radius in origins:
            current.update(visible_coords(self.session.world, [position], radius))
        player.visibility = dict(update_visibility(self.session.world, player.visibility, current))

    def _rejected(self, code: str, message: str, context: dict[str, str] | None = None) -> CommandResult:
        return CommandResult(False, self.session.state_version, feedback=(UserFeedback(code, message, FeedbackSeverity.WARNING, context or {}),))

    def _log(self, command: CommandEnvelope, message: str, event_id: EventId | None = None, error_code: str | None = None) -> None:
        if self.logger is None:
            return
        context: dict[str, object] = {"game_id": self.session.game_id, "command_id": command.command_id, "operation": command.command_type, "state_version": self.session.state_version, "turn": self.session.turn}
        if event_id is not None:
            context["event_id"] = event_id
        if error_code is not None:
            context["error_code"] = error_code
        self.logger.info(message, extra=context)
