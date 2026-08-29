# City and Economy Components

## CIV1-COMP-CITYGRID

The city grid visualizes worked tiles and their relationship to the settlement. It should remain compact enough to coexist with city statistics.

Example:

```text
[F][F][S][T][.]
[F][F][S][T][.]
[.][S][C][S][.]
[.][T][S][F][.]
[.][.][F][.][.]
```

States for a cell:

```text
AVAILABLE
WORKED
UNWORKED
SELECTED
FOCUSED
INVALID
```

Worker reassignment may animate focus movement, but authoritative assignment occurs only after the command is accepted.

## CIV1-COMP-CITIZENSTRIP

Compact population summary. A client may use symbolic citizens, specialists, or counts.

Examples:

```text
Citizens: :) :) :|
Citizens: 8 total / 2 unhappy
```

The component should expose a readable textual equivalent for assistive clients.

## CIV1-COMP-YIELDPANEL

Shows food, production/shields, trade, corruption, and other values relevant to the current ruleset.

Recommended structure:

```text
Food:      ████████░░
Shields:   ██████
Trade:     █████
Corrupt:   █
```

Bars should include a numeric/textual value when space permits so animation is not the only signal.

## CIV1-COMP-PROGRESSBAR

Reusable progress component for research, food growth, production, save/load operations, and replay progress.

States:

```text
EMPTY
ACTIVE
NEAR_COMPLETE
COMPLETE
PAUSED
ERROR
```

ASCII baseline:

```text
[======------]
```

ANSI/Unicode enhancement:

```text
████████░░░░
```

## CIV1-COMP-PRODUCTIONQUEUE

Shows current production and, where supported, pending production.

Minimum fields:

```text
item
current_amount
required_amount
estimated_turns
rush_available
```

Example:

```text
PRODUCTION: SETTLERS
Shields: ██████------------
Complete in 7 turns
```

Animation hook: `EFFECT.CITY.PRODUCTION_PROGRESS`.

## CIV1-COMP-IMPROVEMENTLIST

Lists city improvements and wonders with availability and optional status.

Recommended markers:

```text
[BUILT]
[AVAILABLE]
[BLOCKED]
[OBSOLETE]
[SELL]
```

The component should avoid implying why an item is blocked unless the authoritative view model provides that explanation.

## CIV1-COMP-CITY-DETAILS

A composed region containing city identity, population, government context, yields, supported units, improvements, production, and actions.

## Growth animation

`EFFECT.CITY.GROWTH` should emphasize the changed value without replaying an entire city screen.

Example:

```text
Population: 7
       ↓
Population: 8  +1
```

## Production completion

A completion event may use:

```text
[████████████]
SETTLERS READY!
```

The final result persists as a static state so a player who looks away during the effect can still understand what happened.

## Sell confirmation

Selling an improvement must use a confirmation modal where appropriate. The component should show item, city, return value, and the explicit action buttons.

```text
SELL BARRACKS IN ROME?
Receive: 20 gold
[ SELL ] [ KEEP ]
```

No animation may substitute for confirmation.
