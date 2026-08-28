# CivilizationClone Agent Governance

This file is the canonical project-wide instruction source for every coding agent and human contributor working in this repository.

## Mission

Build the project described in `PLAN.md`: a headless, deterministic, API-first 4X strategy engine with original mechanics/content and client-independent simulation rules.

## Source of truth

Read these before changing code:

1. `PLAN.md` — product architecture, scope, roadmap, and design boundaries.
2. `docs/WORKFLOW.md` — required Git/GitHub development workflow.
3. This `AGENTS.md` — mandatory agent behavior and verification policy.

For civilization, research, or historical content-pack work, also read:

- `docs/CIVILIZATION_ROSTER.md` — planned historical faction roster, expansion waves, design identities, and content guardrails.
- `docs/TECHNOLOGY_TREES.md` — shared research model plus civilization-specific heritage technology branches, prerequisites, implementation guidance, and validation requirements.

These content plans supplement `PLAN.md`; they do not override the engine/content separation, deterministic simulation rules, or original-content boundary.

When these documents disagree, stop expanding scope and prefer the narrowest interpretation consistent with `PLAN.md`.

## Mandatory workflow for every agent

1. Inspect the current branch, repository state, relevant files, tests, and active roadmap phase before editing.
2. Work on a feature/fix/chore branch. Do not develop directly on `main`.
3. Keep changes scoped to one coherent milestone or problem.
4. Preserve deterministic simulation behavior. Randomness must use the engine RNG abstraction and seeded state.
5. Keep domain rules out of API/UI/client adapters.
6. Add or update automated tests for behavior changes.
7. Before claiming completion, hand verification to the local QA/playtest role described below.
8. Fix failures found by QA, then have QA rerun the affected checks.
9. Open a pull request only after local verification is green, except when explicitly opening a draft PR to expose known unfinished work.
10. GitHub CI is a deterministic second gate; it must never be treated as a replacement for local verification.

## Local QA is the testing authority

For OpenCode, use `.opencode/agents/local-qa.md` as the dedicated local testing/playtesting agent.

Implementation/review/planning agents must not report tests as passed unless the tests were actually executed. When OpenCode subagents are available, delegate final verification to `local-qa` rather than self-certifying.

When another agent harness is used and cannot invoke the OpenCode agent, that agent must follow the same QA protocol locally itself. The protocol applies to all agents regardless of vendor or harness.

### What local QA owns

Local QA performs all applicable verification:

- formatting and linting;
- static type checking;
- unit tests;
- integration tests;
- API contract tests;
- deterministic replay/state-hash tests;
- save/load round-trip tests;
- simulation invariants/property tests;
- end-to-end tests;
- client smoke tests;
- human-style interactive playtesting when a playable client exists.

### Human-style playtesting requirement

Interactive acceptance testing must exercise the client the way a person would whenever tooling permits it.

For GUI/web/desktop clients, QA should:

- launch the real client/application;
- inspect the rendered screen rather than reading hidden internal state as a substitute for acceptance testing;
- navigate with normal keyboard and pointer input;
- use visible labels/locations/accessibility targets when available;
- use screen coordinates when target-based selection is unavailable;
- click, select, type, scroll, drag, zoom, pan, open menus, and confirm dialogs through the user-facing interface;
- verify visible feedback after each important action;
- capture the action sequence and observed result in the QA report;
- repeat important paths from a clean game/session when practical.

For terminal/TUI clients, QA should:

- launch the real interactive program;
- send actual keystrokes as a user would;
- navigate menus, prompts, maps, and commands through the displayed interface;
- verify the screen/output after each important action.

Acceptance testing must not bypass the user interface by directly mutating game state, calling private methods, editing save files, or using internal database writes. API-level tests remain appropriate for validating the API itself, but they do not replace client playtesting.

### Minimum playable-game QA scenario

Once enough functionality exists, the local QA agent should be able to play a small match from creation to victory/termination and verify at least:

1. create/start game;
2. inspect map and fog of war;
3. select and move a unit;
4. explore at least one hidden tile;
5. found or manage a settlement;
6. choose production;
7. choose research;
8. end multiple turns;
9. interact with another player/AI;
10. execute combat when available;
11. save and reload when available;
12. finish or validate a configured victory condition;
13. confirm no hidden information leaks through the client.

The exact scenario grows with the roadmap. Do not fail an early milestone because later-milestone systems do not yet exist.

## QA report contract

Every verification report must state:

- commit/working tree tested;
- environment relevant to the test;
- exact commands executed;
- automated checks passed/failed/skipped;
- playtest scenario and user-visible steps performed;
- failures with reproducible steps;
- screenshots/logs/artifacts when available;
- final status: `PASS`, `FAIL`, or `BLOCKED`.

Skipped checks require a reason. `BLOCKED` is not `PASS`.

## Separation of duties

- `implementer`: changes product code and tests; does not self-certify final QA.
- `local-qa`: runs tests and human-style playtests; does not modify product code to make failures disappear.
- `reviewer`: reviews correctness, architecture, security, regressions, and missing tests; does not replace QA.
- GitHub Actions: runs deterministic scripts only; no LLMs, coding agents, AI review agents, browser agents, or agent-generated approvals.

## GitHub and CI policy

GitHub automation must be conventional, reproducible CI/CD only.

Allowed examples:

- checkout;
- Python/uv setup;
- dependency installation;
- lint/format checks;
- type checks;
- tests;
- coverage;
- static/security scanners;
- build/package verification;
- deterministic artifact generation.

Disallowed in required CI/workflow gates:

- autonomous coding agents;
- LLM calls;
- agent-authored fixes pushed by CI;
- AI-generated approvals;
- tests that depend on an AI agent deciding whether output looks correct.

See `docs/WORKFLOW.md` for branch/PR/merge policy.

## Engineering standards

- Target Python 3.12+ unless the project later raises the minimum.
- Prefer async-native I/O in async code. Never block the event loop with synchronous network/disk calls; use async libraries or an explicit worker/thread boundary where unavoidable.
- Use typed public APIs and explicit domain types.
- Prefer pure domain logic and deterministic functions.
- Keep transport schemas separate from domain models.
- Version rulesets and serialized game state.
- Treat backwards compatibility of the public API and save format deliberately.
- Keep tests deterministic and independent of wall-clock timing wherever possible.
- Avoid global mutable state.
- Do not commit secrets, tokens, credentials, generated local state, or private data.

## Definition of done

A change is complete only when:

- implementation matches the active roadmap scope;
- relevant documentation is updated;
- automated tests exist and pass locally;
- local QA has executed the applicable verification protocol;
- human-style client playtesting has passed if the change affects a playable client;
- the PR accurately documents verification and known limitations;
- required GitHub CI checks pass;
- review findings are resolved.
