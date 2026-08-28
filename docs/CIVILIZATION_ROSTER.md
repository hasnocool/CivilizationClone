# Planned Civilization Roster

## Purpose

This document defines the historical civilization/faction candidates that CivilizationClone can draw from after the proof of concept, and identifies a smaller set that is useful for exercising the demo ruleset.

For project terminology, **civilization** or **faction** is preferred over nationality because several candidates represent historical empires, kingdoms, confederations, or city-state cultures rather than modern nation-states.

The roster is a gameplay/content plan, not a claim that a people had fixed innate traits. Civilization-specific mechanics must be grounded in historically associated institutions, engineering, infrastructure, trade patterns, military organization, geography, or knowledge traditions. They must never encode race, ethnicity, or nationality as an inherent biological advantage.

The project must continue to use original rules text, original balance, original ability names, and original content data. Historical facts are reference material; proprietary Civilization-series faction abilities, Civilopedia text, balance values, artwork, leaders, or other protected content must not be copied.

Technology specializations in this project are also **not claims of exclusive invention**. Knowledge moved between societies constantly. A heritage technology means that the ruleset chooses to emphasize a historically relevant specialization for gameplay.

---

## Design model

Every historical civilization should use the same engine contracts and receive its identity through data-driven content:

1. the shared universal technology tree;
2. one civilization-specific heritage technology branch;
3. civilization modifiers expressed through the generic effect pipeline;
4. optional unique unit, building, infrastructure, or improvement definitions later;
5. AI research preferences that use public ruleset data rather than bespoke code;
6. no civilization-specific `if civilization == ...` logic in the engine.

The detailed technology branches are defined in [`TECHNOLOGY_TREES.md`](TECHNOLOGY_TREES.md).

### Roster selection criteria

A civilization is a good addition when it contributes several of the following:

- a distinct map or terrain interaction;
- a distinct economic or logistics problem;
- a distinct research specialization;
- a different military or mobility pattern;
- a different settlement-development pattern;
- a different trade or knowledge-network pattern;
- useful balance contrast with existing factions;
- geographic and historical breadth across the total roster;
- mechanics that can be represented by reusable engine systems rather than bespoke scripting.

Avoid adding two factions at the same time if they fill almost exactly the same mechanical niche. Add the one that exercises more engine systems first, then revisit the other after the content model has enough depth to differentiate them properly.

---

## Planned roster

The roster is intentionally staged. **Wave 0 is the demo candidate pool**, not a requirement to ship all six immediately. The first implementation should select four civilizations, then add the remaining two after simulation balance and AI research behavior are stable.

| Wave | Civilization id | Display identity | Primary gameplay identity | Heritage-technology theme |
| --- | --- | --- | --- | --- |
| 0 | `egyptian` | Egyptian kingdoms | river growth, storage, large construction | basin irrigation, river transport, quarry logistics |
| 0 | `roman` | Roman Republic/Empire | roads, infrastructure, frontier logistics | surveying, concrete, aqueducts, bridges, harbors |
| 0 | `han_chinese` | Han-era Chinese states | technical standardization, archives, canals | cast iron, paper, crossbows, canals, direction finding |
| 0 | `maya` | Maya city-states | water management, dense cities, astronomy | cisterns, raised fields, records, calendars, reservoirs |
| 0 | `malian` | Mali Empire | long-distance trade, markets, scholarship | wells, caravans, gold assay, manuscripts, river trade |
| 0 | `mongol` | Mongol Empire | extreme mobility, remounts, relay logistics | composite bows, herd systems, route mapping, siege adaptation |
| 1 | `greek` | Hellenic city-states | maritime reach, mathematics, applied mechanics | triremes, geometry, cranes, torsion mechanics, navigation |
| 1 | `persian` | Achaemenid/Sasanian-inspired Persia | arid infrastructure, roads, administrative logistics | qanats, relay routes, weights, caravan stations |
| 1 | `indian` | Classical Indian polities | waterworks, mathematics, metallurgy, monsoon trade | stepwells, numerical methods, crucible steel, navigation |
| 1 | `japanese` | Japanese historical states | terrain-efficient settlement, craft specialization, fortification | terracing, smelting, joinery, land survey, fortification |
| 1 | `inca` | Inca Empire | mountain infrastructure, storage, vertical terrain | terraces, rope bridges, roads, quipu, highland storage |
| 1 | `norse` | Norse/Scandinavian societies | cold-water mobility, exploration, coastal trade | clinker hulls, riveting, wayfinding, provisioning |
| 2 | `mexica` | Mexica/Aztec Empire | lake-city productivity, markets, dense provisioning | chinampas, canoe freight, causeways, aqueducts, market systems |
| 2 | `abbasid` | Abbasid-era caliphate | research networks, mathematics, medicine, trade | paper workshops, translation, algebra, astrolabes, institutions |
| 2 | `english` | Medieval/early-modern England | maritime industry, resource processing, dockyards | wool finishing, deep-keel ships, coal drainage, dry docks |
| 2 | `ottoman` | Ottoman Empire | artillery engineering, urban works, combined logistics | gun casting, shipyards, dome engineering, water systems, charts |

