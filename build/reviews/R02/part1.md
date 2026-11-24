# R02 — Studies: a deep account of an area of the war, beside the memoranda (v1.0.7)

*A revision without a provision. It adds a command and the machinery to keep what that command writes; it changes nothing in the war. No event is created, changed or cancelled, no end vector moves, and the end state is unchanged.*

## Why

The user proposed on 24 Nov 2026 that, in place of a memorandum, he could name two or three facets of the war (the air war, CIDG, the anti-VCI campaign, the war in the Delta, the maritime war) and have each written up as it now stands, and he approved the design set out below the same day¹. The record already shows the need. After eleven memoranda, two checkpoints and a meta-checkpoint, the state of any one area is scattered: its events lie across six chapters, its findings across the memoranda that happened to touch it, and its measure across end vectors in which 124 of 132 facets have stood unjudged since R01. No record answers the plain question "where does the air war stand?" without a reader assembling it himself.

## What changes (v1.0.7)

**A new command, `STUDY <two or three areas>`** (`procedures/STUDY.md`). It opens a study run, `STnn`, with one part per area, each part in its own thread. Each part writes one study, `studies/<slug>.md`. This is a deep account of the area across every phase, from January 1964 to the war's end, as the chapters, memoranda, checkpoints and registers now have it. A study is written by a historian of this war, not in the COMUSMACV voice, and to the chronicle standard.

**A study describes; it never changes the war.** It adds, alters and cancels no event and never moves the end state. Where the record disagrees with itself about the area, the study lists the disagreement under *Questions for the record*, marked for an erratum or for the next checkpoint. It does not settle the disagreement by writing a third version. A study is never written into the chapters, which are already long. The script refuses a study run that touches an event, the chapters' prose or the end state.

**A study judges its area's variables, and every value keeps one copy.** Each study carries tags: the variables and facets it covers. It judges them phase by phase on the scale of R01.
- A headline variable or one of its facets has one copy, in the chapters' end vectors. A study may judge such an entry only while it is `unjudged` or `converted` (or add the parent's binding facet). An entry a memorandum or checkpoint has already judged is not re-judged by a study; disagreement with it is a question for the record.
- Every other variable or facet the study covers, such as the RF/PF, the VNAF, sea infiltration or the police, is held in the study's own `[values]`, with a real indicator beside it where one exists.
- The script draws both into a *Current values* table in every pack and reading copy.

**Studies route into the memoranda through their tags.**
- *Part 1* runs `fie.py pack NNN --part 1` after triage and reads every study that shares a variable with the provision, so the dossier is written against the area as it stands.
- *Part 2* carries the studies' summaries, values and questions in its pack, and must judge the provision's pushes against each under `### Against the studies`. Each study is marked `consistent` or `contradicts`, and a contradiction must be stated in plain words with which side should give way. The checker refuses a Part 2 that leaves a matched study unjudged, and the audit line reports each verdict.
- *Part 3* closes with a `` block for each such study: what changed in the area and which events show it, with value lines for the study-held values that move. The script appends each block to its study as a dated entry under *Since this study*, adding the chapter values the memorandum moved on the study's variables. The checker refuses a Part 3 that omits a block.
- A *VETO revision* whose change reaches a study's area adds such a block too.

**Checkpoints fold.** The checkpoint pack lists every study with its waiting entries, how far its values have drifted, which memoranda contradicted it, and its open questions. Step 8a of `procedures/CHECKPOINT.md` folds the entries into the study's text and values, re-judges, and answers the questions (`fie.py study fold CPnn <slug>`). Where a study has drifted too far to fold honestly, the checkpoint sets `rerun = true` with a reason, and `fie.py status` advises a fresh `STUDY` of that area. The thresholds at which the script advises a re-run are in `rules/CONFIG.toml` `[studies]`; the call is the checkpoint's.

**What else changed.** The authority order (E2) now places the studies below the record and above the generated views. E4 states that a study never changes the war. The record formats, the bootstrap, the Part 1–3, checkpoint, meta-checkpoint and revision procedures, the templates, the README and the design note describe the above. `fie.py` gained the `study` command, the Part 1 pack, the study pack, the checks and the reading copies (`build/studies/`, `build/STUDIES.md`). The project instructions field gains `study` among the boot commands and `STUDY` among the commands.

## What this revision did to the record

Nothing in the war. No chapter, register, memorandum or review was changed, and no study has been written yet; the user will name the first areas. Memoranda 001–011 are unaffected: they finished before any study existed, and the new checks apply only to parts finished from now on.

**The end state** is unchanged: rung (b), dependent survival.

## Directives

- **DIRR02-1** · A study describes the war and never changes it: no study adds, alters or cancels an event or moves the end state, and where a study finds the record inconsistent it records a question for an erratum or a checkpoint rather than settling it (the user's design of 24 Nov 2026; R02)
- **DIRR02-2** · Every memorandum whose variables a study covers is written against that study: Part 2 judges its pushes against the study's values and says plainly when the provision's effect contradicts the study and which should give way, and Part 3 records what changed in the area in the study's entry (R02)
- **DIRR02-3** · A study's value is never cited as a measurement: study values are exercise judgments on the R01 scale, an indicator a study gives carries its own provenance, and a figure the study generates carries the X-tag of its study run (X-ST01 and so on) forever (A13a; R02)

## What remains

The first study run, on the areas the user names.

## Notes

1. Stipulated in the provision.
