# World Map and Terrain Components

The strategic map is the primary persistent workspace. The current scene contract identifies it as `CIV1-UI-007` and prioritizes map viewport, focused tile/unit feedback, critical status, commands, then secondary history. fileciteturn4file0

## CIV1-COMP-MAPGRID

The map viewport renders a rectangular collection of terrain cells. It should support:

- scrolling/panning;
- a map cursor;
- selected and targeted cells;
- unit/city overlays;
- unexplored/fogged cells;
- route previews;
- event highlights;
- optional animated environmental details.

The map renderer should treat each cell as a composable tile rather than encoding all information into one glyph.

## CIV1-COMP-TILE

A tile is the atomic spatial component.

Logical layers:

```text
base terrain
resource/yield
improvements
routes
city
unit
selection
fog/status overlay
```

This layering allows the same tile to render differently as state changes without inventing new scene types.

## CIV1-COMP-TERRAIN

Terrain glyphs should have a strict ASCII baseline and optional ANSI/Unicode forms.

Examples:

```text
ASCII: plains = .
ASCII: forest = f
ASCII: hills  = ^
ASCII: ocean  = ~

ANSI: plains = ·
ANSI: forest = ♣
ANSI: hills  = ▲
ANSI: ocean  = ≈
```

Animations such as `WATER_SHIMMER` are decorative and optional.

## CIV1-COMP-RESOURCE

Represents food, production, and trade contribution without requiring the map to become visually dense.

Possible compact grammar:

```text
F = food
S = shields/production
T = trade
C = special city/resource marker
```

ANSI clients may supplement these with distinct semantic glyphs, but the resource meaning must remain discoverable in the tile-information scene.

## CIV1-COMP-ROAD

Infrastructure should read as a connection between neighboring tiles rather than an isolated icon.

Example:

```text
..====..====..
```

Animation hook:

`EFFECT.MAP.BUILD_PROGRESS` can reveal a road segment progressively after an authoritative build event.

## CIV1-COMP-CITYMARKER

A city marker identifies the settlement and optionally displays population/selection information.

Compact form:

```text
[ROM]
```

Expanded form:

```text
┌──────┐
│ ROME │
│  4   │
└──────┘
```

States:

```text
NORMAL
SELECTED
TARGETED
UNDER_EVENT
NEWLY_FOUNDED
CAPITAL
```

`CITY_FOUND` may animate the selection highlight and label reveal, then settle to a static marker.

## CIV1-COMP-UNITMARKER

Represents a unit or stack on a map tile.

The marker must communicate ownership/faction and active selection independently when possible.

Example:

```text
[A]
```

Potential expanded ANSI form:

```text
▶[A]
```

Do not require tiny portraits or complex unit art to understand the active unit.

## CIV1-COMP-FOG

Fog/exploration state hides unavailable terrain while clearly distinguishing:

- unexplored;
- explored but currently out of sight;
- visible.

Example:

```text
???????
?? .. ??
?? [A]??
```

The renderer must never leak hidden information through animation, tooltips, status text, or decorative map effects.

## CIV1-COMP-MAPPATH

Shows a movement or route preview without implying that the command has been committed.

Example:

```text
[A]-.-.-[TARGET]
```

or:

```text
[A] → → ↘ ↓ [X]
```

Once the engine confirms movement, the preview is replaced by authoritative unit position.

## Map animation hooks

Recommended effects:

```text
EFFECT.CURSOR.MOVE
EFFECT.CURSOR.TARGET
EFFECT.MAP.TILE_REVEAL
EFFECT.MAP.MOVE_UNIT
EFFECT.MAP.PATH_PREVIEW
EFFECT.MAP.BUILD_PROGRESS
EFFECT.MAP.WATER_SHIMMER
EFFECT.MAP.CITY_FOUND
```

## Responsive behavior

When space is constrained:

1. preserve map cells;
2. preserve selected tile/unit visibility;
3. collapse secondary status panels;
4. move action controls into a modal/menu;
5. never shrink map glyphs below one terminal cell.
