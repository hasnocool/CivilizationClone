import asyncio

from civilization_clone.tools.benchmark import run_benchmark


def test_benchmark_reports_plan_quality_and_replay_metrics() -> None:
    result = asyncio.run(run_benchmark(games=2, seed=9000, max_commands=80))

    assert result["games"] == 2
    assert result["commands"] == result["accepted_commands"] + result["rejected_commands"]
    assert 0.0 <= result["completion_rate"] <= 1.0
    assert 0.0 <= result["rejection_rate"] <= 1.0
    assert result["replay_failures"] == 0
    assert result["replay_failure_rate"] == 0.0
    assert sum(result["victory_distribution"].values()) == 2
    assert result["commands_per_second"] >= 0.0
    assert result["turns_per_second"] >= 0.0
    assert len(result["matches"]) == 2
    assert all(match["replay_matched"] for match in result["matches"])
