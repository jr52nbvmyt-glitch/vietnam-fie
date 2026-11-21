<!-- fie v1.0 -->
# CHECKPOINT — calibration of the analysis against the war it describes

**Trigger:** `CHECKPOINT`, due every `checkpoint_every` complete memoranda (`fie.py status` says when). Its own thread, two parts on `CONTINUE`. No new provision is introduced.
**Output:** `reviews/CPnn/part1.md`, `part2.md`; chapter fixes staged in `reviews/CPnn/chapters/`. Reading copies in `build/reviews/CPnn/`.

A checkpoint costs the same every time: it reviews the memoranda since the last checkpoint, one phase end to end, and a few variables' interactions — never everything at once. Over successive checkpoints every phase and every crowded variable gets its turn.

## Part 1 — The state of the war

1. `python3 scripts/fie.py review CPnn --init` (nn = the next checkpoint number), then `python3 scripts/fie.py pack CPnn`. Read the pack, then every chapter in `history/chapters/`.
2. **State of the war.** A reassessment against the entire cumulative force, written from the chapters at the chronicle standard: dated, named events with formations, places, systems and outcomes. This is analysis of the war, not a rewrite of it.
3. **Coherence review** of the phase the pack names. Read its chapter end to end against the chapters either side of it, the end state, and the positions register. Every contradiction, thinned account, silently restored enemy capability, or event that no longer follows from its causes: fix it by staging the chapter (`fie.py chapters CPnn Pk`) and editing it, and list each fix with its event ID. If any chapter is flagged as over the size limit, consolidate it here: merge minor events into a single summary event (`EVCPnn-k`, origin `HIST-ALT` or `NEW`), marking each merged event `CANCELLED` with a pointer to the summary, and keep every fact a later memorandum or position relies on.
4. **Interaction sweep.** For each variable the pack suggests, read its ledger: every provision that pushes it or depends on it. For each pair, ask whether their interaction is in the record (`fie.py grep`). Where it is missing, write it — and if it changes the war, edit the chapters. List the variables in a `<!-- swept -->` block.
5. **Cumulative downstream review.** Every chain in the pack: resolved as predicted, resolved differently and why, still running, or compounded into something unanticipated.
6. **Calibration.** Every `[X-…]` judgment on a headline variable in the chapters: what it rests on, its reliability under A13, and whether the memoranda moved it by a traceable mechanism or by assertion. Flag any figure that differs between the chapters and the memoranda, and say which the record should carry (fix the chapter, or file an erratum).
7. **Experience of the war.** Four to six short passages from positions the memoranda rarely occupy — an RF/PF platoon leader, a hamlet chief, a VC district cadre, a PAVN porter on the Trail, an American district advisor, a Saigon ministry official. Each dated and located, and each testing one claim the analysis has made: is the change visible from where this person stands? Where it is not, say what that implies for the claim.

## Part 2 — Trajectory and limits

8. **Revised trajectory.** Where the war goes from here with the force currently held, phase by phase, ending in the A9 call and the reason the next rung is not reached. If the end state changes, edit `history/endstate.toml` and log it (`by = "CPnn"`).
9. **Limiting factors.** The binding constraint on each line of effort, ranked by how directly it blocks the next rung.
10. **Gap register review.** Every gap: its status, what moved it, what would close it. Updated lines go in a `<!-- gaps -->` block.
11. **The bill.** What the force still lacks, ranked.
12. **Phase redraw**, if a memorandum proposed one and the war warrants it (G2): edit `history/phases.toml` (rename, redate, add `P7`…, or set `retired = true`); run `python3 scripts/fie.py baseline --init`, which creates an empty chapter for any new phase and touches nothing else; stage every affected chapter and move events across by the CANCELLED/NEW rule in `procedures/PART3.md`; state in one line what each historical phase became.
13. Any new settled position goes in a `<!-- positions -->` block; any correction to method in a `<!-- directives -->` block (`DIRCPnn-k`).
14. `python3 scripts/fie.py review CPnn --finish`, commit, push, send the two reading copies and `build/WAR-HISTORY.md` if chapters changed, and close with the next memorandum number.
