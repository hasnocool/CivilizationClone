# Map, Combat, and City Effect Recipes

## EFFECT.MAP.MOVE_UNIT

Purpose: communicate confirmed movement between neighboring cells.

Storyboard:

```text
01  [A].......
02  ..[A].....
03  ....[A]...
04  ......[A].
```

Metadata:

```text
duration: FAST per step
loop: ONCE
interruptible: ALWAYS
skip: YES
```

Fallback: redraw final map immediately.

## EFFECT.COMBAT.ATTACK

Purpose: show direction of an attack without requiring sprite animation.

```text
01  [LEGION]      [PHALANX]
02  [LEGION] ---> [PHALANX]
03  [LEGION] ==>  [PHALANX]
```

## EFFECT.COMBAT.IMPACT

Short impact effect.

```text
01  [A]  [E]
02  [A] *[E]*
03  [A] [#]
04  [A]
```

The impact sequence must never determine the result.

## EFFECT.COMBAT.RESULT

Show the authoritative outcome.

```text
-----------------------------
COMBAT RESULT
LEGION defeats PHALANX
-----------------------------
```

This is a `RESULT` severity effect and should hold until acknowledgement or normal scene flow permits dismissal.

## EFFECT.COMBAT.VICTORY

Optional celebratory marker:

```text
  *   VICTORY!   *
      LEGION
  *             *
```

Keep it compact. Do not obscure the map or result text.

## EFFECT.COMBAT.DEFEAT

Use restrained negative emphasis. Do not create distressing or excessively graphic imagery.

```text
[LEGION]
   X
DEFEATED
```

## EFFECT.CITY.PRODUCTION_PROGRESS

Use discrete progress changes tied to view-model values.

```text
[====------]
[======----]
[========--]
[==========]
```

## EFFECT.CITY.PRODUCTION_READY

```text
01  [==========]
02  *[==========]*
03  SETTLERS READY!
04  SETTLERS READY!
```

The final frame remains static.

## EFFECT.CITY.CITIZEN_ASSIGN

Focus moves across candidate cells:

```text
[F][F][S][T]
    ^
```

then:

```text
[F][F][S][T]
        ^
```

On confirmation, the tile becomes selected/worked according to authoritative state.

## EFFECT.CITY.GROWTH

Highlight changed population/yield state without forcing full-screen motion.

```text
POPULATION: 7  ->  8  (+1)
```

## EFFECT.CITY.IMPROVEMENT_BUILD

Reveal construction status using bar fill and a completion marker.

```text
BARRACKS [===-------]
BARRACKS [======----]
BARRACKS [==========]
BARRACKS READY
```
