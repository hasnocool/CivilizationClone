# Civ1-Inspired Terminal Animation Contract

This document defines how animated ASCII/ANSI references are represented so multiple clients can implement equivalent presentation without coupling animation to game rules.

## 1. Animation is presentation-only

Animations may respond to:

- scene entry;
- focus changes;
- cursor movement;
- authoritative command acknowledgements;
- authoritative domain events exposed by the client view model;
- modal open/close;
- replay progression.

Animations must never:

- determine combat results;
- advance the game turn;
- consume engine RNG;
- mutate authoritative state;
- hide an authoritative failure;
- assume a command succeeded before the engine confirms it.

## 2. Timeline model

An animation is a sequence of render states. A render state may change text, glyphs, border emphasis, cursor location, or visible data while leaving the scene's logical state unchanged.

```text
Animation
  ├── metadata
  ├── start state
  ├── frames/state steps
  ├── timing
  ├── input policy
  ├── accessibility policy
  └── final state
```

## 3. Timing vocabulary

```text
INSTANT      0 ms logical transition; render immediately.
TINY         40-80 ms; micro-feedback.
FAST         80-150 ms; cursor/focus feedback.
NORMAL       150-300 ms; common transitions.
SLOW         300-600 ms; modal or reveal emphasis.
DRAMATIC     600-1200 ms; discoveries, launches, major results.
HOLD         Persists until input or authoritative state change.
```

Timing values are defaults, not rigid requirements. Clients may clamp timing for terminal refresh rates and accessibility preferences.

## 4. Loop modes

```text
ONCE
LOOP
PING_PONG
HOLD
LOOP_UNTIL_EVENT
REVEAL_THEN_HOLD
```

Decorative loops should default to `LOOP_UNTIL_EVENT`. Important outcome animations should default to `REVEAL_THEN_HOLD`.

## 5. Interruptibility

Every animation declares one of:

```text
ALWAYS       Input may interrupt immediately; final state is applied.
SAFE_POINT   Input is accepted at frame boundaries.
END_ONLY     Input is queued until the animation reaches its final state.
LOCKED       No interaction except explicit emergency/back behavior.
```

The default for ordinary UI feedback is `ALWAYS`.

## 6. Skip behavior

Skip may be:

```text
YES          Jump to final rendered state.
NO           Animation cannot be skipped.
ACK          Player must acknowledge the result after the reveal.
```

For example, technology discovery can skip the reveal but must still stop on the final discovery frame so the player can read it.

## 7. Frame encoding

ASCII references should use visibly numbered storyboard frames when motion matters:

```text
FRAME 01
FRAME 02
FRAME 03
```

Each frame should be valid monospace content and should document the expected terminal width where alignment matters.

ANSI references may use semantic roles rather than literal escape codes:

```text
<TITLE>
<FOCUS>
<WARN>
<INFO>
```

Clients map these roles to their active palette/capability tier.

## 8. State interpolation

Do not require numeric interpolation for simple terminal rendering. Most effects should define discrete symbolic states.

Recommended approaches:

- cursor movement: discrete cell positions;
- progress: discrete bar steps;
- text reveal: character/word batches;
- map movement: adjacent-cell frames;
- chart drawing: added segments per frame;
- border effects: discrete border variants.

## 9. Capability negotiation

A client should expose presentation capabilities such as:

```text
ASCII_ONLY
ANSI_COLOR
UNICODE_BOX_DRAWING
CURSOR_CONTROL
BLINK_SUPPORTED
TRUECOLOR
REDUCED_MOTION
STATIC_CAPTURE
```

The renderer chooses the richest compatible representation.

## 10. Accessibility

Every animation must have a final static state that carries the full semantic meaning.

Examples:

- a flashing warning also contains `WARNING` text;
- a progress animation also exposes percentage/quantity where useful;
- a blinking focus marker also uses a persistent focus glyph;
- a combat impact animation ends with a textual result;
- a replay animation exposes current turn/year independent of motion.

## 11. Determinism

Given the same input state and animation configuration, the storyboard output must be deterministic. Decorative randomization is prohibited in canonical references because it complicates screenshots, testing, replay comparison, and cross-client consistency.

## 12. Reference storyboard

```text
EFFECT.MAP.MOVE_UNIT

trigger: confirmed_unit_move
start: [A] at x=10,y=5
end:   [A] at x=12,y=5
duration: FAST
loop: ONCE
interruptible: ALWAYS
skip: YES

01  [A]........
02  ..[A]......
03  ....[A]....

final:
....[A]........
```

## 13. Scene transition contract

Scene transitions should be attached to scene routing, not hidden inside scene content.

```text
caller scene
  -> transition.out
  -> new scene
  -> transition.in
```

A failed transition must leave the caller scene intact. A command acknowledgement is never inferred from a successful visual transition.

## 14. Testing

Animation tests should verify:

- frame ordering;
- expected number of frames/state steps;
- final state correctness;
- skip behavior;
- reduced-motion fallback;
- ASCII fallback;
- terminal-width constraints;
- no authoritative state mutation;
- stable deterministic output.
