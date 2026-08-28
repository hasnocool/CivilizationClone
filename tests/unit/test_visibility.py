# tests/unit/test_visibility.py
from civilization_clone.domain.ids import GameId
from civilization_clone.domain.map import HexCoord
from civilization_clone.engine.mapgen import MapGenerationConfig, generate_world
from civilization_clone.engine.visibility import Visibility, update_visibility, visible_coords


def test_visible_tiles_become_discovered_after_moving_away() -> None:
    world = generate_world(
        game_id=GameId("visibility"),
        seed=9,
        config=MapGenerationConfig(radius=3),
    ).world

    first_visible = visible_coords(world, [HexCoord(0, 0)], 1)
    first_state = update_visibility(world, {}, first_visible)
    moved_visible = visible_coords(world, [HexCoord(2, -1)], 1)
    moved_state = update_visibility(world, first_state, moved_visible)

    assert first_state[HexCoord(0, 0)] is Visibility.VISIBLE
    assert moved_state[HexCoord(0, 0)] is Visibility.DISCOVERED
    assert moved_state[HexCoord(2, -1)] is Visibility.VISIBLE
