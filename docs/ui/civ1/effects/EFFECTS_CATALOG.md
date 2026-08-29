# Civ1-Inspired Terminal Visual Effects Catalog

This catalog defines the reusable visual-effect vocabulary for the CivilizationClone Civilization-I-inspired terminal presentation system.

The goal is not to prescribe one terminal implementation. Effects describe intent, visual behavior, timing, interruption policy, accessibility behavior, and capability requirements so TUI, Bevy, Godot, Unity, Unreal, and web clients can reproduce the same presentation language without sharing rendering code.

## Design principles

1. Effects are semantic. A scene requests an effect by name and meaning, not by embedding terminal escape sequences.
2. Effects are composable. A focused menu item can use `CURSOR.PULSE` inside `FRAME.FOCUS` while the scene itself remains unchanged.
3. Every effect has a non-animated fallback. Reduced-motion, monochrome, static screenshots, and plain-ASCII clients must remain understandable.
4. Animation never changes authoritative game state. Effects react to already-authoritative view-model state or presentation events.
5. Skip/interrupt rules are explicit. Important results may require acknowledgement, while decorative motion is always interruptible.
6. Accessibility is first-class. Color may reinforce meaning but never be the only signal.

## Effect ID format

Use `EFFECT.<FAMILY>.<NAME>`.

Examples:

```text
EFFECT.FRAME.REVEAL
EFFECT.CURSOR.PULSE
EFFECT.MAP.MOVE_UNIT
EFFECT.COMBAT.IMPACT
EFFECT.RESEARCH.DISCOVERY
EFFECT.TEXT.TYPEWRITER
EFFECT.SPACE.LAUNCH
```

## Effect metadata contract

Every documented effect should define:

```text
id
family
purpose
trigger
visual_layers
frames_or_state_steps
default_duration
loop_mode
interruptible
skippable
minimum_terminal_tier
ascii_fallback
reduced_motion_behavior
accessibility_note
sound_cue_hint
```

## Core effect families

### Frame effects

`EFFECT.FRAME.STATIC` — canonical border with no motion.

`EFFECT.FRAME.REVEAL` — draws a panel progressively from corners or edges.

`EFFECT.FRAME.PULSE` — briefly changes border emphasis to show attention without moving the content.

`EFFECT.FRAME.FOCUS` — adds a persistent visual distinction around the active panel.

`EFFECT.FRAME.WARNING` — briefly emphasizes a warning frame before settling.

`EFFECT.FRAME.CLOSE` — visually collapses or erases a modal before returning to its caller.

### Cursor and focus effects

`EFFECT.CURSOR.STATIC` — baseline `>`/`▶`/`@` marker.

`EFFECT.CURSOR.BLINK` — alternates visible and dim/blank states.

`EFFECT.CURSOR.PULSE` — alternates between primary and secondary focus glyphs.

`EFFECT.CURSOR.MOVE` — shows a map cursor travelling between coordinates.

`EFFECT.CURSOR.TARGET` — displays a target bracket or crosshair around a selected map square.

`EFFECT.CURSOR.INVALID` — rejects an illegal or unavailable selection using shape + text feedback.

### Map effects

`EFFECT.MAP.TILE_REVEAL` — uncovers previously hidden terrain.

`EFFECT.MAP.MOVE_UNIT` — animates a unit between adjacent map cells.

`EFFECT.MAP.PATH_PREVIEW` — draws a prospective movement path with directional markers.

`EFFECT.MAP.BUILD_PROGRESS` — animates infrastructure appearing on a tile.

`EFFECT.MAP.WATER_SHIMMER` — subtle looping water variation.

`EFFECT.MAP.TERRAIN_ACTIVITY` — optional subtle environmental movement.

`EFFECT.MAP.CITY_FOUND` — highlights the selected site, reveals the city label, then returns to normal map emphasis.

### Combat effects

`EFFECT.COMBAT.ATTACK` — directional attack cue.

`EFFECT.COMBAT.IMPACT` — brief symbolic impact frame.

`EFFECT.COMBAT.RESULT` — outcome reveal that persists long enough to read.

