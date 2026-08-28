"""Minimal common game state used by the deterministic v0.1 core."""

from dataclasses import dataclass
from enum import StrEnum

from civilization_clone.domain.ids import GameId, RulesetId


class GameStatus(StrEnum):
    """Lifecycle status shared by future game aggregates."""

    SETUP = "setup"
    ACTIVE = "active"
    FINISHED = "finished"


class GamePhase(StrEnum):
    """High-level engine phase; later milestones may extend this enum."""

    SETUP = "setup"
    PLAYER_TURN = "player_turn"
    GLOBAL_RESOLUTION = "global_resolution"


@dataclass(frozen=True, slots=True)
class RulesetRef:
    """Stable ruleset identity embedded in authoritative state."""

    ruleset_id: RulesetId
    version: str


@dataclass(frozen=True, slots=True)
class CoreGameState:
    """Smallest authoritative state shared by all future game aggregates."""

    game_id: GameId
    ruleset: RulesetRef
    seed: int
    state_version: int = 0
    turn: int = 0
    phase: GamePhase = GamePhase.SETUP
    status: GameStatus = GameStatus.SETUP

    def __post_init__(self) -> None:
        if self.state_version < 0:
            raise ValueError("state_version must be non-negative")
        if self.turn < 0:
            raise ValueError("turn must be non-negative")
