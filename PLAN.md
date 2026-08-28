# CivilizationClone — Proof-of-Concept Engine Plan

## 1. Project Goal

Build a **headless, deterministic, turn-based 4X strategy engine** inspired by the broad Civilization-style genre, exposed through a stable API so that **any client** can play or observe the same simulation.

The engine must own all authoritative game state and rules. Clients are presentation and input layers only.

Examples of possible clients:

- terminal / TUI;
- browser;
- Godot, Unity, Unreal, or another game engine;
- desktop or mobile app;
- Discord/chat bot;
- AI-agent player;
- automated play-test harness;
- replay/spectator viewer.

The proof of concept should be small enough to implement and test quickly, but its boundaries should already support expansion into a much deeper 4X game.

> This project should implement original mechanics, names, data, art, and content. It should not copy proprietary Civilization game data, text, artwork, maps, or other copyrighted assets.

---

## 2. Proof-of-Concept Success Criteria

The POC is successful when a complete game can be created and played to a deterministic conclusion through the API without any graphical client.

A POC game should support:

1. procedural map generation;
2. 2–6 civilizations/players;
3. human and basic AI players;
4. fog of war and per-player visibility;
5. units that can move, explore, settle, and fight;
6. cities that work tiles, produce yields, grow, and build items;
7. a small technology tree;
8. resources and terrain effects;
9. simple diplomacy states;
10. turn progression;
11. one or more victory conditions;
12. save/load;
13. deterministic replay from seed + commands;
14. REST API control;
15. WebSocket event streaming;
16. automated end-to-end play tests using the same public API as real clients.

A minimal game should be playable entirely with `curl`, a Python script, or an API test client.

---

## 3. Core Design Principles

### 3.1 Headless authoritative engine

The simulation must not depend on UI frameworks, rendering engines, operating-system windows, or client state.

```text
                         ┌──────────────────────────────┐
                         │           CLIENTS            │
                         │                              │
                         │ TUI  Web  Godot  Mobile  AI  │
                         └──────────────┬───────────────┘
                                        │
                              REST / WebSocket
                                        │
                         ┌──────────────▼───────────────┐
                         │          API LAYER           │
                         │ auth • commands • queries    │
                         │ subscriptions • serialization│
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │       APPLICATION LAYER      │
                         │ command handlers • queries   │
                         │ game/session orchestration   │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │       SIMULATION CORE        │
                         │ map • units • cities • tech  │
                         │ combat • economy • diplomacy │
                         │ turns • victory • visibility │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │        PERSISTENCE           │
                         │ snapshots • command log      │
                         │ events • ruleset metadata    │
                         └──────────────────────────────┘
```

### 3.2 Deterministic simulation

Given the same:

- engine version;
- ruleset version;
- map seed;
- game seed;
- initial configuration;
- ordered command stream;

…the engine must produce the same authoritative state.

All randomness must flow through a deterministic game RNG service. Domain code must never call global random functions directly.

### 3.3 Commands in, events/state out

Clients request actions by submitting commands.

Examples:

- `MoveUnit`;
- `FoundCity`;
- `SetResearch`;
- `SetCityProduction`;
- `AttackUnit`;
- `EndTurn`;
- `DeclareWar`.

The engine validates and executes commands, mutates authoritative state, and produces domain events.

Examples:

- `UnitMoved`;
- `TileDiscovered`;
- `CityFounded`;
- `CombatResolved`;
- `TechnologyCompleted`;
- `TurnAdvanced`;
- `GameEnded`.

### 3.4 Client-agnostic protocol

No game rule should know whether a command came from a browser, TUI, game engine, or AI.

### 3.5 Data-driven content

Terrain, units, technologies, buildings, resources, yields, and balance values should be loaded from versioned data files instead of being hard-coded into the engine wherever practical.

### 3.6 Thin transport layer

HTTP/WebSocket handlers translate protocol objects into application commands and queries. They must not contain game rules.

### 3.7 Explicit state visibility

The authoritative world contains everything. A player-facing state projection contains only information that player is allowed to know.

This prevents clients from receiving hidden enemy positions or unexplored-map information.

### 3.8 Local-first development and verification

All linting, type checking, unit tests, integration tests, replay verification, and end-to-end tests should be runnable locally from a single command. Do not make GitHub Actions a project dependency.

---

## 4. Recommended Technology Stack

Initial implementation target:

