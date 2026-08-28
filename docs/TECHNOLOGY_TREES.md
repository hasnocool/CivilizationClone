# Civilization Technology Trees

## Purpose

This document defines an original technology-tree plan for the historical civilizations listed in [`CIVILIZATION_ROSTER.md`](CIVILIZATION_ROSTER.md).

The design deliberately does **not** reproduce a Civilization-series technology tree, technology descriptions, costs, unlock tables, or balance. It uses the engine model already planned for CivilizationClone: a generic directed acyclic research graph with data-driven unlocks and modifiers.

The core design is:

```text
shared technologies
        +
heritage branch for selected civilization
        =
that player's available research graph
```

A heritage technology is a gameplay specialization, not a claim that a society exclusively invented the underlying idea. Technologies, engineering methods, institutions, and scientific knowledge routinely moved between cultures. The branch simply emphasizes historically relevant areas in an original ruleset.

---

## 1. Research-tree architecture

### Shared tree

All civilizations research from the same shared foundation. Shared technologies represent broadly transferable capabilities needed by the engine and keep the game readable across factions.

### Heritage branches

Each civilization adds an eight-node heritage branch. Heritage nodes:

- may require shared technologies;
- may require earlier nodes in the same heritage branch;
- may unlock units, buildings, improvements, routes, or generic modifiers;
- should emphasize conditional capabilities rather than unconditional global bonuses;
- must remain a DAG;
- are normally available only to their owning civilization in the standard historical ruleset;
- can be made globally available by custom/mod rulesets later.

### Prerequisite semantics

Unless a future schema explicitly introduces `any_of`, every prerequisite listed for a technology is an **AND** requirement.

### Effect semantics

Effects below are design intent, not final balance numbers. Implementation should express them through reusable effect/modifier definitions such as:

- terrain yield modifiers;
- movement-cost modifiers;
- construction/production modifiers;
- storage modifiers;
- trade range/capacity modifiers;
- visibility/exploration modifiers;
- unit/building/improvement unlocks;
- research modifiers with clear conditions;
- settlement defense/logistics modifiers.

Do not implement heritage effects as civilization-specific engine conditionals.

---

## 2. Shared foundation tree

The POC can start with a subset of this tree. The expansion content can progressively enable the rest without changing the research engine.

| Technology id | Requires | Role |
| --- | --- | --- |
| `core.agriculture` | — | food production and basic farming |
| `core.stoneworking` | — | worked stone and early construction |
| `core.animal_husbandry` | — | managed herds and mounted-development prerequisite |
| `core.sailing` | — | basic water movement and coastal transport |
| `core.writing` | — | records, research, administration prerequisite |
| `core.irrigation` | `core.agriculture` | controlled water for farming |
| `core.mining` | `core.stoneworking` | mineral extraction |
| `core.trade` | `core.agriculture` | organized exchange and route systems |
| `core.metallurgy` | `core.mining` | metal tools, weapons, and workshops |
| `core.construction` | `core.stoneworking` | larger permanent structures |
| `core.mathematics` | `core.writing` | formal calculation and engineering prerequisite |
| `core.administration` | `core.writing`, `core.trade` | larger settlement/empire coordination |
| `core.engineering` | `core.construction`, `core.mathematics` | advanced infrastructure |
| `core.currency` | `core.trade`, `core.mathematics` | standardized exchange and treasury systems |
| `core.fortification` | `core.construction`, `core.metallurgy` | stronger defensive works |
| `core.scholarship` | `core.writing`, `core.mathematics` | organized advanced research |
| `core.navigation` | `core.sailing`, `core.mathematics` | reliable long-distance water travel |
| `core.gunpowder` | `core.metallurgy`, `core.scholarship` | early gunpowder equipment and artillery prerequisite |
| `core.banking` | `core.currency`, `core.administration` | advanced finance/trade systems |
| `core.scientific_method` | `core.scholarship`, `core.administration` | later systematic research |
| `core.oceanic_navigation` | `core.navigation`, `core.scholarship` | sustained ocean-range travel |

### Recommended demo subset

For the first heritage-tree demo, enable enough shared prerequisites to support the selected factions rather than enabling every advanced common technology immediately. A practical first slice is:

