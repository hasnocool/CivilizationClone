"""CivilizationClone deterministic 4X engine core."""

from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile, WorldMap
from civilization_clone.domain.state import CoreGameState, GamePhase, GameStatus
from civilization_clone.engine.event_log import EventLog, EventLogError
from civilization_clone.engine.mapgen import MapGenerationConfig, MapGenerationResult, generate_world
from civilization_clone.engine.rng import DeterministicRng, RngFactory
from civilization_clone.engine.state_hash import canonical_json, state_hash
from civilization_clone.rules.loader import RulesetLoader
from civilization_clone.rules.schemas import RulesetManifest

__all__ = [
    "CoreGameState",
    "DeterministicRng",
    "EventLog",
    "EventLogError",
    "GamePhase",
    "GameStatus",
    "HexCoord",
    "MapGenerationConfig",
    "MapGenerationResult",
    "ResourceType",
    "RngFactory",
    "RulesetLoader",
    "RulesetManifest",
    "TerrainType",
    "Tile",
    "WorldMap",
    "canonical_json",
    "generate_world",
    "state_hash",
]

__version__ = "0.2.0"
