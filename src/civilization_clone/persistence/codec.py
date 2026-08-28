"""Canonical save-document codec for deterministic engine restoration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from civilization_clone.domain.economy import ProductionKind, ProductionOrder, SettlementState
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
    CivilizationId,
    CommandId,
    EventId,
    GameId,
    PlayerId,
    RulesetId,
    SettlementId,
    UnitId,
)
from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile, WorldMap
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.strategy import (
    DiplomaticRelationship,
    DiplomacyStatus,
    ResearchState,
    TradeOffer,
    VictoryResult,
    VictoryType,
)
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.advanced import AdvancedGameEngine
from civilization_clone.engine.economy import UNITS
from civilization_clone.engine.event_log import EventLog
from civilization_clone.engine.session import CommandResult, GameEngine
from civilization_clone.engine.state_hash import state_hash as canonical_state_hash

_SAVE_VERSION = 3
_PRE_TRADE_SAVE_VERSION = 2
_LEGACY_SAVE_VERSION = 1


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def _event_to_data(event: EventEnvelope) -> dict[str, Any]:
    return {
        "event_id": str(event.event_id),
        "game_id": str(event.game_id),
        "sequence": event.sequence,
        "event_type": event.event_type,
        "state_version": event.state_version,
        "payload": _jsonable(event.payload),
        "causation_command_id": (
            str(event.causation_command_id) if event.causation_command_id is not None else None
        ),
    }


def _event_from_data(data: Mapping[str, Any]) -> EventEnvelope:
    causation = data.get("causation_command_id")
    return EventEnvelope.create(
        event_id=EventId(str(data["event_id"])),
        game_id=GameId(str(data["game_id"])),
        sequence=int(data["sequence"]),
        event_type=str(data["event_type"]),
        state_version=int(data["state_version"]),
        payload=dict(data.get("payload", {})),
        causation_command_id=CommandId(str(causation)) if causation is not None else None,
    )


def _feedback_to_data(feedback: UserFeedback) -> dict[str, Any]:
    return {
        "code": feedback.code,
        "message": feedback.message,
        "severity": feedback.severity.value,
        "context": dict(feedback.context),
    }


def _feedback_from_data(data: Mapping[str, Any]) -> UserFeedback:
    return UserFeedback(
        code=str(data["code"]),
        message=str(data["message"]),
        severity=FeedbackSeverity(str(data["severity"])),
        context={str(key): str(value) for key, value in dict(data.get("context", {})).items()},
    )


def _result_to_data(result: CommandResult) -> dict[str, Any]:
    return {
        "accepted": result.accepted,
        "state_version": result.state_version,
        "events": [_event_to_data(event) for event in result.events],
        "feedback": [_feedback_to_data(feedback) for feedback in result.feedback],
    }


def _result_from_data(data: Mapping[str, Any]) -> CommandResult:
    return CommandResult(
        accepted=bool(data["accepted"]),
        state_version=int(data["state_version"]),
        events=tuple(_event_from_data(item) for item in data.get("events", [])),
        feedback=tuple(_feedback_from_data(item) for item in data.get("feedback", [])),
    )


def engine_to_document(engine: GameEngine) -> dict[str, Any]:
    """Serialize authoritative state, journal, and idempotency cache."""
    processed = [
        {
            "command_id": str(command_id),
            "result": _result_to_data(result),
        }
        for command_id, result in engine._processed.items()
    ]
    return {
        "save_version": _SAVE_VERSION,
        "state": engine.session.canonical_state(),
        "events": [_event_to_data(event) for event in engine.event_log.snapshot()],
        "processed": processed,
        "state_hash": engine.state_hash(),
        "event_hash": engine.event_hash(),
    }


def engine_from_document(document: Mapping[str, Any]) -> GameEngine:
    """Restore a complete engine and verify persisted deterministic hashes.

    Save version 1 predates civilization identity. Save version 2 predates v1.1
    trade diplomacy fields. Older snapshots are verified in their original canonical
    form before deterministic default migration; version 3 is verified after restore.
    """
    save_version = int(document.get("save_version", 0))
    if save_version not in {_LEGACY_SAVE_VERSION, _PRE_TRADE_SAVE_VERSION, _SAVE_VERSION}:
        raise ValueError("unsupported save document version")

    state_data = _mapping(document["state"])
    expected_state_hash = str(document.get("state_hash", ""))
    if (
        save_version in {_LEGACY_SAVE_VERSION, _PRE_TRADE_SAVE_VERSION}
        and expected_state_hash
        and canonical_state_hash(state_data) != expected_state_hash
    ):
        raise ValueError("pre-v1.1 state snapshot does not match persisted checkpoint")

    session = _session_from_state(state_data)
    journal = EventLog(session.game_id)
    journal.extend(_event_from_data(_mapping(item)) for item in document.get("events", []))
    processed = {
        CommandId(str(item["command_id"])): _result_from_data(_mapping(item["result"]))
        for item in document.get("processed", [])
    }
    engine = AdvancedGameEngine(session=session, event_log=journal, _processed=processed)

    if (
        save_version == _SAVE_VERSION
        and expected_state_hash
        and engine.state_hash() != expected_state_hash
    ):
        raise ValueError("restored state hash does not match persisted checkpoint")
    expected_event_hash = str(document.get("event_hash", ""))
    if expected_event_hash and engine.event_hash() != expected_event_hash:
        raise ValueError("restored event hash does not match persisted checkpoint")
    return engine


def _session_from_state(state: Mapping[str, Any]) -> GameSession:
    ruleset_data = _mapping(state["ruleset"])
    world = _world_from_state(_mapping(state["world"]))
    session = GameSession(
        game_id=GameId(str(state["game_id"])),
        ruleset=RulesetRef(
            RulesetId(str(ruleset_data["id"])),
            str(ruleset_data["version"]),
        ),
        seed=int(state["seed"]),
        world=world,
        max_turns=int(state.get("max_turns", 60)),
        next_unit_index=int(state.get("next_unit_index", 0)),
        next_settlement_index=int(state.get("next_settlement_index", 0)),
        turn=int(state.get("turn", 0)),
        active_player_index=int(state.get("active_player_index", 0)),
        state_version=int(state.get("state_version", 0)),
        status=GameStatus(str(state.get("status", GameStatus.SETUP.value))),
        phase=GamePhase(str(state.get("phase", GamePhase.SETUP.value))),
    )

    for raw_player in state.get("players", []):
        player_data = _mapping(raw_player)
        player_id = PlayerId(str(player_data["player_id"]))
        research_data = _mapping(player_data.get("research", {}))
        visibility = {
            HexCoord(int(item["q"]), int(item["r"])): Visibility(str(item["state"]))
            for item in player_data.get("visibility", [])
        }
        session.players[player_id] = PlayerState(
            player_id=player_id,
            name=str(player_data["name"]),
            controller=ControllerType(str(player_data.get("controller", "human"))),
            civilization_id=CivilizationId(
                str(player_data.get("civilization_id", "river_compact"))
            ),
            visibility=visibility,
            gold=int(player_data.get("gold", 0)),
            science=int(player_data.get("science", 0)),
            culture=int(player_data.get("culture", 0)),
            research=ResearchState(
                selected=(
                    str(research_data["selected"])
                    if research_data.get("selected") is not None
                    else None
                ),
                progress=int(research_data.get("progress", 0)),
                completed={str(item) for item in research_data.get("completed", [])},
            ),
            eliminated=bool(player_data.get("eliminated", False)),
            ever_had_presence=bool(player_data.get("ever_had_presence", False)),
        )

    session.player_order = [PlayerId(str(item)) for item in state.get("player_order", [])]

    for raw_unit in state.get("units", []):
        unit_data = _mapping(raw_unit)
        unit_id = UnitId(str(unit_data["unit_id"]))
        definition = _unit_definition(str(unit_data["definition_id"]))
        position_data = _mapping(unit_data["position"])
        session.units[unit_id] = UnitState(
            unit_id=unit_id,
            owner_id=PlayerId(str(unit_data["owner_id"])),
            definition=definition,
            position=HexCoord(int(position_data["q"]), int(position_data["r"])),
            movement_remaining=int(unit_data["movement_remaining"]),
            hit_points=int(unit_data.get("hit_points", 100)),
        )

    for raw_settlement in state.get("settlements", []):
        settlement_data = _mapping(raw_settlement)
        center_data = _mapping(settlement_data["center"])
        settlement_id = SettlementId(str(settlement_data["settlement_id"]))
        session.settlements[settlement_id] = SettlementState(
            settlement_id=settlement_id,
            owner_id=PlayerId(str(settlement_data["owner_id"])),
            center=HexCoord(int(center_data["q"]), int(center_data["r"])),
            population=int(settlement_data.get("population", 1)),
            food_storage=int(settlement_data.get("food_storage", 0)),
            production_storage=int(settlement_data.get("production_storage", 0)),
            territory={
                HexCoord(int(item["q"]), int(item["r"]))
                for item in settlement_data.get("territory", [])
            },
            worked_tiles={
                HexCoord(int(item["q"]), int(item["r"]))
                for item in settlement_data.get("worked_tiles", [])
            },
            buildings={str(item) for item in settlement_data.get("buildings", [])},
            production_queue=[
                ProductionOrder(
                    ProductionKind(str(item["kind"])),
                    str(item["definition_id"]),
                    int(item["cost"]),
                )
                for item in settlement_data.get("production_queue", [])
            ],
        )

    for raw_relationship in state.get("diplomacy", []):
        relationship_data = _mapping(raw_relationship)
        first = PlayerId(str(relationship_data["first_player_id"]))
        second = PlayerId(str(relationship_data["second_player_id"]))
        pending = relationship_data.get("pending_peace_from")
        raw_trade = relationship_data.get("pending_trade")
        trade: TradeOffer | None = None
        if raw_trade is not None:
            trade_data = _mapping(raw_trade)
            trade = TradeOffer(
                proposer_id=PlayerId(str(trade_data["proposer_id"])),
                offered_gold=int(trade_data["offered_gold"]),
                requested_gold=int(trade_data["requested_gold"]),
            )
        last_trade_turn = relationship_data.get("last_trade_turn")
        session.diplomacy[(first, second)] = DiplomaticRelationship(
            status=DiplomacyStatus(str(relationship_data["status"])),
            pending_peace_from=PlayerId(str(pending)) if pending is not None else None,
            pending_trade=trade,
            completed_trades=int(relationship_data.get("completed_trades", 0)),
            last_trade_turn=int(last_trade_turn) if last_trade_turn is not None else None,
        )

    raw_victory = state.get("victory")
    if raw_victory is not None:
        victory_data = _mapping(raw_victory)
        session.victory = VictoryResult(
            winner_id=PlayerId(str(victory_data["winner_id"])),
            victory_type=VictoryType(str(victory_data["victory_type"])),
            turn=int(victory_data["turn"]),
            score=int(victory_data["score"]),
        )
    return session


def _world_from_state(data: Mapping[str, Any]) -> WorldMap:
    tiles: dict[HexCoord, Tile] = {}
    for raw_tile in data.get("tiles", []):
        tile_data = _mapping(raw_tile)
        coord = HexCoord(int(tile_data["q"]), int(tile_data["r"]))
        raw_resource = tile_data.get("resource")
        tiles[coord] = Tile(
            coord=coord,
            terrain=TerrainType(str(tile_data["terrain"])),
            resource=ResourceType(str(raw_resource)) if raw_resource is not None else None,
        )
    return WorldMap(
        radius=int(data["radius"]),
        seed=int(data["seed"]),
        tiles=tiles,
        spawns=tuple(
            HexCoord(int(item["q"]), int(item["r"])) for item in data.get("spawns", [])
        ),
    )


def _unit_definition(definition_id: str) -> UnitDefinition:
    definition = UNITS.get(definition_id)
    if definition is not None:
        return definition
    if definition_id == "founder":
        return UnitDefinition(
            "founder",
            movement=2,
            vision_radius=1,
            can_found=True,
            attack_strength=1,
            defense_strength=2,
        )
    return UnitDefinition(definition_id)


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("save document field must be an object")
    return value
