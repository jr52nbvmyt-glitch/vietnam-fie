<!-- fie v1.0.3 -->
# Design — Vietnam Force-Injection Exercise, v1.0.3

*Replaces the V2 project architecture. Written 21 November 2026 from the V2 problems briefing. Target model: Opus 5.5. Storage: this Git repository.*

## 1. What went wrong, in two sentences

The unit of work was the whole war: every memorandum re-narrated 1964–75, so the largest output grew with the war while the context window stayed fixed. And the conversation was treated as the source of truth with storage as a copy of it, so every record passed through a regeneration step — which is where drift, compression and invention got in.

The analytical specification (the role, rules A1–A13, what §1–§6 must contain, the meta-checkpoint) was sound and is carried over almost word for word. What is rebuilt is everything around it.

## 2. Principles

1. **The repository is the record; the conversation is scratch.** Nothing exists only in a thread. Compaction can cost working memory, never record.
2. **Write once, never copy.** Content goes into its file as it is written. Anything derived — cards, index, ledgers, the War History, reading copies — is produced by a script from the records, never by the model from memory.
3. **Change the war; don't retell it.** The war exists once, as chapters. A memorandum edits the chapters it changes; unchanged text carries forward word for word.
4. **Code keeps the books; the model writes the analysis.** Counting floors, checking cross-references, appending registers, building indexes and computing the audit line are done by `scripts/fie.py`.
5. **Every figure carries its provenance**, so estimates cannot harden into metrics.
6. **Bounded reading.** Each part loads a pack built and capped by the script, not "everything that might matter".

## 3. How it is built

### Storage

| Layer | Where | Rule |
|---|---|---|
| **Memoranda** — what was written | `memos/NNN/`: manifest, sources, three parts, its edited chapters | Immutable once a part is finished. Corrected only by errata |
| **The war** — what happened | `history/chapters/P1–P6.md`, `endstate.toml`, `phases.toml` | One copy. Changed only by promoting a memo's or review's edited chapters |
| **Registers** — what was decided | `history/` positions, persons, directives, gaps, Trajectory Log | Appended by the script from blocks in the text; never edited |
| **Views** — what is read | `build/`: index, cards, ledgers, event index, War History, reading copies, packs | Generated. Never edited; rebuilt |

Git keeps every version of everything, so "the originals are gone" cannot recur, and there is no practical size limit: three hundred memoranda at a few hundred KB each, with their chapter copies and reading copies, comes to the order of 100–200 MB, well within what GitHub handles.

### A memorandum

| You send | Claude does | You receive |
|---|---|---|
| A provision | Opens memo NNN; triage into the manifest (provisions, systems, world variables pushed and depended on); researches the specifications on the web; writes §1 with every figure tagged; finishes, commits, pushes | **Part 1** — the dossier |
| CONTINUE | Builds the Part 2 pack (routed cards, variable ledgers, positions, provision index); greps the archive for interactions routing missed; writes §2 and §3 | **Part 2** — integration, channels, findings, §3 |
| CONTINUE | Reads the whole war; stages and edits the chapters this provision changes; writes §4 (the course of the war, the revised phases with their analysis, nulls for the rest), §5, §6, the log entry; updates the end state; the script stamps, promotes and rebuilds | **Part 3**, the **War History**, the **Trajectory Log** |

One thread per memorandum. If a thread grows long, CONTINUE in a new thread resumes from disk.

### The war as chapters

Each phase is a chapter of prose with events as headed entries: `## EV005-3 · Operation SILVER LANCE · 2–9 Mar 1966 · Bong Son Plain, Binh Dinh Province · NEW · 005`. Every event has an origin (HIST, HIST-ALT, CANCELLED, NEW, FREE) and the list of works that created or changed it, which the script maintains. Each chapter carries an end vector: fifteen headline variables in bands against the historical state at the phase's end.

- **Ripple rule.** When a memorandum moves a phase's end vector, the next phase is either revised or its null must answer the change; the checker flags it.
- **End state** is one record (`history/endstate.toml`) with its history. No memorandum can leave Saigon's fate ambiguous again.
- **Scale.** When the chapters outgrow the full-read limit, Part 3 reads in full only what it changes and exact digests of the rest; checkpoints consolidate any chapter flagged as too long.

### Three ways to read the course of the war

