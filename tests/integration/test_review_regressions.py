# tests/integration/test_review_regressions.py
from civilization_clone.application.projection import project_event
from civilization_clone.domain.ids import CommandId, EventId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import GameStatus, RulesetRef
from civilization_clone.engine.commands import CommandEnvelope
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
        command_id=CommandId(f"review-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _three_player_engine() -> tuple[GameEngine, PlayerId, PlayerId, PlayerId]:
    engine = GameEngine.create(
        game_id=GameId("review-game"),
        seed=7331,
        ruleset=RulesetRef(RulesetId("poc-core"), "0.8.0"),
        map_config=MapGenerationConfig(radius=4, player_count=3, water_percent=0),
    )
    p1 = PlayerId("p1")
    p2 = PlayerId("p2")
    p3 = PlayerId("p3")
    assert engine.process(_command(1, engine, "JoinGame", p1, {"name": "One"})).accepted
    assert engine.process(_command(2, engine, "JoinGame", p2, {"name": "Two"})).accepted
    assert engine.process(_command(3, engine, "JoinGame", p3, {"name": "Three"})).accepted
    assert engine.process(_command(4, engine, "StartGame")).accepted
    return engine, p1, p2, p3


def test_active_player_concession_advances_to_next_living_player() -> None:
    engine, p1, p2, _ = _three_player_engine()
    assert engine.session.current_player_id == p1

    result = engine.process(_command(5, engine, "Concede", p1))

    assert result.accepted
    assert engine.session.status is GameStatus.ACTIVE
    assert engine.session.players[p1].eliminated
    assert engine.session.current_player_id == p2
    assert result.events[-1].event_type == "TurnStarted"
    assert result.events[-1].payload["player_id"] == p2
    assert engine.process(_command(6, engine, "EndTurn", p2)).accepted


def test_peace_offer_is_visible_only_to_bilateral_participants() -> None:
    engine, p1, p2, p3 = _three_player_engine()
    assert engine.process(
        _command(5, engine, "DeclareWar", p1, {"target_player_id": p2})
    ).accepted
    offered = engine.process(
        _command(6, engine, "OfferPeace", p1, {"target_player_id": p2})
    )
    assert offered.accepted
    event = offered.events[0]

    assert project_event(engine.session, event, p1) is not None
    assert project_event(engine.session, event, p2) is not None
    assert project_event(engine.session, event, p3) is None


def test_combat_event_owner_ids_survive_unit_removal_for_both_participants() -> None:
    engine, p1, p2, p3 = _three_player_engine()
    event = engine._emit(
        "UnitDamaged",
        {
            "unit_id": "destroyed-unit",
            "owner_id": p2,
            "attacker_owner_id": p1,
            "defender_owner_id": p2,
            "damage": 100,
            "destroyed": True,
        },
        CommandId("review-combat-event"),
    )

    assert project_event(engine.session, event, p1) is not None
    assert project_event(engine.session, event, p2) is not None
    assert project_event(engine.session, event, p3) is None
