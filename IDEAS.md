# CivilizationClone Ideas Backlog

This document is a long-term design laboratory for ideas that could push CivilizationClone beyond a conventional Civilization-style 4X game and toward a deterministic, emergent civilization and world-history simulator.

The intent is not to implement everything. Ideas should compete for inclusion through prototyping, playtesting, simulation cost, explainability, and whether they create meaningful decisions rather than additional chores.

The central design thesis is:

> Civilizations should not be the entire simulation. Civilizations should emerge from the simulation.

And the central player-experience goal is:

> Increase depth faster than we increase required player input.

A larger empire should create harder strategic problems, not simply more clicks.

---

# Research-Informed Design Conclusions

This backlog was expanded after reviewing Firaxis' own Civilization VII design rationale, Civilization VII reviews and community criticism, CivFanatics discussions about late-game play, and systems used successfully by Old World, Victoria 3, Crusader Kings III, Distant Worlds 2, Stellaris, Endless Legend, Frostpunk, Terra Invicta, and related strategy/simulation games.

The most important findings are below.

## 1. The late game is the genre's central unsolved problem

Firaxis explicitly identified three root causes when designing Civilization VII:

- snowballing makes later decisions irrelevant;
- required actions grow with empire size until decisions become chores;
- civilization bonuses often matter only during a narrow historical window.

The answer should not simply be a hard reset between eras. A better solution is to preserve the consequences of earlier decisions while changing the *kind* of strategic problems the player faces.

## 2. More systems are useful only when they interact

Victoria 3 is instructive because population, employment, prices, political power, interest groups, laws, migration, and industry interact. A factory is not merely a production modifier; it changes employment, wages, demand, politics, urbanization, and trade.

CivilizationClone should prefer systems that produce consequences in several other systems.

## 3. Deep simulation requires aggressive delegation

Old World's Orders mechanic demonstrates that limiting available actions can make a strategy game more interesting because the player must decide what deserves attention.

Distant Worlds 2 demonstrates the complementary principle: complex simulated systems can remain manageable when the player may automate, advise, supervise, or directly control each domain.

CivilizationClone should therefore have first-class automation, governors, policy rules, alerts, and exceptions rather than treating automation as an accessibility afterthought.

## 4. Players need continuity and historical scars

A common criticism of hard age transitions is that accomplishments can feel erased. Good history simulation should instead create layers:

- old roads remain under modern highways;
- former capitals remain culturally important;
- obsolete industries leave cities with identities and political interests;
- old wars influence diplomatic memory;
- vanished states leave minorities, borders, claims, monuments, institutions, and diasporas;
- institutions may survive the civilization that founded them.

History should accumulate rather than periodically disappear.

## 5. Diplomacy should be a game, not a menu

Civilization VII reviews criticized diplomacy for feeling thin and transactional. Other strategy games show useful alternatives:

- negotiated demands and diplomatic plays;
- favors and leverage;
- multilateral institutions;
- foreign investment;
- subject autonomy;
- domestic political lobbies;
- federations and blocs;
- long-term reputation.

Diplomacy should be capable of changing borders, economies, laws, alliances, institutions, and spheres of influence without requiring war.

## 6. Crises should create strategies, not merely penalties

Endless Legend's winter design discussion contains an important general lesson: a global event is boring if it simply makes everyone slower. A crisis becomes interesting when it changes incentives and creates new opportunities for some strategies while threatening others.

Every crisis should therefore answer:

- What new strategy becomes possible?
- Who benefits?
- Who is exposed?
- What permanent historical consequence can result?

## 7. Factions should differ in rules, not merely percentages

Endless Legend's strongest factions change fundamental rules of play. CivilizationClone should move toward systemic asymmetry:

- different administration models;
- different settlement structures;
- different knowledge pathways;
- different military organization;
- different economic institutions;
- different diplomatic tools;
- different relationships between central and local government.

Nationality-specific technology trees should be part of this larger principle rather than the only differentiator.

## 8. The world should remain interesting even when the player is not acting

Distant Worlds 2's private economy and Crusader Kings III's character simulation make their worlds feel alive because autonomous actors continue pursuing goals.

CivilizationClone should contain actors that have their own incentives:

- households;
- firms;
- institutions;
- governors;
- political factions;
- religious organizations;
- universities;
- military commands;
- cities;
- regional governments;
- diasporas;
- minor powers.

The player should steer a civilization rather than personally perform every action undertaken by everyone in it.

---

# Design Guardrails

Every major feature should satisfy most of these rules.

1. **Deterministic core.** The same seed, commands, and ruleset produce the same authoritative result.
2. **Headless first.** Every mechanic must work through the engine/API without depending on a particular UI.
3. **Explainable outcomes.** The API should expose why a price changed, a rebellion formed, a technology spread, or an AI chose an action.
4. **No mandatory click inflation.** Empire scale must not linearly increase required player actions.
5. **Delegatable.** Repetitive operational decisions should support policies, governors, queues, rules, or automation.
6. **Consequential.** Important choices should affect more than one system and remain visible later.
7. **Recoverable.** Losing territory, a war, an election, or even an empire should create a new strategic situation rather than automatically ending meaningful play.
8. **Asymmetric where valuable.** Civilizations should sometimes have different rules, not just different modifiers.
9. **Emergent before scripted.** Prefer simulations that generate stories, with authored content layered over them.
10. **Historically inspired, not historically predetermined.** Geography and institutions should make historical outcomes plausible without forcing them.
11. **No omniscient player by default.** Knowledge, intelligence, maps, forecasts, and statistics may have uncertainty.
12. **Scale abstraction with era.** The player should not be assigning individual workers in a continent-spanning industrial state unless they explicitly choose to.

---

# GOAT-Level Design Bets

If only a small fraction of this file can be built, these are the highest-value bets.

| Priority | System | Why it could transform the genre |
|---|---|---|
| 1 | Player attention + delegation | Solves late-game micromanagement without removing depth |
| 2 | Population + autonomous actors | Makes the civilization feel inhabited rather than spreadsheet-like |
| 3 | Persistent historical layers | Makes a 6,000-year campaign feel like one continuous history |
| 4 | Emergent rise/fall/successor states | Turns setbacks into stories instead of reload prompts |
| 5 | Living economy + logistics | Makes geography, trade, infrastructure, and war interdependent |
| 6 | Deep diplomacy + world order | Gives peaceful players a strategic game as rich as warfare |
| 7 | Dynamic technology + knowledge diffusion | Makes development reflect what societies actually do |
| 8 | Internal politics + legitimacy | Makes governing an empire strategically different from acquiring one |
| 9 | Fog of knowledge | Makes exploration, intelligence, diplomacy, and science matter for the entire game |
| 10 | Dynamic crises | Keeps every era strategically fresh without erasing prior accomplishments |
| 11 | Systemic faction asymmetry | Makes civilizations genuinely replayable |
| 12 | World-history ledger | Turns each completed campaign into a unique historical artifact |
| 13 | Limited wars + negotiated peace | Makes conflict politically meaningful rather than total conquest by default |
| 14 | Private economy | Adds life and complexity without requiring the player to control every transaction |
| 15 | Institutions that outlive states | Creates continuity deeper than leaders or bonuses |
| 16 | Cities with identities | Makes places memorable across thousands of years |
| 17 | Diasporas and migration networks | Creates soft power, cross-border ties, and consequences of war/economics |
| 18 | Adaptive era transitions | Makes history change because the world changed, not because a timer expired |
| 19 | Play-after-collapse | Makes losing interesting and enables extraordinary comeback stories |
| 20 | Strategic late-game world systems | Replaces victory-button waiting with genuinely new decisions |

---

# I. People, Society, and Identity

## 1. Dynamic Population

Cities should contain demographic cohorts instead of only an integer population value.

Cohorts may track:

- culture;
- language;
- religion;
- occupation;
- wealth;
- education;
- age distribution;
- political preferences;
- loyalty;
- health;
- fertility;
- migration tendency;
- social mobility;
- urban/rural status.

Conquest should change political control immediately but population identity only gradually, if at all.

## 2. Migration

People should move in response to opportunity and pressure.

Drivers can include wages, housing, food, safety, taxation, political rights, education, family ties, war, climate, infrastructure, discrimination, disasters, and cultural affinity.

Migration can create booming frontier cities, shrinking industrial regions, refugee destinations, multicultural capitals, and political backlash without requiring bespoke scripts.

## 3. Diasporas

Migrants should not lose all connection to their places of origin.

Diasporas can create:

- trade links;
- remittances;
- cultural influence;
- diplomatic pressure;
- migration chains;
- lobbying;
- knowledge transfer;
- claims of protection;
- reconciliation opportunities.

A civilization can remain influential after losing territory if its people and institutions are spread across the world.

## 4. Dynamic Culture

Culture should be spatial, social, and multi-layered rather than a single yield.

