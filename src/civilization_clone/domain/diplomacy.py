"""Deterministic player-to-player diplomacy primitives."""

from enum import StrEnum

from civilization_clone.domain.ids import PlayerId


class DiplomacyStatus(StrEnum):
    PEACE = "peace"
    WAR = "war"


def relationship_key(left: PlayerId, right: PlayerId) -> tuple[PlayerId, PlayerId]:
    """Return a stable unordered key for one player pair."""
    if left == right:
        raise ValueError("a player cannot have a diplomatic relationship with itself")
    return tuple(sorted((left, right)))  # type: ignore[return-value]
