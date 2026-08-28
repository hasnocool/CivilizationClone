# tests/api/test_websocket.py
from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager


def test_authenticated_websocket_publishes_new_events_in_order() -> None:
    client = TestClient(create_app(GameManager(), AuthManager(b"ws-secret")))
    created = client.post(
        "/api/v1/games",
        json={"game_id": "ws-game", "seed": 707, "player_count": 2, "water_percent": 0},
    ).json()
    admin = created["admin_token"]

    tokens: dict[str, str] = {}
    for index, player_id in enumerate(("p1", "p2"), start=1):
        joined = client.post(
            "/api/v1/games/ws-game/players",
            headers={"Authorization": f"Bearer {admin}"},
            json={
                "command_id": f"join-{index}",
                "player_id": player_id,
                "name": player_id,
            },
        ).json()
        tokens[player_id] = joined["player_token"]

    started = client.post(
        "/api/v1/games/ws-game/commands",
        headers={"Authorization": f"Bearer {admin}"},
        json={"command_id": "start", "command_type": "StartGame", "payload": {}},
    )
    assert started.status_code == 200

    history = client.get(
        "/api/v1/games/ws-game/events",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    ).json()
    after_sequence = max(event["sequence"] for event in history)

    with client.websocket_connect(
        f"/api/v1/games/ws-game/events/ws?after_sequence={after_sequence}",
        subprotocols=["civilization.v1", tokens["p1"]],
    ) as websocket:
        assert websocket.accepted_subprotocol == "civilization.v1"
        response = client.post(
            "/api/v1/games/ws-game/commands",
            headers={"Authorization": f"Bearer {tokens['p1']}"},
            json={
                "command_id": "research",
                "command_type": "ChooseResearch",
                "player_id": "p1",
                "payload": {"technology_id": "surveying"},
            },
        )
        assert response.status_code == 200
        event = websocket.receive_json()
        assert event["sequence"] == after_sequence + 1
        assert event["event_type"] == "ResearchSelected"
        assert event["payload"]["player_id"] == "p1"
