"""Original deterministic proof-of-concept combat resolution."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import UnitId
from civilization_clone.engine.hexgrid import distance
from civilization_clone.engine.rng import RngFactory


@dataclass(frozen=True, slots=True)
class CombatResolution:
    attacker_id: UnitId
    defender_id: UnitId
    damage: int
    defender_destroyed: bool


def resolve_attack(
    session: GameSession,
    attacker_id: UnitId,
    defender_id: UnitId,
    context: str,
) -> CombatResolution:
    """Resolve one adjacent attack using a context-isolated deterministic RNG stream."""
    attacker = session.units[attacker_id]
    defender = session.units[defender_id]
    if distance(attacker.position, defender.position) != 1:
        raise ValueError("combatants must be adjacent")
    rng = RngFactory(session.seed).stream(f"combat:{context}")
    variation = rng.randint(-5, 5)
    strength_delta = attacker.definition.combat_strength - defender.definition.combat_strength
    damage = max(10, min(60, 30 + strength_delta + variation))
    defender.hit_points = max(0, defender.hit_points - damage)
    attacker.movement_remaining = 0
    destroyed = defender.hit_points == 0
    if destroyed:
        del session.units[defender_id]
    return CombatResolution(attacker_id, defender_id, damage, destroyed)
