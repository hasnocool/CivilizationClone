# CivilizationClone — Proof-of-Concept Engine Plan

## 1. Purpose

CivilizationClone is a **headless, deterministic, turn-based 4X strategy engine** exposed through stable application/API boundaries so that any client can play the same authoritative simulation.

Possible clients include web, desktop, terminal/TUI, mobile, Godot/Unity/Unreal or another renderer, Discord/chat-style clients, AI agents, automated play-test harnesses, and replay/spectator tools.

The engine owns rules and state. Clients only submit commands and render authorized projections, events, and user feedback.

The design is informed by public official Firaxis/2K Civilization documentation, but CivilizationClone must use **original implementation, balance, names, text, rules data, art, audio, maps, and content**. Do not copy proprietary Civilization data or assets.

This project is not affiliated with or endorsed by Firaxis Games, 2K, or Take-Two.

---

## 2. Official design references

Primary design references:

- Civilization franchise overview: https://civilization.2k.com/
- Civilization VI official overview: https://civilization.2k.com/en-GB/civ-vi/
- Civilization support/manual resources: https://support.civilization.com/
- Civilization VII official site/game-guide hub: https://civilization.2k.com/seven/
- Civilization VII — Managing Your Empire dev diary: https://civilization.2k.com/civ-vii/archive/dev-diary/managing-your-empire/
- Civilization VII game-guide archive: https://civilization.2k.com/civ-vii/game-guide/

Broad design lessons used here:

1. turn-based 4X structure;
2. spatial tile/hex world;
3. exploration and fog of war;
4. settlement growth and territorial development;
5. resource/economic management;
6. technology and cultural/social progression;
7. military movement and combat;
8. diplomacy and changing relationships;
9. data-driven leader/civilization modifiers;
10. multiple paths to victory;
11. late-game automation/specialization to reduce micromanagement;
12. rules and presentation should remain separable.

---

## 3. Proof-of-concept success criteria

The POC is complete when two or more players can finish a small deterministic game entirely through the public engine/API surface.

A complete POC match must be able to:

1. create a seeded game;
2. generate a hex map;
3. configure/join players;
4. spawn starting units;
5. explore hidden territory;
6. found settlements;
7. work territory and generate yields;
8. queue production;
9. research technologies;
10. move and fight units;
11. conduct basic diplomacy;
12. advance authoritative turns;
13. persist/reload a game;
14. replay from the deterministic event journal;
15. expose useful runtime diagnostics;
16. expose safe user-facing feedback;
17. detect and finalize victory;
18. reconstruct authorized client state/events without leaking hidden state.

### Initial POC limits

- 2–4 players;
- one map layer;
- small/medium hex maps;
- one simplified historical-style phase/era;
- 4–6 terrain types;
- 3–5 resources;
- 4–6 unit classes;
- 4–8 buildings;
- 8–12 technologies;
- 2 original civilization definitions;
- simple war/peace diplomacy;
- score and conquest-style victory;
- deterministic simple AI.

---

## 4. Core architecture

The simulation has **no dependency on a graphical client or HTTP framework**.

```text
CLIENTS
  Web / TUI / Desktop / Mobile / Godot / Bots / Tests
                    |
                    v
            API / CLIENT ADAPTERS
       commands / queries / feedback / events
                    |
                    v
             APPLICATION LAYER
        sessions / command routing / actors
                    |
                    v
            DOMAIN / ENGINE CORE
 map / units / settlements / economy / research / combat
 diplomacy / visibility / victory / deterministic event journal
                    |
                    v
               PERSISTENCE
       snapshots / durable events / configs

Operational side-channel (not authoritative state):
  structured runtime/debug logs -> console/files/support tools
```

### Fundamental rule

Clients request actions; they never directly mutate authoritative state.

```text
MoveUnitCommand
    -> validate identity/ownership/turn
    -> validate movement and destination
    -> resolve deterministic rule effects
    -> mutate authoritative state
    -> emit immutable UnitMoved event
    -> append event to deterministic journal
    -> increment/record state version
    -> publish authorized projection/event
    -> produce safe user feedback if needed
    -> write operational diagnostic logs as a side effect only
```

---

## 5. Technology direction

Target **Python 3.12+**.

POC direction:

