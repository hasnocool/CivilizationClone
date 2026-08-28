# CivilizationClone — Proof-of-Concept Engine Plan

## 1. Purpose

CivilizationClone will be a **headless, deterministic, turn-based 4X strategy engine** exposed through a versioned API so that any client can play the same game: web UI, desktop UI, terminal/TUI, mobile app, Discord-style bot, AI agent, automated test harness, or a future 2D/3D client.

The engine is inspired by the long-running design patterns documented publicly by Firaxis/2K for the Sid Meier's Civilization series: exploration, territorial expansion, resource/economic development, technological and cultural progression, diplomacy, warfare, distinct civilizations/leaders, and multiple paths to victory.

The proof of concept should prove that those systems can be modeled **without coupling simulation rules to presentation**.

> Important boundary: this project should use original implementation, original balance values, original text, and original content definitions. Official Civilization documentation is a design reference only. Do not copy proprietary game data, Civilopedia text, art, audio, leader likenesses, maps, UI, balance tables, or other protected content. The project is not affiliated with or endorsed by Firaxis Games, 2K, or Take-Two.

---

## 2. Official design references

Primary official references used when planning this project:

- Civilization franchise overview: https://civilization.2k.com/
- Civilization VI official overview: https://civilization.2k.com/en-GB/civ-vi/
- Civilization support/manual resources: https://support.civilization.com/
- Civilization VII official site/game-guide hub: https://civilization.2k.com/seven/
- Civilization VII — Managing Your Empire dev diary: https://civilization.2k.com/civ-vii/archive/dev-diary/managing-your-empire/
- Civilization VII game-guide archive: https://civilization.2k.com/civ-vii/game-guide/

The useful design lessons are broader than any one Civilization release:

1. Civilization is fundamentally a **turn-based 4X game**.
2. The world is spatial and tile-based; modern entries use **hexagonal maps**.
3. Players explore unknown territory, settle and develop territory, exploit resources, and compete/cooperate with other powers.
4. Cities/settlements are core economic entities.
5. Research and social/cultural progression unlock capabilities over time.
6. Military units occupy and move through the world and resolve combat under deterministic rules plus controlled randomness.
7. Diplomacy changes relationships between players over time.
8. Different leaders/civilizations modify the base rules through data-driven abilities.
9. Victory is not limited to conquest; the engine should support multiple configurable victory trackers.
10. Late-game micromanagement and runaway snowballing are known design problems, so systems should support automation, batching, specialization, soft caps, and catch-up mechanics later without rewriting the engine.

---

## 3. Proof-of-concept goal

The POC is complete when two or more players can finish a small deterministic game entirely through the API.

A complete POC match should support this loop:

1. Create a game with a seed and configuration.
2. Generate a hex map.
3. Join/select a player profile and an original test civilization.
4. Spawn starting units.
5. Explore hidden tiles.
6. Found settlements.
7. Work territory and generate yields.
8. Queue production.
9. Research technologies.
10. Move units and fight another player.
11. Conduct basic diplomacy.
12. End turns through an authoritative turn controller.
13. Persist and reload the match.
14. Replay the match from its event log.
15. Detect a victory condition and finalize the game.
16. Allow any client to reconstruct its permitted view of state from the API.

### Initial POC match limits

Keep the first playable slice intentionally small:

- 2–4 players.
- One map layer.
- Small/medium hex maps.
- One historical-style era/phase rather than a full human-history timeline.
- 4–6 terrain types.
- 3–5 resource types.
- 4–6 unit classes.
- 4–8 buildings.
- 8–12 technologies.
- 2 original civilization definitions.
- Basic war/peace diplomacy.
- Score and conquest-style victory conditions.
- Simple AI opponent.

The architecture must support later expansion without requiring those larger systems in the POC.

---

## 4. Core architecture principle

The simulation engine must have **no dependency on a graphical client or HTTP framework**.

