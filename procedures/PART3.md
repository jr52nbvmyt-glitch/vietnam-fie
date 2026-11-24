<!-- fie v1.0.6 -->
# Part 3 — §4 The course of the war · §5 Delta ledger · §6 Changed / not changed

**Trigger:** `CONTINUE` when the open memorandum's status is `part2`.
**Output:** edited chapters in `memos/NNN/chapters/`, `memos/NNN/part3.md` (created from the template when Part 2 finished), and `history/endstate.toml` if the end state changes. Reading copies: `build/memos/NNN/Part-3.md`, `build/WAR-HISTORY.md`, `history/TRAJECTORY-LOG.md`.

§4 is the largest section of the memorandum and is never compressed. It now has two halves: **the war itself**, which you change by editing the chapters, and **the analysis of the change**, which you write in `part3.md`.

## Steps

1. This is a fresh thread. Do not read the part files: the pack carries this memorandum's own card, with its findings. Read `memos/NNN/manifest.toml`.
2. The pack (`build/packs/PACK-NNN-part3.md`) was printed by `boot`; it is already read.
3. **Read the war.** The pack holds exact digests of every chapter — overview, every event's header, how the phase ends, end vector. From them decide which phases this provision materially changes (materiality rule below), then read those chapters in full, and the one before each for its ending. Small histories are read whole; the pack says which mode applies.
4. **Write the changes to the war** into `memos/NNN/amend.md` in one Write call and apply them with `python3 scripts/fie.py amend NNN memos/NNN/amend.md`, which stages the chapters it touches — see *Changing the war*.
5. For a small fix afterwards, edit the staged chapter in `memos/NNN/chapters/` directly; for anything larger, a second amend file.
6. **Write `part3.md`** — see *The analysis*. Write §4.0 last of the §4 sections, after the chapters are edited, from the chapters.
7. **End state.** If the war's end changes, edit `history/endstate.toml`: the fields, `last_changed = "NNN"`, and a new `[[history]]` entry (`by`, `rung`, `reason`).
8. `python3 scripts/fie.py finish NNN --part 3 --push`. It stamps the events you touched, promotes your chapters into `history/`, appends the log, positions and persons, and rebuilds the War History, then commits and pushes. Then send `build/memos/NNN/Part-3.md`, `build/memos/NNN/CHANGES.md` (every event and passage this memorandum changed, before and after), `build/WAR-HISTORY.md` and `history/TRAJECTORY-LOG.md`, and close.

## Changing the war

**The amend file.** One file, written once, holding every change this memorandum makes to the war as whole blocks:
- `## EV000-14 · <title> · <date> · <place> · <origin> · NNN` and its full text — replaces that event wherever it is. Write the whole event as it now stands.
- `## EVNNN-k · …` with a new ID — a new event, inserted by its date into the phase that date falls in.
- **The first line of every event you create or change** is `*Initiative: enemy*`, `*Initiative: allied*`, `*Initiative: both*` or `*Initiative: neither*` — who chose that this event would happen, when and where. The script builds the enemy's war in sequence from these (`build/ENEMY.md`), so the enemy can be read as one campaign.
- `## P2 · Overview`, `## P2 · How the phase ends` — replace those passages of chapter P2.
- `## P2 · end_vector`, then whole entries like `"ARVN.effectiveness" = { low = 5, high = 7, conf = "medium", binding = "anti_armor", note = "holds and counter-attacks in the lowlands; still breaks before massed armor" }` or `"ARVN.effectiveness.anti_armor" = { low = -1, high = 2, conf = "low", note = "…" }` — each line replaces that entry. `## P6 · snapshot` does the same for the end-of-1974 snapshot.

Only what changes goes in the file; every other word of the chapters stays as it is. The file stays in `memos/NNN/` as the record of what this memorandum did to the war.


The chapters are the only copy of the war. You change them; you never retell them.

