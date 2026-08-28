# Development and GitHub Workflow

This workflow applies to humans and **all coding-agent harnesses**. Agent-specific files may add operating details, but they may not weaken this process.

## Principles

- `main` stays reviewable and releasable.
- Development happens on short-lived branches.
- **All CI and testing run locally.**
- **GitHub Actions is never used.**
- Local agents are responsible for deterministic CI, integration testing, diagnostics, and playtesting.
- A dedicated local QA/playtest pass is required for changes affecting executable behavior.
- Interactive clients are playtested through the same user-facing controls a human uses.
- Pull requests carry explicit local verification evidence instead of hosted-CI status checks.

## Branch model

Use short-lived branches from current `main`:

- `feat/<topic>` — new capability;
- `fix/<topic>` — defect fix;
- `chore/<topic>` — tooling/governance/maintenance;
- `docs/<topic>` — documentation only;
- `refactor/<topic>` — behavior-preserving restructuring;
- `test/<topic>` — test-only work.

Do not develop directly on `main`.

## Change lifecycle

```text
PLAN / ISSUE
    |
    v
SCOPED BRANCH
    |
    v
IMPLEMENTATION + TESTS + LOGGING
    |
    v
FOCUSED LOCAL CHECKS
    |
    v
LOCAL AGENT CI: scripts/ci.sh
    |
    v
LOCAL-QA INTEGRATION / REPLAY / LOG CHECKS
    |
    v
HUMAN-STYLE CLIENT PLAYTEST (when applicable)
    |
    v
CODE / ARCHITECTURE REVIEW
    |
    v
PULL REQUEST WITH LOCAL QA EVIDENCE
    |
    v
REVIEW FINDINGS RESOLVED LOCALLY
    |
    v
FINAL LOCAL-QA RE-RUN
    |
    v
MERGE
```

## Canonical local CI gate

The repository exposes one canonical deterministic non-interactive CI command:

```bash
bash scripts/ci.sh
```

This command is intended to own, as applicable:

- repository/governance checks;
- dependency validation;
- formatting checks;
- linting;
- static type checking;
- unit/integration/property tests;
- deterministic event/replay/state-hash tests;
- logging/feedback tests;
- build/package checks;
- security/static checks later.

Agents may run focused tests while iterating, but `local-qa` must run the canonical gate before a PR is ready to merge.

If dependency installation is unavailable in one environment, report `BLOCKED` rather than pretending the gate passed. Run the gate from a connected local development environment before merge.

## No GitHub Actions

Do not add `.github/workflows/` files.

Do not configure GitHub-hosted CI, Actions runners, workflow status checks, paid CI services, or autonomous cloud testing as merge requirements.

If an old GitHub Actions workflow exists, remove it.

GitHub is only the collaboration/review layer. The authoritative test evidence comes from local agent QA reports.

## Event, runtime logging, and feedback verification

Changes that affect commands, state transitions, events, persistence, APIs, or clients must consider three channels:

1. deterministic domain event journal;
2. operational runtime/debug logs;
3. safe user-facing feedback.

Local QA should verify, when applicable:

- event sequence/game/state-version invariants;
- same input produces the same event journal and state hash;
- runtime logging on/off or different log levels do not change deterministic outputs;
- logs include useful correlation context;
- logs do not expose secrets or unrestricted hidden state;
- expected user errors produce stable safe feedback codes/messages;
- stack traces/internal debug context are not exposed through user feedback.

## Interactive playtesting gate

When a change affects a playable TUI, web, desktop, mobile, Godot, or other graphical client, local QA must use the actual client.

### Graphical client

Use normal user interaction: launch the app, inspect rendered output, click/select visible controls or map locations, use screen coordinates when necessary, type input, scroll/drag/pan/zoom, navigate menus, and verify visible feedback after important actions.

### TUI/terminal client

Use the real interactive process and send actual keystrokes. Do not replace a TUI acceptance path with direct function calls.

### No acceptance-test shortcuts

Do not directly mutate databases, saves, internal objects, or private APIs to simulate actions that the player is expected to perform through the client.

## Local diagnostic artifacts

Use ignored local directories such as:

```text
logs/
artifacts/
```

Preserve useful logs/traces/screenshots when debugging failures. QA reports should cite their local paths when they materially help reproduction.

Do not commit routine generated logs, screenshots, databases, or private runtime state.

## Commit policy

Prefer small, coherent commits with imperative messages such as:

- `feat: add deterministic hex map generator`
- `feat: add structured command logging`
- `fix: preserve visibility state after reload`
- `test: cover event journal determinism`

Do not mix unrelated cleanup into feature commits.

## Pull request requirements

A PR should contain:

### Summary

What changed and why.

### Scope

Which `PLAN.md` milestone/requirement it implements or supports.

### Local verification

Include actual evidence:

- `bash scripts/ci.sh` result;
- focused test commands if relevant;
- local QA status;
- deterministic seed/event/replay checks when applicable;
- logging/feedback checks when applicable;
- interactive playtest scenario/result when applicable;
- artifact/log paths for relevant failures or diagnostics.

### Risks / limitations

Call out known gaps, migrations, compatibility concerns, or intentionally deferred work.

A PR with known failing required local checks should remain draft unless there is a documented reason to expose the failure for collaboration.

## Recommended `main` branch rules

Because the project does not use hosted CI, do **not** require GitHub status checks.

Recommended protections where available without paid automation:

- pull request before merge;
- resolved review conversations;
- no force pushes;
- no branch deletion;
- linear history if the project chooses squash/rebase-only merges.

Prefer squash merge for roadmap-sized PRs unless preserving individual commits adds meaningful value.

## Failure loop

When local QA or review finds a problem:

1. record the failure/reproduction and relevant logs;
2. implementation agent/human fixes it on the same branch;
3. rerun focused checks;
4. rerun `bash scripts/ci.sh` locally;
5. rerun affected event/logging/playtest paths;
6. update the PR verification notes if the failure was material.

Do not paper over failures by disabling tests, reducing assertions, suppressing logs that reveal defects, adding broad ignores, or marking unstable behavior expected without an explicit design decision.

## Release direction

The POC does not need hosted release automation. Releases should be prepared and verified locally from reviewed commits/tags, with deterministic build/test scripts and manually published artifacts/metadata as needed.