Culture spreads through population, trade, education, religion, media, migration, institutions, tourism, prestige, conquest, and shared history.

Cities and regions can become culturally mixed, hybridize, assimilate, revive older identities, or influence foreign populations.

## 5. Hybrid Cultures

Long-term contact should sometimes create new cultures rather than forcing one side to replace the other.

Hybrid cultures can inherit:

- language traits;
- architectural styles;
- institutions;
- cuisine/trade preferences;
- military traditions;
- civic traditions;
- technologies.

These should be named and recorded by the history system.

## 6. Languages

Languages should spread through trade, education, administration, migration, literature, religion, science, and media.

A language might become a regional lingua franca, diplomatic language, scientific language, or global commercial language.

Translation capacity can influence knowledge diffusion and diplomacy.

## 7. Demographic Transition

Population growth should change with development.

Agrarian societies, early industrial cities, mature industrial societies, and wealthy modern societies should not all follow the same population-growth formula.

Age structure can affect labor supply, military manpower, education costs, pensions, housing demand, and politics.

## 8. Social Mobility

Education, wealth, law, institutions, and economic structure should affect movement between occupations and social classes.

A society can become rich but politically unstable if opportunity remains concentrated.

## 9. Inequality

Track distribution, not only average prosperity.

Two civilizations with identical GDP-equivalent output may feel very different if one has broad prosperity and the other has extreme concentration.

Inequality can influence consumption, migration, political factions, crime/corruption pressure, social mobility, and legitimacy.

## 10. Household Needs

Population demand should create economic pressure without requiring individual household simulation.

Needs can evolve from subsistence food and shelter toward manufactured goods, education, transport, electricity, healthcare, communications, leisure, and other services.

This makes economic development change *what the economy is for*.

---

# II. Politics, Government, and Legitimacy

## 11. Internal Political Factions

Population groups should empower political factions based on material interests, culture, institutions, and ideology.

Examples include landowners, merchants, labor, military institutions, religious organizations, rural interests, industrialists, scientists, environmental interests, and regional movements.

Policies should create winners and losers rather than being pure bonuses.

## 12. Political Parties and Coalitions

Where government type supports them, political parties can emerge as coalitions of interest groups.

A coalition may agree on some questions while containing serious internal contradictions.

## 13. Composable Governments

Government should be assembled from institutions rather than selected from a single dropdown.

Components may include:

- executive structure;
- legislature;
- judiciary;
- succession/election method;
- regional authority;
- voting franchise;
- civil service;
- economic constitution;
- military control;
- religious settlement.

## 14. Governments Evolve Instead of Unlocking

A civilization should not research a government and instantly transform.

Institutional change should depend on education, technology, political pressure, economic structure, legitimacy, factions, crises, and previous reforms.

## 15. Legitimacy

Separate raw state capacity from public or elite acceptance of rule.

Legitimacy may come from:

- tradition;
- elections;
- religion;
- prosperity;
- military success;
- law;
- nationalism;
- dynastic continuity;
- ideology;
- effective administration.

Different regimes can depend on different legitimacy sources.

## 16. Public Mandates and Promises

Borrow a lesson from Frostpunk: the government can make explicit promises.

Examples:

- complete a railway;
- defend an ally;
- avoid a war;
- reduce a shortage;
- fund education;
- recover a region;
- reform a law.

Keeping or breaking promises affects trust and political capital. This gives narrative weight to ordinary strategic choices.

## 17. Administrative Capacity

Large empires should require administration.

Administrative capacity depends on bureaucracy, communication, literacy, transport, institutions, law, local cooperation, and technology.

Overextension should create concrete tradeoffs rather than a generic empire-size penalty.

## 18. Regional Government

Large states can organize territory into provinces, states, departments, colonies, autonomous regions, or other administrative units.

The player can choose how much authority to delegate.

## 19. Local Governors as Autonomous Actors

Governors should have goals, competence, loyalty, political support, and local relationships.

They can manage routine decisions automatically while occasionally creating political problems or unexpected successes.

This turns delegation into gameplay rather than merely an automation checkbox.

## 20. Federalism and Autonomy

Regions may negotiate powers over taxation, language, education, policing, trade, infrastructure, or local law.

Autonomy can reduce administrative burden and separatism while limiting central control.

## 21. Succession and Constitutional Transition

Leadership change should matter without turning the game into a character simulator exclusively.

Different systems may experience:

- hereditary succession;
- elections;
- appointments;
- coups;
- regencies;
- coalition changes;
- constitutional crises.

Leadership turnover should interact with institutions so a mature state is not entirely dependent on one person.

## 22. Generational Leaders

Leaders should not live for 6,000 years.

Civilizations persist while leaders, dynasties, administrations, parties, and ruling coalitions change.

A leader's legacy should remain in laws, institutions, cities, wars, infrastructure, and historical memory.

## 23. Cabinets and Advisors

Key offices can be filled by simulated people or institutional representatives.

Advisors can improve domains, propose policies, disagree with the player, represent factions, and become historical characters.

## 24. Political Capital

Major reforms should consume political capacity rather than being free instant switches.

This creates opportunity cost between domestic reform, foreign policy, emergency actions, and institutional projects.

## 25. Revolutions with Negotiated Outcomes

Internal crises should not always be binary rebellion/no rebellion.

Possible outcomes include reform, autonomy, coalition change, constitutional convention, secession, restoration, negotiated settlement, or civil conflict.

---

# III. Rise, Fall, and Civilizational Continuity

## 26. Rise, Fall, Fragmentation, and Reunification

Large empires should gain power but also accumulate structural stresses such as administrative distance, inequality, regional identity, legitimacy problems, fiscal strain, succession disputes, and external pressure.

States can federalize, decentralize, fracture, reform, collapse, reunify, merge, or produce successor states.

## 27. Successor States

When a civilization fractures, successor states inherit different mixtures of:

- institutions;
- territory;
- military formations;
- debts;
- diplomatic commitments;
- cultural identity;
- claims;
- technology;
- leaders;
- historical legitimacy.

This makes collapse a transformation of the world rather than deletion.

## 28. Play After Collapse

One of the boldest features: losing the central state should not necessarily end the campaign.

The player might continue as:

- a successor state;
- government-in-exile;
- surviving region;
- federation partner;
- restored dynasty;
- diaspora-backed movement.

A spectacular recovery could become more memorable than a conventional victory.

## 29. Voluntary Unions

Civilizations can merge through diplomacy.

Possible structures include federations, dynastic unions, confederations, commonwealths, customs unions, and full political unions.

The resulting state should inherit history from all participants rather than pretending one simply conquered the others.

## 30. Emergent Civilization Names

Names can respond to dynasty, government, geography, dominant culture, capital, religion, revolution, federation, union, or restoration.

Historical aliases should remain searchable in the API and chronicle.

## 31. Historical Claims

Claims should emerge from previous control, treaties, settlement patterns, dynastic inheritance, cultural ties, and international recognition.

Claims can fade, strengthen, be renounced, transferred, disputed, or internationally arbitrated.

## 32. Persistent Historical Layers

The world should remember prior eras physically and institutionally.

Examples:

- ancient roads become modern corridors;
- former borders influence regions;
- old capitals retain prestige;
- ruins become archaeological sites;
- closed mines leave industrial towns;
- old universities retain research traditions;
- past migration creates minorities;
- war damage affects urban form;
- ancient irrigation remains useful centuries later.

## 33. Age Transitions Triggered by the World

Do not rely only on a global turn counter.

An era can emerge from thresholds such as communication speed, trade integration, energy use, military organization, scientific capability, urbanization, exploration, or institutional change.

Different regions may enter transformations at different times.

## 34. No Hard Historical Reset

Era change should introduce new strategic layers while preserving consequences.

Obsolete systems should decay, transform, or become automated rather than vanish arbitrarily.

## 35. Adaptive Crises

Crises should emerge from actual conditions.

Examples:

- fiscal crisis from debt;
- legitimacy crisis from political exclusion;
- food crisis from crop failure plus weak trade;
- industrial crisis from energy shortage;
- alliance crisis from incompatible commitments;
- ecological crisis from accumulated land use;
- succession crisis from weak institutions.

The crisis should feel like the world responding to the player's history.

## 36. Crises Create Opportunities

Every crisis should unlock strategies as well as penalties.

A trade disruption may encourage domestic industry. A political crisis may enable constitutional reform. A climate shock may make new regions valuable. A collapsing rival may create diplomatic openings.

---

# IV. Cities, Settlements, and Institutions

## 37. Settlements Evolve Naturally

Replace the instant Settler -> City transformation with development stages such as camp, village, town, city, metropolis, or specialized settlement.

Some settlements may never become large cities and can still matter strategically.

## 38. Cities Develop Identities

City roles should emerge from geography and history.

Examples:

- port city;
- financial center;
- university city;
- pilgrimage center;
- administrative capital;
- industrial region;
- military frontier;
- artistic center;
- agricultural market town.

