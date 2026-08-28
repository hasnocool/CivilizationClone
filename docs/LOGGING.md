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

The initial implementation is in memory. Durable event persistence arrives in the persistence/replay milestone while keeping the same ordering contract.

## 2. Runtime/debug logs

Runtime logs are operational diagnostics only.

They may include timestamps, levels, component/logger names, exception information, and correlation context such as:

- `game_id`;
- `command_id`;
- `event_id`;
- `turn`;
- `state_version`;
- `operation`;
- `error_code`.

Changing log level, formatter, or destination must not alter game state, RNG usage, events, or hashes.

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
- structured logs contain useful correlation context;
- feedback objects are immutable and safe to render;
- hidden/private data is filtered from user-facing channels.
