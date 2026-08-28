"""CivilizationClone deterministic 4X engine core."""

from civilization_clone.domain.gameplay import (
    ControllerType,
    GameSession,
    PlayerState,
    UnitDefinition,
    UnitState,
)
from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile, WorldMap
from civilization_clone.domain.state import CoreGameState, GamePhase, GameStatus
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.event_log import EventLog, EventLogError
from civilization_clone.engine.mapgen import MapGenerationConfig, MapGenerationResult, generate_world
from civilization_clone.engine.rng import DeterministicRng, RngFactory
from civilization_clone.engine.session import CommandResult, GameEngine
from civilization_clone.engine.state_hash import canonical_json, state_hash
from civilization_clone.rules.loader import RulesetLoader
from civilization_clone.rules.schemas import RulesetManifest

__all__ = [
    "CommandResult",
    "ControllerType",
    "CoreGameState",
    "DeterministicRng",
    "EventLog",
    "EventLogError",
    "GameEngine",
    "GamePhase",
    "GameSession",
    "GameStatus",
    "HexCoord",
    "MapGenerationConfig",
    "MapGenerationResult",
    "PlayerState",
    "ResourceType",
    "RngFactory",
    "RulesetLoader",
    "RulesetManifest",
    "TerrainType",
    "Tile",
    "UnitDefinition",
    "UnitState",
    "Visibility",
    "WorldMap",
    "canonical_json",
    "generate_world",
    "state_hash",
]

__version__ = "0.3.0"