Identity influences migration, politics, institutions, and investment.

## 39. Urban Form

Cities should physically change as transportation and industry change.

Dense pre-industrial cores, industrial belts, suburbs, port districts, rail corridors, civic centers, and high-density modern areas can emerge from rules rather than being static district puzzles.

## 40. Housing and Land Markets

Population growth should require land and housing.

High demand can raise costs, encourage expansion, increase density, push migration, and create political pressure.

## 41. Persistent Institutions

Universities, banks, courts, guilds, religious orders, corporations, hospitals, newspapers, museums, military academies, laboratories, and political organizations should be entities with their own histories.

Institutions can outlive rulers and even states.

## 42. Institutional Reputation

Prestigious institutions attract talent, capital, students, pilgrims, tourists, or political support.

Reputation should be slow to build and possible to damage.

## 43. Institutional Networks

Institutions should collaborate across cities and borders.

Examples include university networks, religious hierarchies, banking systems, research societies, merchant guilds, and international NGOs.

## 44. Wonders as Living Institutions

A wonder should not become a dead tile after construction.

Its purpose can evolve:

- temple -> heritage site;
- fortress -> museum;
- palace -> parliament;
- industrial landmark -> cultural site.

Its historical meaning may become more valuable than its original function.

## 45. Multi-Stage Great Projects

Great projects should involve planning, funding, materials, engineering, politics, and sometimes multiple civilizations.

Examples can include canal systems, continental rail networks, global scientific projects, major restoration projects, or large infrastructure programs.

## 46. Maintenance and Decay

Infrastructure and buildings should require maintenance at an aggregated level.

Neglect creates deterioration rather than instant disappearance.

Maintenance policy can be delegated by region and priority.

## 47. Postwar Reconstruction

War should create a strategic reconstruction phase rather than an instant return to full productivity.

Players can choose what to restore, redesign, abandon, memorialize, or modernize.

---

# V. Economy, Trade, Finance, and Autonomous Actors

## 48. Production Chains

Resources should move through meaningful production chains.

Examples:

```text
Iron Ore -> Iron -> Tools -> Machinery
Grain -> Flour -> Food
Coal + Iron -> Steel -> Rail / Machinery
Oil -> Fuel / Chemicals / Plastics
Silicon -> Electronics -> Computers
```

The engine should aggregate routine flows so the player manages networks and policy rather than individual shipments.

## 49. Dynamic Markets

Prices respond to supply, demand, transport cost, stockpiles, war, embargoes, technology, disasters, population needs, and market access.

Economic shocks should propagate through trade networks.

## 50. Transport Costs

Goods should not teleport.

Distance, roads, rivers, ports, rail, shipping capacity, terrain, borders, tariffs, and security affect delivered prices.

This makes geography economically meaningful throughout the game.

## 51. Trade Corridors

Persistent high-volume trade routes should become strategic corridors.

Corridors can attract cities, infrastructure, diplomacy, piracy/security pressure, cultural exchange, and political competition.

## 52. Economic Chokepoints

Straits, canals, river mouths, rail junctions, mountain passes, pipelines, data links, and major ports can become economic chokepoints.

Control matters because networks use them, not because the tile has an arbitrary bonus.

## 53. Private Economy

Inspired by Distant Worlds 2, much routine economic activity should occur autonomously.

Private actors may build firms, move goods, invest, migrate, and respond to prices while the player shapes taxes, law, infrastructure, subsidies, regulation, trade access, and strategic priorities.

## 54. Firms and Entrepreneurship

Companies can emerge where market conditions support them.

Firms may:

- expand;
- merge;
- fail;
- innovate;
- lobby;
- relocate;
- invest abroad;
- become national champions;
- form monopolies.

## 55. Corporations as Transnational Actors

Large corporations can operate across borders and create political relationships between states.

Governments can regulate, tax, subsidize, charter, nationalize, privatize, sanction, or break them up.

## 56. Foreign Investment

Civilizations can gain influence and returns by investing in infrastructure, industry, resources, institutions, or development abroad.

Foreign ownership can create both interdependence and domestic political tension.

## 57. Public Finance

States should have revenue sources and expenditures beyond a single gold balance.

At a strategic level track:

- taxation;
- tariffs;
- state enterprises;
- debt service;
- administration;
- military spending;
- infrastructure;
- education;
- social services;
- subsidies.

## 58. Debt and Credit

Governments, institutions, and firms can borrow.

Creditworthiness depends on fiscal history, institutions, stability, economic output, and currency confidence.

Debt enables extraordinary projects but creates future constraints.

## 59. Banking and Financial Crises

Banks can allocate capital and amplify economic growth.

Poor regulation, asset concentration, war, or defaults can create crises that spread through financial networks.

This should be abstract enough to remain strategic rather than accounting-heavy.

## 60. Currencies and Monetary Blocs

Later eras can support currencies, exchange-rate regimes, monetary unions, reserve currencies, and financial influence.

A civilization may wield monetary power without territorial conquest.

## 61. Economic Cycles

Investment booms, shortages, technological disruption, debt, and demand shifts can generate expansion and contraction.

Players should respond through policy rather than receive random recession events detached from the simulation.

## 62. Strategic Reserves

States can maintain reserves of food, fuel, currency, or critical materials.

Reserves trade efficiency for resilience and become important during crises.

---

# VI. Infrastructure, Logistics, Energy, and Geography

## 63. Logistics Networks

Military and economic systems should depend on supply networks.

Supply can abstract food, equipment, fuel, replacement capacity, and transport throughput rather than requiring manual inventories for every unit.

## 64. Infrastructure Networks

Roads, rail, ports, canals, airports, power, water, sewage, pipelines, and communications should form connected networks.

A disconnected improvement should not function identically to one integrated into a major system.

## 65. Rivers as Major Systems

Rivers should support transport, irrigation, fertility, industry, settlement, boundaries, defense, hydropower, and trade.

## 66. Navigable Rivers

Major rivers should permit appropriate inland transport and make river ports, bridges, mouths, and canals strategically important.

## 67. Hydrology

Rivers and lakes should derive from world geography.

Dams, irrigation, deforestation, drought, floods, and climate can alter water availability and downstream conditions.

## 68. Electricity as a Resource

Electricity should be generated, transmitted, and consumed.

Grid reliability, generation mix, fuel supply, storage, and interconnection become strategic in industrial and modern eras.

## 69. Energy Transitions

Civilizations should experience transitions among biomass, animal power, water/wind, coal, oil, electricity, nuclear, and renewables based on technology, geography, price, and policy.

Old infrastructure creates path dependence.

## 70. Communication Networks

Administrative and military coordination should improve as information moves faster.

Postal systems, printing, telegraph, radio, telephone, satellites, and digital networks can transform governance and markets.

## 71. Standards and Interoperability

Technological systems should sometimes require standards.

Examples:

- rail gauges;
- electrical standards;
- measurement systems;
- currencies;
- shipping containers;
- communications protocols.

Shared standards increase trade and network effects while creating lock-in and geopolitical influence.

## 72. Infrastructure as Soft Power

Financing a neighbor's railway, port, grid, or communications system can integrate their economy with yours and generate influence without annexation.

---

# VII. Science, Technology, Education, and Knowledge

## 73. Dynamic Technology Discovery

Technology should combine prerequisites with discovery pressure generated by actual activity.

A maritime civilization naturally accelerates navigation and shipbuilding. A mining-industrial state accelerates metallurgy and mechanical engineering. A dense scholarly network accelerates abstract science.

## 74. Competing Technology Paths

There should not always be a single universally superior sequence.

Different resource bases, institutions, geography, and doctrines can sustain different technological solutions for long periods.

## 75. Knowledge Diffusion

Technologies spread through trade, migration, education, books, institutions, diplomacy, espionage, conquest, scientific exchange, reverse engineering, and shared language.

A civilization can lead research without permanently monopolizing knowledge.

## 76. Research Ecosystems

Universities, firms, governments, military institutions, and independent inventors can pursue different kinds of research.

Breakthroughs may require combinations of theoretical knowledge, engineering capacity, funding, and practical demand.

## 77. Competing Schools of Thought

Scientific and intellectual fields can contain rival schools.

One approach may dominate because of evidence, institutional prestige, politics, or resource availability and later be displaced.

## 78. Scientific Uncertainty

Research should occasionally reveal uncertainty rather than a guaranteed next node.

The player can choose between safer incremental work and higher-risk research programs.

## 79. Engineering vs. Science

Knowing a principle and being able to deploy it at scale should be different achievements.

A civilization might understand electricity before possessing the industry, standards, workforce, or grid required to transform society with it.

## 80. Open Knowledge, Patents, and Secrecy

Later institutions can choose different innovation regimes.

Open research accelerates diffusion and collaboration; proprietary or secret systems may preserve temporary advantage but reduce spillovers.

