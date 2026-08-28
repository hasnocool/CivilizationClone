"""Strict data-driven civilization definition schema and loader."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from civilization_clone.domain.ids import CivilizationId, validate_id

_ALLOWED_KEYS = frozenset(
    {
        "id",
        "name",
        "description",
        "tags",
        "research_preferences",
        "content_hooks",
    }
)


@dataclass(frozen=True, slots=True)
class CivilizationDefinition:
    """Original POC civilization identity expressed entirely as content data."""

    civilization_id: CivilizationId
    name: str
    description: str
    tags: tuple[str, ...] = ()
    research_preferences: tuple[str, ...] = ()
    content_hooks: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CivilizationDefinition":
        unknown = set(data) - _ALLOWED_KEYS
        if unknown:
            raise ValueError(f"unknown civilization fields: {sorted(unknown)}")
        raw_id = data.get("id")
        name = data.get("name")
        description = data.get("description", "")
        if not isinstance(raw_id, str):
            raise TypeError("civilization id must be text")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("civilization name must be non-empty text")
        if not isinstance(description, str):
            raise TypeError("civilization description must be text")
        return cls(
            civilization_id=validate_id(raw_id, CivilizationId),
            name=name.strip(),
            description=description.strip(),
            tags=_text_tuple(data.get("tags", []), "tags"),
            research_preferences=_text_tuple(
                data.get("research_preferences", []),
                "research_preferences",
            ),
            content_hooks=_text_tuple(data.get("content_hooks", []), "content_hooks"),
        )


def load_civilizations(path: Path) -> tuple[CivilizationDefinition, ...]:
    """Load a deterministic ordered civilization content file with unique IDs."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read civilization definitions: {path}") from exc
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in civilization definitions: {path}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError("civilization definitions root must be a non-empty array")

    definitions: list[CivilizationDefinition] = []
    seen: set[CivilizationId] = set()
    for index, item in enumerate(data):
        if not isinstance(item, Mapping):
            raise TypeError(f"civilization definition {index} must be an object")
        definition = CivilizationDefinition.from_mapping(item)
        if definition.civilization_id in seen:
            raise ValueError(f"duplicate civilization id: {definition.civilization_id}")
        seen.add(definition.civilization_id)
        definitions.append(definition)
    return tuple(definitions)


def _text_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"civilization {field_name} must be an array")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"civilization {field_name} values must be non-empty text")
        normalized.append(item.strip())
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"civilization {field_name} values must be unique")
    return tuple(normalized)
