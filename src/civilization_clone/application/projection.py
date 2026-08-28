"""Authorized client projections over authoritative game state and events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId, SettlementId, UnitId
from civilization_clone.domain.map import HexCoord
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.research import available_technologies
from civilization_clone.rules.poc import POC_CIVILIZATIONS_BY_ID


def project_game(session: GameSession, viewer_id: PlayerId) -> dict[str, Any]:
    """Build a player-authorized snapshot without exposing unknown map or hidden units."""
    player = session.players.get(viewer_id)
    if player is None:
        raise KeyError(f"player not found: {viewer_id}")
    civilization = POC_CIVILIZATIONS_BY_ID.get(player.civilization_id)

    tiles = []
    for coord, visibility in sorted(player.visibility.items()):
        if visibility is Visibility.UNKNOWN:
            continue
        tile = session.world.tiles[coord]
        tiles.append(
            {
                "q": coord.q,
                "r": coord.r,
                "visibility": visibility.value,
                "terrain": tile.terrain.value,
                "resource": tile.resource.value if tile.resource is not None else None,
            }
        )

    visible_coords = {
        coord for coord, visibility in player.visibility.items() if visibility is Visibility.VISIBLE
    }
    units = [
        {
            "unit_id": str(unit.unit_id),
            "owner_id": str(unit.owner_id),
            "definition_id": unit.definition.definition_id,
            "q": unit.position.q,
            "r": unit.position.r,
            "movement_remaining": unit.movement_remaining if unit.owner_id == viewer_id else None,
            "hit_points": unit.hit_points,
        }
        for _, unit in sorted(session.units.items())
        if unit.owner_id == viewer_id or unit.position in visible_coords
    ]
    settlements = [
        {
            "settlement_id": str(settlement.settlement_id),
            "owner_id": str(settlement.owner_id),
            "q": settlement.center.q,
            "r": settlement.center.r,
            "population": settlement.population,
            "food_storage": settlement.food_storage if settlement.owner_id == viewer_id else None,
            "production_storage": (
                settlement.production_storage if settlement.owner_id == viewer_id else None
            ),
            "buildings": (
                sorted(settlement.buildings) if settlement.owner_id == viewer_id else []
            ),
            "production_queue": (
                [
                    {
                        "kind": order.kind.value,
                        "definition_id": order.definition_id,
                        "cost": order.cost,
                    }
                    for order in settlement.production_queue
                ]
                if settlement.owner_id == viewer_id
                else []
            ),
        }
        for _, settlement in sorted(session.settlements.items())
        if settlement.owner_id == viewer_id or settlement.center in visible_coords
    ]
    diplomacy = [
        {
            "other_player_id": str(second if first == viewer_id else first),
            "status": relationship.status.value,
            "pending_peace_from": (
                str(relationship.pending_peace_from)
                if relationship.pending_peace_from is not None
                else None
            ),
        }
        for (first, second), relationship in sorted(session.diplomacy.items())
        if viewer_id in (first, second)
    ]
    victory = None
    if session.victory is not None:
        victory = {
            "winner_id": str(session.victory.winner_id),
            "victory_type": session.victory.victory_type.value,
            "turn": session.victory.turn,
            "score": session.victory.score,
        }

    return {
        "game_id": str(session.game_id),
        "turn": session.turn,
        "state_version": session.state_version,
        "status": session.status.value,
        "phase": session.phase.value,
        "active_player_id": (
            str(session.current_player_id) if session.current_player_id is not None else None
        ),
        "viewer": {
            "player_id": str(viewer_id),
            "name": player.name,
            "controller": player.controller.value,
            "civilization_id": str(player.civilization_id),
            "gold": player.gold,
            "science": player.science,
            "culture": player.culture,
            "research": {
                "selected": player.research.selected,
                "progress": player.research.progress,
                "completed": sorted(player.research.completed),
                "available": list(available_technologies(player)),
                "preferences": (
                    list(civilization.research_preferences)
                    if civilization is not None
                    else []
                ),
            },
            "eliminated": player.eliminated,
        },
        "players": [
            {
                "player_id": str(player_id),
                "name": other.name,
                "controller": other.controller.value,
                "civilization_id": str(other.civilization_id),
                "eliminated": other.eliminated,
            }
            for player_id, other in sorted(session.players.items())
        ],
        "map": {
            "radius": session.world.radius,
            "tiles": tiles,
        },
        "units": units,
        "settlements": settlements,
        "diplomacy": diplomacy,
        "victory": victory,
    }


def project_event(
    session: GameSession,
    event: EventEnvelope,
    viewer_id: PlayerId,
) -> dict[str, Any] | None:
    """Return a safe event representation or None when the event is not authorized."""
    player = session.players.get(viewer_id)
    if player is None:
        raise KeyError(f"player not found: {viewer_id}")

    payload = _plain_payload(event.payload)
    event_type = event.event_type
    globally_safe = {
        "GameStarted",
        "TurnStarted",
        "TurnEnded",
        "PlayerJoined",
        "PlayerEndedTurn",
        "WarDeclared",
        "PlayerConceded",
        "PlayerEliminated",
        "VictoryAchieved",
    }
    if event_type in globally_safe:
        return _event_projection(event, payload)

    if event_type in {"PeaceOffered", "PeaceAccepted", "PeaceRejected"}:
        if viewer_id in _diplomacy_participants(session, payload):
            return _event_projection(event, payload)
        return None

    owner = _event_owner(session, payload)
    if owner == viewer_id:
        return _event_projection(event, payload)

    coord = _event_coord(payload)
    if coord is not None and player.visibility.get(coord) is Visibility.VISIBLE:
        return _event_projection(event, payload)

    if event_type in {"UnitAttacked", "UnitDamaged", "UnitDestroyed"}:
        involved = _combat_involved_players(session, payload)
        if viewer_id in involved:
            return _event_projection(event, payload)

    return None


def _event_projection(event: EventEnvelope, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": str(event.event_id),
        "sequence": event.sequence,
        "event_type": event.event_type,
        "state_version": event.state_version,
        "payload": payload,
    }


def _event_owner(session: GameSession, payload: Mapping[str, Any]) -> PlayerId | None:
    for key in ("player_id", "owner_id"):
        raw = payload.get(key)
        if isinstance(raw, str) and raw in session.players:
            return PlayerId(raw)
    raw_unit = payload.get("unit_id")
    if isinstance(raw_unit, str):
        unit = session.units.get(UnitId(raw_unit))
        if unit is not None:
            return unit.owner_id
    raw_settlement = payload.get("settlement_id")
    if isinstance(raw_settlement, str):
        settlement = session.settlements.get(SettlementId(raw_settlement))
        if settlement is not None:
            return settlement.owner_id
    return None


def _event_coord(payload: Mapping[str, Any]) -> HexCoord | None:
    q = payload.get("q", payload.get("to_q"))
    r = payload.get("r", payload.get("to_r"))
    if (
        isinstance(q, int)
        and not isinstance(q, bool)
        and isinstance(r, int)
        and not isinstance(r, bool)
    ):
        return HexCoord(q, r)
    return None


def _diplomacy_participants(
    session: GameSession,
    payload: Mapping[str, Any],
) -> set[PlayerId]:
    participants: set[PlayerId] = set()
    for key in ("player_id", "target_player_id"):
        raw = payload.get(key)
        if isinstance(raw, str) and raw in session.players:
            participants.add(PlayerId(raw))
    return participants


def _combat_involved_players(
    session: GameSession,
    payload: Mapping[str, Any],
) -> set[PlayerId]:
    players: set[PlayerId] = set()
    for key in ("attacker_id", "defender_id", "unit_id"):
        raw = payload.get(key)
        if not isinstance(raw, str):
            continue
        unit = session.units.get(UnitId(raw))
        if unit is not None:
            players.add(unit.owner_id)
    for key in ("attacker_owner_id", "defender_owner_id", "owner_id"):
        raw = payload.get(key)
        if isinstance(raw, str) and raw in session.players:
            players.add(PlayerId(raw))
    return players


def _plain_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain_payload(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_payload(item) for item in value]
    return value
