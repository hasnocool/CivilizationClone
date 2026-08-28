"""Generic deterministic yield-modifier application pipeline."""

from collections.abc import Iterable

from civilization_clone.domain.economy import ModifierOperation, YieldBundle, YieldModifier


def apply_yield_modifiers(
    base: YieldBundle,
    modifiers: Iterable[YieldModifier],
) -> YieldBundle:
    """Apply modifiers in a stable explicit order using integer arithmetic."""
    result = base
    ordered = sorted(
        modifiers,
        key=lambda modifier: (
            modifier.priority,
            modifier.source,
            modifier.yield_type.value,
            modifier.operation.value,
            modifier.value,
        ),
    )
    for modifier in ordered:
        current = result.value(modifier.yield_type)
        if modifier.operation is ModifierOperation.FLAT:
            updated = max(0, current + modifier.value)
        else:
            updated = max(0, current * (100 + modifier.value) // 100)
        result = result.with_value(modifier.yield_type, updated)
    return result
