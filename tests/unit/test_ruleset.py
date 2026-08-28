# tests/unit/test_ruleset.py
import json
from pathlib import Path

import pytest

from civilization_clone.rules.loader import RulesetLoadError, RulesetLoader


@pytest.fixture
def loader() -> RulesetLoader:
    return RulesetLoader()


def test_loads_poc_ruleset(loader: RulesetLoader) -> None:
    manifest = loader.load(Path("content/poc/ruleset.json"))

    assert manifest.ruleset_id == "poc-core"
    assert manifest.version == "0.1.0"
    assert manifest.schema_version == 1
    assert manifest.metadata["content_origin"] == "original"


def test_rejects_unknown_fields(tmp_path: Path, loader: RulesetLoader) -> None:
    path = tmp_path / "ruleset.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "test",
                "version": "0.1.0",
                "name": "Test",
                "unexpected": True,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RulesetLoadError, match="unknown ruleset manifest fields"):
        loader.load(path)


def test_rejects_invalid_semver(tmp_path: Path, loader: RulesetLoader) -> None:
    path = tmp_path / "ruleset.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "test",
                "version": "v1",
                "name": "Test",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RulesetLoadError, match="semantic version"):
        loader.load(path)


def test_rejects_invalid_json(tmp_path: Path, loader: RulesetLoader) -> None:
    path = tmp_path / "ruleset.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(RulesetLoadError, match="invalid JSON"):
        loader.load(path)
