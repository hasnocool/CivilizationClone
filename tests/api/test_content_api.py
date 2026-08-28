from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager


def test_research_options_expose_effective_viewer_costs_and_states() -> None:
    client = TestClient(create_app(GameManager(), AuthManager(b"content-test-secret")))
    created = client.post(
        "/api/v1/games",
        json={
            "game_id": "research-options",
            "seed": 31,
            "player_count": 2,
            "water_percent": 0,
        },
    )
    assert created.status_code == 201
    admin = created.json()["admin_token"]

    p1 = client.post(
        "/api/v1/games/research-options/players",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "command_id": "join-p1",
            "player_id": "p1",
            "name": "p1",
            "civilization_id": "horizon_league",
        },
    ).json()["player_token"]
    p2 = client.post(
        "/api/v1/games/research-options/players",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "command_id": "join-p2",
            "player_id": "p2",
            "name": "p2",
            "civilization_id": "river_compact",
        },
    ).json()["player_token"]

    started = client.post(
        "/api/v1/games/research-options/commands",
        headers={"Authorization": f"Bearer {admin}"},
        json={"command_id": "start", "command_type": "StartGame", "payload": {}},
    )
    assert started.status_code == 200
    assert started.json()["accepted"]

    response = client.get(
        "/api/v1/games/research-options/research-options",
        headers={"Authorization": f"Bearer {p1}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["player_id"] == "p1"
    options = {item["technology_id"]: item for item in body["options"]}

    assert options["masonry"]["base_cost"] == 7
    assert options["masonry"]["effective_cost"] == 6
    assert options["masonry"]["status"] == "available"
    assert options["masonry"]["selectable"] is True
    assert options["bronze_work"]["status"] == "locked"
    assert options["bronze_work"]["blockers"] == ["prerequisites_incomplete"]

    river_response = client.get(
        "/api/v1/games/research-options/research-options",
        headers={"Authorization": f"Bearer {p2}"},
    )
    assert river_response.status_code == 200
    river_options = {
        item["technology_id"]: item for item in river_response.json()["options"]
    }
    assert river_options["masonry"]["effective_cost"] == 7

    missing_auth = client.get("/api/v1/games/research-options/research-options")
    assert missing_auth.status_code == 401
