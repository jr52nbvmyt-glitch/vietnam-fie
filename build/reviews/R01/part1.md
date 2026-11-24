# R01 — The variable scale: ranges, facets, the 1974 snapshot and the rung test (v1.0.6)

*A revision without a provision. It changes how the war is measured, not the war itself. No event is created, changed or cancelled; the end state is unchanged.*

## Why

The user ruled on 24 Nov 2026 that the capped −3 to +3 bands on the world variables were too coarse to carry the analysis and failed to capture its nuances, and chose the replacement in this revision's thread¹. The record already showed the problem. Of the 143 pushes that memoranda 001–010 filed, 131 were ±1: in practice the scale recorded only whether a variable moved, not how far. Two headline variables, ARVN effectiveness and identifying the VCI, sat at the cap of +3 in Phases II and III, and the analysis had begun carrying a second, finer scale in prose to get around it. POSCP02-1 measured further gains on the ARVN battalion "in that running sum and not in the band". DIRMT01-2 and DIRCP02-3 built the running sums of sub-band estimates that the bands could not hold.

The user also pointed out that a single variable could hide the very differences the war turned on. "ARVN effectiveness" does not distinguish an army that fights well in the paddies from one that can stop tanks, clear a city, or withdraw under pressure without breaking¹.

## What changes (v1.0.6)

**The scale.** Every value is a range on a scale of −10 to +10, with a confidence and a one-line note on what the range means on the ground. The anchors are: 0 no effect, ±1 a trace, ±2 to ±4 noticeable, ±5 to ±7 substantial, ±8 to ±10 transformative. ±10 is reserved for a different war on that variable. The width of the range is the uncertainty, and a range may cross zero when even the direction is uncertain. The values remain judgments, not measurements. The definition sits at the head of `schema/VARIABLES.toml`.

**Hard units where they are honest.** Each headline variable now has a tier.
- *Hard:* night control of hamlets, displacement, Trail tonnage arriving, American casualties and American political tolerance. These have a real unit and published historical figures. Once history's figure for a phase's end date has been researched and entered as `hist` with its historical tag, the chapter also states this war's figure as `est`, tagged as an exercise judgment forever. The range stays the judgment; the figures say what it means.
- *Semi-hard:* VCI strength, identifying the VCI, finding the main force, enemy control of engagements and ARVN effectiveness. These have a proxy unit but thin sources, so anchors are optional.
- *Soft:* the GVN's legitimacy, Saigon's stability, Hanoi's will, ARVN self-sufficiency and the negotiating position. These have no honest unit, and the range and its note carry them alone.

No anchor has been entered yet. The research of the thirty hard anchors (five variables, six phases) is the next piece of this work.

**Facets.** Variables whose parts fail separately now have facets. These are sub-variables on the same scale, and a provision that acts on one pushes that facet, not the parent:
- *ARVN effectiveness:* small-unit and counter-guerrilla infantry; combined arms; anti-armor; urban combat; air-ground and fire-support coordination; mobile defence and withdrawal under pressure; night operations.
- *The Regional and Popular Forces:* outpost defence; night patrol and ambush; reaction and relief.
- *The VNAF:* close air support; lift; maintenance and sortie rate; survivability against air defence.
- *ARVN self-sufficiency:* maintenance; logistics and distribution; organic fire support; the replacement and training pipeline.
- *American political tolerance:* public opinion; Congress and appropriations; the administration.
- *Night control and the GVN's legitimacy:* split by corps region, I to IV Corps, because the northern provinces and the Delta are different wars.

A parent's range is never the average of its facets. Once any facet is judged, the parent names its *binding* facet, the one that decides outcomes. Every facet starts `unjudged`, because converting today's bands into facets would invent detail the record does not hold.

**The 1974 snapshot.** Phase VI now carries a second vector, `[snapshot]`, dated December 1974, before the last offensive. DIRMT01-3 found Phase VI's end vector "blind by construction": it is taken after the fall and cannot record anything the fall erased. The snapshot starts unjudged. The checker warns any memorandum that revises Phase VI and leaves it so.

