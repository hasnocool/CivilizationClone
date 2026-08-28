"""Independent deterministic replay from accepted public command transcripts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from civilization_clone.domain.gameplay import GameSession
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.event_log import EventLog
from civilization_clone.engine.session import GameEngine


class ReplayVerificationError(RuntimeError):
    """Raised at the first detected deterministic replay divergence."""


@dataclass(frozen=True, slots=True)
class ReplayReport:
    """Stable replay verification result for diagnostics and release QA."""

    command_count: int
    live_state_hash: str
    replay_state_hash: str
    live_event_hash: str
    replay_event_hash: str

    @property
    def matched(self) -> bool:
        return (
            self.live_state_hash == self.replay_state_hash
            and self.live_event_hash == self.replay_event_hash
        )


def verify_replay(
    engine: GameEngine,
    commands: Iterable[CommandEnvelope],
) -> ReplayReport:
    """Rebuild a game from its immutable map origin and accepted command transcript."""
    transcript = tuple(commands)
    initial_events = tuple(
        event for event in engine.event_log if event.causation_command_id is None
    )
    journal = EventLog(engine.session.game_id)
    journal.extend(initial_events)
    replay = GameEngine(
        session=GameSession(
            game_id=engine.session.game_id,
            ruleset=engine.session.ruleset,
            seed=engine.session.seed,
            world=engine.session.world,
            max_turns=engine.session.max_turns,
        ),
        event_log=journal,
    )

    for index, command in enumerate(transcript):
        result = replay.process(command)
        if not result.accepted:
            code = result.feedback[0].code if result.feedback else "COMMAND_REJECTED"
            raise ReplayVerificationError(
                f"replay rejected accepted command {index} ({command.command_id}): {code}"
            )

    report = ReplayReport(
        command_count=len(transcript),
        live_state_hash=engine.state_hash(),
        replay_state_hash=replay.state_hash(),
        live_event_hash=engine.event_hash(),
        replay_event_hash=replay.event_hash(),
    )
    if not report.matched:
        raise ReplayVerificationError(
            "replay final hashes diverged: "
            f"state={report.live_state_hash}/{report.replay_state_hash} "
            f"events={report.live_event_hash}/{report.replay_event_hash}"
        )
    return report


def command_to_data(command: CommandEnvelope) -> dict[str, Any]:
    """Serialize one immutable command for durable replay storage."""
    return {
        "command_id": str(command.command_id),
        "game_id": str(command.game_id),
        "command_type": command.command_type,
        "player_id": str(command.player_id) if command.player_id is not None else None,
        "expected_state_version": command.expected_state_version,
        "payload": _plain(command.payload),
        "client_timestamp": command.client_timestamp,
    }


def command_from_data(data: Mapping[str, Any]) -> CommandEnvelope:
    """Restore one replay command from durable JSON-compatible data."""
    raw_player_id = data.get("player_id")
    payload = data.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ValueError("replay command payload must be an object")
    return CommandEnvelope.create(
        command_id=CommandId(str(data["command_id"])),
        game_id=GameId(str(data["game_id"])),
        command_type=str(data["command_type"]),
        player_id=PlayerId(str(raw_player_id)) if raw_player_id is not None else None,
        expected_state_version=(
            int(data["expected_state_version"])
            if data.get("expected_state_version") is not None
            else None
        ),
        payload=dict(payload),  # type: ignore[arg-type]
        client_timestamp=(
            str(data["client_timestamp"]) if data.get("client_timestamp") is not None else None
        ),
    )


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value
