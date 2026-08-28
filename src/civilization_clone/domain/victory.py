"""Victory-condition primitives."""

from enum import StrEnum


class VictoryKind(StrEnum):
    CONQUEST = "conquest"
    SCORE = "score"
