from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager


def _client() -> TestClient:
    return TestClient(create_app(GameManager(), AuthManager(b"civilization-api-secret")))


def test_public_civilization_catalog_exposes_selection_and_bonus_data() -> None:
    client = _client()

    response = client.get("/api/v1/rules/civilizations")

    assert response.status_code == 200
    civilizations = response.json()
    assert [item["civilization_id"] for item in civilizations] == [
        "river_compact",
        "horizon_league",
    ]
    river, horizon = civilizations
    assert river["starting_resources"] == {"gold": 4, "culture": 1}
    assert river["yield_modifiers"][0]["yield_type"] == "food"
    assert river["defense_strength_percent"] == 10
    assert horizon["starting_resources"] == {"gold": 2, "science": 2}
    assert horizon["yield_modifiers"][0]["yield_type"] == "science"
    assert horizon["research_cost_percent"] == -15


def test_join_player_selects_civilization_and_projection_reports_it() -> None:
    client = _client()
    created = client.post(
        "/api/v1/games",
        json={"game_id": "civ-api-game", "seed": 17, "player_count": 2},
    )
    assert created.status_code == 201
    admin_token = created.json()["admin_token"]

    joined = client.post(
        "/api/v1/games/civ-api-game/players",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "command_id": "join-horizon",
            "player_id": "p1",
            "name": "One",
            "civilization_id": "horizon_league",
        },
    )
    assert joined.status_code == 200
    body = joined.json()
    assert body["accepted"]
    assert body["civilization_id"] == "horizon_league"
    player_token = body["player_token"]

    state = client.get(
        "/api/v1/games/civ-api-game/state",
        headers={"Authorization": f"Bearer {player_token}"},
    )
    assert state.status_code == 200
    assert state.json()["viewer"]["civilization_id"] == "horizon_league"
    assert state.json()["viewer"]["science"] == 2