```text
Agriculture ──> Irrigation
Stoneworking ──> Mining ──> Metallurgy
      └───────> Construction ──┐
Writing ──────> Mathematics ───┴─> Engineering
   └──────────> Administration
Sailing
Trade
```

---

# 3. Wave 0 heritage trees

## 3.1 Egyptian kingdoms — `egyptian`

**Design goal:** turn river access into reliable food, storage, mobility, and high-capacity construction. The branch becomes less valuable on maps without meaningful river/floodplain access.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `egyptian.basin_irrigation` | `core.irrigation` | unlock basin-style river farming improvement; conditional Food on river/floodplain tiles |
| `egyptian.quarry_sledges` | `core.stoneworking` | improve quarry/stone-resource production and heavy-construction logistics |
| `egyptian.nilometer_surveying` | `egyptian.basin_irrigation`, `core.mathematics` | improve river-settlement planning; unlock survey infrastructure tied to river tiles |
| `egyptian.river_barges` | `egyptian.basin_irrigation`, `core.sailing` | reduce friendly river-corridor transport friction and improve river trade capacity |
| `egyptian.monumental_lifting` | `egyptian.quarry_sledges`, `core.engineering` | improve production efficiency for large civic/infrastructure projects |
| `egyptian.granary_accounting` | `egyptian.nilometer_surveying`, `core.administration` | increase food-storage efficiency and reduce growth loss from storage caps |
| `egyptian.desert_waystations` | `egyptian.river_barges`, `core.trade` | extend trade/logistics through arid tiles when linked to developed settlements |
| `egyptian.hydraulic_stateworks` | `egyptian.monumental_lifting`, `egyptian.granary_accounting`, `egyptian.desert_waystations` | capstone river-infrastructure network: stronger connected irrigation/storage/transport effects |

Logical shape:

```text
Basin Irrigation -> Nilometer Surveying -> Granary Accounting ----┐
       └---------> River Barges -> Desert Waystations ------------┤
Quarry Sledges -> Monumental Lifting ------------------------------┴-> Hydraulic Stateworks
```

## 3.2 Roman Republic/Empire — `roman`

**Design goal:** create value by connecting settlements and military fronts through durable infrastructure.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `roman.road_bedding` | `core.construction` | unlock improved road segments with lower friendly movement cost |
| `roman.cadastral_survey` | `core.writing`, `core.construction` | improve territory/infrastructure planning and reduce route/improvement placement cost |
| `roman.concrete_mixes` | `core.construction`, `core.metallurgy` | unlock durable masonry/concrete infrastructure class and building-production modifiers |
| `roman.marching_camps` | `roman.road_bedding`, `core.fortification` | unlock temporary/limited frontier camp infrastructure for army support |
| `roman.aqueduct_gradients` | `roman.cadastral_survey`, `core.engineering` | unlock aqueduct infrastructure and improve inland settlement growth capacity |
| `roman.bridge_corps` | `roman.road_bedding`, `core.engineering` | reduce river-crossing penalties on improved routes; unlock major bridge works |
| `roman.harbor_caissons` | `roman.concrete_mixes`, `core.sailing`, `core.engineering` | improve harbor construction and coastal logistics |
| `roman.integrated_logistics` | `roman.marching_camps`, `roman.aqueduct_gradients`, `roman.bridge_corps`, `roman.harbor_caissons`, `core.administration` | capstone network bonus for settlements/armies connected by developed infrastructure |

## 3.3 Han-era Chinese states — `han_chinese`

