# Applied Visual References — Units, Diplomats, Caravans, Minor Tribes

Range: `CIV1-UI-086..104`
Source: `ascii/06_units_special.ascii`, `ansii/06_units_special.ansii`

## Scene bindings
086 Stack Activation = STACK.REVEAL + CURSOR.MOVE + UNIT.PULSE
087 Go To Targeting = TARGET.CURSOR + PATH.PREVIEW + DESTINATION.PULSE
088 Home City Reassignment = CITY.LIST_REVEAL + CURSOR.MOVE + LINK.PULSE
089 Settler Context Orders = MENU.REVEAL + ORDER.HIGHLIGHT
090 Change Terrain = TILE.PREVIEW + PROGRESS.REVEAL + CONFIRM.PULSE
091 Bribe Offer = MONEY.ROLL + TARGET.PULSE + CONFIRM.PULSE
092 Bribe Result = RESULT.REVEAL + TARGET.UPDATE
093 Incite Revolt Price = MONEY.ROLL + WARNING.FRAME
094 Incite Revolt Result = CITY.FLASH + RESULT.REVEAL
095 Embassy Result = DIPLOMACY.SEAL + RESULT.REVEAL
096 Steal Technology = TECH.REVEAL + DATA.SLIDE
097 Industrial Sabotage = ALERT.PULSE + RESULT.REVEAL
098 Enemy City Inspection = MAP.CENTER + CITY.PANEL_REVEAL
099 Caravan Delivery = ROUTE.DRAW + GOLD.COUNT_ROLL + RESULT.REVEAL
100 Caravan Wonder Contribution = WONDER.PROGRESS + DECISION.PULSE
101 Ancient Wisdom = TEXT.CENTER_REVEAL + TECH.DISCOVERY
102 Tribe Joins = CITY.FOUND + MARKER.PULSE
103 Tribe Barbarians = ALERT.PULSE + MAP.CENTER
104 Barbarian Ransom = MONEY.ROLL + ALERT.PULSE

## ASCII storyboards

STACK.REVEAL:
```text
[LEG]
[SET]
[CHA]
```
then:
```text
>[LEG]
 [SET]
 [CHA]
```
Focus moves without changing stack membership.

PATH.PREVIEW:
```text
[A] - - - - [X]
```
then:
```text
[A] - - . - [X]
```
Dashed route is provisional; authoritative movement replaces it only after command confirmation.

DIPLOMAT.RESULT:
```text
MISSION COMPLETE
-----------------
EMBASSY ESTABLISHED
```
Reveal heading first, result second, details last.

CARAVAN.ROUTE:
```text
[A]====o====[B]
```
Build the route line from origin toward destination; delivery result then counts the reward.

MINOR TRIBE:
```text
???
```
```text
ANCIENT WISDOM
```
```text
ANCIENT WISDOM
Technology gained: ___
```
Only render the actual engine-provided result.

## ANSI treatment

Unit focus uses `▶`/`▷`. Targeting uses a pulsing bracket around the selected destination, not color alone. Diplomat and caravan results can use a short border reveal. Money transfers use fixed-width number rolling so columns do not jump.

No animation may reveal unavailable enemy-city or intelligence data. Reduced motion shows the complete result immediately.
