# tests/rules/test_poc_content_limits.py
from pathlib import Path

from civilization_clone.domain.map import ResourceType, TerrainType
from civilization_clone.engine.economy import BUILDINGS, UNITS
from civilization_clone.engine.research import TECHNOLOGIES
from civilization_clone.rules.civilizations import load_civilizations


def test_poc_content_counts_remain_within_plan_limits() -> None:
    civilizations_path = Path(__file__).parents[2] / "content" / "poc" / "civilizations.json"
    civilizations = load_civilizations(civilizations_path)

    assert 5 <= len(TerrainType) <= 7
    assert 3 <= len(ResourceType) <= 5
    assert len(civilizations) == 2
    assert 4 <= len(UNITS) + 1 <= 6  # production units plus the founder class
    assert 4 <= len(BUILDINGS) <= 8
    assert 8 <= len(TECHNOLOGIES) <= 12
