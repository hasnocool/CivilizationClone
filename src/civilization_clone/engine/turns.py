"""Sequential deterministic turn advancement helpers."""

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import PlayerId


def refresh_player_units(session: GameSession, player_id: PlayerId) -> None:
    for unit in session.units.values():
        if unit.owner_id == player_id:
            unit.movement_remaining = unit.definition.movement


def advance_turn(session: GameSession) -> tuple[bool, PlayerId]:
    """Advance to the next non-eliminated player."""
    if not session.player_order:
        raise ValueError("cannot advance turn without players")
    start_index = session.active_player_index
    wrapped = False
    while True:
        session.active_player_index += 1
        if session.active_player_index >= len(session.player_order):
            session.active_player_index = 0
            session.turn += 1
            wrapped = True
        player_id = session.player_order[session.active_player_index]
        if not session.players[player_id].eliminated:
            refresh_player_units(session, player_id)
            return wrapped, player_id
        if session.active_player_index == start_index:
            raise ValueError("no active players remain")
