"""Research, diplomacy, elimination, and victory domain primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from civilization_clone.domain.ids import PlayerId


@dataclass(frozen=True, slots=True)
class TechnologyDefinition:
    """One node in the generic prerequisite research DAG."""

    technology_id: str
    cost: int
    prerequisites: frozenset[str] = frozenset()
    unlocks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.technology_id.strip():
            raise ValueError("technology id must not be blank")
        if self.cost <= 0:
            raise ValueError("technology cost must be positive")
        if self.technology_id in self.prerequisites:
            raise ValueError("technology cannot require itself")


@dataclass(slots=True)
class ResearchState:
    """Mutable per-player research selection and deterministic progress."""

    selected: str | None = None
    progress: int = 0
    completed: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.progress < 0:
            raise ValueError("research progress must be non-negative")


class DiplomacyStatus(StrEnum):
    """POC bilateral diplomatic relationship state."""

    UNKNOWN = "unknown"
    CONTACTED = "contacted"
    PEACE = "peace"
    WAR = "war"


@dataclass(slots=True)
class DiplomaticRelationship:
    """Canonical relationship for one unordered pair of players."""

    status: DiplomacyStatus = DiplomacyStatus.UNKNOWN
    pending_peace_from: PlayerId | None = None


class VictoryType(StrEnum):
    """POC victory conditions."""

    CONQUEST = "conquest"
    SCORE = "score"


@dataclass(frozen=True, slots=True)
class VictoryResult:
    """Final deterministic match outcome."""

    winner_id: PlayerId
    victory_type: VictoryType
    turn: int
    score: int
