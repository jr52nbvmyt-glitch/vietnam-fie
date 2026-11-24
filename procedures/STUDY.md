<!-- fie v1.0.7 -->
# STUDY — a deep account of two or three areas of the war, as the record now stands

**Trigger:** `STUDY` followed by the areas I name, two or three at a time: the air war, CIDG, the anti-VCI campaign, the war in the Delta, the maritime war, or any other part of the war. It is not a memorandum and no provision is introduced.
**Output:** one study per area in `studies/<slug>.md`, each written in its own part; any end-vector judgments the studies make, staged in `reviews/STnn/chapters/`. Reading copies in `build/studies/<slug>.md`, and the index in `build/STUDIES.md`.

A study **describes**. It is the record's account of one area — its forces, its campaigns, its people, the enemy's war in it, and how far it now differs from history — told phase by phase from January 1964 to the war's end, as the chapters, memoranda, checkpoints and registers now have it. It changes nothing in the war: it adds no event, alters none, and never moves the end state. When the record disagrees with itself about the area, the study says so and sends the question to an erratum or the next checkpoint; it does not settle it by writing a third version.

A study is not a chapter and is never pasted into one. The chapters are the war; a study is a reading of it, kept beside it.

## Parts and threads

One part per area, each in its own thread, in the order I named them: Part 1 in the thread my `STUDY` arrives in, then `CONTINUE` in a new thread for each further area. Effort: high — this is reasoning over the whole record, not research. No other work that writes to the repository runs until the last part has pushed.

## Steps — Part 1 (the thread my message arrives in)

1. `python3 scripts/fie.py study --init "<area 1>" "<area 2>" ["<area 3>"]`, in my words. It opens `reviews/STnn/`, gives each area a slug, and stages each study in `reviews/STnn/studies/<slug>.md` — from `templates/study.md`, or, for an area that already has a study, the existing study (a **re-run**: rewrite it from the record as it now stands and fold its since-entries into it). It refuses if any other work is open.
2. Continue with *Every part* below for the first area.

## Every part