- **Python 3.12+**;
- **FastAPI** for HTTP/WebSocket API;
- **Pydantic v2** for transport schemas and configuration;
- **dataclasses or focused domain models** for simulation state where appropriate;
- **SQLAlchemy 2 async** for persistence boundaries if a relational store is used;
- **SQLite** for the POC, with WAL mode and async access;
- **Alembic** once persistent schema migrations become necessary;
- **pytest** + `pytest-asyncio` for tests;
- **Hypothesis** for property/state-machine testing where valuable;
- **Ruff** for linting/formatting;
- **Pyright** or strict mypy for static type checking;
- **uv** for dependency/project management;
- **orjson** or equivalent only if profiling later proves serialization is important.

The simulation core should remain framework-independent so it can eventually be embedded as a library or run behind another transport.

Async code must not perform blocking disk/network work on the event loop. Blocking third-party operations should be replaced with async equivalents or isolated using an appropriate worker/thread boundary.

---

## 5. Repository Structure

Proposed initial structure:

```text
CivilizationClone/
├── PLAN.md
├── README.md
├── pyproject.toml
├── uv.lock
├── src/
│   └── civilization_clone/
│       ├── __init__.py
│       ├── api/
│       │   ├── app.py
│       │   ├── dependencies.py
│       │   ├── errors.py
│       │   ├── routes/
│       │   │   ├── games.py
│       │   │   ├── commands.py
│       │   │   ├── players.py
│       │   │   └── admin.py
│       │   ├── schemas/
│       │   └── websocket.py
│       ├── application/
│       │   ├── commands.py
│       │   ├── handlers.py
│       │   ├── queries.py
│       │   └── services.py
│       ├── domain/
│       │   ├── ids.py
│       │   ├── game.py
│       │   ├── map.py
│       │   ├── tile.py
│       │   ├── player.py
│       │   ├── civilization.py
│       │   ├── unit.py
│       │   ├── city.py
│       │   ├── economy.py
│       │   ├── technology.py
│       │   ├── combat.py
│       │   ├── diplomacy.py
│       │   ├── visibility.py
│       │   ├── victory.py
│       │   ├── commands.py
│       │   └── events.py
│       ├── engine/
│       │   ├── simulation.py
│       │   ├── turn_engine.py
│       │   ├── command_bus.py
│       │   ├── event_bus.py
│       │   ├── rng.py
│       │   ├── rules.py
│       │   └── invariants.py
│       ├── mapgen/
│       │   ├── generator.py
│       │   ├── terrain.py
│       │   ├── resources.py
│       │   └── starts.py
│       ├── ai/
│       │   ├── player.py
│       │   ├── strategy.py
│       │   ├── tactical.py
│       │   └── heuristics.py
│       ├── persistence/
│       │   ├── models.py
│       │   ├── repositories.py
│       │   ├── sqlite.py
│       │   ├── snapshots.py
│       │   └── command_log.py
│       ├── projections/
│       │   ├── player_view.py
│       │   ├── map_view.py
│       │   └── replay_view.py
│       ├── rulesets/
│       │   ├── loader.py
│       │   ├── schema.py
│       │   └── basic/
│       │       ├── manifest.yaml
│       │       ├── terrains.yaml
│       │       ├── units.yaml
│       │       ├── technologies.yaml
│       │       ├── buildings.yaml
│       │       └── resources.yaml
│       └── config.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── replay/
│   └── e2e/
├── scripts/
│   ├── check.py
│   ├── run_server.py
│   ├── simulate_game.py
│   └── replay_game.py
└── examples/
    ├── curl/
    └── python_client/
```

---

## 6. Game Model

### 6.1 Game

A game is the aggregate coordinating the simulation.

Suggested fields:

```text
Game
├── id
├── engine_version
├── ruleset_id
├── ruleset_version
├── status
├── created_at
├── turn_number
├── phase
├── active_player_id / pending_players
├── map
├── players
├── civilizations
├── units
├── cities
├── diplomacy
├── research
├── victory_state
├── rng_state
└── revision
```

Use opaque stable IDs rather than array indexes in the public protocol.

### 6.2 Hex map

Use axial hex coordinates `(q, r)` for the initial map.

A tile contains:

- coordinate;
- terrain type;
- optional feature;
- optional resource;
- base yields;
- movement cost;
- passability;
- owner/cultural controller, if any;
- city reference, if present;
- occupying units;
- improvements later.

Initial terrain set:

- grassland;
- plains;
- desert;
- tundra;
- hill;
- mountain;
- coast;
- ocean.

