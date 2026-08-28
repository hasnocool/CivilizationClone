# tests/unit/test_state_hash.py
from dataclasses import dataclass

import pytest

from civilization_clone.engine.state_hash import canonical_json, state_hash


@dataclass(frozen=True)
class SampleState:
    turn: int
    labels: set[str]


def test_mapping_and_set_order_do_not_change_hash() -> None:
    first = {"b": 2, "a": {"z", "x", "y"}}
    second = {"a": {"y", "z", "x"}, "b": 2}

    assert canonical_json(first) == canonical_json(second)
    assert state_hash(first) == state_hash(second)


def test_dataclass_hash_changes_when_state_changes() -> None:
    first = SampleState(turn=4, labels={"known", "visible"})
    second = SampleState(turn=5, labels={"known", "visible"})

    assert state_hash(first) != state_hash(second)


def test_bytes_have_explicit_canonical_representation() -> None:
    assert canonical_json(b"\x00\xff") == '{"$bytes":"00ff"}'


def test_nan_is_rejected() -> None:
    with pytest.raises(ValueError):
        canonical_json(float("nan"))


def test_non_string_mapping_key_is_rejected() -> None:
    with pytest.raises(TypeError):
        canonical_json({1: "value"})
