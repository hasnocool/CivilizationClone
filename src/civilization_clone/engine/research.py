"""Deterministic technology DAG validation and per-player research resolution."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.domain.gameplay import PlayerState
from civilization_clone.domain.strategy import TechnologyDefinition
from civilization_clone.domain.types import JsonValue

TECHNOLOGIES: dict[str, TechnologyDefinition] = {
    "surveying": TechnologyDefinition("surveying", 5, unlocks=("exploration_methods",)),
    "masonry": TechnologyDefinition("masonry", 7, unlocks=("settlement_methods",)),
    "bronze_work": TechnologyDefinition(
        "bronze_work",
        8,
        prerequisites=frozenset({"surveying"}),
        unlocks=("warrior",),
    ),
    "engineering": TechnologyDefinition(
        "engineering",
        10,
        prerequisites=frozenset({"masonry"}),
        unlocks=("production_methods",),
    ),
    "archery": TechnologyDefinition(
        "archery",
        9,
        prerequisites=frozenset({"surveying"}),
        unlocks=("archer",),
    ),
    "writing": TechnologyDefinition(
        "writing",
        8,
        prerequisites=frozenset({"masonry"}),
        unlocks=("knowledge_archive",),
    ),
    "mathematics": TechnologyDefinition(
        "mathematics",
        12,
        prerequisites=frozenset({"writing"}),
        unlocks=("calculation_methods",),
    ),
    "logistics": TechnologyDefinition(
        "logistics",
        14,
        prerequisites=frozenset({"engineering", "mathematics"}),
        unlocks=("logistics_methods",),
    ),
}

PRODUCTION_TECH_REQUIREMENTS: dict[str, str] = {
    "warrior": "bronze_work",
    "archer": "archery",
}


@dataclass(frozen=True, slots=True)
class ResearchOutcome:
    """One deterministic research-domain event description."""

    event_type: str
    payload: dict[str, JsonValue]


def validate_technology_dag(
    technologies: dict[str, TechnologyDefinition] = TECHNOLOGIES,
) -> None:
    """Reject missing prerequisites and cycles in a technology definition set."""
    missing = {
        prerequisite
        for technology in technologies.values()
        for prerequisite in technology.prerequisites
        if prerequisite not in technologies
    }
    if missing:
        raise ValueError(f"unknown technology prerequisites: {sorted(missing)}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(technology_id: str) -> None:
        if technology_id in visited:
            return
        if technology_id in visiting:
            raise ValueError(f"technology cycle detected at {technology_id}")
        visiting.add(technology_id)
        for prerequisite in sorted(technologies[technology_id].prerequisites):
            visit(prerequisite)
        visiting.remove(technology_id)
        visited.add(technology_id)

    for technology_id in sorted(technologies):
        visit(technology_id)


def available_technologies(player: PlayerState) -> tuple[str, ...]:
    """Return currently selectable technologies in stable order."""
    completed = player.research.completed
    return tuple(
        technology_id
        for technology_id, definition in sorted(TECHNOLOGIES.items())
        if technology_id not in completed and definition.prerequisites <= completed
    )


def choose_research(player: PlayerState, technology_id: str) -> str | None:
    """Select research and return a rejection reason when it is unavailable."""
    definition = TECHNOLOGIES.get(technology_id)
    if definition is None:
        return "unknown_technology"
    if technology_id in player.research.completed:
        return "already_completed"
    if not definition.prerequisites <= player.research.completed:
        return "prerequisites_incomplete"
    if player.research.selected != technology_id:
        player.research.selected = technology_id
        player.research.progress = 0
    return None


def production_is_unlocked(player: PlayerState, definition_id: str) -> bool:
    """Return whether a production definition's research prerequisite is satisfied."""
    required = PRODUCTION_TECH_REQUIREMENTS.get(definition_id)
    return required is None or required in player.research.completed


def resolve_research(player: PlayerState) -> tuple[ResearchOutcome, ...]:
    """Spend accumulated science on selected research without losing overflow."""
    outcomes: list[ResearchOutcome] = []
    selected = player.research.selected
    if selected is None or player.science <= 0:
        return ()

    while selected is not None and player.science > 0:
        definition = TECHNOLOGIES[selected]
        remaining = definition.cost - player.research.progress
        spent = min(player.science, remaining)
        player.science -= spent
        player.research.progress += spent
        outcomes.append(
            ResearchOutcome(
                "ResearchAdvanced",
                {
                    "player_id": player.player_id,
                    "technology_id": selected,
                    "spent": spent,
                    "progress": player.research.progress,
                    "cost": definition.cost,
                },
            )
        )
        if player.research.progress < definition.cost:
            break

        player.research.completed.add(selected)
        player.research.selected = None
        player.research.progress = 0
        outcomes.append(
            ResearchOutcome(
                "TechnologyCompleted",
                {
                    "player_id": player.player_id,
                    "technology_id": selected,
                    "unlocks": list(definition.unlocks),
                },
            )
        )
        selected = None
    return tuple(outcomes)


validate_technology_dag()
