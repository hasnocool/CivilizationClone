# tests/unit/test_logging.py
import io
import json
import logging

from civilization_clone.domain.ids import GameId, RulesetId
from civilization_clone.domain.state import CoreGameState, RulesetRef
from civilization_clone.engine.state_hash import state_hash
from civilization_clone.observability.logging import configure_logging, log_with_context


def build_state_hash() -> str:
    return state_hash(
        CoreGameState(
            game_id=GameId("game-1"),
            ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
            seed=42,
        )
    )


def test_json_logging_contains_context() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = configure_logging(level=logging.DEBUG, json_output=True, handler=handler)
    log_with_context(
        logger,
        logging.INFO,
        "command accepted",
        {"game_id": "game-1", "command_id": "cmd-1", "state_version": 2},
    )

    record = json.loads(stream.getvalue())
    assert record["message"] == "command accepted"
    assert record["game_id"] == "game-1"
    assert record["command_id"] == "cmd-1"
    assert record["state_version"] == 2


def test_logging_configuration_does_not_change_state_hash() -> None:
    before = build_state_hash()
    stream = io.StringIO()
    logger = configure_logging(
        level=logging.DEBUG,
        json_output=True,
        handler=logging.StreamHandler(stream),
    )
    log_with_context(logger, logging.DEBUG, "diagnostic", {"game_id": "game-1"})
    after = build_state_hash()

    assert before == after
