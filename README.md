# CivilizationClone

CivilizationClone is an original, headless, deterministic, turn-based 4X strategy engine.
Clients will eventually interact with the same authoritative simulation through a versioned API.

This repository does **not** bundle proprietary Civilization game data, rules text, art, maps, UI,
or other protected assets. The project uses original implementation and content.

## Current milestone: v0.4 settlements, economy, and effects

The engine now includes the deterministic core, hex world, game sessions/turns/units, and a working
settlement economy:

- founder units can establish settlements and are consumed by founding;
- settlements control a deterministic center-and-neighbor territory;
- population limits how many additional controlled tiles can be worked;
- Food, Production, Gold, Science, and Culture use typed deterministic yield bundles;
- terrain/resources generate original POC yields;
- end-turn resolution accumulates yields and deterministic population growth;
- production queues support cancellation, buildings, and produced units;
- granary/workshop examples exercise a generic ordered yield-modifier pipeline;
- produced units receive deterministic IDs and legal spawn positions;
- settlement/economy actions emit deterministic domain events and safe feedback;
- logging remains operational-only and cannot alter state or event hashes.

Research, combat, diplomacy, victory, durable persistence/replay, HTTP APIs, AI, and a playable client
remain later milestones described in `PLAN.md`.

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
