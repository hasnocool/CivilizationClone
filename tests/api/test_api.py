# tests/api/test_api.py
from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager


def _client() -> TestClient:
    return TestClient(create_app(GameManager(), AuthManager(b"test-secret")))


def _create(client: TestClient, game_id: str, *, seed: int = 4242) -> str:
    response = client.post(
        "/api/v1/games",
        json={"game_id": game_id, "seed": seed, "player_count": 2, "water_percent": 0},
    )
    assert response.status_code == 201
    token = response.json()["admin_token"]
    assert isinstance(token, str) and token
    return token


def _join(
    client: TestClient,
    game_id: str,
    admin_token: str,
    player_id: str,
    civilization_id: str = "river_compact",
) -> str:
    response = client.post(
        f"/api/v1/games/{game_id}/players",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "command_id": f"join-{player_id}",
            "player_id": player_id,
            "name": player_id,
            "civilization_id": civilization_id,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"]
    assert body["civilization_id"] == civilization_id
    token = body["player_token"]
    assert isinstance(token, str) and token
    return token


def _command(
    client: TestClient,
    game_id: str,
    token: str,
    command_id: str,
    command_type: str,
    *,
    player_id: str | None = None,
    payload: dict[str, object] | None = None,
    expected_state_version: int | None = None,
) -> dict[str, object]:
    body: dict[str, object] = {
        "command_id": command_id,
        "command_type": command_type,
        "payload": payload or {},
    }
    if player_id is not None:
        body["player_id"] = player_id
    if expected_state_version is not None:
        body["expected_state_version"] = expected_state_version
    response = client.post(
        f"/api/v1/games/{game_id}/commands",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )
    assert response.status_code == 200
    return response.json()


def test_api_exposes_and_validates_original_civilization_content() -> None:
    client = _client()
    civilizations = client.get("/api/v1/rules/civilizations")
    assert civilizations.status_code == 200
    body = civilizations.json()
    assert [item["civilization_id"] for item in body] == [
        "river_compact",
        "horizon_league",
    ]
    assert all(item["description"] for item in body)

    admin = _create(client, "civilization-api")
    p1_token = _join(
        client,
        "civilization-api",
        admin,
        "p1",
        civilization_id="horizon_league",
    )
    rejected = client.post(
        "/api/v1/games/civilization-api/players",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "command_id": "join-invalid-civ",
            "player_id": "p2",
            "name": "p2",
            "civilization_id": "not-a-civilization",
        },
    )
    assert rejected.status_code == 200
    assert not rejected.json()["accepted"]
    assert rejected.json()["feedback"][0]["code"] == "INVALID_CIVILIZATION"

    state = client.get(
        "/api/v1/games/civilization-api/state",
        headers={"Authorization": f"Bearer {p1_token}"},
    )
    assert state.status_code == 200
    assert state.json()["viewer"]["civilization_id"] == "horizon_league"


def test_api_exposes_presentation_safe_rules_content_in_stable_order() -> None:
    client = _client()
    response = client.get("/api/v1/rules/content")
    assert response.status_code == 200
    body = response.json()

    unit_ids = [item["definition_id"] for item in body["units"]]
    building_ids = [item["definition_id"] for item in body["buildings"]]
    technology_ids = [item["technology_id"] for item in body["technologies"]]
    assert unit_ids == sorted(unit_ids)
    assert building_ids == sorted(building_ids)
    assert technology_ids == sorted(technology_ids)

    units = {item["definition_id"]: item for item in body["units"]}
    buildings = {item["definition_id"]: item for item in body["buildings"]}
    technologies = {item["technology_id"]: item for item in body["technologies"]}

    assert units["river_warden"]["name"] == "River Warden"
    assert units["river_warden"]["required_civilization"] == "river_compact"
    assert units["warrior"]["required_technology"] == "bronze_work"
    assert buildings["field_archive"]["required_civilization"] == "horizon_league"
    assert buildings["field_archive"]["yield_modifiers"][0]["yield_type"] == "science"
    assert technologies["bronze_work"]["prerequisites"] == ["surveying"]
    assert "warrior" in technologies["bronze_work"]["unlocks"]


def test_api_game_lifecycle_and_player_projection_hide_enemy_start() -> None:
    client = _client()
    admin = _create(client, "api-game")
    p1_token = _join(client, "api-game", admin, "p1", "horizon_league")
    _join(client, "api-game", admin, "p2")

    started = _command(client, "api-game", admin, "start", "StartGame")
    assert started["accepted"]
    assert all(event["event_type"] != "UnitSpawned" for event in started["events"])

    state = client.get(
        "/api/v1/games/api-game/state",
        headers={"Authorization": f"Bearer {p1_token}"},
    )
    assert state.status_code == 200
    projection = state.json()
    assert projection["viewer"]["player_id"] == "p1"
    assert projection["viewer"]["civilization_id"] == "horizon_league"
    assert {player["civilization_id"] for player in projection["players"]} == {
        "river_compact",
        "horizon_league",
    }
    assert {unit["owner_id"] for unit in projection["units"]} == {"p1"}
    assert len(projection["map"]["tiles"]) < 61

    legal = client.get(
        "/api/v1/games/api-game/legal-actions",
        headers={"Authorization": f"Bearer {p1_token}"},
    )
    assert legal.status_code == 200
    assert "EndTurn" in legal.json()["actions"]
    assert legal.json()["mandatory_decisions"][0]["kind"] == "research"


