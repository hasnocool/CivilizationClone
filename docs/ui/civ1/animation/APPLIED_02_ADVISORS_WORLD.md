# Applied Visual References — Civilopedia, Advisors, World Reports

Range: `CIV1-UI-019..034`
Source: `ascii/02_advisors_world.ascii`, `ansii/02_advisors_world.ansii`

## Scene bindings
019 Browser = INDEX.REVEAL + CURSOR.MOVE + PAGE.FLIP
020 Entry = PAGE.REVEAL + TEXT.TYPEWRITER + PAGE.FLIP
021 Advisors Hub = PANEL.SWEEP + CURSOR.PULSE
022 City Status = TABLE.REVEAL + ROW.HIGHLIGHT
023 Military Advisor = TABLE.REVEAL + UNIT.COUNT_ROLL
024 Intelligence = DATA.REDACTED_REVEAL + RIVAL.HIGHLIGHT
025 Attitude = MOOD.INDICATOR + TABLE.REVEAL
026 Trade = DATA.STREAM + NUMBER.ROLL
027 Rates = SLIDER.SNAP + VALUE.ROLL
028 Science Advisor = RESEARCH.PROGRESS + TABLE.REVEAL
029 World Menu = MENU.REVEAL + CURSOR.PULSE
030 Wonders = WONDER.ICON_REVEAL + STATUS.PULSE
031 Top Five Cities = RANKING.SORT + ROW.REVEAL
032 Score = SCORE.COUNTUP + BAR.GROW
033 Known World Map = MAP.TILE_REVEAL + MARKER.PULSE
034 Demographics = BAR.GROW + RANKING.REVEAL

## ASCII storyboards

TABLE.REVEAL:
```text
CITY STATUS
-----------
Rome
```
```text
CITY STATUS
-----------
Rome      80
Antium    24
```
```text
CITY STATUS
-----------
Rome      80   23
Antium    24   11
Neapolis  16    7
```

RANKING.SORT:
```text
1. ?????
2. ?????
3. ?????
```
```text
1. Rome
2. Antium
3. Neapolis
```

SCORE.COUNTUP:
```text
SCORE: 00000
```
```text
SCORE: 00125
```
```text
SCORE: 00842
```
Final numeric result holds; animation must not imply a different authoritative score.

PAGE.FLIP can be represented in plain ASCII by erasing and redrawing the body while retaining the title and page indicator.

## ANSI treatment

Use semantic roles rather than fixed colors. `<TITLE>` remains stable while `<FOCUS>` moves between rows. Tables should reveal row-by-row only when doing so does not obscure the values. Graphs use `BAR.GROW`; text labels remain visible at all times.

For intelligence views, do not animate hidden information into existence. Only animate data that the engine has already made visible.

Reduced-motion endpoint: complete table/report rendered immediately.