## 81. Education Systems

Education should convert resources and institutions into literacy, skills, research capacity, social mobility, political participation, and economic productivity.

The structure of education matters, not merely total spending.

## 82. Brain Drain and Brain Gain

Talented populations and researchers should migrate toward safe, wealthy, prestigious, tolerant, well-funded institutions.

A civilization can become a scientific power partly by attracting people rather than only generating science points internally.

## 83. Collaborative Global Science

Late-game scientific projects can require multinational institutions, shared funding, and data.

Competition and cooperation can coexist.

---

# VIII. Religion, Ideology, Media, and Soft Power

## 84. Dynamic Religion

Religions should contain doctrines, institutions, holy places, clergy structures, reform movements, and regional practices rather than operate only as colored pressure.

## 85. Schisms and Reforms

Religious disagreement can create branches, reform movements, syncretic traditions, councils, and reconciliations.

Changes should be driven by politics, geography, institutions, interpretation, and cultural contact.

## 86. Ideologies Emerge from Conditions

Political ideologies should arise from combinations of technology, class structure, institutions, inequality, war, education, and previous political traditions.

They should not simply unlock from a civic node.

## 87. Public Sphere and Media

Printing, newspapers, radio, television, and digital media change how quickly ideas spread and how governments communicate with citizens.

Media organizations can become institutions with ownership, credibility, audience, and political alignment.

## 88. Information Reliability

Not every report should be equally trustworthy.

Players can receive rumors, estimates, intelligence assessments, official statistics, merchant reports, diplomatic reports, and scientific surveys with different confidence levels.

## 89. Propaganda and Counter-Narratives

Information campaigns can influence legitimacy, diplomacy, recruitment, culture, or foreign opinion, but effectiveness depends on credibility and media access rather than a guaranteed button effect.

## 90. Cultural Works with Provenance

Great works should have creators, locations, ownership history, cultural context, and movement across the world.

They can be sold, gifted, inherited, displaced, repatriated, stolen in historical events, restored, or displayed.

## 91. World Fairs, Festivals, and International Events

Civilizations can compete for prestige through recurring international events rather than only one-time wonders.

Hosting requires infrastructure and investment but can accelerate tourism, diplomacy, technology exchange, and urban development.

## 92. Prestige Has Multiple Sources

Prestige should come from science, culture, institutions, diplomacy, wealth, military reputation, humanitarian action, exploration, sport, architecture, and historical achievements.

Different societies can become globally influential for different reasons.

---

# IX. Exploration, Maps, and Information

## 93. Fog of Knowledge

The player should not automatically know exact foreign population, production, armies, technology, diplomacy, or resources.

Information comes from observation, trade, diplomacy, spies, institutions, satellites, and public statistics.

## 94. Maps Can Be Wrong or Outdated

Early maps can have approximate coastlines, uncertain routes, rumored cities, incomplete borders, and stale information.

Cartography, surveying, printing, aerial photography, and satellites progressively improve accuracy.

## 95. Exploration Expeditions

Exploration should involve decisions about goals, supplies, specialists, risk, route, and sponsorship rather than moving a disposable unit through fog.

Expeditions can produce maps, scientific observations, diplomatic contacts, artifacts, trade routes, or prestige.

## 96. Scientific Exploration

Exploration should continue after the map is geographically revealed.

Later expeditions can survey geology, ecology, oceans, poles, deep sea, atmosphere, and space.

## 97. Archaeology from Actual History

Archaeological sites should be generated from prior events in the current campaign.

A battlefield, abandoned capital, destroyed temple, ancient road, shipwreck, or lost settlement can become a later archaeological discovery.

This closes a powerful loop between simulation and historical storytelling.

## 98. Intelligence Networks

Espionage should depend on persistent networks, access, agents, institutions, diaspora links, trade ties, communications, and counterintelligence.

The interesting decision becomes where to build access and what information to trust, not repeatedly assigning identical spy missions.

---

# X. Diplomacy, International Order, and Minor Powers

## 99. Clause-Based Diplomacy

Treaties should be assembled from reusable clauses such as borders, navigation, trade, tariffs, migration, research, mutual defense, military access, sanctions, investment, resources, autonomy, recognition, and dispute resolution.

## 100. Diplomatic Leverage

Diplomacy should use trust, favors, obligations, economic dependence, domestic lobbies, military credibility, prestige, and shared institutions.

Influence becomes relational rather than a generic currency alone.

## 101. Negotiated Diplomatic Plays

Before conflict, states can make demands, recruit supporters, offer concessions, call in obligations, threaten sanctions, or propose arbitration.

A dispute may reshape the world without becoming a war.

## 102. Limited Wars and Explicit War Goals

Wars should usually begin with political objectives.

Possible goals include territory, recognition, independence, treaty revision, reparations, access, regime support, or defense of an ally.

Achieving the goal should create pressure to negotiate rather than automatically incentivize total conquest.

## 103. Peace Conferences

Peace should be negotiated among relevant participants.

Settlements can include borders, autonomy, guarantees, reparations, demilitarized arrangements, recognition, prisoners, access, sanctions, and international supervision.

## 104. Long-Term Diplomatic Memory

AI and populations should remember:

- fulfilled treaties;
- betrayals;
- aid during crises;
- shared wars;
- border settlements;
- investment;
- historical rivalry;
- reconciliation;
- cultural ties.

Memory should decay and be reinterpreted rather than being an eternal modifier.

## 105. Domestic Foreign-Policy Lobbies

Interest groups may care about particular foreign relationships because of trade, ideology, religion, diaspora, security, or investment.

Foreign policy can therefore create domestic consequences.

## 106. Spheres of Influence

States can create influence through trade, finance, infrastructure, institutions, military guarantees, culture, diplomacy, and investment.

A sphere is an emergent network of dependence rather than a simple ownership flag.

## 107. Federations and Power Blocs

Civilizations can construct international organizations with customizable rules.

Possible competencies include defense, trade, migration, research, currency, infrastructure, environment, courts, and foreign policy.

## 108. World Institutions

Late-game institutions should be politically important rather than decorative.

Members can propose rules, negotiate coalitions, trade favors, establish standards, coordinate crises, impose sanctions, fund projects, and create courts or agencies.

## 109. International Law

Treaties and institutions can gradually create norms.

States may comply because of reputation, reciprocity, domestic law, economic dependence, or institutional enforcement rather than because a game rule makes violation impossible.

## 110. Minor Powers with Agency

Minor states should have goals, factions, economies, territory, diplomacy, and survival strategies.

They should not exist merely as bonus dispensers for major civilizations.

## 111. Non-State Actors

Merchant leagues, religious orders, corporations, universities, liberation movements, international organizations, and other actors can influence diplomacy without owning conventional territory.

## 112. Protectorates, Subjects, and Autonomy

Subject relationships should have negotiated rights and obligations.

Autonomy can evolve over time, and a subject can become a partner, federation member, independent ally, or adversary.

---

# XI. Warfare Without Late-Game Unit Chore

## 113. Strategic Command Layer

As armies grow, the player should shift from moving every individual unit toward commanding formations, fronts, theaters, objectives, and priorities.

Direct tactical control can remain available for players who want it.

## 114. Orders as a Scarce Strategic Resource

Borrow the best lesson from Old World without copying it literally: leadership attention should be limited.

A civilization can theoretically do many things, but the central government can actively prioritize only some of them each turn or planning cycle.

This makes *not acting everywhere* a valid strategic choice.

## 115. Commanders and Institutional Military Memory

Commanders, units, and military institutions can accumulate experience, doctrine, traditions, and reputation.

Knowledge should persist partly after individuals retire.

## 116. Doctrine

Military effectiveness should reflect organizational doctrine, logistics, training, communications, terrain expertise, and industrial support rather than only unit-era strength.

## 117. Mobilization Has Economic Consequences

Large wars should pull labor, transport, finance, industrial capacity, and political attention away from civilian society.

Peace and war therefore become different economic states.

## 118. War Weariness Is Social

War exhaustion should emerge from casualties, duration, legitimacy, shortages, disrupted trade, political factions, enemy actions, and whether the population believes the war aims are justified or achievable.

## 119. Occupation Is Governance

Holding captured territory requires administration, security, local cooperation, supply, and political policy.

Occupation should not instantly convert a region into a normal productive province.

## 120. Resistance and Collaboration Are Political

Local behavior depends on legitimacy, culture, institutions, occupation policy, living conditions, war aims, and expectations about the future.

Use aggregate political systems rather than repetitive unit whack-a-mole.

## 121. Reconstruction and Reintegration

Post-conflict regions may require reconstruction, reconciliation, legal integration, autonomy agreements, or institutional reform.

Winning a war can create decades of strategic consequences.

---

# XII. Environment, Agriculture, Health, and Resilience

## 122. Dynamic Climate

Track temperature, rainfall, drought risk, sea level, storm patterns, snow cover, and other broad climate conditions.

