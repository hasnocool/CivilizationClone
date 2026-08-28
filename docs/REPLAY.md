# Deterministic Replay Contract

## Purpose

Replay is an independent verification path, not a synonym for loading a saved snapshot. A v1 replay reconstructs a fresh engine from the immutable generated world and reprocesses the accepted authoritative command transcript through the normal command path.

From v1.1 onward replay uses `AdvancedGameEngine`, which delegates every original v1.0 command to the stable base `GameEngine` implementation and adds post-POC command extensions such as bilateral trade. This keeps old commands on their original deterministic path while allowing the replay verifier to understand new accepted command types.

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
4. wraps that state in a fresh `AdvancedGameEngine`;
5. submits every accepted command in transcript order through normal deterministic command processing;
6. fails immediately if an accepted command is rejected during replay;
7. computes the fresh final state hash and event-journal hash;
8. compares both with the live/restored engine;
9. fails verification if either hash differs.

Civilization selection, bilateral trade state/transfers, and all data-driven modifiers are command/state inputs and therefore participate in the same replay/state-hash contract.

This detects state-transition drift as well as event-shape/order drift.

## Corpus

`tests/corpus/replay_cases.json` is the committed deterministic replay corpus. It covers multiple seeds and behavior paths including:

- mixed River Compact/Horizon League civilization selection and starting effects;
- two-player concession/victory;
- three-player active-player elimination and turn handoff;
- settlement founding, production, economy turns, and research;
- war, peace proposal, explicit peace rejection, and subsequent victory;
- v1.1 bilateral trade offer, turn handoff, acceptance, Gold exchange, and continued match flow.

`tests/replay/test_replay_corpus.py` executes every corpus case through `AdvancedGameEngine` and requires both state and event hashes to match independent replay.

## Persistence verification

`GameManager` records accepted commands and passes the complete transcript to `SqliteGameStore` whenever authoritative events are persisted. A newly constructed manager lazily loads both the snapshot and command transcript from SQLite and can call `verify_replay(game_id)` without relying on the prior process's memory.

New games persist `replay_complete=true`. The marker is carried forward on every later save. When reading an older save that has no marker, the store conservatively infers completeness by comparing all event causation command IDs with the durable command IDs instead of assuming that a non-empty transcript is complete.

### Save format v3

v1.1 introduces save-document version 3 because canonical diplomatic relationships now contain:

- an optional immutable pending trade proposal;
- completed-trade count;
- last completed trade turn.

The compatibility rule is intentionally strict:

1. a v1 or v2 document's stored state hash is checked against its **raw historical state mapping before migration**;
2. missing newer fields are then filled with deterministic defaults;
3. the migrated session is restored into `AdvancedGameEngine`;
4. v3 documents additionally require the fully restored post-migration state hash to equal the stored checkpoint;
5. event-journal hashes are verified for every supported save version.

This prevents a migration from silently accepting a corrupted historical save while also avoiding the impossible requirement that a v2 hash equal a v3 canonical structure containing new keys.

## Legacy v0.8 / save-v1 compatibility

Snapshots created before the first v1 release did not store civilization identity or accepted command payloads. The legacy raw state hash is verified before migration; missing civilization identity is then restored to the compatibility default `river_compact`, and v1.1 trade relationship fields default to no pending offer, zero completed trades, and no last-trade turn.

A complete independent command replay cannot be reconstructed from those legacy files. Current code may still load such a snapshot for normal local use, but `GameManager.verify_replay()` marks it explicitly unavailable rather than treating an empty/incomplete transcript as valid.

Crucially, that incomplete provenance is durable. Processing new commands and saving/restarting the migrated game does **not** convert the old history into a complete replay transcript. Start a new game when full independent replay verification is required. This is an explicit compatibility boundary rather than an inferred or lossy certification.

## Save-v2 compatibility

Save-v2 documents already contain civilization identity and replay transcript provenance but predate canonical trade fields. Their original raw state hash is verified first, then the new relationship fields are migrated to deterministic empty defaults. If the transcript is complete, independent replay remains available because the new advanced engine delegates all pre-v1.1 command types to the original v1.0 command implementation.

## Versioning

Replay depends on deterministic rules behavior. Ruleset/save/API versions must therefore be treated deliberately. A future change that intentionally changes deterministic outcomes must either preserve the old ruleset implementation for old saves/replays or explicitly introduce a migration/incompatibility boundary.

Every post-POC phase that changes canonical state must define its save migration and replay behavior before that phase can be considered complete.
