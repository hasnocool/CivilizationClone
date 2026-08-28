# Development and GitHub Workflow

This workflow applies to humans and **all coding-agent harnesses**. Agent-specific files may add operating details, but they may not weaken this process.

## Principles

- `main` stays reviewable and releasable.
- Development happens on short-lived branches.
- Local verification happens before a PR is considered ready.
- GitHub Actions runs deterministic, conventional CI only.
- AI/coding agents are development tools, not CI infrastructure.
- A dedicated local QA/playtest pass is required for changes affecting executable behavior.
- Interactive clients are playtested through the same user-facing controls a human uses.

## Branch model

Use short-lived branches from current `main`:

- `feat/<topic>` — new capability;
- `fix/<topic>` — defect fix;
- `chore/<topic>` — tooling/governance/maintenance;
- `docs/<topic>` — documentation only;
- `refactor/<topic>` — behavior-preserving restructuring;
- `test/<topic>` — test-only work.

Do not develop directly on `main`.

Before starting substantive work:

1. fetch/update `main`;
2. inspect `PLAN.md` and the current milestone;
3. create a scoped branch;
4. identify acceptance criteria and affected tests.

## Change lifecycle

```text
PLAN / ISSUE
    |
    v
SCOPED BRANCH
    |
    v
IMPLEMENTATION + TESTS
    |
    v
FOCUSED LOCAL CHECKS
    |
    v
LOCAL-QA AUTOMATED GATE
    |
    v
HUMAN-STYLE CLIENT PLAYTEST (when applicable)
    |
    v
CODE / ARCHITECTURE REVIEW
    |
    v
PULL REQUEST
    |
    v
GITHUB ACTIONS (deterministic, no agents)
    |
    v
REVIEW FINDINGS RESOLVED
    |
    v
MERGE
```

## Local development gate

The repository should expose one canonical deterministic local CI command:

```bash
bash scripts/ci.sh
```

As the project matures this command owns the standard non-interactive gate: governance checks, formatting, linting, typing, tests, and other deterministic checks.

Developers/agents may run focused commands while iterating, but the canonical gate must be run before a PR is marked ready.

The dedicated local QA agent then performs any additional integration/end-to-end verification and interactive playtesting that cannot be represented by the deterministic CI script.

## Interactive playtesting gate

When a change affects a playable TUI, web, desktop, mobile, Godot, or other graphical client, local QA must use the actual client.

### Graphical client

Use normal user interaction:

- launch the app;
- inspect rendered output;
- click/select visible controls or map locations;
- prefer semantic/label/accessibility targets where available;
- use screen coordinates when necessary;
- type normal input;
- use keyboard shortcuts only if they are user-facing shortcuts;
- scroll, drag, pan, zoom, and navigate menus as a user would;
- verify visible state after important actions.

### TUI/terminal client

Use the real interactive process and send actual keystrokes. Do not replace a TUI acceptance path with direct function calls.

### No acceptance-test shortcuts

Do not directly mutate databases, saves, internal objects, or private APIs to simulate actions that the player is expected to perform through the client. Internal/API tests are still useful, but they test a different layer.

## Commit policy

Prefer small, coherent commits with imperative messages such as:

- `feat: add deterministic hex map generator`
- `fix: preserve visibility state after reload`
- `test: cover combat replay determinism`
- `docs: define local playtest workflow`

Do not mix unrelated cleanup into feature commits.

## Pull request requirements

A PR should contain:

### Summary

What changed and why.

### Scope

Which `PLAN.md` milestone/requirement it implements or supports.

### Verification

Include the actual local verification performed:

- `bash scripts/ci.sh` result;
- focused test commands if relevant;
- local QA status;
- interactive playtest scenario and result if applicable;
- deterministic seed/replay checks when applicable.

### Risks / limitations

Call out known gaps, migrations, compatibility concerns, or intentionally deferred work.

A PR with known failing required checks should remain draft unless there is a documented reason to expose the failure for collaboration.

## GitHub Actions policy

GitHub Actions must be **agent-free**.

Required CI may execute only deterministic tools/scripts such as:

- repository/governance checks;
- dependency setup;
- formatting/linting;
- static type checking;
- unit/integration/property tests;
- deterministic replay tests;
- build/package checks;
- dependency/static/security scanning;
- coverage reporting.

Required workflows must not:

- invoke OpenCode or another coding agent;
- call an LLM/API to judge code correctness;
- ask an agent to repair failing code;
- push autonomous AI fixes;
- use AI-generated review approval as a merge gate;
- use visual AI judgment as the only test oracle.

The canonical GitHub workflow should call the same `scripts/ci.sh` used locally wherever practical. This reduces local/CI drift.

## Recommended protected-branch rules for `main`

Once repository settings are configured, require:

- pull request before merge;
- required status check: the conventional CI workflow;
- branch up to date before merge when practical;
- resolved review conversations;
- no force pushes;
- no branch deletion;
- linear history if the project chooses squash/rebase-only merges.

Prefer squash merge for roadmap-sized PRs unless preserving individual commits adds meaningful value.

## Failure loop

When local QA, review, or CI finds a problem:

1. record the failure/reproduction;
2. implementation agent/human fixes it on the same branch;
3. rerun focused checks;
4. rerun the canonical local CI gate;
5. rerun the affected local QA/playtest path;
6. update the PR verification notes if the failure was material.

Do not paper over failures by disabling tests, reducing assertions, adding broad ignores, or marking unstable behavior as expected without an explicit design decision.

## Release direction

The POC does not need automated deployment initially. When releases begin, keep release automation deterministic as well: build artifacts from a reviewed commit/tag, verify hashes/tests, generate standard metadata, and publish. Do not place autonomous coding agents in the release path.
