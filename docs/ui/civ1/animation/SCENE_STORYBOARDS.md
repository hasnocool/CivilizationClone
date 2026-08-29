# Canonical Scene Animation Storyboards

This catalog provides representative motion recipes for the most visually important scene families. These are references for implementation and testing; clients may render equivalent effects using their own technology.

## CIV1-UI-007 — Strategic World Map

### Map entry

```text
01 +------------------------------+
02 | MAP                          |
03 |                              |
04 +------------------------------+
```

Use `TRANSITION.SCAN` or a direct static render depending on context.

### Unit selection

```text
01  [A]
02  >[A]<
03  ▶[A]◀
04  ▶[A]◀
```

Settle on one persistent focus marker.

### Unit movement

```text
[A].........
..[A].......
....[A].....
......[A]...
```

## CIV1-UI-011 — Found City

```text
01  [TARGET]
02  [*TARGET*]
03  [CITY]
04  [CITY: ANTIUM]
```

After the authoritative city-founded event, settle to the normal city marker.

## CIV1-UI-012 — City Management

### Production update

```text
01  SETTLERS [====------]
02  SETTLERS [======----]
03  SETTLERS [========--]
04  SETTLERS [==========]
05  SETTLERS READY
```

### Worker assignment

Focus moves cell by cell, then the confirmed assignment changes the worked/unworked representation.

## CIV1-UI-018 — Technology Discovered

```text
01  DISCOVERY!
02  DISCOVERY!      *
03  DISCOVERY!   MATHEMATICS
04  MATHEMATICS
    Allows: Catapult
05  MATHEMATICS
    Allows: Catapult
    Leads: Astronomy
```

Final frame holds until continuation is accepted.

## Diplomacy leader arrival

```text
01  +----------------+
    |                |
    |    [PORTRAIT]  |
    |                |
    +----------------+

02  CAESAR
03  CAESAR: "..."
04  RESPONSE OPTIONS
```

## Warning event

```text
01  WARNING
02  !! WARNING !!
03  !! BARBARIANS APPROACH !!
04  !! BARBARIANS APPROACH !!
```

Settle to a readable static warning card.

## Palace/Wonder presentation

Use center reveal:

```text
01          *
02        *   *
03      [WONDER]
04  THE GREAT PYRAMIDS
05  Completed in Memphis
```

## Space launch

```text
01      /===\
          ||

02      /===\
          ||
         /||\

03       /===\
          ||
         /||\
        / || \

04          *
           /===\
             ||
```

Final scene reports flight status.

## Victory

```text
01  VICTORY!
02    *
03  * VICTORY! *
04    *     *
05  FINAL RESULTS
```

## Replay

The replay cursor advances along a deterministic timeline:

```text
4000 BC ----●---------------- 1720 BC
            ^
          CURRENT
```

Advance may use `FAST`; pause/step uses immediate state changes.
