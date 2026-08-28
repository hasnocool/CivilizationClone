"""Safe user-facing feedback primitives."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType


class FeedbackSeverity(StrEnum):
    """Severity appropriate for display in a client notification surface."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class UserFeedback:
    """Typed message safe for direct client presentation."""

    code: str
    message: str
    severity: FeedbackSeverity = FeedbackSeverity.INFO
    context: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.code or any(character.isspace() for character in self.code):
            raise ValueError("feedback code must be non-empty and contain no whitespace")
        if not self.message.strip():
            raise ValueError("feedback message must not be blank")
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))
