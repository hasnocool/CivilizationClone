# Civilization I UI/UX Scene Reference

This directory is the canonical visual reference for CivilizationClone clients that want a compact, Civilization-I-inspired interaction model without coupling presentation to engine state.

## Goals

- catalog the complete core Civilization I style scene flow used as inspiration for CivilizationClone;
- give terminal/TUI, Bevy, Godot, Unity, Unreal, web, and future clients stable scene identifiers;
- provide both strict 7-bit `.ascii` wireframes and richer `.ansii` terminal-art references;
- separate reusable scene families from one-off presentation so clients do not implement dozens of unrelated screens;
- keep game logic in the engine/API and treat these files as presentation references only.

## Layout sets

| Range | Category | ASCII | ANSII |
|---|---|---|---|
| 01-06 | Boot and game setup | `ascii/00_boot_setup.ascii` | `ansii/00_boot_setup.ansii` |
| 07-18 | Strategic map, cities, research | `ascii/01_core_gameplay.ascii` | `ansii/01_core_gameplay.ansii` |
| 19-34 | Civilopedia, advisors, world reports | `ascii/02_advisors_world.ascii` | `ansii/02_advisors_world.ansii` |
| 35-46 | Palace, diplomacy, government, events | `ascii/03_diplomacy_events.ascii` | `ansii/03_diplomacy_events.ansii` |
| 47-57 | Space race, victory, defeat, save/load | `ascii/04_space_endgame.ascii` | `ansii/04_space_endgame.ansii` |

See `SCENE_INDEX.md` for every scene ID and `SCENE_CONTRACT.md` for how client implementations should consume them.

## Format conventions

### `.ascii`

Strict ASCII-only layouts. These are the portability baseline and should render correctly in a plain terminal using a monospace font.

### `.ansii`

ANSI-art-style references using box-drawing characters, stronger hierarchy, and semantic style tags such as `<TITLE>`, `<MENU>`, `<FOCUS>`, `<WARN>`, and `<INFO>`. The extension intentionally follows the project request spelling `.ansii`. Clients may map those semantic roles to their own colors/themes rather than copying terminal escape codes literally.

## Important design boundary

These documents describe UI composition and flow. They do **not** define rules logic, hidden state, combat outcomes, production formulas, diplomacy AI, research legality, or persistence behavior. A client should request authoritative state from the engine and submit commands back through the engine/API.

## Recommended client architecture

```text
INPUT
  |
  v
CLIENT SCENE ROUTER
  |
  +-- map
  +-- city
  +-- advisor/report
  +-- diplomacy
  +-- research
  +-- event/modal
  +-- endgame
  |
  v
COMMANDS ---------------------> ENGINE/API
  ^                                |
  |                                v
  +--------- VIEW MODEL / EVENTS --+
```

## Scene families

The 57 reference scenes collapse into a much smaller implementation surface:

1. boot/setup;
2. strategic map;
3. city management;
4. research/civilopedia;
5. advisor/report table;
6. diplomacy/leader dialog;
7. generic event/modal;
8. palace/wonder presentation;
9. spaceship builder;
10. endgame/results;
11. save/load browser.

Clients should favor reusable components and scene families over creating 57 unique code paths.