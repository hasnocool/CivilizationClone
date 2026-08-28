# tests/integration/test_strategic_systems.py
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import GameStatus, RulesetRef
from civilization_clone.domain.strategy import DiplomacyStatus, VictoryType
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.diplomacy import relationship_key
from civilization_clone.engine.hexgrid import neighbors
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.session import GameEngine


def _command(
    index: int,
    engine: GameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"strategic-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _setup_engine() -> tuple[GameEngine, PlayerId, PlayerId]:
    engine = GameEngine.create(
        game_id=GameId("strategic-game"),
        seed=991,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.5.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    assert engine.process(_command(1, engine, "JoinGame", first, {"name": "One"})).accepted
    assert engine.process(_command(2, engine, "JoinGame", second, {"name": "Two"})).accepted
    assert engine.process(_command(3, engine, "StartGame")).accepted
    return engine, first, second


def test_end_turn_requires_mandatory_research_choice() -> None:
    engine, first, _ = _setup_engine()
    before_hash = engine.state_hash()
    before_events = len(engine.event_log)

    result = engine.process(_command(4, engine, "EndTurn", first))

    assert not result.accepted
    assert result.feedback[0].code == "MANDATORY_CHOICE_REQUIRED"
    assert result.feedback[0].context["choice"] == "research"
    assert engine.state_hash() == before_hash
    assert len(engine.event_log) == before_events


def test_research_completes_from_accumulated_science() -> None:
    engine, first, _ = _setup_engine()
    selected = engine.process(
        _command(4, engine, "ChooseResearch", first, {"technology_id": "surveying"})
    )
    assert selected.accepted

    engine.session.players[first].science = 5
    ended = engine.process(_command(5, engine, "EndTurn", first))

    assert ended.accepted
    assert "surveying" in engine.session.players[first].research.completed
    assert any(event.event_type == "TechnologyCompleted" for event in ended.events)


def test_war_peace_round_trip_uses_bilateral_relationship() -> None:
    engine, first, second = _setup_engine()
    target_second = {"target_player_id": second}
    target_first = {"target_player_id": first}

    assert engine.process(_command(4, engine, "DeclareWar", first, target_second)).accepted
    relationship = engine.session.diplomacy[relationship_key(first, second)]
    assert relationship.status is DiplomacyStatus.WAR

    assert engine.process(
        _command(5, engine, "ChooseResearch", first, {"technology_id": "surveying"})
    ).accepted
    assert engine.process(_command(6, engine, "EndTurn", first)).accepted
    assert engine.process(_command(7, engine, "OfferPeace", second, target_first)).accepted
    assert engine.process(
        _command(8, engine, "ChooseResearch", second, {"technology_id": "masonry"})
    ).accepted
    assert engine.process(_command(9, engine, "EndTurn", second)).accepted
    assert engine.process(_command(10, engine, "AcceptPeace", first, target_second)).accepted
    assert relationship.status is DiplomacyStatus.PEACE


def _combat_script() -> GameEngine:
    engine, first, second = _setup_engine()
    assert engine.process(
        _command(4, engine, "DeclareWar", first, {"target_player_id": second})
    ).accepted

    attacker = next(unit for unit in engine.session.units.values() if unit.owner_id == first)
    defender = next(unit for unit in engine.session.units.values() if unit.owner_id == second)
    destination = next(
        coord
        for coord in neighbors(attacker.position)
        if coord in engine.session.world.tiles and engine.session.world.tiles[coord].passable
    )
    defender.position = destination

    result = engine.process(
        _command(
            5,
            engine,
            "AttackUnit",
            first,
            {"attacker_id": attacker.unit_id, "defender_id": defender.unit_id},
        )
    )
    assert result.accepted
    assert any(event.event_type == "UnitAttacked" for event in result.events)
    return engine


def test_combat_is_deterministic_for_same_seed_and_command_stream() -> None:
    first = _combat_script()
    second = _combat_script()
    assert first.state_hash() == second.state_hash()
    assert first.event_hash() == second.event_hash()


def test_concession_finishes_match_with_conquest_victory() -> None:
    engine, first, second = _setup_engine()
    result = engine.process(_command(4, engine, "Concede", second))

    assert result.accepted
    assert engine.session.status is GameStatus.FINISHED
    assert engine.session.victory is not None
    assert engine.session.victory.winner_id == first
    assert engine.session.victory.victory_type is VictoryType.CONQUEST
    assert any(event.event_type == "VictoryAchieved" for event in result.events)