```text
                         ┌──────────────────────────────┐
                         │           CLIENTS            │
                         │                              │
                         │ Web / TUI / Desktop / Bot   │
                         │ Mobile / AI Agent / Tests   │
                         └──────────────┬───────────────┘
                                        │
                                 REST / WebSocket
                                        │
                         ┌──────────────▼───────────────┐
                         │          API LAYER           │
                         │ auth • commands • queries    │
                         │ projections • subscriptions  │
                         └──────────────┬───────────────┘
                                        │
                              typed command boundary
                                        │
                         ┌──────────────▼───────────────┐
                         │      GAME APPLICATION        │
                         │ game sessions • turn actor   │
                         │ command routing • snapshots  │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │       DOMAIN / ENGINE        │
                         │ deterministic game rules     │
                         │ map • cities • units • AI    │
                         │ economy • research • combat  │
                         └──────────────┬───────────────┘
                                        │
                               events / snapshots
                                        │
                         ┌──────────────▼───────────────┐
                         │        PERSISTENCE           │
                         │ event log • saves • configs  │
                         └──────────────────────────────┘
```

### Design rule

Clients **request actions**; they never directly mutate game state.

For example:

```text
MoveUnitCommand
      ↓
validate ownership
validate turn
validate movement budget
validate destination
resolve movement
update authoritative state
emit UnitMoved event
increment state version
publish player-visible event
```

---

## 5. Technology direction

Target Python **3.12+**.

Recommended stack for the POC:

- FastAPI for the HTTP API.
- Pydantic v2 models for API/domain boundary schemas.
- Uvicorn for ASGI serving.
- `asyncio`/AnyIO for non-blocking network and persistence operations.
- SQLAlchemy 2 async APIs for persistence boundaries.
- SQLite in WAL mode for local POC development.
- PostgreSQL as the intended production persistence option.
- Alembic for schema migrations.
- pytest + pytest-asyncio for tests.
- Hypothesis for property-based rule testing.
- Ruff for linting/formatting.
- Pyright or strict mypy for static type checking.
- `uv` for project/dependency management.

### Concurrency rule

Do not allow arbitrary concurrent writes to one game object.

Each running game should have a **single serialized command stream** (actor/mailbox model or equivalent). API requests may arrive concurrently, but state-changing commands for a game are processed in order.

This gives us:

- thread-safe state mutation;
- deterministic command ordering;
- fewer lock-related bugs;
- easy replay;
- straightforward idempotency;
- safe WebSocket fan-out;
- non-blocking API workers.

CPU-heavy AI/pathfinding work can later run in worker processes against immutable snapshots, but workers must return proposed commands rather than mutating authoritative state.

---

## 6. Domain model

### `Game`

Authoritative aggregate for a match.

Fields/concepts:

- game id;
- ruleset id/version;
- random seed;
- current turn;
- current phase;
- game status;
- state version;
- player order;
- world/map id;
- victory configuration;
- RNG state or deterministic random stream identifiers.

### `Player`

Represents one participant.

- player id;
- controller type: human/bot;
- civilization id;
- leader/profile id;
- resources/treasury;
- research state;
- diplomacy relationships;
- known-map/fog state;
- settlements;
- units;
- score/victory progress;
- eliminated flag.

### `CivilizationDefinition`

Data-driven rules modifier rather than hard-coded subclass logic.

- id;
- display name;
- tags;
- starting bonuses;
- passive modifiers;
- unique unit references;
- unique building references;
- optional research modifiers;
- optional economy/combat modifiers.

All POC civilizations should be original fictional/test content.

### `WorldMap`

- width/height or map radius;
- topology;
- seed;
- tile collection;
- spawn regions;
- resource placement;
- map metadata.

### `Tile`

Use axial hex coordinates `(q, r)` internally.

- coordinate;
- terrain type;
- feature tags;
- resource;
- base yields;
- movement cost;
- defense modifier;
- passability;
- settlement id if occupied;
- unit occupancy references;
- improvement/building references later.

### `Settlement`

- settlement id;
- owner;
- center coordinate;
- population;
- food/growth storage;
- production storage;
- controlled tiles;
- worked tiles;
- build queue;
- buildings;
- defense;
- local modifiers;
- generated yields.

The engine should leave room for a later `town`/`city` specialization model without requiring it in v0.x.

### `Unit`

- unit id;
- owner;
- unit definition id;
- position;
- hit points;
- movement points;
- combat strength;
- ranged strength/range when applicable;
- experience/promotion state later;
- status effects;
- action flags.

### `TechnologyDefinition`

Technology progression is a directed acyclic graph.

- id;
- cost;
- prerequisites;
- unlocks;
- modifiers;
- tags.

The same generic progression engine should later support civics/social research as a separate tree.

### `DiplomaticRelationship`

For each player pair:

- contact state;
- peace/war state;
- relationship score optional;
- treaties;
- active offers;
- grievance/history ledger later.

