<!-- fie v1.0.9 -->
# Part 1 — Triage and §1 Provision dossier

**Trigger:** a provision arrives and no memorandum is in progress.
**Output:** `memos/NNN/manifest.toml`, `sources.md`, `part1.md`. Reading copy: `build/memos/NNN/Part-1.md`.

## Steps

1. `python3 scripts/fie.py new` — note the memorandum number NNN it opens.
2. **Triage — fill `memos/NNN/manifest.toml`.**
   - One `[[provision]]` per distinct system: `PNNNa`, `PNNNb` … A provision message naming two systems makes two provisions.
   - `quantity`: as stipulated, tagged `[U]`. If the message gives none, choose a realistic first increment and tag it `[E: basis]`.
   - `arrival`: as stipulated, else `default_arrival` from CONFIG. Never before the campaign opens (A1a).
   - `systems`: the functional systems it joins (FIND, FIX, STRIKE, INTERDICT, SECURE, ADVISE, SUBVERT, SUSTAIN).
   - `[[push]]` and `[[depend]]`: every world variable it moves and every variable it relies on, from `schema/VARIABLES.toml`. A push is the provision's own change in the variable's natural unit (v1.0.8, `schema/VARIABLES.toml`): `dlow`, `dhigh` (or `plow`, `phigh` as a percentage of history's figure), `at` (the phase by whose end it is measured), `conf` (low, medium or high) and a `note` giving the mechanism in the unit's terms — "4–9 points more of the Delta's rural population held after dark by the end of 1967", not "noticeable". Present the range narrow, around your best estimate, and carry the real uncertainty in `conf` and, where it is much wider than the range, in one clause of the note (RULES A12b). Where a variable has facets, push the facet the provision acts on (an anti-tank missile pushes `ARVN.effectiveness.anti_armor`, not ARVN effectiveness at large); push the parent only if it acts on every facet alike, and say so in the note. Read each variable's unit and `better` before choosing a sign. This drives routing in Part 2, so be generous with `depend` — the cross-system interactions travel through what a provision depends on. Draft now; refine in Part 2.
   - `links`: earlier memoranda you already know this one must be read against.
   - **Studies.** Then run `python3 scripts/fie.py pack NNN --part 1` and read it: every study (`studies/`) whose tags share a variable with the manifest, with its current values. They are the record's account of the areas this provision enters. Write the dossier against them — what the area already holds, where it is weak, what this provision would be benchmarked against (D7, D10, D13, D16) — and cite a study as `studies/<slug>`, keeping its figures' own tags. Boot listed the studies on file; if the pack loads none, go on.
3. **Ask once if it matters.** Before researching, check the provision against what you need to know: quantity, configuration or variant, arrival date, and any enabler it depends on — satellites, datalinks, fuel, spares, an industrial base — against the `[conditions]` table in `rules/CONFIG.toml`. Where something is unstated, undefined by the conditions, and would change the dossier, put every such question to me in one short message and end the turn; resume Part 1 in the same thread when I answer, and record what I said in the manifest with `[U]`. Do not ask about anything CONFIG already defaults (era, arrival) or anything a reasonable reading settles; say what you assumed in D1 instead.
4. **Research the specifications.** Use web search and fetch: manufacturer data, service publications, official programme documents, reputable defence references. For an institutional or programme provision, the sources are its design, comparable real programmes, and the historical studies of the problem it addresses. Record every source you use in `sources.md` as `[S1] Title — publisher or URL — what it supports`, numbered in order of first use. Cite them in the text. Where no source gives a figure, estimate and tag `[E: basis]`. Never fabricate (A3a). **Budget the research:** about six searches or fetches per provision. Prefer one or two authoritative pages fetched over many searches; stop when every figure in D1–D8 has a source or an honest estimate. Search results stay in the context for the rest of the part, so each one costs again on every later tool call.
5. **Write `memos/NNN/part1.md`** in one Write call, the whole part at once. The file exists from the template. For each provision, one section `## §1.<n> <full designation> — PNNNa` with all sixteen fields below as `### D<k> · <name>` headings. Never abbreviate a field, never write "as with the previous system" (C2, C3). Every figure carries a tag.
6. **Card blocks.** D14, D15 and D16 are written inside their card blocks (the template places them), so the card takes them verbatim. After D16, fill `card:figures` with five to ten tagged bullets: the figures a later memorandum is most likely to need. Write card blocks to stand alone — a later memorandum sees only the card.
7. `python3 scripts/fie.py finish NNN --part 1 --push`, then send `build/memos/NNN/Part-1.md`, and close (BOOTSTRAP, *Every turn*).

## The sixteen fields

| Field | Content |
|---|---|
| **D1 · Designation, manufacturer, in-service date, quantity, unit organisation** | Full designation and variant, manufacturer, real-world in-service date, quantity provided, and how it is organised in theater (units, sections, basing) |
| **D2 · Crew and complement; personnel spaces against the ceiling** | Crew per platform or staff per element, total personnel, and **the personnel spaces it consumes** under CONFIG's troop ceiling setting |
| **D3 · Weapons and payload** | With munition designations and quantities |
| **D4 · Sensors: triple canopy, night, monsoon** | With designations and detection ranges against stated target types — and specifically **performance under triple canopy, at night, and in monsoon** |
| **D5 · Performance** | Range, speed, endurance, altitude, protection |
| **D6 · Communications, datalink, and talking to ARVN** | Architecture, and whether it can talk to ARVN |
| **D7 · Domain conditions** | **Air:** basing, runway length and surface, revetment and hardening needs, and survivability against the *specific* threat — small arms and 12.7mm over the South, 37mm and 57mm AAA over the Trail, SA-2 and MiG-21 over the North. **Ground:** mobility in paddy, canopy and laterite; monsoon degradation. **Naval or riverine:** draught, sea state, the Rung Sat and delta channel constraints |
| **D8 · Logistics footprint** | Fuel, spares, specialist personnel, sustainment rate, and what it needs that RVNAF cannot supply |
| **D9 · Transferability to ARVN** | Could this be handed over under Vietnamization, on what timeline, with what training pipeline, and what happens to it if it is transferred |
| **D10 · Employment envelope** | The conditions under which it performs to specification, and the conditions under which performance collapses: weather, sea state or monsoon, canopy, night, EW environment, radius from base, and tempo sustained over weeks rather than demonstrated once |
| **D11 · Failure modes** | How it breaks, what breaks first, what a partial failure looks like as distinct from a total one, and what the force does during the window it is unavailable |
| **D12 · Degradation curve** | Capability at month one against month twelve: mission-capable rate, crew proficiency, spares depth, and specifically what declines first |
| **D13 · Comparative benchmark** | The in-theater system it displaces or outperforms, named, and the size of the margin. "Better" is not an attribute; a stated multiple or delta against a named baseline is |
| **D14 · Negative specification** | What it cannot do that a reader of everything above might reasonably assume it can. State this explicitly. It is the most useful line in the dossier, because it is what stops §2 inheriting an inflated premise |
| **D15 · What it denies the enemy** | If anything |
| **D16 · Honest verdict** | One paragraph on what it actually buys |

**Institutional and programme provisions** (reforms, training systems, advisory programmes, medical systems): the fields keep their numbers and are read as follows. D3 — *instruments and authorities*: the laws, funds, powers and leverage it brings, and what it can compel. D4 — *information inputs*: what it learns, how, and how reliably in contested hamlets and at night. D5 — *throughput and capacity*: cases, hectares, trainees, patients per month, and the rate limit. D6 — *reporting chain and interface with the GVN and RVNAF*. D7 — *reach and security preconditions*: which provinces, districts and hamlets it covers, and what security it needs to operate. State the reading in the field's first line.

## Rules that bind hardest here

A10a (writing for the reader — a dossier can be exact and still readable), A3 and A3a (real figures, sources, no fabrication), A4 (2026 configurations), A6 (which half of find-and-fix it touches), A11 (precise designations), C2 and C3 (no back-reference, no compression).
