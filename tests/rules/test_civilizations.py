# tests/rules/test_civilizations.py
from pathlib import Path

import pytest

from civilization_clone.domain.economy import ModifierOperation, YieldType
from civilization_clone.rules.civilizations import (
    CivilizationDefinition,
    load_civilizations,
)
from civilization_clone.rules.poc import POC_CIVILIZATIONS, POC_CIVILIZATIONS_BY_ID


def test_poc_content_contains_two_unique_original_civilizations() -> None:
    path = Path(__file__).parents[2] / "content" / "poc" / "civilizations.json"
    definitions = load_civilizations(path)

    assert len(definitions) == 2
    assert {str(item.civilization_id) for item in definitions} == {
        "river_compact",
        "horizon_league",
    }
    assert definitions == POC_CIVILIZATIONS
    assert all(item.research_preferences for item in definitions)
    assert all(item.content_hooks for item in definitions)

    river = POC_CIVILIZATIONS_BY_ID[definitions[0].civilization_id]
    horizon = POC_CIVILIZATIONS_BY_ID[definitions[1].civilization_id]
    assert river.starting_resources == {"gold": 4, "culture": 1}
    assert river.yield_modifiers[0].yield_type is YieldType.FOOD
    assert river.yield_modifiers[0].operation is ModifierOperation.FLAT
    assert river.yield_modifiers[0].value == 1
    assert horizon.starting_resources == {"gold": 2, "science": 2}
    assert horizon.research_cost_percent == -15


def test_civilization_schema_rejects_invalid_content() -> None:
    with pytest.raises(ValueError, match="unknown civilization fields"):
        CivilizationDefinition.from_mapping({"id": "x", "name": "X", "unexpected": True})

    with pytest.raises(ValueError, match="values must be unique"):
        CivilizationDefinition.from_mapping(
            {"id": "x", "name": "X", "tags": ["trade", "trade"]}
        )

    with pytest.raises(ValueError, match="unknown civilization starting resources"):
        CivilizationDefinition.from_mapping(
            {"id": "x", "name": "X", "starting_resources": {"unknown": 1}}
        )

    with pytest.raises(ValueError, match="between -90 and 200"):
        CivilizationDefinition.from_mapping(
            {"id": "x", "name": "X", "research_cost_percent": -100}
        )

    with pytest.raises(ValueError, match="unsupported enum value"):
        CivilizationDefinition.from_mapping(
            {
                "id": "x",
                "name": "X",
                "yield_modifiers": [
                    {"yield_type": "invalid", "operation": "flat", "value": 1}
                ],
            }
        )
