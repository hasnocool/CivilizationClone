# tests/unit/test_pathfinding.py
import pytest

from civilization_clone.domain.map import HexCoord, TerrainType, Tile, WorldMap
from civilization_clone.engine.hexgrid import within_radius
from civilization_clone.engine.pathfinding import PathNotFound, find_path, path_cost


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
