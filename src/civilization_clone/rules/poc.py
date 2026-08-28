"""Packaged original proof-of-concept content definitions."""

from civilization_clone.domain.ids import CivilizationId
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
            "unique_units": ["river_warden"],
            "unique_buildings": ["canal_depot"],
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
            "unique_units": ["trailblazer"],
            "unique_buildings": ["field_archive"],
            "research_preferences": ["surveying", "writing", "archery"],
            "content_hooks": ["waystation", "field_archive"],
        }
    ),
)

POC_CIVILIZATIONS_BY_ID = {
    definition.civilization_id: definition for definition in POC_CIVILIZATIONS
}


def _unique_content_owners(attribute: str) -> dict[str, CivilizationId]:
    owners: dict[str, CivilizationId] = {}
    for definition in POC_CIVILIZATIONS:
        content_ids = getattr(definition, attribute)
        for content_id in content_ids:
            if content_id in owners:
                raise ValueError(f"duplicate unique content id: {content_id}")
            owners[content_id] = definition.civilization_id
    return owners


POC_UNIQUE_UNIT_OWNERS = _unique_content_owners("unique_units")
POC_UNIQUE_BUILDING_OWNERS = _unique_content_owners("unique_buildings")
