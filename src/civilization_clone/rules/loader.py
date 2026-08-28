"""File-system ruleset loading with strict schema validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from civilization_clone.rules.schemas import RulesetManifest


class RulesetLoadError(ValueError):
    """Raised when a ruleset manifest cannot be parsed or validated."""


@dataclass(frozen=True, slots=True)
class RulesetLoader:
    """Loads versioned ruleset manifests from JSON files."""

    def load(self, path: Path) -> RulesetManifest:
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RulesetLoadError(f"unable to read ruleset manifest: {path}") from exc

        try:
            data: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RulesetLoadError(f"invalid JSON in ruleset manifest: {path}") from exc

        if not isinstance(data, dict):
            raise RulesetLoadError("ruleset manifest root must be an object")

        try:
            return RulesetManifest.from_mapping(data)
        except (TypeError, ValueError) as exc:
            raise RulesetLoadError(str(exc)) from exc
