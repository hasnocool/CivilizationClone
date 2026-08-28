# tests/integration/test_settlement_economy.py
import logging

from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.economy import settlement_yield, tile_yield
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.research import available_technologies
from civilization_clone.engine.session import GameEngine


def command(
    index: int,
    engine: GameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"eco-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def setup_engine(logger: logging.Logger | None = None) -> tuple[GameEngine, PlayerId, PlayerId]:
    game_id = GameId("economy-game")
    engine = GameEngine.create(
        game_id=game_id,
        seed=505,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.1.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
        logger=logger,
    )
    p1 = PlayerId("p1")
    p2 = PlayerId("p2")
    assert engine.process(command(1, engine, "JoinGame", p1, {"name": "One"})).accepted
    assert engine.process(command(2, engine, "JoinGame", p2, {"name": "Two"})).accepted
    assert engine.process(command(3, engine, "StartGame")).accepted
    return engine, p1, p2


def found_first_settlement(engine: GameEngine, player: PlayerId, index: int = 4) -> str:
    unit = next(unit for unit in engine.session.units.values() if unit.owner_id == player)
    result = engine.process(
        command(index, engine, "FoundSettlement", player, {"unit_id": unit.unit_id})
    )
    assert result.accepted
    return next(
        settlement.settlement_id
        for settlement in engine.session.settlements.values()
        if settlement.owner_id == player
    )


def _ensure_research(engine: GameEngine, player: PlayerId, index: int) -> int:
    state = engine.session.players[player]
    if state.research.selected is not None:
        return index
    options = available_technologies(state)
    if not options:
        return index
    assert engine.process(
        command(index, engine, "ChooseResearch", player, {"technology_id": options[0]})
    ).accepted
    return index + 1


def advance_full_round(engine: GameEngine, p1: PlayerId, p2: PlayerId, index: int) -> int:
    index = _ensure_research(engine, p1, index)
    assert engine.process(command(index, engine, "EndTurn", p1)).accepted
    index += 1
    index = _ensure_research(engine, p2, index)
    assert engine.process(command(index, engine, "EndTurn", p2)).accepted
    return index + 1


def test_founding_consumes_founder_and_creates_controlled_territory() -> None:
    engine, p1, _ = setup_engine()
    founder = next(unit for unit in engine.session.units.values() if unit.owner_id == p1)
    position = founder.position
    settlement_id = found_first_settlement(engine, p1)
    settlement = engine.session.settlements[settlement_id]
    assert founder.unit_id not in engine.session.units
    assert settlement.center == position
    assert settlement.center in settlement.territory
    assert len(settlement.territory) >= 4


def test_population_limits_worked_tiles() -> None:
    engine, p1, _ = setup_engine()
    settlement_id = found_first_settlement(engine, p1)
    settlement = engine.session.settlements[settlement_id]
    candidates = sorted(
        coord
        for coord in settlement.territory
        if coord != settlement.center and engine.session.world.tile(coord).passable
    )
    first = engine.process(
        command(
            5,
            engine,
            "SetWorkedTile",
            p1,
            {"settlement_id": settlement_id, "q": candidates[0].q, "r": candidates[0].r},
        )
    )
    second = engine.process(
        command(
            6,
            engine,
            "SetWorkedTile",
            p1,
            {"settlement_id": settlement_id, "q": candidates[1].q, "r": candidates[1].r},
        )
    )
    assert first.accepted
    assert not second.accepted
    assert second.feedback[0].code == "WORKED_TILE_LIMIT"


def test_building_queue_completes_and_modifier_affects_yield() -> None:
    engine, p1, p2 = setup_engine()
    settlement_id = found_first_settlement(engine, p1)
    assert engine.process(
        command(
            5,
            engine,
            "QueueProduction",
            p1,
            {"settlement_id": settlement_id, "kind": "building", "definition_id": "granary"},
        )
    ).accepted
    index = 10
    for _ in range(8):
        if "granary" in engine.session.settlements[settlement_id].buildings:
            break
        index = advance_full_round(engine, p1, p2, index)
    settlement = engine.session.settlements[settlement_id]
    assert "granary" in settlement.buildings
    assert any(event.event_type == "BuildingCompleted" for event in engine.event_log)
    base_food = tile_yield(engine.session.world.tile(settlement.center)).food
    # River Compact contributes +1 Food and the granary contributes another +1.
    assert settlement_yield(engine.session, settlement).food == base_food + 2


def test_unit_production_spawns_deterministic_unit() -> None:
    engine, p1, p2 = setup_engine()
    settlement_id = found_first_settlement(engine, p1)
    assert engine.process(
        command(
            5,
            engine,
            "QueueProduction",
            p1,
            {"settlement_id": settlement_id, "kind": "unit", "definition_id": "scout"},
        )
    ).accepted
    index = 10
    for _ in range(10):
        if any(unit.owner_id == p1 for unit in engine.session.units.values()):
            break
        index = advance_full_round(engine, p1, p2, index)
    produced = [unit for unit in engine.session.units.values() if unit.owner_id == p1]
    assert len(produced) == 1
    assert produced[0].definition.definition_id == "scout"
    assert any(event.event_type == "UnitProduced" for event in engine.event_log)


def run_economy_script(logger: logging.Logger | None = None) -> GameEngine:
    engine, p1, p2 = setup_engine(logger)
    settlement_id = found_first_settlement(engine, p1)
    engine.process(
        command(
            5,
            engine,
            "QueueProduction",
            p1,
            {"settlement_id": settlement_id, "kind": "building", "definition_id": "workshop"},
        )
    )
    index = 20
    for _ in range(4):
        index = advance_full_round(engine, p1, p2, index)
    return engine


def test_economy_script_and_logging_are_deterministic() -> None:
    first = run_economy_script()
    second = run_economy_script()
    logger = logging.getLogger("civilization_clone.test.economy")
    logger.handlers = [logging.NullHandler()]
    logger.propagate = False
    with_logging = run_economy_script(logger)
    assert first.state_hash() == second.state_hash() == with_logging.state_hash()
    assert first.event_hash() == second.event_hash() == with_logging.event_hash()
