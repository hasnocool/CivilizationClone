# tests/unit/test_state.py
import pytest

from civilization_clone.domain.ids import GameId, RulesetId
from civilization_clone.domain.state import CoreGameState, RulesetRef


def test_core_game_state_defaults_to_setup() -> None:
    state = CoreGameState(
        game_id=GameId("game-1"),
        ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
        seed=123,
    )

    assert state.state_version == 0
    assert state.turn == 0
    assert state.phase.value == "setup"
    assert state.status.value == "setup"


@pytest.mark.parametrize("field,value", [("state_version", -1), ("turn", -1)])
def test_core_game_state_rejects_negative_counters(field: str, value: int) -> None:
    kwargs = {field: value}
    with pytest.raises(ValueError):
        CoreGameState(
            game_id=GameId("game-1"),
            ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
            seed=123,
            **kwargs,
        )
