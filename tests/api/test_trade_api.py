from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager


def _setup_three_player_game() -> tuple[TestClient, dict[str, str]]:
    client = TestClient(create_app(GameManager(), AuthManager(b"trade-api-test-secret")))
    created = client.post(
        "/api/v1/games",
        json={
            "game_id": "trade-api",
            "seed": 919,
            "player_count": 3,
            "water_percent": 0,
        },
    )
    assert created.status_code == 201
    admin = created.json()["admin_token"]
    tokens: dict[str, str] = {}
    for index, player_id in enumerate(("p1", "p2", "p3"), start=1):
        joined = client.post(
            "/api/v1/games/trade-api/players",
            headers={"Authorization": f"Bearer {admin}"},
            json={
                "command_id": f"join-{index}",
                "player_id": player_id,
                "name": player_id,
                "civilization_id": "river_compact",
            },
        )
        assert joined.status_code == 200
        assert joined.json()["accepted"]
        tokens[player_id] = joined.json()["player_token"]

    started = client.post(
        "/api/v1/games/trade-api/commands",
        headers={"Authorization": f"Bearer {admin}"},
        json={"command_id": "start", "command_type": "StartGame", "payload": {}},
    )
    assert started.status_code == 200
    assert started.json()["accepted"]
    return client, tokens


def _command(
    client: TestClient,
    token: str,
    command_id: str,
    command_type: str,
    player_id: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/games/trade-api/commands",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "command_id": command_id,
            "command_type": command_type,
            "player_id": player_id,
            "payload": payload or {},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_trade_commands_are_legal_and_bilateral_events_remain_private() -> None:
    client, tokens = _setup_three_player_game()

    legal = client.get(
        "/api/v1/games/trade-api/legal-actions",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    )
    assert legal.status_code == 200
    for command_type in ("OfferTrade", "AcceptTrade", "RejectTrade", "CancelTrade"):
        assert command_type in legal.json()["actions"]

    offered = _command(
        client,
        tokens["p1"],
        "trade-offer",
        "OfferTrade",
        "p1",
        {"target_player_id": "p2", "offered_gold": 2, "requested_gold": 1},
    )
    assert offered["accepted"] is True
    assert [event["event_type"] for event in offered["events"]] == ["TradeOffered"]

    p1_state = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    ).json()
    p2_state = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p2']}"},
    ).json()
    p3_state = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p3']}"},
    ).json()

    p1_relation = next(item for item in p1_state["diplomacy"] if item["other_player_id"] == "p2")
    p2_relation = next(item for item in p2_state["diplomacy"] if item["other_player_id"] == "p1")
    assert p1_relation["pending_trade"] == {
        "proposer_id": "p1",
        "offered_gold": 2,
        "requested_gold": 1,
    }
    assert p2_relation["pending_trade"] == p1_relation["pending_trade"]
    assert all(item["pending_trade"] is None for item in p3_state["diplomacy"])

    p2_events = client.get(
        "/api/v1/games/trade-api/events",
        headers={"Authorization": f"Bearer {tokens['p2']}"},
    ).json()
    p3_events = client.get(
        "/api/v1/games/trade-api/events",
        headers={"Authorization": f"Bearer {tokens['p3']}"},
    ).json()
    assert any(event["event_type"] == "TradeOffered" for event in p2_events)
    assert all(event["event_type"] != "TradeOffered" for event in p3_events)

    assert _command(
        client,
        tokens["p1"],
        "research-p1",
        "ChooseResearch",
        "p1",
        {"technology_id": "surveying"},
    )["accepted"] is True
    assert _command(client, tokens["p1"], "end-p1", "EndTurn", "p1")["accepted"] is True

    accepted = _command(
        client,
        tokens["p2"],
        "accept-trade",
        "AcceptTrade",
        "p2",
        {"target_player_id": "p1"},
    )
    assert accepted["accepted"] is True
    assert [event["event_type"] for event in accepted["events"]] == ["TradeAccepted"]

    p1_after = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    ).json()
    p2_after = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p2']}"},
    ).json()
    assert p1_after["viewer"]["gold"] == 3
    assert p2_after["viewer"]["gold"] == 5
    completed = next(
        item for item in p1_after["diplomacy"] if item["other_player_id"] == "p2"
    )
    assert completed["pending_trade"] is None
    assert completed["completed_trades"] == 1


def test_trade_rejects_invalid_or_unaffordable_terms_without_mutating_gold() -> None:
    client, tokens = _setup_three_player_game()
    before = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    ).json()

    invalid = _command(
        client,
        tokens["p1"],
        "bad-trade",
        "OfferTrade",
        "p1",
        {"target_player_id": "p2", "offered_gold": 999, "requested_gold": 0},
    )
    assert invalid["accepted"] is False
    assert invalid["feedback"][0]["code"] == "TRADE_REJECTED"
    assert invalid["feedback"][0]["context"]["reason"] == "insufficient_gold"

    after = client.get(
        "/api/v1/games/trade-api/state",
        headers={"Authorization": f"Bearer {tokens['p1']}"},
    ).json()
    assert after["viewer"]["gold"] == before["viewer"]["gold"]
