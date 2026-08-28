"""Typed identifiers for CivilizationClone domain objects."""

from collections.abc import Callable
from typing import NewType

GameId = NewType("GameId", str)
PlayerId = NewType("PlayerId", str)
CommandId = NewType("CommandId", str)
EventId = NewType("EventId", str)
UnitId = NewType("UnitId", str)
RulesetId = NewType("RulesetId", str)


def validate_id[T](value: str, constructor: Callable[[str], T]) -> T:
    """Validate an external identifier before constructing its domain type."""
    if not value or not value.strip():
        raise ValueError("identifier must not be blank")
    if any(character.isspace() for character in value):
        raise ValueError("identifier must not contain whitespace")
    return constructor(value)
