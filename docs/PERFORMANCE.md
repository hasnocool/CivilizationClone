# Performance Baseline

Performance measurements are operational diagnostics, never authoritative simulation inputs. Timing data must not affect RNG consumption, command order, event payloads, state hashes, or replay outcomes.

## Standard local benchmark

```bash
uv run civilization-clone-benchmark --games 10 --seed 1000 --max-commands 2000
```

The benchmark runs deterministic two-player bot matches in-process and reports JSON containing:

- simulation and replay-verification elapsed time;
- total/accepted/rejected commands and rejection rate;
- total turns;
- commands/second and turns/second for the simulation phase;
- finished-game count and completion rate;
- victory distribution, including unfinished matches;
- replay failure count/rate;
- per-match completion/victory information;
- per-match replay-match status;
- per-match deterministic state and event hashes.

Every measured game is independently replayed after simulation. A replay mismatch is counted as a benchmark failure signal even if the live match otherwise completed.

The time-based fields are intentionally non-deterministic diagnostics. State/event hashes and replay results must remain deterministic for the same software/ruleset/seed and command behavior.

## Release baseline procedure

Before a v1 release candidate:

1. run `bash scripts/ci.sh`;
2. run the standard benchmark on the target development machine;
3. require zero replay failures and investigate material command rejection/completion anomalies;
4. save the JSON output under ignored `artifacts/` with machine/runtime notes;
5. rerun at least one identical seed set and confirm deterministic hashes match;
6. investigate material throughput regressions before release;
7. record the measured baseline in the pull request/release notes rather than committing machine-specific numbers as universal requirements.

The POC goal from `PLAN.md` is that a small match can execute many automated turns per second. No universal numeric threshold is hard-coded because CPU, Python build, power state, and platform differ materially.

## Hot paths to watch

- command processing latency;
- turn/economy/research resolution;
- pathfinding and movement-range queries;
- bot decision latency;
- snapshot encoding and SQLite persistence;
- replay verification;
- projection/event filtering;
- subscriber fan-out;
- runtime log-handler latency.

Performance work must preserve deterministic ordering and the per-game serialized mutation rule. CPU-heavy future work may use immutable snapshots in workers, but workers may only propose commands; they never mutate authoritative game state.