def test_production_options_are_player_scoped_and_preserve_queue_semantics() -> None:
    client = _client()
    admin = _create(client, "production-options", seed=17)
    p1_token = _join(client, "production-options", admin, "p1", "horizon_league")
    p2_token = _join(client, "production-options", admin, "p2", "river_compact")
    _command(client, "production-options", admin, "start", "StartGame")

    state = client.get(
        "/api/v1/games/production-options/state",
        headers={"Authorization": f"Bearer {p1_token}"},
    ).json()
    founder_id = state["units"][0]["unit_id"]
    founded = _command(
        client,
        "production-options",
        p1_token,
        "found-for-options",
        "FoundSettlement",
        player_id="p1",
        payload={"unit_id": founder_id},
    )
    assert founded["accepted"]

    state = client.get(
        "/api/v1/games/production-options/state",
        headers={"Authorization": f"Bearer {p1_token}"},
    ).json()
    settlement_id = state["settlements"][0]["settlement_id"]

    missing_auth = client.get(
        "/api/v1/games/production-options/production-options",
        params={"settlement_id": settlement_id},
    )
    assert missing_auth.status_code == 401

    response = client.get(
        "/api/v1/games/production-options/production-options",
        params={"settlement_id": settlement_id},
        headers={"Authorization": f"Bearer {p1_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["player_id"] == "p1"
    assert body["settlement_id"] == settlement_id
    assert body["is_active_player"] is True

    options = {(item["kind"], item["definition_id"]): item for item in body["options"]}
    trailblazer = options[("unit", "trailblazer")]
    assert trailblazer["queue_allowed"] is True
    assert trailblazer["completion_unlocked"] is True

    river_warden = options[("unit", "river_warden")]
    assert river_warden["queue_allowed"] is True
    assert river_warden["completion_unlocked"] is False
    assert river_warden["completion_blockers"] == ["civilization_restricted"]

    warrior = options[("unit", "warrior")]
    assert warrior["queue_allowed"] is True
    assert warrior["completion_unlocked"] is False
    assert warrior["completion_blockers"] == ["technology_required"]

    enemy_lookup = client.get(
        "/api/v1/games/production-options/production-options",
        params={"settlement_id": settlement_id},
        headers={"Authorization": f"Bearer {p2_token}"},
    )
    assert enemy_lookup.status_code == 404
    assert enemy_lookup.json()["detail"] == "settlement not found"


def test_api_rejects_forged_or_mismatched_player_identity() -> None:
    client = _client()
    admin = _create(client, "auth-api")
    p1_token = _join(client, "auth-api", admin, "p1")
    _join(client, "auth-api", admin, "p2")
    _command(client, "auth-api", admin, "start", "StartGame")

    missing = client.get("/api/v1/games/auth-api/state")
    assert missing.status_code == 401

    forged = client.get(
        "/api/v1/games/auth-api/state",
        headers={"Authorization": "Bearer definitely-not-valid"},
    )
    assert forged.status_code == 403

    mismatch = client.post(
        "/api/v1/games/auth-api/commands",
        headers={"Authorization": f"Bearer {p1_token}"},
        json={
            "command_id": "forged-player",
            "command_type": "EndTurn",
            "player_id": "p2",
            "payload": {},
        },
    )
    assert mismatch.status_code == 403


def test_api_returns_safe_feedback_for_stale_state_version() -> None:
    client = _client()
    admin = _create(client, "stale-api", seed=9)
    p1_token = _join(client, "stale-api", admin, "p1")
    _join(client, "stale-api", admin, "p2")
    _command(client, "stale-api", admin, "start", "StartGame")

    body = _command(
        client,
        "stale-api",
        p1_token,
        "stale-command",
        "EndTurn",
        player_id="p1",
        expected_state_version=0,
    )
    assert not body["accepted"]
    assert body["feedback"][0]["code"] == "STALE_STATE_VERSION"
    assert "path" not in body["feedback"][0]["context"]


def test_join_game_command_is_not_available_on_generic_command_route() -> None:
    client = _client()
    admin = _create(client, "join-route")
    response = client.post(
        "/api/v1/games/join-route/commands",
        headers={"Authorization": f"Bearer {admin}"},
        json={"command_id": "bad-join", "command_type": "JoinGame", "payload": {}},
    )
    assert response.status_code == 405
