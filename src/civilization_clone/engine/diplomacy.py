"""Deterministic bilateral diplomacy helpers."""

from __future__ import annotations

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId
from civilization_clone.domain.strategy import DiplomaticRelationship, DiplomacyStatus


def relationship_key(first: PlayerId, second: PlayerId) -> tuple[PlayerId, PlayerId]:
    """Return the stable unordered key for a bilateral relationship."""
    if first == second:
        raise ValueError("a player cannot have diplomacy with itself")
    return (first, second) if first < second else (second, first)


def get_relationship(
    session: GameSession,
    first: PlayerId,
    second: PlayerId,
) -> DiplomaticRelationship:
    """Return/create one bilateral relationship in canonical key order."""
    key = relationship_key(first, second)
    relationship = session.diplomacy.get(key)
    if relationship is None:
        relationship = DiplomaticRelationship(status=DiplomacyStatus.PEACE)
        session.diplomacy[key] = relationship
    return relationship


def declare_war(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Enter war, returning a stable rejection reason when invalid."""
    if actor not in session.players or target not in session.players:
        return "player_not_found"
    if actor == target:
        return "self_target"
    relationship = get_relationship(session, actor, target)
    if relationship.status is DiplomacyStatus.WAR:
        return "already_at_war"
    relationship.status = DiplomacyStatus.WAR
    relationship.pending_peace_from = None
    return None


def offer_peace(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Record a deterministic peace proposal from one side of a war."""
    if actor not in session.players or target not in session.players:
        return "player_not_found"
    if actor == target:
        return "self_target"
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.WAR:
        return "not_at_war"
    relationship.pending_peace_from = actor
    return None


def accept_peace(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Accept the opposing player's pending peace offer."""
    if actor not in session.players or target not in session.players:
        return "player_not_found"
    if actor == target:
        return "self_target"
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.WAR:
        return "not_at_war"
    if relationship.pending_peace_from != target:
        return "no_pending_offer"
    relationship.status = DiplomacyStatus.PEACE
    relationship.pending_peace_from = None
    return None


def at_war(session: GameSession, first: PlayerId, second: PlayerId) -> bool:
    """Return whether two players are currently at war without mutating state."""
    relationship = session.diplomacy.get(relationship_key(first, second))
    return relationship is not None and relationship.status is DiplomacyStatus.WAR
