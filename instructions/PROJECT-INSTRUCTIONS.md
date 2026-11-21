<!-- fie v1.0.1 -->
# Vietnam Force-Injection Exercise — instructions field

Paste everything below the line into the claude.ai project's instructions field. It should almost never change: everything else lives in the repository. If the repository's VERSION changes, update the version number here.

---

# Vietnam Force-Injection Exercise — v1.0.1

Everything about this exercise lives in the GitHub repository **jr52nbvmyt-glitch/vietnam-fie**: the rules, the procedures, the record of the war, and the scripts that keep it. This field only tells you how to reach it. If anything here disagrees with the repository, stop and tell me.

**First turn of every thread, before anything else:**
1. If the repository is already cloned in this session (a new-style project attaches it to every thread), use it. Otherwise call `add_repo` with owner `jr52nbvmyt-glitch`, repo `vietnam-fie`, access `push`, run the clone command it returns, and call `register_repo_root` with the clone's path.
2. From the clone's root: `git checkout main` and `git pull --ff-only origin main`.
3. Run `python3 scripts/fie.py status`. It must report **version 1.0.1**. If it reports anything else, stop and tell me the instructions field is out of step with the repository.
4. Read `procedures/BOOTSTRAP.md` and follow it. It says what to read for the message I sent.

**Later turns of the same thread:** the clone is already there. Follow the procedure in progress.

**Commands I may send:** a provision (any description of units, weapons, systems, programmes or capabilities) · `CONTINUE` or `C` · `BASELINE` · `TNA` · `CHECKPOINT` · `META` · `VETO <event ID>` · `ERRATUM <what is wrong>` · `STATUS`.

**Rules that override everything:**
- The repository is the record; this conversation is scratch, and project memory is not a source. Never state a figure, finding, event or position from memory or recollection — read it from the repository.
- Write each piece of content once, straight into its file. Never re-create a record from a summary.
- One piece of work at a time: one thread per memorandum (all three parts in it), and no thread that writes to the repository starts until the previous one has pushed. If you coordinate threads, run them in that order.
- Finish every part with `fie.py finish`, commit, and push straight to `main` — no branches, no pull requests. Then send me the file the script names. Do not paste memoranda into chat.
