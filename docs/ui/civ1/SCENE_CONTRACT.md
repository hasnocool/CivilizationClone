# Civ1-Inspired Client Scene Contract

This document turns the visual references in this directory into a client-facing implementation contract for CivilizationClone.

## 1. Stable scene identifiers

Clients, tests, docs, screenshots, and bug reports should refer to scenes using the `CIV1-UI-NNN` identifiers in `SCENE_INDEX.md` rather than client-specific class or file names.

Examples:

- `CIV1-UI-007` — strategic world map;
- `CIV1-UI-012` — city management;
- `CIV1-UI-037` — diplomacy conversation;
- `CIV1-UI-049` — spaceship overview.

## 2. Engine ownership vs. client ownership

### Engine/API owns

- authoritative game state;
- command legality;
- movement and combat resolution;
- city yields and production;
- research legality and progress;
- diplomacy state and AI decisions;
- government transitions;
- wonder completion;
- victory/defeat conditions;
- save/load semantics;
- deterministic events and replay behavior.

### Client owns

- scene routing;
- focus and selection state that is purely presentational;
- layout and responsive composition;
- input mapping;
- animation and transitions;
- colors, fonts, sprites, audio, and accessibility;
- rendering engine state into the scene families described here.

A client must not infer hidden rules from these mockups.

## 3. Recommended reusable scene families

```text
SceneRouter
├── BootSetupScene
├── StrategicMapScene
│   ├── MapViewport
│   ├── UnitPanel
│   ├── OrdersMenu
│   └── InspectOverlay
├── CityScene
│   ├── ResourceGrid
│   ├── CitizenStrip
│   ├── YieldPanel
│   ├── ProductionPanel
│   └── ImprovementsPanel
├── ResearchScene
├── CivilopediaScene
├── ReportScene
│   ├── AdvisorReport
│   └── WorldReport
├── DiplomacyScene
├── EventModal
├── PresentationScene
│   ├── Palace
│   ├── Wonder
│   └── Launch
├── SpaceshipScene
├── ResultsScene
└── SaveLoadScene
```

## 4. Minimum scene state

Each rendered scene should be reproducible from a small view model containing at least:

```text
scene_id
scene_family
title
body/model payload
available_actions
focused_action
return_scene
modal_stack
player_context
turn_context
```

Client-specific render state can extend this but should remain outside deterministic engine state unless it materially affects gameplay.

## 5. Action model

The visual labels in the `.ascii` and `.ansii` files are presentation examples. Internally, prefer stable action identifiers such as:

```text
continue
cancel
open_city
open_civilopedia
open_advisor
select_research
select_production
buy_production
sell_improvement
issue_unit_order
open_diplomacy
accept_deal
reject_deal
change_government
launch_spaceship
save_game
load_game
```

A UI label may be localized or restyled while the action identifier remains stable.

## 6. Navigation invariants

1. `CIV1-UI-007` World Map is the default in-game hub.
2. `CIV1-UI-012` City Management is the second major persistent workspace.
3. Advisors, World Reports, Civilopedia, Orders, and most dialogs should return to the scene that opened them unless an authoritative engine event redirects the player.
4. Modal confirmation must not mutate game state until its affirmative action is submitted.
5. Presentation-only scenes should never silently consume gameplay commands.
6. Victory or defeat transitions may lock normal map/city navigation and route into the results sequence.

## 7. Modal stack

Use one shared modal stack rather than making every confirmation a top-level scene.

```text
WORLD MAP
  └── ORDERS
      └── GENERIC-CONFIRM

CITY
  └── SELL IMPROVEMENT
      └── GENERIC-CONFIRM

DIPLOMACY
  └── DECLARE WAR
      └── GENERIC-CONFIRM
```

The reusable `GENERIC-CONFIRM` overlay in the layout files is deliberately outside the numbered 57-scene catalog.

## 8. Input equivalence

Every client should expose equivalent logical actions even when physical input differs:

| Logical action | TUI | Keyboard/mouse GUI | Gamepad/touch |
|---|---|---|---|
| move focus | arrows/tab | arrows/tab/hover | d-pad/stick/swipe |
| activate | enter/space | click/enter | primary/tap |
| cancel/back | escape | escape/back control | secondary/back gesture |
| map pan | arrows/vi keys | drag/edge/keys | stick/drag |
| inspect | hotkey/enter | click/context | primary/hold |

## 9. Responsive guidance

The references intentionally resemble low-resolution classic PC layouts. Modern clients should preserve hierarchy rather than pixel geometry.

Priority order for the strategic map:

1. map viewport;
2. focused tile/unit feedback;
3. critical turn/resources status;
4. available commands;
5. history/status log.

Priority order for city management:

1. city identity and population;
2. worked/resource tiles;
3. citizens and yields;
4. current production;
5. supported units and improvements;
6. secondary city actions.

## 10. Accessibility

Do not rely on color alone. The `.ansii` semantic tags are roles, not mandatory colors.

- focused selections should have a marker such as `>` or `▶` in addition to color;
- warnings should contain text/iconography in addition to red styling;
- progress bars should include numeric or textual progress when possible;
- all actions should be keyboard reachable in desktop/TUI clients;
- screen-reader-friendly clients should expose table/field names rather than ASCII art as raw unreadable decoration.

## 11. Testing references

Client tests may use these IDs for human-style acceptance scenarios. Examples:

```text
CIV1-UI-007 -> select settler -> open CIV1-UI-008 -> Found City
CIV1-UI-011 -> confirm -> CIV1-UI-012
CIV1-UI-012 -> Change Production -> CIV1-UI-013 -> select unit -> return
CIV1-UI-007 -> Advisors -> CIV1-UI-021 -> CIV1-UI-022 -> return
CIV1-UI-036 -> CIV1-UI-037 -> CIV1-UI-038 -> accept/reject -> return
CIV1-UI-049 -> launch confirmation -> CIV1-UI-050
```

Executable behavior remains governed by the repository's normal local QA and playtesting rules; these references simply provide a common visual vocabulary.
