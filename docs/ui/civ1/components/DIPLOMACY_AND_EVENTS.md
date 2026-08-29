# Diplomacy and Event Components

## CIV1-COMP-LEADERPORTRAIT

Terminal portrait blocks provide character identity without requiring raster art.

A portrait should have:

- stable dimensions;
- name/title label;
- optional diplomatic mood indicator;
- static fallback;
- enough surrounding whitespace to remain recognizable at narrow widths.

Example:

```text
+--------------------+
|      .----.        |
|     / o  o \       |
|    |   --   |      |
|     \ ____ /       |
|      `----'        |
|       CAESAR       |
+--------------------+
```

Portrait animation should be subtle: entrance, expression/mood emphasis, or dialogue attention. Do not create rapid blinking faces.

## CIV1-COMP-DIALOGUE

Structured leader/player conversation region.

Recommended layers:

```text
leader identity
leader portrait
speaker marker
current statement
response choices
relationship/treaty context
```

Example:

```text
CAESAR
-------
"We propose peace."

> ACCEPT
  REJECT
  COUNTER
```

Text reveal may use `EFFECT.TEXT.TYPEWRITER`, but the completed statement must be available in the final frame.

## CIV1-COMP-TRADEOFFER

Displays proposed transactions using explicit give/receive columns.

```text
ROME OFFERS        YOUR CIVILIZATION OFFERS
Writing            50 gold
```

Every side should be visually unambiguous. A confirmation action must remain explicit.

## CIV1-COMP-TREATYBADGE

Compact status marker for peace, war, alliance, ceasefire, trade agreement, or broken treaty.

Example:

```text
[PEACE]
[WAR]
[ALLIANCE]
[CEASEFIRE]
```

Transitions may use a short visual emphasis, but the final badge and label remain static.

## CIV1-COMP-EVENTCARD

Reusable modal/card for notices, disasters, city events, combat results, and economy failures.

Structure:

```text
SEVERITY
TITLE
DESCRIPTION
CONSEQUENCE/SUMMARY
ACTIONS
```

## CIV1-COMP-SEVERITY

Severity must be encoded through at least two independent channels.

```text
<INFO>       informational marker
<NOTICE>     important notice
<WARN>       warning marker
<CRITICAL>   critical marker
```

A color change, where available, is secondary to marker text/glyphs.

## Diplomacy animation hooks

```text
EFFECT.DIPLOMACY.ARRIVAL
EFFECT.DIPLOMACY.MOOD
EFFECT.DIPLOMACY.PROPOSAL
EFFECT.DIPLOMACY.ACCEPT
EFFECT.DIPLOMACY.REJECT
```

## Event animation hooks

```text
EFFECT.EVENT.NOTICE
EFFECT.EVENT.WARNING
EFFECT.EVENT.CRITICAL
EFFECT.EVENT.DISASTER
```

Critical information should use `HOLD` behavior until acknowledged or otherwise resolved by the scene contract.
