# Civilization I UI/UX Scene Reference

This directory is the canonical visual reference for CivilizationClone clients implementing a Civilization-I-inspired interaction model without coupling presentation to engine state.

## Coverage

The reference catalogs **168 distinct UI state templates**. The original `CIV1-UI-001..057` IDs are preserved for compatibility; `058..168` cover the startup, menu, subview, special-unit, event, diplomacy, replay, and failure states that were compressed or omitted in the first pass.

A scene ID represents a visually or behaviorally distinct UI template. Content variants such as individual leaders, technologies, wonders, units, generated city names, or government-specific advisor costumes are parameters of those templates rather than separate scene IDs.

See `COVERAGE_AUDIT.md` for the evidence, scope, and inclusion rules used for the expanded audit.

## Goals

- catalog the documented Civilization I scene/menu/modal/report flow used as inspiration for CivilizationClone;
- give terminal/TUI, Bevy, Godot, Unity, Unreal, web, and future clients stable scene identifiers;
- provide both strict 7-bit `.ascii` wireframes and richer `.ansii` terminal-art references for every canonical ID;
- document the original IBM/DOS keyboard controls and map each binding to stable logical actions/scenes;
- document scene-to-scene ingress, exits, returns, modes, event injections, and terminal paths for all 168 IDs;
- keep original IDs stable as the reference grows;
- separate reusable scene families from one-off presentation;
- keep game logic in the engine/API and treat these files as presentation references only.

## Canonical references

- `COVERAGE_AUDIT.md` — audit of omissions in the original 57-scene pass, source material, and the canonical definition of a distinct UI state.
- `SCENE_INDEX.md` — stable `CIV1-UI-NNN` identifiers for every canonical UI state.
- `HOTKEYS.md` — IBM/DOS classic hotkeys, keyboard-only controls, context precedence, logical action IDs, and hotkey-to-scene Mermaid chart.
- `NAVIGATION.md` — exhaustive 168-state ingress/exit matrix, direct-key overlays, and subsystem Mermaid transition charts.
- `SCENE_GRAPH.md` — family-level navigation, exhaustive scene coverage map, and scene-family ownership graph.
- `mermaid-gallery.html` — browser gallery that automatically extracts and renders every Mermaid block from `SCENE_GRAPH.md`, `HOTKEYS.md`, and `NAVIGATION.md`, with search, theme switching, raw source, and SVG export.
- `SCENE_CONTRACT.md` — cross-client implementation contract, actions, ownership boundaries, responsive behavior, accessibility, and acceptance-test guidance.

## Mermaid gallery

Serve the repository through any local HTTP server and open:

```text
/docs/ui/civ1/mermaid-gallery.html
```

For example, from the repository root:

```bash
python -m http.server
```

Then visit the path above on the local server. The gallery reads the Markdown files directly, so Mermaid diagrams remain single-source and automatically reflect documentation edits after a reload.

## Layout sets

| Range | Category | ASCII | ANSII |
|---|---|---|---|
| 001-006 | Boot and game setup | `ascii/00_boot_setup.ascii` | `ansii/00_boot_setup.ansii` |
| 007-018 | Strategic map, cities, research | `ascii/01_core_gameplay.ascii` | `ansii/01_core_gameplay.ansii` |
| 019-034 | Civilopedia, advisors, world reports | `ascii/02_advisors_world.ascii` | `ansii/02_advisors_world.ansii` |
| 035-046 | Palace, diplomacy, government, events | `ascii/03_diplomacy_events.ascii` | `ansii/03_diplomacy_events.ansii` |
| 047-057 | Space race, victory, defeat, save/load | `ascii/04_space_endgame.ascii` | `ansii/04_space_endgame.ansii` |
| 058-085 | Startup/system, Game menu, turn/historian states | `ascii/05_system_menus.ascii` | `ansii/05_system_menus.ansii` |
| 086-104 | Unit modes, Diplomats, Caravans, minor tribes | `ascii/06_units_special.ascii` | `ansii/06_units_special.ansii` |
| 105-130 | City subviews, environmental/disaster events, report pages | `ascii/07_city_events_reports.ascii` | `ansii/07_city_events_reports.ansii` |
| 131-142 | Extended diplomacy | `ascii/08_diplomacy_extended.ascii` | `ansii/08_diplomacy_extended.ansii` |
| 143-168 | Space status, replay, failures, presentation/help states | `ascii/09_space_replay_misc.ascii` | `ansii/09_space_replay_misc.ansii` |

Start with `SCENE_INDEX.md`, then open the matching ASCII or ANSII range file. Use `HOTKEYS.md` to determine input bindings, `NAVIGATION.md` for exact scene ingress/exits, `SCENE_GRAPH.md` for the broader architecture/coverage view, and `mermaid-gallery.html` to view all charts together. Numeric ID order is not the runtime navigation order.

## Format conventions

### `.ascii`

Strict ASCII-only layouts. These are the portability baseline and should render correctly in a plain terminal using a monospace font.

### `.ansii`

ANSI-art-style references using box-drawing characters, stronger hierarchy, and semantic style tags such as `<TITLE>`, `<MENU>`, `<FOCUS>`, `<WARN>`, and `<INFO>`. The extension intentionally follows the project request spelling `.ansii`. Clients should map semantic roles to their own colors/themes instead of copying terminal escape codes literally.

## Important design boundary

These documents describe UI composition and flow. They do **not** define rules logic, hidden state, combat outcomes, production formulas, diplomacy AI, research legality, or persistence behavior. A client requests authoritative state from the engine and submits commands back through the engine/API.

## Recommended client architecture

```text
PHYSICAL INPUT
  |
  v
INPUT MAP / CLASSIC HOTKEY PROFILE
  |
  v
LOGICAL UI ACTIONS
  |
  v
CLIENT SCENE ROUTER <-------- RETURN / MODAL STACK
  |
  +-- boot/setup/system
  +-- strategic map / unit modes
  +-- city / city subviews
  +-- advisor/report/civilopedia
  +-- diplomacy / special units
  +-- event / notification / presentation
  +-- space race / endgame / replay
  +-- persistence
  |
  v
COMMANDS ---------------------> ENGINE/API
  ^                                |
  |                                v
  +--------- VIEW MODEL / EVENTS --+
```

The scene router should resolve hotkeys using the context precedence documented in `HOTKEYS.md` and use the transition semantics/return paths in `NAVIGATION.md`.

## Reusable scene families

The 168 canonical states should **not** become 168 unrelated code paths. They collapse into reusable families:

1. boot/setup/system selection;
2. menu/list selection;
3. strategic map and target-selection modes;
4. unit inspect/order/context dialogs;
5. city management and city subviews;
6. research/Civilopedia browser and two-page detail;
7. advisor/report tables and secondary pages;
8. diplomacy/leader negotiation and transactional dialogs;
9. special-unit result dialogs;
10. generic event/disaster/environment notifications;
11. palace/wonder/improvement presentations;
12. spaceship status/build/launch/in-flight presentation;
13. results/Hall of Fame/replay/Powergraph;
14. save/load/persistence prompts;
15. shared confirmations and contextual help.

Clients should favor reusable components and scene families while keeping every `CIV1-UI-NNN` state individually addressable for documentation, testing, screenshots, and accessibility.
