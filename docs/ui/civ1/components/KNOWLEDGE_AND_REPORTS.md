# Knowledge and Report Components

## CIV1-COMP-TABLE

Aligned textual tables are a core terminal pattern for advisors, rankings, city lists, and world reports.

Requirements:

- stable column widths per rendered viewport;
- clear heading row;
- focusable rows;
- horizontal fallback for very wide reports;
- explicit empty state;
- numeric alignment for comparable values.

Example:

```text
CITY          POP   FOOD   PROD   TRADE
Rome           8      10      6       7
Antium         5       7      4       4
```

## CIV1-COMP-GRAPH

Character-based graph for Powergraph, trend reports, and replay statistics.

The graph needs:

- axes or a clearly documented baseline;
- legend;
- current position marker;
- textual summary for accessibility;
- static fallback.

Animation hook: `EFFECT.RESULTS.POWERGRAPH_DRAW`.

## CIV1-COMP-TECHCARD

Technology summary containing title, description, prerequisites, enabled content, and follow-on technologies.

Example:

```text
MATHEMATICS
-----------
Allows: Catapult
Leads to: Astronomy
Prerequisites: Writing, Code of Laws
```

## CIV1-COMP-TECHCHAIN

Represents the technology relationship graph in a compact terminal-friendly layout.

Example:

```text
WRITING --> MATHEMATICS --> ASTRONOMY
      \-> LITERACY
```

A focused technology should remain visibly marked while neighboring nodes provide context.

## CIV1-COMP-CIVILOPEDIAENTRY

Reusable article layout for units, technologies, terrain, improvements, governments, wonders, and historical/gameplay reference content.

Regions:

```text
TITLE
CATEGORY/BREADCRUMB
SUMMARY
PRIMARY DATA
DETAILS
RELATED ENTRIES
ACTIONS
```

## CIV1-COMP-HISTORYTIMELINE

Compact chronological list for historian/replay states.

```text
4000 BC  Civilization founded
3500 BC  First city
3200 BC  Writing discovered
```

The timeline can animate newly revealed entries but must retain a complete static version.

## Report emphasis

Reports can use semantic states:

```text
NORMAL
BEST
WORST
IMPROVING
DECLINING
CURRENT
SELECTED
```

Do not rely on red/green alone to communicate improvement or decline; use arrows, words, or signs as well.
