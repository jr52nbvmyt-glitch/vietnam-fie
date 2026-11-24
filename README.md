<!-- fie v1.0.4 -->
# Vietnam Force-Injection Exercise

A long-running counterfactual: modern forces and capabilities are injected into the Vietnam War from 1 January 1964, one provision at a time, and COMUSMACV reports in numbered memoranda on how each one changes the war. This repository is the whole record — the rules, the procedures, the war as it now stands, every memorandum, and the scripts that keep the books.

Why it is built this way: [DESIGN.md](DESIGN.md).

## Running a memorandum

| You send | You get back |
|---|---|
| A provision — any description of units, weapons, systems, programmes or capabilities | **Part 1:** §1, the provision dossier |
| `CONTINUE` | **Part 2:** §2 integration and second-order effects, §3 changes to existing forces |
| `CONTINUE` | **Part 3:** §4 the course of the war and the revised phases, §5, §6 — plus the updated **War History** and **Trajectory Log** |

**Send each `CONTINUE` in a new thread.** Every part reads what it needs from the repository, so a fresh thread costs far less than carrying the earlier parts along. Effort: medium for Part 1 (research), high for Parts 2 and 3.

## In a new-style project

Attach the repository to the project, put the workers on Opus 5.5 (high, or xhigh for Parts 2 and 3) and the coordinator on whatever is cheapest, and paste the instructions text. Send a provision in the main chat; the coordinator opens a thread for the memorandum. Read each part from its thread; for `CONTINUE`, the coordinator starts a fresh thread for the next part. The coordinator runs one piece of work at a time, and every thread pushes straight to `main`. Project memory may hold your preferences, never the war: figures, findings, events and positions come only from this repository.

## Other commands

| Command | What it does |
|---|---|
| `BASELINE` | Writes the historical war as the starting chapters. Once, before anything else (three parts) |
| `TNA` | The Theater Needs Assessment and the gap register. Once, after BASELINE |
| `CHECKPOINT` | Every ten memoranda: state of the war, one phase's coherence review, an interaction sweep, calibration, trajectory, the bill (two parts) |
| `META` | Every third checkpoint: an audit of the analysis itself, then unexplored terrain (two parts) |
| `VETO <event ID>` | Removes a free-play event and reruns its consequences |
| `ERRATUM <what is wrong>` | Records a correction to a finished memorandum |
| `STATUS` | Where things stand |

## What to read

- `build/memos/NNN/` — each memorandum, part by part, and complete as `MEMO-NNN.md`
- `build/WAR-HISTORY.md` — the whole war as it now stands; ◆ marks what the latest memorandum changed
- `history/TRAJECTORY-LOG.md` — one paragraph per memorandum: the arc of the war across all provisions
- `build/INDEX.md` — every provision in theater · `build/EVENTS.md` — every event · `build/LEDGERS.md` — what pushes each world variable

## Layout

| Path | Holds |
|---|---|
| `instructions/` | The text for the claude.ai project's instructions field |
| `rules/` | `RULES.md` (role and standing rules) and `CONFIG.toml` (settings, floors, limits) |
| `procedures/` | One file per command |
| `schema/` | `FORMATS.md` (every record format) and `VARIABLES.toml` (the world variables) |
| `templates/` | Starting files for manifests, parts and chapters |
| `history/` | The war: chapters, phases, end state, and the registers |
| `memos/`, `reviews/`, `revisions/`, `errata/` | The record of each piece of work |
| `build/` | Generated views. Never edited by hand |
| `scripts/fie.py` | The bookkeeping script |

## Changing the system

Change rules, procedures, formats or scripts only at a checkpoint, never in the middle of a memorandum. Then bump `VERSION`, the `<!-- fie vX -->` header of every Markdown file in `rules/`, `procedures/`, `schema/` and `instructions/` (and `CLAUDE.md`, `README.md`, `DESIGN.md`), the `version` keys in `CONFIG.toml` and `VARIABLES.toml`, and the version in the project's instructions field. `fie.py status` reports any file left behind.
