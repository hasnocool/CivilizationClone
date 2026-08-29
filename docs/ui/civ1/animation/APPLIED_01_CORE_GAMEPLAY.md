# Applied Visual References — Core Gameplay

Range: `CIV1-UI-007..018`
Source: `ascii/01_core_gameplay.ascii`, `ansii/01_core_gameplay.ansii`

## Scene bindings
007 MAP = MAP.TILE_REVEAL + CURSOR.TARGET + MAP.MOVE_UNIT + MAP.WATER_SHIMMER
008 ORDERS = MENU.REVEAL + CURSOR.PULSE + ACTION.CONFIRM
009 TILE INFO = PANEL.REVEAL + DATA.STREAM
010 UNIT INFO = PANEL.REVEAL + UNIT.SILHOUETTE_REVEAL
011 FOUND CITY = CITY.FOUND + TEXT.TYPEWRITER + CONFIRM.PULSE
012 CITY = CITY.RESOURCE_TICK + PRODUCTION.PROGRESS + CURSOR.PULSE
013 PRODUCTION = MENU.REVEAL + CURSOR.MOVE + VALUE.HIGHLIGHT
014 BUY = MONEY.NUMBER_ROLL + CONFIRM.PULSE
015 SELL = WARNING.FRAME + CONFIRM.PULSE
016 CITY VIEW = BUILDING.REVEAL + PANEL.DRAW
017 RESEARCH = MENU.REVEAL + CURSOR.PULSE + RESEARCH.SELECT
018 DISCOVERY = TECH.DISCOVERY + TEXT.CENTER_REVEAL + REWARD.HIGHLIGHT

## Concrete ASCII storyboards

MAP.TILE_REVEAL:
```text
.....^^^^
... .^^^^
.. [A]...
```
then reveal adjacent known cells from the authoritative map event; never reveal hidden cells merely because an animation is running.

MAP.MOVE_UNIT:
```text
[A]......
..[A]....
....[A]..
```
Commit only after confirmed movement; otherwise show `-.-` path preview.

CITY.FOUND:
```text
   [SET]
      |
      v
 +----------+
 |  ANTIUM  |
 |    1     |
 +----------+
```

PRODUCTION.PROGRESS:
```text
SETTLERS [====--------]
SETTLERS [========----]
SETTLERS [============]
        READY
```

TECH.DISCOVERY:
```text
DISCOVERY!
```
```text
DISCOVERY!
MATHEMATICS
```
```text
DISCOVERY!
MATHEMATICS
Allows: Catapult
Leads to: Astronomy
```

## Concrete ANSI storyboard guidance

Use `<TITLE>`/`<FOCUS>`/`<INFO>` roles already established by the ANSI scene references. A focused item may pulse its marker, but the final frame must remain visually distinct without color.

Recommended rich effects:
- map water alternates `≈ ~ ≈ ~` without moving land/city state;
- active unit marker cycles `▶[A]`, `▷[A]`;
- city production bar uses block progress;
- discovery modal uses border draw + centered title reveal;
- buy/sell prompts briefly emphasize only the decision row, never the whole screen.

Reduced motion: show the final state immediately.