Optional POC features:

- forest;
- river flag;
- marsh.

### 6.3 Yields

Keep the initial economic model small:

- `food`;
- `production`;
- `science`;
- `gold`.

Culture, faith, influence, amenities, tourism, religion, and more complex economic resources are deliberately deferred.

### 6.4 Players and civilizations

Separate **player identity/controller** from **civilization game data**.

```text
Player
├── id
├── controller_type: human | ai
├── display_name
├── civilization_id
├── connected/session state
└── turn state

Civilization
├── id
├── name
├── adjective
├── color metadata
├── starting bonuses
└── optional traits
```

For the POC, civilizations can be symmetric except for names/colors. Unique units and unique buildings can wait until the engine is proven.

### 6.5 Units

Initial unit types:

- Settler;
- Scout;
- Warrior;
- Archer.

Unit state:

- id;
- owner;
- type;
- position;
- health;
- movement points;
- attack/ranged strength;
- experience optional;
- status flags;
- per-turn action state.

Initial unit actions:

- move;
- skip/wait;
- fortify;
- melee attack;
- ranged attack;
- found city (Settler);
- disband optional.

### 6.6 Cities

City state:

- id;
- owner;
- name;
- location;
- population;
- food stockpile;
- production stockpile;
- current production;
- worked tiles;
- buildings;
- borders/owned tiles;
- per-turn yield summary.

POC city loop:

1. determine worked tiles;
2. sum yields;
3. consume food requirement;
4. apply growth progress;
5. apply production progress;
6. complete a unit/building when threshold is reached;
7. add science/gold to owner;
8. emit resulting events.

Initial build options:

- Warrior;
- Scout;
- Settler;
- Monument-equivalent original building;
- Workshop-equivalent original building.

### 6.7 Technology

Use a small directed acyclic graph.

Example POC technologies with original/generic names:

```text
Agriculture
├── Irrigation
└── Animal Husbandry

Crafting
├── Masonry
└── Metalworking

Writing
└── Mathematics
```

Each technology specifies:

- cost;
- prerequisites;
- unlocks;
- optional modifiers.

A player chooses one active research target. Science accumulates each turn until completion.

### 6.8 Resources

Initial resource classes:

- bonus resource: improves tile yield;
- strategic resource: required for selected units later.

For the earliest POC, strategic-resource gating may be omitted while keeping the schema ready for it.

### 6.9 Diplomacy

Initial diplomacy is intentionally simple.

Relationship states:

- self;
- neutral;
- war.

Commands:

- declare war;
- offer peace;
- accept peace.

Later versions can add treaties, alliances, trade, grievances, reputation, espionage, and federations.

### 6.10 Combat

POC combat should be deterministic except for a bounded RNG modifier controlled by the game RNG.

Inputs can include:

- attacker strength;
- defender strength;
- current health;
- terrain defense modifier;
- ranged/melee mode;
- deterministic random roll.

Outputs:

- damage to attacker;
- damage to defender;
- destroyed units;
- movement/occupation result;
- events.

Combat math must live behind a rules interface so it can be replaced without changing API handlers.

### 6.11 Fog of war

Each player tracks tile knowledge using at least three states:

- `unknown` — never seen;
- `discovered` — seen previously but not currently visible;
- `visible` — currently observable.

Player projections must redact hidden dynamic information from discovered-but-not-visible tiles.

### 6.12 Victory

Implement at least two victory paths:

- **Conquest:** only one civilization remains with cities;
- **Science/Progress:** complete the final POC technology/project.

A configurable max-turn score victory can prevent endless AI games.

---

## 7. Turn System

The POC should use a deterministic sequential turn model first.

```text
TURN START
   │
   ├─ reset active player's unit movement/actions
   ├─ process beginning-of-turn effects
   ├─ active player submits commands
   │    ├─ move
   │    ├─ attack
   │    ├─ city orders
   │    ├─ research order
   │    └─ diplomacy
   │
   ├─ EndTurn
   │
   ├─ process city economy
   ├─ process research
   ├─ process end-of-turn effects
   ├─ recompute visibility
   ├─ check victory
   └─ advance to next player / next round
```

The architecture should not assume sequential turns forever. A future ruleset may use simultaneous planning/resolution.

### Turn invariants

- a player cannot act outside its legal turn unless a future reaction system explicitly allows it;
- a unit cannot spend more movement/action points than it owns;
- completed/dead entities cannot act;
- every successful command increments the game revision;
- commands should be idempotent when a client supplies a unique command ID;
- the same accepted command stream must replay identically.

