"""Authoritative player, unit, settlement, and game-session models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from civilization_clone.domain.economy import SettlementState
from civilization_clone.domain.ids import GameId, PlayerId, SettlementId, UnitId
from civilization_clone.domain.map import HexCoord, WorldMap
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.visibility import Visibility


class ControllerType(StrEnum):
    """Controller category for one player."""

    HUMAN = "human"
    BOT = "bot"


@dataclass(slots=True)
class PlayerState:
    """Authoritative mutable state for one player."""

    player_id: PlayerId
    name: str
    controller: ControllerType = ControllerType.HUMAN
    visibility: dict[HexCoord, Visibility] = field(default_factory=dict)
    gold: int = 0
    science: int = 0
    culture: int = 0


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    """Small data-driven unit definition shared by movement and production."""

    definition_id: str
    movement: int = 2
    vision_radius: int = 1
    production_cost: int = 0
    can_found: bool = False

    def __post_init__(self) -> None:
        if not self.definition_id.strip():
            raise ValueError("unit definition id must not be blank")
        if self.movement <= 0:
            raise ValueError("unit movement must be positive")
        if self.vision_radius < 0:
            raise ValueError("unit vision radius must be non-negative")
        if self.production_cost < 0:
            raise ValueError("unit production cost must be non-negative")


@dataclass(slots=True)
class UnitState:
    """Authoritative mutable state for one unit."""

    unit_id: UnitId
    owner_id: PlayerId
    definition: UnitDefinition
    position: HexCoord
    movement_remaining: int
    hit_points: int = 100

    @classmethod
    def spawn(
        cls,
        *,
        unit_id: UnitId,
        owner_id: PlayerId,
        definition: UnitDefinition,
        position: HexCoord,
    ) -> "UnitState":
        return cls(
            unit_id=unit_id,
            owner_id=owner_id,
            definition=definition,
            position=position,
            movement_remaining=definition.movement,
        )


@dataclass(slots=True)
class GameSession:
    """In-memory authoritative aggregate for the current engine milestones."""

    game_id: GameId
    ruleset: RulesetRef
    seed: int
    world: WorldMap
    players: dict[PlayerId, PlayerState] = field(default_factory=dict)
    player_order: list[PlayerId] = field(default_factory=list)
    units: dict[UnitId, UnitState] = field(default_factory=dict)
    settlements: dict[SettlementId, SettlementState] = field(default_factory=dict)
    next_unit_index: int = 0
    next_settlement_index: int = 0
    turn: int = 0
    active_player_index: int = 0
    state_version: int = 0
    status: GameStatus = GameStatus.SETUP
    phase: GamePhase = GamePhase.SETUP

    @property
    def current_player_id(self) -> PlayerId | None:
        if self.status is not GameStatus.ACTIVE or not self.player_order:
            return None
        return self.player_order[self.active_player_index]

    @property
    def max_players(self) -> int:
        return len(self.world.spawns)

    def canonical_state(self) -> dict[str, object]:
        """Return a deterministic JSON-key-safe representation for hashing/replay."""
        players = []
        for player_id in sorted(self.players):
            player = self.players[player_id]
            players.append(
                {
                    "player_id": player_id,
                    "name": player.name,
                    "controller": player.controller.value,
                    "gold": player.gold,
                    "science": player.science,
                    "culture": player.culture,
                    "visibility": [
                        {"q": coord.q, "r": coord.r, "state": visibility.value}
                        for coord, visibility in sorted(player.visibility.items())
                    ],
                }
            )

        units = [
            {
                "unit_id": unit.unit_id,
                "owner_id": unit.owner_id,
                "definition_id": unit.definition.definition_id,
                "position": {"q": unit.position.q, "r": unit.position.r},
                "movement_remaining": unit.movement_remaining,
                "hit_points": unit.hit_points,
            }
            for _, unit in sorted(self.units.items())
        ]

        settlements = [
            {
                "settlement_id": settlement.settlement_id,
                "owner_id": settlement.owner_id,
                "center": {"q": settlement.center.q, "r": settlement.center.r},
                "population": settlement.population,
                "food_storage": settlement.food_storage,
                "production_storage": settlement.production_storage,
                "territory": [
                    {"q": coord.q, "r": coord.r} for coord in sorted(settlement.territory)
                ],
                "worked_tiles": [
                    {"q": coord.q, "r": coord.r} for coord in sorted(settlement.worked_tiles)
                ],
                "buildings": sorted(settlement.buildings),
                "production_queue": [
                    {
                        "kind": order.kind.value,
                        "definition_id": order.definition_id,
                        "cost": order.cost,
                    }
                    for order in settlement.production_queue
                ],
            }
            for _, settlement in sorted(self.settlements.items())
        ]

        return {
            "game_id": self.game_id,
            "ruleset": {"id": self.ruleset.ruleset_id, "version": self.ruleset.version},
            "seed": self.seed,
            "world": self.world.canonical_state(),
            "players": players,
            "player_order": list(self.player_order),
            "units": units,
            "settlements": settlements,
            "next_unit_index": self.next_unit_index,
            "next_settlement_index": self.next_settlement_index,
            "turn": self.turn,
            "active_player_index": self.active_player_index,
            "state_version": self.state_version,
            "status": self.status.value,
            "phase": self.phase.value,
        }
