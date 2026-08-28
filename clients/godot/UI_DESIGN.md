# Godot UI Design Contract

This document defines the presentation contract for the CivilizationClone Godot client. It is a client-only concern; none of these rules may alter authoritative simulation behavior.

## Goals

The interface must remain understandable and operable from the minimum supported 640×480 window through large desktop displays. Controls may wrap, stack, scroll, or trim text, but they must not overlap, disappear outside the viewport, or require a specific fixed resolution.

## Information hierarchy

The client is organized into four layers:

1. **Application toolbar** — always reachable controls for Menu, Settings, and current display/UI-scale status.
2. **Connection/lobby layer** — API connection and hotseat game creation.
3. **Game layer** — viewer/game status, map, action panels, events, and feedback.
4. **Settings layer** — full-window modal presentation settings above all other client UI.

The settings layer never contains game authority or credentials.

## Application toolbar

The toolbar should stay directly beneath the client title and wrap instead of clipping when horizontal space is limited.

Required controls:

- `Menu` with Display & Interface Settings, Fit Window to Screen, and Reset UI Scale;
- direct `Settings` button so display controls are discoverable without opening a menu;
- compact current display summary such as `1280×720 • UI 100%`.

At narrow widths the summary may move onto another wrapped row. Menu and Settings controls must remain visible.

## Panels

All major panels use consistent visual treatment:

- visible background separation from the window;
- one-pixel border;
- rounded corners;
- interior content margins;
- no child control is allowed to rely on the panel edge as spacing;
- dense content uses vertical scrolling instead of increasing minimum window size.

Panel contents should prefer vertical groups. Horizontal groups are reserved for short action clusters and must use flow/wrap behavior.

## Main game layout

### Wide layout

At widths of 900 px or greater:

- map and action sidebar are side-by-side;
- map gets approximately twice the stretch weight of the sidebar;
- both remain resizable through the split container;
- the sidebar scrolls independently.

### Narrow layout

Below 900 px:

- map and sidebar stack vertically;
- the map remains visible and scales its hexes to its current rectangle;
- the action panel remains scrollable;
- form grids reduce to two columns.

### Compact layout

Below 640 px layout width, or at high UI scale where effective content becomes similarly constrained:

- action grids collapse to one column;
- horizontal action rows wrap;
- labels wrap;
- buttons may ellipsize text rather than exceed their container;
- tooltips preserve the complete text when a control is trimmed.

The native window itself has a minimum physical size of 640×480.

## Dropdown and menu rules

Every `OptionButton` and application popup must obey these rules:

- `fit_to_longest_item` is disabled;
- the control expands only within its assigned container;
- displayed button text may trim with ellipsis;
- selected full text is available through a tooltip;
- popup menus are non-native so the client can consistently constrain them;
- popup maximum width is the smaller of 560 px or the visible viewport minus 32 px;
- popup maximum height is the smaller of 440 px or the visible viewport minus 48 px;
- longer lists expose a search field;
- newly-created runtime dropdowns receive the same normalization as controls present at startup.

A long civilization, settlement, research, or future production name must never force the sidebar or lobby wider than the window.

## Dynamic hotseat rows

Hotseat player rows are constructed only after API connection, so the responsive system must handle nodes added after initial scene creation.

Each row must:

- wrap onto multiple lines if needed;
- allow player name and civilization controls to shrink within their container;
- preserve complete selected dropdown text through tooltip/popup access;
- remain usable at 640×480 with lobby scrolling.

## Settings screen

Settings occupy the full available client rectangle with a scrollable content area. There is no fixed modal width that can exceed a small window.

### Window mode

Choices:

- Windowed;
- Maximized;
- Fullscreen;
- Exclusive Fullscreen.

### Windowed resolution

Choices:

- Fit to screen (90% of current usable display area);
- 800×600;
- 1024×576;
- 1024×768;
- 1280×720;
- 1366×768;
- 1600×900;
- 1920×1080;
- 2560×1440.

A requested windowed size is clamped to the monitor's usable area so the title bar and controls cannot be stranded offscreen.

### UI scale

Choices:

- 75%;
- 85%;
- 100%;
- 110%;
- 125%;
- 150%;
- 175%.

UI scaling uses the root `Window.content_scale_factor`. It is presentation-only and must never enter commands, deterministic state, events, replay hashes, or server requests.

### Persistence

Settings are stored in `user://client_settings.cfg` using `ConfigFile` and restored on launch.

Allowed persisted values:

- window mode;
- remembered windowed width/height;
- UI scale.

Credentials and game/session data are prohibited from this file.

## Accessibility and visibility

- Controls should have at least a 36 px default interactive height before UI scaling.
- Text labels wrap rather than draw over neighboring controls.
- Long buttons trim safely when wrapping cannot provide enough space.
- Scroll containers must remain keyboard/mouse reachable.
- Settings can be dismissed with the normal `ui_cancel` action.
- Color is not the only carrier of gameplay meaning; labels/markers remain required.

## Acceptance matrix

Local human-style QA must verify at least:

| Window / mode | UI scale | Required result |
| --- | ---: | --- |
| 640×480 windowed | 75% | all primary controls reachable; no overlap |
| 800×600 windowed | 100% | lobby and game panels usable |
| 1024×768 windowed | 125% | dropdowns stay on-screen; scrolling works |
| 1280×720 windowed | 100% | normal side-by-side game layout |
| 1600×900 windowed | 100% | map expands without excessive sidebar width |
| Fit to screen | 100% | centered safe window on current monitor |
| Maximized | 100% | full usable area reflows correctly |
| Fullscreen | 100% | no stale windowed clipping |
| 1280×720 windowed | 175% | controls remain reachable through wrapping/scrolling |

For every row above, open all populated dropdowns and verify their popup is entirely reachable within the visible viewport.
