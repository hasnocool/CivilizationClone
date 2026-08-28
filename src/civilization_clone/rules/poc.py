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
            "research_preferences": ["surveying", "writing", "archery"],
            "content_hooks": ["waystation", "field_archive"],
        }
    ),
)

POC_CIVILIZATIONS_BY_ID = {
    definition.civilization_id: definition for definition in POC_CIVILIZATIONS
}
