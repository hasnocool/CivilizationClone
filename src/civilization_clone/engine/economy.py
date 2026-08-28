"""Deterministic settlement yields, growth, production, and spawning."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.domain.economy import (
    BuildingDefinition,
    ModifierOperation,
    ProductionKind,
    ProductionOrder,
    SettlementState,
    YieldBundle,
    YieldModifier,
    YieldType,
)
from civilization_clone.domain.gameplay import GameSession, UnitDefinition, UnitState
from civilization_clone.domain.ids import PlayerId, UnitId
from civilization_clone.domain.map import HexCoord, ResourceType, TerrainType, Tile
from civilization_clone.domain.types import JsonValue
from civilization_clone.engine.effects import apply_yield_modifiers
from civilization_clone.engine.hexgrid import neighbors
from civilization_clone.engine.research import production_is_unlocked
from civilization_clone.rules.poc import POC_CIVILIZATIONS_BY_ID

BUILDINGS: dict[str, BuildingDefinition] = {
    "granary": BuildingDefinition(
        "granary",
        cost=6,
        modifiers=(
            YieldModifier("building:granary", YieldType.FOOD, ModifierOperation.FLAT, 1),
        ),
    ),
    "workshop": BuildingDefinition(
        "workshop",
        cost=8,
        modifiers=(
            YieldModifier(
                "building:workshop",
                YieldType.PRODUCTION,
                ModifierOperation.FLAT,
                1,
            ),
        ),
    ),
    "market": BuildingDefinition(
        "market",
        cost=9,
        modifiers=(
            YieldModifier("building:market", YieldType.GOLD, ModifierOperation.FLAT, 1),
        ),
    ),
    "archive": BuildingDefinition(
        "archive",
        cost=10,
        modifiers=(
            YieldModifier("building:archive", YieldType.SCIENCE, ModifierOperation.FLAT, 1),
        ),
    ),
}

UNITS: dict[str, UnitDefinition] = {
    "scout": UnitDefinition(
        "scout",
        movement=3,
        vision_radius=2,
        production_cost=8,
        attack_strength=3,
        defense_strength=3,
    ),
    "warrior": UnitDefinition(
        "warrior",
        movement=2,
        vision_radius=1,
        production_cost=10,
        attack_strength=7,
        defense_strength=6,
    ),
    "archer": UnitDefinition(
        "archer",
        movement=2,
        vision_radius=1,
        production_cost=12,
        attack_strength=6,
        defense_strength=3,
        ranged_range=2,
    ),
}


@dataclass(frozen=True, slots=True)
class EconomyOutcome:
    """One deterministic domain event description produced by economy resolution."""

    event_type: str
    payload: dict[str, JsonValue]


def tile_yield(tile: Tile) -> YieldBundle:
    """Return original POC base yields for one tile."""
    base = {
        TerrainType.WATER: YieldBundle(food=1),
        TerrainType.PLAINS: YieldBundle(food=1, production=1),
        TerrainType.GRASSLAND: YieldBundle(food=2, production=1),
        TerrainType.HILLS: YieldBundle(food=1, production=2),
        TerrainType.DESERT: YieldBundle(food=1, production=1, gold=1),
        TerrainType.TUNDRA: YieldBundle(food=1, production=1),
    }[tile.terrain]
    resource_bonus = {
        ResourceType.FOOD: YieldBundle(food=1),
        ResourceType.MINERAL: YieldBundle(production=1),
        ResourceType.GOLD: YieldBundle(gold=1),
        None: YieldBundle(),
    }[tile.resource]
    return base.add(resource_bonus)


def settlement_yield(session: GameSession, settlement: SettlementState) -> YieldBundle:
    """Calculate yields from tiles and generic civilization/building modifiers."""
    total = tile_yield(session.world.tile(settlement.center)).add(
        YieldBundle(science=1, culture=1)
    )
    for coord in sorted(settlement.worked_tiles):
        total = total.add(tile_yield(session.world.tile(coord)))

    modifiers: list[YieldModifier] = []
    owner = session.players[settlement.owner_id]
    civilization = POC_CIVILIZATIONS_BY_ID.get(owner.civilization_id)
    if civilization is not None:
        modifiers.extend(civilization.yield_modifiers)
    for building_id in sorted(settlement.buildings):
        definition = BUILDINGS.get(building_id)
        if definition is not None:
            modifiers.extend(definition.modifiers)
    return apply_yield_modifiers(total, modifiers)


def growth_threshold(population: int) -> int:
    return 6 + population * 2


def production_order(kind: str, definition_id: str) -> ProductionOrder | None:
    """Build a validated production order from the POC definition registries."""
    try:
        production_kind = ProductionKind(kind)
    except ValueError:
        return None
    if production_kind is ProductionKind.BUILDING:
        definition = BUILDINGS.get(definition_id)
        if definition is None:
            return None
        return ProductionOrder(production_kind, definition_id, definition.cost)
    definition = UNITS.get(definition_id)
    if definition is None:
        return None
    return ProductionOrder(production_kind, definition_id, definition.production_cost)


def resolve_player_economy(
    session: GameSession,
    player_id: PlayerId,
) -> tuple[EconomyOutcome, ...]:
    """Resolve one player's settlements in deterministic settlement-id order."""
    outcomes: list[EconomyOutcome] = []
    player = session.players[player_id]
    settlements = [
        settlement
        for _, settlement in sorted(session.settlements.items())
        if settlement.owner_id == player_id
    ]
    for settlement in settlements:
        yields = settlement_yield(session, settlement)
        settlement.food_storage += yields.food
        settlement.production_storage += yields.production
        player.gold += yields.gold
        player.science += yields.science
        player.culture += yields.culture
        outcomes.append(
            EconomyOutcome(
                "SettlementYielded",
                {"settlement_id": settlement.settlement_id, **yields.as_dict()},
            )
        )

        while settlement.food_storage >= growth_threshold(settlement.population):
            threshold = growth_threshold(settlement.population)
            settlement.food_storage -= threshold
            settlement.population += 1
            outcomes.append(
                EconomyOutcome(
                    "PopulationGrew",
                    {
                        "settlement_id": settlement.settlement_id,
                        "population": settlement.population,
                    },
                )
            )

        outcomes.extend(_resolve_production(session, settlement))
    return tuple(outcomes)


