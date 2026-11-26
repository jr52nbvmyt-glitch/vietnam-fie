<!-- fie v1.0.9 -->
# Revisions — VETO and ERRATUM

Finished parts are never edited. The war is changed only through its chapters; a finished record is corrected only by an erratum that points at it.

## VETO `<event ID>` — remove a free-play development (G4)

1. `python3 scripts/fie.py review Rnn --init` (nn = the next revision number). Confirm with `fie.py grep <event ID>` that the event exists and has origin `FREE`; if it is not free play, tell me what it is and stop.
2. Find its consequences: `fie.py grep <event ID>` across the chapters and memoranda, and read the events that follow from it.
3. Stage every chapter that must change: `python3 scripts/fie.py chapters Rnn Pk …`.
4. Edit: the vetoed event becomes `CANCELLED`, its text saying it was vetoed. Rerun its consequences without it — every event that depended on it is altered or cancelled, and anything that now happens instead is a new event `EVRnn-k`. Update end vectors.
5. Write `revisions/Rnn/part1.md`: what was vetoed, what changed in consequence (event by event), and the effect on the end state. If the change reaches an area a study covers (`studies/`; `fie.py grep` the event ID there too), add a `<!-- study <slug> -->` … `<!-- /study -->` block for it, as Part 3 does (`procedures/PART3.md`); the script appends it to the study. If a settled position no longer holds, reverse it in a `<!-- positions -->` block. If the end state changes, edit `history/endstate.toml` (`by = "Rnn"`).
6. `python3 scripts/fie.py review Rnn --finish --push`, send the reading copy and `build/WAR-HISTORY.md`.

## ERRATUM `<what is wrong>` — correct a finished record

1. Find the error: `fie.py grep`. Read the record around it. An erratum may come from a study's *Questions for the record* (`- **Q-n** · ERRATUM · …`); cite the study and the question in `source`.
2. Write `errata/Enn.md` (nn = the next number):
   ```
   # Enn — <one-line title>
   memos: <affected memo numbers, comma-separated>
   location: <file and section, e.g. memos/004/part1.md §1.1 D5>
   wrong: <what the record says, quoted>
   correct: <what it should say, tagged with its provenance>
   source: <how you know>
   consequences: <what later memoranda or chapters relied on it>
   ```
3. Every Part 2 pack that loads an affected memorandum's card also loads this erratum.
4. If the error reached the war — a chapter carries it or relied on it — also run a revision (steps 1, 3–6 of VETO, with the erratum as the reason).
5. `python3 scripts/fie.py build`, commit, push, and tell me in one line what was corrected and what it touched.
