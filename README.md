# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Clients will eventually interact with the same authoritative simulation through a versioned API.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v0.3 game sessions, turns, players, and units

v0.1 established deterministic engine foundations and local-only agent CI. v0.2 added the hex world,
seeded map generation, pathfinding, and fog primitives. v0.3 adds the first playable simulation loop:

- authoritative `GameSession`, `PlayerState`, and `UnitState` models;
- human/bot controller metadata and typed unit definitions;
- deterministic player join and game-start commands;
- deterministic starting-unit placement on generated map spawns;
- sequential active-player turns with movement refresh;
- validated adjacent movement, terrain costs, passability, and occupancy checks;
- per-player fog updates as units move;
- in-memory command idempotency and optimistic `state_version` rejection;
- deterministic game, turn, spawn, movement, and player events appended to one event journal;
- safe typed feedback for rejected commands;
- structured command/runtime logging that cannot affect state or event hashes;
- multi-turn deterministic integration tests.

Settlements/economy, research/combat/diplomacy/victory, durable persistence, HTTP APIs, AI, and a
playable client remain later milestones described in `PLAN.md`.

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

## Logging model

CivilizationClone separates three channels:

- **domain event journal** — deterministic authoritative history used for replay/debugging;
- **runtime logs** — operational structured diagnostics that never affect simulation state;
- **user feedback** — safe typed messages clients can render without exposing internal debug information.

Generated local logs/artifacts belong under ignored `logs/` and `artifacts/` directories.
