# Space, Victory, Replay, and Results Effect Recipes

## EFFECT.SPACESHIP.BUILD

Reveal ship sections progressively.

```text
01       /---\
         \___/

02      /=====\
      /  XXX  \
      \_______/

03      /=====\
     /   XXX   \
    |    XXX    |
     \_________/
```

Each component should correspond to authoritative construction state. The animation is not permitted to invent completed sections.

## EFFECT.SPACE.LAUNCH

Use a staged symbolic launch.

```text
01       /===\
          ||
          ||

02       /===\
          ||
         /||\

03        /===\
          ||
         /||\
        / || \

04             *
           /===\
             ||
```

Final state includes textual destination/status so the meaning is never dependent on the drawing.

## EFFECT.SPACE.FLIGHT

Optional low-motion starfield. The ship itself may move by a few cells while stars shift slowly.

Do not use random star positions in canonical references; use deterministic frames.

## EFFECT.RESULTS.RATING_REVEAL

Recommended order:

```text
VICTORY
  ↓
CIVILIZATION
  ↓
SCORE
  ↓
RATING
  ↓
HISTORICAL SUMMARY
```

Each stage uses `SLOW`, followed by a final static result page.

## EFFECT.RESULTS.HOF_ENTRY

Highlight the inserted Hall of Fame row without scrolling unpredictably.

```text
> ROME      1280     1st
  EGYPT      910     2nd
```

## EFFECT.RESULTS.POWERGRAPH_DRAW

Draw graph lines in deterministic left-to-right segments.

```text
|
| A
| A---
|     A----
| B-
+-------------
```

The complete chart should be displayed when the effect ends.

## EFFECT.RESULTS.REPLAY_START

Show replay timeline and establish the initial event/turn marker before playback begins.

## Victory presentation

Use sparse celebratory effects:

```text
        *
     \  |  /
   --  VICTORY  --
     /  |  \
        *
```

The result title and outcome remain persistent.

## Defeat presentation

Use restrained presentation with clear text and no distracting motion.

```text
--------------------------------
CIVILIZATION FALLS
--------------------------------
[ RESULTS ] [ REPLAY ]
```
