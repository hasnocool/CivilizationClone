# Applied Visual References — Space Status, Replay, Failures, Help

Range: `CIV1-UI-143..168`
Source: `ascii/09_space_replay_misc.ascii`, `ansii/09_space_replay_misc.ansii`

## Scene bindings
143 Rival Spaceship Status = SHIP.STATUS_SCAN + PANEL.REVEAL
144 Spaceship Launch Confirmation = COUNTDOWN.REVEAL + CONFIRM.PULSE
145 Spaceship In Flight = STARFIELD.DRIFT + SHIP.PULSE
146 Rival Spaceship Launch = LAUNCH.SUMMARY + ALERT.PULSE
147 Rival Alpha Centauri Arrival = VICTORY.REVEAL + RIVAL.HIGHLIGHT
148 Automatic History End = TURN.ROLL + ENDGAME.REVEAL
149 Continue After Victory = DECISION.PULSE + VICTORY.FRAME
150 Replay Options = MENU.REVEAL + CURSOR.PULSE
151 Quick Replay = REPLAY.SCRUB + MAP.PLAYBACK
152 Complete Replay = REPLAY.EVENT_STEP + MAP.PLAYBACK + TEXT.LOG_REVEAL
153 Write Replay to Disk = SAVE.PROGRESS + CHECKMARK.PULSE
154 Powergraph = GRAPH.DRAW + CURSOR.PULSE
155 Destruction Replay Offer = DEFEAT.REVEAL + DECISION.PULSE
156 Palace Improvement Invitation = PALACE.DRAW + CHOICE.PULSE
157 Rival Wonder Completed = WONDER.REVEAL + ALERT.PULSE
158 Wonder Obsolete = STATUS.FLASH + TEXT.REVEAL
159 Treasury Shortfall = GOLD.DRAIN + WARNING.FRAME
160 Unsupported Unit Lost = UNIT.FADE + ALERT.PULSE
161 City Destroyed = CITY.FADE + MAP.FLASH
162 Capture Loot Technology = TECH.REVEAL + RESULT.PULSE
163 Capture Loot Gold = GOLD.COUNT_ROLL + RESULT.PULSE
164 Nuclear Attack Result = CRITICAL.FRAME + MAP.FLASH + RESULT.REVEAL
165 SDI Interception = SHIELD.FLASH + RESULT.REVEAL
166 Research Help Overlay = HELP.REVEAL + CURSOR.PULSE
167 Production Help Overlay = HELP.REVEAL + CURSOR.PULSE
168 City Advisor Recommendation = ADVICE.TYPEWRITER + TARGET.PULSE + CONFIRM.PULSE

## Concrete ASCII storyboards

COUNTDOWN.REVEAL:
```text
LAUNCH IN 3
```
```text
LAUNCH IN 2
```
```text
LAUNCH IN 1
```
```text
LAUNCH!
```

STARFIELD.DRIFT:
```text
.     *      .
   .      *
*       .
```
```text
  .       *
*     .       .
    *
```
The starfield moves while the ship remains the same authoritative object.

REPLAY.EVENT_STEP:
```text
TURN 0142
[MAP]
EVENT: FOUNDED ROME
```
```text
TURN 0143
[MAP]
EVENT: ROAD BUILT
```
Controls remain visible at all times.

GRAPH.DRAW:
```text
A |       *
B |    *
C |  *
  +----------
```
then progressively extend the historical lines until the complete graph is rendered.

FAILURE.STORY:
```text
WARNING: TREASURY SHORTFALL
```
```text
WARNING: TREASURY SHORTFALL
Barracks sold to maintain the treasury.
```

## ANSI treatment

Space scenes may use `✦`/`*` star particles only where the terminal tier supports them; ASCII `*` is always valid. Replay playback should update map and event log together but must never mutate live game state. Powergraph lines should use semantic series roles and remain readable in monochrome.

Critical combat/economy failures use explicit text plus markers. Help overlays use a clearly delineated border and do not erase the underlying scene from the logical navigation stack.