### `VictoryTracker`

Victory conditions must be pluggable.

POC:

- score victory after a configured maximum turn;
- conquest/elimination victory.

Later:

- science/progression race;
- culture/influence;
- diplomacy;
- configurable scenario objectives.

---

## 7. Hex-map subsystem

Use axial coordinates because they simplify neighbor and distance calculations.

Required utilities:

- six-neighbor lookup;
- hex distance;
- radius/ring queries;
- line queries;
- movement range;
- A* pathfinding;
- terrain movement costs;
- passability rules;
- occupancy rules;
- spawn validation;
- territory ownership;
- visibility/fog computation.

### Map generation POC

Start with deterministic procedural generation:

1. seed RNG;
2. generate land/water mask;
3. assign terrain bands;
4. place features;
5. place strategic/bonus resources;
6. choose valid starting regions;
7. normalize unfair starts using configurable scoring;
8. serialize map definition.

Map generation must produce the same result from the same seed + ruleset version.

---

## 8. Fog of war and player projections

A client must never receive authoritative hidden state by default.

Maintain visibility states such as:

- `UNKNOWN` — never seen;
- `DISCOVERED` — previously seen, current dynamic details hidden;
- `VISIBLE` — currently observable.

The server will maintain the full state but expose **player-specific projections**.

```text
Authoritative GameState
       ├── project(player_a) → Player A view
       ├── project(player_b) → Player B view
       └── project(admin)    → complete debug view
```

This is essential if web, multiplayer, bots, and third-party clients all use the same API.

---

## 9. Yield/economy model

Use a small generic POC yield set:

- Food — settlement growth;
- Production — construction and unit creation;
- Gold — treasury and purchases/maintenance later;
- Science — technology progress;
- Culture — social/civic progress later.

Keep yields represented through extensible typed maps so new yield types do not require database redesign.

Every turn:

```text
tile yields
+ buildings
+ civilization modifiers
+ temporary modifiers
- maintenance/penalties
= settlement yields
= empire totals
```

All modifiers should pass through one modifier/effect pipeline rather than being scattered across entity classes.

---

## 10. Modifier/effect system

Avoid hard-coding rules such as civilization-specific `if` statements in engine internals.

Instead, definitions register typed modifiers.

Conceptual modifier types:

- flat yield;
- percentage yield;
- terrain yield;
- unit combat;
- movement;
- build cost;
- research cost;
- upkeep;
- visibility;
- settlement growth;
- conditional trigger.

A modifier should contain:

- source;
- target selector;
- operation;
- value;
- condition;
- duration;
- stacking policy;
- priority/order.

This is one of the most important architectural decisions because nearly every future civilization, technology, policy, wonder, building, event, and difficulty modifier can use the same mechanism.

---

## 11. Turn model

Use a deterministic state machine.

POC recommendation: sequential players with explicit end-turn commands, while designing the command model so simultaneous-turn multiplayer can be added later.

### Turn lifecycle

```text
GAME TURN START
    ↓
start active player turn
    ↓
refresh unit movement/actions
apply start-turn effects
resolve recurring economy/growth/research
    ↓
accept commands
    ├── move
    ├── attack
    ├── found settlement
    ├── change production
    ├── choose research
    ├── diplomacy
    └── end turn
    ↓
validate player has completed mandatory choices
    ↓
end active player turn
    ↓
next player
    ↓
GLOBAL TURN END
    ↓
resolve global effects
check victory
snapshot if required
increment turn
```

Mandatory decisions should be queryable via the API so clients know why `EndTurn` is rejected.

---

## 12. Command model

Everything that mutates game state is a command.

POC commands:

- `CreateGame`
- `JoinGame`
- `StartGame`
- `MoveUnit`
- `AttackUnit`
- `FoundSettlement`
- `SetWorkedTile`
- `QueueProduction`
- `CancelProduction`
- `ChooseResearch`
- `DeclareWar`
- `OfferPeace`
- `AcceptPeace`
- `EndTurn`
- `Concede`

Every command envelope should include:

- `command_id`;
- `game_id`;
- `player_id`;
- expected `state_version` when appropriate;
- command type;
- payload;
- client timestamp for diagnostics only.

### Idempotency

`command_id` must be unique per game.

If a client retries the same request after a timeout, the engine should return the original result instead of applying the command twice.

---

## 13. Event model

