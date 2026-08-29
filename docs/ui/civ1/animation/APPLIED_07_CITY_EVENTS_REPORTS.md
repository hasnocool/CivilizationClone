# Applied Visual References — City Subviews, Environment, Reports

Range: `CIV1-UI-105..130`
Source: `ascii/07_city_events_reports.ascii`, `ansii/07_city_events_reports.ansii`

## Scene bindings
105 City Information = TABLE.REVEAL + ROW.HIGHLIGHT
106 Happiness Chart = BAR.GROW + MOOD.INDICATOR
107 City Map = MAP.REVEAL + UNIT.PULSE + ROUTE.DRAW
108 Citizen Reassignment = CURSOR.MOVE + TILE.SELECT + CITIZEN.PULSE
109 Specialist Assignment = CURSOR.MOVE + SPECIALIST.REVEAL
110 Rename City = TEXT.TYPEWRITER + CARET.PULSE
111 City Unit Activation = UNIT.PULSE + MENU.REVEAL
112 Improvement Completed = BUILDING.REVEAL + RESULT.PULSE
113 Wonder Race Lost = WARNING.FRAME + PRODUCTION.RESET
114 Civil Disorder Continues = ALERT.PULSE + CITY.MARKER_PULSE
115 We Love the King Day = CELEBRATION.PULSE + CITY.MARKER_PULSE
116 Pollution = ALERT.PULSE + TILE.REVEAL
117 Global Warming = WORLD.WASH + ALERT.PULSE
118 Nuclear Meltdown = CRITICAL.FRAME + CITY.FLASH
119 Earthquake = MAP.SHAKE_SYMBOLIC + DAMAGE.REVEAL
120 Famine = FOOD.BAR_DRAIN + ALERT.PULSE
121 Fire = FLAME.STREAM + DAMAGE.REVEAL
122 Flood = WATER.SWEEP + DAMAGE.REVEAL
123 Piracy = ROUTE.INTERRUPT + ALERT.PULSE
124 Plague = CITY.MARKER_PULSE + WARNING.FRAME
125 Volcano = MOUNTAIN.FLASH + MAP.SHAKE_SYMBOLIC
126 Military Casualties = TABLE.REVEAL + NUMBER.ROLL + ROW.HIGHLIGHT
127 Intelligence Detail = DATA.SLIDE + REDACTED.REVEAL
128 Civilopedia Section = MENU.REVEAL + CURSOR.PULSE
129 History Page = PAGE.FLIP + TEXT.TYPEWRITER
130 Gameplay Page = PAGE.FLIP + DATA.REVEAL

## Concrete event storyboards

CITIZEN.SELECT:
```text
[F][F][S][T]
    ^
```
```text
[F][F][S][T]
       ^
```
Then show `REMOVE`/`ASSIGN` action feedback; do not alter data until engine confirmation.

HAPPINESS:
```text
HAPPY [###-------]
HAPPY [######----]
HAPPY [##########]
```

ENVIRONMENT EVENTS:
Pollution uses a one-cell marker appearing on the authoritative tile. Flood/fire/volcano may animate the event symbol over 2-4 frames, then settle on the final affected state.

ASCII-only symbolic examples:
```text
~~~~~  ->  ~~~~  ->  ~~~~~
  ^         ^         ^
```
```text
[FIRE] -> [F***] -> [FIRE]
```
Use restrained symbolic motion, not destructive screen-wide animation.

## ANSI treatment

City subviews can use block bars and box drawing. Environmental events use semantic `<WARN>`/`<CRITICAL>` roles plus textual names. The event frame must remain understandable in a static capture.
