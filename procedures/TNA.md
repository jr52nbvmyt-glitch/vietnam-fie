<!-- fie v1.0.5 -->
# TNA — Theater Needs Assessment

**Trigger:** `TNA`. Runs once, after BASELINE and before the first provision, in its own thread.
**Output:** `reviews/TNA/part1.md`. Reading copy: `build/reviews/TNA/part1.md`.

## Steps

1. `python3 scripts/fie.py review TNA --init`.
2. Read `history/chapters/P1.md` (the situation at the opening date).
3. Write `reviews/TNA/part1.md`, as COMUSMACV on the campaign's opening date: an honest diagnosis of the deficits facing MACV, ranked by how directly each connects to the Republic of Vietnam failing to become a state that can survive.
4. Cover at minimum: finding and fixing the main force; identifying the VCI inside the population; hamlet security and who holds the countryside after dark; the sanctuary problem in Laos and Cambodia and what it does to any theory of attrition; the Trail as a logistics system and the real throughput requirement against its capacity; infiltration by sea and through Sihanoukville; the RVNAF's officer corps, leadership selection, desertion, and corruption; the advisory effort's leverage and its limits; the personnel ceiling and what it forecloses; air power's effectiveness against a dispersed, night-moving, low-signature enemy; the measurement problem and the corruption of the statistics you are given; and the American political clock as a strategic constraint with a finite and unknown expiry.
5. Each in enough detail that I understand both the problem and why it matters. Conclude with which A9 rung you assess is achievable with what you hold on the opening date.
6. After it, a first `<!-- menu -->` block in the format in `procedures/CHECKPOINT.md` step 11: five to eight provisions that would bite hardest on the top gaps.
7. End with a `<!-- gaps -->` block: one line per deficit, ranked — `- **G-1** · <name> · open · <one line> (TNA)`. This is the gap register later memoranda and checkpoints report against.
8. `python3 scripts/fie.py review TNA --finish --push`, send the reading copy, and tell me you are ready to receive provisions.