Successful commands produce immutable domain events.

Examples:

- `GameCreated`
- `GameStarted`
- `TurnStarted`
- `UnitMoved`
- `UnitAttacked`
- `UnitDamaged`
- `UnitDestroyed`
- `SettlementFounded`
- `ProductionQueued`
- `ProductionCompleted`
- `TechnologySelected`
- `TechnologyCompleted`
- `WarDeclared`
- `PeaceEstablished`
- `PlayerEndedTurn`
- `TurnEnded`
- `PlayerEliminated`
- `VictoryAchieved`

Events enable:

- replay;
- debugging;
- client updates;
- audit trails;
- spectator mode;
- deterministic tests;
- AI analysis;
- rollback/branch experiments later.

---

## 14. Deterministic randomness

Randomness is allowed, but never uncontrolled global randomness.

All random outcomes must derive from:

- game seed;
- deterministic stream/category;
- stable event/command context.

Suggested streams:

- map generation;
- combat;
- neutral events;
- AI tie-breaking.

The engine should record enough information to reproduce every random result exactly during replay.

---

## 15. Combat POC

Start small.

Combat needs:

- melee and ranged categories;
- attack/defense strength;
- hit points;
- terrain defense;
- deterministic RNG variance with a seeded stream;
- unit destruction;
- movement/action consumption;
- ownership/war validation.

Do not reproduce Civilization's exact combat formulas. Create original configurable formulas with tests.

Later extensions:

- zones of control;
- fortifications;
- siege;
- promotions;
- commanders;
- naval/air layers;
- support units;
- retreat;
- supply/logistics.

---

## 16. Settlement POC

Settlements should be engines of growth and production.

Minimum loop:

1. founder unit establishes settlement;
2. center tile becomes controlled;
3. settlement works one or more controlled tiles;
4. worked tiles produce yields;
5. food advances growth;
6. production advances build queue;
7. population growth adds workable capacity;
8. completed buildings add modifiers;
9. completed units spawn on/near the settlement.

Territorial growth can initially be deterministic and simplified, then replaced by a culture/border system later.

---

## 17. Research POC

Implement a generic prerequisite graph.

Example original test tree:

```text
Agriculture
├── Masonry
│   └── Engineering
└── Animal Husbandry
    └── Riding

Writing
└── Mathematics
```

Research flow:

- player chooses an available technology;
- empire Science adds progress each turn;
- completed technology emits an event;
- unlocks become available immediately or at next defined phase;
- client obtains newly available choices through a query.

A second progression tree can later use exactly the same engine for civics/social development.

---

## 18. Diplomacy POC

Initial diplomacy is intentionally small:

- unknown;
- contacted;
- at peace;
- at war;
- peace proposal pending.

Commands:

- declare war;
- offer peace;
- accept/reject peace.

Later:

- trade deals;
- alliances;
- open borders;
- diplomatic currency/influence;
- grievances;
- reputation;
- joint wars;
- independent powers/city-states;
- global diplomatic systems using original rules.

---

## 19. AI architecture

Bots should consume the **same legal command interface as human clients**.

```text
GameSnapshot
    ↓
BotPolicy.choose_commands(...)
    ↓
normal validated engine commands
```

POC bot priorities:

1. reveal nearby unknown tiles;
2. find a legal settlement location;
3. keep settlement production active;
4. choose available research;
5. defend threatened settlements;
6. attack enemy units when favorable;
7. end turn.

Do not give normal AI direct access to hidden opponent state. A special omniscient debug bot can exist only for testing.

Future AI layers:

- utility scoring;
- goal planning;
- tactical search;
- strategic economic planning;
- diplomacy personalities;
- simulation/rollouts;
- LLM advisor/controller adapters that propose commands but cannot bypass validation.

---

## 20. API design

Use `/api/v1` from the first endpoint.

### Game lifecycle

```text
POST   /api/v1/games
GET    /api/v1/games/{game_id}
POST   /api/v1/games/{game_id}/players
POST   /api/v1/games/{game_id}/start
POST   /api/v1/games/{game_id}/commands
GET    /api/v1/games/{game_id}/state
GET    /api/v1/games/{game_id}/events
GET    /api/v1/games/{game_id}/legal-actions
```

### Player-scoped projection

```text
GET /api/v1/games/{game_id}/players/{player_id}/view
```

The endpoint returns only information that player is permitted to know.

### Definitions/content

