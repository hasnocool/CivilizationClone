# Logging, Event Journal, and User Feedback

CivilizationClone intentionally separates three channels so debugging never compromises determinism or leaks information.

## 1. Deterministic domain event journal

The event journal is authoritative simulation history.

Requirements:

- immutable `EventEnvelope` entries;
- one game per journal;
- contiguous event sequences;
- non-decreasing state versions;
- deterministic payload/order;
- reproducible from the same seed and command stream;
- suitable for state/replay hashing;
- no operational timestamps/host/process metadata unless explicitly modeled as game state.

The journal begins in memory and is durably mirrored into append-only SQLite event rows without changing its deterministic ordering contract.

## 2. Runtime/debug logs

Runtime logs are operational diagnostics only.

They may include timestamps, levels, component/logger names, exception information, and correlation context such as:

- `game_id`;
- `command_id`;
- `event_id`;
- `turn`;
- `state_version`;
- `operation`;
- `error_code`;
- accepted/cached command status;
- command/event counts;
- non-authoritative latency measurements.

Changing log level, formatter, or destination must not alter game state, RNG usage, events, command ordering, or hashes.

### Default API/application diagnostics

The runnable v1 API configures the `civilization_clone` logger and emits two safe diagnostic classes:

1. HTTP completion records containing method, URL **path only**, status code, and duration;
2. application command/save/load/replay records containing stable identifiers, outcome fields, counts, and duration where applicable.

Logging work initiated from async handlers/application code crosses an explicit `asyncio.to_thread` boundary so synchronous stream/file handlers do not block the event loop.

Request bodies, `Authorization` headers, bearer tokens, WebSocket credential subprotocol values, player names, and hidden player projections are deliberately not included in these records.

### Runtime controls

The default server recognizes:

- `CIVILIZATION_CLONE_LOG_LEVEL` — standard Python logging level name; defaults to `INFO`;
- `CIVILIZATION_CLONE_LOG_JSON` — `1`, `true`, `yes`, or `on` enables compact JSON-lines output.

### Structured JSON

`civilization_clone.observability.logging.JsonLogFormatter` provides JSON-lines diagnostics suitable for tools and local support logs.

### Human-readable logs

`configure_logging(json_output=False)` provides a conventional console format for local development.

## 3. User-facing feedback

`UserFeedback` is a safe typed client-facing message:

- stable code;
- severity;
- human-readable message;
- small safe context map.

Do not pass raw exceptions or debug logs directly to users.

User feedback must not expose:

- stack traces;
- secrets/tokens;
- private filesystem paths;
- raw DB errors;
- hidden opponent information;
- unrestricted authoritative state.

## 4. Local diagnostic artifacts

Use ignored local paths:

```text
logs/
artifacts/
```

QA may preserve traces/screenshots/logs there and cite paths in reports.

## 5. Testing requirements

When relevant, tests should prove:

- journal sequence/game/state-version invariants;
- deterministic event-journal equality/hash equality;
- logging enabled/disabled does not change deterministic state hashes;
- structured logs contain useful correlation and latency context;
- HTTP/application diagnostics omit credentials and request-body private fields;
- feedback objects are immutable and safe to render;
- hidden/private data is filtered from user-facing channels.
