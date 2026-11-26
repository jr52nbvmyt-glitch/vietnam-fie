# R07 — Narrow ranges, honest confidence (v1.0.9)

*A revision of the rules, made on the user's ruling of 25 November 2026 and kept within version 1.0.9 at the user's instruction. It changes how the exercise presents its own estimates. No event is created, altered or cancelled, no end vector moves, no settled position is reversed, and the end state in `history/endstate.toml` is unchanged.*

## Why

The user asks for the ranges on the exercise's estimates to be narrower, because a narrow range is more presentable, and accepts that the real uncertainty may be greater than the range shows. The rules until now told the writer to let the width of the range be the uncertainty, which produced figures such as "150–300" and "2–12 points". The record already carries a confidence label on every judged value and push (`conf`, checked by the script), so the real uncertainty has a place to live that is not the width of the range. This revision moves it there.

## What changes

| File | Change |
|---|---|
| `rules/RULES.md` | A new rule, **A12b — Narrow ranges, honest confidence**. An estimate is a narrow range around the best estimate: about a fifth of its midpoint wide; a share about 5 points; a difference from history about a third of its larger end, spanning zero only when the direction is in doubt. The confidence label carries the real uncertainty and is never dropped: `conf` on every value and push, and a plain word beside a prose figure of low confidence. Where the real uncertainty is much wider than the range, the note or sentence says so once. History's figures and measured indicators are given as their sources give them. A11 points to it. |
| `schema/VARIABLES.toml` | The header's "the width of the range is the uncertainty" is replaced by the A12b guide. |
| `schema/FORMATS.md` | The push format says ranges are narrow and `conf` carries the uncertainty; the three examples are narrowed to fit (4–9 to 6–8 points, 6–12 to 8–11, −45 to −30% to −40 to −34%). |
| `procedures/PART1.md`, `PART3.md`, `STUDY.md` | Where each tells the writer how to set a range, it now points to A12b. |
| `rules/VOICE.md` | One line under *Analysis*: "about 230–250 dead, low confidence" reads; "150–300" does not. |

## The checks

The script already refuses a judged value or push without a confidence label (`conf` must be low, medium or high) and shows the label beside every range in the reading copies, so nothing there needed to change. It has no limit on a range's width, and none is added: the old chapters and memoranda carry wide ranges that stay as written, and a width check would warn on them at every finish. A12b is enforced by the writer and the reviewers, as A12 is.

## Effect on the record

None on the war. Values already in the chapters, studies and memoranda stay as written; they narrow as later memoranda, checkpoints and study re-runs judge them again.

- **DIRR07-1** · The exercise's own estimates are presented as narrow ranges around the best estimate (RULES A12b: about a fifth of the midpoint; a share about 5 points; a difference about a third of its larger end), and the real uncertainty is carried by the confidence label, never dropped, with one plain clause where it is much wider than the range shown; history's figures and measured indicators are given as their sources give them (the user's ruling of 25 Nov 2026; R07)
