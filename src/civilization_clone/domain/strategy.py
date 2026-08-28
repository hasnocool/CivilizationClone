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
    """Bilateral diplomatic relationship state."""

    UNKNOWN = "unknown"
    CONTACTED = "contacted"
    PEACE = "peace"
    WAR = "war"


@dataclass(frozen=True, slots=True)
class TradeOffer:
    """One pending bilateral lump-sum gold exchange proposal.

    Terms are always expressed from the proposer's perspective: ``offered_gold``
    moves from proposer to recipient and ``requested_gold`` moves the other way if
    the recipient accepts. Keeping the proposal immutable makes persistence and
    deterministic event payloads straightforward.
    """

    proposer_id: PlayerId
    offered_gold: int
    requested_gold: int

    def __post_init__(self) -> None:
        if self.offered_gold < 0 or self.requested_gold < 0:
            raise ValueError("trade gold amounts must be non-negative")
        if self.offered_gold == 0 and self.requested_gold == 0:
            raise ValueError("trade offer must exchange at least some gold")


@dataclass(slots=True)
class DiplomaticRelationship:
    """Canonical relationship for one unordered pair of players."""

    status: DiplomacyStatus = DiplomacyStatus.UNKNOWN
    pending_peace_from: PlayerId | None = None
    pending_trade: TradeOffer | None = None
    completed_trades: int = 0
    last_trade_turn: int | None = None

    def __post_init__(self) -> None:
        if self.completed_trades < 0:
            raise ValueError("completed trade count must be non-negative")
        if self.last_trade_turn is not None and self.last_trade_turn < 0:
            raise ValueError("last trade turn must be non-negative")


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
