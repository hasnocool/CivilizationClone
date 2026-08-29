# Framing and Navigation Components

## CIV1-COMP-FRAME

The primary visual container for a scene, modal, report, or presentation. A frame establishes hierarchy and gives the terminal composition a stable rectangle.

### Responsibilities

- provide consistent outer margins;
- establish title placement;
- delimit content from status and actions;
- support static and animated border variants;
- maintain fixed dimensions during animation whenever possible.

### Variants

```text
ASCII_DOUBLE
ASCII_SINGLE
ANSI_DOUBLE
ANSI_HEAVY
ANSI_MINIMAL
FULL_WIDTH
COMPACT_MODAL
```

### State hooks

`STATIC`, `FOCUS`, `WARNING`, `CRITICAL`, `REVEAL`, `CLOSE`.

## CIV1-COMP-PANEL

A nested region used to divide maps, statistics, reports, production lists, or dialogue.

Panels should have one visual job. Avoid deeply nested borders that waste scarce terminal columns.

## CIV1-COMP-TABBAR

Top-level navigation such as `GAME | ORDERS | ADVISORS | WORLD | CIVILOPEDIA`.

Requirements:

- active tab must be visually distinct without color dependency;
- keyboard focus follows logical tab order;
- long labels require truncation rules or horizontal navigation;
- selected and merely focused tabs are distinct states.

## CIV1-COMP-MENULIST

Vertical command selection used by orders, setup, game menus, production, diplomacy, and system dialogs.

Recommended rendering:

```text
> Move
  Wait
  Sentry
```

Focused state should use a persistent marker. ANSI emphasis may supplement it.

## CIV1-COMP-ACTIONBAR

Bottom or side region containing contextual actions.

Example:

```text
[PREV] [NEXT] [SELL] [RENAME] [EXIT]
```

Actions should expose stable logical IDs even when visible wording changes.

## CIV1-COMP-BREADCRUMB

Optional hierarchy indicator for Civilopedia, reports, and nested menus.

```text
CIVILOPEDIA > UNITS > LEGION
```

## CIV1-COMP-CURSOR

The universal point-of-attention indicator. It has two primary forms: menu cursor and map cursor.

Menu cursor:

```text
▶ Move
  Wait
```

Map cursor:

```text
.. .. [@] .. ..
```

Cursor motion may use `EFFECT.CURSOR.MOVE`; blink should always have a static fallback.

## CIV1-COMP-FOCUS

A semantic layer that indicates keyboard/gamepad focus independently of selection. It may add a marker, border, inverse emphasis, or ANSI role.

Focus must survive monochrome and reduced-motion modes.

## CIV1-COMP-TEXTFIELD

Terminal input control for city names, player names, filenames, and settings.

Features:

- visible insertion point;
- fixed or maximum width;
- safe clipping/truncation;
- submit/cancel actions;
- placeholder text where useful;
- validation feedback without destroying entered text.

Example:

```text
City Name: [ Antium______________]
```

## CIV1-COMP-TOGGLE

Represents binary or enumerated settings.

```text
Sound: [ON]
Grid:  [OFF]
```

Use text plus marker; do not rely on color alone.

## CIV1-COMP-SELECTION

Shared selection grammar for lists, map cells, technologies, resources, and report rows.

Recommended semantic states:

```text
DEFAULT
FOCUSED
SELECTED
DISABLED
INVALID
TARGET
```

Selection transitions may use `EFFECT.CURSOR.PULSE` or `EFFECT.CURSOR.TARGET` but the final selected state must be static.
