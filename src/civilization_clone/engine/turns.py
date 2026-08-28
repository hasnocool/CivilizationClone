"""Sequential deterministic turn advancement helpers."""

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId


def refresh_player_units(session: GameSession, player_id: PlayerId) -> None:
    """Refresh movement for units owned by the player whose turn is starting."""
    for unit in session.units.values():
        if unit.owner_id == player_id:
            unit.movement_remaining = unit.definition.movement


def advance_turn(session: GameSession) -> tuple[bool, PlayerId]:
    """Advance active player and return (wrapped_game_turn, new_active_player)."""
    if not session.player_order:
        raise ValueError("cannot advance turn without players")
    session.active_player_index += 1
    wrapped = session.active_player_index >= len(session.player_order)
    if wrapped:
        session.active_player_index = 0
        session.turn += 1
    player_id = session.player_order[session.active_player_index]
    refresh_player_units(session, player_id)
    return wrapped, player_id
