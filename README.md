# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Every client interacts with the same authoritative simulation through a versioned API/application boundary.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v1.1 advanced diplomacy and atomic trade

The v0.1→v1.0 proof of concept is complete. v1.1 begins the ordered post-POC roadmap in `PLAN.md` by extending the same authoritative engine/API with replay-safe bilateral trade.

Current capabilities include:

- deterministic hex maps, line/range/pathfinding utilities, fog of war, turns, players, units, settlements, economy, research, abstract combat, diplomacy, and victory;
- two original data-driven civilizations with selectable identity, starting resources, generic yield/research/combat modifiers, and public discovery metadata;
- mandatory research decisions enforced by the authoritative engine before end-turn mutation;
- war/peace diplomacy including peace offers, acceptance, and explicit rejection;
- **v1.1 bilateral Gold trade** with `OfferTrade`, `AcceptTrade`, `RejectTrade`, and `CancelTrade` through the normal command bus;
- atomic trade settlement with affordability revalidation and idempotent accepted-command retries;
- automatic invalidation of pending trade offers on war or player elimination/concession;
- participant-only trade state/events so unrelated players cannot observe private terms;
- completed-trade counters and last-trade turn in authorized bilateral projections;
- append-only deterministic domain events, state/event hashes, persisted accepted/rejected command idempotency, and safe feedback;
- async-safe SQLite snapshots, immutable event storage, accepted-command replay transcripts, and durable replay-provenance tracking;
- save format v3 with hash-verified migration from pre-civilization v1 and pre-trade v2 snapshots;
- independent replay that rebuilds the advanced engine from the generated world plus accepted commands and compares final state/event hashes;
- serialized per-game mutation through the async application manager;
- fog-safe player projections and authorized event filtering;
- FastAPI `/api/v1` lifecycle, rules-discovery, command, query, legal-action, and WebSocket surfaces;
- HMAC-signed host/player credentials so API identity is not trusted from arbitrary payload fields;
- WebSocket credentials carried in the subprotocol header instead of request URLs;
- structured safe HTTP/application diagnostics with blocking log handlers isolated from the async event loop;
- deterministic projection-only bots that use public civilization research preferences and can negotiate/answer simple trade offers without hidden-state access;
- a playable hotseat terminal client that uses only public HTTP contracts, including v1.1 trade commands;
- Godot, Unity, and Unreal Engine graphical client foundations that remain thin API adapters;
- deterministic replay corpus and public-client end-to-end coverage;
- local benchmark and release tooling with no hosted CI dependency.

See `PLAN.md` for the ordered v1.1→v2.0 post-POC roadmap. The next planned phase is **v1.2 — Trade networks, open borders, and logistics**.

## Development

Install the project and development tools with `uv`:

```bash
uv sync --dev
```

Run the canonical local verification gate:

```bash
bash scripts/ci.sh
```

The gate checks governance, dependency sync, formatting, linting, type checking, tests, and package build. All CI is local. GitHub Actions is intentionally prohibited by project governance.

## Run the API

```bash
export CIVILIZATION_CLONE_AUTH_SECRET="choose-a-local-secret"
uv run civilization-clone-api
```

By default the API binds to `127.0.0.1:8000` and stores games in
`data/civilization_clone.sqlite3`.

Optional environment variables:

- `CIVILIZATION_CLONE_HOST` — bind host;
- `CIVILIZATION_CLONE_PORT` — TCP port;
- `CIVILIZATION_CLONE_DB` — SQLite database path;
- `CIVILIZATION_CLONE_AUTH_SECRET` — stable HMAC secret used to sign host/player credentials;
- `CIVILIZATION_CLONE_LOG_LEVEL` — runtime logging level, default `INFO`;
- `CIVILIZATION_CLONE_LOG_JSON` — enable compact JSON-lines diagnostics with `1`, `true`, `yes`, or `on`.

If no auth secret is supplied, a loopback-only local process may use an ephemeral secret. Existing credentials therefore stop working after that process restarts; set the environment variable for durable local sessions. Binding beyond loopback requires an explicit auth secret.

Primary public routes:

