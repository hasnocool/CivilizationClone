# tests/api/test_api.py
from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.application.manager import GameManager


def _command(
    client: TestClient,
    game_id: str,
    command_id: str,
    command_type: str,
    *,
    player_id: str | None = None,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/games/{game_id}/commands",
        json={
            "command_id": command_id,
            "command_type": command_type,
            "player_id": player_id,
            "payload": payload or {},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_api_game_lifecycle_and_player_projection_hide_enemy_start() -> None:
    client = TestClient(create_app(GameManager()))
    created = client.post(
        "/api/v1/games",
        json={
            "game_id": "api-game",
            "seed": 4242,
            "map_radius": 4,
            "player_count": 2,
            "water_percent": 0,
        },
    )
    assert created.status_code == 201

    assert _command(
        client,
        "api-game",
        "join-1",
        "JoinGame",
        player_id="p1",
        payload={"name": "One"},
    )["accepted"]
    assert _command(
        client,
        "api-game",
        "join-2",
        "JoinGame",
        player_id="p2",
        payload={"name": "Two"},
    )["accepted"]
    started = _command(client, "api-game", "start", "StartGame")
    assert started["accepted"]
    assert all(event["event_type"] != "UnitSpawned" for event in started["events"])

    state = client.get("/api/v1/games/api-game/state", params={"player_id": "p1"})
    assert state.status_code == 200
    projection = state.json()
    assert projection["viewer"]["player_id"] == "p1"
    assert {unit["owner_id"] for unit in projection["units"]} == {"p1"}
    assert len(projection["map"]["tiles"]) < 61

    legal = client.get(
        "/api/v1/games/api-game/legal-actions",
        params={"player_id": "p1"},
    )
    assert legal.status_code == 200
    assert "EndTurn" in legal.json()["actions"]
    assert legal.json()["mandatory_decisions"][0]["kind"] == "research"


def test_api_returns_safe_feedback_for_stale_state_version() -> None:
    client = TestClient(create_app(GameManager()))
    assert client.post(
        "/api/v1/games",
        json={"game_id": "stale-api", "seed": 9, "player_count": 2},
    ).status_code == 201
    _command(
        client,
        "stale-api",
        "join-1",
        "JoinGame",
        player_id="p1",
        payload={"name": "One"},
    )
    _command(
        client,
        "stale-api",
        "join-2",
        "JoinGame",
        player_id="p2",
        payload={"name": "Two"},
    )
    _command(client, "stale-api", "start", "StartGame")

    response = client.post(
        "/api/v1/games/stale-api/commands",
        json={
            "command_id": "stale-command",
            "command_type": "EndTurn",
            "player_id": "p1",
            "expected_state_version": 0,
            "payload": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert not body["accepted"]
    assert body["feedback"][0]["code"] == "STALE_STATE_VERSION"
    assert "path" not in body["feedback"][0]["context"]
