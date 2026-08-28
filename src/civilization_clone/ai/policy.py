"""Deterministic bot policies that consume only authorized player projections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.domain.map import HexCoord
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.hexgrid import distance, neighbors


class BotPolicy(Protocol):
    """Policy interface restricted to a player-authorized snapshot."""

    def choose_command(
        self,
        view: Mapping[str, Any],
        *,
        decision_number: int,
    ) -> CommandEnvelope:
        """Choose exactly one normal engine command from an authorized view."""


class SimpleBotPolicy:
    """Small deterministic policy for exploration, growth, research, trade, and combat."""

    def choose_command(
        self,
        view: Mapping[str, Any],
        *,
        decision_number: int,
    ) -> CommandEnvelope:
        game_id = GameId(str(view["game_id"]))
        viewer = _mapping(view["viewer"])
        player_id = PlayerId(str(viewer["player_id"]))
        version = int(view["state_version"])
        command_id = CommandId(f"bot-{player_id}-{decision_number}")

        if view.get("status") != "active" or view.get("active_player_id") != player_id:
            return _command(command_id, game_id, player_id, version, "Concede")

        research = _mapping(viewer.get("research", {}))
        selected = research.get("selected")
        completed = {str(item) for item in research.get("completed", [])}
        if selected is None:
            available = tuple(str(item) for item in research.get("available", []))
            preferences = tuple(str(item) for item in research.get("preferences", []))
            technology = _preferred_available_technology(available, preferences)
            if technology is not None:
                return _command(
                    command_id,
                    game_id,
                    player_id,
                    version,
                    "ChooseResearch",
                    {"technology_id": technology},
                )

        own_units = [
            _mapping(unit)
            for unit in view.get("units", [])
            if _mapping(unit).get("owner_id") == player_id
        ]
        founder = next(
            (unit for unit in own_units if unit.get("definition_id") == "founder"),
            None,
        )
        if founder is not None:
            return _command(
                command_id,
                game_id,
                player_id,
                version,
                "FoundSettlement",
                {"unit_id": str(founder["unit_id"])},
            )

        diplomacy = [_mapping(item) for item in view.get("diplomacy", [])]
        trade_response = _trade_response(viewer, diplomacy)
        if trade_response is not None:
            command_type, payload = trade_response
            return _command(
                command_id,
                game_id,
                player_id,
                version,
                command_type,
                payload,
            )

        at_war_with = {
            str(item["other_player_id"])
            for item in diplomacy
            if item.get("status") == "war"
        }
        attack = _first_visible_attack(own_units, view.get("units", []), at_war_with)
        if attack is not None:
            return _command(
                command_id,
                game_id,
                player_id,
                version,
                "AttackUnit",
                attack,
            )

        own_settlements = [
            _mapping(settlement)
            for settlement in view.get("settlements", [])
            if _mapping(settlement).get("owner_id") == player_id
        ]
        for settlement in own_settlements:
            if not settlement.get("production_queue"):
                unit_id = "warrior" if "bronze_work" in completed else "scout"
                return _command(
                    command_id,
                    game_id,
                    player_id,
                    version,
                    "QueueProduction",
                    {
                        "settlement_id": str(settlement["settlement_id"]),
                        "kind": "unit",
                        "definition_id": unit_id,
                    },
                )

        turn = int(view.get("turn", 0))
        trade_target = _trade_offer_target(viewer, diplomacy)
        if 3 <= turn < 8 and trade_target is not None:
            return _command(
                command_id,
                game_id,
                player_id,
                version,
                "OfferTrade",
                {
                    "target_player_id": trade_target,
                    "offered_gold": 1,
                    "requested_gold": 1,
                },
            )

        if turn >= 8 and not at_war_with:
            peace = next(
                (item for item in diplomacy if item.get("status") == "peace"),
                None,
            )
            if peace is not None:
                return _command(
                    command_id,
                    game_id,
                    player_id,
                    version,
                    "DeclareWar",
                    {"target_player_id": str(peace["other_player_id"])},
                )

        movable = [
            unit
            for unit in own_units
            if int(unit.get("movement_remaining") or 0) > 0
            and unit.get("definition_id") != "founder"
        ]
        if movable and decision_number % 8 < 6:
            unit = movable[decision_number % len(movable)]
            origin = HexCoord(int(unit["q"]), int(unit["r"]))
            candidates = sorted(neighbors(origin))
            destination = candidates[decision_number % len(candidates)]
            return _command(
                command_id,
                game_id,
                player_id,
                version,
                "MoveUnit",
                {
                    "unit_id": str(unit["unit_id"]),
                    "q": destination.q,
                    "r": destination.r,
                },
            )

        return _command(command_id, game_id, player_id, version, "EndTurn")


def _trade_response(
    viewer: Mapping[str, Any],
    diplomacy: list[Mapping[str, Any]],
) -> tuple[str, dict[str, Any]] | None:
    player_id = str(viewer["player_id"])
    gold = int(viewer.get("gold", 0))
    for relation in sorted(diplomacy, key=lambda item: str(item.get("other_player_id", ""))):
        raw_offer = relation.get("pending_trade")
        if not isinstance(raw_offer, Mapping):
            continue
        offer = _mapping(raw_offer)
        if str(offer.get("proposer_id")) == player_id:
            continue
        offered_gold = int(offer.get("offered_gold", 0))
        requested_gold = int(offer.get("requested_gold", 0))
        target = str(relation["other_player_id"])
        if requested_gold <= offered_gold and gold >= requested_gold:
            return "AcceptTrade", {"target_player_id": target}
        return "RejectTrade", {"target_player_id": target}
    return None


def _trade_offer_target(
    viewer: Mapping[str, Any],
    diplomacy: list[Mapping[str, Any]],
) -> str | None:
    if int(viewer.get("gold", 0)) < 1:
        return None
    candidates = [
        relation
        for relation in diplomacy
        if relation.get("status") == "peace"
        and relation.get("pending_trade") is None
        and int(relation.get("completed_trades", 0)) == 0
    ]
    if not candidates:
        return None
    chosen = min(candidates, key=lambda item: str(item.get("other_player_id", "")))
    return str(chosen["other_player_id"])


def _preferred_available_technology(
    available: tuple[str, ...],
    preferences: tuple[str, ...],
) -> str | None:
    available_set = set(available)
    for technology_id in preferences:
        if technology_id in available_set:
            return technology_id
    return min(available_set) if available_set else None


def _first_visible_attack(
    own_units: list[Mapping[str, Any]],
    all_units: Any,
    at_war_with: set[str],
) -> dict[str, str] | None:
    enemies = [
        _mapping(unit)
        for unit in all_units
        if str(_mapping(unit).get("owner_id")) in at_war_with
    ]
    for attacker in sorted(own_units, key=lambda unit: str(unit["unit_id"])):
        if int(attacker.get("movement_remaining") or 0) <= 0:
            continue
        attacker_coord = HexCoord(int(attacker["q"]), int(attacker["r"]))
        attack_range = 2 if attacker.get("definition_id") == "archer" else 1
        for defender in sorted(enemies, key=lambda unit: str(unit["unit_id"])):
            defender_coord = HexCoord(int(defender["q"]), int(defender["r"]))
            if distance(attacker_coord, defender_coord) <= attack_range:
                return {
                    "attacker_id": str(attacker["unit_id"]),
                    "defender_id": str(defender["unit_id"]),
                }
    return None


def _command(
    command_id: CommandId,
    game_id: GameId,
    player_id: PlayerId,
    version: int,
    command_type: str,
    payload: dict[str, Any] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=command_id,
        game_id=game_id,
        command_type=command_type,
        player_id=player_id,
        expected_state_version=version,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("bot view field must be an object")
    return value
