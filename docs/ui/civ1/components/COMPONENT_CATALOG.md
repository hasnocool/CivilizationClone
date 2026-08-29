# Civ1-Inspired Terminal Component Catalog

Components are reusable presentation primitives shared by the canonical scene references. A component describes composition, semantics, states, fallbacks, and accessibility behavior; it does not contain game rules.

## Component contract

Every reusable component should document:

```text
component_id
purpose
inputs
states
ASCII representation
ANSI representation
focus behavior
selection behavior
error/warning behavior
animation hooks
responsive behavior
reduced-motion behavior
accessibility behavior
```

## Component families

### Navigation and framing

- `CIV1-COMP-FRAME` — outer scene/modal frame.
- `CIV1-COMP-PANEL` — nested content panel.
- `CIV1-COMP-TABBAR` — top-level section navigation.
- `CIV1-COMP-MENULIST` — vertical command/list selector.
- `CIV1-COMP-ACTIONBAR` — contextual actions.
- `CIV1-COMP-BREADCRUMB` — navigation context.

### Input and focus

- `CIV1-COMP-CURSOR` — keyboard/map cursor.
- `CIV1-COMP-FOCUS` — semantic focus treatment.
- `CIV1-COMP-TEXTFIELD` — terminal text entry.
- `CIV1-COMP-TOGGLE` — binary/multi-state setting.
- `CIV1-COMP-SELECTION` — single/multi-selection marker.

### World map

- `CIV1-COMP-MAPGRID` — strategic map viewport.
- `CIV1-COMP-TILE` — terrain cell.
- `CIV1-COMP-TERRAIN` — terrain glyph/state.
- `CIV1-COMP-RESOURCE` — yield/resource marker.
- `CIV1-COMP-ROAD` — route/infrastructure marker.
- `CIV1-COMP-CITYMARKER` — city marker and label.
- `CIV1-COMP-UNITMARKER` — unit stack/identity.
- `CIV1-COMP-FOG` — unexplored/hidden terrain.
- `CIV1-COMP-MAPPATH` — movement route preview.

### City and economy

- `CIV1-COMP-CITIZENSTRIP` — citizen/specialist summary.
- `CIV1-COMP-YIELDPANEL` — food/shields/trade values.
- `CIV1-COMP-PROGRESSBAR` — generic progress.
- `CIV1-COMP-PRODUCTIONQUEUE` — current/next production.
- `CIV1-COMP-IMPROVEMENTLIST` — buildings/wonders.
- `CIV1-COMP-CITYGRID` — worked resource map.

### Reports and knowledge

- `CIV1-COMP-TABLE` — aligned report table.
- `CIV1-COMP-GRAPH` — chart/graph.
- `CIV1-COMP-TECHCARD` — technology detail.
- `CIV1-COMP-TECHCHAIN` — prerequisites/unlocks.
- `CIV1-COMP-CIVILOPEDIAENTRY` — knowledge article.

### Diplomacy and events

- `CIV1-COMP-LEADERPORTRAIT` — terminal leader portrait.
- `CIV1-COMP-DIALOGUE` — leader/player dialogue.
- `CIV1-COMP-TRADEOFFER` — transaction terms.
- `CIV1-COMP-TREATYBADGE` — diplomatic state.
- `CIV1-COMP-EVENTCARD` — event/notification modal.
- `CIV1-COMP-SEVERITY` — information severity cue.

### Presentation and results

- `CIV1-COMP-PALACEVIEW` — palace/improvement presentation area.
- `CIV1-COMP-WONDERVIEW` — wonder completion view.
- `CIV1-COMP-SPACESHIP` — spaceship schematic/status.
- `CIV1-COMP-REPLAYTIMELINE` — replay controls/timeline.
- `CIV1-COMP-POWERGRAPH` — comparative history chart.
- `CIV1-COMP-RATINGBLOCK` — end-game score/rating.

## Composition rule

Scenes should assemble components rather than redefine the same primitive repeatedly.

```text
Scene
 ├─ FRAME
 ├─ TABBAR
 ├─ CONTENT
 │   ├─ MAPGRID
 │   │   ├─ TILE
 │   │   ├─ CITYMARKER
 │   │   └─ UNITMARKER
 │   └─ YIELDPANEL
 └─ ACTIONBAR
```

## State naming

Component states should use predictable names:

```text
DEFAULT
FOCUSED
SELECTED
DISABLED
ACTIVE
BUSY
WARNING
ERROR
COMPLETED
HIDDEN
```

A component may expose additional domain-neutral states where necessary, such as `OCCUPIED`, `TARGETED`, or `CONTESTED`.
