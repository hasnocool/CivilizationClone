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
- display typed feedback and authorized events;
- persist local presentation/display preferences under `user://`.

The server remains authoritative for legality, fog of war, ownership, economy, research, diplomacy, combat resolution, victory, persistence, and replay.

See `API_COVERAGE.md` for the explicit mapping between the current `/api/v1` surface and Godot.

## Responsive window and layout

The desktop window is intentionally **not fixed-size**. It can be freely resized and the UI responds to the actual window dimensions rather than assuming a single virtual desktop resolution.

Responsive behavior includes:

- no `window_width_override` or `window_height_override`;
- native resizable window enabled;
- content stretching disabled so Control containers receive the real viewport dimensions;
- horizontal action rows converted to `HFlowContainer` so controls wrap instead of overlapping;
- dynamically-created player rows are normalized after they are constructed, not only at initial scene load;
- the game map/sidebar uses a generic `SplitContainer` whose orientation changes automatically;
- wide windows show map and controls side-by-side;
- narrow windows stack map and controls vertically;
- lobby content becomes vertically scrollable when window height is constrained;
- dense grids reduce their column count at narrow/compact breakpoints;
- text labels wrap and long button text trims safely;
- dropdown controls do not reserve width for their longest item;
- dropdown popup windows are clamped to the visible viewport and become searchable for longer lists;
- selected dropdown text is available as a tooltip when the control itself has to trim it;
- panels receive consistent interior margins/borders so controls do not visually collide with panel edges;
- the authorized hex map dynamically scales and recenters its hexes to fit the available map rectangle;
- event/control panes remain vertically scrollable rather than pushing neighboring UI outside the window.

Current responsive breakpoints are presentation-only and can change without affecting gameplay:

- below 900 px viewport width: stacked game layout and two-column form grids;
- below 640 px viewport width: compact one-column action-button grids.

## Display & Interface Settings

The client toolbar provides **Menu** and **Settings** controls at all stages of the UI. The settings screen is full-window and scroll-safe, so it remains usable even at small resolutions.

Available settings:

- window mode: Windowed, Maximized, Fullscreen, Exclusive Fullscreen;
- windowed resolution presets: 800×600, 1024×576, 1024×768, 1280×720, 1366×768, 1600×900, 1920×1080, and 2560×1440;
- **Fit to screen (90%)**, which chooses a safe window size from the current display's usable area;
- UI scale: 75%, 85%, 100%, 110%, 125%, 150%, and 175%;
- Reset Defaults;
- quick toolbar actions for fitting the window to the current screen and resetting UI scale.

Windowed resolutions are clamped to the current monitor's usable area so selecting a preset larger than the monitor cannot strand controls offscreen. The minimum supported resizable window is 640×480.

Display preferences are saved to:

```text
user://client_settings.cfg
```

Only presentation preferences are stored there. API credentials, game authority, and simulation state are never written into the client settings file.

## Current `/api/v1` coverage

The Godot client consumes the current POC lifecycle, gameplay, discovery, authorized option, and live-event surfaces rather than only the original hotseat happy path.

Implemented lifecycle/setup fields include:

- health, civilization, and rules-content discovery;
- game ID and seed;
- player count and map radius;
- map water percentage and resource percentage;
- per-player civilization selection;
- per-player `human` / `bot` controller selection;
- admin-authorized StartGame;
- manual attach to an existing game using a player credential;
- local disconnect/session clearing.

All current POC gameplay command types are sent through the public command endpoint. State, legal actions, research options, settlement production options, event history, and live events are always fetched with the selected player's credential when authorization is required.

## Server-driven rules/content browser

The client does not copy unit/building/technology registries into GDScript.

Public presentation metadata comes from:

- `GET /api/v1/rules/civilizations`;
- `GET /api/v1/rules/content`.

Player-specific legality/cost information comes from:

- `GET /api/v1/games/{game_id}/research-options`;
- `GET /api/v1/games/{game_id}/production-options?settlement_id=...`.

The **Rules Browser** shows civilization descriptions, tags, starting resources, bonuses, unique content, technology costs, prerequisites, unlocks, and current viewer research status.

The production area uses a server-populated dropdown instead of asking the user to type a gameplay definition ID. Visible labels use server-provided names and costs. The old line edit remains hidden only as an internal bridge into the already-existing command handler; it is not a source of rules or user input.

Production choices deliberately distinguish two states:

- **queue now** — whether `QueueProduction` can currently accept that item for the selected settlement/viewer;
- **completion gate** — stable civilization/research requirements that must be satisfied before the queued item can complete.

This preserves the current engine rule that some known items may be queued before their research/civilization completion gate is met. Such entries stay visibly annotated rather than being incorrectly removed by client logic.

Research choices use the viewer's authoritative effective cost after civilization modifiers and current-turn legality. Raw technology IDs remain command metadata only.

## Live authorized events

The Godot client uses `WebSocketPeer` for the v1 event WebSocket.

- requested protocols are `civilization.v1` followed by the player token;
- the token is **never** placed in the WebSocket URL;
- `after_sequence` is the only resume value in the URL;
- an authorized HTTP event query bootstraps the cursor before the live connection;
- viewer changes close the old stream and authenticate a new one;
- policy close (`1008`) is presented as an authorization problem;
- other disconnects use bounded exponential retry;
- incoming authorized events trigger normal authenticated projection refreshes.

The live-event status appears in the game toolbar.

## Attach existing game

