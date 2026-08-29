# Semantic ANSI Palette Contract

The palette system defines meaning separately from terminal color implementation.

## Semantic roles

```text
<TITLE>
<SUBTITLE>
<MENU>
<FOCUS>
<SELECTED>
<INFO>
<ACTION>
<NOTICE>
<WARN>
<CRITICAL>
<GOOD>
<BAD>
<PLAYER>
<ALLY>
<ENEMY>
<TERRAIN>
<WATER>
<FOREST>
<MOUNTAIN>
<CITY>
<UNIT>
<RESOURCE>
<RESEARCH>
<DIPLOMACY>
<VICTORY>
<DEFEAT>
```

These tags are semantic references, not literal escape codes.

## Capability tiers

### ASCII_ONLY

No color. Meaning must come from text, symbols, borders, ordering, or spacing.

### ANSI_BASIC

Eight/eight-bright-color semantic mapping.

### ANSI_256

256-color themes may provide finer contrast but must preserve semantic relationships.

### ANSI_TRUECOLOR

Optional RGB themes for clients that support them.

## Recommended theme families

### CLASSIC_VGA

High-contrast late-1980s/early-1990s PC aesthetic.

### MONOCHROME

Single-color phosphor-like interface. Uses bold/inverse/markers instead of hue.

### GREEN_TERMINAL

Phosphor-inspired green presentation with restrained emphasis.

### AMBER_TERMINAL

Warm monochrome terminal aesthetic.

### HIGH_CONTRAST

Maximum text/background separation and reduced decorative styling.

## Contrast requirements

- focus must remain visible without color;
- warnings must contain a marker such as `WARN`, `!`, or `!!`;
- victory/positive state should have text or glyph feedback;
- disabled content should not become ambiguous when colors are unavailable;
- selected and focused states must remain distinguishable.

## Animation interaction

Color changes may reinforce animation states, but animation must remain meaningful when the palette is static.

Example:

```text
<FOCUS>▶ Move
```

The `▶` is the reliable semantic marker; ANSI emphasis is additive.

## Theme extensibility

Future clients may define additional themes so long as they map all required semantic roles and preserve accessibility rules. Client-specific palette files should not change scene logic or action identifiers.
