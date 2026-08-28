"""Async public API client using worker-thread isolated stdlib HTTP I/O."""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

JsonObject = dict[str, Any]
JsonValue = JsonObject | list[Any] | str | int | float | bool | None


class ApiError(RuntimeError):
    """Safe client-side representation of an HTTP/API failure."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"API {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class JsonTransport(Protocol):
    async def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        query: dict[str, str | int] | None = None,
        token: str | None = None,
    ) -> JsonValue: ...


@dataclass(frozen=True, slots=True)
class UrllibJsonTransport:
    """Small async-safe JSON transport with all urllib work off the event loop."""

    base_url: str = "http://127.0.0.1:8000"
    timeout: float = 10.0

    async def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        query: dict[str, str | int] | None = None,
        token: str | None = None,
    ) -> JsonValue:
        return await asyncio.to_thread(
            self._request_sync,
            method,
            path,
            payload,
            query,
            token,
        )

    def _request_sync(
        self,
        method: str,
        path: str,
        payload: JsonObject | None,
        query: dict[str, str | int] | None,
        token: str | None,
    ) -> JsonValue:
        base = self.base_url.rstrip("/")
        url = f"{base}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as exc:
            detail = exc.reason
            try:
                payload_value = json.loads(exc.read().decode("utf-8"))
                if isinstance(payload_value, dict):
                    detail = str(payload_value.get("detail", detail))
            except (UnicodeError, ValueError):
                pass
            raise ApiError(exc.code, str(detail)) from exc
        except urllib.error.URLError as exc:
            raise ApiError(0, f"connection failed: {exc.reason}") from exc


@dataclass(slots=True)
class CivilizationApiClient:
    """Typed-enough convenience wrapper around the stable public v1 API."""

    transport: JsonTransport = field(default_factory=UrllibJsonTransport)
    _client_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    _command_number: int = 0

    async def health(self) -> JsonObject:
        return _object(await self.transport.request("GET", "/api/v1/health"))

    async def civilizations(self) -> list[JsonObject]:
        value = await self.transport.request("GET", "/api/v1/rules/civilizations")
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise ApiError(0, "API returned an invalid civilization list")
        return [dict(item) for item in value]

    async def create_game(
        self,
        game_id: str,
        *,
        seed: int,
        player_count: int = 2,
        map_radius: int = 4,
        water_percent: int = 20,
        resource_percent: int = 18,
    ) -> JsonObject:
        return _object(
            await self.transport.request(
                "POST",
                "/api/v1/games",
                payload={
                    "game_id": game_id,
                    "seed": seed,
                    "player_count": player_count,
                    "map_radius": map_radius,
                    "water_percent": water_percent,
                    "resource_percent": resource_percent,
                },
            )
        )

    async def join_player(
        self,
        game_id: str,
        admin_token: str,
        *,
        player_id: str,
        name: str,
        controller: str = "human",
        civilization_id: str = "river_compact",
    ) -> JsonObject:
        return _object(
            await self.transport.request(
                "POST",
                f"/api/v1/games/{game_id}/players",
                token=admin_token,
                payload={
                    "command_id": self._next_command_id("join"),
                    "player_id": player_id,
                    "name": name,
                    "controller": controller,
                    "civilization_id": civilization_id,
                },
            )
        )

    async def start_game(self, game_id: str, admin_token: str) -> JsonObject:
        return await self.command(
            game_id,
            admin_token,
            "StartGame",
            player_id=None,
            expected_state_version=None,
        )

    async def command(
        self,
        game_id: str,
        token: str,
        command_type: str,
        *,
        player_id: str | None = None,
        expected_state_version: int | None = None,
        payload: JsonObject | None = None,
    ) -> JsonObject:
        body: JsonObject = {
            "command_id": self._next_command_id(command_type.lower()),
            "command_type": command_type,
            "payload": payload or {},
        }
        if player_id is not None:
            body["player_id"] = player_id
        if expected_state_version is not None:
            body["expected_state_version"] = expected_state_version
        return _object(
            await self.transport.request(
                "POST",
                f"/api/v1/games/{game_id}/commands",
                token=token,
                payload=body,
            )
        )

    async def state(self, game_id: str, player_token: str) -> JsonObject:
        return _object(
            await self.transport.request(
                "GET",
                f"/api/v1/games/{game_id}/state",
                token=player_token,
            )
        )

    async def legal_actions(self, game_id: str, player_token: str) -> JsonObject:
        return _object(
            await self.transport.request(
                "GET",
                f"/api/v1/games/{game_id}/legal-actions",
                token=player_token,
            )
        )

    async def events(
        self,
        game_id: str,
        player_token: str,
        *,
        after_sequence: int = -1,
    ) -> list[JsonObject]:
        value = await self.transport.request(
            "GET",
            f"/api/v1/games/{game_id}/events",
            token=player_token,
            query={"after_sequence": after_sequence},
        )
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise ApiError(0, "API returned an invalid event list")
        return [dict(item) for item in value]

    def _next_command_id(self, prefix: str) -> str:
        self._command_number += 1
        return f"client-{self._client_id}-{prefix}-{self._command_number}"


def _object(value: JsonValue) -> JsonObject:
    if not isinstance(value, dict):
        raise ApiError(0, "API returned an invalid JSON object")
    return value
