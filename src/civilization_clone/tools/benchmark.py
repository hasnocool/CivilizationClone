"""Local performance baseline runner for deterministic bot simulations."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict

from civilization_clone.ai.runner import create_bot_match, run_bot_match
from civilization_clone.application.manager import GameManager
from civilization_clone.domain.ids import GameId


async def run_benchmark(*, games: int, seed: int, max_commands: int) -> dict[str, object]:
    """Run deterministic matches and report non-authoritative timing metrics."""
    if games <= 0:
        raise ValueError("games must be positive")
    manager = GameManager()
    started_ns = time.perf_counter_ns()
    summaries: list[dict[str, object]] = []
    total_commands = 0
    total_turns = 0

    for index in range(games):
        game_id = GameId(f"benchmark-{seed}-{index}")
        await create_bot_match(manager, game_id=game_id, seed=seed + index, player_count=2)
        metrics = await run_bot_match(
            manager,
            game_id=game_id,
            max_commands=max_commands,
        )
        data = asdict(metrics)
        data["game_id"] = str(metrics.game_id)
        data["winner_id"] = str(metrics.winner_id) if metrics.winner_id is not None else None
        summaries.append(data)
        total_commands += metrics.commands
        total_turns += metrics.turns

    elapsed_seconds = (time.perf_counter_ns() - started_ns) / 1_000_000_000
    return {
        "games": games,
        "seed": seed,
        "max_commands": max_commands,
        "elapsed_seconds": elapsed_seconds,
        "commands": total_commands,
        "turns": total_turns,
        "commands_per_second": total_commands / elapsed_seconds if elapsed_seconds else 0.0,
        "turns_per_second": total_turns / elapsed_seconds if elapsed_seconds else 0.0,
        "matches": summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark CivilizationClone bot simulations")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--max-commands", type=int, default=2000)
    args = parser.parse_args()
    result = asyncio.run(
        run_benchmark(games=args.games, seed=args.seed, max_commands=args.max_commands)
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
