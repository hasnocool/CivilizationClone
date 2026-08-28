# Civ1 UI/UX Coverage Audit

The original 57-scene catalog was intentionally compact, but it compressed several distinct Civilization I UI states into single families. This audit expands the reference so client implementations can test and render every **distinct documented screen, menu, modal, subview, event report, or endgame presentation template** without creating a separate ID for every content instance (for example, every individual technology, leader, wonder, or unit type).

## Scope

The canonical target is the original DOS/IBM Civilization interaction model, supplemented by cross-port screenshots when they expose the same core state more clearly. Platform-only setup/window chrome is marked as such. The catalog does **not** treat each leader portrait, government-specific advisor costume, technology entry, wonder illustration, or generated city name as a separate scene; those are parameterized content variants of the same scene template.

## Primary evidence

- Civilization manual HTML: https://www.civfanatics.com/content/civ1/manual/civ1_man.htm
- Original PC manual PDF: https://www.gamesdatabase.org/Media/SYSTEM/Microsoft_DOS/Manual/formated/Sid_Meier-s_Civilization.pdf
- DOS screenshot catalog: https://www.mobygames.com/game/585/sid-meiers-civilization/screenshots/dos/
- Cross-platform screenshot catalog: https://www.mobygames.com/game/585/sid-meiers-civilization/screenshots/

## Gaps found in the original 57-scene pass

The first pass omitted or merged the following documented UI families:

1. startup/system states: credits, sound-driver choice, Game/World options, load-drive selection, competition level, ruler-name entry, and manual copy-protection quiz;
2. map menus and prompts: Game menu, Options submenu, separate tax/luxury dialogs, Find City, End of Turn, and Instant Advice;
3. periodic historian/adulation reports beyond the Palace screen;
4. unit interaction modes: unit-stack activation, Go To targeting, home-city reassignment, Settler context orders, and special Diplomat/Caravan outcomes;
5. city subviews: Info, Happy, Map, citizen reassignment, specialist assignment, rename, and city-unit activation;
6. multi-page reports: Military casualties and Intelligence details;
7. Civilopedia section selection and two-page entry presentation;
8. diplomacy states: peace offers, technology selection, buying peace, post-treaty negotiation, military proposals, treaty-breaking warnings, and Senate intervention;
9. world events: minor tribe outcomes, barbarian ransom, pollution, global warming, nuclear meltdown, disaster reports, wonder-race loss, and continued civil disorder;
10. space/endgame states: rival ship status, launch confirmation, ship-in-flight, rival launch/arrival, automatic history ending, continue-playing prompt, replay menu, quick/complete replay, replay export, and Powergraph;
11. resource/failure notifications: treasury shortfall, unsupported unit loss, city destruction/capture loot, nuclear result/SDI interception;
12. presentation states: palace improvement invitation, rival-wonder announcement, wonder obsolescence, and city advisor recommendation overlays.

## Canonical ID policy

`CIV1-UI-001` through `CIV1-UI-057` remain unchanged for backward compatibility. Newly identified states begin at `CIV1-UI-058`.

A state gets its own canonical ID when at least one of these is true:

- it changes the available player actions;
- it changes navigation/focus behavior;
- it is a distinct modal/report/page documented by the manual;
- it requires a different acceptance-test path;
- it is a distinct full-screen presentation or event notification.

Parameterized variants remain one scene when only the content changes. For example, all seven natural-disaster types use the same event-shell family but each still gets its own ID because the event semantics and expected text/result differ.

## Expanded layout files

The original files remain in place. Supplemental files cover the omitted states in both strict ASCII and enhanced ANSII form:

| Range | Category | ASCII | ANSII |
|---|---|---|---|
| 058-085 | startup, Game menu, turn/report states | `ascii/05_system_menus.ascii` | `ansii/05_system_menus.ansii` |
| 086-104 | units, Diplomats, Caravans, minor tribes | `ascii/06_units_special.ascii` | `ansii/06_units_special.ansii` |
| 105-130 | city subviews, disasters, advisor/Civilopedia pages | `ascii/07_city_events_reports.ascii` | `ansii/07_city_events_reports.ansii` |
| 131-142 | extended diplomacy | `ascii/08_diplomacy_extended.ascii` | `ansii/08_diplomacy_extended.ansii` |
| 143-168 | space race, replay, failure/presentation states | `ascii/09_space_replay_misc.ascii` | `ansii/09_space_replay_misc.ansii` |

This raises the canonical template count to **168 distinct UI states** while preserving the original IDs.