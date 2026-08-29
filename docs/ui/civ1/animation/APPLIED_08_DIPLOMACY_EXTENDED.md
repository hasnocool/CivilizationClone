# Applied Visual References — Extended Diplomacy

Range: `CIV1-UI-131..142`
Source: `ascii/08_diplomacy_extended.ascii`, `ansii/08_diplomacy_extended.ansii`

## Scene bindings
131 Rival Initiates Contact = PORTRAIT.REVEAL + ALERT.PULSE
132 Peace Offer = DIPLOMACY.SEAL + DECISION.PULSE
133 Technology Trade Selection = LIST.REVEAL + ITEM.HIGHLIGHT
134 Buy Peace / Rival Demand = MONEY.ROLL + WARNING.FRAME + DECISION.PULSE
135 Post-Treaty Menu = MENU.REVEAL + PORTRAIT.PULSE
136 Military Proposal Target = TARGET.CURSOR + MAP.CENTER
137 Military Proposal Payment = MONEY.ROLL + CONFIRM.PULSE
138 Demand Tribute Result = RESULT.REVEAL + MONEY.COUNT_ROLL
139 Break Treaty Warning = CRITICAL.FRAME + CONFIRM.PULSE
140 Senate Blocks War = WARNING.FRAME + TEXT.REVEAL
141 Declaration of War = ALERT.PULSE + TRANSITION.SCAN
142 Peace Treaty Signed = DIPLOMACY.SEAL + TEXT.REVEAL

## ASCII storyboards

PORTRAIT.REVEAL:
```text
[      ]
```
```text
[  O   ]
[ /|\  ]
```
```text
[  O   ]
[ /|\  ]
[ / \  ]
LEADER
```

TREATY.SEAL:
```text
PEACE TREATY
------------
```
```text
PEACE TREATY
------------
[ SIGNED ]
```

WAR.TRANSITION:
```text
NEGOTIATION
    |
    v
WARNING
    |
    v
WAR DECLARED
```

## ANSI treatment

Diplomatic state changes should be highly legible: `<INFO>` for accepted peace, `<WARN>` for demands, `<CRITICAL>` for broken treaties/war. Use `▶` focus markers and a brief border emphasis around the final decision row.

No animation should change the underlying offered terms. Every result animation starts only after authoritative command success.
