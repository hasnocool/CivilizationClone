# Civ1-Inspired Client Scene Contract

This document turns the visual references in this directory into a client-facing implementation contract for CivilizationClone.

## 1. Stable scene identifiers

Clients, tests, docs, screenshots, and bug reports should refer to scenes using the `CIV1-UI-NNN` identifiers in `SCENE_INDEX.md` rather than client-specific class or file names.

The canonical catalog currently contains **168 distinct UI state templates**. `CIV1-UI-001..057` are the original IDs and remain stable; `058..168` extend coverage to documented system/setup states, menus, unit modes, city subviews, special-unit interactions, events, diplomacy branches, replay, and endgame/failure states.

Examples:

- `CIV1-UI-007` — strategic world map;
- `CIV1-UI-012` — city management;
- `CIV1-UI-071` — Game menu;
- `CIV1-UI-087` — Go To destination targeting;
- `CIV1-UI-106` — city happiness chart;
- `CIV1-UI-135` — post-treaty diplomacy menu;
- `CIV1-UI-150` — replay options;
- `CIV1-UI-154` — Powergraph.

`COVERAGE_AUDIT.md` defines what counts as a separate canonical state and documents why the original 57-state pass was incomplete.

## 2. Engine ownership vs. client ownership

### Engine/API owns

- authoritative game state;
- command legality;
- movement and combat resolution;
- city yields and production;
- research legality and progress;
- diplomacy state and AI decisions;
- government transitions;
- wonder completion and obsolescence;
- environmental/disaster outcomes;
- special-unit outcomes;
- victory/defeat conditions;
- save/load semantics;
- deterministic events and replay behavior.

### Client owns

- scene routing from authoritative state/events;
- focus and selection state that is purely presentational;
- layout and responsive composition;
- input mapping;
- animation and transitions;
- colors, fonts, sprites, audio, and accessibility;
- rendering engine state into the scene families described here.

A client must not infer hidden rules from these mockups.

## 3. Recommended reusable scene families

The 168 stable IDs are testable/documentable states, **not** a recommendation to write 168 unrelated scene classes.

```text
SceneRouter
├── BootSystemScene
│   ├── Credits
│   ├── SetupSelector
│   ├── DriverSelector
│   ├── NameEntry
│   └── CopyProtectionPrompt
├── MenuScene
│   ├── MainMenu
│   ├── GameMenu
│   ├── OptionsMenu
│   └── GenericListPicker
├── StrategicMapScene
│   ├── MapViewport
│   ├── UnitPanel
│   ├── OrdersMenu
│   ├── InspectOverlay
│   ├── TargetSelectionMode
│   └── EndTurnOverlay
├── UnitInteractionScene
│   ├── StackActivation
│   ├── SettlerOrders
│   ├── DiplomatActions
│   └── CaravanActions
├── CityScene
│   ├── ResourceGrid
│   ├── CitizenStrip
│   ├── YieldPanel
│   ├── ProductionPanel
│   ├── ImprovementsPanel
│   ├── InfoSubview
│   ├── HappySubview
│   ├── MapSubview
│   └── WorkerAssignmentMode
├── ResearchScene
│   └── ContextHelpOverlay
├── CivilopediaScene
│   ├── SectionMenu
│   ├── Browser
│   ├── HistoryPage
│   └── GameplayPage
├── ReportScene
│   ├── AdvisorReport
│   ├── AdvisorDetailPage
│   ├── WorldReport
│   └── HistorianRanking
├── DiplomacyScene
│   ├── LeaderDialog
│   ├── TransactionPrompt
│   ├── TreatyMenu
│   └── MilitaryProposal
├── EventModal
│   ├── CityEvent
│   ├── DisasterEvent
│   ├── EnvironmentEvent
│   ├── CombatEvent
│   └── EconomyFailureEvent
├── PresentationScene
│   ├── Palace
│   ├── Wonder
│   ├── Improvement
│   └── Launch
├── SpaceshipScene
│   ├── Builder
│   ├── RivalStatus
│   └── InFlightStatus
├── ResultsScene
│   ├── FinalRating
│   ├── HallOfFame
│   ├── ReplaySelector
│   ├── ReplayPlayback
│   └── Powergraph
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

Mode-like states such as `CIV1-UI-087` Go To targeting and `CIV1-UI-108` city worker reassignment also need explicit cursor/selection context, but that context should remain client-side unless it changes authoritative gameplay state.

## 5. Action model

The visual labels in the `.ascii` and `.ansii` files are presentation examples. Internally, prefer stable action identifiers such as:

```text
continue
cancel
open_game_menu
open_options
open_city
open_civilopedia
open_advisor
select_research
select_production
buy_production
sell_improvement
issue_unit_order
select_map_target
activate_unit
reassign_home_city
assign_worker
assign_specialist
open_diplomacy
accept_deal
reject_deal
break_treaty
change_government
launch_spaceship
open_replay
advance_replay
save_game
load_game
```

A UI label may be localized or restyled while the action identifier remains stable.

## 6. Navigation invariants

1. `CIV1-UI-007` World Map is the default in-game hub.
2. `CIV1-UI-012` City Management is the second major persistent workspace.
3. System/setup states (`058..070`) precede or wrap normal play rather than owning rules state.
4. Advisors, World Reports, Civilopedia, Orders, and most dialogs should return to the scene that opened them unless an authoritative engine event redirects the player.
5. Mode states such as Go To targeting and worker assignment must have a deterministic cancel path back to their caller.
6. Modal confirmation must not mutate game state until its affirmative action is submitted.
7. Event/presentation scenes should never silently consume gameplay commands.
8. Diplomacy subflows may branch through several transactional states before returning to the map.
9. Victory/defeat/end-of-history transitions may lock normal map/city navigation and route into results/replay.
10. Replay is a presentation of recorded history; it must not mutate authoritative game state.

## 7. Modal stack

Use one shared modal stack for generic confirmations, but preserve dedicated canonical states when the original interaction has materially different wording/actions.

```text
WORLD MAP
  └── GAME MENU
      └── QUIT CONFIRMATION (CIV1-UI-077)

