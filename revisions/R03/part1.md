<!-- R03 part 1 -->
# R03 — Natural units: the −10..+10 scale retired (v1.0.8)

*A revision without a provision. It changes how the war is measured, not the war itself. No event is created, changed or cancelled, and the end state is unchanged.*

## Why

On 25 November 2026, during checkpoint CP03, the user ruled that the −10..+10 scale is close to meaningless. A value such as "+3 on night control" never says how many hamlets that is. The user accepts figures that carry a small inherent error, because the exercise estimates [U]. The user chose to have every variable given a natural unit before the checkpoint's Part 2 re-judges the end vectors, rather than putting figures beside the scale [U].

The record had already shown the cost of the old scale. CP03 found three things the scale had let pass (CP03 Part 1, §3 and §5):

- **Night control sat unjudged in Phases I–V.** Its converted +2..+4 in Phases I to V had never been judged, through three memoranda that broke the infrastructure of the held belt. A converted +2..+4 does not look wrong beside a VCI strength of −8..−6, because neither range says how many hamlets or how many cadre it means.
- **The hard-unit machinery was never used.** R01 had built hard-tier `hist`/`est` fields so that figures could sit beside the scale. None of the thirty anchors was ever entered, because the figures were optional and the scale was not.
- **An unsized claim went untested.** Memorandum 013's claim that the opening strike held two to four PAVN divisions in the North "for months" was entered as −1..0 on PAVN strength in the South. Had it been written in the unit, thousands of troops arriving months late, it would have had to name the formations, and the claim would have been tested when it was made.

## What changes (v1.0.8)

**Every variable has a unit.** All 57 variables in `schema/VARIABLES.toml`, and every facet, now carry four fields:
- `kind`: count, share, months or ladder.
- `unit`: what one unit is.
- `better`: the direction that favours the allies.
- `rungs`: for a ladder, its named positions in order.

The scale's anchor words ("noticeable", "substantial") are gone. Examples:
- Night control is the percentage of the rural population in hamlets the GVN holds after dark, by corps in its facets.
- Trail tonnage is tons a year arriving.
- VCI strength is thousands of cadre.
- Identifying the VCI is thousands of listed cadre of district rank or above neutralised a year.
- ARVN effectiveness is weapons lost per hundred weapons captured, and its seven facets each have a unit of their own: minutes for fire, days to clear a town, and the share of withdrawals completed intact.

**Three things that move in steps are ladders.** For each, the ladder is in the schema:
- **Hanoi's will**, from "would accept a divided Vietnam" to "fights for reunification at any cost and on any timetable".
- **The negotiation**, from "no talks" to "an agreement with enforcement".
- **What Washington will grant the war**, from "nothing further: aid ends" to "forces increased on the commander's request".

The administration facet of American political tolerance is a ladder too. Congress's facet is dollars of military aid appropriated for the fiscal year, and the public's facet is Gallup's "not a mistake" share.

**A value reads as a figure.** An end-vector entry gives history's figure at the phase's end, with its source (`hist`, `src`). It then gives this war's figure as a range in the same unit (`low`, `high`). Where history's figure has not yet been researched, the entry gives the difference from it instead, either in the unit (`dlow`, `dhigh`) or as a percentage of history's figure (`plow`, `phigh`). The note says what the figure means on the ground.

The `converted` confidence is retired. An entry that had only a mechanical conversion is now `unjudged` and keeps its old range in `was`.

**A push reads as a change.** From memorandum 014, a provision's push is its own contribution in the unit, by the end of a named phase. For example, "4–9 points more of IV Corps' rural population held after dark by the end of Phase II" is written `dlow = 4, dhigh = 9, at = "P2"`. Memoranda 001–010 (bands) and 011–013 (the −10..+10 ranges) stay as written, and the script shows them marked with their scale.

**What did not change.** Every value is still a judgment and never a measurement (A12, A13). Each value still carries:
- its confidence;
- a range whose width is the uncertainty;
- facets and binding facets;
- the ripple rule, which now compares the figures;
- the 1974 snapshot;
- the rung test.

## What this revision did to the record

**The schema, the script and the procedures.** `schema/VARIABLES.toml` was rewritten. `scripts/fie.py` now validates values in their units. It refuses a share outside 0..100, a rung that is not on its ladder, a figure from history without a source, and the retired `converted`. It shows values as figures, checks pushes from memorandum 014 in units, and weighs routing in units by confidence. The formats (`schema/FORMATS.md`) and the instructions in PART1, PART3, CHECKPOINT and STUDY now speak in units. The version is 1.0.8 throughout.

**The chapters' end vectors.** All six chapters were staged and only their front matter changed, as follows.

*History's figures entered (45 entries):*