---

## Wave 0 — demo candidate pool

### Egyptian kingdoms — `egyptian`

**Why it belongs in the demo:** exercises rivers, food storage, terrain-conditioned yields, transport, and high-production construction.

**Strategic identity:** turn a river corridor into an exceptionally reliable settlement network. The faction should be strong at converting river access into food, transport, and construction capacity, but weaker when forced to expand far from water.

**Systems exercised:** river/floodplain tags, terrain yield modifiers, storage, infrastructure production, movement modifiers, construction unlocks.

### Roman Republic/Empire — `roman`

**Why it belongs in the demo:** is an excellent test of reusable infrastructure mechanics.

**Strategic identity:** connect settlements and armies with roads, bridges, camps, aqueducts, and ports. The strength should come from network effects and reduced logistical friction rather than a flat combat bonus.

**Systems exercised:** route movement, build-cost modifiers, settlement infrastructure, fortification, harbor construction, logistics.

### Han-era Chinese states — `han_chinese`

**Why it belongs in the demo:** combines production, knowledge infrastructure, engineering, and standardized equipment.

**Strategic identity:** scale efficiently by improving workshops, administrative knowledge storage, canals, and standardized military production.

**Systems exercised:** production modifiers, research modifiers, archives, canals, unit production, exploration/navigation bonuses.

### Maya city-states — `maya`

**Why it belongs in the demo:** proves that strong cities do not require river-only design and creates a very different water-management puzzle from Egypt.

**Strategic identity:** build productive compact settlements by storing water, improving difficult land, and investing in mathematical/astronomical knowledge.

**Systems exercised:** non-river water infrastructure, dense settlement bonuses, research unlocks, causeways, reservoir capacity.

### Mali Empire — `malian`

**Why it belongs in the demo:** exercises trade, gold/resource processing, desert traversal, and knowledge-network mechanics.

**Strategic identity:** make distant settlements economically coherent through caravan routes, market standards, river ports, and manuscript-based scholarship.

**Systems exercised:** trade capacity, route range, resource value modifiers, desert logistics, research from commerce.

### Mongol Empire — `mongol`

**Why it belongs in the demo:** creates the strongest contrast with infrastructure-heavy factions and pressure-tests movement/combat logistics.

**Strategic identity:** maintain mobile armies over very long distances through remounts, relay stations, route knowledge, and adapted siege craft. Mobility must be earned through terrain/logistics systems, not unconditional extra actions.

**Systems exercised:** movement, mounted-unit support, supply/logistics, map knowledge, relay infrastructure, siege unlocks.

---

## Wave 1 — first expansion set

### Hellenic city-states — `greek`

Maritime engineering and applied mathematics. The heritage branch should convert scholarship into practical naval, construction, and mechanical advantages rather than simply granting generic Science.

### Persian empires — `persian`

Arid-land engineering and long-distance state logistics. Qanat-like waterworks, surveyed routes, relay stations, standardized weights, and mountain-pass engineering create a resilient inland network.

### Classical Indian polities — `indian`

Water engineering, metallurgy, computation, astronomy, and monsoon navigation. This faction should reward combining urban infrastructure with knowledge and trade rather than specializing in only one yield.

### Japanese historical states — `japanese`

Efficient use of constrained terrain, highly developed craft production, coastal transport, timber engineering, survey, and layered fortifications.

### Inca Empire — `inca`

A mountain-focused infrastructure faction. Terraces, bridges, roads, storage, accounting, and relay systems should make difficult elevation and fragmented terrain economically viable.

### Norse/Scandinavian societies — `norse`