**The rung test.** The A9 call is now tested against stated conditions for rungs (b) to (e) in `rules/RUNGS.toml`. Every §4.N closes with a `` block giving PASS, FAIL or OPEN on each condition, with its evidence. The script refuses a Part 3 whose end state is not the highest rung the test supports, unless the outcome is off the ladder. Conditions b1 and b2 draw the line between (a) and (b) that DIRMT01-1 found the ladder's words did not draw: the historical fall, twenty-five months after the last American combat troops left, fails b2. The conditions are the user's to change.

**Cards.** The card limit is now set per provision (`card_chars_base` plus `card_chars_per_provision`), because a flat limit penalised multi-provision memoranda and C3 forbids compressing a provision to fit. When a full card will not fit in a Part 2 pack, the pack now loads it short, without key figures and negative specifications, instead of dropping it.

## What this revision did to the record

**The chapters.** Each of the six chapters' end vectors was converted mechanically from the old bands, with no new judgment:
- ±1 became ±2..±4, ±2 became ±5..±7, ±3 became ±8..±10, and 0 became 0..0.
- Each converted entry is marked `converted`.
- Four entries were at the cap of the old bands: ARVN effectiveness and identifying the VCI, each in Phases II and III. These now sit at +8..+10, the top of the new scale. Their notes say that this may overstate or understate them and that they wait to be re-judged against the running sums of DIRMT01-2.
- The facets and the Phase VI snapshot were added as `unjudged`.

No event and no prose in any chapter changed.

**The memoranda.** Memoranda 001–010 are unchanged. Their manifests keep `band` on the old scale as history, and the script reads them through the same mapping for routing, ledgers and cards, which show both forms (for example "+1 [old band ≈ +2..+4]"). A memorandum from 011 on may not write `band`.

**The end state** is unchanged: rung (a), Saigon falls on 30 April 1975.

## Directives and positions

- **DIRR01-1** · DIRCP02-3's rule for a variable "already at the cap of the bands" lapses, because the scale has no cap short of a different war: a provision that acts on such a variable re-judges its range, and the range of the facet it acts on, and the running sums of DIRMT01-2 now say which part of that range they support rather than whether they cross a band; the rest of DIRCP02-3 stands, the target the enemy moves to in answer is still named, and a product of overlapping judgments is still reported as a range with its upper bound marked (the user's change of scale, 24 Nov 2026; R01)
- **DIRR01-2** · A range marked "converted" is the old band restated, not a judgment: it is never cited as a judgment of the war, and every memorandum or checkpoint whose evidence bears on a converted entry, or on one of the four entries converted from the cap, re-judges it with a confidence and a note (R01's mechanical conversion of the end vectors)
- **DIRR01-3** · Where a variable has facets, §2 names the facet a provision acts on, and every revised phase that judges a facet names the parent's binding facet and says why it binds; the parent is never the average of its facets, and a gain on one facet is not reported as a gain on the parent unless the binding facet moved (the user's point of 24 Nov 2026 that "ARVN effectiveness" does not discriminate between urban combat, combined arms, anti-armor and the rest)

- **REVR01-1** · reverses POSCP02-1 · vars: ARVN.effectiveness, ENEMY.engagement_control · The judgment of POSCP02-1 on the war stands: the ARVN battalions broken in 1966–67 are about two-fifths to a half fewer than history's, a judgment whose factors overlap and whose upper bound is the "about half" of 010, and none of it changes which fights the enemy accepts. What is reversed is its method: further provisions on the ARVN battalion are no longer measured outside the variable because the variable is capped. They are measured on the v1.0.6 scale, in the range of ARVN effectiveness and the facet they act on, and the running sum feeds that range (R01)

## What remains

Three pieces of work follow, each in its own thread:
1. Researching the thirty hard anchors, which are history's figures for the five hard variables at each phase's end.
2. A re-judgment pass on the four entries converted from the cap and on the facets where the record holds evidence, with the Phase VI snapshot judged from the chapters.
3. The first memorandum under v1.0.6, which carries the first rung test.

Until the re-judgment pass has run, a `converted` range means exactly what the old band meant.

## Notes

1. Stipulated in the provision.
