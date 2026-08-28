"""Fog-of-war primitives for player-specific map projections."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum
from types import MappingProxyType

from civilization_clone.domain.map import HexCoord, WorldMap
from civilization_clone.engine.hexgrid import distance


class Visibility(StrEnum):
    """Player-relative visibility state for one tile."""

    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    VISIBLE = "visible"


def visible_coords(
    world: WorldMap,
    origins: Iterable[HexCoord],
    radius: int,
) -> frozenset[HexCoord]:
    """Calculate currently visible coordinates around one or more origins."""
    if radius < 0:
        raise ValueError("radius must be non-negative")
    origin_tuple = tuple(origins)
    return frozenset(
        coord
        for coord in world.tiles
        if any(distance(coord, origin) <= radius for origin in origin_tuple)
    )


def update_visibility(
    world: WorldMap,
    previous: Mapping[HexCoord, Visibility],
    currently_visible: Iterable[HexCoord],
) -> Mapping[HexCoord, Visibility]:
    """Advance fog state without restoring previously hidden dynamic information."""
    visible = frozenset(currently_visible)
    result: dict[HexCoord, Visibility] = {}
    for coord in world.tiles:
        if coord in visible:
            result[coord] = Visibility.VISIBLE
        elif previous.get(coord) in (Visibility.VISIBLE, Visibility.DISCOVERED):
            result[coord] = Visibility.DISCOVERED
        else:
            result[coord] = Visibility.UNKNOWN
    return MappingProxyType(result)
