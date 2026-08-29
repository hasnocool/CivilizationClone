# Civ1-Inspired Animation Timing Standards

Timing is standardized so the terminal visual language feels consistent across all scene families.

## Timing bands

| Name | Default | Intended use |
|---|---:|---|
| INSTANT | 0 ms | state changes, static redraws |
| MICRO | 60 ms | tiny focus/cursor changes |
| FAST | 120 ms | movement and lightweight feedback |
| NORMAL | 220 ms | menu/modal transitions |
| SLOW | 400 ms | information reveals |
| DRAMATIC | 800 ms | discoveries, wonders, launches |
| HOLD | indefinite | acknowledgement/results |

## Guidelines

Do not animate every redraw. A terminal UI should feel deliberate rather than busy.

Use MICRO for focus changes, FAST for map movement, NORMAL for modal transitions, SLOW for text and panel reveals, and DRAMATIC only for major presentations.

## Frame rate

A client should target a stable presentation cadence rather than maximizing terminal refresh rate. A practical default is 8-15 visual frames per second for terminal animation. A renderer may reduce this when output transport or terminal latency requires it.

## Input latency

Input must remain responsive during decorative animations. Cursor and menu navigation should normally use `ALWAYS` interruptibility. Longer presentation sequences should expose skip behavior unless the result requires acknowledgement.

## Reduced motion

Reduced-motion mode replaces animation with:

```text
animated transition -> final state
blink -> persistent marker
pulse -> stronger static border
movement -> endpoint
chart draw -> complete chart
text reveal -> complete text
```

## Terminal-width constraints

Animation must not cause a panel to change width between frames unless the effect explicitly documents that behavior. Avoid right-edge drift caused by changing text length; reserve the maximum width needed before revealing content.

## Timing examples

### Menu focus

```text
0 ms   > Move
60 ms  ▶ Move
120 ms > Move
```

### Map movement

```text
120 ms/frame
[A].....
.[A]....
..[A]...
```

### Technology discovery

```text
0 ms    frame shell
250 ms  title
500 ms  technology name
750 ms  enabled content
1000 ms final detail
800 ms hold
```

### Space launch

```text
0-400 ms   staging
400-800 ms ignition
800-1200 ms ascent
1200-1600 ms separation/flight
HOLD       status
```
