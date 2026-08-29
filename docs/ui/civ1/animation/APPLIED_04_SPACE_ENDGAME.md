# Applied Visual References — Space, Endgame, Persistence

Range: `CIV1-UI-047..057`
Source: `ascii/04_space_endgame.ascii`, `ansii/04_space_endgame.ansii`

## Scene bindings
047 Wonder Completed = WONDER.REVEAL + FANFARE.PULSE + TEXT.CENTER_REVEAL
048 Wonder Illustration = ART.DRAW + BORDER.PULSE
049 Spaceship Overview = SHIP.BUILD + MODULE.LIGHT + STATUS.PULSE
050 Spaceship Launch = SHIP.LAUNCH + EXHAUST.STREAM + SCENE.WIPE
051 Alpha Centauri Victory = VICTORY.REVEAL + SCORE.COUNTUP + FIREWORKS.SYMBOLIC
052 Conquest Victory = VICTORY.REVEAL + SCORE.COUNTUP + BATTLE.RESULT_RECAP
053 Defeat = DEFEAT.REVEAL + SCORE.COUNTUP + FADE_SYMBOLIC
054 Final Rating = SCORE.COUNTUP + RANKING.REVEAL
055 Hall of Fame = TABLE.REVEAL + RANKING.HIGHLIGHT
056 Save Game = TEXT.TYPEWRITER + SAVE.PROGRESS + CONFIRM.PULSE
057 Load Game = LIST.REVEAL + LOAD.PROGRESS + CHECKMARK.PULSE

## ASCII storyboards

SHIP.BUILD:
```text
     [====]
       ||
      /__\\
```
then:
```text
     /====\\
    |  XX  |
     \\____/
       ||
```

SHIP.LAUNCH:
```text
       /\\
      /==\\
       ||
```
```text
       /\\
      /==\\
       ||
      /||\\
```
```text
         /\\
        /==\\
         ||
        /||\\
       / || \\
```
Final frame holds before the next scene.

VICTORY.REVEAL:
```text
================================
           VICTORY!
================================
```
Then score counts upward using fixed-width digits.

DEFEAT.REVEAL:
```text
--------------------------------
        CIVILIZATION FALLS
--------------------------------
```
Use subdued fade/erase, never rapid flashing.

SAVE.PROGRESS:
```text
SAVING [----------]
SAVING [=====-----]
SAVING [==========]
```

## ANSI treatment

Spaceship scenes may use a richer starfield and block progress bars. Launch should be a short non-looping sequence and must always end on the `CIV1-UI-050` presentation state. Victory uses `VICTORY` semantic styling; defeat uses `DEFEAT`; neither relies on color alone.

Reduced-motion endpoint: fully assembled ship, final score, or completed save/load result immediately.