- FastAPI for later HTTP/WebSocket API;
- Pydantic v2 at transport/application boundaries later;
- asyncio/AnyIO for non-blocking network/persistence work;
- SQLAlchemy 2 async persistence APIs later;
- SQLite WAL for local POC persistence;
- PostgreSQL as a possible production persistence target;
- Alembic once migrations exist;
- stdlib `logging` with structured JSON support for runtime diagnostics;
- pytest + pytest-asyncio;
- Hypothesis where property/state-machine testing is useful;
- Ruff;
- Pyright or strict mypy;
- `uv` project/dependency management.

### Async/concurrency rule

Do not allow arbitrary concurrent writes to one game object.

Each running game uses one serialized state-mutation stream (actor/mailbox or equivalent). API requests may arrive concurrently, but state-changing commands for a game are processed in deterministic order.

CPU-heavy AI/pathfinding may later run against immutable snapshots in workers, but workers return proposed commands; they never mutate authoritative state.

Never block an async event loop with synchronous disk/network operations. Use async-native libraries or explicit worker/thread boundaries when unavoidable.

---

## 6. Domain model

### `Game`

- game id;
- ruleset id/version;
- seed;
- current turn/phase/status;
- state version;
- player order;
- world/map id;
- victory configuration;
- deterministic RNG stream states/identifiers;
- deterministic event-journal sequence.

### `Player`

- player id;
- controller type human/bot;
- civilization/profile;
- treasury/resources;
- research;
- diplomacy;
- fog/known map;
- settlements;
- units;
- score/victory progress;
- eliminated flag.

### `CivilizationDefinition`

Data-driven rather than subclass-specific logic:

- id/display name/tags;
- starting bonuses;
- passive modifiers;
- unique unit/building references;
- research/economy/combat modifiers.

POC content is original fictional/test content.

### `WorldMap` and `Tile`

Use axial hex coordinates `(q, r)` internally. Tiles contain terrain/features/resources, yields, movement/passability, defense, settlement/occupancy references, and later territory/improvement references.

### `Settlement`

- id/owner/center;
- population;
- food/growth;
- production/build queue;
- territory/worked tiles;
- buildings;
- defense;
- generated yields/modifiers.

### `Unit`

- id/owner/definition;
- position;
- hit points;
- movement/actions;
- combat/range;
- experience/promotions later;
- statuses.

### `TechnologyDefinition`

Generic prerequisite DAG with id/cost, prerequisites, unlocks, modifiers, and tags. The same progression machinery should later support civics/social development.

### `DiplomaticRelationship`

Contact, peace/war, pending proposals, and later treaties/history.

### `VictoryTracker`

Pluggable conditions. POC includes maximum-turn score and conquest/elimination. Later add science/progression, culture/influence, diplomacy, and scenario objectives.

---

## 7. Hex-map subsystem

Required utilities:

- six-neighbor lookup;
- hex distance;
- ring/radius queries;
- line queries;
- movement range;
- A* pathfinding;
- terrain costs/passability;
- occupancy;
- spawn validation;
- territory;
- visibility/fog.

### Deterministic map generation

1. derive map RNG stream;
2. generate land/water mask;
3. assign terrain;
4. place features;
5. place resources;
6. identify valid start regions;
7. normalize starts with deterministic scoring;
8. serialize map definition.

Same seed + ruleset version must produce the same map.

---

## 8. Fog of war and projections

Visibility states:

- `UNKNOWN` — never observed;
- `DISCOVERED` — observed before, dynamic details hidden;
- `VISIBLE` — currently observable.

```text
Authoritative GameState
  -> project(player_a)
  -> project(player_b)
  -> project(admin/debug)
```

Player clients, event streams, user feedback, and normal player logs must not expose unauthorized hidden state.

---

## 9. Economy/yields

POC yield types: Food, Production, Gold, Science, and Culture. Use extensible typed yield maps.

```text
tile yields
+ buildings
+ civilization modifiers
+ temporary effects
- maintenance/penalties
= settlement yields
= empire totals
```

---

## 10. Modifier/effect system

Avoid civilization-specific conditionals in engine internals.

Typed modifier concepts include flat/percentage yield, terrain yield, combat, movement, build/research cost, upkeep, visibility, growth, and conditional triggers.

Each modifier includes source, target selector, operation, value, conditions, duration, stacking policy, and priority/order.

---

## 11. Turn model

POC: sequential players with explicit end-turn commands, while preserving a future path to simultaneous-turn multiplayer.

```text
GLOBAL TURN START
 -> active-player start
 -> refresh actions
 -> recurring economy/growth/research
 -> accept legal commands
 -> ensure mandatory choices complete
 -> active-player end
 -> next player
 -> GLOBAL TURN END
 -> global effects
 -> victory check
 -> optional snapshot
 -> next turn
```