| Variable | Figures | Source |
|---|---|---|
| US killed by hostile action | 1965: 1,369; 1967: 9,378; 1968: 14,592; 1971: 1,380; 1972: 300; 1974: 0; 1975: 2 | [R03·S1], [H40]; the two Marines of 29 April 1975 [H] |
| Gallup "not a mistake" | 1965: about 60%; Dec 1967: 44%; Dec 1968: 41% | [R03·S2], [R03·S1] |
| HES A–C share | Jan 1968: 67.2%, standing for Dec 1967; Dec 1968: 76.3% | [R03·S3], [R03·S4] |
| Share of engagements the enemy initiated | 1966: 66%; Oct 1966–May 1968: 68% | [R03·S5] |
| Changes of government | four in Phase I (the coup of January 1964, the attempt of September 1964, the coup of February 1965 and Quat's resignation in June 1965); none in Phases II–V; two in 1975 | [H8] [H10] [H23], [H] |

*History's position on each ladder, from the record:*
- Hanoi's will is at rung 4 throughout.
- The negotiation:
  - rung 1 in Phases I and II;
  - rung 2 from 1968 [H51];
  - rung 3 in 1974, after the Paris Agreement.
- What Washington will grant:
  - rung 5 in 1965 and 1967 [H21];
  - rung 4 from 31 March 1968;
  - rung 2 in 1974–75, with $700 million for fiscal 1975 [H72] [H71].

*The 69 judged entries were translated into units, each by its own note's mechanism.* The full list is in the staged chapters, and every old range is kept in `was`. The larger translations:
- **VCI strength:** about a third to nearly a half fewer cadre than history's in Phases II and III, and a tenth to a fifth fewer in Phase I.
- **Identifying the VCI:** about 1,500–3,000 more listed cadre of district rank or above taken a year in 1966–68 than history's.
- **Trail tonnage arriving:** 5–17% below history's in Phase III, by Commando Hunt's count and the J's share.
- **American political tolerance in Phase VI:** rung 3 against history's rung 2. Congress appropriates about $950 million to $1,275 million for fiscal 1975 against $700 million, and the President's line stands at rung 4 against history's 3.
- **Night control at the end of 1975:** 35–55% of the South's whole rural population held after dark, all of it in III and IV Corps. History's figure is nil, because the Republic had ceased to exist.

*The 55 converted entries are now unjudged in units*, each with its old range in `was`.

*Not judged here.* R01 converted mechanically because a mapping existed. No mapping from "+2..+4" to a share of the population exists, and inventing one would put false figures into the record. Judging the 55 is the work of CP03 Part 2, which reviews Phase III and its evidence. Night control by corps in Phases I–V is to be judged first, because the user's question about the VCI campaign turns on it.

**Checkpoint CP03's staged Phase III** carries the same front matter as this revision's Phase III, so that the checkpoint's finish does not restore the old scale.

**Studies.** The air-war and maritime-interdiction studies keep their values on the −10..+10 scale until they are next folded. Their three since-entries are waiting for CP03 Part 2 to fold them, and that fold re-judges them in units. The study tables say so.

**The end state** is unchanged at rung (b).

## What remains

- **History's figures.** About 105 headline entries (15 variables, six phase ends and the 1974 snapshot) and their facets need history's figure. This revision entered 45, from the record and from five sources. The largest gaps are:
  - night control after 1968, and by corps;
  - refugees;
  - VCI strength by year;
  - Trail tonnage by year;
  - Gallup after 1968;
  - ARVN weapons ratios;
  - the RVNAF's share of its own fire support.

  The thin pages of the Thayer volumes that hold most of these could not be read whole from here. A checkpoint or study that reaches one of them enters it.
- **CP03 Part 2** judges the converted entries in units, beginning with night control by corps.

<!-- directives -->
- **DIRR03-1** · Every value and every push is written in its variable's natural unit (schema/VARIABLES.toml, v1.0.8): this war's figure beside history's where history's is known, otherwise the difference from history in the unit or as a percentage of history's figure, and a note that says what the figure means on the ground; a claim that cannot be put in its unit is not yet a judgment (the user's ruling of 25 Nov 2026 that the −10..+10 scale is meaningless; R03)
- **DIRR03-2** · A memorandum or checkpoint that judges a headline entry researches history's figure for it where it can and enters `hist` and `src`; an `[E: basis]` estimate of history's figure is allowed with its basis stated, and an unresearched figure is never stated from memory (R03; CLAUDE.md "read; never recall")
- **DIRR03-3** · A memorandum re-judges, in units, every unjudged headline entry among its own dependencies when its evidence bears on it, not only the variables it pushes (CP03 §3: night control sat converted through three memoranda that broke the infrastructure it depends on)
<!-- /directives -->
