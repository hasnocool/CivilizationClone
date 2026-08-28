import io
import json
import logging

from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager
from civilization_clone.observability.logging import JsonLogFormatter


def _logger(stream: io.StringIO) -> logging.Logger:
    logger = logging.getLogger("civilization_clone.test.runtime_api")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    return logger


def test_http_and_command_logs_include_safe_context_without_credentials() -> None:
    stream = io.StringIO()
    logger = _logger(stream)
    manager = GameManager(logger=logger)
    client = TestClient(
        create_app(
            manager,
            AuthManager(b"runtime-log-secret"),
            runtime_logger=logger,
        )
    )

    created = client.post(
        "/api/v1/games",
        json={"game_id": "logging-game", "seed": 12, "player_count": 2},
    )
    assert created.status_code == 201
    admin_token = created.json()["admin_token"]
    joined = client.post(
        "/api/v1/games/logging-game/players",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "command_id": "logging-join",
            "player_id": "p1",
            "name": "Private Player Name",
        },
    )
    assert joined.status_code == 200

    raw_logs = stream.getvalue()
    assert admin_token not in raw_logs
    assert "Private Player Name" not in raw_logs
    records = [json.loads(line) for line in raw_logs.splitlines() if line.strip()]
    assert any(
        record.get("operation") == "JoinGame"
        and record.get("command_id") == "logging-join"
        and record.get("accepted") is True
        and isinstance(record.get("duration_ms"), (int, float))
        for record in records
    )
    assert any(
        record.get("path") == "/api/v1/games/logging-game/players"
        and record.get("method") == "POST"
        and record.get("status_code") == 200
        for record in records
    )