Mandatory decisions must be queryable so clients can explain rejected `EndTurn` requests.

---

## 12. Command model

All state mutation uses commands.

POC commands include `CreateGame`, `JoinGame`, `StartGame`, `MoveUnit`, `AttackUnit`, `FoundSettlement`, `SetWorkedTile`, `QueueProduction`, `CancelProduction`, `ChooseResearch`, `DeclareWar`, `OfferPeace`, `AcceptPeace`, `EndTurn`, and `Concede`.

Command envelope includes command id, game id, player id when applicable, expected state version, command type, immutable payload, and optional client timestamp for diagnostics only.

### Idempotency

`command_id` must be unique per game. Retrying the same command returns/reuses the original result rather than applying the mutation twice.

---

## 13. Deterministic domain event model

Successful commands produce immutable events such as `GameCreated`, `GameStarted`, `TurnStarted`, `UnitMoved`, `UnitAttacked`, `UnitDamaged`, `UnitDestroyed`, `SettlementFounded`, production/research events, diplomacy events, turn events, elimination, and victory.

Events support replay, debugging, auditability, client updates, spectator tools, deterministic tests, and AI analysis.

---

## 14. Event logging, runtime logging, diagnostics, and user feedback

The project has **three distinct channels**. They must remain separate.

### 14.1 Deterministic domain event journal

Every successful state-changing command appends immutable events to a game-scoped ordered journal.

The journal is authoritative simulation history and therefore deterministic.

Journal requirements:

- one game id per journal;
- strictly contiguous/monotonic event sequence;
- state version must not move backwards;
- immutable event payloads;
- causation command id when known;
- reproducible ordering from the same seed + command stream;
- suitable for canonical hashing/replay verification;
- in-memory implementation is acceptable initially;
- durable append-only storage arrives later without changing semantics.

Do **not** place wall-clock timestamps, process ids, hostnames, debug levels, filesystem paths, or other operational information in deterministic event payloads unless explicitly modeled as authoritative game data.

### 14.2 Runtime/debug logging

Operational diagnostics are separate from game history.

Structured runtime logs should support fields such as timestamp, level, logger/component, message, game id, command id, event id, turn, state version, operation/action, error code, and exception details when appropriate.

Runtime logs may be human-readable or JSON lines.

Critical invariant: changing logging level, destination, formatter, or enabling/disabling logging **must never** change RNG consumption, authoritative state, event ordering, event payloads, state hashes, or replay outcome.

Never log secrets, credentials, private tokens, or unrestricted hidden-player state.

### 14.3 User-facing feedback

Debug logs are not a user interface.

Expected outcomes/rejections should produce typed safe feedback containing a stable code, severity (`info`, `warning`, `error`), human-readable message, and small safe structured context.

Examples include `MOVE_REJECTED`, `STALE_STATE_VERSION`, `MANDATORY_CHOICE_REQUIRED`, `SAVE_COMPLETED`, and `RULESET_LOAD_FAILED`.

Feedback must not expose stack traces, secrets, internal filesystem paths, raw database errors, or hidden opponent information.

### 14.4 Local diagnostic artifacts

Agents may persist ignored local artifacts under:

```text
logs/
artifacts/
```

Failure reports should preserve useful logs/traces/screenshots and cite local paths when appropriate.

---

## 15. Deterministic randomness

Never use uncontrolled global randomness for simulation rules.

All random outcomes derive from root game seed, deterministic named stream/category, and stable command/event context when needed.

Suggested streams: map generation, combat, neutral events, and AI tie-breaking.

RNG algorithm behavior is regression-tested with known vectors. RNG state must be serializable/restorable.

---

## 16. Combat POC

Use original configurable formulas, not Civilization formulas. Include melee/ranged categories, attack/defense strength, hit points, terrain modifiers, deterministic RNG variation, destruction, action consumption, and ownership/war validation.

Later: zones of control, fortifications, siege, promotions, naval/air, support, retreat, supply/logistics.

---

## 17. Settlement POC

Founder establishes settlement; center becomes controlled; settlement works controlled tiles; yields accumulate; food advances growth; production advances build queue; population increases workable capacity; buildings add modifiers; completed units spawn legally.

Territorial growth can begin simplified and deterministic.

---

## 18. Research POC

Implement a generic prerequisite DAG. Science advances selected research each turn and completion emits deterministic events/unlocks. The same progression engine should support later civics/social development.

