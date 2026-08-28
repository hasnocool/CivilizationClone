# tests/unit/test_hexgrid.py
import pytest

from civilization_clone.domain.map import HexCoord
from civilization_clone.engine.hexgrid import distance, line, neighbors, ring, within_radius


def test_neighbors_are_six_unique_adjacent_coordinates() -> None:
    origin = HexCoord(0, 0)
    adjacent = neighbors(origin)

    assert len(adjacent) == 6
    assert len(set(adjacent)) == 6
    assert all(distance(origin, coord) == 1 for coord in adjacent)


def test_distance_is_symmetric() -> None:
    left = HexCoord(2, -1)
    right = HexCoord(-1, 1)

    assert distance(left, right) == 3
    assert distance(left, right) == distance(right, left)


@pytest.mark.parametrize("radius", [1, 2, 3, 4])
def test_ring_has_exactly_six_times_radius_tiles(radius: int) -> None:
    coords = ring(HexCoord(0, 0), radius)

    assert len(coords) == 6 * radius
    assert len(set(coords)) == len(coords)
    assert all(distance(HexCoord(0, 0), coord) == radius for coord in coords)


def test_hex_disk_tile_count_matches_formula() -> None:
    radius = 4
    coords = within_radius(HexCoord(0, 0), radius)

    assert len(coords) == 1 + 3 * radius * (radius + 1)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (HexCoord(0, 0), HexCoord(4, -2)),
        (HexCoord(-3, 1), HexCoord(2, 2)),
        (HexCoord(2, -3), HexCoord(-2, 1)),
    ],
)
def test_hex_line_is_shortest_connected_and_reversible(start: HexCoord, end: HexCoord) -> None:
    forward = line(start, end)
    reverse = line(end, start)

    assert forward[0] == start
    assert forward[-1] == end
    assert len(forward) == distance(start, end) + 1
    assert all(distance(left, right) == 1 for left, right in zip(forward, forward[1:]))
    assert forward == tuple(reversed(reverse))


def test_hex_line_single_coordinate_is_stable() -> None:
    coord = HexCoord(2, -1)
    assert line(coord, coord) == (coord,)
