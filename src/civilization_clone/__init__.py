"""CivilizationClone deterministic 4X engine core."""

from civilization_clone.domain.state import CoreGameState, GamePhase, GameStatus
from civilization_clone.engine.rng import DeterministicRng, RngFactory
from civilization_clone.engine.state_hash import canonical_json, state_hash
from civilization_clone.rules.loader import RulesetLoader
from civilization_clone.rules.schemas import RulesetManifest

__all__ = [
    "CoreGameState",
    "DeterministicRng",
    "GamePhase",
    "GameStatus",
    "RngFactory",
    "RulesetLoader",
    "RulesetManifest",
    "canonical_json",
    "state_hash",
]

__version__ = "0.1.0"
