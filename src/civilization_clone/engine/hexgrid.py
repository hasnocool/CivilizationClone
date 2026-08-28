"""Pure axial-hex coordinate utilities."""

from civilization_clone.domain.map import HexCoord

_DIRECTIONS = (
    HexCoord(1, 0),
    HexCoord(1, -1),
    HexCoord(0, -1),
    HexCoord(-1, 0),
    HexCoord(-1, 1),
    HexCoord(0, 1),
)


def add(left: HexCoord, right: HexCoord) -> HexCoord:
    """Add two axial coordinates."""
    return HexCoord(left.q + right.q, left.r + right.r)


def neighbors(coord: HexCoord) -> tuple[HexCoord, ...]:
    """Return all six adjacent coordinates in stable clockwise order."""
    return tuple(add(coord, direction) for direction in _DIRECTIONS)


def distance(left: HexCoord, right: HexCoord) -> int:
    """Return axial/cube hex distance."""
    dq = left.q - right.q
    dr = left.r - right.r
    ds = left.s - right.s
    return max(abs(dq), abs(dr), abs(ds))


def ring(center: HexCoord, radius: int) -> tuple[HexCoord, ...]:
    """Return exactly one ring around center in deterministic traversal order."""
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if radius == 0:
        return (center,)

    current = center
    for _ in range(radius):
        current = add(current, _DIRECTIONS[4])

    result: list[HexCoord] = []
    for direction in _DIRECTIONS:
        for _ in range(radius):
            result.append(current)
            current = add(current, direction)
    return tuple(result)


def within_radius(center: HexCoord, radius: int) -> tuple[HexCoord, ...]:
    """Return the complete hex disk around center, sorted for stable iteration."""
    if radius < 0:
        raise ValueError("radius must be non-negative")

    coords = [
        HexCoord(center.q + q, center.r + r)
        for q in range(-radius, radius + 1)
        for r in range(-radius, radius + 1)
        if abs(q + r) <= radius
    ]
    return tuple(sorted(coords))