WORLD MAP
  └── UNIT ORDERS
      └── GENERIC-CONFIRM

CITY
  └── SELL IMPROVEMENT
      └── GENERIC-CONFIRM

DIPLOMACY
  └── BREAK TREATY WARNING (CIV1-UI-139)

SPACE PROGRAM
  └── LAUNCH CONFIRMATION (CIV1-UI-144)
```

The reusable `GENERIC-CONFIRM` overlay is deliberately outside the numbered **168-scene catalog**.

## 8. Input equivalence

Every client should expose equivalent logical actions even when physical input differs:

| Logical action | TUI | Keyboard/mouse GUI | Gamepad/touch |
|---|---|---|---|
| move focus | arrows/tab | arrows/tab/hover | d-pad/stick/swipe |
| activate | enter/space | click/enter | primary/tap |
| cancel/back | escape | escape/back control | secondary/back gesture |
| map pan | arrows/vi keys | drag/edge/keys | stick/drag |
| target map square | cursor + enter | pointer + click | stick/tap |
| inspect | hotkey/enter | click/context | primary/hold |
| advance replay | key/enter | click/control | primary/tap |

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
6. active city subview or assignment mode;
7. secondary city actions.

For small screens, full-screen modals/subviews are preferable to compressing tables until they become unreadable.

## 10. Accessibility

Do not rely on color alone. The `.ansii` semantic tags are roles, not mandatory colors.

- focused selections should have a marker such as `>` or `▶` in addition to color;
- warnings should contain text/iconography in addition to red styling;
- progress bars should include numeric or textual progress when possible;
- all actions should be keyboard reachable in desktop/TUI clients;
- target-selection modes must expose the selected tile in text;
- replay controls must be keyboard reachable and pausable;
- screen-reader-friendly clients should expose table/field names rather than ASCII art as raw unreadable decoration.

## 11. Testing references

Client tests may use these IDs for human-style acceptance scenarios. Examples:

```text
CIV1-UI-060 -> Customize World -> CIV1-UI-062 -> 063 -> 064 -> 065 -> CIV1-UI-004
CIV1-UI-007 -> CIV1-UI-071 -> CIV1-UI-072 -> toggle End of Turn -> return
CIV1-UI-007 -> select unit -> CIV1-UI-086 -> CIV1-UI-087 -> select target -> return
CIV1-UI-007 -> settler -> CIV1-UI-089 -> Found City -> CIV1-UI-011 -> CIV1-UI-012
CIV1-UI-012 -> CIV1-UI-106 -> return -> CIV1-UI-108 -> assign worker -> return
CIV1-UI-040 -> incite revolt -> CIV1-UI-093 -> pay -> CIV1-UI-094 -> map
CIV1-UI-132 -> peace -> CIV1-UI-142 -> CIV1-UI-135 -> CIV1-UI-136 -> return
CIV1-UI-049 -> CIV1-UI-144 -> launch -> CIV1-UI-050 -> CIV1-UI-145
CIV1-UI-054 -> CIV1-UI-150 -> CIV1-UI-151 or CIV1-UI-152 -> CIV1-UI-154
```

Executable behavior remains governed by the repository's normal local QA and playtesting rules; these references provide a stable visual and navigation vocabulary for those tests.