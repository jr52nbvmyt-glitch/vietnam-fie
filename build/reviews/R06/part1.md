# R06 — Studies that teach: the primer, the complete inventory, tables and scenes (v1.0.9)

*A revision of the rules, made on the user's rulings of 25 November 2026. It changes how a study is written. No event is created, altered or cancelled, no end vector moves, no settled position is reversed, and the end state in `history/endstate.toml` is unchanged. No study is re-run here.*

## Why

The user asks for a study to learn the area itself, not only to follow this war's trajectory through it. The small arms study did not say what small arms the soldiers carried, and said nothing of the weapons no memorandum had replaced. The user also found paragraphs that took a narrative approach without telling a story: a sentence such as "the M2 carbine was outgunned by the AK-47" is a comparison, and belongs in a table. DIRR05-3 already rules this for all narrative prose; this revision applies it to studies by name. And the user asks that every study carry a complete inventory: for the air war, a table of exact quantities of each type of fixed-wing and rotary-wing aircraft for each branch of each military, with a description of what each is and how it is used.

## What changes

| File | Change |
|---|---|
| `procedures/STUDY.md` | A study now *teaches, then describes*. Step 5 opens with four rules: teach the subject before telling the war, covering what this war left unchanged as well as what it changed; a complete inventory by branch and force, with exact quantities, description and use, the record's figures first and sourced history otherwise, estimates marked; comparisons in tables; narrative passages as scenes from one person's point of view. Two new required sections follow the Summary: `## Primer — <area> explained` and `## Inventory — <area> by branch and force`. Step 3 lets the primer and inventory be researched as far as they need, from sources, never from memory. |
| `templates/study.md` | The Primer and Inventory headings, after the Summary. |
| `rules/VOICE.md` | A new section, *Studies*: teach before you tell, everything that was there, count it, tables for comparisons and scenes for stories, with an invented example of each. |
| `scripts/fie.py` | `check_study` requires `## Primer` and `## Inventory` of a study written or re-run by a STUDY run, and requires a table in the Inventory. A checkpoint folding a study written before v1.0.9 is warned that the sections are missing, not refused. |
| `rules/CONFIG.toml` | The guide for a study's length rises from 5,000–14,000 words to 8,000–22,000, to hold the primer and the inventory. |
| `CLAUDE.md` | The line on studies now says they teach an area, count its inventory, and describe the war in it. |
| Version | 1.0.8 to 1.0.9 in `VERSION`, every file header, `CONFIG.toml`, `VARIABLES.toml` and the instructions field text in `instructions/PROJECT-INSTRUCTIONS.md`. |

The repository asks that the rules change only at a checkpoint. No memorandum is open, the last checkpoint (CP04) closed after memorandum 015, and the change was the user's own request, so it is made now.

## Effect on the record

None on the war. The three studies on file (air war, maritime interdiction, US and ARVN small arms) were written before this rule and have no primer or inventory. They stand as written until each is re-run; `fie.py status` already advises re-runs of the air war and maritime interdiction studies, and a fresh `STUDY` of any area will now write both sections.

- **DIRR06-1** · A study teaches its subject before it tells the war: after its Summary, a Primer sets out what the area is, as a reader new to it would need, covering every weapon, aircraft, vessel, unit or programme in it, what each is and how it was used, including what this war left unchanged; and an Inventory counts every category of item in the area by branch and by force, with exact quantities, a description and its use, the record's own figures where they exist and sourced historical figures otherwise, estimates marked as such; comparisons go in tables and narrative passages are scenes from one person's point of view (the user's rulings of 25 Nov 2026; R06)
