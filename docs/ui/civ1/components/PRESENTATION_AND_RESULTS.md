# Presentation and Results Components

## CIV1-COMP-PALACEVIEW

A framed ASCII/ANSI art region used for palace views and major civic presentations.

It should support:

- static architectural art;
- centered title;
- optional construction/completion message;
- subtle reveal animation;
- explicit return action.

Recommended effect: `EFFECT.PALACE.REVEAL`.

## CIV1-COMP-WONDERVIEW

Celebratory presentation for wonder completion.

Composition:

```text
WONDER COMPLETE!

[ASCII WONDER ART]

THE PYRAMIDS
Completed in Memphis
```

Recommended effect: `EFFECT.WONDER.REVEAL` followed by a persistent completion frame.

## CIV1-COMP-SPACESHIP

Terminal schematic for spaceship construction, status, and launch.

Suggested layers:

```text
ship silhouette
structural sections
crew/cargo status
flight metrics
destination/status
```

Construction can reveal components one at a time. Launch can use a staged storyboard rather than continuous pixel motion.

## CIV1-COMP-REPLAYTIMELINE

Provides current historical point, controls, and progress.

Example:

```text
4000 BC ────────●──────── 1720 BC
                ^
             CURRENT
```

Controls:

```text
[PLAY] [PAUSE] [STEP] [<<] [>>] [EXIT]
```

## CIV1-COMP-POWERGRAPH

Character-rendered comparative graph.

Example:

```text
POWER
|
|        A------A
|      A
|   B--
+---------------- TIME
```

The graph must have a textual summary and remain legible when animation is disabled.

## CIV1-COMP-RATINGBLOCK

End-game summary with rating, civilization identity, score components, and result.

A staged reveal can show:

1. civilization/result;
2. score;
3. rank/rating;
4. historical summary;
5. available next actions.

Recommended effect: `EFFECT.RESULTS.RATING_REVEAL`.
