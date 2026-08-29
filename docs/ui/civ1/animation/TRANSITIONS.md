# Scene Transition Library

Scene transitions provide a common visual language between the 168 canonical states.

## Transition IDs

```text
TRANSITION.CUT
TRANSITION.FADE_SYMBOLIC
TRANSITION.WIPE_LEFT
TRANSITION.WIPE_RIGHT
TRANSITION.WIPE_UP
TRANSITION.WIPE_DOWN
TRANSITION.SCAN
TRANSITION.CURTAIN
TRANSITION.REVEAL_CENTER
TRANSITION.COLLAPSE
```

## CUT

Immediate replacement. Use for routine navigation where animation would add noise.

ASCII fallback:

```text
OLD SCENE

--- redraw ---

NEW SCENE
```

## FADE_SYMBOLIC

Use progressive density changes rather than relying on actual terminal alpha blending.

```text
FRAME 1  ##########
FRAME 2  ++++++++++
FRAME 3  ..........
FRAME 4
NEW SCENE
```

## WIPE

Reveal the destination scene from one edge. Reserve the full destination dimensions before starting so content does not jump.

## SCAN

Reveal rows sequentially. This is well suited to classic terminal aesthetics and boot/setup screens.

## CURTAIN

Two edge regions close around the old scene and reopen around the new scene. Use sparingly for major presentation boundaries.

## REVEAL_CENTER

Start with a small centered title or panel and expand to the complete scene. Best for technology, wonder, palace, victory, and major diplomatic results.

## COLLAPSE

Compress a modal visually before returning to the caller. The caller's state remains unchanged until the modal has been dismissed.

## Transition rules

- Never use a transition to imply success before engine confirmation.
- The transition must be cancel-safe unless explicitly marked `LOCKED`.
- Reduced-motion mode converts all transitions to `CUT` or a single static reveal frame.
- Screenshots and tests should be able to render the destination scene directly without replaying the transition.