- **Change only what changes. Never rewrite a passage that does not change.** Unchanged text is carried forward word for word, which is what keeps the hundredth memorandum's Phase II the same war as the tenth's. If divergence has made a chapter unworkable as an edit, rewrite it and declare the deviation in the manifest (G6).
- **A historical event that plays out differently:** edit its text; change its origin from `HIST` to `HIST-ALT`; say in the text what changed and which provision or finding changed it.
- **A historical event that no longer happens:** origin `CANCELLED`; replace its text with what happens instead and why it does not occur. Never delete an event.
- **A new event:** insert it at its date, ID `EVNNN-k` (k counts from 1 across all chapters in this memorandum), origin `NEW` (a provision caused it) or `FREE` (free play, G4), works field `NNN`. New operations take operation names: `Operation SILVER LANCE`.
- **An event that moves into another phase:** `CANCELLED` where it was, with a pointer; `NEW` where it now falls, citing the old ID.
- **Prefer changing the war to adding to it.** The war has only so many battles. Where a provision changes how an existing event goes, alter that event rather than adding a parallel one; the floor counts events created *or* changed.
- **Keep events in date order**, and keep the overview and `## How the phase ends` consistent with them.
- **Update the phase's `end_vector`**: for each headline variable you change, its range at the phase's end against the historical state at the same date, on the −10..+10 scale (`schema/VARIABLES.toml`), with its confidence and a note that says what the range means on the ground. An entry still marked `converted` that this memorandum's evidence bears on is re-judged, not left. Where the provision acts on a facet, judge the facet (from `unjudged`) and have the parent name its binding facet. For a hard-tier variable whose entry carries `hist` (history's figure for that date), give `est`, this war's figure, tagged `[X-NNN]`. If a range moves, the next phase must answer it (ripple rule).
- **The snapshot.** A phase with a snapshot date (Phase VI: end of 1974) carries a second vector, `[snapshot]`, before its last offensive. A memorandum that revises that phase judges the snapshot's headline variables: the end vector is taken after the fall and cannot show what the fall erased (DIRMT01-3).
- Figures the exercise generates carry `[X-NNN]`; historical ones `[H]`; earlier memoranda's `[M…]`.

**The chronicle standard.** Every phase is written as a chronicle, not a trend report. A trend report says the interdiction campaign degraded throughput and the offensive culminated early. A chronicle says which formations, on which dates, at which places, with what, against whom, and with what result. Every event you create or change carries:

- a date, or a range tight enough to be useful;
- the formations on both sides, by designation;
- the place, by name — and by grid, route number or province where it sharpens the picture;
- the systems and munitions that decided it, by designation;
- terrain, weather, canopy or monsoon where they bore on the outcome;
- the outcome in concrete terms — ground taken or lost, tonnage, hulls, airframes, prisoners, a bridge standing or down;
- casualties on both sides, with their reliability stated per A13.

An event that cannot be written to this standard is being asserted rather than analysed. Find the detail, or mark the event as an estimate and say what it rests on. **A new operation is described at exactly the granularity of a historical one.** A new operation described more thinly is a failure of nerve, not of information.

**At least one event per memorandum is narrated at length because it embodies a §2 downstream effect** rather than the provision's primary use — the enemy declining battle, the bottleneck that moved, the released formation arriving somewhere nobody planned for it. Cite the finding ID in the event's text. This is how the second-order analysis is shown to be true of the world rather than asserted about it.

## The analysis — `part3.md`

### `## §4.0 The course of the war`

*Write every part of Part 3 under A10a: this is the part the reader reads for the war itself.*

The whole war, January 1964 to its end, as it now runs with everything COMUSMACV holds — a through-line of 1,500–3,500 words in his voice, written fresh in every memorandum. Write it after editing the chapters and from them: it may not contradict a chapter, and it ends where `history/endstate.toml` says the war ends. Show where this provision bends the line and where the line holds regardless of it. This is the part of the memorandum most worth reading; write it as history, not summary.

### One section per phase: `## §4.Pk …` (the template lists them)

**Materiality rule.** Full depth for every phase the provision materially changes. For a phase it does not change, a **stated null** of 40–160 words naming the specific reason it fails to bite, under `<!-- null Pk -->`. A null is an analytical claim and must be defended; "unchanged" and move on is a failure, and padding is equally a failure. If the phase before it had its end vector moved (the checker calls this a ripple), the null must say why the incoming change does not alter this phase, and carry `<!-- ripple-addressed -->` — or the phase must be staged and revised after all.

