# CivilizationClone v1 Public API Contract

## Boundary

`/api/v1` is a client adapter over the application layer. HTTP handlers do not implement simulation rules. Clients submit commands and render authorized projections/events/feedback; they never mutate authoritative state directly.

The current additive implementation version is **1.1.0**. The URL remains `/api/v1` because v1.1 adds compatible command/state/event fields rather than changing existing v1 request semantics.

## Identity and credentials

The v1 API does not trust `player_id` from arbitrary request data.

- `POST /api/v1/games` returns an opaque `admin_token` scoped to that game.
- The admin token authorizes player enrollment and `StartGame`.
- `POST /api/v1/games/{game_id}/players` returns an opaque `player_token` scoped to exactly one game/player pair.
- Player state, events, legal actions, player-specific content options, and normal gameplay commands derive viewer/actor identity from the player token.
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

### Public rules content

`GET /api/v1/rules/content`

This public, read-only endpoint adapts the authoritative POC content registries into deterministic presentation metadata. It is intended for clients that need names, costs, requirements, tooltips, and rules browsers without duplicating gameplay constants.

The response contains:

- producible unit definitions with id/name, movement, vision, production cost, founding capability, abstract attack/defense/ranged values, and public civilization/research requirements;
- building definitions with id/name, production cost, visible yield modifiers, and public civilization/research requirements;
- technology definitions with id/name, base cost, prerequisites, and unlock references.

The public catalog does not contain credentials, fogged game state, opponent-private economy state, command internals, RNG state, save/database metadata, or other hidden authority data. A client must not infer current player legality from this public catalog; use the authenticated option queries below.

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

Current v1 command types:

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
- `OfferTrade`
- `AcceptTrade`
- `RejectTrade`
- `CancelTrade`
- `EndTurn`
- `Concede`

`JoinGame` is intentionally unavailable on the generic command route; use the player-enrollment endpoint so credential issuance cannot be bypassed.

Every command carries a unique `command_id`. `expected_state_version` is optional optimistic concurrency control. Retrying an already-processed command id reuses the original deterministic result rather than mutating twice. Accepted and rejected command results are persisted so idempotency survives process restart.

`EndTurn` is rejected with `MANDATORY_CHOICE_REQUIRED` while a selectable research decision is unresolved. The `legal-actions` query reports the same mandatory research options before the client attempts the command.

### Trade commands and terms

v1.1 adds bilateral lump-sum Gold trade without adding a second mutation API.

`OfferTrade` payload:

```json
{
  "target_player_id": "p2",
  "offered_gold": 2,
  "requested_gold": 1
}
```

Rules:

- only the active player may create/respond to/cancel a trade proposal;
- both players must exist, be non-eliminated, and currently be at peace;
- one pending trade proposal may exist per bilateral relationship;
- `offered_gold` and `requested_gold` are integers from 0 through the configured safety cap; at least one must be positive;
- the proposer must be able to afford the offered amount when proposing;
- both players' balances are revalidated when `AcceptTrade` executes;
- Gold moves atomically only after successful acceptance;
- `RejectTrade` clears the other player's proposal without changing resources;
- `CancelTrade` withdraws the actor's own proposal;
- declaring war or eliminating/conceding a participant invalidates pending trade state;
- command idempotency applies normally, so retrying the same accepted `AcceptTrade` command cannot transfer Gold twice.

The bilateral relationship projection may include:

```json
{
  "pending_trade": {
    "proposer_id": "p1",
    "offered_gold": 2,
    "requested_gold": 1
  },
  "completed_trades": 1,
  "last_trade_turn": 4
}
```

These fields are returned only inside relationships involving the authenticated viewer. Trade proposal/event data is not a public diplomacy feed.

### Queue-time versus completion-time production gates

The current POC deliberately permits a known production definition to be queued before stable civilization/research completion gates are met. `QueueProduction` still validates active-player authority, settlement ownership, known kind/definition, and already-completed buildings at queue time. Production resolution later requires civilization ownership and any required technology before the queued order can complete.

