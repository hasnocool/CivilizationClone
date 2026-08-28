# Godot Client Roadmap

This file is the execution queue for `clients/godot/`. Agents working on the Godot client should follow it in order unless a bug, security issue, API incompatibility, or explicit user request takes priority.

The non-negotiable architecture is **one authoritative deterministic server, many clients**. Godot is never a second rules engine.

## Phase G0 — Project foundation

- [x] Godot 4.7.x project skeleton.
- [x] Compatibility renderer for broad local hardware support.
- [x] Main scene that can instantiate headlessly.
- [x] Public JSON HTTP transport based on `HTTPRequest`.
- [x] Bearer credentials kept out of URLs.
- [x] Client-generated command IDs.
- [x] Headless smoke script.
- [x] Local verification launcher.
- [x] Godot-specific agent/QA instructions.

Exit: project imports and main scene instantiates under Godot 4.7.x.

## Phase G1 — First playable API client

- [x] API health connection flow.
- [x] Public civilization catalog loading.
- [x] New game parameters.
- [x] Full public map-generation parameters: radius, water %, resource %.
- [x] 2–4 player hotseat enrollment.
- [x] Civilization selection per player.
- [x] Public `human` / `bot` controller selection during enrollment.
- [x] Start game through public API.
- [x] In-memory player credential switching.
- [x] Fog-safe authorized map rendering.
- [x] Terrain/resource visualization.
- [x] Own/enemy unit visualization.
- [x] Settlement visualization.
- [x] Own-unit selection.
- [x] Click-to-move command submission.
- [x] Click-visible-enemy attack submission.
- [x] Found settlement action.
- [x] Research selection from server-exposed available/mandatory choices.
- [x] Settlement selection.
- [x] Worked-tile on/off actions.
- [x] Production queue/cancel command submission.
- [x] Diplomacy declare/offer/accept/reject actions.
- [x] End turn and concede.
- [x] Authorized event history panel.
- [x] Safe server feedback rendering.
- [ ] Run complete local Godot import/smoke verification.
- [ ] Run human-style full-match playtest.

Exit: local QA can play a complete hotseat match using the actual Godot window and public API only.

## Phase G2 — Server-driven rules/content browser

Goal: remove remaining manual definition-ID entry without copying gameplay content into Godot.

Server/API:

- [ ] Add a stable read-only public POC rules catalog or player-authorized production-options query.
- [ ] Expose unit definitions needed for presentation: id, movement, vision, production cost, abstract combat stats, requirements, civilization ownership.
- [ ] Expose building definitions needed for presentation: id, production cost, visible yield effects, requirements, civilization ownership.
- [ ] Expose technology display data: id, cost, prerequisites, unlocks, effective player cost where appropriate.
- [ ] Keep hidden/authoritative-only rule data out of public responses.

Godot:

- [ ] Production dropdown populated exclusively from server responses.
- [ ] Disable/annotate locked production options based on server response.
- [ ] Technology browser/tree.
- [ ] Civilization detail cards with bonuses and unique content.
- [ ] Context-sensitive tooltips.

Exit: no gameplay definition IDs or rule constants are manually duplicated in the Godot UI.

## Phase G3 — Rich map interaction

- [ ] Camera pan and zoom.
- [ ] Fit-map button.
- [ ] Tile hover inspection.
- [ ] Selected-unit movement-range overlay from authoritative/legal query data.
- [ ] Legal target highlighting.
- [ ] Path preview sourced from server-authorized movement/path information.
- [ ] Distinct visible/discovered fog treatment.
- [ ] Resource icons or generated vector markers.
- [ ] Settlement borders/territory overlay.
- [ ] Worked-tile overlay.
- [ ] Better stacking/selection when unit and settlement share a tile.
- [ ] Map legend.

Exit: map interaction is understandable without reading raw IDs.

## Phase G4 — Unit and settlement inspectors

Unit panel:

- [ ] Definition/name.
- [ ] Owner/civilization.
- [ ] HP/action state.
- [ ] Movement.
- [ ] Abstract game combat values.
- [ ] Founding capability where public.
- [ ] Selected-unit actions derived from legal server state.

Settlement panel:

- [ ] Population.
- [ ] Current/last visible yields.
- [ ] Food/production storage.
- [ ] Buildings.
- [ ] Production queue with progress.
- [ ] Territory/worked tiles.
- [ ] Queue reordering if/when server supports it.

Exit: routine play no longer depends on raw event payload inspection.

## Phase G5 — Real-time authorized event stream

- [x] Godot `WebSocketPeer` client.
- [x] Use `civilization.v1` + player token subprotocol handshake as required by API contract.
- [x] Never put token in WebSocket query string.
- [x] Resume using non-secret `after_sequence`.
- [x] Auto-refresh projection after relevant events.
- [x] Reconnect/backoff state machine.
- [x] Viewer switch cleanly closes/re-authenticates stream.
- [ ] Event notifications/toasts.
- [ ] Test that unauthorized/bilateral/hidden events do not surface with an executable local API + Godot run.