A cold-coast exploration and commerce faction. Ship construction, repairability, shallow-draft landings, long-distance wayfinding, and expedition provisioning are the core identity.

---

## Wave 2 — second expansion set

### Mexica/Aztec Empire — `mexica`

Lake agriculture, canoe freight, causeways, aqueducts, market organization, and capital provisioning. It should excel at turning lakeshore terrain and dense settlement networks into productivity.

### Abbasid-era caliphate — `abbasid`

Knowledge transmission and applied scholarship. Paper production, translation institutions, mathematical methods, astronomical instruments, medical institutions, irrigation literature, and caravan infrastructure form a research/trade network.

### Medieval/early-modern England — `english`

Resource processing and maritime industry. Wool finishing, harbor engineering, deep-keel vessels, mining drainage, navigation tables, dry docks, and integrated dockyards build toward an industrial maritime economy.

### Ottoman Empire — `ottoman`

Large-scale artillery, shipbuilding, urban engineering, cartography, and combined logistics. It should reward coordinated military and infrastructure investment rather than a simple unit-strength modifier.

---

## Demo implementation recommendation

Implement these four first:

1. `egyptian` — terrain-conditioned economy and storage;
2. `roman` — infrastructure and network logistics;
3. `maya` — alternate water-management and knowledge path;
4. `mongol` — high-mobility military/logistics contrast.

Then add `han_chinese` and `malian` once the first simulation balance pass is stable.

This four-faction slice deliberately covers four very different engine stresses: river economy, infrastructure networks, compact non-river urbanism, and mobile expansion.

---

## Content contract for every civilization

Before a civilization is considered implemented, its content pack should define:

- stable civilization id and display name;
- historical framing note and time-range intent;
- gameplay identity and explicit weaknesses/tradeoffs;
- heritage technology branch;
- starting-bias tags if the ruleset uses them;
- modifiers using the generic effect system;
- AI flavor/preferences for research, settlement, economy, and military priorities;
- at least one content hook for a later unique unit/building/improvement, even if the asset is not implemented yet;
- localization-ready player-facing names/descriptions;
- deterministic validation tests;
- balance telemetry labels.

### Required balance guardrails

- No civilization receives a permanent unconditional bonus to every major yield.
- A civilization's strongest bonus must have a map, infrastructure, timing, or opportunity-cost dependency.
- Every heritage branch must contain at least one economic/infrastructure choice and one strategic or military/mobility choice.
- Heritage technologies should unlock capabilities or conditional modifiers more often than flat percentage bonuses.
- A branch must not invalidate the shared technology tree.
- The AI must be able to value branch technologies using data, without a civilization-specific planning algorithm.
- Simulation reports should compare win rate, research completion timing, settlement count, yield curves, map control, military losses, and victory timing by civilization.

---

## Expansion sequencing

### Expansion phase E0 — heritage-tech framework

- add technology availability rules;
- add `heritage`/civilization tags;
- expose shared vs heritage technologies through ruleset APIs;
- validate prerequisites across shared and heritage graphs;
- add AI valuation metadata;
- preserve deterministic research choice/replay.

### Expansion phase E1 — four-faction demo

Implement `egyptian`, `roman`, `maya`, and `mongol` with their full heritage branches. Run bot-vs-bot matrices on identical seeds and map settings.

### Expansion phase E2 — six-faction demo

Add `han_chinese` and `malian`, then verify that knowledge/trade-heavy strategies compete with military and infrastructure strategies.

### Expansion phase E3 — Wave 1

Add `greek`, `persian`, `indian`, `japanese`, `inca`, and `norse` in small batches so balance regressions can be attributed to a specific addition.

### Expansion phase E4 — Wave 2

Add `mexica`, `abbasid`, `english`, and `ottoman` after naval, trade, artillery/siege, and richer infrastructure systems exist.

---

## Acceptance criteria for the roster plan

The expansion roster is ready to implement when:

- every planned civilization has a complete heritage branch in `TECHNOLOGY_TREES.md`;
- every branch forms an acyclic prerequisite graph;
- every branch depends on shared technologies instead of replacing basic human development with isolated faction-only research;
- each civilization has a materially different strategic identity;
- effects can be represented by reusable rules/modifier systems;
- historical framing avoids exclusive-invention claims and essentialist national traits;
- all content remains original and independent of proprietary Civilization-series data;
- implementation can be delivered as versioned ruleset content without changing client contracts.
