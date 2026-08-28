"""FastAPI /api/v1 adapter with no embedded simulation rules."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect

from civilization_clone.api.schemas import (
    CommandRequest,
    CommandResponse,
    CreateGameRequest,
    EventResponse,
    FeedbackResponse,
    GameCreatedResponse,
    HealthResponse,
)
from civilization_clone.application.manager import GameManager
from civilization_clone.application.projection import project_event, project_game
from civilization_clone.domain.ids import CommandId, GameId, PlayerId, validate_id
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.research import available_technologies
from civilization_clone.engine.session import CommandResult, GameEngine

_PUBLIC_EVENT_TYPES = frozenset(
    {
        "GameStarted",
        "TurnStarted",
        "TurnEnded",
        "PlayerJoined",
        "PlayerEndedTurn",
        "WarDeclared",
        "PeaceOffered",
        "PeaceAccepted",
        "PlayerConceded",
        "PlayerEliminated",
        "VictoryAchieved",
    }
)


def create_app(manager: GameManager | None = None) -> FastAPI:
    """Create the public API adapter around one application-layer game manager."""
    app = FastAPI(
        title="CivilizationClone API",
        version="0.8.0",
        description="Client-agnostic deterministic 4X engine API.",
    )
    game_manager = manager or GameManager()
    app.state.game_manager = game_manager

    @app.get("/api/v1/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.post("/api/v1/games", response_model=GameCreatedResponse, status_code=201)
    async def create_game(request: CreateGameRequest) -> GameCreatedResponse:
        try:
            game_id = validate_id(request.game_id, GameId)
            engine = await game_manager.create_game(
                game_id=game_id,
                seed=request.seed,
                map_config=MapGenerationConfig(
                    radius=request.map_radius,
                    player_count=request.player_count,
                    water_percent=request.water_percent,
                    resource_percent=request.resource_percent,
                ),
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return GameCreatedResponse(
            game_id=str(engine.session.game_id),
            seed=engine.session.seed,
            state_version=engine.session.state_version,
            status=engine.session.status.value,
        )

    @app.post(
        "/api/v1/games/{game_id}/commands",
        response_model=CommandResponse,
    )
    async def submit_command(game_id: str, request: CommandRequest) -> CommandResponse:
        try:
            resolved_game_id = validate_id(game_id, GameId)
            player_id = (
                validate_id(request.player_id, PlayerId)
                if request.player_id is not None
                else None
            )
            command = CommandEnvelope.create(
                command_id=validate_id(request.command_id, CommandId),
                game_id=resolved_game_id,
                command_type=request.command_type,
                player_id=player_id,
                expected_state_version=request.expected_state_version,
                payload=request.payload,  # type: ignore[arg-type]
                client_timestamp=request.client_timestamp,
            )
            result = await game_manager.process(command)
            engine = await game_manager.get_engine(resolved_game_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return _command_response(engine, result, player_id)

    @app.get("/api/v1/games/{game_id}/state")
    async def game_state(
        game_id: str,
        player_id: str = Query(min_length=1),
    ) -> dict[str, Any]:
        try:
            resolved_game_id = validate_id(game_id, GameId)
            viewer_id = validate_id(player_id, PlayerId)
            engine = await game_manager.get_engine(resolved_game_id)
            return project_game(engine.session, viewer_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/games/{game_id}/events", response_model=list[EventResponse])
    async def game_events(
        game_id: str,
        player_id: str = Query(min_length=1),
        after_sequence: int = Query(default=-1, ge=-1),
    ) -> list[EventResponse]:
        try:
            resolved_game_id = validate_id(game_id, GameId)
            viewer_id = validate_id(player_id, PlayerId)
            engine = await game_manager.get_engine(resolved_game_id)
            events = await game_manager.snapshot_events(resolved_game_id)
            projected = [
                project_event(engine.session, event, viewer_id)
                for event in events
                if event.sequence > after_sequence
            ]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return [EventResponse.model_validate(event) for event in projected if event is not None]

    @app.get("/api/v1/games/{game_id}/legal-actions")
    async def legal_actions(
        game_id: str,
        player_id: str = Query(min_length=1),
    ) -> dict[str, Any]:
        try:
            resolved_game_id = validate_id(game_id, GameId)
            viewer_id = validate_id(player_id, PlayerId)
            engine = await game_manager.get_engine(resolved_game_id)
            player = engine.session.players[viewer_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        is_turn = engine.session.current_player_id == viewer_id
        actions: list[str] = ["Concede"] if not player.eliminated else []
        mandatory: list[dict[str, Any]] = []
        if is_turn and not player.eliminated:
            actions.extend(
                [
                    "MoveUnit",
                    "AttackUnit",
                    "FoundSettlement",
                    "SetWorkedTile",
                    "QueueProduction",
                    "CancelProduction",
                    "ChooseResearch",
                    "DeclareWar",
                    "OfferPeace",
                    "AcceptPeace",
                    "EndTurn",
                ]
            )
            if player.research.selected is None:
                mandatory.append(
                    {
                        "kind": "research",
                        "options": list(available_technologies(player)),
                    }
                )
        return {
            "game_id": game_id,
            "player_id": player_id,
            "state_version": engine.session.state_version,
            "is_active_player": is_turn,
            "actions": actions,
            "mandatory_decisions": mandatory,
        }

    @app.websocket("/api/v1/games/{game_id}/events/ws")
    async def event_websocket(websocket: WebSocket, game_id: str) -> None:
        raw_player_id = websocket.query_params.get("player_id")
        if raw_player_id is None:
            await websocket.close(code=1008, reason="player_id is required")
            return
        try:
            resolved_game_id = validate_id(game_id, GameId)
            viewer_id = validate_id(raw_player_id, PlayerId)
            engine = await game_manager.get_engine(resolved_game_id)
            if viewer_id not in engine.session.players:
                raise KeyError(f"player not found: {viewer_id}")
            queue = await game_manager.subscribe(resolved_game_id)
        except (KeyError, ValueError):
            await websocket.close(code=1008, reason="game or player not found")
            return

        await websocket.accept()
        try:
            after_sequence = _websocket_after_sequence(websocket)
            for event in await game_manager.snapshot_events(resolved_game_id):
                if event.sequence <= after_sequence:
                    continue
                projected = project_event(engine.session, event, viewer_id)
                if projected is not None:
                    await websocket.send_json(projected)
            while True:
                event = await queue.get()
                projected = project_event(engine.session, event, viewer_id)
                if projected is not None:
                    await websocket.send_json(projected)
        except WebSocketDisconnect:
            pass
        finally:
            game_manager.unsubscribe(resolved_game_id, queue)

    return app


def _command_response(
    engine: GameEngine,
    result: CommandResult,
    viewer_id: PlayerId | None,
) -> CommandResponse:
    events: list[EventResponse] = []
    for event in result.events:
        projected = None
        if viewer_id is not None:
            projected = project_event(engine.session, event, viewer_id)
        elif event.event_type in _PUBLIC_EVENT_TYPES:
            projected = {
                "event_id": str(event.event_id),
                "sequence": event.sequence,
                "event_type": event.event_type,
                "state_version": event.state_version,
                "payload": _plain_mapping(event.payload),
            }
        if projected is not None:
            events.append(EventResponse.model_validate(projected))

    feedback = [
        FeedbackResponse(
            code=item.code,
            message=item.message,
            severity=item.severity.value,
            context=dict(item.context),
        )
        for item in result.feedback
    ]
    return CommandResponse(
        accepted=result.accepted,
        state_version=result.state_version,
        events=events,
        feedback=feedback,
    )


def _websocket_after_sequence(websocket: WebSocket) -> int:
    raw = websocket.query_params.get("after_sequence", "-1")
    try:
        return max(-1, int(raw))
    except ValueError:
        return -1


def _plain_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    def convert(item: Any) -> Any:
        if isinstance(item, Mapping):
            return {str(key): convert(child) for key, child in item.items()}
        if isinstance(item, tuple):
            return [convert(child) for child in item]
        return item

    return {str(key): convert(item) for key, item in value.items()}