Clients must not tighten or reinterpret this rule locally. The production-options query exposes `queue_allowed`/`queue_blockers` separately from `completion_unlocked`/`completion_blockers` so a UI can clearly label a queueable future item without pretending it can already complete.

## Queries

All normal queries require a player credential and return only that player's authorized projection or player-scoped option data.

- `GET /api/v1/games/{game_id}/state`
- `GET /api/v1/games/{game_id}/events?after_sequence=N`
- `GET /api/v1/games/{game_id}/legal-actions`
- `GET /api/v1/games/{game_id}/research-options`
- `GET /api/v1/games/{game_id}/production-options?settlement_id=<own-settlement-id>`

The player projection includes the viewer's selected civilization id and public civilization ids for the player roster. Unknown map tiles are omitted. Previously discovered but not currently visible tiles contain only persistent map knowledge. Hidden opposing units are omitted. Opponent settlement internals, production queues, private economy details, and unrelated bilateral trade proposals are not exposed.

### Research options

`GET /api/v1/games/{game_id}/research-options`

Requires the player token. The response returns every public POC technology with:

- id and display name;
- base and viewer-effective research cost after authoritative civilization modifiers;
- prerequisites and unlocks;
- content status (`available`, `selected`, `locked`, or `completed`);
- `selectable` and stable blocker codes, including active-turn legality.

This keeps effective costs and command affordances server-derived. Clients should submit the selected `technology_id` through the normal `ChooseResearch` command and still handle command rejection normally.

### Production options

`GET /api/v1/games/{game_id}/production-options?settlement_id=<id>`

Requires the player token. The requested settlement must belong to the authenticated viewer. An unknown settlement and another player's settlement intentionally produce the same generic `404 settlement not found` response so the query is not a settlement-existence oracle.

Each option contains its kind, id/name, cost, public requirements, queue-time status/blockers, and stable completion-content status/blockers. The response does not reveal hidden opponent state. Resource accumulation and unit spawn-space availability remain runtime conditions rather than permanent content-unlock flags.

Clients should use this endpoint to populate normal production controls, but still submit `QueueProduction` through the authoritative command route and handle the resulting accepted/rejected response.

## Event stream

`WS /api/v1/games/{game_id}/events/ws?after_sequence=N`

The credential is supplied through the WebSocket subprotocol header as described above. The server first sends authorized historical events newer than `after_sequence`, then publishes newly appended authorized events in journal order. Command retries do not republish old events.

Peace offers/acceptances/rejections and all `Trade*` proposal/result/cancellation events are bilateral rather than globally visible. Combat events include stable participant ownership in their deterministic payload so both involved players retain authorization even after a destroyed unit has been removed from current state.

## Feedback and errors

Expected gameplay rejection is returned in the normal command response using typed feedback with stable code, severity, safe message, and small safe context. v1.1 trade validation uses `INVALID_TRADE` for malformed terms and `TRADE_REJECTED` with a stable safe `reason` context for rule rejection.

Authentication/transport failures use HTTP status codes and must not expose stack traces, filesystem paths, database internals, credentials, or hidden-player state.

## Compatibility

The v1 contract deliberately hardens the earlier v0.8 prototype by replacing trusted `player_id` query/body identity with signed credentials and a dedicated enrollment endpoint. It also makes civilization identity and its generic modifiers part of authoritative state/save/replay behavior. Public read-model additions under `/api/v1/rules/content`, `/research-options`, and `/production-options` are additive presentation/discovery surfaces; command authority remains unchanged.

v1.1 is additive at the HTTP path level: existing v1 commands and response fields remain valid, while trade commands and diplomacy projection fields are new. Durable save format v3 adds trade relationship fields; older v1/v2 save documents are hash-verified in their original form before deterministic default migration. Future incompatible public changes require a new API version or an explicit compatibility decision.