The connection panel also supports attaching to an existing game without recreating it.

Required:

- game ID;
- player token.

Optional:

- player ID, which is checked against the viewer identity returned by the authorized state projection.

The token field is masked. The token stays in process memory only. **Disconnect / Clear Session** closes the event stream and clears admin/player credentials from client memory.

## Current playable flow

1. Run the CivilizationClone API locally.
2. Open `clients/godot/project.godot` in Godot 4.7.x.
3. Connect to the API, default `http://127.0.0.1:8000`.
4. Configure game ID, seed, player count, radius, water %, and resource %.
5. Configure each player name, civilization, and Human/Bot controller type.
6. Create and start the game.
7. Switch the active viewer with the viewer selector.
8. Observe live authorized event-stream status in the game toolbar.
9. Browse civilization and technology details from the server-driven Rules Browser.
10. Click one of the current viewer's units to select it.
11. Click an empty authorized tile to submit `MoveUnit`.
12. Click a visible opposing unit while one of your units is selected to submit `AttackUnit`.
13. Found/select a settlement and choose production from the authorized server-driven dropdown.
14. Choose research using server names and effective viewer costs.
15. Use the side panel for worked tiles, diplomacy, turn advancement, concession, and event inspection.
16. Use **Disconnect / Clear Session** to remove in-memory credentials and return to the connection screen.

Alternatively, use **Attach Existing Game** from the connection panel with an existing game ID and player token.

## Input model

### Map

- Click own unit: select it.
- Click own settlement: select it for settlement actions.
- With own unit selected, click empty tile: move attempt.
- With own unit selected, click visible enemy unit: attack attempt.
- Click any authorized tile: select tile for worked-tile actions.

### Hotseat / controller setup

The client keeps credentials only in memory for the current process. It does not write bearer tokens to disk.

The lobby can submit `human` or `bot` controller values through the existing enrollment API. Godot does not implement bot logic itself; server/application behavior remains authoritative.

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

API/content acceptance should include, at minimum:

1. connect to the API and confirm the public rules browser populates;
2. create a game using non-default water/resource values;
3. create at least one Human and one Bot enrollment where the server setup supports it;
4. verify the game starts only through the public admin-authorized command path;
5. found a settlement and confirm the production dropdown populates from the authorized endpoint;
6. verify a queueable future item remains selectable but visibly shows its completion gate;
7. verify an item the current viewer cannot queue is disabled/annotated;
8. verify research labels use server names and effective civilization-adjusted costs;
9. switch viewers and confirm research/production choices re-authorize for the new player;
10. browse technology prerequisites/unlocks and both civilization detail cards;
11. verify the live-event indicator reaches `live` and commands refresh state without manual Refresh;
12. clear the session and verify credentials are removed from the client UI/process state;
13. attach using a valid existing game/player token;
14. try an invalid token and confirm only safe authorization feedback is shown;
15. confirm no bearer token appears in URLs, event text, status text, or saved settings.

Resize/settings acceptance must include, at minimum:

1. launch at the default window size;
2. open Settings from both the dedicated button and Menu;
3. apply at least 800×600, 1024×768, 1280×720, and Fit to screen;
4. test Windowed and Maximized; test fullscreen modes when supported by the QA machine;
5. test UI scale at 75%, 100%, 125%, and 175%;
6. resize substantially wider and taller;
7. resize below 900 px width and confirm map/sidebar switch to a vertical stack;
8. resize to the 640×480 minimum and confirm action grids/panels remain reachable through wrapping/scrolling;
9. open every populated dropdown and confirm its popup remains inside the visible viewport;
10. connect to the API and confirm dynamically-created hotseat player rows wrap instead of overlap;
11. make the window short enough to require lobby/sidebar/settings scrolling;
12. confirm the hex map remains centered, visible, and clickable after each resize;
13. restart the client and confirm saved display/UI-scale preferences are restored;
14. return to a large window and confirm the layout expands again without stale clipping.

## Files

```text
clients/godot/
├── project.godot
├── scenes/
│   └── main.tscn
├── scripts/
│   ├── api_client.gd
│   ├── api_features.gd
│   ├── content_browser.gd
│   ├── event_stream.gd
│   ├── hex_map.gd
│   ├── main.gd
│   ├── responsive_layout.gd
│   ├── settings_screen.gd
│   └── ui_shell.gd
├── tests/
│   └── smoke_test.gd
├── AGENTS.md
├── API_COVERAGE.md
├── README.md
├── TODO.md
└── UI_DESIGN.md
```

## Security/privacy rules

- Bearer credentials are never printed into the event log UI.
- The HTTP client does not include credentials in URLs.
- WebSocket credentials are supplied only through the required subprotocol handshake, never the URL.
- The client renders only projections/events/options returned for the selected player credential.
- Production options are requested only for the selected viewer's own settlement; the server enforces ownership.
- Error UI should display safe server detail/feedback, not raw stack traces.
- Hidden unit or settlement IDs must never be guessed or surfaced by client code.
- Local settings persist display/interface preferences only, never credentials.
- Attach credentials remain memory-only and are removed by Disconnect / Clear Session.

## Future client work

See `TODO.md`. With G2 implemented, the next logical phase is **G3 rich map interaction**: camera controls, tile inspection, fog distinction, overlays, and server-authorized movement/target/path presentation. G4 inspectors, diplomacy/event polish, accessibility, presentation polish, and systematic local Godot QA remain later client work.