---

## 8. Command Model

All mutating operations should share an envelope.

Example conceptual request:

```json
{
  "command_id": "01J...",
  "game_id": "01J...",
  "player_id": "01J...",
  "expected_revision": 42,
  "type": "move_unit",
  "payload": {
    "unit_id": "01J...",
    "destination": {"q": 4, "r": -2}
  }
}
```

Important fields:

- `command_id` — client-generated idempotency key;
- `expected_revision` — optimistic concurrency protection;
- `player_id` — actor;
- `type` — stable command discriminator;
- `payload` — command-specific data.

Result:

```json
{
  "accepted": true,
  "game_id": "01J...",
  "revision": 43,
  "events": [
    {
      "type": "unit_moved",
      "sequence": 118,
      "data": {}
    }
  ]
}
```

Rejected commands return a machine-readable error code, not only human text.

Examples:

- `NOT_YOUR_TURN`;
- `ENTITY_NOT_FOUND`;
- `UNIT_NOT_OWNED`;
- `DESTINATION_BLOCKED`;
- `INSUFFICIENT_MOVEMENT`;
- `TECH_PREREQUISITE_MISSING`;
- `STALE_GAME_REVISION`;
- `GAME_ALREADY_FINISHED`.

---

## 9. Domain Event Model

Every accepted action should emit explicit events useful for:

- clients;
- persistence;
- replay;
- debugging;
- AI observation;
- analytics;
- future multiplayer synchronization.

Event envelope:

```text
DomainEvent
├── event_id
├── game_id
├── sequence
├── turn
├── revision
├── type
├── actor_player_id?
├── entity_id?
├── data
└── engine/ruleset metadata where required
```

Initial event catalog:

### Game lifecycle

- `game_created`;
- `game_started`;
- `turn_started`;
- `turn_ended`;
- `round_advanced`;
- `game_ended`.

### Map/visibility

- `tile_discovered`;
- `visibility_changed`.

### Units

- `unit_created`;
- `unit_moved`;
- `unit_fortified`;
- `unit_damaged`;
- `unit_destroyed`.

### Cities

- `city_founded`;
- `city_grew`;
- `city_production_changed`;
- `production_completed`.

### Science

- `research_selected`;
- `research_progressed`;
- `technology_completed`.

### Diplomacy/combat

- `war_declared`;
- `peace_offered`;
- `peace_established`;
- `combat_resolved`.

### Victory

- `victory_progressed`;
- `victory_achieved`.

---

## 10. API Design

Version the public API from day one.

Base path:

```text
/api/v1
```

### 10.1 Health/capabilities

```text
GET  /health
GET  /api/v1/capabilities
GET  /api/v1/rulesets
GET  /api/v1/rulesets/{ruleset_id}
```

`capabilities` should expose engine/API versions and feature flags so different clients can negotiate compatibility.

### 10.2 Game lifecycle

```text
POST   /api/v1/games
GET    /api/v1/games/{game_id}
DELETE /api/v1/games/{game_id}          # development/admin initially
POST   /api/v1/games/{game_id}/start
POST   /api/v1/games/{game_id}/save
POST   /api/v1/games/{game_id}/commands
```

Creation request contains:

- map size;
- map seed optional;
- game seed optional;
- player count;
- human/AI controller assignment;
- ruleset;
- victory options;
- turn limit optional.

### 10.3 Player projections

```text
GET /api/v1/games/{game_id}/players/{player_id}/state
GET /api/v1/games/{game_id}/players/{player_id}/map
GET /api/v1/games/{game_id}/players/{player_id}/units
GET /api/v1/games/{game_id}/players/{player_id}/cities
GET /api/v1/games/{game_id}/players/{player_id}/research
GET /api/v1/games/{game_id}/players/{player_id}/diplomacy
```

A convenience complete state endpoint is useful for simple clients, while narrower endpoints help larger clients later.

### 10.4 Legal actions

Useful for UI clients and AI agents:

```text
GET /api/v1/games/{game_id}/players/{player_id}/legal-actions
GET /api/v1/games/{game_id}/units/{unit_id}/legal-actions
GET /api/v1/games/{game_id}/cities/{city_id}/legal-actions
```

The engine remains authoritative: legal-action discovery is advisory and commands are always revalidated at execution time.

### 10.5 Events

```text
GET /api/v1/games/{game_id}/events?after_sequence=123
```