**A revised phase**, in this order:

1. `<!-- chapter Pk -->` — the chronicle. The reading copy inlines your edited chapter here, with ◆ on the events you created or changed. It holds three kinds of thing, kept distinct: historical events that play out differently; historical events that no longer happen, with the reason; and new operations the provisions create.
2. `### Mechanism` — why it went that way: which provision, which interaction, which §2 finding by ID. Each revised phase carries at least one finding forward by ID, and across §4 at least one of them is the strongest positive effect, grounded in a dated, named event. A phase written purely in first-order terms — the capability arrives, does its job, the phase improves — has not been analysed. Equally, a phase written purely in limitations, adaptations and costs has not been analysed either.
3. `### Enemy response and initiative` — what the enemy does, as reaction and on his own initiative (G3). What he detected, when, and what he did about it; what the adaptation cost him. At least once per memorandum, mark with `<!-- initiative -->` a decision not provoked by anything you did, taken for his own reasons, on his own timeline, out of his own politics, doctrine, rivalry, or misreading, and state what drove it — at the chronicle's standard of specificity.
4. `### Causal chains` — at least three per memorandum across all phases, each reaching a third link: `**CNNN-k** [lag] A → B → C → D`, lag one of `immediate`, `weeks`, `months`, `war-shaping`. The terminal link must satisfy: **it would not have been predicted from A alone.** A chain whose third link restates its first has failed; discard it and find another. Place each chain in the phase where its terminal link lands, cross-referring to the phase where it begins.
5. `### Downstream` — consequences for every later phase.
6. `### Clock` — from Phase III on: the provision's effect on **American political tolerance** through the US casualty rate, the visibility of escalation, the appearance of progress or stalemate, and the appropriation cycle. A provision that wins battles and shortens the clock may be a net loss. This is the mechanism by which the war was actually decided.

### `## §4.H Historical comparison`

Across all phases, what the cumulative force has changed from history, stated concretely — formations preserved or destroyed, cities held or lost, offensives blunted, months gained, lives saved, capabilities created — with the margin stated plainly where the outcome is substantially better than historical.

### `## §4.N Net assessment and end state`

The A9 call: which rung the cumulative force now makes reachable, and why the next is not; or, per G5, the outcome in its own terms first. **The rung test:** close §4.N with a `<!-- rungtest -->` … `<!-- /rungtest -->` block, one line per condition in `rules/RUNGS.toml` — `- c1 · PASS · <evidence>`, verdict PASS, FAIL or OPEN, the evidence a dated event or a chapter's range. The script finds the highest rung whose conditions all pass and refuses a part whose `history/endstate.toml` rung differs (unless it is `off`, G5). Under DIRMT01-2, the running sums of sub-scale estimates now say which part of the range they support, not whether they cross a band. If the war's shape has outgrown its phases, propose a redraw here (G2); the next checkpoint carries it out.

### `## §5 Delta ledger`

Changes only: forces gained or lost, variables and facets moved, from which range to which, new categories. The inventory lives in `build/INDEX.md`.

### `## §6 Changed / not changed`

Two bullet lists, `### What has changed` and `### What has not changed`, at least three items each. **"What has changed" carries analytical priority** — genuine improvements at their true weight, with the margin over the historical baseline where it is substantial. Then the constraints, deficits and problems that persist. The balance between the two reflects the balance of reality, not a presumption that downsides and upsides deserve equal space. Do not soften genuine achievement to match the tone of genuine limitation; do not inflate limitation to balance achievement. Back-reference is permitted here (C2).

### Blocks at the end

- `<!-- log -->` — the Trajectory Log entry, 80–220 words: how this provision shifted the war's course and where the end state moved, written for a reader following the whole arc provision by provision. Not a summary of the memorandum.
- `<!-- positions -->` — any judgment this memorandum commits to that later ones must not silently contradict, and any reversal (E3), in the register format.
- `<!-- persons -->` — anyone, historical or invented, who now recurs.
