# Deterministic Replay Contract

## Purpose

Replay is an independent verification path, not a synonym for loading a saved snapshot. A v1 replay reconstructs a fresh engine from the immutable generated world and reprocesses the accepted authoritative command transcript through the normal `GameEngine.process()` path.

## Durable inputs

SQLite stores three related but separate forms of data:

1. **snapshot** — current authoritative state plus persisted command-id idempotency results;
2. **event journal** — immutable deterministic events keyed by contiguous event sequence;
3. **accepted command transcript** — immutable accepted commands keyed by contiguous replay sequence.

Operational logs, credentials, wall-clock timestamps, host information, and client rendering state are never replay inputs.

The save document also records a `replay_complete` provenance marker. It says whether the durable command transcript covers the full command-caused event history represented by that snapshot; it is not itself an authoritative gameplay rule.

## Accepted-command transcript

Only a command that was newly accepted and actually appended deterministic events is added to the replay transcript. Idempotent retries return their cached result and do not create a second transcript row.

Each durable command stores:

- command id;
- game id;
- command type;
- authoritative player id when applicable;
- expected state version when supplied;
- immutable payload;
- optional client timestamp as diagnostic envelope data only.

Rows are append-only. Attempting to change an existing sequence or command id is a replay-divergence error.

## Replay algorithm

`verify_replay(engine, commands)`:

1. copies only the initial non-command events (`GameCreated` and deterministic map-generation events);
2. creates a fresh `GameSession` from the same game id, ruleset, seed, immutable world, and victory-turn configuration;
3. initializes a fresh event journal from the initial events;
4. submits every accepted command in transcript order through the normal command processor;
5. fails immediately if an accepted command is rejected during replay;
6. computes the fresh final state hash and event-journal hash;
7. compares both with the live/restored engine;
8. fails verification if either hash differs.

Civilization selection and all data-driven civilization modifiers are command/state inputs and therefore participate in the same replay/state-hash contract.

This detects state-transition drift as well as event-shape/order drift.

## Corpus

`tests/corpus/replay_cases.json` is the committed deterministic replay corpus. It covers multiple seeds and behavior paths including:

- mixed River Compact/Horizon League civilization selection and starting effects;
- two-player concession/victory;
- three-player active-player elimination and turn handoff;
- settlement founding, production, economy turns, and research;
- war, peace proposal, explicit peace rejection, and subsequent victory.

`tests/replay/test_replay_corpus.py` executes every corpus case and requires both state and event hashes to match replay.

## Persistence verification

`GameManager` records accepted commands and passes the complete transcript to `SqliteGameStore` whenever authoritative events are persisted. A newly constructed manager lazily loads both the snapshot and command transcript from SQLite and can call `verify_replay(game_id)` without relying on the prior process's memory.

New v1 games persist `replay_complete=true`. The marker is carried forward on every later save. When reading an older save that has no marker, the store conservatively infers completeness by comparing all event causation command IDs with the durable command IDs instead of assuming that a non-empty transcript is complete.

## Legacy v0.8 save compatibility

Snapshots created before v1 did not store civilization identity or accepted command payloads. The legacy raw state hash is verified before migration; missing civilization identity is then restored to the v1 compatibility default `river_compact`.

A complete independent command replay cannot be reconstructed from those legacy files. v1 may still load such a snapshot for normal local use, but `GameManager.verify_replay()` marks it explicitly unavailable rather than treating an empty/incomplete transcript as valid.

Crucially, that incomplete provenance is durable. Processing new v1 commands and saving/restarting the migrated game does **not** convert the old history into a complete replay transcript. Start a new v1 game when full independent replay verification is required. This is an explicit compatibility boundary rather than an inferred or lossy certification.

## Versioning

Replay depends on deterministic rules behavior. Ruleset/save/API versions must therefore be treated deliberately. A future change that intentionally changes deterministic outcomes must either preserve the old ruleset implementation for old saves/replays or explicitly introduce a migration/incompatibility boundary.
