"""Deterministic conquest and score victory evaluation."""

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId
from civilization_clone.domain.state import GameStatus
from civilization_clone.domain.victory import VictoryKind


def player_score(session: GameSession, player_id: PlayerId) -> int:
    player = session.players[player_id]
    settlements = [item for item in session.settlements.values() if item.owner_id == player_id]
    units = [item for item in session.units.values() if item.owner_id == player_id]
    return (
        sum(item.population * 10 + len(item.buildings) * 5 for item in settlements)
        + len(units) * 2
        + len(player.completed_technologies) * 8
        + player.gold
    )


def evaluate_victory(session: GameSession) -> tuple[PlayerId, VictoryKind] | None:
    active = [player_id for player_id in session.player_order if not session.players[player_id].eliminated]
    if len(active) == 1 and len(session.player_order) >= 2:
        session.winner_id = active[0]
        session.victory_kind = VictoryKind.CONQUEST
        session.status = GameStatus.FINISHED
        return active[0], VictoryKind.CONQUEST
    if session.turn > session.max_turns and active:
        winner = max(active, key=lambda player_id: (player_score(session, player_id), str(player_id)))
        session.winner_id = winner
        session.victory_kind = VictoryKind.SCORE
        session.status = GameStatus.FINISHED
        return winner, VictoryKind.SCORE
    return None
