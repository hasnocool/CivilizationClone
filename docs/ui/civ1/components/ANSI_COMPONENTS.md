# ANSI Component Reference

ANSI components extend the strict ASCII baseline with Unicode box drawing, richer glyphs, semantic style roles, and optional cursor/control effects.

## Frame

```text
╔════════════════════════════════╗
║ <TITLE>ROME                    ║
╠════════════════════════════════╣
║ content                        ║
╚════════════════════════════════╝
```

## Focus

```text
<FOCUS>▶ Move
        Wait
        Sentry
```

The role may map to color, bold, inverse, or another theme-specific treatment.

## Map

```text
≈ ≈ · · ▲ ▲
≈ · ♣ · · ▲
· · [R] ══ ·
```

## Unit marker

```text
▶[A]
```

## City marker

```text
┌──────┐
│ ROME │
│  4   │
└──────┘
```

## Progress

```text
████████░░░░  66%
```

## Warning

```text
<WARN> !! BARBARIANS APPROACH !!
```

## Technology card

```text
┌──────────────────────────────┐
│ <TITLE>DISCOVERY!           │
├──────────────────────────────┤
│      <RESEARCH>MATHEMATICS  │
│                              │
│ <INFO>Allows: Catapult       │
│ <INFO>Leads: Astronomy       │
└──────────────────────────────┘
```

## Dialogue

```text
╔══════════════════════════════╗
║ <DIPLOMACY> CAESAR           ║
╠══════════════════════════════╣
║ "We propose peace."           ║
║                              ║
║ <FOCUS>▶ ACCEPT              ║
║        REJECT                ║
╚══════════════════════════════╝
```

## ANSI rules

- semantic tags are references, not required literal escape sequences;
- a renderer chooses palette and capability tier;
- Unicode glyphs must degrade to ASCII when unavailable;
- colors do not carry meaning alone;
- blinking is optional and normally disabled in high-accessibility modes;
- terminal control sequences must be isolated inside the renderer rather than embedded in canonical scene semantics.
