"""FastAPI /api/v1 adapter with no embedded simulation rules."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect

from civilization_clone.api.auth import AuthenticationError, AuthManager
from civilization_clone.api.content import (
    production_options_response,
    research_options_response,
    rules_content_response,
)
from civilization_clone.api.schemas import (
    CivilizationResponse,
    CivilizationYieldModifierResponse,
    CommandRequest,
    CommandResponse,
    CreateGameRequest,
    EventResponse,
    FeedbackResponse,
    GameCreatedResponse,
    HealthResponse,
    JoinPlayerRequest,
    PlayerJoinedResponse,
    ProductionOptionsResponse,
    ResearchOptionsResponse,
    RulesContentResponse,
)
from civilization_clone.application.manager import GameManager
from civilization_clone.application.projection import project_event, project_game
from civilization_clone.domain.ids import (
    CommandId,
    GameId,
    PlayerId,
    SettlementId,
    validate_id,
)
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.mapgen import MapGenerationConfig
from civilization_clone.engine.research import available_technologies
from civilization_clone.engine.session import CommandResult, GameEngine
from civilization_clone.observability.logging import safe_log_with_context
from civilization_clone.rules.poc import POC_CIVILIZATIONS

_PUBLIC_EVENT_TYPES = frozenset(
    {
        "GameStarted",
        "TurnStarted",
        "TurnEnded",
        "PlayerJoined",
        "PlayerEndedTurn",
        "WarDeclared",
        "PlayerConceded",
        "PlayerEliminated",
        "VictoryAchieved",
    }
)
_WEBSOCKET_PROTOCOL = "civilization.v1"


def create_app(
    manager: GameManager | None = None,
    auth: AuthManager | None = None,
    runtime_logger: logging.Logger | None = None,
) -> FastAPI:
    """Create the public API adapter around application and identity services."""
    app = FastAPI(
        title="CivilizationClone API",
        version="1.1.0",
        description="Client-agnostic deterministic 4X engine API.",
    )
    game_manager = manager or GameManager()
    auth_manager = auth or AuthManager.from_environment()
    app.state.game_manager = game_manager
    app.state.auth_manager = auth_manager

    if runtime_logger is not None:

        @app.middleware("http")
        async def log_http_request(request: Request, call_next: Any) -> Any:
            started = time.perf_counter()
            status_code = 500
            try:
                response = await call_next(request)
                status_code = int(response.status_code)
                return response
            finally:
                duration_ms = round((time.perf_counter() - started) * 1000, 3)
                await asyncio.to_thread(
                    safe_log_with_context,
                    runtime_logger,
                    logging.INFO if status_code < 500 else logging.ERROR,
                    "http request completed",
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                    },
                )

    @app.get("/api/v1/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/api/v1/rules/civilizations", response_model=list[CivilizationResponse])
    async def civilizations() -> list[CivilizationResponse]:
        return [
            CivilizationResponse(
                civilization_id=str(definition.civilization_id),
                name=definition.name,
                description=definition.description,
                tags=list(definition.tags),
                starting_resources=dict(definition.starting_resources),
                yield_modifiers=[
                    CivilizationYieldModifierResponse(
                        yield_type=modifier.yield_type.value,
                        operation=modifier.operation.value,
                        value=modifier.value,
                        priority=modifier.priority,
                    )
                    for modifier in definition.yield_modifiers
                ],
                research_cost_percent=definition.research_cost_percent,
                attack_strength_percent=definition.attack_strength_percent,
                defense_strength_percent=definition.defense_strength_percent,
                unique_units=list(definition.unique_units),
                unique_buildings=list(definition.unique_buildings),
                research_preferences=list(definition.research_preferences),
                content_hooks=list(definition.content_hooks),
            )
            for definition in POC_CIVILIZATIONS
        ]

    @app.get("/api/v1/rules/content", response_model=RulesContentResponse)
    async def rules_content() -> RulesContentResponse:
        return rules_content_response()

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
            admin_token=auth_manager.issue_admin(game_id),
        )

    @app.post(
        "/api/v1/games/{game_id}/players",
        response_model=PlayerJoinedResponse,
    )
    async def join_player(
        game_id: str,
        request: JoinPlayerRequest,
        authorization: str | None = Header(default=None),
    ) -> PlayerJoinedResponse:
        resolved_game_id = _game_id(game_id)
        _require_admin(auth_manager, authorization, resolved_game_id)
        try:
            player_id = validate_id(request.player_id, PlayerId)
            command = CommandEnvelope.create(
                command_id=validate_id(request.command_id, CommandId),
                game_id=resolved_game_id,
                command_type="JoinGame",
                player_id=player_id,
                payload={
                    "name": request.name,
                    "controller": request.controller,
                    "civilization_id": request.civilization_id,
                },
            )
            result = await game_manager.process(command)
            engine = await game_manager.get_engine(resolved_game_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        response = _command_response(engine, result, player_id)
        civilization_id = request.civilization_id
        if result.accepted:
            civilization_id = str(engine.session.players[player_id].civilization_id)
        return PlayerJoinedResponse(
            accepted=response.accepted,
            state_version=response.state_version,
            player_id=str(player_id),
            civilization_id=civilization_id,
            player_token=(
                auth_manager.issue_player(resolved_game_id, player_id) if result.accepted else None
            ),
            events=response.events,
            feedback=response.feedback,
        )

    @app.post(
        "/api/v1/games/{game_id}/commands",
        response_model=CommandResponse,
    )
    async def submit_command(
        game_id: str,
        request: CommandRequest,
        authorization: str | None = Header(default=None),
    ) -> CommandResponse:
        resolved_game_id = _game_id(game_id)
        if request.command_type == "JoinGame":
            raise HTTPException(
                status_code=405,
                detail="JoinGame uses POST /api/v1/games/{game_id}/players",
            )

        player_id: PlayerId | None
        if request.command_type == "StartGame":
            _require_admin(auth_manager, authorization, resolved_game_id)
            player_id = None
        else:
            player_id = _require_player(auth_manager, authorization, resolved_game_id)
            if request.player_id is not None and request.player_id != str(player_id):
                raise HTTPException(status_code=403, detail="player identity does not match credential")

        try:
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
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        resolved_game_id = _game_id(game_id)
        viewer_id = _require_player(auth_manager, authorization, resolved_game_id)
        try:
            engine = await game_manager.get_engine(resolved_game_id)
            return project_game(engine.session, viewer_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/api/v1/games/{game_id}/production-options",
        response_model=ProductionOptionsResponse,
    )
    async def production_options(
        game_id: str,
        settlement_id: str,
        authorization: str | None = Header(default=None),
    ) -> ProductionOptionsResponse:
        resolved_game_id = _game_id(game_id)
        viewer_id = _require_player(auth_manager, authorization, resolved_game_id)
        try:
            resolved_settlement_id = validate_id(settlement_id, SettlementId)
            engine = await game_manager.get_engine(resolved_game_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        settlement = engine.session.settlements.get(resolved_settlement_id)
        if settlement is None or settlement.owner_id != viewer_id:
            raise HTTPException(status_code=404, detail="settlement not found")
        return production_options_response(engine.session, viewer_id, settlement)

    @app.get(
        "/api/v1/games/{game_id}/research-options",
        response_model=ResearchOptionsResponse,
    )
    async def research_options(
        game_id: str,
        authorization: str | None = Header(default=None),
    ) -> ResearchOptionsResponse:
        resolved_game_id = _game_id(game_id)
        viewer_id = _require_player(auth_manager, authorization, resolved_game_id)
        try:
            engine = await game_manager.get_engine(resolved_game_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return research_options_response(engine.session, viewer_id)

    @app.get("/api/v1/games/{game_id}/events", response_model=list[EventResponse])
    async def game_events(
        game_id: str,
        after_sequence: int = -1,
        authorization: str | None = Header(default=None),
    ) -> list[EventResponse]:
        if after_sequence < -1:
            raise HTTPException(status_code=422, detail="after_sequence must be at least -1")
        resolved_game_id = _game_id(game_id)
        viewer_id = _require_player(auth_manager, authorization, resolved_game_id)
        try:
            engine = await game_manager.get_engine(resolved_game_id)
            events = await game_manager.snapshot_events(resolved_game_id)
            projected = [
                project_event(engine.session, event, viewer_id)
                for event in events
                if event.sequence > after_sequence
            ]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return [EventResponse.model_validate(event) for event in projected if event is not None]

    @app.get("/api/v1/games/{game_id}/legal-actions")
    async def legal_actions(
        game_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        resolved_game_id = _game_id(game_id)
        viewer_id = _require_player(auth_manager, authorization, resolved_game_id)
        try:
            engine = await game_manager.get_engine(resolved_game_id)
            player = engine.session.players[viewer_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

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
                    "RejectPeace",
                    "OfferTrade",
                    "AcceptTrade",
                    "RejectTrade",
                    "CancelTrade",
                    "EndTurn",
                ]
            )
            if player.research.selected is None:
                options = available_technologies(player)
                if options:
                    mandatory.append(
                        {
                            "kind": "research",
                            "options": list(options),
                        }
                    )
        return {
            "game_id": game_id,
            "player_id": str(viewer_id),
            "state_version": engine.session.state_version,
            "is_active_player": is_turn,
            "actions": actions,
            "mandatory_decisions": mandatory,
        }

    @app.websocket("/api/v1/games/{game_id}/events/ws")
    async def event_websocket(websocket: WebSocket, game_id: str) -> None:
        try:
            raw_token = _websocket_credential(websocket)
            resolved_game_id = validate_id(game_id, GameId)
            viewer_id = auth_manager.verify_player(raw_token, resolved_game_id)
            engine = await game_manager.get_engine(resolved_game_id)
            if viewer_id not in engine.session.players:
                raise KeyError(f"player not found: {viewer_id}")
            queue = await game_manager.subscribe(resolved_game_id)
        except (AuthenticationError, KeyError, ValueError):
            await websocket.close(code=1008, reason="game or credential not authorized")
            return

        await websocket.accept(subprotocol=_WEBSOCKET_PROTOCOL)
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


def _game_id(raw: str) -> GameId:
    try:
        return validate_id(raw, GameId)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="bearer credential is required")
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="bearer credential is required")
    return token


def _require_admin(
    auth: AuthManager,
    authorization: str | None,
    game_id: GameId,
) -> None:
    try:
        auth.verify_admin(_bearer_token(authorization), game_id)
    except AuthenticationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


def _require_player(
    auth: AuthManager,
    authorization: str | None,
    game_id: GameId,
) -> PlayerId:
    try:
        return auth.verify_player(_bearer_token(authorization), game_id)
    except AuthenticationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


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


def _websocket_credential(websocket: WebSocket) -> str:
    raw_protocols = websocket.headers.get("sec-websocket-protocol", "")
    protocols = [item.strip() for item in raw_protocols.split(",") if item.strip()]
    if len(protocols) != 2 or protocols[0] != _WEBSOCKET_PROTOCOL:
        raise AuthenticationError("websocket credential protocol is required")
    return protocols[1]


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
