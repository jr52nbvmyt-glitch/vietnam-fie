<!-- fie v1.0.3 -->
# Part 2 — §2 Integration and second-order effects · §3 Changes to existing forces

**Trigger:** `CONTINUE` when the open memorandum's status is `part1`.
**Output:** `memos/NNN/part2.md` (created from the template when Part 1 finished). Reading copy: `build/memos/NNN/Part-2.md`.

## Steps

1. This is a fresh thread. Do not read `part1.md` in full: the pack carries this memorandum's own card (figures, negative specification, what it denies, verdict). Read `memos/NNN/manifest.toml`.
2. **Refine the manifest** now that you know the provision: its pushes and depends are what routing uses. Add every variable the §2 analysis will plainly touch.
3. `python3 scripts/fie.py pack NNN --part 2`, then read `build/packs/PACK-NNN-part2.md` in full. It holds: the routing table, the standing directives, errata, the cards of the earlier memoranda that share the most world variables with this one, a ledger for every variable this provision touches, the settled positions on those variables, the full provision index, and the gap register.
4. **Second net.** Run `fie.py grep` on two to four terms that this provision's effects travel through — terms from its negative specification and its depends, not its name (e.g. `refugee`, `helicopter hours`, `district chief`). Read the hits that bear on it. This is how interactions that routing missed get found.
5. If a card lacks a figure, finding or concept you need, find the line with `fie.py grep` and read that part of `memos/MMM/`. Tag what you take `[M…]` (A3b).
6. **Write `part2.md`** to the standard below, in one Write call.
7. `python3 scripts/fie.py finish NNN --part 2`, then commit, push, send `build/memos/NNN/Part-2.md`, and close.

## §2 — what it must do

This section does two things that must be kept distinct but are analysed together because each shapes the other: first-order integration of the provision into the force, and the second- and third-order effects that follow from that integration — including the enemy's adaptation, which propagates through the channels like any other downstream consequence.

**The governing aim is comprehensiveness.** Every provision touches more interactions in this theater than the dossier can name. The channels exist to force a systematic traverse so that effects which fall outside the provision's designed purpose — the ones most likely to be missed — are found before they surface in the chronicle as unexplained outcomes. An interaction caught here and carried into §4 by its finding ID is an interaction the analysis did not miss.

**Nothing stated in §1's verdict counts as a second-order effect.** A direct consequence of the system doing what it was built to do is first order and belongs in the integration analysis. Second-order effects are what the first-order effects then cause.

### Part A — Integration (`## §2 Part A — Integration`)

Do **not** enumerate pairwise interactions. Organise the cumulative force into the functional systems — **FIND** (ISR, SIGINT, sensors, recon) · **FIX** (holding an enemy who chooses whether to fight) · **STRIKE** (air, artillery, naval gunfire) · **INTERDICT** (the Trail, the sanctuaries, coastal and riverine infiltration) · **SECURE** (hamlet security, territorial forces, pacification) · **ADVISE** (RVNAF capability generation, the advisory effort, Vietnamization) · **SUBVERT** (VCI attack, Chieu Hoi, PSYOP, the information war) · **SUSTAIN** (ports, in-country distribution, the ceiling) — and analyse at that level.

- `### Functional systems` — which systems the provision joins, strengthens, and makes newly viable.
- `### Compound pairings` — **only** the specific pairings producing compound effects, named explicitly, with earlier provisions by ID. Put one line per pairing in the `card:interactions` block.
- Always address, under their own headings: `### The find-to-fix chain against the main force` · `### The identify-to-neutralise chain against the VCI` · `### Dependence on SECURE` (everything in the countryside depends on it) · `### The ADVISE cluster` (which has no analogue in a conventional theater and which every provision either feeds or starves).

`### Employment concepts` — how it is actually used. Distinct from integration and not satisfied by it: integration says which systems it joins; this says what it does on a given Tuesday. Each concept is a `#### ECNNN-k · <name>` heading. Give its profile concretely: launch or departure, transit, time on station, the engagement sequence, recovery, turnaround, and the resulting cycle rate per day and per week. Where a concept has a minimum viable package — two airframes and a tanker, a section and its ISR feed — state the package. Where a concept depends on another provision, say which, and what it degrades to without it.

Include the concepts **tried and abandoned**, and why, with `(abandoned)` after the name. A provision's real employment is defined as much by what its operators stopped doing as by what they settled into, and the abandoned concept usually names a constraint the dossier did not surface. Summarise all concepts on one line in the `card:concepts` block.

### Part B — Channels (`## §2 Part B — Channels`)

For each functional system the provision touches, traverse the channels below, each under its own `### <channel>` heading named exactly as here. Content, or a defended null of two sentences; a bare "no effect" is unacceptable. **Analytical weight applies throughout: a channel effect is stated at its true magnitude relative to the provision's primary contribution.** A genuine but minor displacement effect of a provision that saves thousands of lives is analytically real and belongs here, but it is not the headline, and presenting the traverse as though the secondary effects outweigh the primary ones is a distortion.