This enables polling/recovery if a WebSocket connection drops.

### 10.6 WebSocket

```text
WS /api/v1/games/{game_id}/stream
```

Subscriptions should be scoped by authenticated player or spectator role.

Possible messages:

```text
server.hello
snapshot.available
event.batch
turn.changed
command.result
game.finished
server.error
```

WebSockets are for notification/streaming, not a separate rules path. Mutating commands should initially continue through the same command application service used by REST.

---

## 11. API Compatibility and Versioning

Track separately:

- engine version;
- API version;
- ruleset ID/version;
- save-format version.

A saved game should record all four.

Public JSON discriminators and field names should be considered contracts once released.

Breaking protocol changes require a new API version or migration strategy.

---

## 12. Persistence and Replay

### 12.1 POC persistence strategy

Use a hybrid approach:

1. durable game snapshot;
2. append-only accepted command log;
3. append-only resulting event log;
4. periodic snapshots as games become larger.

This makes debugging and deterministic verification much easier than storing only the latest state.

### 12.2 Deterministic replay

Replay process:

```text
initial config + seed
        │
        ▼
create clean game
        │
        ▼
apply accepted commands in sequence
        │
        ▼
compare state hash after each checkpoint
        │
        ▼
final state must equal persisted final state
```

Store a canonical state hash at important checkpoints.

Replay divergence should report the first differing command/event/revision.

### 12.3 Save/load

Minimum operations:

- save active game;
- load game;
- list saved games;
- verify save compatibility;
- reject incompatible versions clearly.

---

## 13. Deterministic RNG

Create a dedicated RNG service owned by each game.

Required properties:

- seeded;
- serializable state;
- deterministic across replay;
- domain-purpose calls can be traced in debug mode.

Prefer purpose-specific methods, for example:

```text
rng.combat_roll(...)
rng.map_noise(...)
rng.resource_roll(...)
rng.ai_tiebreak(...)
```

Map generation should preferably use a separate seed/stream from runtime combat and AI so adding a random map feature does not silently change every future combat roll.

---

## 14. Procedural Map Generation

POC generation pipeline:

```text
map dimensions
   ↓
seed deterministic noise / region generation
   ↓
land vs water
   ↓
terrain assignment
   ↓
features
   ↓
resource placement
   ↓
connected-component validation
   ↓
starting-position scoring
   ↓
player start placement
   ↓
map validation
```

Map generator invariants:

- every player receives a legal starting tile;
- starting positions have minimum separation;
- each start has reasonable nearby food/production;
- no player starts on impassable terrain;
- required traversable areas are connected or intentionally separated;
- generation with the same seed is stable.

Small POC sizes might include:

- Duel: ~20×12;
- Small: ~32×20;
- Standard test: ~48×30.

Exact dimensions should remain configurable.

---

## 15. Basic AI

The first AI does not need to be sophisticated. It needs to be **complete, deterministic, legal, and capable of finishing games**.

### 15.1 AI architecture

```text
AI turn
  │
  ├─ observe player projection
  ├─ update strategic priorities
  ├─ select research
  ├─ select city production
  ├─ evaluate units
  │    ├─ defend
  │    ├─ explore
  │    ├─ settle
  │    └─ attack
  ├─ optionally handle diplomacy
  ├─ submit normal public commands
  └─ EndTurn
```

The AI should submit commands through the same application command path as humans, not mutate game objects directly.

### 15.2 Initial heuristics

Settler:

- find high-yield legal settlement tiles;
- avoid nearby hostile units;
- prefer spacing from existing friendly cities.

Scout:

- maximize discovery of unknown tiles;
- avoid obviously losing combat.

Military:

- defend threatened cities;
- attack nearby favorable targets during war;
- otherwise explore/patrol.

City production:

- ensure minimum defense;
- build scouts early;
- produce settler if city/population conditions permit;
- otherwise choose a simple economy item.

Research:

- score technologies by unlocked options and current needs.

AI tie-breaking must be deterministic.

---

## 16. Ruleset / Content Pack Design

A ruleset manifest should identify:

```yaml
id: basic
version: 0.1.0
name: Basic Original Ruleset
engine_api: ">=0.1,<0.2"
```

Data definitions should reference stable IDs:

```yaml
id: warrior
name: Warrior
category: military
movement: 2
melee_strength: 8
cost: 30
prerequisites: []
```

The loader must validate:

