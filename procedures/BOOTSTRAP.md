<!-- fie v1.0.5 -->
# Bootstrap — printed by `fie.py boot` on the first turn of every thread

The repository is the record. The conversation is scratch. Nothing you need may exist only in the conversation, and nothing in the record may come from memory.

## First turn of a thread

1. **Find or attach the repository.** In a new-style project it is already cloned when the thread starts: find the clone (it holds `scripts/fie.py`). If it is not there, call `add_repo` with the owner and repo the project instructions name and `access: "push"`, run the clone command it returns, and call `register_repo_root`.
2. **Boot, in one call:** `python3 scripts/fie.py boot <command>`, where the command is `provision`, `continue`, `baseline`, `tna`, `checkpoint`, `meta`, `veto` or `erratum` (table below). It checks out `main` and pulls it, runs the status check, and prints the rules, the voice guide, the settings, the formats, the procedure for this command, and — for Parts 2 and 3, checkpoints and meta-checkpoints — the context pack. **Everything it prints is read; do not open those files again in this thread.** If the pull fails, stop and tell me.
3. **Act on the status it printed:**
   - **Version**: its first two numbers must match the version the project instructions expect (1.0 matches 1.0.5). If not, stop and tell me.
   - **Config incomplete**: stop, list the unset values, and ask me for them. Never choose a constraint setting yourself.
   - **Uncommitted changes or unpushed commits**: an earlier turn was interrupted. Tell me in one line what they are, then commit and push them before anything else.
   - **In progress**: if my message is a new provision while a memorandum is open, tell me which part it is at and ask whether to finish it first.
   - **Checkpoint due**: mention it in one line, then do what I asked.
4. **Follow the procedure** it printed.

## Commands

| My message | Procedure |
|---|---|
| A provision: any description of units, weapons, vehicles, aircraft, sensors, infrastructure, programmes or capabilities | `procedures/PART1.md` — opens a new memorandum |
| `CONTINUE` or `C` | The next part of the work in progress: `PART2.md`, `PART3.md`, or the next part of a baseline, checkpoint or meta-checkpoint |
| `BASELINE` | `procedures/BASELINE.md` |
| `TNA` | `procedures/TNA.md` |
| `CHECKPOINT` | `procedures/CHECKPOINT.md` |
| `META` or `META-CHECKPOINT` | `procedures/META.md` |
| `VETO <event ID>` | `procedures/REVISIONS.md` |
| `ERRATUM <what is wrong>` | `procedures/REVISIONS.md` |
| `STATUS` | Run `fie.py status`; report it in plain words; stop |
| Anything else | Answer as yourself, outside the COMUSMACV voice. Change nothing in the repository unless I ask |

Before the first memorandum, `BASELINE` must have run (`fie.py new` refuses otherwise). If I send a provision first, tell me and offer to run `BASELINE`.

## One piece of work at a time

The memoranda form a single sequence: each one edits the chapters the next one reads. So:

- **One thread per part.** Each part of a memorandum runs in a fresh thread: Part 1 in the thread the provision arrives in, then `CONTINUE` in a new thread for Part 2, and again for Part 3. A part reads what it needs from the repository — its own card and pack — so nothing from an earlier part's thread is carried, and the context stays small. BASELINE, checkpoints and meta-checkpoints work the same way, one part per thread; TNA and each revision take one thread.
- **Effort.** Part 1, BASELINE and TNA are research: medium effort is enough. Parts 2 and 3, checkpoints and META are reasoning: high. Higher than high is rarely worth its usage here.
- **Never two at once.** No thread that writes to the repository starts while another such thread has unfinished work. `fie.py status` shows open work; a new memorandum waits until the open one is complete and pushed.
- **If you are a project's coordinator** (a new-style project's main chat, directing threads): start one thread per piece of work above, in order, each after the previous one has pushed. For my `CONTINUE`, start a new thread for the next part of the open work. Parallel threads are allowed only for work that writes nothing to the repository — reading, answering a question, research for me. Report progress from the files the threads send (`build/memos/…`, `build/WAR-HISTORY.md`, `history/TRAJECTORY-LOG.md`), not from your own summary of them.

## Every turn

- **Earlier parts are read from the repository, never from the conversation** — and in summary: the pack carries this memorandum's own card. Read an earlier part's file only for a specific passage the card lacks, found first with `fie.py grep`.
- **Every part ends the same way:**
  1. `python3 scripts/fie.py finish … --push` (or `review … --finish --push`, `baseline --finish --push`). Fix every ERROR and run it again until it passes; read every WARNING and fix it, or make sure the text states the reason for a genuine shortfall (G7). On a clean finish it commits and pushes straight to `main` — never a branch, never a pull request. If it reports the push rejected because `main` moved, stop and tell me rather than merging: two pieces of work have run at once. If it reports any other push failure, tell me — the work is committed locally but survives only as long as this session.
  3. Send me the reading copy the script names, with SendUserFile, display `render`. Do not paste the memorandum into chat.
  4. In chat, at most three sentences, as yourself: anything I should know (a floor shortfall and why, a decision you made, a ripple you followed), then the next command, e.g. *Send CONTINUE for Part 2.*
- **Never edit** a finished part, a register in `history/` (registers are written by the script from blocks in your text), or anything in `build/`.
- **Project memory is not a source.** A project's shared memory may hold my preferences and notes on how the work runs. It never holds, and you never take from it, a figure, finding, event, position, or the state of the war: those come only from the repository. Do not write summaries of memoranda into memory.
- **Economy.** Every tool call re-sends the whole thread plus a large fixed overhead, so the cost of a part is mostly its number of tool calls. Aim for about fifteen. Do not use the task list. Chain shell commands into one call where you can. Load only what the procedure says. Make few, large tool calls: write a file in one Write, change the war with one amend file (`procedures/PART3.md`), run `finish` once more after fixes rather than checking piecemeal. Do not read a file to confirm a write that succeeded. Do not re-read the rules on later turns of the same thread.
