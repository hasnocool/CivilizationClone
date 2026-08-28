"""Deterministic A* pathfinding over hex maps."""

from __future__ import annotations

import heapq

from civilization_clone.domain.map import HexCoord, WorldMap
from civilization_clone.engine.hexgrid import distance, neighbors


class PathNotFound(ValueError):
    """Raised when no legal path can connect two requested coordinates."""


def find_path(world: WorldMap, start: HexCoord, goal: HexCoord) -> tuple[HexCoord, ...]:
    """Find the lowest-cost deterministic path between two passable map tiles."""
    if start not in world.tiles or goal not in world.tiles:
        raise PathNotFound("start and goal must exist")
    if not world.tile(start).passable or not world.tile(goal).passable:
        raise PathNotFound("start and goal must be passable")
    if start == goal:
        return (start,)

    frontier: list[tuple[int, int, int, int, HexCoord]] = []
    heapq.heappush(frontier, (distance(start, goal), 0, start.q, start.r, start))
    came_from: dict[HexCoord, HexCoord | None] = {start: None}
    costs: dict[HexCoord, int] = {start: 0}

    while frontier:
        _, current_cost, _, _, current = heapq.heappop(frontier)
        if current_cost != costs[current]:
            continue
        if current == goal:
            break

        for candidate in sorted(neighbors(current)):
            tile = world.tiles.get(candidate)
            if tile is None or not tile.passable:
                continue
            new_cost = current_cost + tile.movement_cost
            if new_cost >= costs.get(candidate, 10**18):
                continue
            costs[candidate] = new_cost
            came_from[candidate] = current
            heapq.heappush(
                frontier,
                (
                    new_cost + distance(candidate, goal),
                    new_cost,
                    candidate.q,
                    candidate.r,
                    candidate,
                ),
            )

    if goal not in came_from:
        raise PathNotFound("no path exists")

    reversed_path: list[HexCoord] = []
    cursor: HexCoord | None = goal
    while cursor is not None:
        reversed_path.append(cursor)
        cursor = came_from[cursor]
    reversed_path.reverse()
    return tuple(reversed_path)


def path_cost(world: WorldMap, path: tuple[HexCoord, ...]) -> int:
    """Return movement cost for a path, excluding the starting tile."""
    return sum(world.tile(coord).movement_cost for coord in path[1:])