```text
GET /api/v1/rulesets
GET /api/v1/rulesets/{ruleset_id}
GET /api/v1/rulesets/{ruleset_id}/units
GET /api/v1/rulesets/{ruleset_id}/buildings
GET /api/v1/rulesets/{ruleset_id}/technologies
GET /api/v1/rulesets/{ruleset_id}/civilizations
```

### Real-time channel

```text
WS /api/v1/games/{game_id}/stream
```

WebSocket messages should publish:

- state version changes;
- player-visible domain events;
- turn changes;
- required decisions;
- game completion.

Clients that cannot use WebSockets can poll events using `after_sequence`.

---

## 21. API response philosophy

Clients should not need to reimplement core rules merely to render the game.

Useful state should include computed values such as:

- legal destination tiles;
- current movement points;
- build progress;
- current yields;
- available research;
- valid production options;
- diplomacy status;
- mandatory decisions;
- victory progress;
- visible map coordinates.

But the API must still treat the server as authoritative. Client-provided calculated values are never trusted.

---

## 22. Persistence and replay

Use a hybrid model:

1. append immutable event;
2. update/store current snapshot;
3. periodically create durable snapshots;
4. retain ruleset version used by the match.

Suggested tables/concepts:

- `games`;
- `game_players`;
- `game_events`;
- `game_snapshots`;
- `rulesets`;
- optional `command_results` for idempotency.

Each event needs monotonically increasing sequence numbers per game.

A replay test should be able to:

```text
initial state + seed + ordered commands/events
                    ↓
                replay
                    ↓
state_hash == recorded_state_hash
```

---

## 23. Ruleset/content packs

Keep mechanics and content separate.

Suggested layout:

```text
src/
  civilization_clone/
    domain/
    engine/
    application/
    api/
    persistence/
    ai/
    rules/
    projections/

content/
  poc/
    ruleset.yaml
    terrains.yaml
    resources.yaml
    units.yaml
    buildings.yaml
    technologies.yaml
    civilizations.yaml
    victories.yaml
```

Definitions should be validated at startup.

Rulesets require explicit semantic versions so persisted games always know which balance/rules they were created with.

---

## 24. Suggested repository structure

```text
CivilizationClone/
├── PLAN.md
├── README.md
├── pyproject.toml
├── alembic.ini
├── src/
│   └── civilization_clone/
│       ├── __init__.py
│       ├── domain/
│       │   ├── game.py
│       │   ├── player.py
│       │   ├── map.py
│       │   ├── settlement.py
│       │   ├── unit.py
│       │   ├── research.py
│       │   ├── diplomacy.py
│       │   ├── victory.py
│       │   └── events.py
│       ├── engine/
│       │   ├── commands.py
│       │   ├── reducer.py
│       │   ├── turns.py
│       │   ├── movement.py
│       │   ├── combat.py
│       │   ├── economy.py
│       │   ├── effects.py
│       │   └── visibility.py
│       ├── application/
│       │   ├── game_service.py
│       │   ├── game_actor.py
│       │   └── command_bus.py
│       ├── persistence/
│       │   ├── models.py
│       │   ├── repositories.py
│       │   └── snapshots.py
│       ├── api/
│       │   ├── app.py
│       │   ├── dependencies.py
│       │   ├── routes/
│       │   └── schemas/
│       ├── ai/
│       │   ├── base.py
│       │   └── simple_bot.py
│       └── rules/
│           ├── loader.py
│           └── schemas.py
├── content/
│   └── poc/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── replay/
│   └── api/
└── migrations/
```

---

## 25. Testing strategy

This project should treat determinism as a first-class feature.

### Unit tests

- hex coordinate math;
- distance/neighbors;
- pathfinding;
- movement validation;
- yields;
- research prerequisites;
- combat resolution;
- visibility;
- modifier stacking;
- victory conditions.

### Property tests

Examples:

- hex distance is symmetric;
- movement never ends on an illegal tile;
- a destroyed unit cannot act;
- yield totals never depend on dictionary iteration order;
- replay always produces the same final hash;
- command retries never apply twice;
- a player projection never reveals an undiscovered enemy unit.

### Integration tests

Run complete scripted games through the command bus.

### API contract tests

- create/start game;
- submit commands;
- stale state-version handling;
- idempotent command retries;
- WebSocket event ordering;
- fog-of-war filtering.

### Simulation tests

