"""Original deterministic POC combat validation and resolution."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.domain.gameplay import GameSession, UnitState
from civilization_clone.domain.ids import CommandId, PlayerId, UnitId
from civilization_clone.domain.map import TerrainType
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.diplomacy import at_war
from civilization_clone.engine.hexgrid import distance
from civilization_clone.engine.rng import RngFactory
from civilization_clone.rules.poc import POC_CIVILIZATIONS_BY_ID


@dataclass(frozen=True, slots=True)
class CombatResolution:
    """Deterministic result of one legal abstract game combat action."""

    attacker_damage: int
    defender_damage: int
    attacker_destroyed: bool
    defender_destroyed: bool


def validate_attack(
    session: GameSession,
    player_id: PlayerId,
    attacker_id: UnitId,
    defender_id: UnitId,
) -> str | None:
    """Return a stable rejection reason, or None for a legal game attack."""
    if session.current_player_id != player_id:
        return "not_active_player"
    attacker = session.units.get(attacker_id)
    if attacker is None:
        return "unit_not_found"
    if attacker.owner_id != player_id:
        return "not_owner"
    if attacker.movement_remaining <= 0:
        return "no_actions_remaining"

    defender = session.units.get(defender_id)
    if defender is None:
        return "target_unavailable"
    if defender.owner_id == player_id:
        return "friendly_target"
    if session.players[player_id].visibility.get(defender.position) is not Visibility.VISIBLE:
        return "target_unavailable"
    if not at_war(session, attacker.owner_id, defender.owner_id):
        return "not_at_war"
    attack_range = max(1, attacker.definition.ranged_range)
    if distance(attacker.position, defender.position) > attack_range:
        return "target_out_of_range"
    return None


def resolve_attack(
    session: GameSession,
    attacker_id: UnitId,
    defender_id: UnitId,
    command_id: CommandId,
) -> CombatResolution:
    """Resolve one legal abstract action using a command-scoped deterministic RNG stream."""
    attacker = session.units[attacker_id]
    defender = session.units[defender_id]
    rng = RngFactory(session.seed).stream(
        f"combat:{session.turn}:{attacker_id}:{defender_id}:{command_id}"
    )

    attacker_strength = _modified_strength(
        session,
        attacker.owner_id,
        attacker.definition.attack_strength,
        attack=True,
    )
    defender_strength = _modified_strength(
        session,
        defender.owner_id,
        defender.definition.defense_strength,
        attack=False,
    )
    defender_bonus = _terrain_defense(session, defender)
    variation = rng.randint(-3, 3)
    defender_damage = max(
        5,
        20 + attacker_strength - defender_strength - defender_bonus + variation,
    )
    defender.hit_points = max(0, defender.hit_points - defender_damage)

    attacker_damage = 0
    if defender.hit_points > 0 and attacker.definition.ranged_range == 0:
        counter_variation = rng.randint(-2, 2)
        counter_attack = _modified_strength(
            session,
            defender.owner_id,
            defender.definition.attack_strength,
            attack=True,
        )
        attacker_defense = _modified_strength(
            session,
            attacker.owner_id,
            attacker.definition.defense_strength,
            attack=False,
        )
        attacker_damage = max(
            3,
            10 + counter_attack - attacker_defense + counter_variation,
        )
        attacker.hit_points = max(0, attacker.hit_points - attacker_damage)

    attacker.movement_remaining = 0
    attacker_destroyed = attacker.hit_points == 0
    defender_destroyed = defender.hit_points == 0
    if attacker_destroyed:
        del session.units[attacker_id]
    if defender_destroyed:
        del session.units[defender_id]

    return CombatResolution(
        attacker_damage=attacker_damage,
        defender_damage=defender_damage,
        attacker_destroyed=attacker_destroyed,
        defender_destroyed=defender_destroyed,
    )


def _modified_strength(
    session: GameSession,
    player_id: PlayerId,
    base_strength: int,
    *,
    attack: bool,
) -> int:
    civilization = POC_CIVILIZATIONS_BY_ID.get(session.players[player_id].civilization_id)
    if civilization is None:
        return base_strength
    percent = (
        civilization.attack_strength_percent
        if attack
        else civilization.defense_strength_percent
    )
    return max(0, (base_strength * (100 + percent) + 50) // 100)


def _terrain_defense(session: GameSession, defender: UnitState) -> int:
    terrain = session.world.tile(defender.position).terrain
    return 3 if terrain is TerrainType.HILLS else 0
