from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.domain.strategy import DiplomacyStatus
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.diplomacy import relationship_key
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
        command_id=CommandId(f"reject-peace-{index}"),
        game_id=engine.session.game_id,
        command_type=kind,
        player_id=player,
        payload=payload or {},  # type: ignore[arg-type]
    )


def test_reject_peace_clears_offer_but_keeps_war() -> None:
    engine = GameEngine.create(
        game_id=GameId("reject-peace-game"),
        seed=912,
        ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
        map_config=MapGenerationConfig(radius=4, player_count=2, water_percent=0),
    )
    first = PlayerId("p1")
    second = PlayerId("p2")
    assert engine.process(_command(1, engine, "JoinGame", first, {"name": "One"})).accepted
    assert engine.process(_command(2, engine, "JoinGame", second, {"name": "Two"})).accepted
    assert engine.process(_command(3, engine, "StartGame")).accepted
    assert engine.process(
        _command(4, engine, "DeclareWar", first, {"target_player_id": second})
    ).accepted
    assert engine.process(
        _command(5, engine, "ChooseResearch", first, {"technology_id": "surveying"})
    ).accepted
    assert engine.process(_command(6, engine, "EndTurn", first)).accepted
    offered = engine.process(
        _command(7, engine, "OfferPeace", second, {"target_player_id": first})
    )
    assert offered.accepted
    relationship = engine.session.diplomacy[relationship_key(first, second)]
    assert relationship.pending_peace_from == second

    assert engine.process(
        _command(8, engine, "ChooseResearch", second, {"technology_id": "masonry"})
    ).accepted
    assert engine.process(_command(9, engine, "EndTurn", second)).accepted
    rejected = engine.process(
        _command(10, engine, "RejectPeace", first, {"target_player_id": second})
    )

    assert rejected.accepted
    assert relationship.status is DiplomacyStatus.WAR
    assert relationship.pending_peace_from is None
    assert [event.event_type for event in rejected.events] == ["PeaceRejected"]
