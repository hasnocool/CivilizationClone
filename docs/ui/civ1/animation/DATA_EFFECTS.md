# Data Visualization Effects

These effects animate changes in values without turning the terminal UI into a constantly moving display.

## EFFECT.DATA.PROGRESS

Generic discrete progress animation. The final value is authoritative.

```text
[███-------] 30%
[██████----] 60%
[████████--] 80%
[██████████] 100%
```

## EFFECT.DATA.NUMBER_ROLL

Use for treasury, population, score, year, or other values where a change deserves emphasis.

Rules:

- never imply intermediate values are authoritative;
- stop on the exact view-model value;
- use at most a small number of intermediate steps.

## EFFECT.DATA.BAR_FILL

Fills a bar from its old value to new value. Use for research, food storage, production, and replay progress.

## EFFECT.DATA.CHART_DRAW

Progressively draws a graph or sparkline. Best for Powergraph and historical reports.

## EFFECT.DATA.ROW_REVEAL

Reveals report rows sequentially. Use only for major result screens; ordinary reports should render immediately.

## EFFECT.DATA.DELTA

Visually attach a concise delta to an updated value.

```text
TREASURY: 153  (+12)
```

The delta should disappear or settle to a static historical indicator according to scene needs.

## EFFECT.DATA.STATUS_CHANGE

Emphasize a transition such as:

```text
PEACE -> WAR
DESPOTISM -> MONARCHY
RESEARCH -> DISCOVERY
BUILDING -> READY
```

The textual before/after labels are more important than animation.

## Reduced-motion rules

All data effects collapse to the final value plus optional delta text. No critical information may be omitted.
