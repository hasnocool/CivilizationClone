# tests/integration/test_deterministic_core.py
from pathlib import Path

from civilization_clone.domain.ids import GameId
from civilization_clone.domain.state import CoreGameState, RulesetRef
from civilization_clone.engine.rng import RngFactory
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.rules.loader import RulesetLoader


def build_sample_result(seed: int) -> str:
    manifest = RulesetLoader().load(Path("content/poc/ruleset.json"))
    rng = RngFactory(seed).stream("v0.1-sample")
    state = CoreGameState(
        game_id=GameId("sample-game"),
        ruleset=RulesetRef(manifest.ruleset_id, manifest.version),
        seed=seed,
    )
    sample = {
        "state": state,
        "ruleset": manifest,
        "random_probe": [rng.next_u64() for _ in range(16)],
    }
    return state_hash(sample)


def test_same_seed_produces_same_deterministic_result() -> None:
    assert build_sample_result(123456789) == build_sample_result(123456789)


def test_different_seed_changes_sample_result() -> None:
    assert build_sample_result(123456789) != build_sample_result(987654321)
