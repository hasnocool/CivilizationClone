# Applied Visual References — Palace, Diplomacy, Government, Events

Range: `CIV1-UI-035..046`
Source: `ascii/03_diplomacy_events.ascii`, `ansii/03_diplomacy_events.ansii`

## Scene bindings
035 Palace = PALACE.DRAW + BRICK.BUILD + CHOICE.PULSE
036 First Contact = DIPLOMACY.ARRIVAL + PORTRAIT.REVEAL + DIALOG.TYPEWRITER
037 Diplomacy = PORTRAIT.PULSE + DIALOG.TYPEWRITER + MENU.REVEAL
038 Technology Exchange = ITEM.TRANSFER + CONFIRM.PULSE
039 Tribute/Demand = WARNING.FRAME + VALUE.ROLL + DECISION.PULSE
040 Diplomat Mission = INFILTRATION.CURSOR + MENU.REVEAL + RESULT.FLASH
041 Revolution = TRANSITION.SCAN + TEXT.REVEAL + GOVERNMENT.FLIP
042 Government Selection = OPTION.SELECT + PANEL.REVEAL + CONFIRM.PULSE
043 New Cabinet = PORTRAIT.REVEAL + PANEL.SWEEP
044 Barbarian Warning = ALERT.PULSE + MAP.CENTER + TEXT.REVEAL
045 Civil Disorder = ALERT.PULSE + CITY.MARKER_PULSE
046 City Captured = MAP.FLASH + CITY.REPLACE + TEXT.REVEAL

## ASCII storyboards

PALACE.DRAW:
```text
      /\\
     /  \\
    /____\\
    | [] |
    |____|
```
Then add one wing at a time. Choice cursor remains separate from artwork.

DIPLOMACY.ARRIVAL:
```text
+----------------------+
| FOREIGN ENVOY ARRIVES|
|                      |
|       [LEADER]       |
+----------------------+
```
Then type the opening line until the full dialogue is available.

ALERT.PULSE:
```text
! BARBARIANS APPROACH !
```
Alternate border punctuation only; do not require flashing characters to convey meaning.

CITY.REPLACE:
```text
[OLD CITY]
    X
[NEW OWNER]
```
Then settle to the authoritative captured-city marker.

## ANSI treatment

Diplomacy portraits may reveal in three symbolic stages (outline, face, name). Dialogue uses `TEXT.TYPEWRITER`, but the entire line becomes immediately available through the normal skip action.

Warnings may use `<WARN>` or `<CRITICAL>` plus `!` markers. Government change uses a two-step visual: old government label -> transition divider -> new government label.

Accessibility: warnings, war declarations, and city capture must include text and symbol cues independently of color or blink.
