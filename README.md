# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Clients will eventually interact with the same authoritative simulation through a versioned API.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v0.2 hex world and map generation

v0.1 established the deterministic core, event journal, structured diagnostics, typed user feedback,
and local-only agent CI. v0.2 adds the first spatial simulation layer:

- axial `HexCoord` coordinates with six-neighbor, distance, ring, and radius helpers;
- immutable terrain/resource/tile/world-map models;
- deterministic seeded terrain and resource generation;
- deterministic, spread-out passable player spawn selection;
- weighted deterministic A* pathfinding;
- `UNKNOWN` / `DISCOVERED` / `VISIBLE` fog-of-war primitives;
- canonical world-map representation for state hashing/replay;
- deterministic map-generation domain events and operational logging;
- regression tests proving logging configuration does not alter generated state/events.

Turns, units, settlements, persistence, HTTP APIs, AI, and playable clients are later milestones
described in `PLAN.md`.

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
