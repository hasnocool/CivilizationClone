"""Canonical serialization and hashing for deterministic state verification."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
from typing import Any


def _normalize(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _normalize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Enum):
        return _normalize(value.value)
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("canonical state mappings require string keys")
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized_items = [_normalize(item) for item in value]
        return sorted(normalized_items, key=_encode_normalized)
    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported canonical state value: {type(value).__name__}")


def _encode_normalized(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_json(value: Any) -> str:
    """Serialize state into canonical JSON independent of mapping/set insertion order."""
    return _encode_normalized(_normalize(value))


def state_hash(value: Any) -> str:
    """Return a SHA-256 hex digest of canonical state."""
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()
