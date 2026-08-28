# Proof-of-Concept Roadmap Status

This document maps the current implementation branch to `PLAN.md`. It records implementation scope only; local QA remains authoritative for PASS/FAIL status.

| Milestone | Implementation status | Evidence area |
| --- | --- | --- |
| v0.1 deterministic core/diagnostics | implemented | domain IDs/state/events/feedback, RNG, hashing, logging, rules loader |
| v0.2 hex world/map generation | implemented | hex utilities, deterministic map generation, pathfinding, visibility |
| v0.3 sessions/turns/players/units | implemented | command processor, movement, turn state, player/unit events |
| v0.4 settlements/economy/effects | implemented | founding, territory, yields, growth, production, modifiers |
| v0.5 research/combat/diplomacy/victory | implemented | research DAG, deterministic combat, war/peace, elimination/victory |
| v0.6 durable saves/replay | implemented and hardened in v1 | SQLite snapshots/events/idempotency plus accepted-command replay verification |
| v0.7 client-agnostic API | implemented and hardened in v1 | FastAPI `/api/v1`, projections, feedback, WebSocket, signed identity |
| v0.8 AI/automation | implemented | projection-only bot policy, bot match runner, metrics |
| v0.9 first playable client | implemented | `civilization-clone-tui`, public-HTTP-only hotseat play |
| v1.0 POC hardening | implementation complete on feature branch | e2e public-client test, replay corpus, docs, release/playtest scripts, benchmark tooling |

## v0.9 exit path

Local QA must run `bash scripts/playtest_tui.sh` and exercise the real TUI using normal keystrokes. The smoke path should include setup, player switching, fog/map inspection, movement/founding, production/research, multiple turns, diplomacy/combat when practical, authorized events/feedback, persistence restart where applicable, and a victory/concession path.

## v1.0 exit path

Before marking v1.0 release-ready, local QA must provide the `AGENTS.md` QA report contract and execute at minimum:

```bash
bash scripts/ci.sh
uv run civilization-clone-benchmark --games 10 --seed 1000 --max-commands 2000
bash scripts/playtest_tui.sh
bash scripts/release.sh
```

`bash scripts/release.sh` intentionally re-runs the canonical CI gate before building artifacts.

## Current verification state

Implementation in GitHub does not imply tests were executed in this ChatGPT connector environment. Until a local development agent runs the commands above, the correct QA status is `BLOCKED`, not `PASS`.