Human activity can influence later-era climate while natural variability matters throughout history.

## 123. Land Use

Tiles can transition among forest, pasture, farmland, urban land, wetland, degraded land, restored ecosystem, and other uses.

Land-use history should affect fertility, runoff, biodiversity, carbon, and settlement.

## 124. Soil and Agriculture

Food production depends on soil, water, crops, climate, labor, tools, fertilizer, mechanization, storage, transport, and institutions.

Agricultural development should be one of the foundational technologies of civilization rather than simply a tile yield.

## 125. Crop and Food Diversity

Different regions can support different crops and food systems.

Trade and migration spread crops, cuisines, techniques, and resilience.

## 126. Food Storage and Famine Resilience

Food crises should depend not only on production but also reserves, trade, transport, inequality, governance, and conflict.

A rich state with poor distribution can still suffer serious shortages.

## 127. Public Health

Disease pressure can be modeled at a societal level through population density, clean water, sanitation, nutrition, trade connectivity, public health institutions, and medicine.

Avoid repetitive random plague buttons; outbreaks should emerge from conditions and spread through networks.

## 128. Ecosystem Services

Forests, wetlands, fisheries, soils, and biodiversity provide services such as water regulation, food, materials, resilience, and tourism.

Destroying natural systems can create delayed economic costs.

## 129. Pollution

Industrial activity produces local and regional externalities.

Pollution can affect health, agriculture, migration, politics, and international relations.

## 130. Environmental Restoration

Later societies can restore rivers, forests, wetlands, soils, and former industrial sites.

Environmental gameplay should include recovery, not only irreversible decline.

## 131. Disaster Recovery

Disasters should damage networks and communities unevenly.

Preparedness, institutions, wealth, infrastructure, insurance/reserves, and governance determine recovery speed.

A disaster can redirect migration and urban history for centuries.

---

# XIII. Player Attention, Delegation, and Anti-Micromanagement

## 132. Attention Budget

This may be the single most important usability mechanic in the entire design.

The player should have limited high-level attention, represented explicitly or implicitly.

The result: the empire can become more complex without requiring the player to manually touch every subsystem each turn.

## 133. Domain-Level Automation

Every major domain should support:

```text
Manual
Advise
Supervise
Automate with policy
Full automate
```

Domains can include city production, infrastructure, trade, research, exploration, military posture, diplomacy, taxation, and development.

## 134. Policy-Driven Automation

Automation should follow rules the player defines.

Examples:

```text
Maintain food reserve >= 20 turns
Never demolish historical buildings
Prioritize rail links to ports
Avoid debt above configured threshold
Do not settle low-water regions
Auto-upgrade infrastructure only if ROI threshold is met
```

This turns automation into strategy.

## 135. Governors Execute Intent

Instead of telling a city exactly what to build forever, the player can assign intent:

- research center;
- industrial hub;
- defensive frontier;
- trade port;
- cultural capital;
- balanced growth;
- ecological restoration.

Governors translate intent into operational decisions.

## 136. Exception-Based Management

The game should notify the player when a system leaves an acceptable range rather than asking for routine confirmation.

Examples:

- reserve falls below threshold;
- governor wants to override policy;
- strategic corridor is congested;
- ally requests treaty revision;
- major institution is failing;
- regional legitimacy is collapsing.

## 137. Empire-Wide Queues and Templates

Players should be able to create reusable infrastructure, city, military, and development templates.

## 138. Batch Decisions

If ten cities face the same problem, the player should be able to make one policy decision rather than ten identical clicks.

## 139. Strategic Planning Mode

Allow the player to sketch multi-turn intent:

- infrastructure corridors;
- settlement priorities;
- development zones;
- military fronts;
- conservation areas;
- research programs.

The simulation then executes within constraints and reports deviations.

## 140. Advisor Recommendations with Reasons

Advisors should provide recommendations plus causal explanations and expected tradeoffs.

Example:

```text
Recommend: expand North River rail capacity
Why:
  82% utilization
  steel exports delayed 2.4 turns average
  three cities depend on corridor
Expected effect:
  +11% regional market access
  -420 treasury now
Risks:
  increases debt ratio to 43%
```

## 141. Automation Must Be Deterministic

Automated decisions should use deterministic policies and expose their inputs so local agents and test harnesses can reproduce them.

---

# XIV. AI That Feels Like Other Civilizations

## 142. Difficulty Through Better Decisions, Not Huge Cheats

Difficulty should primarily modify planning depth, information mistakes, risk tolerance, coordination, and strategic competence.

Resource bonuses can remain optional but should not be the core solution.

## 143. AI Strategic Identity

AI civilizations should pursue coherent long-term strategies derived from geography, institutions, resources, threats, leaders, and political constraints.

## 144. AI Has the Same Institutional Constraints

AI should generally operate through the same logistics, diplomacy, population, economy, administration, and information systems as the player.

## 145. AI Explainability

For debugging and player trust, expose why the AI:

- declared war;
- rejected a treaty;
- invested in a region;
- changed policy;
- prioritized technology;
- allied with a rival;
- accepted peace.

## 146. AI Memory

AI relationships should use structured historical memory rather than arbitrary hidden mood swings.

## 147. AI Can Misjudge

Because information is imperfect, even strong AI should sometimes make reasonable mistakes based on outdated or incorrect information.

This is preferable to making AI omniscient.

## 148. AI Personalities Should Change Strategy, Not Sanity

Leader personality can alter risk tolerance, diplomatic style, priorities, and values, but should not force obviously irrational behavior merely to make a character colorful.

## 149. AI Uses Delegation Too

The AI should use the same governor, policy, automation, and planning abstractions exposed to players. This improves testability and keeps the game systems coherent.

---

# XV. Dynamic Objectives, Loss, Victory, and the Late Game

## 150. No Single Predetermined Endgame Loop

The late game should introduce new strategic layers rather than ask the player to repeat early-game actions at larger scale.

Candidate late-game systems include:

- global institutions;
- ideological competition;
- mass media;
- multinational firms;
- energy transitions;
- global infrastructure;
- climate coordination;
- financial systems;
- orbital infrastructure;
- international scientific projects;
- information networks.

## 151. Dynamic Historical Objectives

Goals should partly emerge from the world.

Examples:

- reunify a fractured cultural region;
- secure an endangered trade corridor;
- lead a scientific institution;
- modernize without losing political stability;
- preserve a federation;
- rebuild after collapse;
- create a monetary union;
- restore an ecological region.

## 152. Civilization Ambitions

Borrowing the useful part of Old World's ambitions, civilizations can adopt medium-term national projects that give direction without becoming rigid victory paths.

Ambitions should be generated from current history and opportunities.

## 153. Historical Achievements Instead of Winner-Takes-All

Track accomplishments such as:

- longest continuous state;
- greatest trading network;
- highest living standard;
- largest scientific contribution;
- greatest cultural influence;
- most resilient recovery;
- most influential language;
- most durable alliance;
- largest infrastructure network;
- strongest environmental recovery;
- greatest institutional legacy.

## 154. Multiple Measures of Success

A civilization can be militarily weak yet culturally dominant, territorially small yet financially central, politically fragmented yet scientifically influential.

The final chronicle should reflect these distinctions.

## 155. Make Losing Fun

Loss should create new goals, not only a defeat screen.

A reduced civilization may focus on survival, diplomacy, modernization, cultural preservation, independence, or eventual restoration.

## 156. Graceful Concession

If a player's position is mathematically or strategically decided, the game can offer a meaningful historical wrap-up rather than forcing dozens of ceremonial turns.

The player may continue if desired.

## 157. Post-Victory Sandbox

Victory should not require the simulation to stop.

Players can continue the world, disable score/victory checks, or hand control to AI and observe history.

## 158. World-Order Endgame

Instead of a final technology automatically ending the game, mature civilizations compete to shape the rules of the world:

- trade order;
- security architecture;
- scientific institutions;
- environmental agreements;
- monetary systems;
- communications standards;
- orbital governance.

The late game becomes about *what kind of world was created*.

---

# XVI. History, Narrative, and Memory

## 159. World-History Ledger

Every significant event should be recorded in a queryable event ledger.

Examples:

```text
318 BC  University of Alexandria founded
42 BC   Sicily earthquake damaged three cities
622 AD  Persian Empire fragmented into three successor states
1498    First trans-oceanic trade corridor established
1843    Northern Railway connected six industrial cities
```

## 160. Procedural Chronicle

The game should generate readable histories from authoritative events rather than inventing unsupported narrative.

Possible outputs:

- civilization history;
- city history;
- dynasty/leader history;
- war history;
- economic history;
- technology history;
- institutional history;
- diplomatic history.

## 161. Historical Maps

Allow the player to view the world at any past turn with known borders, population, cultures, infrastructure, trade, and environment.

## 162. City Timelines

