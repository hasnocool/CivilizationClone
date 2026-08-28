from civilization_clone.domain.gameplay import UnitDefinition
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.hexgrid import neighbors
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import GameEngine


def _command(
    engine: GameEngine,
    command_id: str,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(command_id),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _defender_damage(defender_civilization: str) -> int:
    engine = GameEngine.create(
        game_id=GameId("civilization-combat"),
        seed=4545,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    attacker_player = PlayerId("attacker")
    defender_player = PlayerId("defender")
    assert engine.process(
        _command(
            engine,
            "join-attacker",
            "JoinGame",
            attacker_player,
            {"name": "Attacker", "civilization_id": "horizon_league"},
        )
    ).accepted
    assert engine.process(
        _command(
            engine,
            "join-defender",
            "JoinGame",
            defender_player,
            {"name": "Defender", "civilization_id": defender_civilization},
        )
    ).accepted
    assert engine.process(_command(engine, "start", "StartGame")).accepted
    assert engine.process(
        _command(
            engine,
            "declare-war",
            "DeclareWar",
            attacker_player,
            {"target_player_id": defender_player},
        )
    ).accepted

    attacker = next(
        unit for unit in engine.session.units.values() if unit.owner_id == attacker_player
    )
    defender = next(
        unit for unit in engine.session.units.values() if unit.owner_id == defender_player
    )
    test_definition = UnitDefinition(
        "test_guard",
        movement=2,
        attack_strength=10,
        defense_strength=10,
    )
    attacker.definition = test_definition
    defender.definition = test_definition
    defender.position = next(
        coord
        for coord in neighbors(attacker.position)
        if coord in engine.session.world.tiles and engine.session.world.tile(coord).passable
    )

    result = engine.process(
        _command(
            engine,
            "same-attack-command",
            "AttackUnit",
            attacker_player,
            {"attacker_id": attacker.unit_id, "defender_id": defender.unit_id},
        )
    )
    assert result.accepted
    damage_event = next(
        event
        for event in result.events
        if event.event_type == "UnitDamaged" and event.payload.get("owner_id") == defender_player
    )
    return int(damage_event.payload["damage"])


def test_river_compact_generic_defense_bonus_reduces_identical_seeded_damage() -> None:
    horizon_damage = _defender_damage("horizon_league")
    river_damage = _defender_damage("river_compact")

    assert river_damage == horizon_damage - 1