**Design goal:** reward standardized production, information storage, and engineered transport networks.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `han_chinese.standardized_crossbow_parts` | `core.metallurgy` | unlock standardized crossbow equipment/unit path; improve ranged-unit production consistency |
| `han_chinese.cast_iron_workshops` | `core.metallurgy`, `core.construction` | improve workshop/tool production and infrastructure build throughput |
| `han_chinese.paper_workshops` | `core.writing`, `core.trade` | unlock paper-workshop knowledge infrastructure; conditional research/administration efficiency |
| `han_chinese.canal_grading` | `core.irrigation`, `core.engineering` | unlock canal infrastructure and improve movement/trade between connected waterways |
| `han_chinese.wheelbarrow_logistics` | `han_chinese.cast_iron_workshops`, `core.construction` | reduce local infrastructure logistics cost and improve overland supply efficiency |
| `han_chinese.civil_archives` | `han_chinese.paper_workshops`, `core.administration` | improve research/administration in developed settlements with archive infrastructure |
| `han_chinese.magnetic_direction_finding` | `han_chinese.cast_iron_workshops`, `core.scholarship`, `core.navigation` | improve exploration reliability and water-route visibility/range |
| `han_chinese.state_engineering_bureaus` | `han_chinese.canal_grading`, `han_chinese.wheelbarrow_logistics`, `han_chinese.civil_archives`, `han_chinese.magnetic_direction_finding` | capstone coordination bonus for workshops, canals, and knowledge infrastructure |

## 3.4 Maya city-states — `maya`

**Design goal:** support compact productive cities through stored water, intensive land use, records, and astronomy.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `maya.limestone_cisterns` | `core.stoneworking`, `core.irrigation` | unlock cistern infrastructure that supports settlements away from rivers |
| `maya.raised_field_cultivation` | `core.agriculture`, `core.irrigation` | improve Food on suitable wet/lowland tiles with developed farming |
| `maya.lime_plaster_kilns` | `core.stoneworking`, `core.construction` | improve dense urban construction and stone-building production |
| `maya.vigesimal_records` | `core.writing`, `core.mathematics` | unlock specialized recordkeeping; conditional Science/administration from developed cities |
| `maya.calendrical_tables` | `maya.vigesimal_records`, `core.scholarship` | improve research timing/seasonal planning effects and unlock astronomy infrastructure |
| `maya.sacbe_causeways` | `maya.lime_plaster_kilns`, `core.engineering` | unlock causeway routes that improve movement between nearby developed settlements |
| `maya.reservoir_networks` | `maya.limestone_cisterns`, `maya.raised_field_cultivation`, `core.engineering` | improve stored-water capacity and urban growth in water-limited terrain |
| `maya.observatory_complexes` | `maya.calendrical_tables`, `maya.reservoir_networks`, `core.construction` | capstone knowledge/urban infrastructure bonus for compact developed settlement clusters |

## 3.5 Mali Empire — `malian`

**Design goal:** make distance economically useful through desert logistics, resource valuation, trade standards, and scholarship.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `malian.desert_well_chains` | `core.irrigation`, `core.trade` | unlock arid-route support improvements and extend viable caravan paths |
| `malian.gold_assaying` | `core.mining`, `core.trade` | improve Gold value from precious-metal resources and trade transactions |
| `malian.caravan_pack_systems` | `core.animal_husbandry`, `core.trade` | increase overland trade range/capacity across arid terrain |
| `malian.river_portage` | `core.sailing`, `core.trade` | improve transfer between river/coastal transport and land trade routes |
| `malian.mudbrick_thermal_design` | `core.construction`, `malian.desert_well_chains` | improve arid-settlement building efficiency and storage/resilience |
| `malian.manuscript_workshops` | `core.writing`, `core.scholarship`, `malian.gold_assaying` | convert developed trade/market activity into conditional research benefits |
| `malian.market_standards` | `core.currency`, `malian.gold_assaying`, `core.administration` | improve market/trade efficiency across connected settlements |
| `malian.trans_saharan_logistics` | `malian.caravan_pack_systems`, `malian.river_portage`, `malian.mudbrick_thermal_design`, `malian.manuscript_workshops`, `malian.market_standards` | capstone long-range commerce network with arid-route and knowledge synergies |

## 3.6 Mongol Empire — `mongol`

