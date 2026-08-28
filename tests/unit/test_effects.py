# tests/unit/test_effects.py
from civilization_clone.domain.economy import (
    ModifierOperation,
    YieldBundle,
    YieldModifier,
    YieldType,
)
from civilization_clone.engine.effects import apply_yield_modifiers


def test_yield_modifier_pipeline_uses_stable_priority_order() -> None:
    base = YieldBundle(food=10, production=4)
    modifiers = [
        YieldModifier("late", YieldType.FOOD, ModifierOperation.PERCENT, 50, priority=20),
        YieldModifier("early", YieldType.FOOD, ModifierOperation.FLAT, 2, priority=10),
        YieldModifier("prod", YieldType.PRODUCTION, ModifierOperation.FLAT, 3),
    ]
    first = apply_yield_modifiers(base, modifiers)
    second = apply_yield_modifiers(base, reversed(modifiers))
    assert first == second
    assert first.food == 18
    assert first.production == 7


def test_percentage_reduction_never_creates_negative_yields() -> None:
    result = apply_yield_modifiers(
        YieldBundle(food=3),
        [YieldModifier("penalty", YieldType.FOOD, ModifierOperation.PERCENT, -100)],
    )
    assert result.food == 0
