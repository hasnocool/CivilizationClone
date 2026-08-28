# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Clients will eventually interact with the same authoritative simulation through a versioned API.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v0.1 deterministic core

v0.1 establishes the foundations required by later engine milestones:

- Python 3.12+ package layout;
- typed domain identifiers and common core state;
- deterministic SplitMix64-based random streams;
- immutable command and event envelopes;
- canonical state serialization and SHA-256 hashing;
- strict, versioned JSON ruleset manifest loading;
- deterministic in-memory domain event journal;
- structured runtime/debug logging and typed user feedback;
- deterministic tests and agent-operated local-only CI.

Map generation, turns, units, settlements, persistence, HTTP APIs, AI, and playable clients are later
milestones described in `PLAN.md`.

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
