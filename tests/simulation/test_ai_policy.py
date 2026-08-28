from civilization_clone.ai.policy import SimpleBotPolicy


def test_bot_prefers_public_civilization_research_preference() -> None:
    view = {
        "game_id": "ai-policy-game",
        "state_version": 4,
        "status": "active",
        "active_player_id": "bot-1",
        "turn": 1,
        "viewer": {
            "player_id": "bot-1",
            "civilization_id": "horizon_league",
            "research": {
                "selected": None,
                "completed": [],
                "available": ["masonry", "surveying"],
                "preferences": ["surveying", "writing", "archery"],
            },
        },
        "units": [],
        "settlements": [],
        "diplomacy": [],
    }

    command = SimpleBotPolicy().choose_command(view, decision_number=0)

    assert command.command_type == "ChooseResearch"
    assert command.payload["technology_id"] == "surveying"
    assert command.player_id == "bot-1"


def test_bot_falls_back_deterministically_when_preference_is_unavailable() -> None:
    view = {
        "game_id": "ai-policy-game",
        "state_version": 5,
        "status": "active",
        "active_player_id": "bot-1",
        "turn": 2,
        "viewer": {
            "player_id": "bot-1",
            "research": {
                "selected": None,
                "completed": ["surveying"],
                "available": ["masonry", "bronze_work"],
                "preferences": ["writing"],
            },
        },
        "units": [],
        "settlements": [],
        "diplomacy": [],
    }

    command = SimpleBotPolicy().choose_command(view, decision_number=1)

    assert command.command_type == "ChooseResearch"
    assert command.payload["technology_id"] == "bronze_work"


def _trade_view(*, offered: int, requested: int, gold: int = 4) -> dict[str, object]:
    return {
        "game_id": "ai-trade-game",
        "state_version": 12,
        "status": "active",
        "active_player_id": "bot-2",
        "turn": 4,
        "viewer": {
            "player_id": "bot-2",
            "gold": gold,
            "research": {
                "selected": "masonry",
                "completed": [],
                "available": [],
                "preferences": [],
            },
        },
        "units": [],
        "settlements": [],
        "diplomacy": [
            {
                "other_player_id": "bot-1",
                "status": "peace",
                "pending_trade": {
                    "proposer_id": "bot-1",
                    "offered_gold": offered,
                    "requested_gold": requested,
                },
                "completed_trades": 0,
            }
        ],
    }


def test_bot_accepts_non_losing_affordable_trade() -> None:
    command = SimpleBotPolicy().choose_command(
        _trade_view(offered=2, requested=1),
        decision_number=7,
    )

    assert command.command_type == "AcceptTrade"
    assert command.payload == {"target_player_id": "bot-1"}


def test_bot_rejects_unfavorable_or_unaffordable_trade() -> None:
    unfavorable = SimpleBotPolicy().choose_command(
        _trade_view(offered=1, requested=2),
        decision_number=7,
    )
    unaffordable = SimpleBotPolicy().choose_command(
        _trade_view(offered=5, requested=5, gold=2),
        decision_number=7,
    )

    assert unfavorable.command_type == "RejectTrade"
    assert unaffordable.command_type == "RejectTrade"


def test_bot_proposes_one_equal_trade_before_late_war_behavior() -> None:
    view = _trade_view(offered=1, requested=1)
    relation = view["diplomacy"][0]  # type: ignore[index]
    assert isinstance(relation, dict)
    relation["pending_trade"] = None
    viewer = view["viewer"]
    assert isinstance(viewer, dict)
    viewer["research"]["selected"] = "masonry"  # type: ignore[index]

    command = SimpleBotPolicy().choose_command(view, decision_number=8)

    assert command.command_type == "OfferTrade"
    assert command.payload == {
        "target_player_id": "bot-1",
        "offered_gold": 1,
        "requested_gold": 1,
    }