- duplicate IDs;
- missing references;
- tech cycles;
- invalid yields;
- impossible costs;
- unsupported schema versions.

The core engine should rely on interfaces and validated definitions rather than assumptions about a specific content pack.

---

## 17. Security and Multiplayer Boundary

Full internet multiplayer authentication is not required for the first POC, but the API should avoid painting itself into a corner.

POC roles:

- admin/server;
- player;
- spectator.

Rules:

- never trust `player_id` alone in an internet-facing deployment;
- player authorization must be resolved from a session/token later;
- player projections must enforce fog-of-war redaction server-side;
- command ownership is validated server-side;
- clients never upload authoritative state;
- use optimistic revision checks to reject stale commands;
- use command IDs for retry safety.

For localhost development, authentication may be disabled by configuration.

---

## 18. Concurrency Model

For the POC, serialize commands **per game**.

Different games may execute concurrently, but two state-changing commands for the same game must not interleave unpredictably.

Conceptually:

```text
Game A command queue ──► single ordered mutation stream
Game B command queue ──► single ordered mutation stream
Game C command queue ──► single ordered mutation stream
```

This greatly simplifies determinism and replay.

Do not hold a global lock across independent games.

Network and persistence operations should be asynchronous/non-blocking. The simulation can remain synchronous CPU code behind the per-game execution boundary until profiling demonstrates the need for process-level parallelism.

---

## 19. Error Model

Use a standard API error body:

```json
{
  "error": {
    "code": "DESTINATION_BLOCKED",
    "message": "The destination tile cannot be entered by this unit.",
    "details": {
      "unit_id": "...",
      "q": 3,
      "r": 7
    }
  }
}
```

Avoid leaking hidden information through error messages. For example, a move into a fogged tile should not reveal a hidden enemy unless game rules would reveal that enemy through the attempted action.

---

## 20. Observability

POC logs should include structured fields:

- game ID;
- player ID where applicable;
- command ID;
- command type;
- revision;
- turn;
- event sequence;
- duration;
- rejection/error code.

Useful metrics later:

- commands/sec;
- command latency;
- game turn duration;
- AI decision time;
- active games;
- persisted snapshot size;
- replay verification failures;
- WebSocket connections.

Never make log output part of authoritative behavior.

---

## 21. Testing Strategy

Testing is a first-class POC requirement.

### 21.1 Unit tests

Cover pure mechanics:

- hex coordinate/distance/neighbors;
- pathfinding;
- movement costs;
- yield calculations;
- city growth;
- production;
- research prerequisites;
- combat calculation;
- visibility;
- victory conditions;
- map-generation invariants;
- ruleset validation.

### 21.2 Domain invariant tests

Examples:

- an entity ID is unique;
- a unit occupies exactly one legal tile;
- destroyed units do not remain active;
- a city location contains that city;
- player resources cannot become invalid unless explicitly allowed;
- game revision increases monotonically;
- event sequence increases monotonically;
- current player is valid;
- finished games reject mutations.

### 21.3 API contract tests

Validate:

- request/response schemas;
- command errors;
- concurrency conflicts;
- projection redaction;
- version/capability endpoints;
- reconnect/event catch-up behavior.

### 21.4 Replay tests

For recorded scenarios:

1. create game with known seed;
2. execute command fixture;
3. persist state hash;
4. rebuild from command log;
5. assert identical final hash and important intermediate hashes.

### 21.5 Property-based tests

Use generated command/state combinations to test properties such as:

- movement never increases remaining movement;
- research cannot complete before required progress;
- map neighbor symmetry;
- no legal command causes an invariant violation;
- replay always equals live execution.

### 21.6 Full automated play tests

Create a test harness that starts a real API server and plays games through HTTP as a human-compatible client would.

Scenarios:

- 2 AI players from game creation through victory;
- 4 AI players on several seeds;
- human-scripted player vs AI;
- city founding and growth;
- research victory;
- conquest victory;
- save/restart/load/continue;
- WebSocket disconnect/reconnect;
- duplicate command retry;
- stale-revision conflict;
- deterministic replay.

Nightly-style local stress scripts can run hundreds or thousands of seeded AI games and report:

- crashes;
- invariant violations;
- games exceeding max turn;
- invalid commands generated by AI;
- victory distribution;
- average turns;
- replay divergence.

No graphical client is required to verify engine correctness.

---

## 22. Reference End-to-End POC Flow

