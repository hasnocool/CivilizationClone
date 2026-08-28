"""Deterministic bilateral diplomacy helpers."""

from __future__ import annotations

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId
from civilization_clone.domain.strategy import DiplomaticRelationship, DiplomacyStatus, TradeOffer

MAX_TRADE_GOLD = 1000


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
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is DiplomacyStatus.WAR:
        return "already_at_war"
    relationship.status = DiplomacyStatus.WAR
    relationship.pending_peace_from = None
    relationship.pending_trade = None
    return None


def offer_peace(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Record a deterministic peace proposal from one side of a war."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.WAR:
        return "not_at_war"
    relationship.pending_peace_from = actor
    return None


def accept_peace(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Accept the opposing player's pending peace offer."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.WAR:
        return "not_at_war"
    if relationship.pending_peace_from != target:
        return "no_pending_offer"
    relationship.status = DiplomacyStatus.PEACE
    relationship.pending_peace_from = None
    return None


def reject_peace(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Reject the opposing player's pending peace offer while remaining at war."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.WAR:
        return "not_at_war"
    if relationship.pending_peace_from != target:
        return "no_pending_offer"
    relationship.pending_peace_from = None
    return None


def offer_trade(
    session: GameSession,
    actor: PlayerId,
    target: PlayerId,
    offered_gold: int,
    requested_gold: int,
) -> str | None:
    """Create one pending bilateral gold trade offer.

    Offers are intentionally simple and atomic for v1.1: no recurring timers or
    hidden trade simulation exists. This keeps replay/state semantics explicit while
    creating a stable foundation for later trade routes and treaty systems.
    """
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.PEACE:
        return "trade_requires_peace"
    if relationship.pending_trade is not None:
        return "trade_offer_pending"
    if offered_gold < 0 or requested_gold < 0:
        return "invalid_trade_amount"
    if offered_gold > MAX_TRADE_GOLD or requested_gold > MAX_TRADE_GOLD:
        return "trade_amount_too_large"
    if offered_gold == 0 and requested_gold == 0:
        return "empty_trade"
    if session.players[actor].gold < offered_gold:
        return "insufficient_gold"
    relationship.pending_trade = TradeOffer(
        proposer_id=actor,
        offered_gold=offered_gold,
        requested_gold=requested_gold,
    )
    return None


def accept_trade(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Accept the other player's pending offer and atomically exchange gold."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    if relationship.status is not DiplomacyStatus.PEACE:
        return "trade_requires_peace"
    offer = relationship.pending_trade
    if offer is None or offer.proposer_id != target:
        return "no_pending_trade"
    proposer = session.players[target]
    recipient = session.players[actor]
    if proposer.gold < offer.offered_gold or recipient.gold < offer.requested_gold:
        return "insufficient_gold"

    proposer.gold = proposer.gold - offer.offered_gold + offer.requested_gold
    recipient.gold = recipient.gold - offer.requested_gold + offer.offered_gold
    relationship.pending_trade = None
    relationship.completed_trades += 1
    relationship.last_trade_turn = session.turn
    return None


def reject_trade(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Reject the other player's pending trade offer."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    offer = relationship.pending_trade
    if offer is None or offer.proposer_id != target:
        return "no_pending_trade"
    relationship.pending_trade = None
    return None


def cancel_trade(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    """Cancel the actor's own pending trade proposal."""
    reason = _participant_reason(session, actor, target)
    if reason is not None:
        return reason
    relationship = get_relationship(session, actor, target)
    offer = relationship.pending_trade
    if offer is None or offer.proposer_id != actor:
        return "no_owned_trade_offer"
    relationship.pending_trade = None
    return None


def cancel_trade_offers_for_player(
    session: GameSession,
    player_id: PlayerId,
) -> tuple[tuple[PlayerId, TradeOffer], ...]:
    """Clear pending offers involving a player and return deterministic cancellation data."""
    cancelled: list[tuple[PlayerId, TradeOffer]] = []
    for (first, second), relationship in sorted(session.diplomacy.items()):
        if player_id not in (first, second) or relationship.pending_trade is None:
            continue
        counterpart = second if first == player_id else first
        cancelled.append((counterpart, relationship.pending_trade))
        relationship.pending_trade = None
    return tuple(cancelled)


def at_war(session: GameSession, first: PlayerId, second: PlayerId) -> bool:
    """Return whether two players are currently at war without mutating state."""
    relationship = session.diplomacy.get(relationship_key(first, second))
    return relationship is not None and relationship.status is DiplomacyStatus.WAR


def _participant_reason(session: GameSession, actor: PlayerId, target: PlayerId) -> str | None:
    if actor not in session.players or target not in session.players:
        return "player_not_found"
    if actor == target:
        return "self_target"
    if session.players[actor].eliminated or session.players[target].eliminated:
        return "player_eliminated"
    return None
