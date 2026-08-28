# tests/unit/test_pathfinding.py
import pytest

from civilization_clone.domain.map import HexCoord, TerrainType, Tile, WorldMap
from civilization_clone.engine.hexgrid import within_radius
from civilization_clone.engine.pathfinding import (
    PathNotFound,
    find_path,
    movement_range,
    path_cost,
)


def _test_world() -> WorldMap:
    tiles = {
        coord: Tile(coord, TerrainType.PLAINS)
        for coord in within_radius(HexCoord(0, 0), 2)
    }
    blocked = HexCoord(1, 0)
    tiles[blocked] = Tile(blocked, TerrainType.WATER)
    return WorldMap(radius=2, seed=1, tiles=tiles)


def test_pathfinding_avoids_impassable_tiles_and_is_reproducible() -> None:
    world = _test_world()

    first = find_path(world, HexCoord(0, 0), HexCoord(2, -1))
    second = find_path(world, HexCoord(0, 0), HexCoord(2, -1))

    assert first == second
    assert HexCoord(1, 0) not in first
    assert path_cost(world, first) == len(first) - 1


def test_pathfinding_rejects_impassable_goal() -> None:
    with pytest.raises(PathNotFound, match="passable"):
        find_path(_test_world(), HexCoord(0, 0), HexCoord(1, 0))


def test_movement_range_respects_budget_impassable_and_blocked_tiles() -> None:
    world = _test_world()
    start = HexCoord(0, 0)
    occupied = HexCoord(0, 1)

    reachable = movement_range(world, start, 2, blocked={occupied})
    repeated = movement_range(world, start, 2, blocked={occupied})

    assert reachable == repeated
    assert start in reachable
    assert HexCoord(1, 0) not in reachable
    assert occupied not in reachable
    assert all(coord in world.tiles and world.tile(coord).passable for coord in reachable)
    assert all(path_cost(world, find_path(world, start, coord)) <= 2 for coord in reachable)


def test_movement_range_rejects_negative_budget() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        movement_range(_test_world(), HexCoord(0, 0), -1)
