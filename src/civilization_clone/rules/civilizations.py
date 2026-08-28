"""Strict data-driven civilization definition schema and loader."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

from civilization_clone.domain.economy import ModifierOperation, YieldModifier, YieldType
from civilization_clone.domain.ids import CivilizationId, validate_id

_ALLOWED_KEYS = frozenset(
    {
        "id",
        "name",
        "description",
        "tags",
        "starting_resources",
        "yield_modifiers",
        "research_cost_percent",
        "attack_strength_percent",
        "defense_strength_percent",
        "unique_units",
        "unique_buildings",
        "research_preferences",
        "content_hooks",
    }
)
_ALLOWED_STARTING_RESOURCES = frozenset({"gold", "science", "culture"})


@dataclass(frozen=True, slots=True)
class CivilizationDefinition:
    """Original POC civilization identity expressed entirely as content data."""

    civilization_id: CivilizationId
    name: str
    description: str
    tags: tuple[str, ...] = ()
    starting_resources: Mapping[str, int] = field(
        default_factory=lambda: MappingProxyType({})
    )
    yield_modifiers: tuple[YieldModifier, ...] = ()
    research_cost_percent: int = 0
    attack_strength_percent: int = 0
    defense_strength_percent: int = 0
    unique_units: tuple[str, ...] = ()
    unique_buildings: tuple[str, ...] = ()
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
        civilization_id = validate_id(raw_id, CivilizationId)
        return cls(
            civilization_id=civilization_id,
            name=name.strip(),
            description=description.strip(),
            tags=_text_tuple(data.get("tags", []), "tags"),
            starting_resources=_starting_resources(data.get("starting_resources", {})),
            yield_modifiers=_yield_modifiers(
                civilization_id,
                data.get("yield_modifiers", []),
            ),
            research_cost_percent=_percent(
                data.get("research_cost_percent", 0),
                "research_cost_percent",
            ),
            attack_strength_percent=_percent(
                data.get("attack_strength_percent", 0),
                "attack_strength_percent",
            ),
            defense_strength_percent=_percent(
                data.get("defense_strength_percent", 0),
                "defense_strength_percent",
            ),
            unique_units=_text_tuple(data.get("unique_units", []), "unique_units"),
            unique_buildings=_text_tuple(
                data.get("unique_buildings", []),
                "unique_buildings",
            ),
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


def _starting_resources(value: Any) -> Mapping[str, int]:
    if not isinstance(value, Mapping):
        raise TypeError("civilization starting_resources must be an object")
    unknown = set(value) - _ALLOWED_STARTING_RESOURCES
    if unknown:
        raise ValueError(f"unknown civilization starting resources: {sorted(unknown)}")
    normalized: dict[str, int] = {}
    for raw_key, raw_value in value.items():
        if not isinstance(raw_key, str):
            raise TypeError("civilization starting resource keys must be text")
        if not isinstance(raw_value, int) or isinstance(raw_value, bool) or raw_value < 0:
            raise ValueError("civilization starting resource values must be non-negative integers")
        normalized[raw_key] = raw_value
    return MappingProxyType(normalized)


def _yield_modifiers(
    civilization_id: CivilizationId,
    value: Any,
) -> tuple[YieldModifier, ...]:
    if not isinstance(value, list):
        raise TypeError("civilization yield_modifiers must be an array")
    modifiers: list[YieldModifier] = []
    for index, raw_modifier in enumerate(value):
        if not isinstance(raw_modifier, Mapping):
            raise TypeError("civilization yield modifier must be an object")
        unknown = set(raw_modifier) - {"yield_type", "operation", "value", "priority"}
        if unknown:
            raise ValueError(f"unknown civilization yield modifier fields: {sorted(unknown)}")
        raw_value = raw_modifier.get("value")
        raw_priority = raw_modifier.get("priority", 100)
        if not isinstance(raw_value, int) or isinstance(raw_value, bool):
            raise TypeError("civilization yield modifier value must be an integer")
        if not isinstance(raw_priority, int) or isinstance(raw_priority, bool):
            raise TypeError("civilization yield modifier priority must be an integer")
        try:
            yield_type = YieldType(str(raw_modifier["yield_type"]))
            operation = ModifierOperation(str(raw_modifier["operation"]))
        except KeyError as exc:
            raise ValueError("civilization yield modifier requires yield_type and operation") from exc
        except ValueError as exc:
            raise ValueError("civilization yield modifier uses an unsupported enum value") from exc
        modifiers.append(
            YieldModifier(
                source=f"civilization:{civilization_id}:{index}",
                yield_type=yield_type,
                operation=operation,
                value=raw_value,
                priority=raw_priority,
            )
        )
    return tuple(modifiers)


def _percent(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"civilization {field_name} must be an integer")
    if value < -90 or value > 200:
        raise ValueError(f"civilization {field_name} must be between -90 and 200")
    return value


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