**Design goal:** create long-range military and strategic mobility through remounts, route knowledge, relays, and field logistics rather than free extra turns.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `mongol.composite_bow_lamination` | `core.animal_husbandry`, `core.metallurgy` | unlock advanced mounted-ranged equipment/unit path |
| `mongol.remount_herd_systems` | `core.animal_husbandry`, `core.trade` | reduce mobility attrition/logistics cost for mounted forces in supported terrain |
| `mongol.felt_camp_engineering` | `core.animal_husbandry`, `core.construction` | unlock mobile-camp support infrastructure with low setup cost |
| `mongol.relay_posts` | `mongol.remount_herd_systems`, `core.administration` | unlock relay network that improves command/logistics range along controlled routes |
| `mongol.steppe_route_mapping` | `mongol.relay_posts`, `core.mathematics` | improve overland exploration and path planning across open terrain |
| `mongol.siege_craft_adaptation` | `core.engineering`, `mongol.felt_camp_engineering` | unlock adapted siege-equipment production after appropriate common engineering |
| `mongol.field_veterinary_methods` | `mongol.remount_herd_systems`, `core.scholarship` | improve recovery/sustainment for mounted formations without increasing base action count |
| `mongol.continental_logistics` | `mongol.steppe_route_mapping`, `mongol.siege_craft_adaptation`, `mongol.field_veterinary_methods`, `mongol.relay_posts` | capstone movement/supply synergy across a developed relay network |

---

# 4. Wave 1 heritage trees

## 4.1 Hellenic city-states — `greek`

**Design goal:** turn mathematics and scholarship into practical maritime and mechanical engineering.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `greek.trireme_framing` | `core.sailing`, `core.construction` | unlock specialized fast oared-warship path and improve early naval construction |
| `greek.geometric_proofs` | `core.writing`, `core.mathematics` | improve engineering/research efficiency when mathematical infrastructure is present |
| `greek.precision_stone_dressing` | `greek.geometric_proofs`, `core.construction` | improve stone civic/infrastructure construction |
| `greek.torsion_mechanics` | `greek.geometric_proofs`, `core.metallurgy` | unlock torsion-engine military/engineering equipment path |
| `greek.harbor_cranes` | `greek.trireme_framing`, `core.engineering` | improve harbor throughput and coastal construction |
| `greek.celestial_navigation` | `greek.geometric_proofs`, `core.navigation`, `core.scholarship` | improve naval exploration/range and route reliability |
| `greek.water_clock_mechanisms` | `greek.torsion_mechanics`, `core.engineering` | unlock precision-mechanism knowledge buildings/modifiers |
| `greek.applied_mechanics` | `greek.harbor_cranes`, `greek.celestial_navigation`, `greek.water_clock_mechanisms`, `greek.precision_stone_dressing` | capstone synergy between scholarship, naval infrastructure, and mechanical construction |

## 4.2 Persian empires — `persian`

**Design goal:** make arid interiors and long land routes productive through water engineering and standardized logistics.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `persian.qanat_tunneling` | `core.irrigation`, `core.mining` | unlock underground-water infrastructure for arid settlements |
| `persian.royal_route_surveying` | `core.trade`, `core.construction` | improve long-distance road construction and route reliability |
| `persian.desert_surveying` | `persian.qanat_tunneling`, `core.mathematics` | improve arid-tile development and route planning |
| `persian.relay_stations` | `persian.royal_route_surveying`, `core.administration` | unlock relay infrastructure that extends communication/logistics range |
| `persian.standardized_weights` | `core.currency`, `core.writing` | improve market/trade consistency between connected settlements |
| `persian.garden_hydraulics` | `persian.qanat_tunneling`, `core.engineering` | improve urban water infrastructure and settlement amenity/growth hooks later |
| `persian.mountain_pass_engineering` | `persian.royal_route_surveying`, `core.engineering` | reduce route/movement penalties through developed hill/mountain passes |
| `persian.imperial_logistics` | `persian.relay_stations`, `persian.standardized_weights`, `persian.garden_hydraulics`, `persian.mountain_pass_engineering` | capstone network bonus across long connected inland routes |

## 4.3 Classical Indian polities — `indian`

