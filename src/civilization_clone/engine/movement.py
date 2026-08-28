"""Validated deterministic unit movement."""

from __future__ import annotations

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId, UnitId
from civilization_clone.domain.map import HexCoord
from civilization_clone.engine.hexgrid import distance


def validate_move(
    session: GameSession,
    player_id: PlayerId,
    unit_id: UnitId,
    destination: HexCoord,
) -> str | None:
    """Return a stable rejection reason, or None when movement is legal."""
    if session.current_player_id != player_id:
        return "not_active_player"
    unit = session.units.get(unit_id)
    if unit is None:
        return "unit_not_found"
    if unit.owner_id != player_id:
        return "not_unit_owner"
    tile = session.world.tiles.get(destination)
    if tile is None:
        return "destination_outside_map"
    if not tile.passable:
        return "destination_impassable"
    if distance(unit.position, destination) != 1:
        return "destination_not_adjacent"
    if any(other.position == destination for other in session.units.values()):
        return "destination_occupied"
    if tile.movement_cost > unit.movement_remaining:
        return "insufficient_movement"
    return None


def apply_move(
    session: GameSession,
    unit_id: UnitId,
    destination: HexCoord,
) -> tuple[HexCoord, int]:
    """Apply an already-validated move and return old position plus movement cost."""
    unit = session.units[unit_id]
    origin = unit.position
    cost = session.world.tile(destination).movement_cost
    unit.position = destination
    unit.movement_remaining -= cost
    return origin, cost