Run hundreds/thousands of bot-vs-bot POC matches and record:

- completion rate;
- average turns;
- victory distribution;
- command failures;
- state divergence/replay failures;
- performance per turn.

---

## 26. Observability

Expose structured diagnostics from the start.

Metrics to capture:

- command latency;
- turn resolution latency;
- pathfinding latency;
- AI decision latency;
- active games;
- commands per game;
- event count;
- snapshot size;
- replay verification failures;
- WebSocket subscriber count;
- invalid-command reasons.

All logs should include `game_id`, `turn`, `state_version`, and `command_id` where applicable.

---

## 27. Security and multiplayer authority

Even in the POC:

- server owns authoritative state;
- player identity is never inferred solely from payload fields;
- commands are authorization-checked;
- hidden state is filtered server-side;
- command payloads are validated;
- command rate limits can be added at API boundary;
- game ruleset/content input is treated as untrusted until schema validation succeeds;
- admin/debug endpoints are separate from normal player endpoints.

---

## 28. Performance principles

Do not prematurely optimize the POC, but preserve the right architecture.

- no blocking database/network calls inside async API handlers;
- one serialized mutation stream per game;
- immutable/read-only snapshots for concurrent readers;
- incremental player projections rather than rebuilding the entire world on every tiny event when scale requires it;
- cache static content definitions;
- use coordinate-indexed dictionaries/arrays for map access;
- use bounded pathfinding searches;
- batch persistence writes when safe;
- snapshot at configurable intervals;
- keep event payloads compact and typed.

A small POC game should comfortably run many turns per second in automated mode.

---

## 29. Milestone roadmap

### v0.1 — Repository and deterministic core

Deliver:

- Python project skeleton;
- CI/lint/type/test configuration;
- typed IDs and common models;
- seeded RNG service;
- command/event base classes;
- state hashing;
- basic ruleset loader.

Exit criteria:

- same seed produces the same deterministic test result;
- CI passes on an empty/sample game.

### v0.2 — Hex world and map generation

Deliver:

- axial coordinates;
- tile model;
- neighbor/distance utilities;
- procedural terrain;
- resources;
- spawn selection;
- A* pathfinding;
- fog-of-war primitives.

Exit criteria:

- deterministic maps;
- pathfinding and visibility test coverage.

### v0.3 — Game session, turns, players, and units

Deliver:

- game aggregate;
- player aggregate/state;
- unit definitions;
- movement;
- turn state machine;
- end-turn flow;
- command validation;
- event emission.

Exit criteria:

- two scripted players can move units for multiple turns deterministically.

### v0.4 — Settlements and economy

Deliver:

- found settlement;
- territory;
- worked tiles;
- yields;
- growth;
- build queue;
- buildings;
- unit production;
- generic effect/modifier pipeline.

Exit criteria:

- players can create functioning settlements and produce new units.

### v0.5 — Research, combat, diplomacy, victory

Deliver:

- technology DAG;
- research progress;
- melee/ranged combat;
- seeded combat variation;
- war/peace state;
- elimination;
- score/conquest victory.

Exit criteria:

- a complete game can reach a legal victory through engine commands alone.

### v0.6 — Event log, saves, replay

Deliver:

- persistence repositories;
- async SQLite storage;
- command idempotency;
- event sequence;
- snapshots;
- reload;
- deterministic replay verifier.

Exit criteria:

- save/reload does not alter state;
- replay final hash matches the live game hash.

### v0.7 — Client-agnostic API

Deliver:

- FastAPI `/api/v1`;
- game lifecycle routes;
- command endpoint;
- query/state endpoints;
- OpenAPI docs;
- player projections;
- WebSocket event stream;
- non-blocking persistence integration.

Exit criteria:

- entire game can be played using HTTP/WebSocket only.

### v0.8 — Basic AI and automation harness

Deliver:

- bot policy interface;
- simple deterministic bot;
- bot-vs-bot runner;
- simulation metrics;
- headless fast-forward mode.

Exit criteria:

- bots reliably finish games without direct state mutation or hidden-state cheating.

### v0.9 — POC content pack and balancing tools

Deliver:

- original POC civilizations;
- original technologies;
- original units/buildings/resources;
- validation tooling;
- balance report from automated simulations;
- configurable game speeds/map sizes.

Exit criteria:

- repeatable playable ruleset distributed entirely as project-owned content.

### v1.0 — Proof of concept complete