**Design goal:** reward combining water engineering, computation, metallurgy, scholarship, and monsoon trade.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `indian.stepwell_hydraulics` | `core.irrigation`, `core.construction` | unlock deep water-storage infrastructure for seasonal/dry regions |
| `indian.cotton_finishing` | `core.agriculture`, `core.trade` | improve textile-resource processing and trade value |
| `indian.crucible_steel` | `core.metallurgy`, `core.construction` | unlock high-quality metal workshop/equipment path |
| `indian.place_value_computation` | `core.writing`, `core.mathematics` | improve advanced calculation/research and administrative efficiency |
| `indian.monsoon_navigation` | `core.sailing`, `core.navigation`, `indian.place_value_computation` | improve seasonal long-range maritime trade reliability/range |
| `indian.observatory_tables` | `indian.place_value_computation`, `core.scholarship` | improve astronomy/navigation research and knowledge infrastructure |
| `indian.urban_drainage` | `indian.stepwell_hydraulics`, `core.engineering` | improve dense-settlement growth/infrastructure capacity |
| `indian.precision_metallurgy` | `indian.crucible_steel`, `indian.place_value_computation`, `indian.observatory_tables`, `core.engineering` | capstone advanced workshop/equipment efficiency tied to developed knowledge centers |

## 4.4 Japanese historical states — `japanese`

**Design goal:** make constrained terrain and carefully developed settlements efficient through agriculture, craft production, survey, and layered defenses.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `japanese.paddy_terracing` | `core.agriculture`, `core.irrigation` | improve Food from developed hill/river-valley farming where valid |
| `japanese.tatara_smelting` | `core.metallurgy` | unlock specialized iron/steel workshop path and equipment-production modifiers |
| `japanese.coastal_craft` | `core.sailing`, `core.construction` | improve short-range coastal transport and fishing/harbor development |
| `japanese.timber_joinery` | `core.construction`, `japanese.tatara_smelting` | improve timber-structure construction and repair efficiency |
| `japanese.castle_earthworks` | `japanese.timber_joinery`, `core.fortification` | unlock layered hill/settlement fortification improvements |
| `japanese.cadastral_land_survey` | `core.writing`, `core.mathematics`, `core.administration` | improve territory development/working efficiency in compact settlements |
| `japanese.matchlock_workshops` | `japanese.tatara_smelting`, `core.gunpowder` | unlock firearm workshop/unit path without replacing shared gunpowder research |
| `japanese.layered_fortification` | `japanese.castle_earthworks`, `japanese.cadastral_land_survey`, `japanese.matchlock_workshops`, `core.engineering` | capstone defensive/infrastructure synergy for developed terrain |

## 4.5 Inca Empire — `inca`

**Design goal:** turn difficult mountain geography into a connected economy through terraces, bridges, roads, storage, and accounting.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `inca.mountain_terraces` | `core.agriculture`, `core.stoneworking` | unlock productive hill/mountain-adjacent terrace improvements |
| `inca.rope_bridge_weaving` | `core.trade`, `core.construction` | unlock bridge infrastructure across defined ravine/river obstacles |
| `inca.fitted_stone_masonry` | `core.stoneworking`, `core.construction` | improve durable highland infrastructure and settlement defenses |
| `inca.highland_road_grading` | `inca.rope_bridge_weaving`, `core.engineering` | reduce movement/logistics cost on improved highland routes |
| `inca.quipu_accounting` | `core.mathematics`, `core.administration` | improve storage/logistics administration without requiring a writing-specific heritage node |
| `inca.qollqa_storage` | `inca.mountain_terraces`, `inca.quipu_accounting`, `core.construction` | unlock high-capacity distributed food/supply storage |
| `inca.relay_runner_stations` | `inca.highland_road_grading`, `inca.quipu_accounting` | improve command/trade/logistics range along highland routes |
| `inca.vertical_ecology_management` | `inca.qollqa_storage`, `inca.relay_runner_stations`, `inca.fitted_stone_masonry` | capstone bonus for networks spanning multiple elevation/terrain bands |

## 4.6 Norse/Scandinavian societies — `norse`

