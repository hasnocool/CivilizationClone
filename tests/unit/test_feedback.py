# tests/unit/test_feedback.py
from types import MappingProxyType

import pytest

from civilization_clone.domain.feedback import FeedbackSeverity, UserFeedback


def test_feedback_is_immutable_and_safe_shape() -> None:
    feedback = UserFeedback(
        code="MOVE_REJECTED",
        message="That unit cannot move there.",
        severity=FeedbackSeverity.WARNING,
        context={"reason": "blocked"},
    )
    assert feedback.context == MappingProxyType({"reason": "blocked"})
    with pytest.raises(TypeError):
        feedback.context["reason"] = "changed"  # type: ignore[index]


@pytest.mark.parametrize("code", ["", "BAD CODE", " BAD"])
def test_feedback_rejects_invalid_codes(code: str) -> None:
    with pytest.raises(ValueError):
        UserFeedback(code=code, message="message")
