# tests/unit/test_ids.py
import pytest

from civilization_clone.domain.ids import GameId, PlayerId, validate_id


def test_validate_id_constructs_typed_value() -> None:
    assert validate_id("game-1", GameId) == "game-1"
    assert validate_id("player-1", PlayerId) == "player-1"


@pytest.mark.parametrize("value", ["", "   ", "game one", "\tgame"])
def test_validate_id_rejects_blank_or_whitespace(value: str) -> None:
    with pytest.raises(ValueError):
        validate_id(value, GameId)
