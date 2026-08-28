"""Hex-world domain models for deterministic map simulation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


@dataclass(frozen=True, order=True, slots=True)
class HexCoord:
    """Axial hex coordinate using q/r with derived cube coordinate s."""

    q: int
    r: int

    @property
    def s(self) -> int:
        return -self.q - self.r


class TerrainType(StrEnum):
    """Original proof-of-concept terrain categories."""

    WATER = "water"
    PLAINS = "plains"
    GRASSLAND = "grassland"
    HILLS = "hills"
    DESERT = "desert"
    TUNDRA = "tundra"


class ResourceType(StrEnum):
    """Original proof-of-concept resource categories."""

    FOOD = "food"
    MINERAL = "mineral"
    GOLD = "gold"


_TERRAIN_COST: dict[TerrainType, int | None] = {
    TerrainType.WATER: None,
    TerrainType.PLAINS: 1,
    TerrainType.GRASSLAND: 1,
    TerrainType.HILLS: 2,
    TerrainType.DESERT: 2,
    TerrainType.TUNDRA: 2,
}


@dataclass(frozen=True, slots=True)
class Tile:
    """One immutable tile in the authoritative world map."""

    coord: HexCoord
    terrain: TerrainType
    resource: ResourceType | None = None

    @property
    def passable(self) -> bool:
        return _TERRAIN_COST[self.terrain] is not None

    @property
    def movement_cost(self) -> int:
        cost = _TERRAIN_COST[self.terrain]
        if cost is None:
            raise ValueError("impassable tile has no movement cost")
        return cost


@dataclass(frozen=True, slots=True)
class WorldMap:
    """Immutable coordinate-indexed world map."""

    radius: int
    seed: int
    tiles: Mapping[HexCoord, Tile]
    spawns: tuple[HexCoord, ...] = ()

    def __post_init__(self) -> None:
        if self.radius < 1:
            raise ValueError("map radius must be at least 1")
        object.__setattr__(self, "tiles", MappingProxyType(dict(self.tiles)))
        if any(coord not in self.tiles for coord in self.spawns):
            raise ValueError("spawn coordinates must exist in map")

    def tile(self, coord: HexCoord) -> Tile:
        """Return the tile at one exact coordinate."""
        return self.tiles[coord]

    def canonical_state(self) -> dict[str, object]:
        """Return a JSON-key-safe deterministic representation for hashing/replay."""
        return {
            "radius": self.radius,
            "seed": self.seed,
            "spawns": [{"q": coord.q, "r": coord.r} for coord in self.spawns],
            "tiles": [
                {
                    "q": coord.q,
                    "r": coord.r,
                    "terrain": tile.terrain.value,
                    "resource": tile.resource.value if tile.resource is not None else None,
                }
                for coord, tile in sorted(self.tiles.items())
            ],
        }
