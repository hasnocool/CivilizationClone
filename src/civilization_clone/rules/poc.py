"""Packaged original proof-of-concept content definitions."""

from civilization_clone.rules.civilizations import CivilizationDefinition

POC_CIVILIZATIONS: tuple[CivilizationDefinition, ...] = (
    CivilizationDefinition.from_mapping(
        {
            "id": "river_compact",
            "name": "River Compact",
            "description": (
                "A network of river-valley settlements that prizes surveying, storage, "
                "public works, and reliable internal trade."
            ),
            "tags": ["rivers", "infrastructure", "growth"],
            "starting_resources": {"gold": 4, "culture": 1},
            "yield_modifiers": [
                {"yield_type": "food", "operation": "flat", "value": 1, "priority": 50}
            ],
            "research_cost_percent": 0,
            "attack_strength_percent": 0,
            "defense_strength_percent": 10,
            "unique_units": [],
            "unique_buildings": [],
            "research_preferences": ["surveying", "masonry", "engineering"],
            "content_hooks": ["canal_infrastructure", "river_market"],
        }
    ),
    CivilizationDefinition.from_mapping(
        {
            "id": "horizon_league",
            "name": "Horizon League",
            "description": (
                "A loose league of frontier cities focused on exploration, archives, "
                "ranged defense, and long-distance coordination."
            ),
            "tags": ["exploration", "knowledge", "mobility"],
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
            "unique_units": [],
            "unique_buildings": [],
            "research_preferences": ["surveying", "writing", "archery"],
            "content_hooks": ["waystation", "field_archive"],
        }
    ),
)

POC_CIVILIZATIONS_BY_ID = {
    definition.civilization_id: definition for definition in POC_CIVILIZATIONS
}
