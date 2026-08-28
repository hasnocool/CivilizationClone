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
from civilization_clone.persistence.replay import ReplayVerificationError


async def run_benchmark(*, games: int, seed: int, max_commands: int) -> dict[str, object]:
    """Run deterministic matches and report non-authoritative timing/quality metrics."""
    if games <= 0:
        raise ValueError("games must be positive")
    if max_commands <= 0:
        raise ValueError("max_commands must be positive")

    manager = GameManager()
    summaries: list[dict[str, object]] = []
    total_commands = 0
    total_accepted = 0
    total_rejected = 0
    total_turns = 0
    finished_games = 0
    replay_failures = 0
    simulation_seconds = 0.0
    replay_seconds = 0.0
    victory_distribution: dict[str, int] = {}

    for index in range(games):
        game_id = GameId(f"benchmark-{seed}-{index}")
        simulation_started_ns = time.perf_counter_ns()
        await create_bot_match(manager, game_id=game_id, seed=seed + index, player_count=2)
        metrics = await run_bot_match(
            manager,
            game_id=game_id,
            max_commands=max_commands,
        )
        simulation_seconds += (
            time.perf_counter_ns() - simulation_started_ns
        ) / 1_000_000_000

        replay_started_ns = time.perf_counter_ns()
        replay_matched = False
        try:
            replay_matched = (await manager.verify_replay(game_id)).matched
        except ReplayVerificationError:
            replay_failures += 1
        else:
            if not replay_matched:
                replay_failures += 1
        replay_seconds += (time.perf_counter_ns() - replay_started_ns) / 1_000_000_000

        data = asdict(metrics)
        data["game_id"] = str(metrics.game_id)
        data["winner_id"] = str(metrics.winner_id) if metrics.winner_id is not None else None
        data["replay_matched"] = replay_matched
        summaries.append(data)

        total_commands += metrics.commands
        total_accepted += metrics.accepted_commands
        total_rejected += metrics.rejected_commands
        total_turns += metrics.turns
        if metrics.finished:
            finished_games += 1
        victory_key = metrics.victory_type or "unfinished"
        victory_distribution[victory_key] = victory_distribution.get(victory_key, 0) + 1

    elapsed_seconds = simulation_seconds + replay_seconds
    return {
        "games": games,
        "seed": seed,
        "max_commands": max_commands,
        "elapsed_seconds": elapsed_seconds,
        "simulation_seconds": simulation_seconds,
        "replay_verification_seconds": replay_seconds,
        "commands": total_commands,
        "accepted_commands": total_accepted,
        "rejected_commands": total_rejected,
        "rejection_rate": total_rejected / total_commands if total_commands else 0.0,
        "turns": total_turns,
        "finished_games": finished_games,
        "completion_rate": finished_games / games,
        "victory_distribution": dict(sorted(victory_distribution.items())),
        "replay_failures": replay_failures,
        "replay_failure_rate": replay_failures / games,
        "commands_per_second": (
            total_commands / simulation_seconds if simulation_seconds else 0.0
        ),
        "turns_per_second": total_turns / simulation_seconds if simulation_seconds else 0.0,
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