def _resolve_production(
    session: GameSession,
    settlement: SettlementState,
) -> list[EconomyOutcome]:
    outcomes: list[EconomyOutcome] = []
    while settlement.production_queue:
        order = settlement.production_queue[0]
        owner = session.players[settlement.owner_id]
        if not production_is_unlocked(owner, order.definition_id):
            break
        if settlement.production_storage < order.cost:
            break
        if order.kind is ProductionKind.UNIT:
            spawn = _find_unit_spawn(session, settlement.center)
            if spawn is None:
                break
            definition = UNITS[order.definition_id]
            unit_id = UnitId(f"unit-{session.next_unit_index}")
            session.next_unit_index += 1
            session.units[unit_id] = UnitState.spawn(
                unit_id=unit_id,
                owner_id=settlement.owner_id,
                definition=definition,
                position=spawn,
            )
            session.players[settlement.owner_id].ever_had_presence = True
            outcomes.append(
                EconomyOutcome(
                    "UnitProduced",
                    {
                        "settlement_id": settlement.settlement_id,
                        "unit_id": unit_id,
                        "definition_id": definition.definition_id,
                        "q": spawn.q,
                        "r": spawn.r,
                    },
                )
            )
        else:
            settlement.buildings.add(order.definition_id)
            outcomes.append(
                EconomyOutcome(
                    "BuildingCompleted",
                    {
                        "settlement_id": settlement.settlement_id,
                        "definition_id": order.definition_id,
                    },
                )
            )
        settlement.production_storage -= order.cost
        settlement.production_queue.pop(0)
    return outcomes


def _find_unit_spawn(session: GameSession, center: HexCoord) -> HexCoord | None:
    candidates = (center, *sorted(neighbors(center)))
    occupied = {unit.position for unit in session.units.values()}
    for coord in candidates:
        tile = session.world.tiles.get(coord)
        if tile is not None and tile.passable and coord not in occupied:
            return coord
    return None
