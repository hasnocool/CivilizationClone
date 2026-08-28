from civilization_clone.application.projection import project_event, project_game
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.advanced import AdvancedGameEngine
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.diplomacy import relationship_key
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.persistence.codec import engine_from_document, engine_to_document
from civilization_clone.persistence.replay import verify_replay


def _command(
    index: int,
    engine: AdvancedGameEngine,
    kind: str,
    player: PlayerId | None = None,
    payload: dict[str, object] | None = None,
) -> CommandEnvelope:
    return CommandEnvelope.create(
        command_id=CommandId(f"trade-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def _started_engine(*, players: int = 2) -> tuple[AdvancedGameEngine, list[PlayerId]]:
    engine = AdvancedGameEngine.create(
        game_id=GameId("trade-game"),
        seed=431,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=players, water_percent=0),
    )
    player_ids = [PlayerId(f"p{index + 1}") for index in range(players)]
    for index, player_id in enumerate(player_ids, start=1):
        assert engine.process(
            _command(index, engine, "JoinGame", player_id, {"name": str(player_id)})
        ).accepted
    assert engine.process(_command(players + 1, engine, "StartGame")).accepted
    return engine, player_ids


def test_trade_acceptance_is_atomic_idempotent_and_projected_to_participants() -> None:
    engine, (first, second) = _started_engine()
    first_start = engine.session.players[first].gold
    second_start = engine.session.players[second].gold

    offered = engine.process(
        _command(
            10,
            engine,
            "OfferTrade",
            first,
            {"target_player_id": second, "offered_gold": 2, "requested_gold": 1},
        )
    )
    assert offered.accepted
    assert [event.event_type for event in offered.events] == ["TradeOffered"]
    relationship = engine.session.diplomacy[relationship_key(first, second)]
    assert relationship.pending_trade is not None
    assert relationship.pending_trade.proposer_id == first

    first_view = project_game(engine.session, first)
    second_view = project_game(engine.session, second)
    assert first_view["diplomacy"][0]["pending_trade"] == {
        "proposer_id": "p1",
        "offered_gold": 2,
        "requested_gold": 1,
    }
    assert second_view["diplomacy"][0]["pending_trade"] == first_view["diplomacy"][0][
        "pending_trade"
    ]

    assert engine.process(
        _command(11, engine, "ChooseResearch", first, {"technology_id": "surveying"})
    ).accepted
    assert engine.process(_command(12, engine, "EndTurn", first)).accepted

    accept_command = _command(
        13,
        engine,
        "AcceptTrade",
        second,
        {"target_player_id": first},
    )
    accepted = engine.process(accept_command)
    assert accepted.accepted
    assert [event.event_type for event in accepted.events] == ["TradeAccepted"]
    assert engine.session.players[first].gold == first_start - 2 + 1
    assert engine.session.players[second].gold == second_start - 1 + 2
    assert relationship.pending_trade is None
    assert relationship.completed_trades == 1
    assert relationship.last_trade_turn == engine.session.turn

    first_after = engine.session.players[first].gold
    second_after = engine.session.players[second].gold
    retried = engine.process(accept_command)
    assert retried == accepted
    assert engine.session.players[first].gold == first_after
    assert engine.session.players[second].gold == second_after


def test_rejected_trade_response_does_not_create_or_mutate_diplomacy_state() -> None:
    engine, (first, _second) = _started_engine()
    before_hash = engine.state_hash()
    before_diplomacy = tuple(sorted(engine.session.diplomacy))

    rejected = engine.process(
        _command(
            14,
            engine,
            "AcceptTrade",
            first,
            {"target_player_id": "ghost"},
        )
    )

    assert not rejected.accepted
    assert rejected.feedback[0].code == "TRADE_REJECTED"
    assert rejected.feedback[0].context["reason"] == "player_not_found"
    assert engine.state_hash() == before_hash
    assert tuple(sorted(engine.session.diplomacy)) == before_diplomacy


def test_trade_event_and_terms_are_hidden_from_uninvolved_player() -> None:
    engine, players = _started_engine(players=3)
    first, second, observer = players
    result = engine.process(
        _command(
            20,
            engine,
            "OfferTrade",
            first,
            {"target_player_id": second, "offered_gold": 1, "requested_gold": 1},
        )
    )
    assert result.accepted
    event = result.events[0]

    assert project_event(engine.session, event, first) is not None
    assert project_event(engine.session, event, second) is not None
    assert project_event(engine.session, event, observer) is None
    observer_view = project_game(engine.session, observer)
    assert all(
        relation["other_player_id"] in {"p1", "p2"}
        and relation["pending_trade"] is None
        for relation in observer_view["diplomacy"]
    )


def test_declaring_war_cancels_pending_trade_and_journals_reason() -> None:
    engine, (first, second) = _started_engine()
    assert engine.process(
        _command(
            30,
            engine,
            "OfferTrade",
            first,
            {"target_player_id": second, "offered_gold": 1, "requested_gold": 1},
        )
    ).accepted

    war = engine.process(
        _command(31, engine, "DeclareWar", first, {"target_player_id": second})
    )
    assert war.accepted
    assert [event.event_type for event in war.events] == ["WarDeclared", "TradeCancelled"]
    assert war.events[-1].payload["reason"] == "war_declared"
    assert engine.session.diplomacy[relationship_key(first, second)].pending_trade is None


def test_trade_state_round_trips_through_save_codec() -> None:
    engine, (first, second) = _started_engine()
    assert engine.process(
        _command(
            40,
            engine,
            "OfferTrade",
            first,
            {"target_player_id": second, "offered_gold": 1, "requested_gold": 1},
        )
    ).accepted

    document = engine_to_document(engine)
    assert document["save_version"] == 3
    restored = engine_from_document(document)

    assert isinstance(restored, AdvancedGameEngine)
    assert restored.state_hash() == engine.state_hash()
    assert restored.event_hash() == engine.event_hash()
    restored_offer = restored.session.diplomacy[relationship_key(first, second)].pending_trade
    assert restored_offer is not None
    assert restored_offer.proposer_id == first
    assert restored_offer.offered_gold == 1
    assert restored_offer.requested_gold == 1


def test_replay_reconstructs_trade_commands_and_final_hashes() -> None:
    engine = AdvancedGameEngine.create(
        game_id=GameId("trade-replay"),
        seed=812,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    commands = [
        _command(50, engine, "JoinGame", first, {"name": "One"}),
        _command(51, engine, "JoinGame", second, {"name": "Two"}),
        _command(52, engine, "StartGame"),
        _command(
            53,
            engine,
            "OfferTrade",
            first,
            {"target_player_id": second, "offered_gold": 1, "requested_gold": 1},
        ),
        _command(54, engine, "ChooseResearch", first, {"technology_id": "surveying"}),
        _command(55, engine, "EndTurn", first),
        _command(56, engine, "AcceptTrade", second, {"target_player_id": first}),
    ]
    for command in commands:
        assert engine.process(command).accepted

    report = verify_replay(engine, commands)
    assert report.matched
    assert report.command_count == len(commands)
