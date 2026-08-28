"""Presentation-safe read models for rules/content discovery.

This module deliberately adapts authoritative registries into client-facing data.
It does not decide simulation outcomes and exposes no hidden player information.
"""

from __future__ import annotations

from civilization_clone.api.schemas import (
    BuildingDefinitionResponse,
    ProductionOptionResponse,
    ProductionOptionsResponse,
    ResearchOptionResponse,
    ResearchOptionsResponse,
    RulesContentResponse,
    TechnologyDefinitionResponse,
    UnitDefinitionResponse,
    YieldModifierResponse,
)
from civilization_clone.domain.economy import ProductionKind, SettlementState
from civilization_clone.domain.gameplay import GameSession, PlayerState
from civilization_clone.domain.ids import PlayerId
from civilization_clone.engine.economy import BUILDINGS, UNITS, production_rule_blockers
from civilization_clone.engine.research import (
    PRODUCTION_TECH_REQUIREMENTS,
    TECHNOLOGIES,
    effective_research_cost,
)
from civilization_clone.rules.poc import POC_UNIQUE_BUILDING_OWNERS, POC_UNIQUE_UNIT_OWNERS


def rules_content_response() -> RulesContentResponse:
    """Return deterministic public presentation metadata for the POC ruleset."""
    units = [
        UnitDefinitionResponse(
            definition_id=definition_id,
            name=_display_name(definition_id),
            movement=definition.movement,
            vision_radius=definition.vision_radius,
            production_cost=definition.production_cost,
            can_found=definition.can_found,
            attack_strength=definition.attack_strength,
            defense_strength=definition.defense_strength,
            ranged_range=definition.ranged_range,
            required_civilization=_optional_str(POC_UNIQUE_UNIT_OWNERS.get(definition_id)),
            required_technology=PRODUCTION_TECH_REQUIREMENTS.get(definition_id),
        )
        for definition_id, definition in sorted(UNITS.items())
    ]
    buildings = [
        BuildingDefinitionResponse(
            definition_id=definition_id,
            name=_display_name(definition_id),
            production_cost=definition.cost,
            yield_modifiers=[
                YieldModifierResponse(
                    source=modifier.source,
                    yield_type=modifier.yield_type.value,
                    operation=modifier.operation.value,
                    value=modifier.value,
                    priority=modifier.priority,
                )
                for modifier in definition.modifiers
            ],
            required_civilization=_optional_str(
                POC_UNIQUE_BUILDING_OWNERS.get(definition_id)
            ),
            required_technology=PRODUCTION_TECH_REQUIREMENTS.get(definition_id),
        )
        for definition_id, definition in sorted(BUILDINGS.items())
    ]
    technologies = [
        TechnologyDefinitionResponse(
            technology_id=technology_id,
            name=_display_name(technology_id),
            cost=definition.cost,
            prerequisites=sorted(definition.prerequisites),
            unlocks=list(definition.unlocks),
        )
        for technology_id, definition in sorted(TECHNOLOGIES.items())
    ]
    return RulesContentResponse(
        units=units,
        buildings=buildings,
        technologies=technologies,
    )


def production_options_response(
    session: GameSession,
    player_id: PlayerId,
    settlement: SettlementState,
) -> ProductionOptionsResponse:
    """Return player-authorized queue options without changing queue semantics.

    ``queue_allowed`` mirrors current QueueProduction action-level requirements.
    ``completion_unlocked`` reports only stable content gates used by production
    resolution (civilization ownership and research unlocks). Resource accumulation
    and unit spawn-space availability are intentionally left as runtime conditions,
    not permanent content locks.
    """
    player = session.players[player_id]
    is_active_player = session.current_player_id == player_id and not player.eliminated
    options: list[ProductionOptionResponse] = []

    for definition_id, definition in sorted(UNITS.items()):
        options.append(
            _production_option(
                player=player,
                settlement=settlement,
                is_active_player=is_active_player,
                kind=ProductionKind.UNIT,
                definition_id=definition_id,
                cost=definition.production_cost,
                required_civilization=_optional_str(
                    POC_UNIQUE_UNIT_OWNERS.get(definition_id)
                ),
            )
        )
    for definition_id, definition in sorted(BUILDINGS.items()):
        options.append(
            _production_option(
                player=player,
                settlement=settlement,
                is_active_player=is_active_player,
                kind=ProductionKind.BUILDING,
                definition_id=definition_id,
                cost=definition.cost,
                required_civilization=_optional_str(
                    POC_UNIQUE_BUILDING_OWNERS.get(definition_id)
                ),
            )
        )

    return ProductionOptionsResponse(
        game_id=str(session.game_id),
        player_id=str(player_id),
        settlement_id=str(settlement.settlement_id),
        state_version=session.state_version,
        is_active_player=is_active_player,
        options=options,
    )


def research_options_response(
    session: GameSession,
    player_id: PlayerId,
) -> ResearchOptionsResponse:
    """Return viewer-authorized research costs, content state, and turn legality."""
    player = session.players[player_id]
    is_active_player = session.current_player_id == player_id and not player.eliminated
    options: list[ResearchOptionResponse] = []
    for technology_id, definition in sorted(TECHNOLOGIES.items()):
        blockers: list[str] = []
        if technology_id in player.research.completed:
            status = "completed"
            blockers.append("already_completed")
        elif not definition.prerequisites <= player.research.completed:
            status = "locked"
            blockers.append("prerequisites_incomplete")
        elif player.research.selected == technology_id:
            status = "selected"
        else:
            status = "available"
        if not is_active_player and "already_completed" not in blockers:
            blockers.append("not_active_player")
        options.append(
            ResearchOptionResponse(
                technology_id=technology_id,
                name=_display_name(technology_id),
                base_cost=definition.cost,
                effective_cost=effective_research_cost(player, technology_id),
                prerequisites=sorted(definition.prerequisites),
                unlocks=list(definition.unlocks),
                status=status,
                selectable=not blockers,
                blockers=blockers,
            )
        )
    return ResearchOptionsResponse(
        game_id=str(session.game_id),
        player_id=str(player_id),
        state_version=session.state_version,
        is_active_player=is_active_player,
        options=options,
    )


def _production_option(
    *,
    player: PlayerState,
    settlement: SettlementState,
    is_active_player: bool,
    kind: ProductionKind,
    definition_id: str,
    cost: int,
    required_civilization: str | None,
) -> ProductionOptionResponse:
    queue_blockers: list[str] = []
    if not is_active_player:
        queue_blockers.append("not_active_player")
    if kind is ProductionKind.BUILDING and definition_id in settlement.buildings:
        queue_blockers.append("already_built")

    completion_blockers = list(production_rule_blockers(player, kind, definition_id))
    if kind is ProductionKind.BUILDING and definition_id in settlement.buildings:
        completion_blockers.insert(0, "already_built")

    return ProductionOptionResponse(
        kind=kind.value,
        definition_id=definition_id,
        name=_display_name(definition_id),
        cost=cost,
        queue_allowed=not queue_blockers,
        queue_blockers=queue_blockers,
        completion_unlocked=not completion_blockers,
        completion_blockers=completion_blockers,
        required_civilization=required_civilization,
        required_technology=PRODUCTION_TECH_REQUIREMENTS.get(definition_id),
    )


def _display_name(definition_id: str) -> str:
    return definition_id.replace("_", " ").title()


def _optional_str(value: object | None) -> str | None:
    return None if value is None else str(value)