Every important city should have a timeline of founding, conquest, migration, major construction, population peaks, institutions, disasters, and political changes.

## 163. Artifact Provenance

Important works, artifacts, documents, and monuments should retain creation and ownership history.

## 164. National Memory

States and populations can remember foundational events differently.

A former war can become a shared victory, tragedy, grievance, liberation story, or reconciliation milestone depending on later institutions and politics.

## 165. Historical Reputation

A civilization's international identity emerges from repeated behavior over centuries: reliable treaty partner, commercial hub, scientific center, aggressive expansionist, mediator, protector, cultural exporter, and so on.

## 166. Great People Emerge from the Simulation

Scientists, artists, engineers, explorers, merchants, politicians, diplomats, and commanders should arise from population and institutions.

Their achievements become part of world history rather than appearing only from a fixed prewritten list.

## 167. Rivalries Between Historical Figures and Institutions

Important people can belong to competing schools, parties, courts, companies, universities, or artistic movements.

This produces stories without requiring every citizen to be simulated individually.

## 168. Player-Defined Historical Markers

Allow players to bookmark events, cities, borders, wars, projects, or people as personally significant. These markers can appear in the final chronicle.

---

# XVII. Systemic Asymmetry and Nationality Design

## 169. Nationalities Change Rules, Not Just Yields

Each nationality should have at least one system-level difference where historically and mechanically justified.

Possible dimensions:

- administration;
- settlement;
- trade;
- military organization;
- diplomacy;
- knowledge;
- religion;
- infrastructure;
- succession;
- regional autonomy;
- institutions.

## 170. Nationality-Specific Technology Ecosystems

Existing nationality technology trees should integrate with dynamic discovery.

A nationality may have unique:

- research pressures;
- institutions;
- alternative prerequisites;
- specialized applications;
- diffusion bonuses;
- historically plausible dead ends;
- synthesis technologies.

## 171. Geography Can Reshape National Identity

A nationality placed in a radically different geography should adapt.

A historically maritime culture forced inland might develop new institutions over centuries rather than being permanently trapped by bonuses designed for coasts.

## 172. Traditions Persist Through Transformation

When civilizations merge, split, reform, or change identity, some traditions can persist as institutional or cultural legacies.

## 173. Asymmetry Must Remain Legible

Systemic differences should be explained in terms of changed rules and incentives, not hidden modifiers.

---

# XVIII. Future and Post-Industrial Era

## 174. Orbital Infrastructure

The space age should add a limited strategic orbital layer for satellites, communications, navigation, science, observation, and later larger projects.

It should extend existing infrastructure systems rather than become an unrelated minigame.

## 175. Space as Global Infrastructure

Satellites can improve weather forecasting, maps, communications, agriculture, logistics, disaster response, and intelligence.

This makes space relevant even before off-world settlement.

## 176. Off-World Projects

Late projects may include lunar research, resource experiments, planetary science, and international missions.

Keep these expensive and institutionally demanding so they emerge from the existing economy and science systems.

## 177. Automation and Labor Transformation

Advanced automation changes labor demand, productivity, education needs, inequality, and politics rather than simply granting +X production.

## 178. Digital Economy

Data networks, software, services, digital trade, and cybersecurity can emerge from communications, education, institutions, and energy infrastructure.

## 179. Global Commons

Climate, oceans, orbital space, scientific knowledge, and major communications systems can require international governance.

## 180. Future Technology Remains Branching

Avoid a single deterministic speculative-tech ladder.

Future development should depend on resource constraints, institutions, political choices, environmental pressures, and prior research ecosystems.

---

# XIX. Small Features With Outsized Impact

## 181. Searchable History

Every event, city, treaty, institution, leader, technology, and war should be searchable through the API/client.

## 182. Causal Tooltips

Every important number should answer "why?"

Example:

```text
Food price +18%
  +9% drought in Western Basin
  +6% railway disruption
  +4% population growth
  -1% strategic reserve release
```

## 183. Future Projection

For systems with understandable trends, show conditional forecasts:

```text
If current policy continues:
  reserve depletion in ~7 turns
  housing shortage worsens
  debt ratio rises to 61%
```

Forecasts should include confidence and assumptions.

## 184. Compare Policies Before Enacting

Players should be able to preview likely winners, losers, costs, risks, and affected systems before major reforms.

## 185. Historical Baseline Comparison

Show how a city, institution, or civilization changed over 10, 50, 100, or 500 turns.

## 186. Automatic Map Annotations

The engine can label major corridors, contested frontiers, cultural regions, economic basins, industrial belts, and metropolitan areas based on simulation data.

## 187. Named Wars and Crises

Major conflicts and crises receive emergent names derived from participants, regions, causes, or later historical interpretation.

## 188. Named Infrastructure

Important bridges, railways, canals, ports, dams, research programs, and expeditions can receive persistent names and histories.

## 189. Memorials and Commemoration

Societies can choose to commemorate major events, changing culture, tourism, legitimacy, reconciliation, or diplomatic relationships.

## 190. Historical Reconciliation

Longstanding rivals can undertake deliberate reconciliation through treaties, memorials, exchanges, institutional cooperation, border settlements, or shared projects.

A rivalry does not have to be mechanically permanent.

---

# XX. Features Civilization Should Have Used to Solve Its Own Core Problems

This section turns the research into direct answers to recurring Civilization weaknesses.

## Problem: Early game is magical, late game is chores

Use:

- attention budget;
- governors;
- automation policies;
- army/front command;
- batch decisions;
- exception-driven alerts;
- world institutions;
- finance;
- global projects;
- dynamic crises;
- new late-game strategic layers.

## Problem: Snowballing decides the game too early

Use:

- logistics constraints;
- administrative capacity;
- internal politics;
- debt;
- maintenance;
- regional autonomy;
- diplomatic balancing;
- technological diffusion;
- dynamic crises;
- coalition formation;
- succession and institutional stress.

These systems should create *new decisions* for strong empires rather than arbitrary rubber-banding.

## Problem: Catch-up systems erase accomplishments

Use:

- diffusion rather than reset;
- successor states;
- preserved institutions;
- adaptive crises;
- changing strategic layers;
- diminishing relevance of obsolete advantages;
- world reaction to dominant powers;
- new technologies that shift comparative advantage.

## Problem: Diplomacy is shallow

Use:

- treaty clauses;
- diplomatic plays;
- favors/obligations;
- lobbies;
- foreign investment;
- blocs;
- world institutions;
- subjects/autonomy;
- negotiated peace;
- historical reputation.

## Problem: Religion becomes repetitive unit pushing

Use:

- institutions;
- doctrine;
- reform;
- schisms;
- demographic adherence;
- education;
- diplomacy;
- culture;
- charitable/educational networks;
- political relationships.

## Problem: Espionage is repetitive missions

Use:

- access networks;
- information confidence;
- institutional infiltration;
- counterintelligence;
- diplomatic consequences;
- media;
- economic intelligence;
- strategic reporting.

## Problem: Minor states become bonus vendors

Use:

- internal goals;
- economies;
- factions;
- diplomacy;
- federations;
- protectorates;
- trade roles;
- regional institutions;
- survival strategies.

## Problem: Every civilization eventually plays similarly

Use:

- systemic asymmetry;
- path-dependent institutions;
- dynamic technology;
- geography-driven adaptation;
- political structures;
- unique administration;
- unique economic organization;
- unique diplomacy;
- persistent historical traditions.

## Problem: Difficulty is mostly AI bonuses

Use:

- better planning;
- shared constraints;
- explainable AI;
- imperfect information;
- coherent strategic identity;
- stronger delegation;
- realistic coalition behavior.

---

# Suggested Prototype Sequence

Do not try to build the entire simulation at once. The best path is to prototype the systems that create the greatest number of later interactions.

## Prototype A: Attention + Delegation

Implement first because every later deep system depends on controlling micromanagement.

Test:

- manual/advised/automated domains;
- governor intent;
- thresholds;
- exception alerts;
- deterministic policy rules;
- batch actions.

Success metric: a player controlling 30 settlements should not need roughly 30x the operational input of a player controlling one settlement.

## Prototype B: Population + Migration

Add cohorts, employment, culture, migration, and basic needs.

Success metric: city growth and decline should produce understandable stories without scripted events.

## Prototype C: Logistics + Markets

Connect production, transport, prices, reserves, infrastructure, and trade.

Success metric: geography should change economic strategy even if resource yields remain identical.

## Prototype D: Internal Politics + Legitimacy

Connect population outcomes to factions, policy support, and regional stability.

Success metric: two equally wealthy civilizations with different economic structures should develop different politics.

## Prototype E: Dynamic Knowledge

Connect practical activity, institutions, research, education, and diffusion.

Success metric: civilizations should develop recognizably different technology portfolios from different histories.

## Prototype F: Successor States + Historical Layers

Make collapse, secession, union, and reform preserve institutions and history.

