# tests/simulation/test_ai_runner.py
from __future__ import annotations

import asyncio

from civilization_clone.ai.runner import create_bot_match, run_bot_match
from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import GameId


async def _run(seed: int):
    manager = GameManager()
    game_id = GameId(f"bot-game-{seed}")
    await create_bot_match(manager, game_id=game_id, seed=seed, player_count=2)
    return await run_bot_match(manager, game_id=game_id, max_commands=160)


def test_bot_simulation_is_deterministic_and_advances_turns() -> None:
    first = asyncio.run(_run(1337))
    second = asyncio.run(_run(1337))

    assert first.commands == second.commands == 160
    assert first.accepted_commands == second.accepted_commands
    assert first.rejected_commands == second.rejected_commands
    assert first.turns == second.turns
    assert first.turns > 2
    assert first.state_hash == second.state_hash
    assert first.event_hash == second.event_hash
