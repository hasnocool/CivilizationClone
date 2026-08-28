# Civ1-Inspired Scene Index

Stable IDs below are intended for documentation, test cases, client routing, screenshots, and issue references.

The catalog contains **168 distinct UI state templates**. `CIV1-UI-001..057` are the original stable IDs; `058..168` were added after a manual/screenshot audit found omitted setup, menu, subview, special-unit, event, diplomacy, replay, and failure states. See `COVERAGE_AUDIT.md` for scope and evidence.

For navigation topology, see `SCENE_GRAPH.md`.

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
| CIV1-UI-058 | Credits / Opening Credits | boot/system | continue |
| CIV1-UI-059 | Sound Driver Selection | boot/system | audio option |
| CIV1-UI-060 | Game / World Options | boot/setup | new/load/Earth/custom/HOF |
| CIV1-UI-061 | Load Drive Prompt | persistence/system | choose drive |
| CIV1-UI-062 | Customize World - Land Mass | boot/setup | world parameter |
| CIV1-UI-063 | Customize World - Temperature | boot/setup | world parameter |
| CIV1-UI-064 | Customize World - Moisture | boot/setup | world parameter |
| CIV1-UI-065 | Customize World - Age / Start | boot/setup | world parameter |
| CIV1-UI-066 | Level of Competition | boot/setup | choose 3-7 civs |
| CIV1-UI-067 | Custom Tribe Name Entry | boot/setup | custom tribe text |
| CIV1-UI-068 | Ruler Name Entry | boot/setup | ruler text |
| CIV1-UI-069 | Copy Protection Quiz | system | answer advance prerequisites |
| CIV1-UI-070 | Copy Protection Failure / Penalty | system | acknowledge |
| CIV1-UI-071 | Game Menu | strategic menu | choose game command |
| CIV1-UI-072 | Game Options Submenu | strategic menu | toggle options |
| CIV1-UI-073 | Tax Rate Dialog | economy | adjust tax |
| CIV1-UI-074 | Luxury Rate Dialog | economy | adjust luxury |
| CIV1-UI-075 | Find City Prompt | strategic menu | locate city |
| CIV1-UI-076 | Save Drive / Slot Prompt | persistence/system | choose save destination |
| CIV1-UI-077 | Quit Confirmation | confirmation | quit/cancel |
| CIV1-UI-078 | Retire Confirmation | confirmation | retire/cancel |
| CIV1-UI-079 | End of Turn Prompt | turn flow | continue turn cycle |
| CIV1-UI-080 | Instant Advice | advisor/help | contextual hint |
| CIV1-UI-081 | Historian Ranking - Advancement | periodic report | continue |
| CIV1-UI-082 | Historian Ranking - Happiness | periodic report | continue |
| CIV1-UI-083 | Historian Ranking - Power | periodic report | continue |
| CIV1-UI-084 | Historian Ranking - Size | periodic report | continue |
| CIV1-UI-085 | Historian Ranking - Wealth | periodic report | continue |
| CIV1-UI-086 | Unit Stack Activation | unit mode | choose unit to activate |
| CIV1-UI-087 | Go To Destination Targeting | unit mode | select destination |
| CIV1-UI-088 | Home City Reassignment | unit mode | change home city |
| CIV1-UI-089 | Settler Context Orders | unit menu | settler-specific orders |
| CIV1-UI-090 | Change Terrain Order | settler mode | confirm transformation |
| CIV1-UI-091 | Diplomat Bribe Enemy Unit Offer | diplomat | pay/refuse |
| CIV1-UI-092 | Diplomat Bribe Result | diplomat | acknowledge |
| CIV1-UI-093 | Diplomat Incite Revolt Price | diplomat | pay/refuse |
| CIV1-UI-094 | Diplomat Incite Revolt Result | diplomat | acknowledge |
| CIV1-UI-095 | Diplomat Establish Embassy Result | diplomat | acknowledge |
| CIV1-UI-096 | Diplomat Steal Technology Result | diplomat | details/acknowledge |
| CIV1-UI-097 | Diplomat Industrial Sabotage Result | diplomat | acknowledge |
| CIV1-UI-098 | Enemy City Inspection | diplomat/city | inspect/return |
| CIV1-UI-099 | Caravan Trade Route Delivery | caravan | delivery result |
| CIV1-UI-100 | Caravan Wonder Contribution Prompt | caravan | contribute/keep |
| CIV1-UI-101 | Minor Tribe - Ancient Wisdom | exploration event | technology result |
| CIV1-UI-102 | Minor Tribe - Joins as City | exploration event | view city |
| CIV1-UI-103 | Minor Tribe - Barbarians | exploration event | acknowledge |
| CIV1-UI-104 | Barbarian Leader Ransom | exploration event | acknowledge |
| CIV1-UI-105 | City Information Tab | city subview | inspect defenders/routes/pollution |
| CIV1-UI-106 | City Happiness Chart | city subview | inspect happiness causes |
| CIV1-UI-107 | City Map Subview | city subview | inspect world/trade/home units |
| CIV1-UI-108 | City Citizen Reassignment Mode | city mode | assign/remove workers |
| CIV1-UI-109 | City Specialist Assignment | city mode | specialist type |
| CIV1-UI-110 | Rename City Prompt | city | rename/cancel |
| CIV1-UI-111 | City Unit Activation | city mode | activate defender/support unit |
| CIV1-UI-112 | City Improvement Completed / View | presentation | continue |
| CIV1-UI-113 | Wonder Race Lost / Forced Production Change | city event | change production |
| CIV1-UI-114 | Civil Disorder Continues | city event | inspect/acknowledge |
| CIV1-UI-115 | We Love the King Day | city event | acknowledge |
| CIV1-UI-116 | Pollution Appears | environment event | center/acknowledge |
| CIV1-UI-117 | Global Warming | environment event | acknowledge |
| CIV1-UI-118 | Nuclear Meltdown | environment event | center/acknowledge |
| CIV1-UI-119 | Disaster - Earthquake | disaster | acknowledge |
| CIV1-UI-120 | Disaster - Famine | disaster | acknowledge |
| CIV1-UI-121 | Disaster - Fire | disaster | acknowledge |
| CIV1-UI-122 | Disaster - Flood | disaster | acknowledge |
| CIV1-UI-123 | Disaster - Piracy | disaster | acknowledge |
| CIV1-UI-124 | Disaster - Plague | disaster | acknowledge |
| CIV1-UI-125 | Disaster - Volcano | disaster | acknowledge |
| CIV1-UI-126 | Military Advisor - Casualties Page | advisor | page/back |
| CIV1-UI-127 | Intelligence Advisor - Detail Page | advisor | detail/back |
| CIV1-UI-128 | Civilopedia Section Menu | civilopedia | choose section |
| CIV1-UI-129 | Civilopedia Entry - History Page | civilopedia | next |
| CIV1-UI-130 | Civilopedia Entry - Gameplay Page | civilopedia | previous/close |
| CIV1-UI-131 | Rival Initiates Contact | diplomacy | receive/refuse |
| CIV1-UI-132 | Peace Offer | diplomacy | peace/war |
| CIV1-UI-133 | Technology Trade Selection | diplomacy | select advance |
| CIV1-UI-134 | Buy Peace / Rival Demand | diplomacy | pay/tech/refuse |
| CIV1-UI-135 | Post-Treaty Negotiation Menu | diplomacy | harmony/proposal/tribute/end |
| CIV1-UI-136 | Military Proposal - Target | diplomacy | choose third party |
| CIV1-UI-137 | Military Proposal - Payment | diplomacy | pay/decline |
| CIV1-UI-138 | Demand Tribute Result | diplomacy | acknowledge |
| CIV1-UI-139 | Break Treaty Warning | diplomacy/confirmation | proceed/cancel |
| CIV1-UI-140 | Senate Blocks War | government/diplomacy | acknowledge |
| CIV1-UI-141 | Declaration of War | diplomacy event | continue |
| CIV1-UI-142 | Peace Treaty Signed | diplomacy event | continue |
| CIV1-UI-143 | Rival Spaceship Status | space report | inspect/close |
| CIV1-UI-144 | Spaceship Launch Confirmation | space race | launch/keep building |
| CIV1-UI-145 | Spaceship In Flight | space race | inspect/close |
| CIV1-UI-146 | Rival Spaceship Launch | space event | inspect/acknowledge |
| CIV1-UI-147 | Rival Alpha Centauri Arrival | endgame | final score |
| CIV1-UI-148 | Automatic History End | endgame | final score |
| CIV1-UI-149 | Continue Playing After Victory | endgame | continue/end |
| CIV1-UI-150 | Replay Options | replay | choose replay/export/skip |
| CIV1-UI-151 | Quick Replay | replay | playback controls |
| CIV1-UI-152 | Complete Replay | replay | event-by-event playback |
| CIV1-UI-153 | Write Replay to Disk Result | replay/system | acknowledge |
| CIV1-UI-154 | Powergraph | endgame report | continue |
| CIV1-UI-155 | Destruction - Replay Offer | endgame | replay/exit |
| CIV1-UI-156 | Palace Improvement Invitation | presentation | view palace |
| CIV1-UI-157 | Rival Wonder Completed Announcement | presentation | view/continue |
| CIV1-UI-158 | Wonder Obsolete Announcement | presentation | acknowledge |
| CIV1-UI-159 | Treasury Shortfall / Improvement Sold | economy failure | acknowledge |
| CIV1-UI-160 | Unsupported Unit Lost | economy failure | acknowledge |
| CIV1-UI-161 | City Destroyed | city event | continue |
| CIV1-UI-162 | City Capture Loot - Technology | capture event | details/acknowledge |
| CIV1-UI-163 | City Capture Loot - Gold | capture event | acknowledge |
| CIV1-UI-164 | Nuclear Attack Result | combat event | continue |
| CIV1-UI-165 | SDI Interception | combat event | acknowledge |
| CIV1-UI-166 | Research Menu Civilopedia Help | help overlay | inspect/close |
| CIV1-UI-167 | Production Menu Civilopedia Help | help overlay | inspect/close |
| CIV1-UI-168 | City Advisor Recommendation Overlays | city/advisor | acknowledge |

## Reusable overlay

`GENERIC-CONFIRM` is not counted in the 168 canonical IDs. It is the shared confirmation shell for expensive, destructive, or irreversible actions where a dedicated historical prompt is not otherwise assigned an ID.

## Layout coverage

Every canonical ID appears in both a strict `.ascii` file and an enhanced `.ansii` file. The range-to-file mapping is maintained in `README.md`.

## Navigation spine

```text
BOOT / SYSTEM
     |
     v
GAME SETUP -------> LOAD / HALL OF FAME
     |
     v
WORLD MAP <-------> CITY
  |  |  |            |\
  |  |  |            | +--> CITY SUBVIEWS / MODES
  |  |  |            +----> PRODUCTION / ADVISORS
  |  |  |
  |  |  +--> RESEARCH / CIVILOPEDIA
  |  +-----> ADVISORS / WORLD REPORTS
  +--------> UNITS / DIPLOMACY / EVENTS
                   |
                   +--> SPACE RACE
                   +--> ENDGAME / REPLAY / POWERGRAPH
```

See `SCENE_GRAPH.md` for the Mermaid scene-family graph and transition notes.