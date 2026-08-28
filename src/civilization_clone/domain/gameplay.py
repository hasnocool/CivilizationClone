"""Authoritative player, unit, settlement, diplomacy, research, and game-session models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from civilization_clone.domain.diplomacy import DiplomacyStatus
from civilization_clone.domain.economy import SettlementState
from civilization_clone.domain.ids import GameId, PlayerId, SettlementId, UnitId
from civilization_clone.domain.map import HexCoord, WorldMap
from civilization_clone.domain.state import GamePhase, GameStatus, RulesetRef
from civilization_clone.domain.victory import VictoryKind
from civilization_clone.domain.visibility import Visibility


class ControllerType(StrEnum):
    HUMAN = "human"
    BOT = "bot"


@dataclass(slots=True)
class PlayerState:
    player_id: PlayerId
    name: str
    controller: ControllerType = ControllerType.HUMAN
    visibility: dict[HexCoord, Visibility] = field(default_factory=dict)
    gold: int = 0
    science: int = 0
    culture: int = 0
    current_research: str | None = None
    research_progress: dict[str, int] = field(default_factory=dict)
    completed_technologies: set[str] = field(default_factory=set)
    eliminated: bool = False


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    definition_id: str
    movement: int = 2
    vision_radius: int = 1
    production_cost: int = 0
    can_found: bool = False
    combat_strength: int = 10

    def __post_init__(self) -> None:
        if not self.definition_id.strip():
            raise ValueError("unit definition id must not be blank")
        if self.movement <= 0:
            raise ValueError("unit movement must be positive")
        if self.vision_radius < 0:
            raise ValueError("unit vision radius must be non-negative")
        if self.production_cost < 0:
            raise ValueError("unit production cost must be non-negative")
        if self.combat_strength <= 0:
            raise ValueError("combat strength must be positive")


@dataclass(slots=True)
class UnitState:
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
        return cls(unit_id, owner_id, definition, position, definition.movement)


@dataclass(slots=True)
class GameSession:
    game_id: GameId
    ruleset: RulesetRef
    seed: int
    world: WorldMap
    players: dict[PlayerId, PlayerState] = field(default_factory=dict)
    player_order: list[PlayerId] = field(default_factory=list)
    units: dict[UnitId, UnitState] = field(default_factory=dict)
    settlements: dict[SettlementId, SettlementState] = field(default_factory=dict)
    diplomacy: dict[tuple[PlayerId, PlayerId], DiplomacyStatus] = field(default_factory=dict)
    peace_offers: set[tuple[PlayerId, PlayerId]] = field(default_factory=set)
    next_unit_index: int = 0
    next_settlement_index: int = 0
    turn: int = 0
    active_player_index: int = 0
    state_version: int = 0
    status: GameStatus = GameStatus.SETUP
    phase: GamePhase = GamePhase.SETUP
    max_turns: int = 50
    winner_id: PlayerId | None = None
    victory_kind: VictoryKind | None = None

    @property
    def current_player_id(self) -> PlayerId | None:
        if self.status is not GameStatus.ACTIVE or not self.player_order:
            return None
        return self.player_order[self.active_player_index]

    @property
    def max_players(self) -> int:
        return len(self.world.spawns)

    def canonical_state(self) -> dict[str, object]:
        players = []
        for player_id in sorted(self.players):
            player = self.players[player_id]
            players.append({
                "player_id": player_id,
                "name": player.name,
                "controller": player.controller.value,
                "gold": player.gold,
                "science": player.science,
                "culture": player.culture,
                "current_research": player.current_research,
                "research_progress": [
                    {"technology_id": tech, "progress": progress}
                    for tech, progress in sorted(player.research_progress.items())
                ],
                "completed_technologies": sorted(player.completed_technologies),
                "eliminated": player.eliminated,
                "visibility": [
                    {"q": coord.q, "r": coord.r, "state": visibility.value}
                    for coord, visibility in sorted(player.visibility.items())
                ],
            })
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
                "settlement_id": item.settlement_id,
                "owner_id": item.owner_id,
                "center": {"q": item.center.q, "r": item.center.r},
                "population": item.population,
                "food_storage": item.food_storage,
                "production_storage": item.production_storage,
                "territory": [{"q": c.q, "r": c.r} for c in sorted(item.territory)],
                "worked_tiles": [{"q": c.q, "r": c.r} for c in sorted(item.worked_tiles)],
                "buildings": sorted(item.buildings),
                "production_queue": [
                    {"kind": order.kind.value, "definition_id": order.definition_id, "cost": order.cost}
                    for order in item.production_queue
                ],
            }
            for _, item in sorted(self.settlements.items())
        ]
        diplomacy = [
            {"left": key[0], "right": key[1], "status": status.value}
            for key, status in sorted(self.diplomacy.items())
        ]
        peace_offers = [{"from": offer[0], "to": offer[1]} for offer in sorted(self.peace_offers)]
        return {
            "game_id": self.game_id,
            "ruleset": {"id": self.ruleset.ruleset_id, "version": self.ruleset.version},
            "seed": self.seed,
            "world": self.world.canonical_state(),
            "players": players,
            "player_order": list(self.player_order),
            "units": units,
            "settlements": settlements,
            "diplomacy": diplomacy,
            "peace_offers": peace_offers,
            "next_unit_index": self.next_unit_index,
            "next_settlement_index": self.next_settlement_index,
            "turn": self.turn,
            "active_player_index": self.active_player_index,
            "state_version": self.state_version,
            "status": self.status.value,
            "phase": self.phase.value,
            "max_turns": self.max_turns,
            "winner_id": self.winner_id,
            "victory_kind": self.victory_kind.value if self.victory_kind is not None else None,
        }