---

## 19. Diplomacy POC

Initial states: unknown, contacted, peace, war, and pending peace proposal. Commands include declare war, offer peace, and accept/reject peace.

Later: trade, alliances, borders, influence, grievances, reputation, joint wars, and independent powers.

---

## 20. AI architecture

Bots consume the **same legal command interface** as human clients.

```text
Authorized GameSnapshot
 -> BotPolicy.choose_commands(...)
 -> normal validated commands
```

POC priorities: explore, find settlement location, maintain production, choose research, defend, attack favorable targets, end turn.

Normal bots do not receive hidden state.

---

## 21. API direction

Use `/api/v1` from the first HTTP endpoint.

Planned areas: game lifecycle, commands, state/projection queries, legal actions/mandatory decisions, event subscriptions/WebSockets, safe user feedback, and separated admin/debug endpoints.

Transport handlers translate requests into application commands/queries and contain no game rules.

---

## 22. Persistence and replay direction

Persistence will store game metadata, immutable durable event journal, periodic snapshots, ruleset/version metadata, and processed command ids/idempotency results.

Replay algorithm:

1. load initial state/ruleset/seed;
2. consume ordered command/event history according to the defined model;
3. reproduce state transitions;
4. compare event sequence/checkpoint hashes;
5. report first divergence with useful diagnostics.

Operational runtime logs are **not** replay input.

---

## 23. Repository structure

```text
CivilizationClone/
├── PLAN.md
├── AGENTS.md
├── README.md
├── pyproject.toml
├── docs/
│   ├── WORKFLOW.md
│   └── LOGGING.md
├── scripts/
│   └── ci.sh
├── src/civilization_clone/
│   ├── domain/
│   │   ├── ids.py
│   │   ├── state.py
│   │   ├── events.py
│   │   └── feedback.py
│   ├── engine/
│   │   ├── commands.py
│   │   ├── event_log.py
│   │   ├── rng.py
│   │   ├── state_hash.py
│   │   ├── reducer.py
│   │   ├── turns.py
│   │   ├── movement.py
│   │   ├── combat.py
│   │   ├── economy.py
│   │   ├── effects.py
│   │   └── visibility.py
│   ├── observability/
│   │   └── logging.py
│   ├── rules/
│   ├── application/
│   ├── persistence/
│   ├── api/
│   └── ai/
├── content/poc/
├── tests/
├── logs/       # ignored local diagnostics
└── artifacts/  # ignored local QA artifacts
```

**Do not add `.github/workflows/`; GitHub Actions is not used.**

---

## 24. Testing strategy

Determinism is first-class.

### Unit tests

Cover ids/common state, hex math/pathfinding, movement, yields, research, combat, visibility, modifiers, victory, event-journal invariants, feedback safety, and logging formatter/context.

### Property/invariant tests

Examples:

- hex distance is symmetric;
- movement never ends illegally;
- destroyed units cannot act;
- yield totals are independent of dictionary iteration order;
- same input produces same final state hash;
- same input produces same deterministic event journal;
- event sequence rejects duplicates/gaps/out-of-order entries;
- command retries do not apply twice;
- player projection never reveals undiscovered enemy unit;
- runtime logging enabled/disabled does not alter deterministic result;
- user feedback does not expose debug-only details.

### Integration tests

Run scripted games through command bus and verify event/log/state behavior.

### API tests

Cover create/start, commands, stale version, idempotency, event ordering, feedback contract, fog filtering, and later WebSocket ordering.

### Simulation tests

Run bot-vs-bot matches and collect completion rate, turns, victory distribution, command failures, replay divergence, and performance.

---

## 25. Observability

Runtime metrics/diagnostics should eventually include command latency, turn-resolution latency, pathfinding latency, AI decision latency, active games, command/event counts, snapshot size, replay failures, invalid-command reasons, subscribers/connections, and error counts by stable code.

Operational log records should include correlation identifiers where available.

---

## 26. Security and multiplayer authority

Even in the POC:

- server/engine owns authoritative state;
- identity is not trusted from arbitrary payload fields;
- ownership/authorization checks precede mutations;
- hidden state is filtered server-side;
- payload/ruleset input is validated;
- admin/debug surfaces are separate;
- logs and feedback avoid secrets/hidden state;
- normal client event feeds are authorized projections, not raw internal history.

---

## 27. Performance principles

