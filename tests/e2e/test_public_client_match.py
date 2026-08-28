# tests/e2e/test_public_client_match.py
from __future__ import annotations

import asyncio
from typing import Any

from fastapi.testclient import TestClient

from civilization_clone.api.app import create_app
from civilization_clone.api.auth import AuthManager
from civilization_clone.application.manager import GameManager
from civilization_clone.client.http import ApiError, CivilizationApiClient, JsonObject, JsonValue


class TestClientTransport:
    """Test-only transport preserving the same async client boundary."""

    def __init__(self, client: TestClient) -> None:
        self.client = client

    async def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        query: dict[str, str | int] | None = None,
        token: str | None = None,
    ) -> JsonValue:
        headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
        response = await asyncio.to_thread(
            self.client.request,
            method,
            path,
            json=payload,
            params=query,
            headers=headers,
        )
        if response.status_code >= 400:
            detail: Any = response.json().get("detail", response.text)
            raise ApiError(response.status_code, str(detail))
        return response.json() if response.content else None


async def _play() -> None:
    app = create_app(GameManager(), AuthManager(b"e2e-secret"))
    http = TestClient(app)
    api = CivilizationApiClient(TestClientTransport(http))

    rules = await api.rules_content()
    assert any(item["definition_id"] == "scout" for item in rules["units"])
    assert any(item["technology_id"] == "surveying" for item in rules["technologies"])

    created = await api.create_game("e2e-game", seed=6006, player_count=2, water_percent=0)
    admin = str(created["admin_token"])
    p1 = await api.join_player("e2e-game", admin, player_id="p1", name="One")
    p2 = await api.join_player("e2e-game", admin, player_id="p2", name="Two")
    assert p1["accepted"] and p2["accepted"]
    p1_token = str(p1["player_token"])
    p2_token = str(p2["player_token"])

    assert (await api.start_game("e2e-game", admin))["accepted"]
    state = await api.state("e2e-game", p1_token)
    assert state["viewer"]["player_id"] == "p1"
    assert state["active_player_id"] == "p1"

    research_options = await api.research_options("e2e-game", p1_token)
    surveying = next(
        item for item in research_options["options"] if item["technology_id"] == "surveying"
    )
    assert surveying["selectable"]

    research = await api.command(
        "e2e-game",
        p1_token,
        "ChooseResearch",
        player_id="p1",
        expected_state_version=int(state["state_version"]),
        payload={"technology_id": "surveying"},
    )
    assert research["accepted"]

    state = await api.state("e2e-game", p1_token)
    founder_id = str(state["units"][0]["unit_id"])
    founded = await api.command(
        "e2e-game",
        p1_token,
        "FoundSettlement",
        player_id="p1",
        expected_state_version=int(state["state_version"]),
        payload={"unit_id": founder_id},
    )
    assert founded["accepted"]

    state = await api.state("e2e-game", p1_token)
    settlement_id = str(state["settlements"][0]["settlement_id"])
    production_options = await api.production_options("e2e-game", p1_token, settlement_id)
    scout = next(
        item
        for item in production_options["options"]
        if item["kind"] == "unit" and item["definition_id"] == "scout"
    )
    assert scout["queue_allowed"]
    queued = await api.command(
        "e2e-game",
        p1_token,
        "QueueProduction",
        player_id="p1",
        expected_state_version=int(state["state_version"]),
        payload={
            "settlement_id": settlement_id,
            "kind": "unit",
            "definition_id": "scout",
        },
    )
    assert queued["accepted"]

    state = await api.state("e2e-game", p1_token)
    conceded = await api.command(
        "e2e-game",
        p1_token,
        "Concede",
        player_id="p1",
        expected_state_version=int(state["state_version"]),
    )
    assert conceded["accepted"]

    final = await api.state("e2e-game", p2_token)
    assert final["status"] == "finished"
    assert final["victory"]["winner_id"] == "p2"
    events = await api.events("e2e-game", p2_token)
    assert events[-1]["event_type"] == "VictoryAchieved"


def test_public_client_can_complete_authenticated_match() -> None:
    asyncio.run(_play())
