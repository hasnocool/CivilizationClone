# tests/integration/test_process_determinism.py
import os
import subprocess
import sys

_PROBE = r'''
from pathlib import Path
from civilization_clone.domain.ids import GameId
from civilization_clone.domain.state import CoreGameState, RulesetRef
from civilization_clone.engine.rng import RngFactory
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.rules.loader import RulesetLoader

manifest = RulesetLoader().load(Path("content/poc/ruleset.json"))
rng = RngFactory(424242).stream("cross-process")
state = CoreGameState(
    game_id=GameId("sample-game"),
    ruleset=RulesetRef(manifest.ruleset_id, manifest.version),
    seed=424242,
)
print(state_hash({
    "state": state,
    "ruleset": manifest,
    "unordered": {"delta", "alpha", "charlie", "bravo"},
    "probe": [rng.next_u64() for _ in range(32)],
}))
'''


def _run_probe(hash_seed: str) -> str:
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = hash_seed
    completed = subprocess.run(
        [sys.executable, "-c", _PROBE],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    return completed.stdout.strip()


def test_hash_is_stable_across_python_hash_seeds() -> None:
    assert _run_probe("1") == _run_probe("8675309")
