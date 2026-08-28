"""Deterministic proof-of-concept hex map generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import EventId, GameId
from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile, WorldMap
from civilization_clone.engine.hexgrid import distance, within_radius
from civilization_clone.engine.rng import RngFactory


@dataclass(frozen=True, slots=True)
class MapGenerationConfig:
    """Small deterministic map-generation configuration."""

    radius: int = 4
    player_count: int = 2
    water_percent: int = 20
    resource_percent: int = 18

    def __post_init__(self) -> None:
        if self.radius < 2:
            raise ValueError("radius must be at least 2")
        if not 2 <= self.player_count <= 4:
            raise ValueError("player_count must be 2..4")
        if not 0 <= self.water_percent <= 60:
            raise ValueError("water_percent must be 0..60")
        if not 0 <= self.resource_percent <= 60:
            raise ValueError("resource_percent must be 0..60")


@dataclass(frozen=True, slots=True)
class MapGenerationResult:
    """Generated map plus deterministic domain events describing generation."""

    world: WorldMap
    events: tuple[EventEnvelope, ...]


_TERRAINS = (
    TerrainType.PLAINS,
    TerrainType.GRASSLAND,
    TerrainType.HILLS,
    TerrainType.DESERT,
    TerrainType.TUNDRA,
)
_RESOURCES = (ResourceType.FOOD, ResourceType.MINERAL, ResourceType.GOLD)


def _land_terrain(roll: int) -> TerrainType:
    return _TERRAINS[roll % len(_TERRAINS)]


def _select_spawns(tiles: dict[HexCoord, Tile], count: int) -> tuple[HexCoord, ...]:
    center = HexCoord(0, 0)
    candidates = sorted(
        (coord for coord, tile in tiles.items() if tile.passable),
        key=lambda coord: (-distance(coord, center), coord.q, coord.r),
    )
    if len(candidates) < count:
        raise ValueError("not enough passable tiles for player spawns")

    selected = [candidates[0]]
    while len(selected) < count:
        remaining = [coord for coord in candidates if coord not in selected]
        best = max(
            remaining,
            key=lambda coord: (
                min(distance(coord, selected_coord) for selected_coord in selected),
                -coord.q,
                -coord.r,
            ),
        )
        selected.append(best)
    return tuple(selected)


def generate_world(
    *,
    game_id: GameId,
    seed: int,
    config: MapGenerationConfig | None = None,
    start_sequence: int = 0,
    state_version: int = 0,
    logger: logging.Logger | None = None,
) -> MapGenerationResult:
    """Generate one deterministic POC map and its map-generation events."""
    resolved_config = config or MapGenerationConfig()
    if logger is not None:
        logger.info(
            "map generation started",
            extra={"game_id": game_id, "operation": "map_generation", "seed": seed},
        )

    rng = RngFactory(seed).stream("map-generation")
    center = HexCoord(0, 0)
    tiles: dict[HexCoord, Tile] = {}

    for coord in within_radius(center, resolved_config.radius):
        edge = distance(coord, center) == resolved_config.radius
        water_roll = rng.randbelow(100)
        is_water = (water_roll < resolved_config.water_percent and coord != center) or (
            edge and water_roll < resolved_config.water_percent // 2
        )
        terrain = TerrainType.WATER if is_water else _land_terrain(rng.randbelow(1000))
        resource = None
        if terrain is not TerrainType.WATER and rng.randbelow(100) < resolved_config.resource_percent:
            resource = _RESOURCES[rng.randbelow(len(_RESOURCES))]
        tiles[coord] = Tile(coord=coord, terrain=terrain, resource=resource)

    tiles[center] = Tile(coord=center, terrain=TerrainType.GRASSLAND)
    spawns = _select_spawns(tiles, resolved_config.player_count)
    world = WorldMap(radius=resolved_config.radius, seed=seed, tiles=tiles, spawns=spawns)

    events = (
        EventEnvelope.create(
            event_id=EventId(f"map-{start_sequence}"),
            game_id=game_id,
            sequence=start_sequence,
            event_type="MapGenerationStarted",
            state_version=state_version,
            payload={"seed": seed, "radius": resolved_config.radius},
        ),
        EventEnvelope.create(
            event_id=EventId(f"map-{start_sequence + 1}"),
            game_id=game_id,
            sequence=start_sequence + 1,
            event_type="MapGenerated",
            state_version=state_version,
            payload={"tile_count": len(tiles), "spawn_count": len(spawns)},
        ),
    )
    if logger is not None:
        logger.info(
            "map generation completed",
            extra={
                "game_id": game_id,
                "operation": "map_generation",
                "tile_count": len(tiles),
                "spawn_count": len(spawns),
            },
        )
    return MapGenerationResult(world=world, events=events)
