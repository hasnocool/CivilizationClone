# Applied Visual References — System, Menus, Turn Flow

Range: `CIV1-UI-058..085`
Source: `ascii/05_system_menus.ascii`, `ansii/05_system_menus.ansii`

## Scene bindings
058 Credits = TEXT.TYPEWRITER + CREDITS.SCROLL
059 Sound Driver = MENU.REVEAL + OPTION.SELECT
060 Game/World Options = PANEL.REVEAL + OPTION.SELECT
061 Load Drive = DRIVE.SCAN + CURSOR.PULSE
062 Land Mass = SLIDER.SNAP + MAP.PREVIEW_CHANGE
063 Temperature = SLIDER.SNAP + WEATHER.PREVIEW_CHANGE
064 Moisture = SLIDER.SNAP + TERRAIN.PREVIEW_CHANGE
065 Age/Start = SLIDER.SNAP + ERA.TEXT_REVEAL
066 Competition = COUNT.ROLL + CURSOR.PULSE
067 Tribe Name = TEXT.TYPEWRITER + CARET.PULSE
068 Ruler Name = TEXT.TYPEWRITER + CARET.PULSE
069 Copy Protection Quiz = PAGE.REVEAL + INPUT.CHECK
070 Copy Protection Failure = WARNING.FRAME + SHAKE_SYMBOLIC
071 Game Menu = MENU.REVEAL + CURSOR.PULSE
072 Game Options = PANEL.REVEAL + TOGGLE.SNAP
073 Tax Rate = SLIDER.SNAP + VALUE.ROLL
074 Luxury Rate = SLIDER.SNAP + VALUE.ROLL
075 Find City = SEARCH.TYPE + MAP.CENTER + MARKER.PULSE
076 Save Drive/Slot = DRIVE.SCAN + SLOT.HIGHLIGHT
077 Quit = WARNING.FRAME + CONFIRM.PULSE
078 Retire = WARNING.FRAME + CONFIRM.PULSE
079 End Turn = TURN.ROLL + MENU.REVEAL + CONFIRM.PULSE
080 Instant Advice = ADVICE.TYPEWRITER + INFO.PULSE
081 Historian Advancement = RANKING.REVEAL + SCORE.COUNTUP
082 Historian Happiness = RANKING.REVEAL + MOOD.INDICATOR
083 Historian Power = RANKING.REVEAL + UNIT.COUNT_ROLL
084 Historian Size = RANKING.REVEAL + NUMBER.ROLL
085 Historian Wealth = RANKING.REVEAL + GOLD.COUNT_ROLL

## Concrete ASCII recipes

SLIDER.SNAP:
```text
TAX  30% [######--------------]
TAX  40% [########------------]
TAX  50% [##########----------]
```

SEARCH.TYPE:
```text
FIND CITY: R
FIND CITY: RO
FIND CITY: ROM
FIND CITY: ROME
```

TURN.ROLL:
```text
YEAR 1720 BC
```
```text
YEAR 1719 BC
```
Final frame remains until the turn transition completes.

CREDITS.SCROLL:
Each credit line moves upward one row at a time; final credit row holds briefly before advancing.

## ANSI recipes

Use `<FOCUS>` on the changing option, `<INFO>` for confirmed values, `<WARN>` for failure/quit prompts. Copy-protection failure may use a brief border emphasis but never require blinking. Historian screens should reveal each row or bar in order, then settle.

All input/edit fields expose a visible caret in ANSI-capable clients and a fixed placeholder/caret in ASCII-only clients.
