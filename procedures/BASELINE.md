<!-- fie v1.0.8 -->
# BASELINE — the historical war as the starting record

**Trigger:** `BASELINE`. Runs once, before the first memorandum, in its own thread, in three parts on `CONTINUE`.
**Output:** `history/chapters/P1.md` … `P6.md`, and `history/baseline-sources.md`. Reading copy: `build/WAR-HISTORY.md`.

The baseline chapters are the historical war from the campaign's opening to the fall of Saigon, written at the chronicle standard. Every memorandum edits them; nothing else in the exercise holds the war. A wrong fact here propagates into every memorandum, so this is research, not recollection.

## Steps

1. `python3 scripts/fie.py baseline --init` creates the six empty chapters with their front matter (every end-vector range 0..0: by definition the baseline is the historical state).
2. **Part 1 of 3:** write P1 and P2. **Part 2:** P3 and P4. **Part 3:** P5 and P6, then finish. Each part ends with a commit and push.
3. For each chapter, replace the empty body with: an overview of the phase's shape; then the events in date order; then `## How the phase ends`. Keep the front matter exactly as created.
4. **Events:** `## EV000-n · <title> · <date> · <place> · HIST · 000`, numbered continuously across the whole war (P1 starts at EV000-1; P2 continues from where P1 ended). Eight to twenty per phase, chosen for what later provisions are likely to bend: the main-force battles, the air campaigns, the pacification programmes, the political crises in Saigon and Washington, the infiltration and the Trail, the offensives. Each event to the chronicle standard in `procedures/PART3.md`: dates, formations on both sides by designation, place, deciding systems, outcome, casualties with their reliability.
5. **Verify.** Use web search for anything you are not certain of — dates, unit designations, casualty ranges. Record sources in `history/baseline-sources.md` as `[S1] Title — publisher or URL — what it supports`, and cite well-established facts `[H]` or `[H#]` with the source number. Where the record itself is disputed, give the range and say so. If a detail cannot be verified, leave it out rather than supply one.
6. Length: about 2,500–5,000 words per chapter. This is the long read the exercise starts from.
7. **Part 3 ends:** `python3 scripts/fie.py baseline --finish --push` (fix any errors), send `build/WAR-HISTORY.md`, and say the exercise is ready for the Theater Needs Assessment (`TNA`) or a first provision.

Write as a historian, not as COMUSMACV: the baseline is the record he inherits, not his memorandum.