**Design goal:** support exploration and trade across cold coasts through robust, repairable, shallow-draft vessels and expedition logistics.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `norse.clinker_hulls` | `core.sailing`, `core.construction` | unlock robust shallow-draft ship class and improve early naval construction |
| `norse.iron_riveting` | `core.metallurgy`, `norse.clinker_hulls` | improve ship durability/repair and naval production efficiency |
| `norse.cold_weather_shipyards` | `norse.iron_riveting`, `core.construction` | improve harbor/ship production in cold/coastal settlements |
| `norse.open_ocean_wayfinding` | `norse.clinker_hulls`, `core.navigation` | improve sea exploration range and reduce navigation penalties |
| `norse.shallow_draft_landings` | `norse.clinker_hulls`, `core.engineering` | improve embark/disembark and river/coastal access for eligible vessels |
| `norse.north_atlantic_provisioning` | `norse.open_ocean_wayfinding`, `core.trade` | extend expedition/trade range when supplied from developed ports |
| `norse.modular_hull_repairs` | `norse.cold_weather_shipyards`, `core.engineering` | reduce repair downtime/cost for ships in friendly ports |
| `norse.long_range_seamanship` | `norse.north_atlantic_provisioning`, `norse.modular_hull_repairs`, `core.oceanic_navigation` | capstone long-range exploration/trade synergy without unconditional naval combat strength |

---

# 5. Wave 2 heritage trees

## 5.1 Mexica/Aztec Empire — `mexica`

**Design goal:** make lake systems and dense urban provisioning strategically powerful through agriculture, water transport, causeways, and markets.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `mexica.chinampa_beds` | `core.agriculture`, `core.irrigation` | unlock high-output lake-edge farming improvements on valid terrain |
| `mexica.obsidian_blade_workshops` | `core.mining`, `core.trade` | improve obsidian/resource processing and unlock specialized equipment path |
| `mexica.canoe_freight` | `core.sailing`, `core.trade` | improve lake/river cargo movement and local trade capacity |
| `mexica.lake_causeways` | `mexica.chinampa_beds`, `core.construction` | unlock causeway connections across valid shallow-water/lake terrain |
| `mexica.aqueduct_channels` | `core.irrigation`, `core.engineering` | improve urban water supply and settlement growth capacity |
| `mexica.market_standards` | `core.currency`, `core.administration`, `mexica.canoe_freight` | improve market throughput and resource exchange in dense settlement networks |
| `mexica.lake_defenses` | `mexica.lake_causeways`, `core.fortification` | improve defenses for settlements/approaches integrated with lake infrastructure |
| `mexica.capital_provisioning` | `mexica.chinampa_beds`, `mexica.aqueduct_channels`, `mexica.market_standards`, `mexica.lake_defenses` | capstone food/market/logistics synergy for dense lake-centered settlement clusters |

## 5.2 Abbasid-era caliphate — `abbasid`

**Design goal:** convert connected trade and knowledge institutions into strong applied research, navigation, medicine, and engineering.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `abbasid.paper_workshops` | `core.writing`, `core.trade` | unlock scalable manuscript/paper knowledge infrastructure |
| `abbasid.translation_houses` | `abbasid.paper_workshops`, `core.administration` | improve research when connected to trade/foreign-contact knowledge sources later |
| `abbasid.algebraic_methods` | `core.mathematics`, `abbasid.translation_houses` | improve engineering/economic calculation research paths |
| `abbasid.astrolabe_refinement` | `core.navigation`, `abbasid.algebraic_methods` | improve navigation/exploration and astronomy-related research |
| `abbasid.observatory_instruments` | `abbasid.astrolabe_refinement`, `core.scholarship` | unlock observatory knowledge infrastructure and advanced research modifiers |
| `abbasid.irrigation_treatises` | `core.irrigation`, `abbasid.paper_workshops`, `core.engineering` | improve dissemination/efficiency of irrigation infrastructure across settlements |
| `abbasid.caravanserai_networks` | `core.trade`, `core.currency`, `abbasid.translation_houses` | extend land trade/logistics and strengthen knowledge exchange along routes |
| `abbasid.medical_institutions` | `abbasid.observatory_instruments`, `abbasid.irrigation_treatises`, `abbasid.caravanserai_networks`, `core.scholarship` | capstone urban knowledge institution with population/recovery/research hooks |

## 5.3 Medieval/early-modern England — `english`

