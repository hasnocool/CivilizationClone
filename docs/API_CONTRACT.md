# CivilizationClone v1 Public API Contract

## Boundary

`/api/v1` is a client adapter over the application layer. HTTP handlers do not implement simulation rules. Clients submit commands and render authorized projections/events/feedback; they never mutate authoritative state directly.

## Identity and credentials

The v1 API does not trust `player_id` from arbitrary request data.

- `POST /api/v1/games` returns an opaque `admin_token` scoped to that game.
- The admin token authorizes player enrollment and `StartGame`.
- `POST /api/v1/games/{game_id}/players` returns an opaque `player_token` scoped to exactly one game/player pair.
- Player state, events, legal actions, and normal gameplay commands derive viewer/actor identity from the player token.
- If a legacy `player_id` is supplied on a command, it must match the signed identity or the request is rejected.
- Tokens are application/transport metadata and never enter deterministic game state, event payloads, state hashes, RNG inputs, or replay transcripts as authority data.

HTTP bearer credentials use:

```text
Authorization: Bearer <token>
```

WebSocket connections deliberately keep credentials out of URLs. Browser clients open the socket with two requested subprotocols:

```text
civilization.v1
<player_token>
```

The server authenticates the second `Sec-WebSocket-Protocol` value and accepts `civilization.v1` as the negotiated subprotocol. Only non-secret resume information such as `after_sequence` belongs in the WebSocket query string. This prevents ordinary access logs from capturing credentials embedded in URLs.

`CIVILIZATION_CLONE_AUTH_SECRET` should be stable for durable local sessions. Without it, a process-local ephemeral key is generated and credentials expire when the server restarts.

## Rules discovery

### Civilizations

`GET /api/v1/rules/civilizations`

This public endpoint returns the playable original POC civilization definitions in deterministic order. Each entry includes:

- civilization id, display name, description, and tags;
- starting Gold/Science/Culture resources;
- generic settlement yield modifiers;
- research-cost and abstract combat-strength percentage modifiers;
- unique unit/building references when present;
- research preferences and content hooks.

Clients should discover these definitions rather than hard-code the available roster. The server remains authoritative for validating the selected `civilization_id` and applying its data-driven effects.

## Lifecycle

### Create game

`POST /api/v1/games`

Request fields include `game_id`, `seed`, `player_count`, map radius, water percentage, and resource percentage. Response includes the game id, seed, state version/status, and the host/admin credential.

### Enroll player

`POST /api/v1/games/{game_id}/players`

Requires the game admin token. Request fields are `command_id`, `player_id`, `name`, optional controller type, and `civilization_id`. Enrollment is internally translated into the normal deterministic `JoinGame` command. Successful enrollment returns the selected civilization id and a player credential.

For v1 compatibility, omitted `civilization_id` defaults to `river_compact`; interactive clients should still present the rules-discovery choices explicitly.

### Start game

`POST /api/v1/games/{game_id}/commands` with `command_type=StartGame` and the game admin token.

## Player commands

Normal commands require a player token and use the same authoritative command processor as local engine callers and bots.

POC command types:

- `MoveUnit`
- `AttackUnit`
- `FoundSettlement`
- `SetWorkedTile`
- `QueueProduction`
- `CancelProduction`
- `ChooseResearch`
- `DeclareWar`
- `OfferPeace`
- `AcceptPeace`
- `RejectPeace`
- `EndTurn`
- `Concede`

`JoinGame` is intentionally unavailable on the generic command route; use the player-enrollment endpoint so credential issuance cannot be bypassed.

Every command carries a unique `command_id`. `expected_state_version` is optional optimistic concurrency control. Retrying an already-processed command id reuses the original deterministic result rather than mutating twice. Accepted and rejected command results are persisted so idempotency survives process restart.

`EndTurn` is rejected with `MANDATORY_CHOICE_REQUIRED` while a selectable research decision is unresolved. The `legal-actions` query reports the same mandatory research options before the client attempts the command.

## Queries

All normal queries require a player credential and return only that player's authorized projection.

- `GET /api/v1/games/{game_id}/state`
- `GET /api/v1/games/{game_id}/events?after_sequence=N`
- `GET /api/v1/games/{game_id}/legal-actions`

The player projection includes the viewer's selected civilization id and public civilization ids for the player roster. Unknown map tiles are omitted. Previously discovered but not currently visible tiles contain only persistent map knowledge. Hidden opposing units are omitted. Opponent settlement internals, production queues, and private economy details are not exposed.

## Event stream

`WS /api/v1/games/{game_id}/events/ws?after_sequence=N`

The credential is supplied through the WebSocket subprotocol header as described above. The server first sends authorized historical events newer than `after_sequence`, then publishes newly appended authorized events in journal order. Command retries do not republish old events.

Peace offers, acceptances, and rejections are bilateral rather than globally visible. Combat events include stable participant ownership in their deterministic payload so both involved players retain authorization even after a destroyed unit has been removed from current state.

## Feedback and errors

Expected gameplay rejection is returned in the normal command response using typed feedback with stable code, severity, safe message, and small safe context.

Authentication/transport failures use HTTP status codes and must not expose stack traces, filesystem paths, database internals, credentials, or hidden-player state.

## Compatibility

The v1 contract deliberately hardens the earlier v0.8 prototype by replacing trusted `player_id` query/body identity with signed credentials and a dedicated enrollment endpoint. It also makes civilization identity and its generic modifiers part of authoritative state/save/replay behavior. Future incompatible public changes require a new API version or an explicit compatibility decision.
