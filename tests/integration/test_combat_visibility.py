from civilization_clone.domain.gameplay import UnitDefinition
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.domain.visibility import Visibility
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.hexgrid import distance
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


def test_attack_rejects_hidden_defender_even_when_id_and_range_are_guessed() -> None:
    engine = GameEngine.create(
        game_id=GameId("hidden-target-game"),
        seed=8181,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    assert engine.process(_command(engine, "join-1", "JoinGame", first, {"name": "One"})).accepted
    assert engine.process(_command(engine, "join-2", "JoinGame", second, {"name": "Two"})).accepted
    assert engine.process(_command(engine, "start", "StartGame")).accepted
    assert engine.process(
        _command(
            engine,
            "war",
            "DeclareWar",
            first,
            {"target_player_id": second},
        )
    ).accepted

    attacker = next(unit for unit in engine.session.units.values() if unit.owner_id == first)
    defender = next(unit for unit in engine.session.units.values() if unit.owner_id == second)
    attacker.definition = UnitDefinition(
        "test_ranged_unit",
        movement=2,
        vision_radius=1,
        attack_strength=6,
        defense_strength=3,
        ranged_range=2,
    )
    hidden_destination = next(
        coord
        for coord, tile in sorted(engine.session.world.tiles.items())
        if tile.passable
        and distance(attacker.position, coord) == 2
        and engine.session.players[first].visibility.get(coord, Visibility.UNKNOWN)
        is not Visibility.VISIBLE
    )
    defender.position = hidden_destination

    result = engine.process(
        _command(
            engine,
            "guessed-hidden-attack",
            "AttackUnit",
            first,
            {"attacker_id": attacker.unit_id, "defender_id": defender.unit_id},
        )
    )

    assert not result.accepted
    assert result.feedback[0].code == "ATTACK_REJECTED"
    assert result.feedback[0].context["reason"] == "target_not_visible"
