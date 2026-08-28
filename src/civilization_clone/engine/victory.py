"""Deterministic elimination, scoring, and POC victory checks."""

from __future__ import annotations

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId
from civilization_clone.domain.strategy import VictoryResult, VictoryType


def player_score(session: GameSession, player_id: PlayerId) -> int:
    """Compute a small deterministic POC score from authoritative state."""
    player = session.players[player_id]
    settlement_population = sum(
        settlement.population
        for settlement in session.settlements.values()
        if settlement.owner_id == player_id
    )
    settlement_count = sum(
        1 for settlement in session.settlements.values() if settlement.owner_id == player_id
    )
    unit_count = sum(1 for unit in session.units.values() if unit.owner_id == player_id)
    return (
        settlement_population * 10
        + settlement_count * 20
        + unit_count * 5
        + len(player.research.completed) * 8
        + player.gold
        + player.culture
    )


def update_eliminations(session: GameSession) -> tuple[PlayerId, ...]:
    """Eliminate players with no settlements and no units after they once had presence."""
    eliminated: list[PlayerId] = []
    for player_id in session.player_order:
        player = session.players[player_id]
        if player.eliminated:
            continue
        has_unit = any(unit.owner_id == player_id for unit in session.units.values())
        has_settlement = any(
            settlement.owner_id == player_id for settlement in session.settlements.values()
        )
        if player.ever_had_presence and not has_unit and not has_settlement:
            player.eliminated = True
            eliminated.append(player_id)
    return tuple(eliminated)


def check_victory(session: GameSession) -> VictoryResult | None:
    """Return a final POC victory when conquest or maximum-turn score is satisfied."""
    if session.victory is not None:
        return session.victory

    living = [player_id for player_id in session.player_order if not session.players[player_id].eliminated]
    if len(living) == 1 and len(session.player_order) >= 2:
        winner = living[0]
        result = VictoryResult(
            winner_id=winner,
            victory_type=VictoryType.CONQUEST,
            turn=session.turn,
            score=player_score(session, winner),
        )
        session.victory = result
        return result

    if session.turn > session.max_turns:
        ranked = sorted(
            (
                (player_score(session, player_id), player_id)
                for player_id in session.player_order
                if not session.players[player_id].eliminated
            ),
            key=lambda item: (-item[0], item[1]),
        )
        if not ranked:
            return None
        score, winner = ranked[0]
        result = VictoryResult(
            winner_id=winner,
            victory_type=VictoryType.SCORE,
            turn=session.turn,
            score=score,
        )
        session.victory = result
        return result
    return None
