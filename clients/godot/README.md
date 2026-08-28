# CivilizationClone Godot Client

This is a Godot 4 client for the authoritative CivilizationClone `/api/v1` service.

## Engine version

Target: **Godot 4.7.x**. Development is currently aligned with Godot 4.7.2 stable.

The project uses the compatibility renderer so local QA can run on a wider range of development hardware.

## Architectural boundary

The Godot project is presentation and input only.

It must never:

- import or reimplement Python engine rules;
- mutate save files or SQLite directly;
- infer hidden state from predictable identifiers;
- decide authoritative outcomes locally;
- use local randomness as simulation authority.

It may:

- render player-authorized projections;
- cache public presentation state;
- generate unique client command IDs;
- submit commands to `/api/v1`;
- display typed feedback and authorized events.

The server remains authoritative for legality, fog of war, ownership, economy, research, diplomacy, combat resolution, victory, persistence, and replay.

## Responsive window and layout

The desktop window is intentionally **not fixed-size**. It can be freely resized and the UI responds to the actual window dimensions rather than assuming a single virtual desktop resolution.

Responsive behavior includes:

- no `window_width_override` or `window_height_override`;
- native resizable window enabled;
- content stretching disabled so Control containers receive the real viewport dimensions;
- horizontal action rows converted to `HFlowContainer` so controls wrap instead of overlapping;
- the game map/sidebar uses a generic `SplitContainer` whose orientation changes automatically;
- wide windows show map and controls side-by-side;
- narrow windows stack map and controls vertically;
- lobby content becomes vertically scrollable when window height is constrained;
- dense grids reduce their column count at narrow/compact breakpoints;
- text labels wrap and long button text trims safely;
- the authorized hex map dynamically scales and recenters its hexes to fit the available map rectangle;
- event/control panes remain scrollable rather than pushing neighboring UI outside the window.

Current responsive breakpoints are presentation-only and can change without affecting gameplay:

- below 900 px viewport width: stacked game layout and two-column form grids;
- below 640 px viewport width: compact one-column action-button grids.

## Current playable flow

1. Run the CivilizationClone API locally.
2. Open `clients/godot/project.godot` in Godot 4.7.x.
3. Connect to the API, default `http://127.0.0.1:8000`.
4. Configure a 2–4 player hotseat game.
5. Choose a civilization for each player.
6. Create and start the game.
7. Switch the active viewer with the viewer selector.
8. Click one of the current viewer's units to select it.
9. Click an empty authorized tile to submit `MoveUnit`.
10. Click a visible opposing unit while one of your units is selected to submit `AttackUnit`.
11. Use the side panel for settlement founding, worked tiles, research, production, diplomacy, turn advancement, concession, and event inspection.

The production definition field deliberately remains server-validated rather than embedding a second copy of gameplay content in Godot. A later API/catalog phase should expose richer production metadata for dropdowns and tooltips.

## Input model

### Map

- Click own unit: select it.
- Click own settlement: select it for settlement actions.
- With own unit selected, click empty tile: move attempt.
- With own unit selected, click visible enemy unit: attack attempt.
- Click any authorized tile: select tile for worked-tile actions.

### Hotseat

The client keeps credentials only in memory for the current process. It does not write bearer tokens to disk.

## Local verification

From repository root:

```bash
bash scripts/verify_godot_client.sh
```

Human-style playtest:

```bash
bash scripts/playtest_godot.sh
```

The human-style test must use the real Godot window with normal pointer/keyboard input. API-level tests do not replace this acceptance test.

Resize acceptance must include, at minimum:

1. launch at the default window size;
2. resize substantially wider and taller;
3. resize below 900 px width and confirm map/sidebar switch to a vertical stack;
4. resize below 640 px width and confirm action grids collapse to one column;
5. make the window short enough to require lobby/sidebar scrolling;
6. confirm controls wrap instead of overlap at every size;
7. confirm the hex map remains centered, visible, and clickable after each resize;
8. return to a large window and confirm the layout expands again without stale clipping.

## Files

```text
clients/godot/
├── project.godot
├── scenes/
│   └── main.tscn
├── scripts/
│   ├── api_client.gd
│   ├── hex_map.gd
│   ├── main.gd
│   └── responsive_layout.gd
├── tests/
│   └── smoke_test.gd
├── AGENTS.md
├── README.md
└── TODO.md
```

## Security/privacy rules

- Bearer credentials are never printed into the event log UI.
- The HTTP client does not include credentials in URLs.
- The client renders only projections returned for the selected player credential.
- Error UI should display safe server detail/feedback, not raw stack traces.
- Hidden unit IDs must never be guessed or surfaced by client code.

## Future client work

See `TODO.md`. The major next steps are server-driven production/research catalogs, richer inspector panels, WebSocket event updates, attach/reconnect flows, accessibility, animation/audio, and systematic Godot QA/playtest automation.
