# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Every client interacts with the same authoritative simulation through a versioned API/application boundary.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v1.0 playable proof of concept

The planned proof-of-concept path through v1.0 is implemented in this branch:

- deterministic hex maps, fog of war, turns, players, units, settlements, economy, research, combat, diplomacy, and victory;
- mandatory research decisions enforced by the authoritative engine before end-turn mutation;
- append-only deterministic domain events, state/event hashes, persisted accepted/rejected command idempotency, and safe feedback;
- async-safe SQLite snapshots, immutable event storage, and accepted-command replay transcripts;
- independent replay that rebuilds the engine from the generated world plus accepted commands and compares final state/event hashes;
- serialized per-game mutation through the async application manager;
- fog-safe player projections and authorized event filtering;
- FastAPI `/api/v1` lifecycle, command, query, legal-action, and WebSocket surfaces;
- HMAC-signed host/player credentials so API identity is not trusted from arbitrary payload fields;
- WebSocket credentials carried in the subprotocol header instead of request URLs;
- deterministic projection-only bots and headless simulation automation;
- a playable hotseat terminal client that uses only public HTTP contracts;
- deterministic replay corpus and public-client end-to-end coverage;
- local benchmark and release tooling with no hosted CI dependency.

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
- `CIVILIZATION_CLONE_AUTH_SECRET` — stable HMAC secret used to sign host/player credentials.

If no auth secret is supplied, a loopback-only local process may use an ephemeral secret. Existing credentials therefore stop working after that process restarts; set the environment variable for durable local sessions. Binding beyond loopback requires an explicit auth secret.

Primary public routes:

- `POST /api/v1/games` — create a game and receive its host/admin credential;
- `POST /api/v1/games/{game_id}/players` — host-authorized player enrollment and player credential issuance;
- `POST /api/v1/games/{game_id}/commands` — authenticated authoritative commands;
- `GET /api/v1/games/{game_id}/state` — authenticated fog-safe player snapshot;
- `GET /api/v1/games/{game_id}/events` — authenticated authorized event history;
- `GET /api/v1/games/{game_id}/legal-actions` — authenticated action/mandatory-decision query;
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

The TUI supports hotseat 2–4 player setup, fog-safe map rendering, player switching, movement, settlement founding/management, production, research, diplomacy, combat, turn advancement, event inspection, and concession/victory. It never imports or mutates engine state directly. The launcher uses a fresh temporary SQLite database unless `CIVILIZATION_CLONE_DB` is explicitly supplied.

## Persistence and deterministic replay

`SqliteGameStore` persists:

- canonical snapshots;
- immutable deterministic event rows;
- immutable accepted-command transcript rows;
- persisted accepted and rejected command idempotency results inside the save document.

All SQLite work runs through explicit worker-thread boundaries when called from async code.
`GameManager.verify_replay()` creates a fresh engine from the immutable generated world and replays the accepted command transcript through normal command processing. A v1 replay is accepted only when both the final state hash and event-journal hash match the live game.

Legacy v0.8 snapshots may still load, but they predate durable accepted-command transcripts and therefore cannot claim complete independent replay verification. See `docs/REPLAY.md` for the replay contract, compatibility boundary, and corpus.

## Local performance and release gates

Run the deterministic simulation benchmark:

```bash
uv run civilization-clone-benchmark --games 10
```

Prepare a local release candidate only after the canonical CI gate succeeds:

```bash
bash scripts/release.sh
```

Build outputs and benchmark/playtest artifacts belong under ignored `artifacts/` paths. See `docs/PERFORMANCE.md` and `docs/WORKFLOW.md`.

## AI boundary

The simple bot policy receives only the same player-authorized projection exposed to normal clients. It does not receive an unrestricted `GameSession`, hidden tiles, or hidden opposing-unit state. Bot commands travel through the normal validated command/application path.

## Logging model

CivilizationClone separates three channels:

- **domain event journal** — deterministic authoritative history used for replay/debugging;
- **runtime logs** — operational structured diagnostics that never affect simulation state;
- **user feedback** — safe typed messages clients can render without exposing internal debug information.

Generated local logs/artifacts belong under ignored `logs/` and `artifacts/` directories.
