"""Authoritative game session and serialized command processor."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from civilization_clone.domain.diplomacy import DiplomacyStatus, relationship_key
from civilization_clone.domain.economy import SettlementState
from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.feedback import FeedbackSeverity, UserFeedback
from civilization_clone.domain.gameplay import ControllerType, GameSession, PlayerState, UnitDefinition, UnitState
from civilization_clone.domain.ids import CommandId, EventId, GameId, PlayerId, SettlementId, UnitId
from civilization_clone.domain.map import HexCoord
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.types import JsonValue
from civilization_clone.engine.combat import resolve_attack
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.economy import production_order, resolve_player_economy
from civilization_clone.engine.event_log import EventLog
from civilization_clone.engine.hexgrid import distance, neighbors
from civilization_clone.engine.mapgen import MapGenerationConfig, generate_world
from civilization_clone.engine.movement import apply_move, validate_move
from civilization_clone.engine.research import choose_research, resolve_research
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.engine.turns import advance_turn
from civilization_clone.engine.victory import evaluate_victory
from civilization_clone.engine.visibility import update_visibility, visible_coords


@dataclass(frozen=True, slots=True)
class CommandResult:
    accepted: bool
    state_version: int
    events: tuple[EventEnvelope, ...] = ()
    feedback: tuple[UserFeedback, ...] = ()


@dataclass(slots=True)
class GameEngine:
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
        max_turns: int = 50,
    ) -> "GameEngine":
        if max_turns <= 0:
            raise ValueError("max_turns must be positive")
        journal = EventLog(game_id)
        journal.append(EventEnvelope.create(
            event_id=EventId(f"{game_id}-event-0"), game_id=game_id, sequence=0,
            event_type="GameCreated", state_version=0,
            payload={"seed": seed, "ruleset_id": ruleset.ruleset_id, "ruleset_version": ruleset.version},
        ))
        generated = generate_world(
            game_id=game_id, seed=seed, config=map_config,
            start_sequence=journal.next_sequence, state_version=0, logger=logger,
        )
        journal.extend(generated.events)
        session = GameSession(
            game_id=game_id, ruleset=ruleset, seed=seed, world=generated.world, max_turns=max_turns
        )
        return cls(session=session, event_log=journal, logger=logger)

    def process(self, command: CommandEnvelope) -> CommandResult:
        if command.game_id != self.session.game_id:
            return self._rejected("WRONG_GAME", "Command targets a different game.")
        cached = self._processed.get(command.command_id)
        if cached is not None:
            return cached
        if self.session.status is GameStatus.FINISHED:
            result = self._rejected("GAME_FINISHED", "The game has already finished.")
            self._processed[command.command_id] = result
            return result
        if command.expected_state_version is not None and command.expected_state_version != self.session.state_version:
            result = self._rejected(
                "STALE_STATE_VERSION", "The game changed before this command could be applied.",
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
            "ChooseResearch": self._choose_research,
            "DeclareWar": self._declare_war,
            "OfferPeace": self._offer_peace,
            "AcceptPeace": self._accept_peace,
            "AttackUnit": self._attack_unit,
            "Concede": self._concede,
            "EndTurn": self._end_turn,
        }
        handler = handlers.get(command.command_type)
        result = self._rejected("UNKNOWN_COMMAND", "That command type is not supported.") if handler is None else handler(command)
        if not result.accepted:
            self._log(command, "command rejected", error_code=result.feedback[0].code if result.feedback else "COMMAND_REJECTED")
        self._processed[command.command_id] = result
        return result

    def state_hash(self) -> str:
        return state_hash(self.session.canonical_state())

    def event_hash(self) -> str:
        return state_hash(self.event_log.snapshot())

    def _emit(self, event_type: str, payload: dict[str, JsonValue], command_id: CommandId) -> EventEnvelope:
        sequence = self.event_log.next_sequence
        event = EventEnvelope.create(
            event_id=EventId(f"{self.session.game_id}-event-{sequence}"), game_id=self.session.game_id,
            sequence=sequence, event_type=event_type, state_version=self.session.state_version,
            payload=payload, causation_command_id=command_id,
        )
        self.event_log.append(event)
        return event

    def _join_game(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.SETUP or command.player_id is None:
            return self._rejected("JOIN_REJECTED", "The player cannot join this game.")
        if command.player_id in self.session.players:
            return self._rejected("PLAYER_EXISTS", "That player has already joined.")
        if len(self.session.player_order) >= self.session.max_players:
            return self._rejected("GAME_FULL", "The game has no open player slots.")
        raw_name = command.payload.get("name", command.player_id)
        if not isinstance(raw_name, str) or not raw_name.strip():
            return self._rejected("INVALID_PLAYER_NAME", "Player name must be non-empty text.")
        try:
            controller = ControllerType(str(command.payload.get("controller", ControllerType.HUMAN.value)))
        except ValueError:
            return self._rejected("INVALID_CONTROLLER", "Unsupported player controller type.")
        self.session.players[command.player_id] = PlayerState(command.player_id, raw_name.strip(), controller)
        self.session.player_order.append(command.player_id)
        self.session.state_version += 1
        event = self._emit("PlayerJoined", {"player_id": command.player_id}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _start_game(self, command: CommandEnvelope) -> CommandResult:
        if self.session.status is not GameStatus.SETUP or len(self.session.player_order) < 2:
            return self._rejected("START_REJECTED", "The game cannot start yet.")
        founder = UnitDefinition("founder", movement=2, vision_radius=1, can_found=True, combat_strength=5)
        for index, player_id in enumerate(self.session.player_order):
            unit_id = UnitId(f"unit-{self.session.next_unit_index}")
            self.session.next_unit_index += 1
            self.session.units[unit_id] = UnitState.spawn(
                unit_id=unit_id, owner_id=player_id, definition=founder,
                position=self.session.world.spawns[index],
            )
            self._update_player_visibility(player_id)
        for left_index, left in enumerate(self.session.player_order):
            for right in self.session.player_order[left_index + 1:]:
                self.session.diplomacy[relationship_key(left, right)] = DiplomacyStatus.PEACE
        self.session.status = GameStatus.ACTIVE
        self.session.phase = GamePhase.PLAYER_TURN
        self.session.turn = 1
        self.session.active_player_index = 0
        self.session.state_version += 1
        events = [self._emit("GameStarted", {"player_count": len(self.session.player_order)}, command.command_id)]
        for unit_id in sorted(self.session.units):
            unit = self.session.units[unit_id]
            events.append(self._emit("UnitSpawned", {
                "unit_id": unit.unit_id, "owner_id": unit.owner_id,
                "definition_id": unit.definition.definition_id,
                "q": unit.position.q, "r": unit.position.r,
            }, command.command_id))
        events.append(self._emit("TurnStarted", {"turn": 1, "player_id": self.session.current_player_id}, command.command_id))
        return CommandResult(True, self.session.state_version, tuple(events))

    def _move_unit(self, command: CommandEnvelope) -> CommandResult:
        player_id = command.player_id
        raw_unit_id, q, r = command.payload.get("unit_id"), command.payload.get("q"), command.payload.get("r")
        if player_id is None or not isinstance(raw_unit_id, str) or not isinstance(q, int) or isinstance(q, bool) or not isinstance(r, int) or isinstance(r, bool):
            return self._rejected("INVALID_MOVE", "MoveUnit requires player_id, unit_id, q, and r.")
        unit_id, destination = UnitId(raw_unit_id), HexCoord(q, r)
        reason = validate_move(self.session, player_id, unit_id, destination)
        if reason is not None:
            return self._rejected("MOVE_REJECTED", "That unit cannot move there.", {"reason": reason})
        origin, cost = apply_move(self.session, unit_id, destination)
        self._update_player_visibility(player_id)
        self.session.state_version += 1
        event = self._emit("UnitMoved", {
            "unit_id": unit_id, "from_q": origin.q, "from_r": origin.r,
            "to_q": destination.q, "to_r": destination.r, "movement_cost": cost,
        }, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _found_settlement(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        raw_unit_id = command.payload.get("unit_id")
        if player_id is None or not isinstance(raw_unit_id, str):
            return self._rejected("INVALID_FOUNDING", "FoundSettlement requires an active founding unit.")
        unit_id = UnitId(raw_unit_id)
        unit = self.session.units.get(unit_id)
        if unit is None or unit.owner_id != player_id or not unit.definition.can_found:
            return self._rejected("INVALID_FOUNDING", "That unit cannot found this settlement.")
        if any(distance(unit.position, item.center) < 3 for item in self.session.settlements.values()):
            return self._rejected("SETTLEMENT_TOO_CLOSE", "Another settlement is too close.")
        settlement_id = SettlementId(f"settlement-{self.session.next_settlement_index}")
        self.session.next_settlement_index += 1
        territory = {coord for coord in (unit.position, *neighbors(unit.position)) if coord in self.session.world.tiles}
        self.session.settlements[settlement_id] = SettlementState(settlement_id, player_id, unit.position, territory=territory)
        del self.session.units[unit_id]
        self._update_player_visibility(player_id)
        self.session.state_version += 1
        event = self._emit("SettlementFounded", {"settlement_id": settlement_id, "player_id": player_id, "q": unit.position.q, "r": unit.position.r}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _set_worked_tile(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        settlement = self._owned_settlement(command, player_id) if player_id is not None else None
        q, r, worked = command.payload.get("q"), command.payload.get("r"), command.payload.get("worked", True)
        if settlement is None or not isinstance(q, int) or isinstance(q, bool) or not isinstance(r, int) or isinstance(r, bool) or not isinstance(worked, bool):
            return self._rejected("INVALID_WORKED_TILE", "Invalid settlement tile request.")
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
        event = self._emit("WorkedTileChanged", {"settlement_id": settlement.settlement_id, "q": q, "r": r, "worked": worked}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _queue_production(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        settlement = self._owned_settlement(command, player_id) if player_id is not None else None
        raw_kind, definition_id = command.payload.get("kind"), command.payload.get("definition_id")
        if settlement is None or not isinstance(raw_kind, str) or not isinstance(definition_id, str):
            return self._rejected("INVALID_PRODUCTION", "Invalid production request.")
        order = production_order(raw_kind, definition_id)
        if order is None or (order.kind.value == "building" and definition_id in settlement.buildings):
            return self._rejected("INVALID_PRODUCTION", "Unknown or unavailable production item.")
        settlement.production_queue.append(order)
        self.session.state_version += 1
        event = self._emit("ProductionQueued", {"settlement_id": settlement.settlement_id, "kind": order.kind.value, "definition_id": order.definition_id, "cost": order.cost}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _cancel_production(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        settlement = self._owned_settlement(command, player_id) if player_id is not None else None
        index = command.payload.get("index", 0)
        if settlement is None or not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(settlement.production_queue):
            return self._rejected("INVALID_PRODUCTION", "Production queue index is out of range.")
        removed = settlement.production_queue.pop(index)
        if index == 0:
            settlement.production_storage = 0
        self.session.state_version += 1
        event = self._emit("ProductionCancelled", {"settlement_id": settlement.settlement_id, "kind": removed.kind.value, "definition_id": removed.definition_id}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _choose_research(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        technology_id = command.payload.get("technology_id")
        if player_id is None or not isinstance(technology_id, str):
            return self._rejected("INVALID_RESEARCH", "ChooseResearch requires a technology_id.")
        reason = choose_research(self.session, player_id, technology_id)
        if reason is not None:
            return self._rejected("RESEARCH_REJECTED", "That technology cannot be selected.", {"reason": reason})
        self.session.state_version += 1
        event = self._emit("TechnologySelected", {"player_id": player_id, "technology_id": technology_id}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _declare_war(self, command: CommandEnvelope) -> CommandResult:
        player_id, target = self._player_target(command)
        if player_id is None or target is None:
            return self._rejected("INVALID_DIPLOMACY", "DeclareWar requires another player.")
        key = relationship_key(player_id, target)
        if self.session.diplomacy.get(key) is DiplomacyStatus.WAR:
            return self._rejected("ALREADY_AT_WAR", "These players are already at war.")
        self.session.diplomacy[key] = DiplomacyStatus.WAR
        self.session.peace_offers.discard((player_id, target))
        self.session.peace_offers.discard((target, player_id))
        self.session.state_version += 1
        event = self._emit("WarDeclared", {"player_id": player_id, "target_player_id": target}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _offer_peace(self, command: CommandEnvelope) -> CommandResult:
        player_id, target = self._player_target(command)
        if player_id is None or target is None or self.session.diplomacy.get(relationship_key(player_id, target)) is not DiplomacyStatus.WAR:
            return self._rejected("INVALID_DIPLOMACY", "Peace can only be offered during war.")
        self.session.peace_offers.add((player_id, target))
        self.session.state_version += 1
        event = self._emit("PeaceOffered", {"player_id": player_id, "target_player_id": target}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _accept_peace(self, command: CommandEnvelope) -> CommandResult:
        player_id, target = self._player_target(command)
        if player_id is None or target is None or (target, player_id) not in self.session.peace_offers:
            return self._rejected("INVALID_DIPLOMACY", "No matching peace offer exists.")
        self.session.diplomacy[relationship_key(player_id, target)] = DiplomacyStatus.PEACE
        self.session.peace_offers.discard((target, player_id))
        self.session.peace_offers.discard((player_id, target))
        self.session.state_version += 1
        event = self._emit("PeaceEstablished", {"player_id": player_id, "target_player_id": target}, command.command_id)
        return CommandResult(True, self.session.state_version, (event,))

    def _attack_unit(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        attacker_raw, defender_raw = command.payload.get("attacker_id"), command.payload.get("defender_id")
        if player_id is None or not isinstance(attacker_raw, str) or not isinstance(defender_raw, str):
            return self._rejected("INVALID_ATTACK", "AttackUnit requires attacker_id and defender_id.")
        attacker_id, defender_id = UnitId(attacker_raw), UnitId(defender_raw)
        attacker, defender = self.session.units.get(attacker_id), self.session.units.get(defender_id)
        if attacker is None or defender is None or attacker.owner_id != player_id or attacker.owner_id == defender.owner_id:
            return self._rejected("INVALID_ATTACK", "Combatants are invalid for this player.")
        if self.session.diplomacy.get(relationship_key(attacker.owner_id, defender.owner_id)) is not DiplomacyStatus.WAR:
            return self._rejected("NOT_AT_WAR", "Combat requires a declared war.")
        if distance(attacker.position, defender.position) != 1 or attacker.movement_remaining <= 0:
            return self._rejected("INVALID_ATTACK", "Attacker must be adjacent and ready to act.")
        self.session.state_version += 1
        resolution = resolve_attack(self.session, attacker_id, defender_id, f"{self.event_log.next_sequence}:{attacker_id}:{defender_id}")
        events = [
            self._emit("UnitAttacked", {"attacker_id": attacker_id, "defender_id": defender_id}, command.command_id),
            self._emit("UnitDamaged", {"unit_id": defender_id, "damage": resolution.damage}, command.command_id),
        ]
        if resolution.defender_destroyed:
            events.append(self._emit("UnitDestroyed", {"unit_id": defender_id, "owner_id": defender.owner_id}, command.command_id))
            events.extend(self._eliminate_if_defeated(defender.owner_id, command.command_id))
        victory = evaluate_victory(self.session)
        if victory is not None:
            events.append(self._victory_event(victory[0], victory[1].value, command.command_id))
        self._update_player_visibility(player_id)
        return CommandResult(True, self.session.state_version, tuple(events))

    def _concede(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may concede.")
        self.session.players[player_id].eliminated = True
        self.session.state_version += 1
        events = [self._emit("PlayerEliminated", {"player_id": player_id, "reason": "conceded"}, command.command_id)]
        victory = evaluate_victory(self.session)
        if victory is not None:
            events.append(self._victory_event(victory[0], victory[1].value, command.command_id))
        else:
            _, next_player = advance_turn(self.session)
            events.append(self._emit("TurnStarted", {"turn": self.session.turn, "player_id": next_player}, command.command_id))
        return CommandResult(True, self.session.state_version, tuple(events))

    def _end_turn(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may end the turn.")
        ended_turn = self.session.turn
        self.session.state_version += 1
        events = [self._emit("PlayerEndedTurn", {"turn": ended_turn, "player_id": player_id}, command.command_id)]
        economy_outcomes = resolve_player_economy(self.session, player_id)
        science_generated = 0
        for outcome in economy_outcomes:
            events.append(self._emit(outcome.event_type, outcome.payload, command.command_id))
            if outcome.event_type == "SettlementYielded":
                science_generated += int(outcome.payload.get("science", 0))
        for outcome in resolve_research(self.session, player_id, science_generated):
            events.append(self._emit(outcome.event_type, outcome.payload, command.command_id))
        self._update_player_visibility(player_id)
        wrapped, next_player = advance_turn(self.session)
        if wrapped:
            events.append(self._emit("TurnEnded", {"turn": ended_turn}, command.command_id))
            victory = evaluate_victory(self.session)
            if victory is not None:
                events.append(self._victory_event(victory[0], victory[1].value, command.command_id))
                return CommandResult(True, self.session.state_version, tuple(events))
        events.append(self._emit("TurnStarted", {"turn": self.session.turn, "player_id": next_player}, command.command_id))
        return CommandResult(True, self.session.state_version, tuple(events))

    def _eliminate_if_defeated(self, player_id: PlayerId, command_id: CommandId) -> list[EventEnvelope]:
        if any(unit.owner_id == player_id for unit in self.session.units.values()) or any(item.owner_id == player_id for item in self.session.settlements.values()):
            return []
        if self.session.players[player_id].eliminated:
            return []
        self.session.players[player_id].eliminated = True
        return [self._emit("PlayerEliminated", {"player_id": player_id, "reason": "defeated"}, command_id)]

    def _victory_event(self, player_id: PlayerId, kind: str, command_id: CommandId) -> EventEnvelope:
        return self._emit("VictoryAchieved", {"player_id": player_id, "victory_kind": kind}, command_id)

    def _active_player(self, command: CommandEnvelope) -> PlayerId | None:
        if self.session.status is not GameStatus.ACTIVE or command.player_id != self.session.current_player_id:
            return None
        return command.player_id

    def _player_target(self, command: CommandEnvelope) -> tuple[PlayerId | None, PlayerId | None]:
        player_id = self._active_player(command)
        raw_target = command.payload.get("target_player_id")
        if player_id is None or not isinstance(raw_target, str):
            return None, None
        target = PlayerId(raw_target)
        if target == player_id or target not in self.session.players or self.session.players[target].eliminated:
            return None, None
        return player_id, target

    def _owned_settlement(self, command: CommandEnvelope, player_id: PlayerId) -> SettlementState | None:
        raw_id = command.payload.get("settlement_id")
        if not isinstance(raw_id, str):
            return None
        item = self.session.settlements.get(SettlementId(raw_id))
        return item if item is not None and item.owner_id == player_id else None

    def _update_player_visibility(self, player_id: PlayerId) -> None:
        player = self.session.players[player_id]
        origins = [(unit.position, unit.definition.vision_radius) for unit in self.session.units.values() if unit.owner_id == player_id]
        origins.extend((item.center, 1) for item in self.session.settlements.values() if item.owner_id == player_id)
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
