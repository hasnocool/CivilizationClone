# Godot Client Agent Instructions

These instructions extend the repository-root `AGENTS.md` for all work under `clients/godot/`.

## Mission

Build a polished Godot client for CivilizationClone without creating a second simulation engine.

The authoritative path is always:

```text
Godot input -> public /api/v1 command -> authoritative server -> authorized projection/events -> Godot render
```

## Required reading before Godot work

1. `/AGENTS.md`
2. `/PLAN.md`
3. `/docs/API_CONTRACT.md`
4. `/clients/godot/README.md`
5. `/clients/godot/TODO.md`

## Godot version

Target Godot 4.7.x unless the project deliberately upgrades. Do not adopt development/preview-only engine APIs without an explicit version decision and migration note.

## Architecture rules

- Never import Python engine code into Godot.
- Never duplicate authoritative legality calculations in GDScript.
- Never mutate SQLite/save files directly.
- Never bypass the API for testing GUI behavior.
- Never infer hidden entities from IDs, timing, error differences, or local guesses.
- Never place bearer credentials in URLs.
- Do not write bearer credentials to plaintext project/log/artifact files.
- Client randomness may only serve presentation/non-authoritative identifiers; it cannot decide game outcomes.
- Every accepted/rejected command result is interpreted from the server response.
- Refresh/render only player-authorized projections.
- Prefer server-exposed legal-action/content metadata over hardcoded gameplay constants.

## UI implementation guidance

- Keep transport code in `scripts/api_client.gd` or later dedicated networking modules.
- Keep map rendering/input in map-specific controls.
- Keep scene/controller orchestration separate from reusable widgets as the UI grows.
- UI state may cache selections, camera position, open panels, and server projections.
- UI state must not become authority.
- Use stable IDs from projections for selection and command payloads.
- Render safe typed feedback rather than raw internal errors.

## Local QA

No GitHub Actions.

Headless client verification:

```bash
bash scripts/verify_godot_client.sh
```

Human-style playtesting:

```bash
bash scripts/playtest_godot.sh
```

The local QA agent should interact with the real Godot window using normal mouse/keyboard events. It may use coordinates or semantic UI targets available to its harness, but it must not simulate success by calling private methods or modifying game state directly.

### Minimum Godot playtest

1. Launch local API.
2. Launch Godot client.
3. Connect through visible UI.
4. Create a 2-player game.
5. Choose civilizations.
6. Start game.
7. Switch viewers.
8. Inspect fog-safe map.
9. Select and move an own unit with pointer input.
10. Found a settlement.
11. Choose research.
12. Queue production.
13. End turns.
14. Perform diplomacy.
15. Exercise abstract in-game combat when practical.
16. Inspect safe feedback/events.
17. Concede or reach a configured victory.
18. Confirm hidden state/tokens do not appear in UI/logs.

Report `PASS`, `FAIL`, or `BLOCKED` exactly as defined by root `AGENTS.md`.

## Testing discipline

When changing `.gd`/`.tscn` files:

- run Godot import/parse checks;
- run the headless smoke test;
- run human-style playtesting for visible interaction changes;
- run root `bash scripts/ci.sh` if server/core/API code changed too.

Do not claim Godot verification passed because files merely exist on GitHub.

## Branch/PR policy

- Work on a feature/fix branch.
- Keep Godot work in a separate PR when practical.
- A Godot PR may depend on an unmerged API PR, but its base and dependency must be explicit.
- Draft PRs are appropriate while local Godot QA is blocked.
- Record exact Godot version and commands used by local QA in the PR.

## Scope control

Follow `TODO.md` phase order. If a desired GUI feature requires new authoritative/server data, add a narrow public API/query contract rather than recreating the rule in GDScript.
