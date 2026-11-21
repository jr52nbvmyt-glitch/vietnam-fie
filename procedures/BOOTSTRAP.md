<!-- fie v1.0 -->
# Bootstrap — read on the first turn of every thread

The repository is the record. The conversation is scratch. Nothing you need may exist only in the conversation, and nothing in the record may come from memory.

## First turn of a thread

1. **Attach and clone.** The project instructions name the repository. Call `add_repo` with that owner and repo and `access: "push"`, run the clone command it returns, then call `register_repo_root` with the clone's path. Work from the clone's root.
2. **Git identity.** If a commit later fails for lack of identity, set it locally: `git config user.name "COMUSMACV (Claude)"` and `git config user.email "noreply@anthropic.com"`.
3. **Status.** Run `python3 scripts/fie.py status` and act on it:
   - **Version** must equal the version the project instructions expect. If not, stop and tell me: the instructions field and the repository are out of step.
   - **Config incomplete**: stop, list the unset values, and ask me for them. Never choose a constraint setting yourself.
   - **Uncommitted changes or unpushed commits**: an earlier turn was interrupted. Look at `git status` and `git diff --stat`, tell me in one line what they are, then commit and push them before anything else.
   - **In progress**: a memorandum is open. If my message is CONTINUE, resume it; if it is a new provision, tell me memo NNN is open at Part N and ask whether to finish it first.
   - **Checkpoint due**: mention it in one line, then do what I asked.
4. **Read** `rules/RULES.md` in full, `rules/CONFIG.toml`, and `schema/FORMATS.md`.
5. **Read the procedure** for my message (table below) in full, and follow it.

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

## Every turn

- **One thread per memorandum.** Its three parts run in the same thread, on `CONTINUE`. A checkpoint or meta-checkpoint gets its own thread.
- **If you cannot see an earlier part** in the conversation (compaction, or a new thread), read it from `memos/NNN/`. Never reconstruct it.
- **Every part ends the same way:**
  1. `python3 scripts/fie.py finish …` — fix every ERROR and run it again until it passes. Read every WARNING: fix it, or, where it reports a genuine shortfall, make sure the text states the reason (G7).
  2. `git add -A && git commit -m "<what>" && git push`. If the push fails, retry once; if it still fails, tell me — the work is committed locally but survives only as long as this session.
  3. Send me the reading copy the script names, with SendUserFile, display `render`. Do not paste the memorandum into chat.
  4. In chat, at most three sentences, as yourself: anything I should know (a floor shortfall and why, a decision you made, a ripple you followed), then the next command, e.g. *Send CONTINUE for Part 2.*
- **Never edit** a finished part, a register in `history/` (registers are written by the script from blocks in your text), or anything in `build/`.
- **Context.** Load only what the procedure says. The packs are sized for this; whole earlier memoranda are read only when a card lacks something you need, and `fie.py grep` finds the line first.
