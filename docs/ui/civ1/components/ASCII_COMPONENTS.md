# Strict ASCII Component Reference

This file is the portability reference for reusable components. It intentionally avoids Unicode box drawing and ANSI control semantics.

## Borders

```text
+------------------------------+
| TITLE                        |
+------------------------------+
```

## Focused menu item

```text
> Move
  Wait
  Sentry
```

## Action bar

```text
[ OK ] [ CANCEL ] [ HELP ]
```

## Text field

```text
City Name: [ Antium____________ ]
```

## Map tile vocabulary

```text
.   plains/open terrain
~   water
^   hills/mountains
f   forest
R   resource/special marker
```

Clients may define additional ASCII glyphs, but canonical references should favor broadly available characters.

## City marker

```text
+------+
| ROME |
|  4   |
+------+
```

## Unit marker

```text
[A]
```

## Selection target

```text
  +---+
  |[A]|
  +---+
```

If a client cannot afford the extra border, use `>[A]<`.

## Progress

```text
[======------]
```

## Warning

```text
!! WARNING !!
```

## Information

```text
[INFO] Mathematics discovered
```

## Table

```text
CITY        POP  FOOD  PROD
Rome          8    10     6
Antium        5     7     4
```

## Graph

```text
|
|     A---
|   A
| B-
+------------
```

## Dialogue

```text
CAESAR:
We propose peace.

> ACCEPT
  REJECT
```

## Replay timeline

```text
4000 BC ---------+---------- 1720 BC
                 ^
               CURRENT
```

## Rules

ASCII components must remain meaningful without color, Unicode, cursor control, blinking, or animation. Every ANSI component should have a recognizable equivalent in this reference set.