Exit: client updates without manual refresh while preserving server-side authorization.

## Phase G6 — Attach/reconnect/session UX

- [x] Attach to existing game with manually supplied game/player credential.
- [ ] Optional OS-keystore-backed credential persistence if implemented safely; never plain-text token files by default.
- [ ] Recent non-secret server/game IDs.
- [x] Clear credentials/logout.
- [x] Graceful invalid-token handling in attach and live-stream status.
- [ ] Server restart guidance when ephemeral auth secret invalidates credentials.
- [ ] Connection loss overlay and HTTP retry UX.

Exit: persistent local server sessions are usable without recreating games.

## Phase G7 — Full diplomacy and event UX

- [ ] Relationship cards.
- [ ] Pending peace offer indicator.
- [ ] Accept/reject affordances only when relevant.
- [ ] War status visible on player list.
- [ ] Event feed categories and filters.
- [ ] Turn-start and mandatory-decision notifications.
- [ ] Victory screen.
- [ ] Defeat/concession state.

Exit: diplomacy and match-end state are obvious without reading raw events.

## Phase G8 — AI and match setup

- [x] Human/bot controller selection in lobby through the existing public enrollment API.
- [ ] Bot status indicators after game start.
- [ ] Spectator/read-only design decision.
- [ ] Fast-forward controls only through public server surfaces.
- [ ] Bot-vs-bot observer mode.
- [ ] Seed/config summary before start.

Exit: Godot can configure common human/AI POC scenarios without engine shortcuts.

## Phase G9 — Accessibility and input

- [ ] Complete keyboard navigation.
- [ ] Focus order review.
- [ ] Gamepad navigation.
- [x] UI scale setting.
- [ ] High-contrast mode.
- [ ] Color-blind-safe map distinction that does not rely only on hue.
- [ ] Screen-reader/accessibility metadata where Godot supports it.
- [ ] Remappable shortcuts.
- [ ] Reduced-motion option once animations exist.

Exit: core game loop is usable without precision pointer-only input.

## Phase G10 — Presentation polish

- [ ] Reusable theme resource.
- [x] Consistent spacing/typography and distinct button/input/label/description hierarchy.
- [ ] Original/generated icons with clear licensing/source notes.
- [ ] Turn transition animation.
- [ ] Selection/movement feedback animation.
- [ ] Optional sound effects/music controls using original or properly licensed assets only.
- [ ] Main menu/settings/about screens.
- [x] Responsive layouts for common desktop resolutions.
- [x] Window/fullscreen settings.

Exit: client feels like an intentional game UI rather than a debugging console.

## Phase G11 — Systematic QA automation

Static/headless:

- [x] Main-scene instantiation smoke test.
- [ ] Parse/import every `.gd` and `.tscn` resource.
- [ ] Pure UI helper tests where practical.
- [ ] Mock/public-API fixture tests without bypassing production request code.
- [ ] Failure-state tests: offline API, 401/403, 404 game, stale state, rejected commands, invalid JSON.

Human-style automation/local agent:

- [ ] Launch API and Godot window.
- [ ] Click Connect.
- [ ] Create two-player game.
- [ ] Choose different civilizations.
- [ ] Select Human/Bot controller combinations.
- [ ] Exercise water/resource map-generation controls.
- [ ] Start.
- [ ] Select/move a unit.
- [ ] Explore fog.
- [ ] Found a settlement.
- [ ] Choose research.
- [ ] Queue production.
- [ ] End several turns.
- [ ] Switch hotseat player using normal UI.
- [ ] Verify live WebSocket event updates and reconnect behavior.
- [ ] Exercise attach-existing-game with a valid player token.
- [ ] Verify invalid attach token is rejected safely.
- [ ] Exercise diplomacy.
- [ ] Exercise abstract combat when reachable.
- [ ] Inspect authorized event/feedback rendering.
- [ ] Finish/concede match.
- [ ] Clear session and confirm credentials are removed from the UI/process state.
- [ ] Confirm hidden information is absent.
- [ ] Capture screenshots/logs under ignored `artifacts/`/`logs/` paths.

Exit: local QA report satisfies root `AGENTS.md` contract.

## Phase G12 — Packaging

- [ ] Desktop export presets after local export templates are available.
- [ ] Linux build verification.
- [ ] Windows build verification.
- [ ] macOS build verification when a suitable local environment exists.
- [ ] Version display tied deliberately to client/API compatibility.
- [ ] Reproducible local export script.
- [ ] No GitHub Actions.

Exit: locally generated desktop client artifacts are reproducible and documented.

## Definition of done for every Godot change

- No simulation authority moved into Godot.
- No hidden state inferred or cached from unauthorized sources.
- No bearer token logged or placed in URLs.
- Client handles rejected commands without pretending mutation succeeded.
- Relevant headless Godot checks actually executed locally before claiming PASS.
- GUI-affecting work receives human-style mouse/keyboard playtesting.
- Root `bash scripts/ci.sh` remains green for server/core changes.
- PR includes exact local QA evidence and remains draft while QA is blocked/failing.
