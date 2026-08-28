"""Sequential deterministic turn advancement helpers."""

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId


def refresh_player_units(session: GameSession, player_id: PlayerId) -> None:
    """Refresh movement for units owned by the player whose turn is starting."""
    for unit in session.units.values():
        if unit.owner_id == player_id:
            unit.movement_remaining = unit.definition.movement


def advance_turn(session: GameSession) -> tuple[bool, PlayerId]:
    """Advance to the next non-eliminated player.

    Returns ``(wrapped_game_turn, new_active_player)``. A full pass over the player order
    advances the global turn exactly once, even when eliminated players are skipped.
    """
    if not session.player_order:
        raise ValueError("cannot advance turn without players")

    living = [
        player_id
        for player_id in session.player_order
        if not session.players[player_id].eliminated
    ]
    if not living:
        raise ValueError("cannot advance turn without a living player")

    wrapped = False
    for _ in range(len(session.player_order)):
        session.active_player_index += 1
        if session.active_player_index >= len(session.player_order):
            session.active_player_index = 0
            session.turn += 1
            wrapped = True
        player_id = session.player_order[session.active_player_index]
        if not session.players[player_id].eliminated:
            refresh_player_units(session, player_id)
            return wrapped, player_id

    raise RuntimeError("failed to locate a living active player")