- do not prematurely optimize;
- no blocking disk/network calls in async handlers;
- serialized mutation stream per game;
- immutable snapshots for readers;
- coordinate-indexed map access;
- bounded pathfinding;
- batch persistence safely;
- compact typed events;
- structured logging should be configurable and avoid expensive debug work when disabled;
- logging must not become part of simulation timing/order assumptions.

A small POC should run many automated turns per second.

---

## 28. Local-only CI policy

This project **does not use GitHub Actions or paid hosted CI**.

All verification runs locally by development agents/humans.

Canonical local CI command:

```bash
bash scripts/ci.sh
```

The local CI/QA process owns dependency/environment validation, formatting/linting, type checking, tests, determinism/replay/event-journal verification, logging/feedback safety checks, build/package checks, and interactive playtests when applicable.

Pull requests contain the exact local QA evidence. GitHub is used for source control, issues, review, PRs, and releases only.

Do not create `.github/workflows/` files or require GitHub status checks for merging.

---

## 29. Milestone roadmap

### v0.1 — Repository, deterministic core, and diagnostics foundation

Deliver:

- Python project skeleton;
- local CI/lint/type/test configuration;
- typed IDs/common models;
- seeded RNG service;
- command/event envelope primitives;
- canonical state hashing;
- basic ruleset loader;
- deterministic in-memory event journal;
- structured runtime/debug logging foundation;
- typed safe user-feedback primitives;
- tests proving logging does not alter deterministic results;
- no GitHub Actions workflow.

Exit criteria:

- same seed produces same deterministic test result;
- fixed RNG vectors pass;
- event-journal invariants pass;
- same deterministic event list hashes identically;
- runtime logging on/off does not alter state hash;
- feedback primitives are immutable/safe;
- complete local agent CI passes in a connected dev environment.

### v0.2 — Hex world and map generation

Deliver axial coordinates, tile model, neighbor/distance/ring utilities, deterministic terrain/resources/spawn selection, A* pathfinding, fog primitives, and map-generation events/logging/diagnostics.

Exit: deterministic maps plus pathfinding/visibility coverage.

### v0.3 — Game sessions, turns, players, units

Deliver game/player aggregates, units, movement, turn state machine, validation, command handling, event emission/journal append integration, useful runtime logs, and safe command feedback.

Exit: two scripted players move for multiple turns deterministically with stable event journals.

### v0.4 — Settlements, economy, effects

Deliver founding/territory/worked tiles, yields/growth, build queues/buildings/unit production, generic modifier/effect pipeline, and economy events/diagnostics/feedback.

Exit: functioning settlements produce units/buildings deterministically.

### v0.5 — Research, combat, diplomacy, victory

Deliver technology DAG/progress, deterministic combat variation, war/peace, elimination, score/conquest victory, safe player feedback, and detailed debug diagnostics.

Exit: legal complete game reaches victory through commands alone.

### v0.6 — Durable event store, saves, replay

Build on the v0.1 event-journal contract:

- async SQLite repositories;
- durable append-only event storage;
- command idempotency persistence;
- snapshots;
- reload;
- replay verifier;
- divergence diagnostics and state-hash checkpoints.

Exit: save/reload preserves state and replay final hash equals live hash.

### v0.7 — Client-agnostic API

Deliver FastAPI `/api/v1`, lifecycle/command/query routes, OpenAPI, player projections, WebSocket authorized event stream, typed user feedback responses, structured request/command logs, and non-blocking persistence integration.

Exit: entire game playable through HTTP/WebSocket only.

### v0.8 — Basic AI and automation harness

Deliver deterministic bot-policy interface, simple bot, bot-vs-bot runner, simulation metrics, headless fast-forward, and AI-decision diagnostics without hidden-state cheating.

### v0.9 — First playable client

Deliver a minimal client (TUI or simple web client) using only public API contracts.

Exit: local QA can human-style playtest a complete match with keystrokes/clicks and verify visible feedback.

### v1.0 — POC hardening

Deliver complete end-to-end test/playtest suite, deterministic replay corpus, documentation, local release/build scripts, performance baseline, stable public POC contracts, and no hosted CI dependency.

---

## 30. Post-POC directions

Possible later work includes larger worlds/eras, richer original culture/religion/influence systems, espionage, trade networks, advanced diplomacy, simultaneous turns, mod/plugin SDK, scenario editor, stronger AI planning, deterministic multiplayer experiments, richer replay/spectator tools, multiple 2D/3D clients, and performance/distributed simulation tooling.

The architectural rule remains: **one authoritative deterministic engine, many clients**.
