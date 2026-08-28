from civilization_clone.client.tui import (
    parse_player_command,
    render_civilizations,
    render_map,
    render_state,
)


def test_parse_player_commands_cover_core_gameplay_surface() -> None:
    assert parse_player_command(["move", "u1", "2", "-1"]) == (
        "MoveUnit",
        {"unit_id": "u1", "q": 2, "r": -1},
    )
    assert parse_player_command(["research", "surveying"]) == (
        "ChooseResearch",
        {"technology_id": "surveying"},
    )
    assert parse_player_command(["produce", "s1", "unit", "scout"]) == (
        "QueueProduction",
        {"settlement_id": "s1", "kind": "unit", "definition_id": "scout"},
    )
    assert parse_player_command(["attack", "u1", "u2"]) == (
        "AttackUnit",
        {"attacker_id": "u1", "defender_id": "u2"},
    )
    assert parse_player_command(["reject", "p2"]) == (
        "RejectPeace",
        {"target_player_id": "p2"},
    )
    assert parse_player_command(["concede"]) == ("Concede", {})


def test_render_civilizations_explains_public_gameplay_bonuses() -> None:
    rendered = render_civilizations(
        [
            {
                "civilization_id": "horizon_league",
                "name": "Horizon League",
                "description": "Exploration and knowledge.",
                "tags": ["exploration", "knowledge"],
                "starting_resources": {"gold": 2, "science": 2},
                "yield_modifiers": [
                    {
                        "yield_type": "science",
                        "operation": "flat",
                        "value": 1,
                        "priority": 50,
                    }
                ],
                "research_cost_percent": -15,
                "attack_strength_percent": 0,
                "defense_strength_percent": 0,
            }
        ]
    )

    assert "Horizon League" in rendered
    assert "science +1 per settlement" in rendered
    assert "research cost -15%" in rendered
    assert "start gold +2, science +2" in rendered


def test_render_map_contains_only_projection_tiles_and_visible_entities() -> None:
    state = {
        "game_id": "g",
        "turn": 1,
        "status": "active",
        "active_player_id": "p1",
        "state_version": 3,
        "viewer": {
            "player_id": "p1",
            "civilization_id": "river_compact",
            "gold": 0,
            "science": 0,
            "culture": 0,
            "research": {"selected": None},
        },
        "map": {
            "radius": 2,
            "tiles": [
                {"q": 0, "r": 0, "terrain": "grassland", "visibility": "visible"},
                {"q": 1, "r": 0, "terrain": "hills", "visibility": "discovered"},
            ],
        },
        "units": [
            {
                "unit_id": "u1",
                "owner_id": "p1",
                "definition_id": "founder",
                "q": 0,
                "r": 0,
                "hit_points": 100,
                "movement_remaining": 2,
            }
        ],
        "settlements": [],
        "victory": None,
    }
    rendered_map = render_map(state)
    rendered_state = render_state(state)
    assert "U" in rendered_map
    assert "u1:founder@(0,0)" in rendered_state
    assert "Game g | turn 1" in rendered_state
    assert "civ=river_compact" in rendered_state