1. **Tags.** In the staged study's front matter, set `tags`: the variables and facets in `schema/VARIABLES.toml` that this area covers (a variable covers its facets). Be generous where the area really bears on a variable — tags route every later memorandum to the study — and honest where it does not. If the area turns on something no variable or facet captures, say so under *Questions for the record* (adding a variable or facet is a version change).
2. `python3 scripts/fie.py pack STnn` and read it. It holds the current values on the tagged variables (from the chapters and the study), each tagged variable's ledger (every provision that pushes it or depends on it), the settled positions on those variables, the memoranda that touched them with their provisions and errata, the standing directives, the gap register, and exact digests of every chapter. On a `CONTINUE` the boot prints this pack for the next area; if the tags are not set yet it lists the variables instead — set them and run the pack again.
3. **Read the record for the area.** `fie.py grep` the area's terms — places, formations, programmes, systems (`Hoa Hao`, `Kien Hoa`, `PBR`, `Game Warden`, `CIDG`, `Mike Force`) — and read in full the events and passages the area turns on. Read the cards (`build/cards/CARD-NNN.md`) of the memoranda that touched it, and the part files only for a passage a card lacks. **Everything in the study comes from the repository** (`[M…]` and `[X-…]` for the exercise's own record and judgments, `[H]` for history). A historical figure the record does not hold may be researched (a few searches at most), listed under `## Sources` as `[S1] …` and cited `[S1]`.
4. **Judge.** The study judges the facets and variables in its area, phase by phase, as at each phase's end against the historical state — the same scale and the same meaning as an end vector (`schema/VARIABLES.toml`). Most of them have stood `unjudged` since the scale change (R01).
   - **Headline variables and their facets** (the keys every chapter's end vector carries) have one copy, in the chapters. Judge an entry that is still `unjudged` or `converted` by writing an amend file of `## Pk · end_vector` (or `## P6 · snapshot`) blocks and applying it: `python3 scripts/fie.py amend STnn <file>`. Where a facet is judged, name the parent's `binding` facet (DIRR01-3). **An entry a memorandum or checkpoint has already judged is not re-judged by a study**: if the study's reading disagrees with it, the disagreement is a question for the record.
   - **Every other variable and facet** (the RF/PF, the VNAF, the Trail's capacity, sea infiltration, the police …) is judged in the study's own front matter, one table per phase: `[values.P4]` then `"RFPF.effectiveness.outpost_defence" = { low = 2, high = 4, conf = "medium", note = "…", ind = "…" }`. The study is this value's one copy.
   - Judge where the record holds evidence, and leave unjudged where it does not — and say which, and why, under `## Judgments`. A range with a confidence and a note that says what it means on the ground; never a precision the record does not support (A12, A13). Where a real indicator exists — sorties, outposts overrun, junks searched, tonnage — give it in `ind` with its tag, history's figure `[H]` beside this war's `[X-STnn]`.
5. **Write the study** into the staged file, in one Write call. The script checks this shape:
   - `# <area> — the war as it stands after memorandum NNN`
   - `## Summary — the state of the area now` — the answer first: what this area is now, in this war, at its end, and the margin over history, at its true weight in both directions (A3, G7). The script inserts the current values table after it in every reading copy and pack.
   - `## P1 · …` through `## P6 · …` — **one section per phase, every phase.** The area's chronicle in that phase as the record has it: the forces on both sides by designation, the provisions at work in it by ID, the events that carried it by ID with date and place, what changed from history and what held, and what the enemy did in it on his own initiative. Chronicle standard (`procedures/PART3.md`): named formations, places, dates, systems, outcomes, casualties with their reliability. Write for the reader (A10a, `rules/VOICE.md`): this is history, not a register. A phase where the area is quiet says why in a short section. Not in the COMUSMACV voice: a study is the record's account, written as a historian of this war would write it, in the third person.
   - `## Judgments` — every value the study set or left unjudged, by key and phase, with the evidence: the events, findings and figures it rests on. Name each headline facet it judged in the chapters, and each it left unjudged and why.
   - `## Questions for the record` — every inconsistency found in the record about this area, one line each: `- **Q-1** · ERRATUM · <what conflicts with what, by file and ID>` (a finished record is wrong: the next `ERRATUM` takes it) or `- **Q-2** · CHECKPOINT · <…>` (a judgment or a chapter that the next checkpoint must reconcile). If none was found, say what was checked.
   - `## Sources` — `[S#]` lines, if any.
   - `## Since this study` — empty. Memoranda append here through the script; never write in it.
   - Front matter: `written` and `as_of` as the template set them; `rerun = false`.
6. `python3 scripts/fie.py study STnn --finish --part k --push`. It checks the study and the staged chapters (no event or prose changed; no already-judged entry re-judged; the end state untouched), promotes them, rebuilds, commits and pushes. Fix every ERROR and run it again; read every WARNING and fix it or answer it in the text.
7. Send me `build/studies/<slug>.md` (and `build/reviews/STnn/CHANGES.md` if chapter values were judged). In chat, at most three sentences, as yourself: what the study found that I should know, the questions it raised, and the next command — *Send CONTINUE for the study of <next area>*, or, after the last, that the run is complete.

## How studies live on

- **Part 1 of a memorandum** (`procedures/PART1.md`) loads every study whose tags share a variable with the new provision's manifest, so the dossier is written against the area as it stands.
- **Part 2** judges the provision's pushes against each such study's values under `### Against the studies`, marking each study `<!-- against <slug>: consistent -->` or `<!-- against <slug>: contradicts -->`, and says in plain words where the provision's effect contradicts a study and which should give way.
- **Part 3** closes with a `<!-- study <slug> -->` block for each such study: what changed in the area and which events show it, and a value line for each study-held value that moves. The script appends it to the study as a dated entry under *Since this study*, with the chapter values the memorandum moved on the study's variables.
- **A checkpoint** folds each study's entries into its text and values, re-judges, answers its questions, and, where a study has drifted too far to fold honestly, sets `rerun = true` with a reason: `fie.py status` then advises a fresh `STUDY` of that area.

## Rules that bind hardest here

E2 and E4 (the chapters are the war; a study never overrides one), A3 (honest weight both ways), A12 and A13 (ranges, not false precision; body count and HES only with their caveats), A6 (which half of find-and-fix an area turns on), A7 (sanctuary), A8 (the population), G3 (the enemy has initiative), A10a (write for the reader), and the repository rule above all: nothing from memory.
