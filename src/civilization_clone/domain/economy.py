"""Settlement economy, yield, production, and modifier domain primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from civilization_clone.domain.ids import PlayerId, SettlementId
from civilization_clone.domain.map import HexCoord


class YieldType(StrEnum):
    FOOD = "food"
    PRODUCTION = "production"
    GOLD = "gold"
    SCIENCE = "science"
    CULTURE = "culture"


@dataclass(frozen=True, slots=True)
class YieldBundle:
    """Fixed POC yield vector with deterministic integer arithmetic."""

    food: int = 0
    production: int = 0
    gold: int = 0
    science: int = 0
    culture: int = 0

    def __post_init__(self) -> None:
        if min(self.food, self.production, self.gold, self.science, self.culture) < 0:
            raise ValueError("yields must be non-negative")

    def value(self, yield_type: YieldType) -> int:
        return int(getattr(self, yield_type.value))

    def with_value(self, yield_type: YieldType, value: int) -> "YieldBundle":
        values = self.as_dict()
        values[yield_type.value] = value
        return YieldBundle(**values)

    def add(self, other: "YieldBundle") -> "YieldBundle":
        return YieldBundle(
            food=self.food + other.food,
            production=self.production + other.production,
            gold=self.gold + other.gold,
            science=self.science + other.science,
            culture=self.culture + other.culture,
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "food": self.food,
            "production": self.production,
            "gold": self.gold,
            "science": self.science,
            "culture": self.culture,
        }


class ModifierOperation(StrEnum):
    FLAT = "flat"
    PERCENT = "percent"


@dataclass(frozen=True, slots=True)
class YieldModifier:
    source: str
    yield_type: YieldType
    operation: ModifierOperation
    value: int
    priority: int = 100

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("modifier source must not be blank")
        if self.operation is ModifierOperation.PERCENT and self.value < -100:
            raise ValueError("percentage modifier cannot reduce below -100 percent")


class ProductionKind(StrEnum):
    BUILDING = "building"
    UNIT = "unit"


@dataclass(frozen=True, slots=True)
class ProductionOrder:
    kind: ProductionKind
    definition_id: str
    cost: int

    def __post_init__(self) -> None:
        if not self.definition_id.strip():
            raise ValueError("production definition id must not be blank")
        if self.cost <= 0:
            raise ValueError("production cost must be positive")


@dataclass(frozen=True, slots=True)
class BuildingDefinition:
    definition_id: str
    cost: int
    modifiers: tuple[YieldModifier, ...] = ()

    def __post_init__(self) -> None:
        if not self.definition_id.strip():
            raise ValueError("building definition id must not be blank")
        if self.cost <= 0:
            raise ValueError("building cost must be positive")


@dataclass(slots=True)
class SettlementState:
    settlement_id: SettlementId
    owner_id: PlayerId
    center: HexCoord
    population: int = 1
    food_storage: int = 0
    production_storage: int = 0
    territory: set[HexCoord] = field(default_factory=set)
    worked_tiles: set[HexCoord] = field(default_factory=set)
    buildings: set[str] = field(default_factory=set)
    production_queue: list[ProductionOrder] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.population <= 0:
            raise ValueError("settlement population must be positive")
