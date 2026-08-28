# CivilizationClone Agent Governance

This file is the canonical project-wide instruction source for every coding agent and human contributor working in this repository.

## Mission

Build the project described in `PLAN.md`: a headless, deterministic, API-first 4X strategy engine with original mechanics/content and client-independent simulation rules.

## Source of truth

Read these before changing code:

1. `PLAN.md` — product architecture, scope, roadmap, logging model, and design boundaries.
2. `docs/WORKFLOW.md` — required Git/GitHub development workflow.
3. This `AGENTS.md` — mandatory agent behavior and verification policy.

When these documents disagree, stop expanding scope and prefer the narrowest interpretation consistent with `PLAN.md`.

## Mandatory workflow for every agent

1. Inspect the current branch, repository state, relevant files, tests, logs, and active roadmap phase before editing.
2. Work on a feature/fix/chore branch. Do not develop directly on `main`.
3. Keep changes scoped to one coherent milestone or problem.
4. Preserve deterministic simulation behavior. Randomness must use the engine RNG abstraction and seeded state.
5. Keep domain rules out of API/UI/client adapters.
6. Add or update automated tests for behavior changes.
7. Add useful event/runtime logging at important boundaries without leaking hidden/private data.
8. Before claiming completion, hand verification to the local QA/playtest role described below.
9. Fix failures found by QA, then have QA rerun the affected checks.
10. Open a pull request only after local verification is green, except when explicitly opening a draft PR to expose known unfinished work.
11. Record the exact local CI/QA evidence in the pull request.

## No GitHub Actions / no hosted CI

**GitHub Actions must never be used in this repository.** This is a permanent project constraint because hosted CI has cost/usage implications we do not want.

Do not create, restore, enable, recommend, or depend on `.github/workflows/*` for CI, testing, release validation, automation, or merge gates.

GitHub is used for:

- source control;
- pull requests;
- code review;
- issues/milestones;
- releases/metadata when needed.

All CI is local and agent-operated.

The canonical deterministic local gate is:

```bash
bash scripts/ci.sh
```

Agents must run applicable local checks themselves or delegate them to `local-qa`. A missing hosted CI check is expected and is never a blocker by itself.

## Local QA is the testing authority

For OpenCode, use `.opencode/agents/local-qa.md` as the dedicated local testing/playtesting agent.

Implementation/review/planning agents must not report tests as passed unless the tests were actually executed. When OpenCode subagents are available, delegate final verification to `local-qa` rather than self-certifying.

When another agent harness is used and cannot invoke the OpenCode agent, that agent must follow the same QA protocol locally itself. The protocol applies to all agents regardless of vendor or harness.

### What local QA owns

Local QA performs all applicable verification locally:

- dependency/environment validation;
- formatting and linting;
- static type checking;
- unit tests;
- integration tests;
- API contract tests;
- deterministic replay/state-hash/event-journal tests;
- save/load round-trip tests;
- simulation invariants/property tests;
- logging and feedback-safety tests;
- end-to-end tests;
- client smoke tests;
- human-style interactive playtesting when a playable client exists.

### Human-style playtesting requirement

Interactive acceptance testing must exercise the client the way a person would whenever tooling permits it.

For GUI/web/desktop clients, QA should launch the real client, inspect rendered output, and use normal keyboard/pointer interactions. Prefer semantic/accessibility targets when available and screen coordinates when necessary. Verify visible feedback after important actions.

For terminal/TUI clients, launch the real interactive program, send actual keystrokes, navigate displayed menus/maps/prompts, and inspect resulting output.

Acceptance testing must not bypass the user interface by directly mutating game state, calling private methods, editing save files, or using internal database writes. API-level tests remain appropriate for validating the API itself, but they do not replace client playtesting.

### Minimum playable-game QA scenario

As capabilities appear, grow toward this complete smoke playthrough:

1. create/start game;
2. inspect map and fog of war;
3. select and move a unit;
4. explore at least one hidden tile;
5. found/manage a settlement;
6. choose production;
7. choose research;
8. end multiple turns;
9. interact with another player/AI;
10. execute combat when available;
11. save and reload when available;
12. verify deterministic replay/event journal;
13. finish or validate a configured victory condition;
14. confirm no hidden information leaks through the client, event feed, feedback, or logs.

The exact scenario grows with the roadmap. Do not fail an early milestone because later-milestone systems do not yet exist.

## Logging and diagnostics policy

The project has three separate channels. Never conflate them.

### Deterministic domain event journal

- Successful state mutations emit immutable domain events.
- Event journal ordering is authoritative and deterministic.
- Journal entries must not depend on wall-clock time, logging configuration, process ids, hostnames, or other operational state.
- Event sequence/game/state-version invariants require tests.
- Durable storage can be added later without changing journal semantics.

### Runtime/debug logs

- Use structured logging for diagnostics and support.
- Include useful correlation fields such as `game_id`, `command_id`, `event_id`, turn, state version, operation, and error code when available.
- Runtime logs must never consume RNG, mutate state, alter event ordering, or change hashes/replay results.
- Never log secrets, tokens, credentials, unrestricted hidden-player state, or sensitive internals.
- Logs and local diagnostic artifacts belong under ignored local paths such as `logs/` and `artifacts/` when persisted.

### User-facing feedback

- Expected errors and outcomes should have stable typed feedback codes/severity/messages.
- User feedback must be safe to render directly in clients.
- Do not expose stack traces, filesystem paths, secrets, hidden opponent state, or debug-only context to users.

## QA report contract

Every verification report must state:

- `Status: PASS|FAIL|BLOCKED`;
- commit/working tree tested;
- environment relevant to the test;
- exact local commands executed;
- automated checks passed/failed/skipped;
- event/logging/feedback checks performed when applicable;
- playtest scenario and user-visible steps performed;
- failures with reproducible steps;
- local log/artifact/screenshot paths when available.

Skipped checks require a reason. `BLOCKED` is not `PASS`.

## Separation of duties

- `implementer`: changes product code and tests; does not self-certify final QA.
- `local-qa`: runs all local CI/tests/playtests; does not modify product code to make failures disappear.
- `reviewer`: reviews correctness, architecture, security, determinism, logging safety, regressions, and missing tests; does not replace QA.
- GitHub: source control/review only; **no GitHub Actions or hosted CI**.

## Engineering standards

- Target Python 3.12+ unless the project later raises the minimum.
- Prefer async-native I/O in async code. Never block the event loop with synchronous network/disk calls; use async libraries or an explicit worker/thread boundary where unavoidable.
- Use typed public APIs and explicit domain types.
- Prefer pure domain logic and deterministic functions.
- Keep transport schemas separate from domain models.
- Version rulesets and serialized game state.
- Treat backwards compatibility of the public API, events, and save format deliberately.
- Keep tests deterministic and independent of wall-clock timing wherever possible.
- Avoid global mutable state.
- Do not commit secrets, tokens, credentials, generated local state, logs, or private data.

## Definition of done

A change is complete only when:

- implementation matches the active roadmap scope;
- relevant documentation is updated;
- automated tests exist and pass locally;
- `bash scripts/ci.sh` passes locally when applicable;
- local QA has executed the applicable verification protocol;
- human-style client playtesting has passed if the change affects a playable client;
- event/runtime logging and user feedback are tested when affected;
- the PR accurately documents local verification and known limitations;
- review findings are resolved.
