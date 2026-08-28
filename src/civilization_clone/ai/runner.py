"""Headless deterministic bot-vs-bot match automation and simulation metrics."""

from __future__ import annotations

from dataclasses import dataclass

from civilization_clone.ai.policy import BotPolicy, SimpleBotPolicy
from civilization_clone.application.manager import GameManager
from civilization_clone.application.projection import project_game
from civilization_clone.domain.ids import CommandId, GameId, PlayerId
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.rules.poc import POC_CIVILIZATIONS


@dataclass(frozen=True, slots=True)
class SimulationMetrics:
    """Stable summary of one automated match."""

    game_id: GameId
    commands: int
    accepted_commands: int
    rejected_commands: int
    turns: int
    finished: bool
    winner_id: PlayerId | None
    victory_type: str | None
    state_hash: str
    event_hash: str


async def create_bot_match(
    manager: GameManager,
    *,
    game_id: GameId,
    seed: int,
    player_count: int = 2,
) -> tuple[PlayerId, ...]:
    """Create, join, and start a deterministic all-bot match through normal commands."""
    await manager.create_game(
        game_id=game_id,
        seed=seed,
        map_config=MapGenerationConfig(radius=4, player_count=player_count),
    )
    players = tuple(PlayerId(f"bot-{index + 1}") for index in range(player_count))
    for index, player_id in enumerate(players):
        civilization = POC_CIVILIZATIONS[index % len(POC_CIVILIZATIONS)]
        result = await manager.process(
            CommandEnvelope.create(
                command_id=CommandId(f"setup-join-{index + 1}"),
                game_id=game_id,
                command_type="JoinGame",
                player_id=player_id,
                payload={
                    "name": f"Bot {index + 1}",
                    "controller": "bot",
                    "civilization_id": civilization.civilization_id,
                },
            )
        )
        if not result.accepted:
            raise RuntimeError(f"failed to join bot player: {player_id}")

    started = await manager.process(
        CommandEnvelope.create(
            command_id=CommandId("setup-start"),
            game_id=game_id,
            command_type="StartGame",
        )
    )
    if not started.accepted:
        raise RuntimeError("failed to start bot match")
    return players


async def run_bot_match(
    manager: GameManager,
    *,
    game_id: GameId,
    policies: dict[PlayerId, BotPolicy] | None = None,
    max_commands: int = 2_000,
) -> SimulationMetrics:
    """Fast-forward a running bot game using only player projections and normal commands."""
    if max_commands <= 0:
        raise ValueError("max_commands must be positive")
    engine = await manager.get_engine(game_id)
    default_policy = SimpleBotPolicy()
    resolved_policies = policies or {}
    accepted = 0
    rejected = 0
    decision_number = 0

    while engine.session.status.value == "active" and decision_number < max_commands:
        active_player = engine.session.current_player_id
        if active_player is None:
            break
        view = project_game(engine.session, active_player)
        policy = resolved_policies.get(active_player, default_policy)
        command = policy.choose_command(view, decision_number=decision_number)
        result = await manager.process(command)
        decision_number += 1
        if result.accepted:
            accepted += 1
        else:
            rejected += 1
        engine = await manager.get_engine(game_id)

    victory = engine.session.victory
    return SimulationMetrics(
        game_id=game_id,
        commands=decision_number,
        accepted_commands=accepted,
        rejected_commands=rejected,
        turns=engine.session.turn,
        finished=engine.session.status.value == "finished",
        winner_id=victory.winner_id if victory is not None else None,
        victory_type=victory.victory_type.value if victory is not None else None,
        state_hash=engine.state_hash(),
        event_hash=engine.event_hash(),
    )