**Design goal:** build from resource processing into increasingly capable maritime industry and dockyard infrastructure.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `english.wool_fulling` | `core.agriculture`, `core.trade` | improve textile-resource processing and market value |
| `english.longbow_stavecraft` | `core.construction`, `core.metallurgy` | unlock specialized ranged-equipment/unit path tied to workshop capacity |
| `english.tidal_harbor_works` | `core.sailing`, `core.construction` | improve harbor production/capacity on suitable coasts |
| `english.deep_keel_hulls` | `english.tidal_harbor_works`, `core.navigation` | unlock larger ocean-capable vessel path |
| `english.coal_drainage` | `core.mining`, `core.engineering` | improve extraction from deep/industrial mineral sites and workshop fuel hooks |
| `english.dry_dock_systems` | `english.deep_keel_hulls`, `english.coal_drainage`, `core.engineering` | unlock advanced shipbuilding/repair infrastructure |
| `english.navigation_tables` | `core.scholarship`, `core.navigation`, `english.deep_keel_hulls` | improve long-range maritime route planning and exploration |
| `english.integrated_dockyards` | `english.dry_dock_systems`, `english.navigation_tables`, `core.oceanic_navigation`, `core.administration` | capstone maritime production/logistics network across developed ports |

## 5.4 Ottoman Empire — `ottoman`

**Design goal:** combine artillery engineering, shipbuilding, urban infrastructure, cartography, and logistics into coordinated state capacity.

| Technology id | Requires | Intended unlock/effect |
| --- | --- | --- |
| `ottoman.gun_casting` | `core.gunpowder`, `core.metallurgy` | unlock heavy gun/artillery workshop path |
| `ottoman.bombard_carriages` | `ottoman.gun_casting`, `core.engineering` | improve transport/deployment of eligible siege artillery |
| `ottoman.domed_load_paths` | `core.construction`, `core.mathematics` | improve large civic/urban building construction and unlock dome-engineering structures |
| `ottoman.caravan_bridgeworks` | `core.trade`, `core.engineering` | improve bridge/road logistics along inland commercial routes |
| `ottoman.imperial_shipyards` | `core.sailing`, `core.engineering`, `core.administration` | unlock high-capacity naval production/repair infrastructure |
| `ottoman.urban_water_distribution` | `core.irrigation`, `ottoman.domed_load_paths`, `core.engineering` | improve growth/infrastructure capacity in large settlements |
| `ottoman.chart_compilation` | `core.navigation`, `core.scholarship`, `ottoman.imperial_shipyards` | improve naval map knowledge, exploration, and route planning |
| `ottoman.combined_arms_logistics` | `ottoman.bombard_carriages`, `ottoman.caravan_bridgeworks`, `ottoman.imperial_shipyards`, `ottoman.chart_compilation`, `core.administration` | capstone logistics synergy for artillery, armies, roads, and fleets operating from developed networks |

---

# 6. Implementation schema recommendations

The existing generic `TechnologyDefinition` can remain the foundation, but expansion content will benefit from explicit metadata.

Suggested conceptual fields:

```yaml
id: egyptian.basin_irrigation
display_name: Basin Irrigation
era: early
cost_class: heritage_early
prerequisites:
  - core.irrigation
availability:
  civilization_ids:
    - egyptian
tags:
  - heritage
  - water
  - river
ai_flavors:
  economy: high
  growth: high
  infrastructure: medium
unlocks:
  - improvement: egyptian_basin_farm
modifiers:
  - type: terrain_yield
    # exact target/condition/value to be defined by the rules schema
```

The YAML above is a schema direction, not final balance or a requirement to adopt these exact field names.

### Validation requirements

Ruleset validation should reject:

- missing prerequisite ids;
- cycles;
- heritage nodes whose owning civilization does not exist;
- duplicate ids;
- impossible/unreachable nodes;
- unlock references to missing content;
- unsupported modifier types;
- invalid era/cost classes;
- contradictory availability rules.

Validation should also emit a machine-readable topological order for deterministic tests and client rendering.

---

# 7. AI research behavior

AI must not need a hard-coded strategy class for each civilization.

Each technology should expose generic AI flavor metadata. The bot can score available technologies using its current state and strategic goals, for example:

```text
technology score =
    unlock utility
  + current terrain synergy
  + settlement/economy need
  + military need
  + route/logistics need
  + victory-plan relevance
  - research opportunity cost
```

Examples:

