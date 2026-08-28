# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Every client interacts with the same authoritative simulation through a versioned API/application boundary.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v0.8 deterministic AI and simulation automation

The proof of concept now implements the planned engine path through v0.8:

- deterministic hex maps, path validation, fog of war, turns, players, and units;
- settlement founding, territory, worked tiles, population growth, yields, production queues, and modifiers;
- baseline Science/Culture generation and a prerequisite technology DAG with deterministic progress;
- technology-gated advanced production capabilities;
- deterministic strategic conflict resolution, diplomacy state, elimination, score/conquest victory checks;
- append-only domain events, state/event hashes, idempotent command retries, and safe typed feedback;
- complete save-document encoding with full authoritative state, event journal, and processed-command cache;
- async-safe SQLite persistence using worker-thread boundaries around blocking SQLite operations;
- save/load hash verification, immutable durable event checks, and replay-divergence detection;
- an async `GameManager` with registry locking, per-game mutation locks, persistence integration, and subscribers;
- fog-safe player projections that omit unknown terrain and hidden opposing units;
- versioned `/api/v1` FastAPI endpoints for game lifecycle, commands, state, events, and legal actions;
- player-authorized WebSocket event streaming;
- a persistent API server entry point backed by SQLite;
- a deterministic bot policy that consumes the same authorized player projection as a normal client;
- headless bot-match automation and deterministic simulation metrics;
- integration coverage for strategic systems, persistence, concurrent commands, event subscriptions, API safety,
  and repeatable bot simulations.

The next planned milestones in `PLAN.md` are v0.9 (first playable client) and v1.0 (hardening/release-quality POC).

## Development

Install the project and development tools with `uv`:

```bash
uv sync --dev
```

Run the canonical local verification gate (all CI is local; GitHub Actions is not used):

```bash
bash scripts/ci.sh
```

Focused test run:

```bash
uv run pytest
```

See `AGENTS.md`, `docs/WORKFLOW.md`, and `docs/LOGGING.md` for the required development, QA, and observability process.

## Run the API

The installed console entry point starts the persistent API server:

```bash
uv run civilization-clone-api
```

By default it binds to `127.0.0.1:8000` and stores games in
`data/civilization_clone.sqlite3`.

Optional environment variables:

- `CIVILIZATION_CLONE_HOST` — bind host;
- `CIVILIZATION_CLONE_PORT` — TCP port;
- `CIVILIZATION_CLONE_DB` — SQLite database path.

The primary routes are:

- `POST /api/v1/games` — create a deterministic game;
- `POST /api/v1/games/{game_id}/commands` — submit an authoritative command;
- `GET /api/v1/games/{game_id}/state?player_id=...` — retrieve a fog-safe player snapshot;
- `GET /api/v1/games/{game_id}/events?player_id=...` — retrieve authorized events;
- `GET /api/v1/games/{game_id}/legal-actions?player_id=...` — inspect available actions/decisions;
- `WS /api/v1/games/{game_id}/events/ws?player_id=...` — subscribe to authorized event updates.

## Persistence and determinism

`SqliteGameStore` persists canonical save documents and the deterministic event journal.
Blocking SQLite work is isolated behind `asyncio.to_thread`, so async API/application callers do not block the event loop.
Reload verifies both state and event hashes and checks the durable event stream for contiguous, immutable content.

The authoritative domain journal never contains wall-clock timestamps or operational logging data.
Runtime logs remain separate and cannot affect state, event ordering, random streams, or hashes.

## AI boundary

The POC bot policy receives only the same player-authorized projection exposed to API clients. It does not receive
an unrestricted `GameSession`, hidden map tiles, or hidden opposing-unit state. Bot commands travel through the same
`CommandEnvelope` and `GameManager.process()` path as human/client commands.

## Logging model

CivilizationClone separates three channels:

- **domain event journal** — deterministic authoritative history used for replay/debugging;
- **runtime logs** — operational structured diagnostics that never affect simulation state;
- **user feedback** — safe typed messages clients can render without exposing internal debug information.

Generated local logs/artifacts belong under ignored `logs/` and `artifacts/` directories.
