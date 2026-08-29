# Research, Diplomacy, and Event Effect Recipes

## EFFECT.RESEARCH.DISCOVERY

A signature discovery sequence.

```text
01  +--------------------------+
    |       DISCOVERY!         |
    +--------------------------+

02  +--------------------------+
    |       DISCOVERY!         |
    |          *               |
    +--------------------------+

03  +--------------------------+
    |       DISCOVERY!         |
    |       MATHEMATICS        |
    +--------------------------+

04  +--------------------------+
    |       DISCOVERY!         |
    |       MATHEMATICS        |
    | Allows: Catapult         |
    +--------------------------+
```

Default: `DRAMATIC`, `ONCE`, `ACK`.

The final frame must remain visible until the scene's normal continuation action is available.

## EFFECT.RESEARCH.CHAIN_REVEAL

Reveal newly available technologies, units, or buildings after the main discovery title.

```text
MATHEMATICS
  |
  +--> Catapult
  +--> Astronomy
```

## EFFECT.RESEARCH.PROGRESS

Use a progress bar plus optional percentage/turn estimate.

```text
SCIENCE [██████░░░░] 60%
```

## EFFECT.DIPLOMACY.ARRIVAL

Reveal the leader identity panel before dialogue.

```text
01  +--------------------+
    |                    |
    |      [LEADER]      |
    |                    |
    +--------------------+

02  +--------------------+
    |       CAESAR       |
    |      [PORTRAIT]    |
    +--------------------+

03  CAESAR
    "We propose peace."
```

## EFFECT.DIPLOMACY.MOOD

Change emphasis when a leader's diplomatic state changes. Use text plus optional border/palette emphasis.

```text
CAESAR [NEUTRAL]
CAESAR [ANGRY]
```

Avoid constant blinking or rapid mood animation.

## EFFECT.DIPLOMACY.PROPOSAL

Reveal the transaction panel after dialogue.

```text
OFFER
-------
YOU GIVE: 50 GOLD
YOU GET:  WRITING

[ACCEPT] [REJECT] [COUNTER]
```

## EFFECT.DIPLOMACY.ACCEPT

Positive response should settle to explicit text:

```text
DEAL ACCEPTED
```

## EFFECT.DIPLOMACY.REJECT

Negative response:

```text
DEAL REJECTED
```

## EFFECT.EVENT.NOTICE

Routine event reveal. Use one short emphasis pulse followed by a static card.

## EFFECT.EVENT.WARNING

Warning should use at least two channels:

```text
!! WARNING !!
BARBARIANS APPROACH
```

ANSI palette emphasis is optional.

## EFFECT.EVENT.CRITICAL

Critical content remains visible until acknowledged or otherwise handled by the scene contract.

```text
+================================+
|| !! CRITICAL !!              ||
|| CITY UNDER ATTACK            ||
||                              ||
|| [ CONTINUE ]                 ||
+================================+
```

## EFFECT.EVENT.DISASTER

Use symbolic environment changes, localized impact emphasis, and a readable outcome summary. Avoid large screen-wide flashing.
