# tests/replay/test_replay_corpus.py
from __future__ import annotations

import json
from pathlib import Path

from civilization_clone.domain.ids import CommandId, GameId, PlayerId, RulesetId
from civilization_clone.domain.state import RulesetRef
from civilization_clone.engine.advanced import AdvancedGameEngine
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.persistence.replay import verify_replay

_CORPUS = Path(__file__).parents[1] / "corpus" / "replay_cases.json"


def test_replay_corpus_matches_state_and_event_hashes() -> None:
    cases = json.loads(_CORPUS.read_text(encoding="utf-8"))
    assert isinstance(cases, list) and cases
    for case_index, case in enumerate(cases):
        game_id = GameId(f"corpus-{case['name']}")
        engine = AdvancedGameEngine.create(
            game_id=game_id,
            seed=int(case["seed"]),
            ruleset=RulesetRef(RulesetId("poc-core"), "1.0.0"),
            map_config=MapGenerationConfig(
                radius=4,
                player_count=int(case["player_count"]),
                water_percent=0,
            ),
        )
        accepted: list[CommandEnvelope] = []
        for command_index, item in enumerate(case["commands"]):
            raw_player = item.get("player")
            command = CommandEnvelope.create(
                command_id=CommandId(f"corpus-{case_index}-{command_index}"),
                game_id=game_id,
                command_type=str(item["type"]),
                player_id=PlayerId(str(raw_player)) if raw_player is not None else None,
                payload=item.get("payload", {}),
            )
            result = engine.process(command)
            assert result.accepted, (case["name"], command.command_type, result.feedback)
            accepted.append(command)

        report = verify_replay(engine, accepted)
        assert report.matched, case["name"]
        assert report.command_count == len(accepted)