```text
1. Client GET /capabilities
2. Client POST /games
3. Server creates seeded map + players
4. Client POST /games/{id}/start
5. Client GET player state
6. Client examines legal actions
7. Client POST command: move scout
8. Server validates command
9. Engine mutates state
10. Engine emits UnitMoved + TileDiscovered
11. Server persists command/events/snapshot state
12. WebSocket subscribers receive visible events
13. Client sets research
14. Client founds city
15. Client chooses production
16. Client ends turn
17. AI players take turns through same command service
18. Turns repeat
19. Victory condition succeeds
20. GameEnded event is emitted
21. Client downloads final state/replay metadata
22. Replay tool rebuilds the same final state hash
```

---

## 23. POC Milestones

## v0.1 — Project Skeleton + Deterministic Core

Goal: establish architecture and test discipline.

Deliverables:

- Python project configuration;
- package/module boundaries;
- typed IDs;
- base game model;
- deterministic RNG service;
- command/event envelopes;
- game revision + event sequence;
- basic config;
- local `check` script running lint, types, and tests;
- initial unit tests.

Acceptance:

- a seeded empty game can be created repeatedly with an identical canonical hash.

---

## v0.2 — Hex Map + Procedural Generation

Deliverables:

- axial coordinate utilities;
- map/tile models;
- terrain definitions;
- deterministic map generator;
- basic resources;
- starting-position selection;
- map validation;
- map projection API schemas;
- generator tests across many seeds.

Acceptance:

- a configured 2–6 player map can be generated deterministically with valid starts.

---

## v0.3 — Units + Movement + Visibility

Deliverables:

- Scout, Settler, Warrior, Archer definitions;
- unit spawning;
- movement points;
- pathfinding;
- occupancy rules;
- movement command;
- fog of war;
- player-specific map projection;
- legal-action queries.

Acceptance:

- a player can explore a hidden map through public commands without receiving hidden state.

---

## v0.4 — Cities + Economy + Production

Deliverables:

- FoundCity command;
- city model;
- city tile ownership/radius;
- worked tile calculation;
- food/growth;
- production queue;
- unit/building production;
- player science/gold accumulation;
- city state API projections.

Acceptance:

- a Settler can found a city that grows and produces a new unit over multiple turns.

---

## v0.5 — Technology + Combat + Diplomacy

Deliverables:

- data-driven technology graph;
- research selection/progress/completion;
- melee combat;
- ranged combat;
- terrain combat modifiers;
- unit destruction;
- neutral/war/peace relationship state;
- war and peace commands;
- related events/tests.

Acceptance:

- two players can research, declare war, fight, and destroy enemy units deterministically.

---

## v0.6 — Turn Engine + Victory + Basic AI

Deliverables:

- full sequential turn state machine;
- beginning/end-turn processing;
- AI controller;
- exploration heuristic;
- settlement heuristic;
- production/research heuristic;
- military heuristic;
- conquest victory;
- progress/science victory;
- max-turn fallback.

Acceptance:

- an AI-vs-AI game can start from a seed and reliably terminate without manual intervention.

---

## v0.7 — REST + WebSocket API

Deliverables:

- FastAPI service;
- `/api/v1` capability endpoints;
- create/start/query game endpoints;
- generic command endpoint;
- legal-action endpoints;
- player projections;
- event polling;
- WebSocket event stream;
- standard error model;
- optimistic revision handling;
- idempotent command retry.

Acceptance:

- a complete game can be played from an external Python client using only documented public APIs.

---

## v0.8 — Persistence + Replay + End-to-End Verification

Deliverables:

- async SQLite persistence;
- save/load;
- command log;
- event log;
- snapshots;
- canonical state hashing;
- replay CLI;
- API-driven automated play-test harness;
- seeded stress-test runner;
- example `curl` and Python clients;
- documentation.

Acceptance:

- a game can be stopped, loaded, completed, and independently replayed to the exact same final state hash.

---

## v0.9 — POC Hardening

Deliverables:

- performance profiling;
- deterministic regression fixtures;
- ruleset validation hardening;
- protocol compatibility tests;
- improved AI legality/recovery;
- projection leakage audit;
- persistence/restart fault tests;
- benchmark baselines;
- complete POC documentation.

Acceptance:

- automated seeded campaigns can run repeatedly without invariant violations, replay divergence, hidden-information leakage, or unrecoverable AI turns.

---

## 24. Definition of POC Complete

The proof of concept is complete when all of the following are true:

