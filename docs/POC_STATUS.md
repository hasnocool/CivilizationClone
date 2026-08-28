# Proof-of-Concept and Post-POC Roadmap Status

This document maps the current implementation branch to `PLAN.md`. It records implementation scope only; local QA remains authoritative for PASS/FAIL status.

| Milestone | Implementation status | Evidence area |
| --- | --- | --- |
| v0.1 deterministic core/diagnostics | implemented | domain IDs/state/events/feedback, RNG, hashing, logging, rules loader |
| v0.2 hex world/map generation | implemented | hex neighbors/distance/ring/radius/line, deterministic map generation, A*, movement range, visibility |
| v0.3 sessions/turns/players/units | implemented | command processor, movement, turn state, player/unit events |
| v0.4 settlements/economy/effects | implemented | founding, territory, yields, growth, production, generic modifiers |
| v0.5 research/combat/diplomacy/victory | implemented | research DAG, deterministic abstract combat, war/peace offer/accept/reject, elimination/victory |
| v0.6 durable saves/replay | implemented and hardened in v1 | SQLite snapshots/events/idempotency, accepted-command replay verification, legacy replay provenance |
| v0.7 client-agnostic API | implemented and hardened in v1 | FastAPI `/api/v1`, rules discovery, projections, feedback, WebSocket, signed identity, safe request/command diagnostics |
| v0.8 AI/automation | implemented | projection-only bot policy, public civilization research preferences, bot match runner, completion/failure/replay metrics |
| v0.9 first playable client | implemented | `civilization-clone-tui`, public-HTTP-only hotseat play, civilization selection, visible feedback |
| v1.0 POC hardening | implemented | E2E public-client tests, replay corpus, migration coverage, docs, release/playtest scripts, benchmark tooling, multiple graphical client foundations |
| v1.1 advanced diplomacy / atomic trade | implementation complete on feature branch | bilateral trade state/commands/events, participant privacy, save v3 migration, replay corpus, API/legal actions, TUI, deterministic bot trade decisions |

The POC remains the stable v1.0 foundation. v1.1 is the first ordered post-POC phase; later phases are defined in `PLAN.md` through v2.0.

## POC content limits

The implementation keeps the initial content slice intentionally small and original:

- 2 original civilizations: River Compact and Horizon League;
- 4–6 total unit classes including the founder class;
- 4–8 buildings;
- 8–12 technologies;
- 3–5 resource categories;
- 4–6-ish terrain families within the current PLAN guard.

Civilization effects are data-driven rather than engine-specific conditionals. Current definitions exercise starting resources, settlement yield modifiers, research-cost modifiers, abstract combat defense modifiers, research preferences, and future unique-content hooks.

## v0.9 exit path

Local QA must run `bash scripts/playtest_tui.sh` and exercise the real TUI using normal keystrokes. The smoke path should include civilization selection, setup, player switching, fog/map inspection, movement/founding, production/research, multiple turns, diplomacy including offer/accept/reject when practical, abstract combat, authorized events/feedback, persistence restart where applicable, and a victory/concession path.

## v1.0 exit path

Before marking v1.0 release-ready, local QA must provide the `AGENTS.md` QA report contract and execute at minimum:

```bash
bash scripts/ci.sh
uv run civilization-clone-benchmark --games 10 --seed 1000 --max-commands 2000
bash scripts/playtest_tui.sh
bash scripts/release.sh
```

The benchmark should report zero replay failures; material completion/rejection/throughput regressions should be investigated and the machine-specific baseline attached to local QA/release evidence.

`bash scripts/release.sh` intentionally re-runs the canonical CI gate before building artifacts.

## v1.1 exit path

v1.1 is not complete merely because the source changes exist. An execution-capable local agent must run:

```bash
bash scripts/ci.sh
bash scripts/playtest_tui.sh
```

The trade-specific human-style acceptance path should include at minimum:

1. create a 2-player game and inspect both starting Gold balances;
2. as the active player, submit `trade p2 2 1`;
3. switch viewers and verify only the two participants can see the pending terms;
4. make the recipient active through normal research/end-turn flow and run `accept-trade p1`;
5. verify Gold moved exactly once and the completed-trade counter advanced;
6. exercise `reject-trade` and `cancel-trade` paths;
7. create a pending offer and declare war, confirming the offer is cancelled;
8. in a 3-player match, confirm the uninvolved player cannot observe private trade terms/events;
9. persist/restart the match and verify the relationship state restores;
10. run deterministic replay verification and confirm both state and event hashes match.

The canonical automated suite additionally covers accepted-command retry idempotency, rejected-command mutation purity, third-party privacy, v2→v3 save migration, API authorization, bot negotiation behavior, and a committed trade replay-corpus case.

## Current verification state

Implementation in GitHub does not imply tests were executed in this ChatGPT connector environment. The attempted fresh checkout of this feature branch could not resolve `github.com`, and the environment has previously been unable to resolve PyPI as well. Until a connected local development agent runs the commands above, the correct QA status is **`BLOCKED`**, not `PASS`.
