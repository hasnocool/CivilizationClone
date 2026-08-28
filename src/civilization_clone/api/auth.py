"""Stateless signed credentials for API authority without simulation coupling."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass

from civilization_clone.domain.ids import GameId, PlayerId


class AuthenticationError(ValueError):
    """Raised when an API credential is missing, malformed, or unauthorized."""


@dataclass(frozen=True, slots=True)
class AuthManager:
    """Issue and verify HMAC-signed game/player credentials.

    Credentials are transport/application metadata only. They never enter authoritative
    game state, deterministic events, replay input, or state hashes.
    """

    secret: bytes

    @classmethod
    def from_environment(cls) -> "AuthManager":
        """Create auth using a configured secret or an ephemeral local-process secret."""
        configured = os.getenv("CIVILIZATION_CLONE_AUTH_SECRET")
        if configured:
            return cls(configured.encode("utf-8"))
        return cls(secrets.token_bytes(32))

    def issue_admin(self, game_id: GameId) -> str:
        return self._issue({"kind": "admin", "game_id": str(game_id)})

    def issue_player(self, game_id: GameId, player_id: PlayerId) -> str:
        return self._issue(
            {
                "kind": "player",
                "game_id": str(game_id),
                "player_id": str(player_id),
            }
        )

    def verify_admin(self, token: str, game_id: GameId) -> None:
        payload = self._verify(token)
        if payload.get("kind") != "admin" or payload.get("game_id") != str(game_id):
            raise AuthenticationError("credential is not authorized for this game")

    def verify_player(self, token: str, game_id: GameId) -> PlayerId:
        payload = self._verify(token)
        if payload.get("kind") != "player" or payload.get("game_id") != str(game_id):
            raise AuthenticationError("credential is not authorized for this game")
        raw_player_id = payload.get("player_id")
        if not isinstance(raw_player_id, str) or not raw_player_id:
            raise AuthenticationError("credential has no player identity")
        return PlayerId(raw_player_id)

    def _issue(self, payload: dict[str, str]) -> str:
        encoded = _b64encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        signature = hmac.new(self.secret, encoded.encode("ascii"), hashlib.sha256).digest()
        return f"{encoded}.{_b64encode(signature)}"

    def _verify(self, token: str) -> dict[str, str]:
        try:
            encoded, raw_signature = token.split(".", 1)
            supplied_signature = _b64decode(raw_signature)
        except (ValueError, UnicodeError) as exc:
            raise AuthenticationError("invalid credential") from exc
        expected = hmac.new(self.secret, encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(supplied_signature, expected):
            raise AuthenticationError("invalid credential")
        try:
            raw_payload = json.loads(_b64decode(encoded).decode("utf-8"))
        except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
            raise AuthenticationError("invalid credential") from exc
        if not isinstance(raw_payload, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in raw_payload.items()
        ):
            raise AuthenticationError("invalid credential")
        return raw_payload


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
