# Civ1-Inspired Scene Index

Stable IDs below are intended for documentation, test cases, client routing, screenshots, and issue references.

For the complete navigation topology, see `SCENE_GRAPH.md`, which contains both the overall ASCII scene graph and Mermaid diagrams.

| ID | Scene | Family | Primary interaction |
|---|---|---|---|
| CIV1-UI-001 | Title Screen | boot/setup | continue |
| CIV1-UI-002 | Main Menu | boot/setup | new/load/options/quit |
| CIV1-UI-003 | World Creation | boot/setup | world parameters |
| CIV1-UI-004 | Difficulty Selection | boot/setup | difficulty |
| CIV1-UI-005 | Civilization / Leader Selection | boot/setup | faction/leader |
| CIV1-UI-006 | Opening / Dawn of Civilization | boot/setup | continue |
| CIV1-UI-007 | Main World Map | strategic map | inspect/move/menus |
| CIV1-UI-008 | Orders Menu | strategic map | unit orders |
| CIV1-UI-009 | Tile Information | strategic map | inspect terrain |
| CIV1-UI-010 | Unit Information | strategic map | inspect unit |
| CIV1-UI-011 | Found City | city | name/confirm |
| CIV1-UI-012 | City Management | city | citizens/resources/production |
| CIV1-UI-013 | Change Production | city | unit/building/wonder |
| CIV1-UI-014 | Buy Production | city | treasury confirmation |
| CIV1-UI-015 | Sell Improvement | city | sell confirmation |
| CIV1-UI-016 | City View | city | presentation |
| CIV1-UI-017 | Choose Research | research | select advance |
| CIV1-UI-018 | Technology Discovered | research | discovery/details |
| CIV1-UI-019 | Civilopedia Browser | civilopedia | category/entry browse |
| CIV1-UI-020 | Civilopedia Entry | civilopedia | read/reference |
| CIV1-UI-021 | Advisors Hub | advisor | report selection |
| CIV1-UI-022 | City Status Advisor | advisor | empire city table |
| CIV1-UI-023 | Military Advisor | advisor | force summary |
| CIV1-UI-024 | Intelligence Advisor | advisor | rival intelligence |
| CIV1-UI-025 | Attitude Advisor | advisor | happiness summary |
| CIV1-UI-026 | Trade Advisor | advisor | income/science/luxury |
| CIV1-UI-027 | Tax/Luxury/Science Rates | advisor | sliders/rates |
| CIV1-UI-028 | Science Advisor | advisor | research summary |
| CIV1-UI-029 | World Menu | world report | report selection |
| CIV1-UI-030 | Wonders of the World | world report | wonder status |
| CIV1-UI-031 | Top Five Cities | world report | ranking |
| CIV1-UI-032 | Civilization Score | world report | score breakdown |
| CIV1-UI-033 | Known World Map | world report | overview map |
| CIV1-UI-034 | Demographics | world report | world ranking |
| CIV1-UI-035 | Palace | presentation | choose improvement |
| CIV1-UI-036 | First Contact | diplomacy | receive/refuse |
| CIV1-UI-037 | Diplomacy Conversation | diplomacy | negotiation menu |
| CIV1-UI-038 | Technology Exchange | diplomacy | trade technology |
| CIV1-UI-039 | Tribute / Demand | diplomacy | accept/refuse/counter |
| CIV1-UI-040 | Diplomat at Foreign City | diplomacy | mission action |
| CIV1-UI-041 | Revolution | government | transition event |
| CIV1-UI-042 | Form a Government | government | government selection |
| CIV1-UI-043 | New Cabinet | government | presentation/continue |
| CIV1-UI-044 | Barbarian Warning | event | acknowledge |
| CIV1-UI-045 | Civil Disorder | event | inspect/acknowledge |
| CIV1-UI-046 | City Captured | event | acknowledge |
| CIV1-UI-047 | Wonder Completed | presentation | view/continue |
| CIV1-UI-048 | Wonder Illustration | presentation | acknowledge |
| CIV1-UI-049 | Spaceship Overview | space race | construct/launch |
| CIV1-UI-050 | Spaceship Launch | space race | presentation |
| CIV1-UI-051 | Alpha Centauri Victory | endgame | final score |
| CIV1-UI-052 | Conquest Victory | endgame | final score |
| CIV1-UI-053 | Defeat | endgame | final score |
| CIV1-UI-054 | Final Rating | endgame | result summary |
| CIV1-UI-055 | Hall of Fame | endgame | ranking |
| CIV1-UI-056 | Save Game | persistence | name/save |
| CIV1-UI-057 | Load Game | persistence | select/load |

## Reusable overlay

`GENERIC-CONFIRM` is not counted in the 57 canonical scene IDs. It should be a shared confirmation modal used for disbanding, selling, declaring war, quitting, launching, spending treasury, and similar irreversible or expensive actions.

## Navigation spine

```text
BOOT -> SETUP -> WORLD MAP <-> CITY
                    |
                    +-> ADVISORS
                    +-> WORLD REPORTS
                    +-> CIVILOPEDIA
                    +-> DIPLOMACY
                    +-> RESEARCH
                    +-> EVENTS
                    +-> SPACE RACE
                    +-> ENDGAME
```

See `SCENE_GRAPH.md` for the expanded ASCII and Mermaid versions of this navigation spine.