1. **§4.0 The course of the war** — written fresh in every memorandum from the chapters: the whole war, 1964 to its end, in COMUSMACV's voice.
2. **The War History** — every chapter as it stands, sent with every memorandum; ◆ marks the events the latest memorandum created or changed.
3. **The Trajectory Log** — one paragraph per memorandum, appended and never rewritten: the arc across all provisions.

### Interactions through world variables

`schema/VARIABLES.toml` defines 57 world variables (night control of hamlets, displacement, VCI strength, Trail tonnage arriving, ARVN self-sufficiency, US political tolerance…). Each provision declares which it pushes, with a band of −3 to +3, and which it depends on. The Part 2 pack routes earlier memoranda by shared variables, weighting cross-dependencies (one provision pushes what another relies on) above parallel pushes. That is how artillery that displaces the population meets a pacification programme that depends on it staying put — which routing by functional system could not see. `fie.py grep` is the second net.

### Provenance

`[U]` stipulated · `[S3]` source 3 in this memo's sources · `[H]` historical · `[E: basis]` estimate · `[D]` derived · `[X-005]` a judgment this exercise made in memo 005 · `[M005]` from memo 005's record. An `[X-…]` figure stays tagged forever; the A13 problem of estimates becoming metrics is caught by the tag travelling with the number.

### The checker

`fie.py finish` refuses a part with structural errors — a missing dossier field, a misnumbered finding, a malformed tag, an undefined source, a deleted event, a bad origin, an out-of-range band, a chain with no lag, a revised phase without its chronicle — and warns on shortfalls against the floors in `rules/CONFIG.toml`. It computes the audit line itself.

## 4. The briefing's problems, and what answers each

| V2 problem | v1.0 answer |
|---|---|
| §1 One memorandum didn't fit in a context window | Three parts, each filed as written; Opus 5.5; capped packs; the war is edited, not retold; digest mode at scale; CONTINUE resumes from disk in a fresh thread |
| §2 Records drift when regenerated | No filing step: the part is the record. Cards are extracted by script from marked blocks in the text. Chapters are edited in place. Git history |
| §3 Always-loaded state grows and duplicates | Nothing is always loaded except a ~400-token instructions field and ~9,000 tokens of rules and formats per thread. Indexes are generated with fixed formats; the model cannot add detail to them |
| §4 Selective retrieval didn't filter, and missed cross-system effects | Routing by shared world variables with cross-dependency weighting, a card cap, and grep as a second net. Checkpoints sweep the most crowded variables in rotation at constant cost |
| §5 Token cost and spikes | No second write of each part; §4 output scales with the provision's effect, not the war's length; checkpoints cost the same every time |
| §6 Instructions pasted by hand and out of date | The instructions field only points at the repository and states a version; `fie.py status` refuses to agree if any file's version differs. No `claude/` prefix, no trailing-space paths, no write-before-read rule. No file is referenced that does not exist |
| §6 Storage limit of 2M tokens | Git |
| §7 Instruction set ~13–16k tokens every turn | Rules ~4.7k and formats ~2.4k once per thread; each part reads only its own procedure (1.6–2.9k); META (2.9k) only when run |
| §7 Re-chronicling the whole war every memo | Chapters amended in place; §4.0 is the through-line |
| §7 Budget contradiction (39% vs "larger than §1 and §2") | Percentages dropped; floors and the rule that §4 is the largest section |
| §7 Undefined CONFIG values | One switch per political constraint, each MODELLED or SUSPENDED; `troop_ceiling` HISTORICAL, NONE or a number; UNSET blocks new memoranda |
| §7 Dates: Phase I from 1961; a 1960 in-service date | Phase I redated January 1964–July 1965; arrival dates separate from in-service dates and never before the campaign opens (A1a) |
| §7 Estimates hardening into metrics | `[X-NNN]` tags; end vectors in bands; no metrics register |
| §7 Historical events tagged as free play | Event origin field: a historical accident is HIST, never FREE (G4) |
| §8 Redesigning during the run | Version 1.0 freezes after the pilot; changes only at checkpoints, with a version bump everywhere |

## 5. Budget on Opus 5.5 (approximate)

