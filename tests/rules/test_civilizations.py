# tests/rules/test_civilizations.py
from pathlib import Path

import pytest

from civilization_clone.rules.civilizations import (
    CivilizationDefinition,
    load_civilizations,
)
from civilization_clone.rules.poc import POC_CIVILIZATIONS


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


def test_civilization_schema_rejects_unknown_fields_and_duplicate_tags() -> None:
    with pytest.raises(ValueError, match="unknown civilization fields"):
        CivilizationDefinition.from_mapping({"id": "x", "name": "X", "unexpected": True})

    with pytest.raises(ValueError, match="values must be unique"):
        CivilizationDefinition.from_mapping(
            {"id": "x", "name": "X", "tags": ["trade", "trade"]}
        )