Success metric: a fragmented empire should create a playable and historically understandable new world rather than merely smaller colored regions.

## Prototype G: Diplomacy + World Order

Add treaty clauses, interests, obligations, negotiated disputes, blocs, and institutions.

Success metric: a player should be able to change the balance of power dramatically without territorial conquest.

## Prototype H: World Chronicle

Generate histories from authoritative events.

Success metric: reading a campaign chronicle should reveal why the world looks the way it does.

---

# Kill Criteria

Ambitious ideas should be removed or redesigned when they fail these tests.

Reject or simplify a feature if:

- optimal play requires repetitive clicking;
- it produces information but no meaningful decision;
- it has no interaction with other systems;
- it requires omniscient knowledge to use competently;
- the AI cannot reason about it using the same rules;
- it cannot explain its outcomes;
- it creates unavoidable snowballing;
- it makes the early game richer but the late game slower;
- it exists mainly because another strategy game has it;
- it is historically flavorful but strategically irrelevant;
- it is strategically important but invisible to the player;
- it cannot be tested deterministically.

---

# Research References

These references informed the design conclusions above. They are inspiration and comparative design research, not specifications to copy.

## Civilization

- Firaxis / Civilization VII Dev Diary #1: Ages and the late-game problems of snowballing, micromanagement, and civilization relevance: https://civilization.2k.com/civ-vii/game-guide/dev-diary/ages/
- PC Gamer, Civilization VII review, particularly discussion of thin diplomacy, late-game systems, government, religion, espionage, and the missing World Congress: https://www.pcgamer.com/games/strategy/civilization-7-review/
- CivFanatics discussions about late-game micromanagement, governors, automation, and meaningful decisions: https://forums.civfanatics.com/

## Old World

- Old World review discussion of the Orders/Legitimacy system and the value of prioritizing actions: https://www.pcgamer.com/old-world-review/

## Victoria 3

- Paradox developer diary describing Pops, industries, political strength, interest groups, laws, and interconnected economic/political simulation: https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-57-the-journey-so-far
- Victoria 3 diplomacy and strategic interests design: https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-58-interest-revisions
- Sphere of Influence systems including foreign investment, subjects, lobbies, and power blocs: https://www.paradoxinteractive.com/games/victoria-3/add-ons/victoria-3-sphere-of-influence

## Distant Worlds 2

- Private/state economy and automated civilian logistics: https://www.matrixgames.com/news/distant-worlds-2-dev-diary-6
- Flexible manual/advisor/automation design: https://www.matrixgames.com/news/distant-worlds-2-dev-diary-1
- Guided automation philosophy: https://www.matrixgames.com/news/distant-worlds-2-feature-stellar-update

## Crusader Kings III

- Character, dynasty, inheritance, realm, and long-form emergent storytelling concepts: https://www.paradoxinteractive.com/games/crusader-kings-iii/about

## Stellaris

- Federations and Galactic Community as examples of customizable multilateral institutions and resolutions: https://www.paradoxinteractive.com/games/stellaris/add-ons/stellaris-federations

## Endless Legend

- Asymmetric faction rules and alternatives to standard 4X play: https://www.pcgamer.com/endless-legend-review/
- Enhanced Winter design notes illustrating the principle that world events should alter strategy rather than simply slow everyone: https://community.amplitude-studios.com/amplitude-studios/endless-legend/blogs/417-shifters-focus-on-the-enhanced-winter

## Frostpunk

- Society, law, promises, and crisis decisions as sources of political consequence: https://www.pcgamer.com/frostpunk-review/

## Terra Invicta

- Factions, councilors, organizations, ideology, and influence operating across conventional nation boundaries: https://wiki.hoodedhorse.com/Terra_Invicta/Factions

---

# Long-Term Vision

The target is not merely a larger Civilization ruleset.

The target is a game where this can happen naturally:

```text
A river creates a trade corridor.
        |
A trading town grows into a city.
        |
Merchants establish institutions.
        |
Those institutions finance industry.
        |
Industry attracts migrants.
        |
Migration changes politics and culture.
        |
Political reform creates regional autonomy.
        |
A university network accelerates engineering.
        |
Railways integrate distant regions.
        |
The state becomes too centralized for its new scale.
        |
A fiscal and legitimacy crisis forces federal reform.
        |
A neighboring state joins the federation voluntarily.
        |
The new union becomes a global standards-setter.
        |
Its language and universities spread worldwide.
        |
Centuries later the original river city is no longer
its capital, but remains its cultural and financial heart.
```

No designer had to script that exact story.

The simulation created it from geography, people, institutions, economics, politics, technology, diplomacy, and historical memory.

That is the standard CivilizationClone should aim for: not merely "one more turn," but **one more chapter in a world whose history the player actually understands and helped create.**

---

# Complete Priority Ranking (1-245)

This ranking is intended as a **development-priority ranking**, not a ranking of which ideas are coolest. It weights each idea by:

- core gameplay impact: 30%;
- how many other systems depend on it: 25%;
- late-game improvement / anti-micromanagement value: 20%;
- emergent-history and replayability value: 15%;
- technical/platform leverage: 10%.

Items #191-245 are audit-gap candidates identified after the original 190-item backlog. Their names are retained here so the ranking can serve as the master prioritization index even before every candidate receives a full write-up.

## S Tier - Foundational / Must-Have

1. **#132 Attention Budget**
2. **#239 Hierarchical Simulation / Level of Detail**
3. **#1 Dynamic Population**
4. **#133 Domain-Level Automation**
5. **#134 Policy-Driven Automation**
6. **#63 Logistics Networks**
7. **#48 Production Chains**
8. **#49 Dynamic Markets**
9. **#17 Administrative Capacity**
10. **#11 Internal Political Factions**
11. **#73 Dynamic Technology Discovery**
12. **#75 Knowledge Diffusion**
13. **#26 Rise, Fall, Fragmentation, and Reunification**
14. **#32 Persistent Historical Layers**
15. **#99 Clause-Based Diplomacy**
16. **#113 Strategic Command Layer**
17. **#199 Geological World Generation**
18. **#191 Mod-First Rules Architecture**
19. **#144 AI Has the Same Institutional Constraints**
20. **#142 Difficulty Through Better Decisions, Not Huge Cheats**
21. **#93 Fog of Knowledge**
22. **#64 Infrastructure Networks**
23. **#53 Private Economy**
24. **#41 Persistent Institutions**
25. **#169 Nationalities Change Rules, Not Just Yields**
26. **#211 Rule of Law**
27. **#217 Labor Markets**
28. **#220 Technology Adoption Curves**
29. **#222 Non-Sedentary Civilizations**
30. **#159 World-History Ledger**

## A+ Tier - Very High Value

31. **#245 Performance as a Game-Design Constraint**
32. **#141 Automation Must Be Deterministic**
33. **#139 Strategic Planning Mode**
34. **#135 Governors Execute Intent**
35. **#136 Exception-Based Management**
36. **#143 AI Strategic Identity**
37. **#145 AI Explainability**
38. **#182 Causal Tooltips**
39. **#35 Adaptive Crises**
40. **#33 Age Transitions Triggered by the World**
41. **#34 No Hard Historical Reset**
42. **#102 Limited Wars and Explicit War Goals**
43. **#101 Negotiated Diplomatic Plays**
44. **#104 Long-Term Diplomatic Memory**
45. **#110 Minor Powers with Agency**
46. **#57 Public Finance**
47. **#50 Transport Costs**
48. **#81 Education Systems**
49. **#193 First-Class Multiplayer Simulation**
50. **#198 Branchable Historical Replays**
51. **#192 WorldBuilder + Scenario Studio**
52. **#242 Mod Compatibility and Versioned Rulesets**
53. **#150 No Single Predetermined Endgame Loop**
54. **#158 World-Order Endgame**
55. **#15 Legitimacy**
56. **#13 Composable Governments**
57. **#14 Governments Evolve Instead of Unlocking**
58. **#19 Local Governors as Autonomous Actors**
59. **#37 Settlements Evolve Naturally**
60. **#38 Cities Develop Identities**
61. **#70 Communication Networks**
62. **#124 Soil and Agriculture**
63. **#126 Food Storage and Famine Resilience**
64. **#122 Dynamic Climate**
65. **#98 Intelligence Networks**
66. **#100 Diplomatic Leverage**
67. **#108 World Institutions**
68. **#106 Spheres of Influence**
69. **#27 Successor States**
70. **#28 Play After Collapse**
71. **#171 Geography Can Reshape National Identity**
72. **#173 Asymmetry Must Remain Legible**
73. **#240 Layered Complexity and Onboarding**
74. **#241 Strategic Map Lenses**
75. **#200 Resource Discovery and Reserve Estimates**
76. **#203 Mobility Ecologies**
77. **#205 Metropolitan Regions**
78. **#228 Strategic Maritime Layer**
79. **#237 Simulation-Driven Narrative Events**
80. **#10 Household Needs**