Deliver:

- stable API v1;
- versioned ruleset;
- deterministic save/replay;
- human and AI controllers;
- multiplayer-safe fog-of-war projections;
- sample API client or TUI;
- complete automated POC match tests;
- architecture/developer documentation.

Exit criteria:

A fresh client can discover the API, create a match, join it, play a legal game to completion, disconnect/reconnect, and reconstruct its view without any client-specific engine logic.

---

## 30. Post-POC expansion path

Only after v1.0 is stable:

### v1.1 — Civics/government/policies

Reuse the research graph and modifier system for social progression and policy slots.

### v1.2 — Rich diplomacy and trade

Treaties, trade routes, negotiations, alliances, influence, independent powers.

### v1.3 — Advanced empire management

Settlement specializations, automation, soft settlement caps, happiness/stability, reduced late-game micromanagement.

### v1.4 — Advanced tactical layer

Zones of control, fortifications, siege, promotions, commanders, naval combat, supply.

### v1.5 — Eras/Ages framework

Add configurable campaign phases where content, rules, resources, or objectives can change while the persistent empire continues.

### v1.6 — Multiple victory frameworks

Science/progression, culture/influence, diplomacy, scenario-specific victory paths.

### v1.7 — Modding SDK

JSON/YAML schemas, content validation CLI, ruleset inheritance, mod load order, compatibility metadata.

### v1.8 — Advanced AI

Strategic planners, tactical evaluators, configurable personalities, parallel snapshot simulation, optional agent/LLM controller API.

### v1.9 — Multiplayer services

Lobby/matchmaking boundary, spectators, reconnect tokens, simultaneous-turn mode, server scaling.

### v2.0 — General-purpose historical 4X engine

The project should by this point be capable of supporting many distinct Civilization-like clients and rulesets rather than being tied to one clone presentation.

---

## 31. Deliberate non-goals for the POC

Do **not** block v1.0 on:

- a graphical client;
- historical leader art/content;
- exact Civilization balance;
- religion;
- espionage;
- governors;
- global congress;
- climate simulation;
- great people;
- wonders with complex bespoke scripting;
- naval/air warfare;
- full historical era progression;
- massive maps;
- ranked multiplayer;
- sophisticated AI;
- monetization/account services.

The POC exists to prove the engine and API boundaries first.

---

## 32. Architecture decisions that should not be compromised

1. **Headless first.** No gameplay rule belongs in a UI.
2. **Server authoritative.** Clients submit intent, not state.
3. **Deterministic simulation.** Seeded randomness and stable ordering everywhere.
4. **Commands in, events out.** All mutations use one auditable path.
5. **Serialized mutation per game.** Concurrent requests must not cause concurrent state mutation.
6. **Async I/O only at service boundaries.** Do not block API/event loops with database or network operations.
7. **Data-driven content.** Civilizations, units, technologies, buildings, terrain, and victory rules are definitions rather than giant conditional trees.
8. **Generic modifier pipeline.** New content should mostly compose existing mechanics.
9. **Player-specific projections.** Hidden information remains on the server.
10. **Version everything.** API, ruleset, events, snapshots, and persistence schemas need migration paths.
11. **Replay is a feature, not a debug afterthought.** A deterministic replay test should exist early.
12. **Original content.** Learn from official Civilization design documentation without embedding proprietary Civilization content.

---

## 33. First implementation slice

The first coding PR after this plan should be deliberately narrow:

```text
v0.1
├── pyproject.toml
├── package skeleton
├── typed identifiers
├── deterministic RNG
├── GameState
├── Command / Event envelopes
├── state version + state hash
├── content/ruleset schema loader
├── test fixtures
└── CI quality gates
```

Do **not** start FastAPI first.

The strongest foundation is a deterministic engine that can run completely in process. Once the domain can execute a scripted game, the API becomes a thin adapter rather than the place where game rules accidentally accumulate.

---

## 34. Definition of success

CivilizationClone succeeds as a POC if we can swap the client without changing the engine.

For example, all of these should eventually be equally valid:

```text
Web browser ─┐
TUI ─────────┤
Godot ───────┤
Unity ───────┤
Mobile ──────┤── API ──> same authoritative engine
Discord bot ─┤
AI agent ────┤
Test runner ─┘
```

That client independence—combined with deterministic rules, replayable events, data-driven content, and a clean modifier system—is the central design goal of the project.