| Item | Tokens |
|---|---|
| Fixed overhead of the session (measured in V2) | ~74,000 |
| Instructions field | ~400 |
| Bootstrap reading (BOOTSTRAP, RULES, CONFIG, FORMATS) | ~9,300 |
| Part 1: procedure + variables + web research + output | ~2,000 + 4,000 + 15,000–30,000 + 10,000–15,000 per system |
| Part 2: procedure + pack (capped at ~35,000) + grep + output | ~3,000 + 2,000–35,000 + 2,000 + 15,000–20,000 |
| Part 3: procedure + pack + chapters (full read capped at ~80,000) + edits + output | ~3,000 + 3,000–6,000 + 40,000–80,000 + 10,000–20,000 + 12,000–20,000 |

A mature thread can approach 280,000 tokens by the end of Part 3. Opus 5.5 ran past 287,000 in the planning session without compacting, but if it does compact, nothing is lost: the parts are on disk. Sending Part 3's CONTINUE in a new thread is always safe.

## 6. Known limits

- **The checker verifies structure, not truth.** A fabricated figure with a real-looking `[S3]` passes if `sources.md` lists something. Research discipline and the checkpoint calibration remain the defence; sources carry URLs so they can be checked.
- **Two checks are heuristic** — untagged-figure detection and the designation count. They warn; they do not block.
- **§4.0 is written fresh** each memorandum. It is derived from the chapters and never read back as a source, but its emphasis can wander. The chapters are the war.
- **Chapters will grow.** The floor counts changed events as well as new ones, the procedure prefers altering events to adding them, and checkpoints consolidate long chapters — but growth needs watching.
- **Pushing depends on the GitHub connection.** Until a part is pushed, it lives only in that session.

## 7. New-style projects (v1.0.1)

In a redesigned project a coordinator in the main chat splits work into parallel threads, each a cloud session on its own branch, sharing a project memory. Three of those features would undo protections this design depends on, so the instructions constrain them:

| Feature | Risk | Rule |
|---|---|---|
| Parallel threads | Two memoranda editing the same chapters, each blind to the other | One piece of work at a time; a new memorandum waits until the open one has pushed. Parallel threads only for work that writes nothing |
| A branch per thread | A finished memorandum stranded on an unmerged branch; the next one starts from an old war | Every thread checks out `main`, pulls, and pushes straight back to `main`. No branches, no pull requests. A rejected push means two pieces of work ran at once: stop |
| Shared memory | Summaries written after the fact — the V2 drift — becoming a source | Memory may hold preferences and process notes only; figures, findings, events, positions and the state of the war come only from the repository |

What the new design adds is used as it is: the repository attached to every thread, threads that keep running when the app is closed, the Library collecting the files sent, and separate model and effort settings for coordinator and workers. `fie.py status` warns if a thread is not on `main`.

## 8. Usage (v1.0.3)

The cost of a part is roughly its context multiplied by its tool calls, because every call re-sends the thread. v1.0.0–1.0.2 ran a memorandum's three parts in one thread, so Part 3 carried Part 1's web research and both earlier parts through dozens of small chapter edits. v1.0.3 cuts both factors:

- **A fresh thread per part.** Parts 2 and 3 read the memorandum's own card from the pack instead of the earlier parts.
- **Digest-first reading.** Part 3 reads exact digests of every chapter and the full text only of the chapters it changes.
- **One amend file.** All of a memorandum's changes to the war go in one file applied by `fie.py amend`, instead of an edit call per change.
- **Capped research.** About six searches or fetches per provision in Part 1.
- **Effort by part.** Medium for research parts, high for reasoning parts.

## 9. Starting up

1. Push this repository to GitHub (private). Connect GitHub to Claude and give the Claude app access to it.
2. Create a new claude.ai project for v1.0 so V2's documents cannot be mistaken for the record. Paste `instructions/PROJECT-INSTRUCTIONS.md` (below its line) into the instructions field.
3. Political constraints: set 21 November 2026 — every constraint as historical (MODELLED), no troop ceiling.
4. `BASELINE` (one thread, three parts), then `TNA` (one thread).
5. **Pilot:** re-run V2's four provisions as memoranda 001–004 — land reform with the NACC; police reform with merit selection; the CIA PAG with general officer reform; 2026 BCT/OSUT with TCCC. Three of the four V2 records are unverified, and re-running them is cheaper than carrying them. Fix whatever the pilot exposes, then freeze v1.0.
