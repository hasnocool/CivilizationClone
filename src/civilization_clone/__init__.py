"""CivilizationClone deterministic 4X engine core."""

from civilization_clone.application.manager import GameManager
from civilization_clone.domain.economy import (
    ProductionKind,
    ProductionOrder,
    SettlementState,
    YieldBundle,
    YieldModifier,
    YieldType,
)
from civilization_clone.domain.gameplay import (
    ControllerType,
    GameSession,
    PlayerState,
    UnitDefinition,
    UnitState,
)
from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile, WorldMap
from civilization_clone.domain.state import CoreGameState, GamePhase, GameStatus
from civilization_clone.domain.strategy import (
    DiplomaticRelationship,
    DiplomacyStatus,
    ResearchState,
    TechnologyDefinition,
    TradeOffer,
    VictoryResult,
    VictoryType,
)
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.advanced import AdvancedGameEngine
from civilization_clone.engine.event_log import EventLog, EventLogError
from civilization_clone.engine.mapgen import MapGenerationConfig, MapGenerationResult, generate_world
from civilization_clone.engine.rng import DeterministicRng, RngFactory
from civilization_clone.engine.session import CommandResult, GameEngine
from civilization_clone.engine.state_hash import canonical_json, state_hash
from civilization_clone.persistence.replay import ReplayReport, ReplayVerificationError, verify_replay
from civilization_clone.persistence.sqlite_store import ReplayDivergenceError, SqliteGameStore
from civilization_clone.rules.loader import RulesetLoader
from civilization_clone.rules.schemas import RulesetManifest

__all__ = [
    "AdvancedGameEngine",
    "CommandResult",
    "ControllerType",
    "CoreGameState",
    "DeterministicRng",
    "DiplomaticRelationship",
    "DiplomacyStatus",
    "EventLog",
    "EventLogError",
    "GameEngine",
    "GameManager",
    "GamePhase",
    "GameSession",
    "GameStatus",
    "HexCoord",
    "MapGenerationConfig",
    "MapGenerationResult",
    "PlayerState",
    "ProductionKind",
    "ProductionOrder",
    "ReplayDivergenceError",
    "ReplayReport",
    "ReplayVerificationError",
    "ResearchState",
    "ResourceType",
    "RngFactory",
    "RulesetLoader",
    "RulesetManifest",
    "SettlementState",
    "SqliteGameStore",
    "TechnologyDefinition",
    "TerrainType",
    "Tile",
    "TradeOffer",
    "UnitDefinition",
    "UnitState",
    "VictoryResult",
    "VictoryType",
    "Visibility",
    "WorldMap",
    "YieldBundle",
    "YieldModifier",
    "YieldType",
    "canonical_json",
    "generate_world",
    "state_hash",
    "verify_replay",
]

__version__ = "1.1.0"