## A Tier - High Value

81. **#2 Migration**
82. **#4 Dynamic Culture**
83. **#76 Research Ecosystems**
84. **#79 Engineering vs. Science**
85. **#116 Doctrine**
86. **#117 Mobilization Has Economic Consequences**
87. **#118 War Weariness Is Social**
88. **#119 Occupation Is Governance**
89. **#120 Resistance and Collaboration Are Political**
90. **#121 Reconstruction and Reintegration**
91. **#103 Peace Conferences**
92. **#107 Federations and Power Blocs**
93. **#109 International Law**
94. **#112 Protectorates, Subjects, and Autonomy**
95. **#105 Domestic Foreign-Policy Lobbies**
96. **#111 Non-State Actors**
97. **#16 Public Mandates and Promises**
98. **#20 Federalism and Autonomy**
99. **#24 Political Capital**
100. **#25 Revolutions with Negotiated Outcomes**
101. **#31 Historical Claims**
102. **#36 Crises Create Opportunities**
103. **#43 Institutional Networks**
104. **#46 Maintenance and Decay**
105. **#54 Firms and Entrepreneurship**
106. **#56 Foreign Investment**
107. **#58 Debt and Credit**
108. **#62 Strategic Reserves**
109. **#65 Rivers as Major Systems**
110. **#67 Hydrology**
111. **#68 Electricity as a Resource**
112. **#69 Energy Transitions**
113. **#71 Standards and Interoperability**
114. **#74 Competing Technology Paths**
115. **#80 Open Knowledge, Patents, and Secrecy**
116. **#82 Brain Drain and Brain Gain**
117. **#84 Dynamic Religion**
118. **#86 Ideologies Emerge from Conditions**
119. **#87 Public Sphere and Media**
120. **#88 Information Reliability**
121. **#94 Maps Can Be Wrong or Outdated**
122. **#127 Public Health**
123. **#129 Pollution**
124. **#131 Disaster Recovery**
125. **#137 Empire-Wide Queues and Templates**
126. **#138 Batch Decisions**
127. **#140 Advisor Recommendations with Reasons**
128. **#146 AI Memory**
129. **#149 AI Uses Delegation Too**
130. **#151 Dynamic Historical Objectives**
131. **#152 Civilization Ambitions**
132. **#155 Make Losing Fun**
133. **#160 Procedural Chronicle**
134. **#161 Historical Maps**
135. **#166 Great People Emerge from the Simulation**
136. **#170 Nationality-Specific Technology Ecosystems**
137. **#172 Traditions Persist Through Transformation**
138. **#183 Future Projection**
139. **#184 Compare Policies Before Enacting**
140. **#195 Simultaneous Planning**

## B Tier - Strong Additions

141. **#197 Observer / Spectator / AI Civilization Mode**
142. **#201 Resource Depletion**
143. **#202 Material Substitution and Recycling**
144. **#204 Living Oceans**
145. **#210 Municipal Government**
146. **#212 Professional Civil Service**
147. **#213 Systemic Corruption**
148. **#214 Internal Fog of Government**
149. **#215 Citizenship and Legal Status**
150. **#216 Civil Society and Social Movements**
151. **#218 Skills and Qualifications**
152. **#219 Service Economies**
153. **#223 Non-Territorial Power**
154. **#224 Colonial Governance and Decolonization**
155. **#225 Frontier Societies**
156. **#226 Diplomatic Corps**
157. **#229 Strategic Airspace Layer**
158. **#230 Secularization and Religious Pluralism**
159. **#232 Religious Social Institutions**
160. **#233 Cultural Movements**
161. **#243 Shareable Seeds and Historical Worlds**
162. **#3 Diasporas**
163. **#5 Hybrid Cultures**
164. **#6 Languages**
165. **#7 Demographic Transition**
166. **#8 Social Mobility**
167. **#9 Inequality**
168. **#12 Political Parties and Coalitions**
169. **#18 Regional Government**
170. **#21 Succession and Constitutional Transition**
171. **#22 Generational Leaders**
172. **#23 Cabinets and Advisors**
173. **#29 Voluntary Unions**
174. **#39 Urban Form**
175. **#40 Housing and Land Markets**
176. **#42 Institutional Reputation**
177. **#44 Wonders as Living Institutions**
178. **#45 Multi-Stage Great Projects**
179. **#47 Postwar Reconstruction**
180. **#51 Trade Corridors**
181. **#52 Economic Chokepoints**
182. **#55 Corporations as Transnational Actors**
183. **#59 Banking and Financial Crises**
184. **#60 Currencies and Monetary Blocs**
185. **#61 Economic Cycles**
186. **#66 Navigable Rivers**
187. **#72 Infrastructure as Soft Power**
188. **#77 Competing Schools of Thought**
189. **#78 Scientific Uncertainty**
190. **#83 Collaborative Global Science**
191. **#85 Schisms and Reforms**
192. **#89 Propaganda and Counter-Narratives**
193. **#90 Cultural Works with Provenance**
194. **#91 World Fairs, Festivals, and International Events**
195. **#92 Prestige Has Multiple Sources**
196. **#95 Exploration Expeditions**
197. **#96 Scientific Exploration**
198. **#114 Orders as a Scarce Strategic Resource**
199. **#115 Commanders and Institutional Military Memory**
200. **#123 Land Use**

## C Tier - Valuable, But Later or More Specialized

201. **#125 Crop and Food Diversity**
202. **#128 Ecosystem Services**
203. **#130 Environmental Restoration**
204. **#147 AI Can Misjudge**
205. **#148 AI Personalities Should Change Strategy, Not Sanity**
206. **#153 Historical Achievements Instead of Winner-Takes-All**
207. **#154 Multiple Measures of Success**
208. **#156 Graceful Concession**
209. **#157 Post-Victory Sandbox**
210. **#162 City Timelines**
211. **#164 National Memory**
212. **#165 Historical Reputation**
213. **#167 Rivalries Between Historical Figures and Institutions**
214. **#174 Orbital Infrastructure**
215. **#175 Space as Global Infrastructure**
216. **#177 Automation and Labor Transformation**
217. **#178 Digital Economy**
218. **#179 Global Commons**
219. **#180 Future Technology Remains Branching**
220. **#181 Searchable History**
221. **#185 Historical Baseline Comparison**
222. **#186 Automatic Map Annotations**
223. **#187 Named Wars and Crises**
224. **#190 Historical Reconciliation**
225. **#194 Asynchronous Civilization**
226. **#196 Shared-Civilization Co-op**
227. **#206 Commuting and Congestion**
228. **#207 Public Transportation**
229. **#208 Land Value and Redevelopment**
230. **#209 Rural Hinterlands**
231. **#221 Technological Obsolescence**
232. **#227 Summits and Conferences**
233. **#231 Pilgrimage and Sacred Geography**
234. **#234 Everyday Culture**
235. **#235 Living Architectural Identity**
236. **#238 Newspapers / Historical Reports**
237. **#244 Procedural Scenario Generator**
238. **#30 Emergent Civilization Names**
239. **#97 Archaeology from Actual History**
240. **#163 Artifact Provenance**
241. **#168 Player-Defined Historical Markers**
242. **#176 Off-World Projects**
243. **#188 Named Infrastructure**
244. **#189 Memorials and Commemoration**
245. **#236 Historically Reactive Music**

## Ranking Interpretation

The top of the ranking is deliberately infrastructure-heavy. Population, logistics, markets, administration, automation, AI, dynamic technology, historical persistence, diplomacy, and scalable simulation make large portions of the remaining backlog possible.

The key dependency pattern is:

```text
Dynamic Population
       |
       +-- Labor Markets
       +-- Migration
       +-- Politics
       +-- Religion
       +-- Culture
       +-- Education
       +-- Military manpower
       +-- Inequality
       `-- Urbanization

Production Chains + Markets
       |
       +-- Trade
       +-- Logistics
       +-- Firms
       +-- Employment
       +-- Prices
       +-- Diplomacy
       +-- War
       `-- Geography

Attention + Automation
       |
       `-- makes all of the above playable
```

The ranking should therefore **not** be treated as a literal build order. A dependency-aware implementation roadmap should sequence prerequisites ahead of dependent features even when the dependent feature is ranked higher in overall importance.

The experience target is to replace late-game chores such as:

```text
move 73 units
choose production in 28 cities
renew 14 trade routes
dismiss 19 routine notifications
```

with strategic questions such as:

```text
Should we federalize the eastern provinces?
Can our industrial economy survive losing access to the Southern Strait?
Should we intervene in the collapsing neighboring empire?
Do we sacrifice short-term growth to electrify the national rail network?
Should we accept foreign researchers fleeing a rival?
Can we prevent the alliance system from turning this regional dispute into a continental war?
```

That distinction should guide future reprioritization of the backlog.