`EFFECT.COMBAT.VICTORY` — compact positive result animation.

`EFFECT.COMBAT.DEFEAT` — restrained negative result animation.

### City effects

`EFFECT.CITY.GROWTH` — population/resource growth cue.

`EFFECT.CITY.PRODUCTION_PROGRESS` — production bar advance.

`EFFECT.CITY.PRODUCTION_READY` — completion pulse and persistent ready marker.

`EFFECT.CITY.CITIZEN_ASSIGN` — focus movement between worked tiles and citizen slots.

`EFFECT.CITY.IMPROVEMENT_BUILD` — construction progress reveal.

### Research effects

`EFFECT.RESEARCH.PROGRESS` — animated science progress indicator.

`EFFECT.RESEARCH.DISCOVERY` — multi-stage technology discovery presentation.

`EFFECT.RESEARCH.CHAIN_REVEAL` — reveals enabled units, buildings, or follow-on technologies.

### Diplomacy effects

`EFFECT.DIPLOMACY.ARRIVAL` — leader panel enters the scene.

`EFFECT.DIPLOMACY.MOOD` — emphasis change when leader attitude changes.

`EFFECT.DIPLOMACY.PROPOSAL` — transaction panel reveal.

`EFFECT.DIPLOMACY.ACCEPT` — positive confirmation.

`EFFECT.DIPLOMACY.REJECT` — negative response.

### Event effects

`EFFECT.EVENT.NOTICE` — routine event reveal.

`EFFECT.EVENT.WARNING` — warning emphasis.

`EFFECT.EVENT.CRITICAL` — high-priority event emphasis.

`EFFECT.EVENT.DISASTER` — event-specific symbolic transition while remaining readable.

### Persistence effects

`EFFECT.SAVE.PROGRESS` — save operation progress.

`EFFECT.LOAD.PROGRESS` — load operation progress.

`EFFECT.IO.ERROR` — static, readable failure state; never depend on flashing alone.

### Presentation effects

`EFFECT.PALACE.REVEAL` — palace scene reveal.

`EFFECT.WONDER.REVEAL` — wonder completion reveal.

`EFFECT.SPACESHIP.BUILD` — component assembly animation.

`EFFECT.SPACE.LAUNCH` — staged launch presentation.

`EFFECT.SPACE.FLIGHT` — optional low-motion starfield and vessel movement.

### Results effects

`EFFECT.RESULTS.RATING_REVEAL` — score/rating fields appear in sequence.

`EFFECT.RESULTS.HOF_ENTRY` — Hall of Fame entry highlight.

`EFFECT.RESULTS.POWERGRAPH_DRAW` — progressive chart draw.

`EFFECT.RESULTS.REPLAY_START` — replay timeline initialization.

## Effect severity levels

```text
DECORATIVE  May be disabled at any time.
FEEDBACK    Communicates a user action or focus change.
NOTICE      Communicates an important but non-blocking event.
CRITICAL    Communicates information that should remain visible until read.
RESULT      Communicates an authoritative outcome and must persist in final form.
```

## Reduced-motion policy

When reduced motion is enabled:

- replace movement with immediate state changes;
- replace blinking with persistent markers;
- replace frame reveals with static final frames;
- replace animated progress with a numeric/static progress representation;
- retain all textual outcome information;
- never encode a gameplay result solely through animation.

## Plain ASCII policy

Plain ASCII fallbacks should use:

```text
> focus
[OK]
[WARN]
[!!]
==== progress
--> movement
-X- impact
*** reveal
```

The exact glyph is less important than maintaining semantic distinction and readability.

## Effect composition example

```text
[CIV1-UI-018] TECHNOLOGY DISCOVERED

Frame:
  EFFECT.FRAME.REVEAL

Title:
  EFFECT.TEXT.CENTER_REVEAL

Technology:
  EFFECT.RESEARCH.DISCOVERY

Follow-on data:
  EFFECT.RESEARCH.CHAIN_REVEAL

Dismissal:
  EFFECT.FRAME.CLOSE
```

This decomposition keeps animation reusable and allows clients to substitute their own rendering techniques while preserving the documented interaction.