- `GET /api/v1/rules/civilizations` — discover playable civilizations and public gameplay bonuses;
- `GET /api/v1/rules/content` — discover presentation-safe unit/building/technology definitions;
- `POST /api/v1/games` — create a game and receive its host/admin credential;
- `POST /api/v1/games/{game_id}/players` — host-authorized player enrollment, civilization selection, and player credential issuance;
- `POST /api/v1/games/{game_id}/commands` — authenticated authoritative commands, including v1.1 trade proposals/responses;
- `GET /api/v1/games/{game_id}/state` — authenticated fog-safe/player-private snapshot;
- `GET /api/v1/games/{game_id}/events` — authenticated authorized event history;
- `GET /api/v1/games/{game_id}/legal-actions` — authenticated action/mandatory-decision query;
- `GET /api/v1/games/{game_id}/research-options` — authorized research choices/costs;
- `GET /api/v1/games/{game_id}/production-options?settlement_id=...` — authorized server-derived production options;
- `WS /api/v1/games/{game_id}/events/ws?after_sequence=...` — authorized player event stream using `Sec-WebSocket-Protocol` for credentials.

See `docs/API_CONTRACT.md` for the v1 public contract.

## Play the TUI

With the API running:

```bash
uv run civilization-clone-tui
```

Or launch both the local persistent API and client for human-style QA:

```bash
bash scripts/playtest_tui.sh
```

The TUI discovers and explains civilization choices through the public API, supports hotseat 2–4 player setup, fog-safe map rendering, player switching, movement, settlement founding/management, production, research, war/peace diplomacy, bilateral Gold trade, abstract combat, turn advancement, event inspection, and concession/victory. It never imports or mutates engine state directly. The launcher uses a fresh temporary SQLite database unless `CIVILIZATION_CLONE_DB` is explicitly supplied.

Trade examples:

```text
trade p2 2 1
accept-trade p1
reject-trade p1
cancel-trade p2
```

The terms above mean “offer 2 Gold and request 1 Gold” from the command issuer's perspective. The server remains authoritative for turn legality, peace status, affordability, and atomic settlement.

## Persistence and deterministic replay

`SqliteGameStore` persists:

- canonical snapshots;
- immutable deterministic event rows;
- immutable accepted-command transcript rows;
- persisted accepted and rejected command idempotency results inside the save document;
- replay-completeness provenance so migrated legacy games cannot be falsely certified as fully replayable.

All SQLite work runs through explicit worker-thread boundaries when called from async code.
`GameManager.verify_replay()` creates a fresh advanced engine from the immutable generated world and replays the accepted command transcript through normal command processing. A v1 replay is accepted only when both the final state hash and event-journal hash match the live game.

Save format v3 adds bilateral trade state. v1 and v2 snapshots are verified against their original canonical state hash before deterministic migration defaults are introduced. Legacy v0.8/v1-format snapshots may still load but predate durable accepted-command transcripts and civilization identity, so replay completeness remains explicitly unavailable. See `docs/REPLAY.md` for the replay contract, compatibility boundary, and corpus.

## Local performance and release gates

Run the deterministic simulation benchmark:

```bash
uv run civilization-clone-benchmark --games 10 --seed 1000 --max-commands 2000
```

The benchmark reports throughput plus completion rate, command rejection rate, victory distribution, replay failures, per-match replay status, and deterministic state/event hashes.

Prepare a local release candidate only after the canonical CI gate succeeds:

```bash
bash scripts/release.sh
```

Build outputs and benchmark/playtest artifacts belong under ignored `artifacts/` paths. See `docs/PERFORMANCE.md` and `docs/WORKFLOW.md`.

## AI boundary

The simple bot policy receives only the same player-authorized projection exposed to normal clients. The projection includes safe research availability, the viewer civilization's public research preferences, and only diplomacy/trade relationships involving that viewer. It does not include hidden tiles, hidden opposing-unit state, unrelated private trade terms, or an unrestricted `GameSession`. Bot commands travel through the normal validated command/application path.

## Logging model

CivilizationClone separates three channels:

- **domain event journal** — deterministic authoritative history used for replay/debugging;
- **runtime logs** — operational structured diagnostics that never affect simulation state and never include credentials/request bodies;
- **user feedback** — safe typed messages clients can render without exposing internal debug information.

Generated local logs/artifacts belong under ignored `logs/` and `artifacts/` directories. See `docs/LOGGING.md` for runtime logging controls and safety rules.
