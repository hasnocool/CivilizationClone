# Strategic Map Animation Specification

The map is the most animation-rich persistent scene, but motion must remain sparse enough that terrain, units, cities, and commands stay readable.

## Unit movement

Use discrete adjacent-cell frames.

```text
FRAME 01  [A]........
FRAME 02  ..[A]......
FRAME 03  ....[A]....
FINAL     ......[A]..
```

The final location is taken from authoritative state. If the command fails, render the unchanged origin plus feedback.

## Cursor movement

Cursor movement may interpolate across map cells, but each rendered cell should be deterministic.

```text
.. [@] ..
.....
```

For directional movement, optionally display a temporary route indicator.

## Path preview

```text
[A] - - - - [X]
```

The preview must be distinguishable from confirmed movement. It disappears on cancel, command rejection, or successful command completion.

## Tile reveal

Use an information-preserving reveal:

```text
?????
??.??
```

then:

```text
~~.^^
~..^^
```

Do not expose unrevealed terrain in an intermediate decorative frame.

## Infrastructure build

```text
.....
===..
=====.
======
```

A build effect may show work progressing, but the completed route/improvement is shown only after the authoritative event confirms it.

## Water shimmer

Subtle two-to-four-frame variation is acceptable:

```text
~ ~ ~ ~
 ~ ~ ~
≈ ~ ≈ ~
 ~ ≈ ~
```

This effect should be disabled in `REDUCED_MOTION` and `STATIC_CAPTURE` modes.

## City founding

Suggested sequence:

```text
FRAME 01  target tile selected
FRAME 02  settlement marker appears
FRAME 03  city name appears
FRAME 04  population/status panel becomes available
FRAME 05  static city marker
```

## Map alerts

For danger or critical events, prefer localized emphasis around the affected tile rather than flashing the entire screen.

Example:

```text
.. [CITY] ..
.. !! !! ..
```

Then settle to:

```text
.. [CITY] ..
.. [WARN] ..
```

## Performance guidance

Map animation should redraw only changed regions where the client permits efficient partial rendering. A complete-screen redraw is acceptable for simple terminals, but animation must not create blocking I/O or excessive output.