- **Displacement.** Denied capability does not vanish. Across a border, underground, into the population, into a different season, down a tier from main force to guerrilla. Where did it go, what does it do from there, and what has your ISR lost by pushing it there? Include the enemy's tactical adaptation: what he moves, disperses, buries, or abandons, and what he accepts losing in order to protect something else.
- **Bottleneck migration.** Name the binding constraint on each affected line of effort before the provision and after. The new constraint is rarely the one the provision addressed, and naming it is often the memorandum's most useful output.
- **Own-force opportunity cost.** What scarce thing does this consume — personnel spaces, airlift, port throughput, advisor billets, helicopter hours, engineer battalions, ARVN units pulled from their districts to train on it? What is now *not* being done?
- **Counterfactual erasure.** What no longer happens, and what becomes of the forces and attention that event was consuming?
- **Perverse effect.** Where does success create a liability? Firepower that secures a valley and empties it. An interdiction success that pushes infiltration into a province with fewer advisors. An ARVN unit made effective and therefore moved away from the district that depended on it.
- **Anticipation.** Does the capability's existence prevent the engagements that would have demonstrated it? In this theater the enemy's principal adaptation is *declining battle* — withdrawing across a border, going to ground, dropping from main force to local force operations, waiting a season. That adaptation makes your metrics improve while achieving nothing, and it is the single most important second-order effect in the war. Name it where it applies.
- **Enemy detection and learning.** How long before the enemy detects the provision and what does he conclude — including what he concludes wrongly? What doctrine does Hanoi derive, how fast does it propagate from COSVN to a district cell, and where else does it apply? What does the enemy get right about this capability that hurts you?
- **Enemy adaptation cost.** What does the counter-move cost the enemy in cadre, tonnage, or time? What does he sacrifice to fund it? Where an adaptation is cheap — costing the enemy less than the provision cost you — say so, because that exchange rate decides whether the provision is winning or merely busy.
- **Cross-boundary feedback.** Follow the loop out of theater and back: theater effect → American casualty rate → domestic political tolerance → appropriation and troop ceiling → return path into the theater. Or: interdiction success → Soviet and Chinese resupply → air defence density over the North → US aircraft loss rate → POW numbers → negotiating position. Follow it until it returns or demonstrably does not.
- **Open channel.** Any mechanism this provision opens that the nine above do not name. Leave it to a line when there is nothing; an empty open channel is honest and a padded one is not.

### Part C (`## §2 Part C — Counter-directional finding and strongest positive effect`)

At least one effect running against the provision's obvious direction: a way it makes something worse, creates a vulnerability, forecloses an option, or produces a result the command will not welcome. **State it at its true weight relative to the provision's primary effect.** If you cannot find one, write `<!-- cd:none -->` and say what you ruled out and why. Do not manufacture one, and do not skip the search.

Then the **strongest positive effect** — the single most significant improvement over historical, quantified where possible. Not the §1 verdict restated but the most significant thing the provision changes about the war, which may be a compound interaction, a downstream consequence, or a combined capability. **The counter-directional prevents overselling; this prevents underselling.** State it at full weight. If the honest assessment is modest, write `<!-- spe:modest -->` and say so.

### Findings

Every channel effect, the counter-directional finding and the strongest positive effect is a numbered finding: a paragraph opening with its bold ID, numbered in order of appearance — `**FNNN-1** (SECURE) …`. The counter-directional opens `**FNNN-k · Counter-directional** …`; the strongest positive `**FNNN-k · Strongest positive** …`. Only the defining paragraph opens with the bold ID; elsewhere cite the ID in plain text. These IDs are how §4 carries findings into the war.

`## §2 Findings register` — the `card:findings` table lists every finding: ID · channel (or CD / SPE) · system · one-line summary · weight (minor / moderate / major / transformative).

## §3 — Changes to existing forces (`## §3 Changes to existing forces`)

How previously present capabilities change in employment, tactics, tempo, or effectiveness. Back-reference is permitted here (C2). Use these headings, each with content or one line saying it is unchanged and why: `### The advisory effort and MACV staff` · `### US conventional forces` · `### US Special Forces and CIDG` · `### ARVN divisions and the JGS` · `### RF/PF and territorial security` · `### Rolling Thunder` · `### Trail interdiction` · `### Arc Light` · `### Airmobile formations` · `### Riverine and coastal forces` · `### Phoenix / Phung Hoang` · `### Third-country forces` · `### Prior provisions`.

Under **Prior provisions**: every earlier provision whose employment changes, by ID and designation, with what changes; then one line listing the IDs of those that do not.

## Rules that bind hardest here

A10a (writing for the reader), A6 (two halves of find-and-fix), A7 (sanctuary), A8 (the population), A13 (metrics), C2, G3, G7.
