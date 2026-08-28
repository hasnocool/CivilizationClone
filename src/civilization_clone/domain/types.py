"""JSON-compatible value types used at stable engine boundaries."""

from collections.abc import Mapping
from types import MappingProxyType


type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type FrozenJsonValue = JsonScalar | tuple[FrozenJsonValue, ...] | Mapping[str, FrozenJsonValue]


def freeze_json(value: JsonValue | FrozenJsonValue) -> FrozenJsonValue:
    """Recursively freeze JSON-compatible data for immutable envelopes."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json(item) for item in value)
    return value


def freeze_payload(
    payload: Mapping[str, JsonValue | FrozenJsonValue],
) -> Mapping[str, FrozenJsonValue]:
    """Copy and deeply freeze a command/event payload."""
    return MappingProxyType({key: freeze_json(value) for key, value in payload.items()})
