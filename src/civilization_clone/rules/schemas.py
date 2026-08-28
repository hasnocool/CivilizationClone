"""Strict v0.1 ruleset manifest schema."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from civilization_clone.domain.ids import RulesetId, validate_id

_RULESET_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")
_ALLOWED_KEYS = frozenset({"schema_version", "id", "version", "name", "description", "metadata"})


@dataclass(frozen=True, slots=True)
class RulesetManifest:
    """Versioned metadata required to identify a data-driven ruleset."""

    schema_version: int
    ruleset_id: RulesetId
    version: str
    name: str
    description: str = ""
    metadata: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RulesetManifest":
        unknown = set(data) - _ALLOWED_KEYS
        if unknown:
            raise ValueError(f"unknown ruleset manifest fields: {sorted(unknown)}")

        schema_version = data.get("schema_version")
        if type(schema_version) is not int or schema_version != 1:
            raise ValueError("unsupported ruleset schema_version; expected integer 1")

        raw_id = data.get("id")
        version = data.get("version")
        name = data.get("name")
        description = data.get("description", "")
        metadata = data.get("metadata", {})

        if not isinstance(raw_id, str):
            raise TypeError("ruleset id must be a string")
        if not isinstance(version, str) or not _RULESET_VERSION.fullmatch(version):
            raise ValueError("ruleset version must be semantic version text such as 0.1.0")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("ruleset name must be a non-empty string")
        if not isinstance(description, str):
            raise TypeError("ruleset description must be a string")
        if not isinstance(metadata, Mapping):
            raise TypeError("ruleset metadata must be an object")

        normalized_metadata: dict[str, str] = {}
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("ruleset metadata keys and values must be strings")
            normalized_metadata[key] = value

        return cls(
            schema_version=schema_version,
            ruleset_id=validate_id(raw_id, RulesetId),
            version=version,
            name=name.strip(),
            description=description,
            metadata=MappingProxyType(normalized_metadata),
        )
