"""Deterministic technology prerequisite graph and research progression."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId
from civilization_clone.domain.types import JsonValue


@dataclass(frozen=True, slots=True)
class TechnologyDefinition:
    technology_id: str
    cost: int
    prerequisites: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.technology_id.strip():
            raise ValueError("technology id must not be blank")
        if self.cost <= 0:
            raise ValueError("technology cost must be positive")


TECHNOLOGIES: dict[str, TechnologyDefinition] = {
    "agriculture": TechnologyDefinition("agriculture", 5),
    "masonry": TechnologyDefinition("masonry", 8, ("agriculture",)),
    "writing": TechnologyDefinition("writing", 6),
    "mathematics": TechnologyDefinition("mathematics", 10, ("writing",)),
}


@dataclass(frozen=True, slots=True)
class ResearchOutcome:
    event_type: str
    payload: dict[str, JsonValue]


def available_technologies(session: GameSession, player_id: PlayerId) -> tuple[str, ...]:
    player = session.players[player_id]
    return tuple(
        technology_id
        for technology_id, definition in sorted(TECHNOLOGIES.items())
        if technology_id not in player.completed_technologies
        and all(item in player.completed_technologies for item in definition.prerequisites)
    )


def choose_research(session: GameSession, player_id: PlayerId, technology_id: str) -> str | None:
    definition = TECHNOLOGIES.get(technology_id)
    if definition is None:
        return "technology_not_found"
    player = session.players[player_id]
    if technology_id in player.completed_technologies:
        return "technology_completed"
    if any(item not in player.completed_technologies for item in definition.prerequisites):
        return "prerequisites_missing"
    player.current_research = technology_id
    return None


def resolve_research(
    session: GameSession,
    player_id: PlayerId,
    science_points: int,
) -> tuple[ResearchOutcome, ...]:
    player = session.players[player_id]
    technology_id = player.current_research
    if technology_id is None or science_points <= 0:
        return ()
    definition = TECHNOLOGIES[technology_id]
    progress = player.research_progress.get(technology_id, 0) + science_points
    player.research_progress[technology_id] = progress
    outcomes = [ResearchOutcome("TechnologyProgressed", {
        "player_id": player_id, "technology_id": technology_id,
        "progress": progress, "cost": definition.cost,
    })]
    if progress >= definition.cost:
        player.completed_technologies.add(technology_id)
        player.current_research = None
        outcomes.append(ResearchOutcome("TechnologyCompleted", {
            "player_id": player_id, "technology_id": technology_id,
        }))
    return tuple(outcomes)
