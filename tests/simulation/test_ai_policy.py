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
