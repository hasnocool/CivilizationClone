# tests/integration/test_civilization_effects.py
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.economy import settlement_yield, tile_yield
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.research import effective_research_cost
from civilization_clone.engine.session import GameEngine


def _command(
    index: int,
    engine: GameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"civilization-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _engine() -> tuple[GameEngine, PlayerId, PlayerId]:
    engine = GameEngine.create(
        game_id=GameId("civilization-effects"),
        seed=31337,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    river = PlayerId("river-player")
    horizon = PlayerId("horizon-player")
    assert engine.process(
        _command(
            1,
            engine,
            "JoinGame",
            river,
            {"name": "River", "civilization_id": "river_compact"},
        )
    ).accepted
    assert engine.process(
        _command(
            2,
            engine,
            "JoinGame",
            horizon,
            {"name": "Horizon", "civilization_id": "horizon_league"},
        )
    ).accepted
    assert engine.process(_command(3, engine, "StartGame")).accepted
    return engine, river, horizon


def test_civilization_starting_resources_are_applied_by_authoritative_join() -> None:
    engine, river, horizon = _engine()

    river_state = engine.session.players[river]
    horizon_state = engine.session.players[horizon]
    assert (river_state.gold, river_state.science, river_state.culture) == (4, 0, 1)
    assert (horizon_state.gold, horizon_state.science, horizon_state.culture) == (2, 2, 0)


def test_civilization_yield_modifier_uses_generic_effect_pipeline() -> None:
    engine, river, _ = _engine()
    founder = next(unit for unit in engine.session.units.values() if unit.owner_id == river)
    founded = engine.process(
        _command(4, engine, "FoundSettlement", river, {"unit_id": founder.unit_id})
    )
    assert founded.accepted

    settlement = next(
        item for item in engine.session.settlements.values() if item.owner_id == river
    )
    base = tile_yield(engine.session.world.tile(settlement.center))
    total = settlement_yield(engine.session, settlement)
    assert total.food == base.food + 1
    assert total.science == base.science + 1
    assert total.culture == base.culture + 1


def test_civilization_research_cost_modifier_is_integer_and_deterministic() -> None:
    engine, river, horizon = _engine()

    assert effective_research_cost(engine.session.players[river], "masonry") == 7
    assert effective_research_cost(engine.session.players[horizon], "masonry") == 6
    assert effective_research_cost(engine.session.players[horizon], "masonry") == 6