- an Egyptian bot with multiple river settlements values `basin_irrigation` and `river_barges` more highly;
- a Mongol bot with mounted forces and a wide empire values `relay_posts` and `field_veterinary_methods`;
- a Norse bot on an inland map should de-prioritize ocean-heavy nodes instead of blindly following the heritage branch;
- an Abbasid bot with strong trade connectivity can value translation/caravan knowledge synergies.

This keeps AI behavior emergent from ruleset data and map state.

---

# 8. Demo build order

For the first four-faction heritage demo:

### Stage 1 — shared prerequisites

Implement/verify the shared technologies needed by `egyptian`, `roman`, `maya`, and `mongol`.

### Stage 2 — first two contrasting branches

Implement:

- `egyptian` — economy/water/construction;
- `mongol` — mobility/logistics/military support.

This immediately tests whether the same research engine can support radically different effects.

### Stage 3 — infrastructure and compact-city branches

Implement:

- `roman` — routes/infrastructure;
- `maya` — water storage/urban knowledge.

### Stage 4 — data-driven AI

Teach the generic bot research scorer to consume technology flavor/effect metadata and run identical seeded maps with each faction.

### Stage 5 — expand to six factions

Add:

- `han_chinese` — workshops/archives/canals;
- `malian` — trade/desert/scholarship.

---

# 9. Balance and simulation requirements

Every added heritage branch should enter automated simulation before being considered stable.

Record at minimum:

- technologies completed by turn;
- average research completion turn by node;
- technologies skipped;
- settlement count and population curve;
- Food/Production/Gold/Science curves;
- route/trade activity;
- unit count and losses;
- controlled territory;
- victory type and turn;
- win rate by civilization;
- win rate by map archetype;
- invalid research selections;
- AI turns with no legal/selected research;
- replay/state-hash consistency.

### Balance expectations

- Heritage branches should create **different strong situations**, not a universal ranking.
- Map generation should not guarantee every faction its perfect terrain, but start-normalization can prevent obviously nonviable starts.
- A heritage branch should usually have opportunity cost: researching it delays another shared or heritage technology.
- Early nodes should establish identity; capstones should amplify a developed strategy rather than rescue a failed one for free.
- A branch should contain at least one node whose value is highly state-dependent so research order is a meaningful decision.

---

# 10. API/client requirements

Clients should be able to render research without embedding branch logic.

The ruleset/research API should expose, for each visible/available technology:

- id;
- localized display name/description;
- heritage/shared classification;
- era/tier;
- prerequisites;
- current progress/cost;
- locked/available/completed state;
- safe reason when locked;
- summarized unlocks/modifiers;
- owning civilization restrictions where appropriate.

The server remains authoritative for availability and completion.

A client should be able to draw the entire research DAG from returned metadata, including shared-to-heritage prerequisite edges.

---

# 11. Testing requirements

At minimum, add tests for:

1. every technology id is unique;
2. every prerequisite exists;
3. each combined shared + heritage graph is acyclic;
4. every heritage node is reachable for its civilization;
5. a different civilization cannot select an exclusive heritage node in the standard ruleset;
6. completing a prerequisite exposes newly legal nodes deterministically;
7. unlocks/modifiers activate exactly once;
8. save/reload preserves research state;
9. replay reproduces technology selections/completions exactly;
10. player projections do not leak hidden opponent research when rules hide it;
11. bots can finish games without getting stuck on a mandatory research choice;
12. the same seed + command stream yields the same research history and final state hash.

Property tests should generate valid small DAGs and verify topological ordering, reachability, and cycle rejection.

---

# 12. Definition of done for one heritage branch

A civilization's technology branch is complete when:

- all eight planned nodes are represented as versioned content data;
- shared prerequisites exist and are validated;
- all unlock/effect references resolve;
- the graph is acyclic and fully reachable;
- API projections expose correct choices and lock reasons;
- generic AI can select and complete the branch;
- focused unit/integration/replay tests pass;
- bot-vs-bot simulations complete on multiple deterministic seeds;
- balance telemetry shows no obvious unrecoverable advantage/disadvantage;
- the branch can be disabled or swapped by a ruleset without changing engine code;
- player-facing text remains original and historically careful.
