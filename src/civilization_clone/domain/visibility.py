"""Player-relative fog-of-war visibility states."""

from enum import StrEnum


class Visibility(StrEnum):
    """Player-relative visibility state for one tile."""

    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    VISIBLE = "visible"
