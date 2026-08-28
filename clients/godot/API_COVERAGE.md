# Godot Public API Coverage

This document maps the authoritative `/api/v1` contract to the Godot client. It is a transport/presentation checklist only. The server remains authoritative for all simulation rules and hidden information.

## Public discovery

| API surface | Godot status | Client behavior |
| --- | --- | --- |
| `GET /api/v1/health` | Implemented | Connection and attach flows verify server availability. |
| `GET /api/v1/rules/civilizations` | Implemented | Lobby civilization selectors are populated from the server response. |

## Game lifecycle

| API surface | Godot status | Client behavior |
| --- | --- | --- |
| `POST /api/v1/games` | Implemented | Game ID, seed, player count, map radius, water %, and resource % are exposed in the lobby. |
| `POST /api/v1/games/{game_id}/players` | Implemented | Player ID, display name, civilization, and `human`/`bot` controller type are submitted through the public enrollment endpoint. |
| `StartGame` via command endpoint | Implemented | Uses the game admin credential returned by create-game. |
| Existing-game attach | Implemented using existing query contract | User supplies game ID and player token; optional player ID is verified against the authorized projection. No credential is persisted. |
| Clear/logout local session | Implemented | WebSocket closes and all in-memory game/admin/player credentials are cleared. |

## Gameplay commands

All current POC command types exposed by the v1 contract are wired through the same generic Godot command transport:

- `MoveUnit`;
- `AttackUnit`;
- `FoundSettlement`;
- `SetWorkedTile`;
- `QueueProduction`;
- `CancelProduction`;
- `ChooseResearch`;
- `DeclareWar`;
- `OfferPeace`;
- `AcceptPeace`;
- `RejectPeace`;
- `EndTurn`;
- `Concede`.

Every command uses a client-generated unique `command_id`, sends optimistic `expected_state_version` when available, and includes a presentation-only client timestamp. Player identity remains derived from the bearer credential by the server.

## Authorized queries

| API surface | Godot status | Client behavior |
| --- | --- | --- |
| `GET .../state` | Implemented | Drives the fog-safe map and current viewer panels. |
| `GET .../legal-actions` | Implemented | Drives legal action and mandatory research presentation. |
| `GET .../events?after_sequence=N` | Implemented | Used to bootstrap an authorized event cursor before the live stream connects. |

## Authorized WebSocket events

`WS /api/v1/games/{game_id}/events/ws?after_sequence=N` is implemented with `WebSocketPeer`.

Security contract:

- URL contains only the non-secret `after_sequence` cursor;
- the requested WebSocket subprotocol list is exactly `civilization.v1`, then the player token;
- the bearer token is never placed in the WebSocket URL;
- viewer changes close the old stream and bootstrap a new authorized stream;
- policy close (`1008`) is treated as an authorization failure;
- other disconnects use bounded exponential reconnect delay;
- received JSON events are merged by monotonically increasing event sequence;
- event-triggered projection refreshes still go through the normal authenticated HTTP state/legal-action queries.

## What is not possible without new server API surfaces

The following roadmap work is **not** an unimplemented client binding to the current v1 API. It requires the server contract to expose additional read-only/authorized data first:

- server-driven unit/building production catalogs and lock reasons;
- complete technology display definitions/unlocks;
- authoritative movement-range/path/target query data;
- richer public unit/settlement inspector metadata where projections do not currently expose it;
- spectator/observer credential semantics if desired;
- bot fast-forward or explicit bot-run controls if desired.

These belong to later API additions (especially Godot phases G2/G3/G8). Godot must not fill these gaps by copying Python rule registries or deriving hidden state locally.

## QA status

Static implementation and smoke assertions exist, but Godot runtime QA must be executed locally before claiming PASS:

```bash
bash scripts/verify_godot_client.sh
bash scripts/ci.sh
bash scripts/playtest_godot.sh
```

The human-style playtest should cover both a newly-created game and an attach-existing-game flow, Human/Bot enrollment choices, viewer switching, WebSocket reconnect behavior, and clearing the local session.