- [ ] Engine runs headlessly.
- [ ] Engine has no dependency on a particular client/rendering framework.
- [ ] Game creation is deterministic from seed/configuration.
- [ ] Map generation works for multiple players.
- [ ] Fog of war is enforced server-side.
- [ ] Units can explore, settle, and fight.
- [ ] Cities generate yields, grow, and produce.
- [ ] Technologies can be researched.
- [ ] Diplomacy supports neutral/war/peace.
- [ ] At least two victory conditions work.
- [ ] Basic AI can finish games.
- [ ] REST API can control every required game action.
- [ ] WebSocket API can stream game changes.
- [ ] Legal-action discovery is available to clients.
- [ ] Commands have idempotency IDs and revision checks.
- [ ] Games can save/load.
- [ ] Accepted command/event history is persisted.
- [ ] Replays reproduce the same state hash.
- [ ] External automated clients can play full games.
- [ ] Local test tooling exercises engine, API, persistence, and replay end to end.
- [ ] Content is original/data-driven rather than copied from proprietary Civilization assets/data.

---

## 25. Explicitly Deferred Beyond the POC

Do **not** block the POC on these features:

- sophisticated diplomacy AI;
- religion;
- espionage;
- tourism/cultural victory;
- governments/policies;
- governors;
- loyalty;
- trade route simulation;
- naval embarkation complexity;
- air combat;
- nuclear weapons;
- climate simulation;
- world congress;
- scripted campaigns;
- mod marketplace;
- matchmaking;
- anti-cheat;
- large-scale internet multiplayer;
- simultaneous turns;
- rollback networking;
- 3D graphics;
- animation systems;
- audio;
- final art/assets;
- proprietary Civilization content compatibility.

These should be designed as later layers on top of proven simulation and API boundaries.

---

## 26. Likely Post-POC Roadmap

Once v0.9 is stable, the next major areas can be introduced independently.

### v1.x — Deeper 4X Rules

- culture and border growth;
- tile improvements/workers;
- strategic resources;
- roads and infrastructure;
- richer buildings and districts;
- government/policy system;
- trade routes;
- improved technology/civic graphs;
- additional victory types.

### v2.x — Advanced AI

- utility-based strategy;
- tactical combat planner;
- city specialization;
- opponent modeling;
- diplomacy personality;
- long-horizon planning;
- AI evaluation tournaments;
- optional ML/LLM strategy adapters that still submit ordinary game commands.

### v3.x — Multiplayer

- authenticated users;
- lobbies;
- reconnectable sessions;
- turn timers;
- simultaneous planning option;
- server authority hardening;
- spectator permissions;
- replay sharing.

### v4.x — Modding / Rules SDK

- versioned ruleset schema;
- custom units/buildings/tech;
- scriptable effects;
- map scripts;
- event hooks;
- scenario definitions;
- validation and sandboxing.

### v5.x — Client Ecosystem

- reference TUI client;
- reference web client;
- Godot client SDK/example;
- generated API clients;
- replay viewer;
- admin/simulation dashboard.

---

## 27. Architectural Rules for Future Contributors/Agents

Before implementing a feature:

1. identify whether it is domain logic, application orchestration, transport, persistence, projection, AI, or ruleset data;
2. keep domain logic out of API routes;
3. expose gameplay mutations as commands;
4. emit meaningful domain events;
5. preserve deterministic behavior;
6. use the game-owned RNG only;
7. never reveal authoritative hidden state through a player projection;
8. update ruleset/schema versions when contracts change;
9. add focused unit tests;
10. add/extend a replay or end-to-end scenario when the feature affects full-game behavior;
11. keep async I/O non-blocking and serialize state changes per game;
12. run the complete local verification suite before considering the work complete.

When a feature appears to require a client-specific workaround, prefer improving the public engine/API contract instead of coupling the simulation to that client.

---

## 28. First Implementation Slice

The first coding PR after this plan should remain deliberately small:

1. initialize `pyproject.toml` for Python 3.12+;
2. create the package boundaries shown above;
3. implement typed IDs;
4. implement hex coordinates;
5. implement deterministic RNG streams;
6. define `GameConfig`, `GameState`, command envelope, and event envelope;
7. implement canonical serialization/state hashing;
8. implement an in-memory repository;
9. add a `CreateGame` application service;
10. add tests proving identical configuration + seeds produce identical state/hash;
11. add the local `scripts/check.py` verification entrypoint;
12. document how to run the test suite.

This establishes the contracts that every later subsystem will build on while avoiding premature implementation of the full game.
