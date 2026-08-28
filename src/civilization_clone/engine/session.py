"""Authoritative v0.3 game session and command processor."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.feedback import FeedbackSeverity, UserFeedback
from civilization_clone.domain.gameplay import (
    ControllerType,
    GameSession,
    PlayerState,
    UnitDefinition,
    UnitState,
)
from civilization_clone.domain.ids import CommandId, EventId, GameId, PlayerId, UnitId
from civilization_clone.domain.map import HexCoord
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.types import JsonValue
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.event_log import EventLog
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
        return CommandResult(
            True,
            self.session.state_version,
            (event,),
            (UserFeedback("PLAYER_JOINED", f"{player.name} joined the game."),),
        )

    def _start_game(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.SETUP:
            return self._rejected("GAME_ALREADY_STARTED", "The game is already active.")
        if len(self.session.player_order) < 2:
            return self._rejected("NOT_ENOUGH_PLAYERS", "At least two players are required.")

        scout = UnitDefinition("scout", movement=2, vision_radius=1)
        for index, player_id in enumerate(self.session.player_order):
            spawn = self.session.world.spawns[index]
            unit_id = UnitId(f"unit-{index}")
            self.session.units[unit_id] = UnitState.spawn(
                unit_id=unit_id,
                owner_id=player_id,
                definition=scout,
                position=spawn,
            )
            self._update_player_visibility(player_id)

        self.session.status = GameStatus.ACTIVE
        self.session.phase = GamePhase.PLAYER_TURN
        self.session.turn = 1
        self.session.active_player_index = 0
        self.session.state_version += 1

        events = [
            self._emit(
                "GameStarted",
                {"player_count": len(self.session.player_order)},
                command.command_id,
            )
        ]
        for unit_id in sorted(self.session.units):
            unit = self.session.units[unit_id]
            events.append(
                self._emit(
                    "UnitSpawned",
                    {
                        "unit_id": unit.unit_id,
                        "owner_id": unit.owner_id,
                        "q": unit.position.q,
                        "r": unit.position.r,
                    },
                    command.command_id,
                )
            )
        events.append(
            self._emit(
                "TurnStarted",
                {"turn": self.session.turn, "player_id": self.session.current_player_id},
                command.command_id,
            )
        )
        self._log(command, "game started", events[-1].event_id)
        return CommandResult(True, self.session.state_version, tuple(events))

    def _move_unit(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.ACTIVE:
            return self._rejected("GAME_NOT_ACTIVE", "The game has not started.")
        if command.player_id is None:
            return self._rejected("PLAYER_REQUIRED", "A player identity is required.")

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
            self._log(command, "move rejected", error_code=reason)
            return self._rejected(
                "MOVE_REJECTED",
                "That unit cannot move to the requested tile.",
                {"reason": reason},
            )

        origin, cost = apply_move(self.session, unit_id, destination)
        self._update_player_visibility(command.player_id)
        self.session.state_version += 1
        event = self._emit(
            "UnitMoved",
            {
                "unit_id": unit_id,
                "from_q": origin.q,
                "from_r": origin.r,
                "to_q": destination.q,
                "to_r": destination.r,
                "movement_cost": cost,
            },
            command.command_id,
        )
        self._log(command, "unit moved", event.event_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _end_turn(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.ACTIVE:
            return self._rejected("GAME_NOT_ACTIVE", "The game has not started.")
        if command.player_id is None or command.player_id != self.session.current_player_id:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may end the turn.")

        ended_turn = self.session.turn
        ended_player = command.player_id
        self.session.state_version += 1
        events = [
            self._emit(
                "PlayerEndedTurn",
                {"turn": ended_turn, "player_id": ended_player},
                command.command_id,
            )
        ]
        wrapped, next_player = advance_turn(self.session)
        if wrapped:
            events.append(self._emit("TurnEnded", {"turn": ended_turn}, command.command_id))
        events.append(
            self._emit(
                "TurnStarted",
                {"turn": self.session.turn, "player_id": next_player},
                command.command_id,
            )
        )
        self._log(command, "turn advanced", events[-1].event_id)
        return CommandResult(True, self.session.state_version, tuple(events))

    def _update_player_visibility(self, player_id: PlayerId) -> None:
        player = self.session.players[player_id]
        units = [unit for unit in self.session.units.values() if unit.owner_id == player_id]
        current = set()
        for unit in units:
            current.update(
                visible_coords(
                    self.session.world,
                    [unit.position],
                    unit.definition.vision_radius,
                )
            )
        player.visibility = dict(update_visibility(self.session.world, player.visibility, current))

    def _rejected(
        self,
        code: str,
        message: str,
        context: dict[str, str] | None = None,
    ) -> CommandResult:
        return CommandResult(
            False,
            self.session.state_version,
            feedback=(UserFeedback(code, message, FeedbackSeverity.WARNING, context or {}),),
        )

    def _log(
        self,
        command: CommandEnvelope,
        message: str,
        event_id: EventId | None = None,
        error_code: str | None = None,
    ) -> None:
        if self.logger is None:
            return
        context: dict[str, object] = {
            "game_id": self.session.game_id,
            "command_id": command.command_id,
            "operation": command.command_type,
            "state_version": self.session.state_version,
            "turn": self.session.turn,
        }
        if event_id is not None:
            context["event_id"] = event_id
        if error_code is not None:
            context["error_code"] = error_code
        self.logger.info(message, extra=context)
