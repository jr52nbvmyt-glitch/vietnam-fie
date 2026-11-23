<!-- fie v1.0.3 -->
# Bootstrap — read on the first turn of every thread

The repository is the record. The conversation is scratch. Nothing you need may exist only in the conversation, and nothing in the record may come from memory.

## First turn of a thread

1. **Find or attach the repository.** In a new-style project the repository is already attached and cloned when the thread starts: find the clone (it holds `scripts/fie.py`) and work from its root. If it is not there, call `add_repo` with the owner and repo the project instructions name and `access: "push"`, run the clone command it returns, then call `register_repo_root` with the clone's path.
2. **Work on main, up to date.** The war is one sequence: every thread starts from the latest `main` and pushes back to it. Run `git checkout main` (or `git checkout -b main origin/main` if there is no local `main`), then `git pull --ff-only origin main`. If the pull refuses because the histories have diverged, stop and tell me: someone else has written to the record.
3. **Git identity.** If a commit later fails for lack of identity, set it locally: `git config user.name "COMUSMACV (Claude)"` and `git config user.email "noreply@anthropic.com"`.
4. **Status.** Run `python3 scripts/fie.py status` and act on it:
   - **Version**: its first two numbers must match the version the project instructions expect (1.0 matches 1.0.2). If not, stop and tell me: the instructions field and the repository are out of step.
   - **Config incomplete**: stop, list the unset values, and ask me for them. Never choose a constraint setting yourself.
   - **Uncommitted changes or unpushed commits**: an earlier turn was interrupted. Look at `git status` and `git diff --stat`, tell me in one line what they are, then commit and push them before anything else.
   - **In progress**: a memorandum is open. If my message is CONTINUE, resume it; if it is a new provision, tell me memo NNN is open at Part N and ask whether to finish it first.
   - **Checkpoint due**: mention it in one line, then do what I asked.
5. **Read** `rules/RULES.md` in full, `rules/VOICE.md`, `rules/CONFIG.toml`, and `schema/FORMATS.md`.
6. **Read the procedure** for my message (table below) in full, and follow it.

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
  1. `python3 scripts/fie.py finish …` — fix every ERROR and run it again until it passes. Read every WARNING: fix it, or, where it reports a genuine shortfall, make sure the text states the reason (G7).
  2. `git add -A && git commit -m "<what>" && git push origin main`. Push straight to `main`: never leave work on a branch and never open a pull request — the next thread reads `main`, and work anywhere else does not exist for it. If the push is rejected because `main` moved, stop and tell me rather than merging: two pieces of work have run at once. If it fails for any other reason, retry once, then tell me — the work is committed locally but survives only as long as this session.
  3. Send me the reading copy the script names, with SendUserFile, display `render`. Do not paste the memorandum into chat.
  4. In chat, at most three sentences, as yourself: anything I should know (a floor shortfall and why, a decision you made, a ripple you followed), then the next command, e.g. *Send CONTINUE for Part 2.*
- **Never edit** a finished part, a register in `history/` (registers are written by the script from blocks in your text), or anything in `build/`.
- **Project memory is not a source.** A project's shared memory may hold my preferences and notes on how the work runs. It never holds, and you never take from it, a figure, finding, event, position, or the state of the war: those come only from the repository. Do not write summaries of memoranda into memory.
- **Economy.** Every tool call re-sends the whole thread, so the cost of a part is its context times its tool calls. Load only what the procedure says. Make few, large tool calls: write a file in one Write, change the war with one amend file (`procedures/PART3.md`), run `finish` once more after fixes rather than checking piecemeal. Do not read a file to confirm a write that succeeded. Do not re-read the rules on later turns of the same thread.
