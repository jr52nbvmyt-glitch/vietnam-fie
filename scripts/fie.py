#!/usr/bin/env python3
"""
fie.py — bookkeeping for the Vietnam Force-Injection Exercise.

The model writes the analysis; this script keeps the books. It never writes
analytical prose. It counts, checks, copies exactly, appends registers and
builds every generated view, so nothing is ever regenerated from memory.
Standard library only (Python 3.11+). Run from anywhere inside the repository.

Commands
  boot COMMAND                        a thread's whole first turn in one call: sync main, status, rules, procedure, pack
  status                              version, config and exercise state (run first in every thread)
  new                                 open the next memorandum: memos/NNN/
  pack NNN --part 2|3                 build the context pack for Part 2 or Part 3
  pack CPnn|MTnn                      build the context pack for a checkpoint or meta-checkpoint
  chapters WORK P2 P3 ... [--drop Pk] stage copies of current chapters for editing in this work
  amend WORK FILE                     apply whole event blocks and phase sections to the chapters in one step
  check NNN --part 1|2|3              validate a part: errors, warnings, and the audit line
  finish NNN --part 1|2|3             check, stamp, promote, append registers, rebuild views
  baseline --init | --finish          create empty chapters / validate and stamp the baseline
  review WORK --init | --finish       WORK = TNA, CPnn, MTnn or Rnn
  build                               rebuild every generated view in build/
  grep WORD [WORD ...]                search the record for lines containing all the words
  study --init AREA [AREA ...]        open the next study run STnn: one part per area (procedures/STUDY.md)
  study STnn --finish --part k        check, promote and publish the study of the run's k-th area
  study fold CPnn|Rnn SLUG [...]      stage studies for a checkpoint (or revision) to fold and re-judge
  pack NNN --part 1                   the studies on a new memorandum's variables, after triage
  pack STnn                           the context pack for the next part of a study run
"""
from __future__ import annotations

import argparse
import json
import re
import signal
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIST = ROOT / "history"
CHAP = HIST / "chapters"
BUILD = ROOT / "build"

SYSTEMS = ["FIND", "FIX", "STRIKE", "INTERDICT", "SECURE", "ADVISE", "SUBVERT", "SUSTAIN"]
CATEGORIES = ["air", "ground", "naval", "riverine", "isr", "infrastructure", "institutional", "medical", "other"]
ORIGINS = ["HIST", "HIST-ALT", "CANCELLED", "NEW", "FREE"]
CHANNELS = ["Displacement", "Bottleneck migration", "Own-force opportunity cost", "Counterfactual erasure",
            "Perverse effect", "Anticipation", "Enemy detection and learning", "Enemy adaptation cost",
            "Cross-boundary feedback", "Open channel"]
LAGS = ["immediate", "weeks", "months", "war-shaping"]
CONSTRAINT_VALUES = ["MODELLED", "SUSPENDED"]
WORK_RE = r"(?:\d{3}|CP\d{2}|MT\d{2}|ST\d{2}|R\d{2}|TNA)"
EVENT_HDR = re.compile(r"^## (EV" + WORK_RE + r"-\d+) · (.+)$", re.M)
TAG_RE = re.compile(r"\[(U|S\d+|H\d*|E:[^\]\n]+|D|X-" + WORK_RE + r"|M\d{3}(?:·S\d+)?)\]")
QTY_UNITS = (r"(?:km|kilometres?|kilometers?|m|metres?|meters?|mm|cm|nm|nmi|ft|feet|kg|t|tonnes?|tons?|lb|lbs|"
             r"kt|knots?|km/h|mph|hours?|hrs?|h|minutes?|min|days?|weeks?|months?|%|percent|personnel|men|"
             r"soldiers|crew|rounds?|litres?|liters?|gallons?|gal|sorties|aircraft|airframes?|vehicles?|"
             r"MHz|GHz|kW|hp|shp|°|seats|beds|advisors|advisers|officers|cadre)")
QTY_RE = re.compile(r"(?<![\w/.-])~?\d[\d,]*(?:\.\d+)?(?:\s?(?:–|-|to)\s?~?\d[\d,]*(?:\.\d+)?)?\s?" + QTY_UNITS + r"(?![A-Za-z])")
CALIBRE_RE = re.compile(r"\b\d{1,3}(?:\.\d)?\s?mm\b(?=\s+(?:howitzers?|guns?|cannons?|mortars?|recoilless|rifles?|rounds?|"
                        r"rockets?|ammunition|AAA|anti-aircraft|machine|automatic|M\d))")
ID_RE = re.compile(r"\b(?:P\d{3}[a-z]|F\d{3}-\d+|EC\d{3}-\d+|C\d{3}-\d+|EV" + WORK_RE + r"-\d+|POS\w+-\d+|REV\w+-\d+|DIR\w+-\d+|G-\d+|E\d{2}|D\d{1,2})\b")
DESIG_RE = re.compile(r"\b(?:[A-Z]{1,5}[/-])*[A-Z]{1,5}-?\d{1,4}(?:[A-Z]{1,3}\d?)?(?:[/-][A-Z0-9]{1,4})*\b"
                      r"|\b\d{1,3}(?:st|nd|rd|th|[A-Z])?(?:\s[A-Z][a-z]+){0,3}\s(?:Division|Regiment|Brigade|Battalion|Group|Squadron|Wing|Corps)\b")
DESIG_EXCLUDE = re.compile(r"^(?:P\d|F\d{3}|EC\d|C\d{3}|EV|POS|REV|DIR|CP\d|MT\d|R\d{2}$|D\d{1,2}$|S\d|H\d|X-|G-|E\d{2}$|A\d{1,2}$|G\d$|B\d$|C\d$|PNNN)")
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
MON_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_ym(s: str) -> str:
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    return f"{MON_ABBR[int(m.group(2))]} {m.group(1)}" if m else s


def phase_heading(p: dict) -> str:
    n = int(p["id"][1:])
    return f"Phase {ROMAN[n] if n < len(ROMAN) else n} — {p['title']} ({fmt_ym(p['start'])} – {fmt_ym(p['end'])})"
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


# ----------------------------------------------------------------------------- basics

def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def load_toml(p: Path) -> dict:
    with open(p, "rb") as f:
        return tomllib.load(f)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9’'\-]+", strip_comments(s)))


def strip_comments(s: str) -> str:
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", s)


def block_bodies(s: str, name: str) -> list[str]:
    return [b.strip() for b in re.findall(r"<!--\s*" + re.escape(name) + r"\s*-->(.*?)<!--\s*/" + re.escape(name) + r"\s*-->", s, flags=re.S)]


def card_blocks(s: str) -> list[tuple[str, str, str]]:
    return [(k, pid or "", body.strip()) for k, pid, body in
            re.findall(r"<!--\s*card:(\w+)(?:\s+(P\d{3}[a-z]))?\s*-->(.*?)<!--\s*/card\s*-->", s, flags=re.S)]


def sections(s: str, level: int) -> list[tuple[str, str]]:
    """Split text into (heading, body) at the given heading level. Text before the first heading is dropped."""
    pat = re.compile(r"^" + "#" * level + r" (.+)$", re.M)
    out, ms = [], list(pat.finditer(s))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(s)
        # stop at any heading of a higher level
        nxt = re.search(r"^#{1," + str(level - 1) + r"} ", s[m.end():end], re.M) if level > 1 else None
        body_end = m.end() + nxt.start() if nxt else end
        out.append((m.group(1).strip(), s[m.end():body_end]))
    return out


def section(s: str, level: int, startswith: str) -> str | None:
    for h, b in sections(s, level):
        if h.startswith(startswith):
            return b
    return None


def paragraphs(s: str) -> list[str]:
    """Prose paragraphs, with heading lines removed (a paragraph may follow its heading without a blank line)."""
    out = []
    for chunk in re.split(r"\n\s*\n", strip_comments(s)):
        body = "\n".join(l for l in chunk.splitlines() if not re.match(r"\s*#{1,6} ", l)).strip()
        if body:
            out.append(body)
    return out


def config() -> dict:
    return load_toml(ROOT / "rules" / "CONFIG.toml")


def variables() -> list[dict]:
    return load_toml(ROOT / "schema" / "VARIABLES.toml")["var"]


def facet_map() -> dict[str, list[str]]:
    """Parent variable ID -> its facet IDs ("<variable>.<facet>")."""
    return {v["id"]: [f"{v['id']}.{f['id']}" for f in v.get("facets", [])] for v in variables()}


def var_ids() -> set[str]:
    """Every variable and every facet."""
    out = set()
    for v, fs in facet_map().items():
        out.add(v)
        out.update(fs)
    return out


def vector_ids() -> list[str]:
    return [v["id"] for v in variables() if v.get("vector")]


def vector_keys() -> list[str]:
    """The keys every end vector (and snapshot) carries: each headline variable, then its facets."""
    fm = facet_map()
    return [k for v in vector_ids() for k in [v] + fm[v]]


def parent(v: str) -> str:
    return ".".join(str(v).split(".")[:2])


def var_def(k: str) -> dict:
    """The definition of a variable or facet: kind, unit, better and (for a ladder) rungs."""
    for x in variables():
        if x["id"] == k:
            return x
        for f in x.get("facets", []):
            if f"{x['id']}.{f['id']}" == k:
                d = dict(f)
                if d.get("kind") == "ladder" and "rungs" not in d:
                    d["rungs"] = re.findall(r"(\d+) [a-z]", d.get("unit", ""))
                return d
    return {}


# The scales. From v1.0.8 (R03) every value is in its variable's natural unit (schema/VARIABLES.toml).
# The retired scales are history: whole-number bands (-3..+3, memoranda 001-010) read through LEGACY,
# and -10..+10 ranges (memoranda 011-013, and chapter values before R03, now kept in `was`).
SCALE = 10
LEGACY = {0: (0, 0), 1: (2, 4), 2: (5, 7), 3: (8, 10)}
LEGACY_LAST_MEMO = 10
SCALE_LAST_MEMO = 13
CONFS = ("low", "medium", "high", "unjudged")
PUSH_CONFS = ("low", "medium", "high")
VAL_ORDER = ("hist", "src", "low", "high", "dlow", "dhigh", "plow", "phigh", "conf", "binding", "was", "note")
FORMS = (("low", "high"), ("dlow", "dhigh"), ("plow", "phigh"))
SRC_RE = re.compile(r"\[(?:H\d*|S\d+|M\d{3}(?:·S\d+)?|R\d{2}·S\d+|E: [^\]]+)\]")


def legacy_range(b: int) -> tuple[int, int]:
    lo, hi = LEGACY[min(3, abs(b))]
    return (lo, hi) if b >= 0 else (-hi, -lo)


def num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def form(v) -> tuple[str, str] | None:
    """Which form a value or push is written in: absolute (low/high), difference (dlow/dhigh) or percent (plow/phigh)."""
    if isinstance(v, dict):
        for f in FORMS:
            if f[0] in v or f[1] in v:
                return f
    return None


def rng(v):
    """(low, high) of a value in whatever form it is written, or None if unjudged. Comparable only within one form."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return legacy_range(v)
    f = form(v)
    if f and num(v.get(f[0])) and num(v.get(f[1])):
        return (v[f[0]], v[f[1]])
    return None


def vkey(v):
    """Everything that makes a value what it is, for telling whether it moved."""
    if not isinstance(v, dict):
        return v
    return tuple((k, v.get(k)) for k in ("hist", "low", "high", "dlow", "dhigh", "plow", "phigh", "conf"))


def push_range(x: dict):
    return rng(x["band"]) if "band" in x else rng(x)


def mid(r) -> float:
    return 0.0 if r is None else (r[0] + r[1]) / 2


def n(x) -> str:
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return f"{x:,}" if isinstance(x, int) else str(x)


def sn(x) -> str:
    return ("+" if num(x) and x > 0 else "") + n(x)


def fmt_rng(r) -> str:
    if r is None:
        return "unjudged"
    return f"{r[0]:+d}" if r[0] == r[1] else f"{r[0]:+d}..{r[1]:+d}"


def fmt_val(v) -> str:
    """A value as a reader sees it: this war's figure (or its difference from history), and history's figure."""
    if v is None:
        return "—"
    if isinstance(v, int) and not isinstance(v, bool):
        return f"{v:+d} (old band ≈ {fmt_rng(legacy_range(v))})"
    if not isinstance(v, dict):
        return str(v)
    hist = f"history {n(v['hist'])}" if "hist" in v else ""
    f = form(v)
    if v.get("conf") == "converted" or (f and f[0] == "low" and "hist" not in v and "src" not in v):
        r = rng(v)
        return (fmt_rng(r) if r else "unjudged") + f" ({v.get('conf', '')}, v1.0.6 scale)"
    if f is None or v.get("conf") == "unjudged":
        return "unjudged" + (f" ({hist})" if hist else "")
    a, b = v.get(f[0]), v.get(f[1])
    if f[0] == "low":
        s = n(a) if a == b else f"{n(a)}–{n(b)}"
    elif f[0] == "dlow":
        s = (sn(a) if a == b else f"{sn(a)} to {sn(b)}") + " against history"
    else:
        s = (f"{sn(a)}%" if a == b else f"{sn(a)}% to {sn(b)}%") + " against history"
    tail = [x for x in (hist if f[0] == "low" else "", v.get("conf", "")) if x]
    return s + (f" ({'; '.join(tail)})" if tail else "")


def fmt_push(x: dict) -> str:
    if "band" in x:
        return f"{int(x['band']):+d} [old band ≈ {fmt_rng(legacy_range(int(x['band'])))}]"
    f = form(x)
    if f and f[0] == "low":
        return fmt_rng(push_range(x)) + " [v1.0.6 scale]" + (f" ({x['conf']})" if x.get("conf") else "")
    a, b = (x.get(f[0]), x.get(f[1])) if f else (None, None)
    pct = "%" if f and f[0] == "plow" else ""
    s = f"{sn(a)}{pct}" if a == b else f"{sn(a)}{pct} to {sn(b)}{pct}"
    unit = var_def(x.get("var", "")).get("unit", "")
    return s + (f" months" if x.get("months") else (f" of history's figure" if pct else f" [{unit}]")) \
        + (f" by the end of {x['at']}" if x.get("at") else "") + (f" ({x['conf']})" if x.get("conf") else "")


def toml_value(x) -> str:
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, (int, float)):
        return str(x)
    if isinstance(x, dict):
        keys = [k for k in VAL_ORDER if k in x] + [k for k in x if k not in VAL_ORDER]
        return "{ " + ", ".join(f"{k} = {toml_value(x[k])}" for k in keys) + " }"
    if isinstance(x, list):
        return "[" + ", ".join(toml_value(i) for i in x) + "]"
    return json.dumps(str(x), ensure_ascii=False)


def dump_front_matter(fm: dict) -> str:
    """Serialise a chapter's front matter: scalars, then [end_vector], then [snapshot] if any."""
    out = [f"{k} = {toml_value(v)}" for k, v in fm.items() if not isinstance(v, dict)]
    for sec in [k for k, v in fm.items() if isinstance(v, dict)]:
        out.append(f"\n[{sec}]")
        for k, v in fm[sec].items():
            out.append(f'"{k}" = {toml_value(v)}' if "." in k else f"{k} = {toml_value(v)}")
    return "\n".join(out)


def check_value(label: str, k: str, v, errors: list, warnings: list):
    """Validate one end-vector, snapshot or study value in natural units (v1.0.8)."""
    if isinstance(v, int) and not isinstance(v, bool):
        errors.append(f"{label}: {k} = {v} is an old band; from v1.0.8 write {{ hist, src, low, high, conf, note }} in the variable's unit")
        return
    if not isinstance(v, dict):
        errors.append(f"{label}: {k} must be an inline table {{ hist, src, low, high, conf, note }}")
        return
    unknown = [x for x in v if x not in VAL_ORDER]
    if unknown:
        errors.append(f"{label}: {k} has unknown field(s) {', '.join(unknown)}")
    d = var_def(k)
    kind = d.get("kind", "count")
    conf = v.get("conf")
    if conf == "converted":
        errors.append(f"{label}: {k} conf 'converted' was retired at R03: judge it in units or mark it unjudged")
    elif conf not in CONFS:
        errors.append(f"{label}: {k} conf {conf!r} must be one of {', '.join(CONFS)}")
    forms = [f for f in FORMS if f[0] in v or f[1] in v]
    if conf == "unjudged":
        if forms:
            errors.append(f"{label}: {k} is unjudged but carries a range")
    elif conf in PUSH_CONFS:
        if len(forms) != 1:
            errors.append(f"{label}: {k} needs exactly one range: low/high (this war's figure), dlow/dhigh (difference from history) or plow/phigh (% of history's figure)")
        else:
            f = forms[0]
            lo, hi = v.get(f[0]), v.get(f[1])
            if not (num(lo) and num(hi)):
                errors.append(f"{label}: {k} needs numbers for {f[0]} and {f[1]}")
            elif lo > hi:
                errors.append(f"{label}: {k} {f[0]} {lo} is above {f[1]} {hi}")
            elif f[0] == "low" and kind == "share" and not (0 <= lo and hi <= 100):
                errors.append(f"{label}: {k} is a share: {lo}..{hi} must lie within 0..100")
            elif f[0] == "low" and kind == "ladder" and not (1 <= lo and hi <= len(d.get("rungs", [])) and float(lo).is_integer() and float(hi).is_integer()):
                errors.append(f"{label}: {k} is a ladder: low and high are rung numbers 1..{len(d.get('rungs', []))}")
            if f[0] == "low" and "hist" not in v:
                errors.append(f"{label}: {k} gives this war's figure (low/high) without history's figure beside it — add hist and src, or write the difference from history (dlow/dhigh or plow/phigh)")
            if f[0] == "plow" and "hist" not in v and not str(v.get("note", "")).strip():
                warnings.append(f"{label}: {k} gives a percentage of history's figure with neither the figure nor a note")
        if not str(v.get("note", "")).strip():
            warnings.append(f"{label}: {k} is judged but has no note saying what the range means on the ground")
    if ("hist" in v) != ("src" in v):
        errors.append(f"{label}: {k} carries one of hist/src without the other — history's figure goes with its source")
    if "hist" in v and not num(v["hist"]):
        errors.append(f"{label}: {k} hist must be a number in the unit (history's figure at the phase's end)")
    if "src" in v and not SRC_RE.search(str(v["src"])):
        errors.append(f"{label}: {k} src needs a provenance tag ([H40], [S3], [M005·S2], [R03·S1] or [E: basis])")


def check_vector(label: str, vec: dict, errors: list, warnings: list):
    keys = vector_keys()
    fm_ = facet_map()
    for k in keys:
        if k not in vec:
            errors.append(f"{label} lacks {k}")
    for k, v in vec.items():
        if k not in keys:
            errors.append(f"{label} has '{k}', which is not a headline variable or one of its facets")
            continue
        check_value(label, k, v, errors, warnings)
    for pv in vector_ids():
        judged = [f for f in fm_[pv] if isinstance(vec.get(f), dict) and vec[f].get("conf") not in (None, "unjudged")]
        b = vec.get(pv, {}).get("binding") if isinstance(vec.get(pv), dict) else None
        if judged and not b:
            errors.append(f"{label}: {pv} has judged facets but names no binding facet (binding = \"<facet>\")")
        if b and f"{pv}.{b}" not in fm_[pv]:
            errors.append(f"{label}: {pv} binding '{b}' is not one of its facets ({', '.join(f.split('.')[-1] for f in fm_[pv]) or 'none'})")


def phases(include_retired: bool = False) -> list[dict]:
    ps = load_toml(HIST / "phases.toml")["phase"]
    return ps if include_retired else [p for p in ps if not p.get("retired")]


def phase_ids() -> list[str]:
    return [p["id"] for p in phases()]


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


# ----------------------------------------------------------------------------- work dirs and manifests

def work_dir(token: str) -> Path:
    if re.fullmatch(r"\d{3}", token):
        return ROOT / "memos" / token
    if re.fullmatch(r"(?:CP|MT|ST)\d{2}|TNA", token):
        return ROOT / "reviews" / token
    if re.fullmatch(r"R\d{2}", token):
        return ROOT / "revisions" / token
    die(f"'{token}' is not a work token (NNN, CPnn, MTnn, STnn, Rnn or TNA)")


def memo_tokens() -> list[str]:
    d = ROOT / "memos"
    return sorted(p.name for p in d.iterdir() if p.is_dir() and re.fullmatch(r"\d{3}", p.name)) if d.exists() else []


def manifest(token: str) -> dict:
    p = work_dir(token) / "manifest.toml"
    if not p.exists():
        die(f"{rel(p)} not found")
    try:
        return load_toml(p)
    except tomllib.TOMLDecodeError as e:
        die(f"{rel(p)} is not valid TOML: {e}")


def manifests(statuses=("part2", "complete")) -> list[tuple[str, dict]]:
    out = []
    for t in memo_tokens():
        try:
            m = load_toml(work_dir(t) / "manifest.toml")
        except Exception:
            continue
        if m.get("status") in statuses:
            out.append((t, m))
    return out


def set_manifest_field(token: str, key: str, value_toml: str):
    p = work_dir(token) / "manifest.toml"
    s = read(p)
    pat = re.compile(r"^" + re.escape(key) + r"\s*=.*$", re.M)
    if pat.search(s):
        s = pat.sub(f"{key} = {value_toml}", s, count=1)
    else:
        s = f"{key} = {value_toml}\n" + s
    write(p, s)


STATUS_ORDER = ["open", "part1", "part2", "complete"]


def status_at_least(m: dict, st: str) -> bool:
    return STATUS_ORDER.index(m.get("status", "open")) >= STATUS_ORDER.index(st)


# ----------------------------------------------------------------------------- chapters and events

def parse_chapter(text: str) -> tuple[dict, str, str]:
    """Return (front matter dict, front matter raw, body)."""
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n?", text, flags=re.S)
    if not m:
        return {}, "", text
    try:
        fm = tomllib.loads(m.group(1))
    except tomllib.TOMLDecodeError as e:
        fm = {"_error": str(e)}
    return fm, m.group(1), text[m.end():]


def parse_events(body: str) -> list[dict]:
    evs = []
    ms = list(EVENT_HDR.finditer(body))
    for i, m in enumerate(ms):
        nxt = re.search(r"^#{1,2} ", body[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(body)
        fields = [f.strip() for f in m.group(2).split(" · ")]
        ev = {"id": m.group(1), "raw_header": m.group(0), "start": m.start(), "end": end,
              "text": body[m.start():end], "body": body[m.end():end], "ok": len(fields) >= 5}
        if ev["ok"]:
            ev["works"] = [w.strip() for w in fields[-1].split(",") if w.strip()]
            ev["origin"] = fields[-2]
            ev["place"] = fields[-3]
            ev["date"] = fields[-4]
            ev["title"] = " · ".join(fields[:-4])
        evs.append(ev)
    return evs


def event_key_text(ev: dict) -> str:
    """Event text with the works field removed, whitespace-normalised, for change detection."""
    hdr = ev["raw_header"]
    if ev.get("ok"):
        hdr = hdr.rsplit(" · ", 1)[0]
    return re.sub(r"\s+", " ", hdr + ev["body"]).strip()


def date_key(d: str):
    y = re.search(r"\b(19[5-9]\d)\b", d)
    if not y:
        return None
    mo = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", d, re.I)
    day = re.match(r"\s*(?:early|mid|late)?\s*(\d{1,2})\b", d)
    return (int(y.group(1)), MONTHS[mo.group(1).lower()] if mo else 0, int(day.group(1)) if day and mo else 0)


def all_events(extra: dict[str, str] | None = None) -> dict[str, tuple[str, dict]]:
    """Map event ID → (phase, event) across history chapters, with staged overrides in `extra` {phase: text}."""
    out = {}
    for pid in [p["id"] for p in phases(include_retired=True)]:
        text = (extra or {}).get(pid) or read(CHAP / f"{pid}.md")
        if not text:
            continue
        _, _, body = parse_chapter(text)
        for ev in parse_events(body):
            out.setdefault(ev["id"], (pid, ev))
    return out


def touched_events(token: str, pid: str, staged_text: str) -> list[dict]:
    """Events in a staged chapter that this work created or changed."""
    _, _, new_body = parse_chapter(staged_text)
    _, _, old_body = parse_chapter(read(CHAP / f"{pid}.md"))
    old = {e["id"]: event_key_text(e) for e in parse_events(old_body)}
    out = []
    for ev in parse_events(new_body):
        if token in ev.get("works", []) or ev["id"] not in old or old[ev["id"]] != event_key_text(ev):
            out.append(ev)
    return out


def stamp_chapter(token: str, pid: str, path: Path):
    """Add the work token to the works field of every touched event and set last_revised. Idempotent."""
    text = read(path)
    touched = {e["id"] for e in touched_events(token, pid, text)}
    fm, fm_raw, body = parse_chapter(text)

    def fix(m):
        eid, rest = m.group(1), m.group(2)
        if eid not in touched:
            return m.group(0)
        fields = rest.split(" · ")
        if len(fields) < 5:
            return m.group(0)
        ws = [w.strip() for w in fields[-1].split(",") if w.strip()]
        if token not in ws:
            ws.append(token)
        fields[-1] = ",".join(ws)
        return f"## {eid} · " + " · ".join(fields)

    body = EVENT_HDR.sub(fix, body)
    if touched:
        fm_raw = re.sub(r'^last_revised\s*=.*$', f'last_revised = "{token}"', fm_raw, count=1, flags=re.M)
    write(path, f"+++\n{fm_raw}\n+++\n{body}")


def check_chapter(text: str, pid: str, errors: list, warnings: list, label: str, all_ids: dict):
    fm, _, body = parse_chapter(text)
    if not fm:
        errors.append(f"{label}: no +++ front matter")
        return
    if "_error" in fm:
        errors.append(f"{label}: front matter is not valid TOML: {fm['_error']}")
        return
    if fm.get("phase") != pid:
        errors.append(f"{label}: front matter phase is '{fm.get('phase')}', expected '{pid}'")
    check_vector(f"{label}: end_vector", fm.get("end_vector", {}), errors, warnings)
    ph = next((p for p in phases() if p["id"] == pid), {})
    if ph.get("snapshot"):
        snap = fm.get("snapshot")
        if not isinstance(snap, dict):
            errors.append(f"{label}: phase {pid} has a snapshot date ({ph['snapshot']}) but the chapter has no [snapshot] table")
        else:
            check_vector(f"{label}: snapshot", snap, errors, warnings)
    last = None
    for ev in parse_events(body):
        if not ev["ok"]:
            errors.append(f"{label}: event header for {ev['id']} needs five fields after the ID: title · date · place · origin · works")
            continue
        if ev["origin"] not in ORIGINS:
            errors.append(f"{label}: {ev['id']} origin '{ev['origin']}' is not one of {', '.join(ORIGINS)}")
        owner = all_ids.get(ev["id"])
        if owner and owner[0] != pid:
            errors.append(f"{label}: {ev['id']} also appears in chapter {owner[0]}")
        k = date_key(ev["date"])
        if k is None:
            warnings.append(f"{label}: {ev['id']} date '{ev['date']}' has no recognisable year")
        elif last and k < last:
            warnings.append(f"{label}: {ev['id']} ({ev['date']}) is out of date order")
        last = k or last
    if words(body) > config()["limits"]["chapter_words_warn"]:
        warnings.append(f"{label}: {words(body):,} words, over {config()['limits']['chapter_words_warn']:,} — flag it for consolidation at the next checkpoint")
    ids = [e["id"] for e in parse_events(body)]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errors.append(f"{label}: duplicate event IDs {', '.join(sorted(dup))}")
    check_tags(body, errors, label, x_required=True)


# ----------------------------------------------------------------------------- tags and figures

VALID_TAG = re.compile(r"(?:U|S\d+|H\d*|D|E:\s*\S.*|M\d{3}(?:·S\d+)?|X-" + WORK_RE + r")")
NEAR_MISS = re.compile(r"(?:E|E\s.*|E;.*|S|S-?\d.*|H-\d.*|X|X-.*|X\d.*|M\d{1,2}|M\d{4,}|M-\d.*)")


def check_tags(s: str, errors: list, label: str, sources: set[int] | None = None, token: str | None = None,
               x_required: bool = False):
    """Reject malformed provenance tags; ignore ordinary bracketed words like [sic] or [months]."""
    s = strip_comments(s)
    for m in re.finditer(r"\[([^\[\]\n]{1,160})\](?!\()", s):
        inner = m.group(1).strip()
        if VALID_TAG.fullmatch(inner):
            if sources is not None and re.fullmatch(r"S\d+", inner) and int(inner[1:]) not in sources:
                errors.append(f"{label}: [{inner}] is not defined in sources.md")
            if re.fullmatch(r"M\d{3}(?:·S\d+)?", inner) and not (ROOT / "memos" / inner[1:4]).exists():
                errors.append(f"{label}: [{inner}] refers to a memo that does not exist")
            if token and inner.startswith("X-") and re.fullmatch(r"\d{3}", inner[2:]) and re.fullmatch(r"\d{3}", token) \
                    and int(inner[2:]) > int(token):
                errors.append(f"{label}: [{inner}] refers to a later memo")
        elif NEAR_MISS.fullmatch(inner):
            if inner == "X" and not x_required:
                errors.append(f"{label}: [X] needs its work number — write [X-NNN]")
            else:
                errors.append(f"{label}: malformed tag [{inner}] — see schema/FORMATS.md §3")


def untagged_figures(s: str) -> list[str]:
    s = strip_comments(s)
    out = []
    for para in re.split(r"\n\s*\n|\n(?=\s*[-*|] )", s):
        para = "\n".join(l for l in para.splitlines() if not re.match(r"\s*#{1,6} ", l))
        for sent in re.split(r"(?<=[.;])\s+(?=[A-Z(])", para):
            if TAG_RE.search(sent):
                continue
            probe = TAG_RE.sub(" ", sent)
            probe = ID_RE.sub(" ", probe)
            probe = CALIBRE_RE.sub(" ", probe)
            probe = re.sub(r"\b(?:[A-Z]{1,5}[/-])*[A-Z]{1,5}-?\d[\w/-]*", " ", probe)  # designations
            if QTY_RE.search(probe):
                out.append(re.sub(r"\s+", " ", sent.strip())[:140])
    return out


def designations(s: str) -> set[str]:
    s = ID_RE.sub(" ", TAG_RE.sub(" ", strip_comments(s)))
    s = re.sub(r"^#+ .*$", " ", s, flags=re.M)
    found = set()
    for m in DESIG_RE.finditer(s):
        d = m.group(0)
        if DESIG_EXCLUDE.match(d) or re.fullmatch(r"\d+", d):
            continue
        if not re.search(r"\d", d):
            continue
        found.add(d)
    return found


def sources_defined(token: str) -> set[int]:
    return {int(n) for n in re.findall(r"^\[S(\d+)\]\s+\S", read(work_dir(token) / "sources.md"), flags=re.M)}


# ----------------------------------------------------------------------------- studies (v1.0.7)
#
# A study is a deep account of one area of the war (the air war, CIDG, the Delta …) as the record stands,
# phase by phase. It lives in studies/<slug>.md and is never part of the chapters. It describes: it adds no
# event and moves no end state. Its judgments go where the record keeps judgments: a headline variable or
# facet into the chapters' end vectors (only entries still unjudged or converted), anything else into the
# study's own [values]. Memoranda append dated "since this study" entries through the script; checkpoints
# fold them into the text.

STUDIES = ROOT / "studies"
STUDY_REQUIRED = ["Summary", "Judgments", "Questions for the record", "Sources", "Since this study"]
# From v1.0.9 (R06) a study written or re-run by a STUDY run teaches its subject and counts it: these two
# sections are required when a STUDY run finishes a part (teaching=True); a checkpoint or revision folding an
# older study is warned, not refused.
STUDY_TEACHING = ["Primer", "Inventory"]
VALUE_LINE = re.compile(r"^-\s*value\s*·\s*(\S+)\s*·\s*(P\d+)\s*·\s*(Δ?)\s*([+-]?[\d,]*\.?\d+)\s*\.\.\s*([+-]?[\d,]*\.?\d+)\s*·\s*(low|medium|high)\s*·\s*(.+)$")
QUESTION_LINE = re.compile(r"^- \*\*Q-\d+\*\* · (?:ERRATUM|CHECKPOINT|RESOLVED|STANDS)\b[^·]* · \S")
STUDY_BLOCK = re.compile(r"<!--\s*study\s+([a-z0-9-]+)\s*-->(.*?)<!--\s*/study\s*-->", re.S)
AGAINST_RE = re.compile(r"<!--\s*against\s+([a-z0-9-]+)\s*:\s*(consistent|contradicts)\s*-->")
SINCE_RE = re.compile(r"<!--\s*since\s+(\S+)\s*-->(.*?)<!--\s*/since\s*-->", re.S)


def slugify(s: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"^(?:the|a|an)-", "", out)[:48] or "area"


def study_slugs() -> list[str]:
    return sorted(p.stem for p in STUDIES.glob("*.md")) if STUDIES.exists() else []


def study_text(slug: str) -> str:
    return read(STUDIES / f"{slug}.md")


def tag_keys(tags) -> list[str]:
    """Every key a study's tags cover: a variable tag covers the variable and its facets; a facet tag, itself."""
    fm_ = facet_map()
    out = []
    for t in tags or []:
        for k in [t] + fm_.get(t, []):
            if k not in out:
                out.append(k)
    return out


def study_parents(fm: dict) -> set[str]:
    return {parent(t) for t in fm.get("tags", []) or []}


def matching_studies(vars_: set[str]) -> list[str]:
    """Studies sharing a variable (by parent) with the given set — the routing a memorandum uses."""
    want = {parent(v) for v in vars_}
    out = []
    for slug in study_slugs():
        fm = parse_chapter(study_text(slug))[0]
        if study_parents(fm) & want:
            out.append(slug)
    return out


def since_entries(body: str) -> list[tuple[str, str]]:
    return [(t, b) for t, b in SINCE_RE.findall(body)]


def value_lines(text: str) -> list[tuple[str, str, dict]]:
    out = []
    for line in text.splitlines():
        m = VALUE_LINE.match(line.strip())
        if m:
            def f_(s):
                x = float(s.replace(",", ""))
                return int(x) if x.is_integer() else x
            lo_k, hi_k = ("dlow", "dhigh") if m.group(3) else ("low", "high")
            out.append((m.group(1), m.group(2), {lo_k: f_(m.group(4)), hi_k: f_(m.group(5)), "conf": m.group(6),
                                                   "note": m.group(7).strip()}))
    return out


def study_values(fm: dict, body: str) -> dict[tuple[str, str], tuple[dict, str]]:
    """(key, phase) -> (value, where it was set): the study's own [values], overridden by later since-entries."""
    vals = {}
    for pid, tbl in (fm.get("values") or {}).items():
        if isinstance(tbl, dict):
            for k, v in tbl.items():
                vals[(k, pid)] = (v, fm.get("folded") or fm.get("written") or "study")
    for tok, txt in since_entries(body):
        for k, pid, v in value_lines(txt):
            vals[(k, pid)] = (v, f"since {tok}")
    return vals


def values_table(fm: dict, body: str, only: set[str] | None = None) -> str:
    """The study's current values, one row per key it covers: headline keys read from the chapters, the rest
    from the study. Generated; never written by hand."""
    vk = set(vector_keys())
    vals = study_values(fm, body)
    ph = phase_ids()
    snap_pid = next((p["id"] for p in phases() if p.get("snapshot")), None)
    chap = {p: parse_chapter(read(CHAP / f"{p}.md"))[0] for p in ph}
    rows = []
    for k in tag_keys(fm.get("tags", [])):
        if only is not None and parent(k) not in only:
            continue
        if k in vk:
            cells = [fmt_val((chap[p].get("end_vector") or {}).get(k)) for p in ph]
            snap = fmt_val((chap[snap_pid].get("snapshot") or {}).get(k)) if snap_pid else ""
            where = "chapters"
        else:
            cells = [fmt_val(vals[(k, p)][0]) if (k, p) in vals else "—" for p in ph]
            snap = ""
            srcs = sorted({vals[(k, p)][1] for p in ph if (k, p) in vals})
            where = "study" + (f" ({', '.join(srcs)})" if srcs else ", not yet judged")
        rows.append(f"| {k} | " + " | ".join(cells) + f" | {snap} | {where} |")
    if not rows:
        return "No tagged variables."
    return ("| Variable | " + " | ".join(ph) + " | 1974 snapshot | Held in |\n|---|" + "---|" * (len(ph) + 2) + "\n"
            + "\n".join(rows) + "\n\n*Values in each variable's natural unit (schema/VARIABLES.toml): this war's figure with history's beside it, "
            "or the difference from history's figure; low, medium, high = confidence; unjudged = not yet judged. "
            "Headline variables and their facets live in the chapters' end vectors; the rest in the study. A study value "
            "set before R03 is on the retired −10..+10 scale until the study is next folded.*")


def study_sources(body: str) -> dict[int, str]:
    sec = section(body, 2, "Sources") or ""
    return {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\[S(\d+)\]\s+(.+)$", sec, re.M)}


def study_render(slug: str, text: str | None = None, short: bool = False, only: set[str] | None = None) -> str:
    """A study as a pack or a reading copy shows it: its text with the current values table after the summary.
    short: summary, values, questions and the since-entries only."""
    text = text if text is not None else study_text(slug)
    fm, _, body = parse_chapter(text)
    title = re.search(r"^# (.+)$", body, re.M)
    head = (f"## Study: {fm.get('area', slug)} (`studies/{slug}.md`)\n*Written {fm.get('written', '?')} · reflects the record "
            f"after memo {fm.get('as_of', '?')} · last folded {fm.get('folded') or '—'} · tags: {', '.join(fm.get('tags', []))}"
            f"{' · RE-RUN ADVISED: ' + str(fm.get('rerun_reason', '')) if fm.get('rerun') else ''}*")
    table = "### Current values\n\n" + values_table(fm, body, only)
    if short:
        parts = [head, "### Summary\n" + (section(body, 2, "Summary") or "").strip(), table,
                 "### Questions for the record\n" + (section(body, 2, "Questions for the record") or "").strip(),
                 "### Since this study\n" + (section(body, 2, "Since this study") or "").strip()]
        return "\n\n".join(parts)
    b = demote(body[title.end():] if title else body, 1)
    b = re.sub(r"(^### Summary[^\n]*\n.*?)(?=^### )", lambda m: m.group(1).rstrip() + "\n\n" + table + "\n\n", b, count=1, flags=re.S | re.M)
    return head + "\n\n" + b.strip()


def study_index_lines() -> list[str]:
    out = []
    for slug in study_slugs():
        fm, _, body = parse_chapter(study_text(slug))
        n = len(since_entries(body))
        out.append(f"- **{slug}** · {fm.get('area', '')} · tags: {', '.join(fm.get('tags', []))} · written {fm.get('written', '?')} "
                   f"as of memo {fm.get('as_of', '?')} · since-entries waiting to fold: {n}"
                   + (f" · RE-RUN ADVISED ({fm.get('rerun_reason', '')})" if fm.get("rerun") else ""))
    return out


def study_drift(slug: str) -> dict:
    """What has accumulated against a study since it was written or last folded."""
    fm, _, body = parse_chapter(study_text(slug))
    entries = since_entries(body)
    base = {(k, p): v for p, tbl in (fm.get("values") or {}).items() if isinstance(tbl, dict) for k, v in tbl.items()}
    drift = 0.0
    for _, txt in entries:
        for k, p, v in value_lines(txt):
            if (k, p) in base:
                drift = max(drift, abs(mid(rng(v)) - mid(rng(base[(k, p)]))))
    moved = sum(len(re.findall(r"→", txt)) for _, txt in entries)
    since = str(fm.get("as_of", "000"))
    contra = []
    for t, _ in manifests(("part2", "complete")):
        if t > since:
            for s_, verdict in AGAINST_RE.findall(read(work_dir(t) / "part2.md")):
                if s_ == slug and verdict == "contradicts":
                    contra.append(t)
    sc = config().get("studies", {})
    advise = (len(entries) >= sc.get("rerun_after_entries", 6) or drift >= sc.get("rerun_drift", 4)
              or len(contra) >= sc.get("rerun_contradictions", 2))
    return {"entries": len(entries), "drift": drift, "chapter_moves": moved, "contradicted_by": contra, "advise": advise}


def check_study(text: str, slug: str, label: str, errors: list, warnings: list, tok: str | None = None, folding: bool = False, teaching: bool = False):
    sc = config().get("studies", {})
    fm, _, body = parse_chapter(text)
    if not fm:
        errors.append(f"{label}: no +++ front matter")
        return
    if "_error" in fm:
        errors.append(f"{label}: front matter is not valid TOML: {fm['_error']}")
        return
    for k in ["area", "slug", "written", "as_of"]:
        if not str(fm.get(k, "")).strip():
            errors.append(f"{label}: front matter '{k}' is blank")
    if fm.get("slug") and fm["slug"] != slug:
        errors.append(f"{label}: slug '{fm['slug']}' should be '{slug}' (the file name)")
    tags = fm.get("tags", [])
    vids = var_ids()
    if not tags:
        errors.append(f"{label}: tags is empty — name the variables and facets this area covers (schema/VARIABLES.toml)")
    for t in tags:
        if t not in vids:
            errors.append(f"{label}: tag '{t}' is not a variable or facet in schema/VARIABLES.toml")
    keys, vk = set(tag_keys(tags)), set(vector_keys())
    ph = phase_ids()
    for pid, tbl in (fm.get("values") or {}).items():
        if pid not in ph:
            errors.append(f"{label}: [values.{pid}] is not a current phase ({', '.join(ph)})")
            continue
        if not isinstance(tbl, dict):
            errors.append(f"{label}: [values.{pid}] must be a table of keys")
            continue
        for k, v in tbl.items():
            if k in vk:
                errors.append(f"{label}: [values.{pid}] {k} is a headline variable or facet — its one copy is the chapter's end vector; judge it there with an amend file")
                continue
            if k not in keys:
                errors.append(f"{label}: [values.{pid}] {k} is not covered by the study's tags")
            if isinstance(v, dict):
                ind = v.get("ind")
                vv = {x: y for x, y in v.items() if x != "ind"}
                if vv.get("conf") not in ("low", "medium", "high"):
                    errors.append(f"{label}: [values.{pid}] {k} conf must be low, medium or high (leave an unjudged key out)")
                check_value(f"{label} [values.{pid}]", k, vv, errors, warnings)
                if ind is not None and not TAG_RE.search(str(ind)):
                    errors.append(f"{label}: [values.{pid}] {k} ind (indicator) needs a provenance tag")
            else:
                check_value(f"{label} [values.{pid}]", k, v, errors, warnings)
    title = re.search(r"^# .+$", body, re.M)
    if not title:
        errors.append(f"{label}: no '# <area>' title line")
    heads = [h for h, _ in sections(body, 2)]
    for h in STUDY_REQUIRED:
        if not any(x.startswith(h) for x in heads):
            errors.append(f"{label}: '## {h}' is missing")
    for h in STUDY_TEACHING:
        if not any(x.startswith(h) for x in heads):
            (errors if teaching else warnings).append(f"{label}: '## {h}' is missing — from v1.0.9 (R06) a study teaches its subject and gives a complete inventory (procedures/STUDY.md, step 5)")
    inv = section(body, 2, "Inventory") or ""
    if any(x.startswith("Inventory") for x in heads) and not re.search(r"^\|.*\|\s*$", inv, re.M):
        errors.append(f"{label}: '## Inventory' has no table — the inventory is counted in tables, by branch and force")
    if heads and not heads[-1].startswith("Since this study"):
        errors.append(f"{label}: '## Since this study' must be the last section (entries are appended there)")
    lo_p = sc.get("phase_words_min", 400)
    for p in phases():
        sec = section(body, 2, f"{p['id']} ")
        if sec is None:
            errors.append(f"{label}: '## {p['id']} · {p['title']}' is missing — a study runs across every phase")
        elif words(sec) < lo_p:
            warnings.append(f"{label}: {p['id']} is {words(sec)} words (guide at least {lo_p}); say why if the area is quiet in that phase")
    main = body.split("## Since this study")[0]
    w = words(main)
    lo, hi = sc.get("study_words", [5000, 14000])
    if not lo <= w <= hi:
        warnings.append(f"{label}: {w:,} words (guide {lo:,}–{hi:,})")
    q = section(body, 2, "Questions for the record") or ""
    for l in [x for x in q.splitlines() if x.strip().startswith("- ")]:
        if not QUESTION_LINE.match(l.strip()):
            errors.append(f"{label}: question line does not match '- **Q-n** · ERRATUM | CHECKPOINT | RESOLVED | STANDS · <text>': “{l.strip()[:80]}”")
    if words(q) < 8:
        warnings.append(f"{label}: 'Questions for the record' is empty — list each inconsistency found, or say plainly that none was found and what was checked")
    srcs = set(study_sources(body))
    check_tags(main, errors, label, sources=srcs, x_required=True)
    if re.search(r"<!--\s*(?:event|EV)", body) or EVENT_HDR.search(body):
        errors.append(f"{label}: a study holds no event headers — events live only in the chapters")
    entries = since_entries(body)
    if folding and entries:
        errors.append(f"{label}: {len(entries)} since-entr{'y' if len(entries) == 1 else 'ies'} still under '## Since this study' — fold them into the text and values, then remove them")
    j = section(body, 2, "Judgments") or ""
    chap = {p: parse_chapter(read(CHAP / f"{p}.md"))[0] for p in ph}
    if tok:
        staged = staged_chapters(tok)
        chap.update({p: parse_chapter(t)[0] for p, t in staged.items()})
    unj = [k for k in keys & vk if all(((chap[p].get("end_vector") or {}).get(k) or {}).get("conf") == "unjudged" for p in ph)]
    unj_named = [k for k in unj if k not in j]
    if unj_named:
        warnings.append(f"{label}: {len(unj_named)} tagged facet(s) unjudged in every phase and not named in '## Judgments' "
                        f"({', '.join(unj_named[:5])}{'…' if len(unj_named) > 5 else ''}) — judge them where the record holds evidence, or say why not")
    conv = [k for k in keys & vk if any("was" in (((chap[p].get("end_vector") or {}).get(k) or {})) and
                                        ((chap[p].get("end_vector") or {}).get(k) or {}).get("conf") == "unjudged" for p in ph)]
    if conv:
        warnings.append(f"{label}: {len(conv)} tagged headline value(s) not yet judged in units in some phase ({', '.join(conv[:5])}) — judge them if the study's evidence bears on them (R03)")


def check_study_chapters(tok: str, errors: list, warnings: list, keys: set[str] | None = None):
    """A study run changes end-vector judgments only: no event, no prose, no entry a memorandum already judged."""
    for pid, txt in staged_chapters(tok).items():
        nfm, _, nbody = parse_chapter(txt)
        ofm, _, obody = parse_chapter(read(CHAP / f"{pid}.md"))
        if re.sub(r"\s+", " ", nbody).strip() != re.sub(r"\s+", " ", obody).strip():
            errors.append(f"chapter {pid} (staged): a study changes no event and no prose — only end-vector entries that are unjudged or converted")
        for k in set(nfm) | set(ofm):
            if k not in ("end_vector", "snapshot") and nfm.get(k) != ofm.get(k):
                errors.append(f"chapter {pid} (staged): front matter '{k}' changed — a study changes only end-vector entries")
        for sec in ("end_vector", "snapshot"):
            nv, ov = nfm.get(sec) or {}, ofm.get(sec) or {}
            for k, v in nv.items():
                o = ov.get(k)
                if v == o:
                    continue
                oc = o.get("conf") if isinstance(o, dict) else None
                if oc in ("unjudged",):
                    pass
                elif isinstance(o, dict) and isinstance(v, dict) and {x: y for x, y in v.items() if x != "binding"} == {x: y for x, y in o.items() if x != "binding"}:
                    pass
                else:
                    errors.append(f"chapter {pid} {sec}: {k} was already judged ({fmt_val(o)}) — a study does not re-judge it; "
                                  f"put the disagreement in 'Questions for the record' for a checkpoint or an erratum")
                if keys is not None and k not in keys and parent(k) not in {parent(x) for x in keys}:
                    warnings.append(f"chapter {pid} {sec}: {k} is outside this study's tags")
    es = load_toml(HIST / "endstate.toml")
    if es.get("last_changed") == tok:
        errors.append(f"endstate.toml: last_changed is {tok} — a study never moves the end state")


def check_study_blocks(text: str, tok: str, label: str, errors: list, required: list[str]):
    """Part 3 (or a review): one '<!-- study slug -->' block per affected study, value lines well formed."""
    blocks = STUDY_BLOCK.findall(text)
    have = [s_ for s_, _ in blocks]
    for slug in required:
        if slug not in have:
            errors.append(f"{label}: no '<!-- study {slug} -->' … '<!-- /study -->' block — this work touches the study's variables; "
                          f"say what changed in the area (or why nothing did) and give any new values")
    vk = set(vector_keys())
    ph = phase_ids()
    for slug, body in blocks:
        if slug not in study_slugs():
            errors.append(f"{label}: '<!-- study {slug} -->' names no study in studies/")
            continue
        if words(body) < 15:
            errors.append(f"{label}: the study {slug} block is under 15 words")
        if re.search(r"\[S\d+\]", body):
            errors.append(f"{label}: the study {slug} block cites [S#] — in a study entry write [M{tok}·S#], since the study has its own sources")
        keys = set(tag_keys(parse_chapter(study_text(slug))[0].get("tags", [])))
        for l in [x for x in body.splitlines() if re.match(r"\s*-\s*value\b", x)]:
            m = VALUE_LINE.match(l.strip())
            if not m:
                errors.append(f"{label}: study {slug} value line should read '- value · <key> · <Pk> · <low>..<high> (in the unit; Δ<low>..<high> for a difference from history) · <low|medium|high> · <note>': “{l.strip()[:80]}”")
                continue
            k, pid, lo, hi = m.group(1), m.group(2), float(m.group(4).replace(",", "")), float(m.group(5).replace(",", ""))
            if k in vk:
                errors.append(f"{label}: study {slug} value line for {k}: a headline variable or facet is judged in the chapter's end vector, not in a study entry (the script records the chapter's move in the entry itself)")
            elif k not in keys:
                errors.append(f"{label}: study {slug} value line for {k}: not covered by the study's tags")
            if pid not in ph:
                errors.append(f"{label}: study {slug} value line for {k}: {pid} is not a current phase")
            if lo > hi:
                errors.append(f"{label}: study {slug} value line for {k}: {lo}..{hi} — low is above high")


def append_study_entries(text: str, tok: str, title: str):
    """Append each study block as a dated since-entry at the end of its study, with the chapter moves on its variables."""
    import datetime
    for slug, body in STUDY_BLOCK.findall(text):
        p = STUDIES / f"{slug}.md"
        cur = read(p)
        if not cur:
            continue
        fm = parse_chapter(cur)[0]
        keys = set(tag_keys(fm.get("tags", [])))
        moves = []
        d = work_dir(tok)
        for bp in sorted((d / "before").glob("P*.md")) if (d / "before").exists() else []:
            bfm = parse_chapter(read(bp))[0]
            afm = parse_chapter(read(CHAP / bp.name))[0]
            for sec in ("end_vector", "snapshot"):
                for k in sorted(keys & set((afm.get(sec) or {}))):
                    o, n = (bfm.get(sec) or {}).get(k), (afm.get(sec) or {}).get(k)
                    if o != n:
                        moves.append(f"{bp.stem}{' snapshot' if sec == 'snapshot' else ''} {k} {fmt_val(o)} → {fmt_val(n)}")
        label = f"Memo {tok}" if re.fullmatch(r"\d{3}", tok) else tok
        entry = (f"### {label} — {title} · {datetime.date.today().isoformat()}\n<!-- since {tok} -->\n{body.strip()}\n"
                 + (f"\n*Chapter values {label} moved on this study's variables: {'; '.join(moves)}.*\n" if moves else "")
                 + "<!-- /since -->\n")
        pat = re.compile(r"### [^\n]*\n<!--\s*since " + re.escape(tok) + r"\s*-->.*?<!--\s*/since\s*-->\n?", re.S)
        cur = pat.sub(lambda _: entry, cur) if pat.search(cur) else cur.rstrip("\n") + "\n\n" + entry
        write(p, cur)
        print(f"Appended a since-entry to studies/{slug}.md")


def promote_studies(tok: str):
    d = work_dir(tok) / "studies"
    for sp_ in sorted(d.glob("*.md")) if d.exists() else []:
        dst = STUDIES / sp_.name
        before = work_dir(tok) / "before-studies" / sp_.name
        if dst.exists() and not before.exists() and read(dst) != read(sp_):
            write(before, read(dst))
        write(dst, read(sp_))
        print(f"Promoted studies/{sp_.name}")


def review_meta(tok: str) -> dict:
    p = work_dir(tok) / "review.toml"
    return load_toml(p) if p.exists() else {}


def study_next_part(tok: str) -> tuple[int, dict] | None:
    rv = review_meta(tok)
    done = rv.get("done", [])
    for i, ar in enumerate(rv.get("area", []), 1):
        if i not in done:
            return i, ar
    return None


def cmd_study(a):
    sc = config().get("studies", {})
    if a.init:
        if a.target:
            a.args = [a.target] + list(a.args)
        areas = [x.strip() for x in a.args if x.strip()]
        lo, hi = sc.get("areas_per_run", [2, 3])
        if not areas:
            die("name the areas: fie.py study --init \"The air war\" \"CIDG\" …")
        if len(areas) > hi:
            die(f"{len(areas)} areas: a study run takes at most {hi} (rules/CONFIG.toml [studies]); run the rest as a second STUDY")
        ow = open_work()
        if ow:
            die(f"{ow[1]} is open ({ow[0]}): one piece of work at a time — finish it first")
        n = len(review_tokens("ST")) + 1
        tok = f"ST{n:02d}"
        d = work_dir(tok)
        done = [t for t, _ in manifests(("complete",))]
        as_of = done[-1] if done else "000"
        rows = []
        slugs = []
        for ar in areas:
            slug = slugify(ar)
            if slug in slugs:
                die(f"two areas share the slug '{slug}'")
            slugs.append(slug)
            rows.append(f'\n[[area]]\nslug = "{slug}"\nname = {json.dumps(ar, ensure_ascii=False)}\nrerun = {"true" if (STUDIES / f"{slug}.md").exists() else "false"}\n')
        write(d / "review.toml", f'work = "{tok}"\nkind = "ST"\nstatus = "open"\nafter_memo = "{as_of}"\ndone = []\n' + "".join(rows))
        for ar, slug in zip(areas, slugs):
            dst = d / "studies" / f"{slug}.md"
            if (STUDIES / f"{slug}.md").exists():
                write(dst, read(STUDIES / f"{slug}.md"))
                print(f"Staged {rel(dst)} — a re-run: the existing study, to be rewritten from the record as it now stands")
            else:
                secs = "\n\n".join(f"## {p['id']} · {phase_heading(p)}" for p in phases())
                t = (read(ROOT / "templates" / "study.md").replace("AREA", ar).replace("SLUG", slug).replace("STNN", tok)
                     .replace("ASOF", as_of).replace("PHASE_SECTIONS", secs))
                write(dst, t)
                print(f"Created {rel(dst)} from the template")
        if len(areas) < lo:
            print(f"NOTE: {len(areas)} area(s); a run is meant to take {lo}–{hi}.")
        print(f"Opened study run {tok} after memo {as_of}: " + "; ".join(f"Part {i} = {ar} ({s})" for i, (ar, s) in enumerate(zip(areas, slugs), 1)))
        print(f"Next: set the tags in {rel(d)}/studies/{slugs[0]}.md, then `python3 scripts/fie.py pack {tok}` and read it.")
        return
    if a.target == "fold":
        if len(a.args) < 2:
            die("fie.py study fold CPnn|Rnn SLUG [SLUG …]")
        tok, slugs = a.args[0], a.args[1:]
        if not re.fullmatch(r"CP\d{2}|R\d{2}", tok):
            die("only a checkpoint (CPnn) or a revision (Rnn) folds studies")
        for slug in slugs:
            src = STUDIES / f"{slug}.md"
            if not src.exists():
                die(f"studies/{slug}.md does not exist")
            dst = work_dir(tok) / "studies" / f"{slug}.md"
            if dst.exists():
                print(f"{rel(dst)} already staged (kept)")
            else:
                write(dst, read(src))
                print(f"Staged {rel(dst)} — fold its since-entries into the text and [values], re-judge, set as_of and folded = \"{tok}\"")
        return
    tok = a.target
    if not tok or not re.fullmatch(r"ST\d{2}", tok):
        die("fie.py study --init AREA … | study STnn --finish --part k | study fold CPnn SLUG …")
    if not a.finish:
        die("say --finish --part k")
    rv = review_meta(tok)
    areas = rv.get("area", [])
    k = a.part or (study_next_part(tok) or (0, {}))[0]
    if not 1 <= k <= len(areas):
        die(f"{tok} has parts 1–{len(areas)}")
    done = rv.get("done", [])
    if k in done:
        die(f"{tok} part {k} is already finished")
    if any(i not in done for i in range(1, k)):
        die(f"{tok}: finish part {min(i for i in range(1, k) if i not in done)} first — the parts run in order")
    slug = areas[k - 1]["slug"]
    sp_ = work_dir(tok) / "studies" / f"{slug}.md"
    errors, warnings = [], []
    txt = read(sp_)
    check_study(txt, slug, f"study {slug}", errors, warnings, tok=tok, folding=True, teaching=True)
    fm = parse_chapter(txt)[0]
    if fm.get("written") != tok:
        errors.append(f"study {slug}: written = '{fm.get('written')}', expected '{tok}'")
    if fm.get("as_of") != rv.get("after_memo"):
        errors.append(f"study {slug}: as_of = '{fm.get('as_of')}', expected '{rv.get('after_memo')}' (the last complete memorandum)")
    if fm.get("rerun"):
        errors.append(f"study {slug}: rerun is still true — a fresh study answers the re-run; set rerun = false")
    keys = set(tag_keys(fm.get("tags", [])))
    staged = staged_chapters(tok)
    ids = all_events(staged)
    for pid, t in staged.items():
        check_chapter(t, pid, errors, warnings, f"chapter {pid} (staged)", ids)
    check_study_chapters(tok, errors, warnings, keys)
    nchanged = 0
    for pid, t in staged.items():
        nv, ov = parse_chapter(t)[0], parse_chapter(read(CHAP / f"{pid}.md"))[0]
        nchanged += sum(1 for sec in ("end_vector", "snapshot") for kk, v in (nv.get(sec) or {}).items() if v != (ov.get(sec) or {}).get(kk))
    nvals = sum(len(t_) for t_ in (fm.get("values") or {}).values() if isinstance(t_, dict))
    _, _, body = parse_chapter(txt)
    nq = len(re.findall(r"^- \*\*Q-\d+\*\*", section(body, 2, "Questions for the record") or "", re.M))
    audit = (f"Audit — Study {tok}, Part {k}/{len(areas)} ({slug}) · v{read(ROOT / 'VERSION').strip()} · words: {words(body.split('## Since this study')[0]):,} · "
             f"tags: {len(fm.get('tags', []))} · chapter entries judged: {nchanged} · study values: {nvals} · questions for the record: {nq}")
    report(errors, warnings, audit)
    if errors:
        print("\nNot finished: fix the errors and run finish again.")
        sys.exit(1)
    write(sp_, re.sub(r'^audit\s*=.*\n?', "", txt, flags=re.M).replace("+++\n", f'+++\naudit = {json.dumps(audit, ensure_ascii=False)}\n', 1))
    promote(tok)
    dst = STUDIES / f"{slug}.md"
    before = work_dir(tok) / "before-studies" / f"{slug}.md"
    if dst.exists() and not before.exists():
        write(before, read(dst))
    write(dst, read(sp_))
    done.append(k)
    rt = read(work_dir(tok) / "review.toml")
    rt = re.sub(r"^done\s*=.*$", "done = [" + ", ".join(map(str, sorted(done))) + "]", rt, flags=re.M)
    if len(done) == len(areas):
        rt = re.sub(r'^status\s*=.*$', 'status = "complete"', rt, flags=re.M)
    write(work_dir(tok) / "review.toml", rt)
    build_all(quiet=True)
    print(f"\nFinished {tok} part {k}: studies/{slug}.md")
    if a.push:
        git_commit_push(f"Study {tok} Part {k}: {areas[k - 1].get('name', slug)}")
    print(f"Send the user: build/studies/{slug}.md" + (" · build/reviews/" + tok + "/CHANGES.md" if staged else ""))
    nxt = study_next_part(tok)
    print(f"Next: CONTINUE in a new thread for Part {nxt[0]} ({nxt[1].get('name')})." if nxt else f"{tok} is complete.")


def pack_study(tok: str):
    lim = config()["limits"]
    nxt = study_next_part(tok)
    if not nxt:
        die(f"{tok} has no part left")
    k, ar = nxt
    slug = ar["slug"]
    staged = read(work_dir(tok) / "studies" / f"{slug}.md")
    fm, _, body = parse_chapter(staged)
    tags = fm.get("tags", []) or []
    pars = {parent(t) for t in tags}
    rv = review_meta(tok)
    parts = [f"<!-- study pack {tok} part {k} -->\n# Context pack — study run {tok}, Part {k} of {len(rv.get('area', []))}: {ar.get('name')} (`{slug}`)\n\n"
             f"*Generated by fie.py. Do not edit. The record as it stands after memo {rv.get('after_memo')}.*"]
    if not tags:
        parts.append(f"## Tags not set yet\n\nSet `tags` in `reviews/{tok}/studies/{slug}.md` (variables and facets from schema/VARIABLES.toml, "
                     f"below), then run `python3 scripts/fie.py pack {tok}` again: the ledgers, positions and values for those variables load then.\n\n"
                     + "\n".join(f"- `{v['id']}` — {v['name']}; higher means {v['higher']}"
                                 + (f"; facets: {', '.join(f['id'] for f in v.get('facets', []))}" if v.get("facets") else "")
                                 + (" · headline" if v.get("vector") else "") for v in variables()))
    if ar.get("rerun") or fm.get("written", tok) != tok:
        parts.append("## The study as it stands (a re-run: rewrite it from the record, folding its since-entries)\n\n" + study_render(slug, read(STUDIES / f"{slug}.md")))
    parts.append("## Other studies\n\n" + ("\n".join(l for l in study_index_lines() if not l.startswith(f"- **{slug}**")) or "None."))
    if tags:
        parts.append("## Current values on this study's variables\n\n" + values_table(fm, body))
        parts.append("## Variable ledgers\n\n" + "\n\n".join(f"### {v}\n" + ("\n".join(ledger_lines(v)) or "No provision pushes or depends on it.") for v in sorted(pars)))
        parts.append("## Settled positions on these variables\n\n" + ("\n".join(positions_for(pars)) or "None."))
        hits = []
        for t, m in manifests(("complete",)):
            pv, dv = memo_vars(m)
            if (set(pv) | dv) & pars:
                hits.append(t)
        parts.append("## Memoranda that touch these variables\n\n" + (", ".join(hits) or "None.") +
                     "\n\nTheir cards are in `build/cards/`; read only the ones the area turns on, and grep for the rest.")
        parts.append("## Provisions in those memoranda\n\n" + ("\n".join(l for l in provision_index_lines() if any(l.endswith(f"memo {t}") for t in hits)) or "None.")
                     + "\n\nEvery provision in theater: `build/INDEX.md`.")
        er = errata_for(set(hits))
        if er:
            parts.append("## Errata affecting those memoranda\n\n" + "\n\n".join(er))
    parts.append("## Standing directives\n\n" + ("\n".join(register_lines("directives.md")) or "None."))
    parts.append("## Gap register (latest status)\n\n" + ("\n".join(latest_by_key(register_lines("gaps.md"))) or "None."))
    parts.append("## Chapter digests (exact extracts; read in full the events the area turns on, found with `fie.py grep`)\n\n"
                 + "\n\n".join(chapter_digest(p["id"]) for p in phases()))
    text = "\n\n".join(parts) + "\n"
    cap = config().get("studies", {}).get("pack_chars", lim["pack_chars"])
    if len(text) > cap:
        print(f"WARNING: pack is {len(text):,} characters, over the {cap:,} limit — read it in two passes")
    out = BUILD / "packs" / f"PACK-{tok}.md"
    write(out, text)
    print(f"Wrote {rel(out)} ({len(text):,} characters, ~{len(text)//4:,} tokens) for part {k}: {ar.get('name')}")


def studies_pack_section(vars_: set[str], part: int) -> tuple[list[str], str]:
    """(slugs, text) of the studies section a memorandum's pack carries."""
    slugs = matching_studies(vars_)
    if not slugs:
        return [], ""
    pars = {parent(v) for v in vars_}
    if part == 2:
        intro = ("## Studies on these variables\n\nJudge this provision's pushes against each study's values in `### Against the studies` "
                 "(§2 Part A), and mark each study `<!-- against <slug>: consistent -->` or `<!-- against <slug>: contradicts -->`. "
                 "Where the provision's effect contradicts a study, say so in plain words and say which should give way.")
        body = "\n\n---\n\n".join(study_render(s_, short=True, only=pars) for s_ in slugs)
    else:
        intro = ("## Studies to update\n\nPart 3 closes with a `<!-- study <slug> -->` … `<!-- /study -->` block for each study below: "
                 "what changed in the area and which events show it, and a value line for any value the study holds that moves "
                 "(`- value · <key> · <Pk> · <low>..<high> · <conf> · <note>`, in the variable's unit; `Δ<low>..<high>` for a difference from history). The script adds the chapter moves itself.")
        body = "\n\n".join(f"### {s_}\n\n" + values_table(*(lambda t: (t[0], t[2]))(parse_chapter(study_text(s_))), only=pars) for s_ in slugs)
    return slugs, f"<!-- studies: {','.join(slugs)} -->\n" + intro + "\n\n" + body


# ----------------------------------------------------------------------------- status

def version_report() -> tuple[str, list[str]]:
    v = read(ROOT / "VERSION").strip()
    bad = []
    for p in ["rules/CONFIG.toml", "schema/VARIABLES.toml"]:
        try:
            if str(load_toml(ROOT / p).get("version")) != v:
                bad.append(f"{p} says {load_toml(ROOT / p).get('version')}")
        except Exception as e:
            bad.append(f"{p} unreadable: {e}")
    files = [ROOT / "CLAUDE.md", ROOT / "README.md", ROOT / "DESIGN.md"]
    for d in ["rules", "procedures", "schema", "instructions"]:
        files += sorted((ROOT / d).glob("*.md"))
    for f in files:
        if not f.exists():
            bad.append(f"{rel(f)} missing")
            continue
        first = read(f).splitlines()[0] if read(f) else ""
        m = re.match(r"<!-- fie v([\d.]+) -->", first)
        if not m or m.group(1) != v:
            bad.append(f"{rel(f)} header says '{first[:40]}'")
    return v, bad


def config_problems() -> list[str]:
    c = config()
    out = []
    for k, val in c.get("constraints", {}).items():
        if k == "troop_ceiling":
            if not (val in ("HISTORICAL", "NONE") or isinstance(val, int)):
                out.append(f"constraints.troop_ceiling = {val!r} (HISTORICAL, NONE or a number)")
        elif val not in CONSTRAINT_VALUES:
            out.append(f"constraints.{k} = {val!r} (MODELLED or SUSPENDED)")
    return out


def review_tokens(prefix: str) -> list[str]:
    d = ROOT / "reviews"
    return sorted(p.name for p in d.iterdir() if p.is_dir() and p.name.startswith(prefix)) if d.exists() else []


def review_done(token: str) -> bool:
    p = work_dir(token) / "review.toml"
    return p.exists() and load_toml(p).get("status") == "complete"


def git_commit_push(msg: str) -> bool:
    """Commit everything and push straight to main. Returns True on success."""
    git("add", "-A")
    if git("status", "--porcelain"):
        r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            subprocess.run(["git", "config", "user.name", "COMUSMACV (Claude)"], cwd=ROOT)
            subprocess.run(["git", "config", "user.email", "noreply@anthropic.com"], cwd=ROOT)
            r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT, capture_output=True, text=True)
            if r.returncode:
                print(f"COMMIT FAILED: {r.stderr.strip()}")
                return False
    for attempt in (1, 2):
        r = subprocess.run(["git", "-c", "push.negotiate=true", "push", "origin", "HEAD:main"], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            print(f"Committed and pushed to main: {msg}")
            return True
        if "rejected" in r.stderr or "non-fast-forward" in r.stderr or "fetch first" in r.stderr:
            print("PUSH REJECTED: main has moved — two pieces of work ran at once. Stop and tell the user; do not merge.")
            return False
    print(f"PUSH FAILED twice: {r.stderr.strip()[-300:]} — tell the user; the work is committed locally only.")
    return False


def open_work() -> tuple[str, str] | None:
    """(kind, token) of unfinished work, if any."""
    for t in memo_tokens():
        st = load_toml(work_dir(t) / "manifest.toml").get("status", "open")
        if st != "complete":
            return ({"open": "part1", "part1": "part2", "part2": "part3"}[st], t)
    for base in [ROOT / "reviews", ROOT / "revisions"]:
        for d in sorted(base.glob("*")) if base.exists() else []:
            rt = d / "review.toml"
            if rt.exists() and load_toml(rt).get("status") != "complete":
                return ("review", d.name)
    have = [p for p in phase_ids() if parse_events(parse_chapter(read(CHAP / f"{p}.md"))[2])]
    if 0 < len(have) < len(phase_ids()):
        return ("baseline", "000")
    return None


def cmd_boot(a):
    """Everything a thread's first turn needs, in one call: sync main, status, rules, the procedure, the pack."""
    out = []
    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        r = subprocess.run(["git", "checkout", "main"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            subprocess.run(["git", "checkout", "-b", "main", "origin/main"], cwd=ROOT, capture_output=True, text=True)
    r = subprocess.run(["git", "pull", "--ff-only", "origin", "main"], cwd=ROOT, capture_output=True, text=True, timeout=300)
    if r.returncode:
        print("STOP: `git pull --ff-only origin main` failed — the record has diverged or is unreachable. Tell the user.\n" + r.stderr[-400:])
        sys.exit(1)
    print("=" * 30 + " STATUS")
    cmd_status(None)
    cmd = a.command.lower()
    ow = open_work()
    proc, pack = None, None
    if cmd in ("provision", "new"):
        proc = ["PART1.md"]
        if ow:
            print(f"\nNOTE: {ow[1]} is open ({ow[0]}). Ask the user whether to finish it first.")
    elif cmd in ("continue", "c"):
        if not ow:
            print("\nNothing is open. Ask the user what to do.")
        elif ow[0] in ("part2", "part3"):
            proc = [f"PART{ow[0][-1]}.md"]
            pack = (ow[1], int(ow[0][-1]))
        elif ow[0] == "part1":
            proc = ["PART1.md"]
        elif ow[0] == "baseline":
            proc = ["BASELINE.md"]
        else:
            tok = ow[1]
            proc = [{"CP": "CHECKPOINT.md", "MT": "META.md", "TN": "TNA.md", "ST": "STUDY.md"}.get(tok[:2], "REVISIONS.md")]
            if tok[:2] in ("CP", "MT", "ST"):
                pack = (tok, 0)
        if ow:
            print(f"\nCONTINUE resumes {ow[1]} at {ow[0]}.")
    else:
        proc = [{"baseline": "BASELINE.md", "tna": "TNA.md", "checkpoint": "CHECKPOINT.md", "meta": "META.md",
                 "veto": "REVISIONS.md", "erratum": "REVISIONS.md", "study": "STUDY.md"}.get(cmd, "")]
        if not proc[0]:
            die(f"unknown command '{a.command}' (provision, continue, baseline, tna, checkpoint, meta, veto, erratum, study)")
        if cmd == "study" and ow:
            print(f"\nNOTE: {ow[1]} is open ({ow[0]}). One piece of work at a time: ask the user whether to finish it first.")
    files = ["procedures/BOOTSTRAP.md", "rules/RULES.md", "rules/VOICE.md", "rules/CONFIG.toml", "schema/FORMATS.md"]
    if proc and proc[0] == "PART1.md":
        files.append("schema/VARIABLES.toml")
    files += [f"procedures/{p}" for p in proc or []]
    for f in files:
        print("\n" + "=" * 30 + f" {f}\n" + read(ROOT / f))
    if proc and proc[0] in ("PART1.md", "STUDY.md"):
        print("\n" + "=" * 30 + " Studies on file (studies/)\n" + ("\n".join(study_index_lines()) or "None yet."))
    if pack:
        tok, part = pack
        pth = None
        if part:
            if (work_dir(tok) / "manifest.toml").exists():
                build_all(quiet=True)
                cmd_pack(argparse.Namespace(work=tok, part=part))
                pth = BUILD / "packs" / f"PACK-{tok}-part{part}.md"
        else:
            if tok.startswith("ST") and (work_dir(tok) / "review.toml").exists():
                build_all(quiet=True)
            cmd_pack(argparse.Namespace(work=tok, part=0))
            pth = BUILD / "packs" / f"PACK-{tok}.md"
        if pth:
            print("\n" + "=" * 30 + f" {rel(pth)}\n" + read(pth))
    print("\n" + "=" * 30 + " END OF BOOT. Everything above is loaded: do not read these files again in this thread.")


def cmd_status(_):
    v, bad = version_report()
    print(f"Repository version: {v}")
    print("Version check: " + ("all files agree" if not bad else "MISMATCH\n  - " + "\n  - ".join(bad)))
    cp = config_problems()
    print("Config: " + ("complete" if not cp else "INCOMPLETE — new memoranda are blocked until these are set in rules/CONFIG.toml:\n  - " + "\n  - ".join(cp)))
    have = [p["id"] for p in phases() if (CHAP / f"{p['id']}.md").exists()]
    baseline = len(have) == len(phases()) and all(parse_events(parse_chapter(read(CHAP / f"{p}.md"))[2]) for p in have)
    print(f"Baseline history: {'present' if baseline else 'MISSING — run BASELINE before the first memorandum'} ({len(have)}/{len(phases())} chapters)")
    print(f"Theater Needs Assessment: {'done' if review_done('TNA') else 'not yet run'}")
    toks = memo_tokens()
    done = [t for t in toks if load_toml(work_dir(t) / "manifest.toml").get("status") == "complete"]
    open_ = [t for t in toks if t not in done]
    print(f"Memoranda complete: {len(done)}" + (f" (latest {done[-1]})" if done else ""))
    for t in open_:
        st = load_toml(work_dir(t) / "manifest.toml").get("status", "open")
        nxt = {"open": "Part 1", "part1": "Part 2", "part2": "Part 3"}.get(st, "?")
        print(f"IN PROGRESS: memo {t}, status '{st}' — next is {nxt}")
    nxt_no = int(toks[-1]) + 1 if toks else 1
    print(f"Next memorandum number: {nxt_no:03d}")
    cps = [t for t in review_tokens("CP") if review_done(t)]
    mts = [t for t in review_tokens("MT") if review_done(t)]
    since = len([t for t in done if not cps or int(t) > int(load_toml(work_dir(cps[-1]) / "review.toml").get("after_memo", "0"))])
    every = config()["checkpoint_every"]
    print(f"Checkpoints: {len(cps)} · meta-checkpoints: {len(mts)} · memoranda since last checkpoint: {since}/{every}"
          + (" — CHECKPOINT DUE" if since >= every else ""))
    me = config()["meta_every_checkpoints"]
    if len(cps) - me * len(mts) >= me:
        print("META-CHECKPOINT DUE")
    got = judged = total = facets_j = facets_all = 0
    for p_ in have:
        fm_ = parse_chapter(read(CHAP / f"{p_}.md"))[0]
        for sec in ("end_vector", "snapshot"):
            vec = fm_.get(sec) or {}
            if not vec:
                continue
            total += sum(1 for v in vector_ids() if v in vec)
            got += sum(1 for v in vector_ids() if isinstance(vec.get(v), dict) and "hist" in vec[v])
            judged += sum(1 for v in vector_ids() if isinstance(vec.get(v), dict) and vec[v].get("conf") in PUSH_CONFS)
            fks = [k for k in vec if k not in vector_ids()]
            facets_all += len(fks)
            facets_j += sum(1 for k in fks if isinstance(vec.get(k), dict) and vec[k].get("conf") in PUSH_CONFS)
    print(f"Units v1.0.8: headline values judged in units {judged}/{total} · history's figure entered {got}/{total} · facets judged {facets_j}/{facets_all}")
    sl = study_slugs()
    if sl:
        waiting = sum(len(since_entries(parse_chapter(study_text(x))[2])) for x in sl)
        rerun = [x for x in sl if parse_chapter(study_text(x))[0].get("rerun")]
        print(f"Studies: {len(sl)} ({', '.join(sl)}) · since-entries waiting for a checkpoint to fold: {waiting}"
              + (f" · RE-RUN ADVISED: {', '.join(rerun)}" if rerun else ""))
    else:
        print("Studies: none yet")
    for t in review_tokens("ST"):
        if not review_done(t):
            nx = study_next_part(t)
            if nx:
                print(f"IN PROGRESS: study run {t}, part {nx[0]} of {len(review_meta(t).get('area', []))} ({nx[1].get('name')}) — next is CONTINUE")
    es = load_toml(HIST / "endstate.toml")
    print(f"End state: rung ({es.get('rung')}) {es.get('rung_label')} — {es.get('summary')}")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch and branch != "main":
        print(f"Git: ON BRANCH '{branch}' — switch to main and pull before writing anything (procedures/BOOTSTRAP.md step 2)")
    dirty = git("status", "--porcelain")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if dirty:
        print(f"Git: UNCOMMITTED CHANGES ({len(dirty.splitlines())} files)")
    if ahead and ahead != "0":
        print(f"Git: {ahead} commit(s) NOT PUSHED")


# ----------------------------------------------------------------------------- new

def cmd_new(_):
    if config_problems():
        die("rules/CONFIG.toml is incomplete; run status")
    if not all((CHAP / f"{p}.md").exists() for p in phase_ids()):
        die("the baseline history is missing; run BASELINE first")
    toks = memo_tokens()
    for t in toks:
        if load_toml(work_dir(t) / "manifest.toml").get("status") != "complete":
            die(f"memo {t} is still in progress; finish it first")
    n = f"{(int(toks[-1]) + 1) if toks else 1:03d}"
    d = work_dir(n)
    d.mkdir(parents=True)
    for name in ["manifest.toml", "sources.md", "part1.md"]:
        write(d / name, read(ROOT / "templates" / name).replace("NNN", n))
    print(f"Opened memorandum {n}: {rel(d)}/")
    print(f"Fill {rel(d)}/manifest.toml (triage), {rel(d)}/sources.md and {rel(d)}/part1.md, then: fie.py finish {n} --part 1")


# ----------------------------------------------------------------------------- packs

def memo_vars(m: dict) -> tuple[dict, set]:
    push = {}
    for p in m.get("push", []):
        if p.get("var"):
            # routing weight: an old push by its midpoint on the band's footing; a push in units by its confidence
            w = abs(mid(push_range(p))) / 3 if ("band" in p or "low" in p) else {"high": 1.0, "medium": 0.8, "low": 0.6}.get(p.get("conf"), 0.6)
            push[parent(p["var"])] = max(push.get(parent(p["var"]), 0), w)
    dep = {parent(d["var"]) for d in m.get("depend", []) if d.get("var")}
    return push, dep


def route(token: str) -> list[tuple[float, str, list[str]]]:
    m = manifest(token)
    npush, ndep = memo_vars(m)
    links = {str(x) for x in m.get("links", [])}
    out = []
    for t, om in manifests():
        if t == token:
            continue
        opush, odep = memo_vars(om)
        score, why = 0.0, []
        for v in sorted(set(npush) & set(opush)):
            score += npush[v] + opush[v]
            why.append(f"{v} (both push)")
        for v in sorted(set(npush) & odep):
            score += 1.5 * npush[v]
            why.append(f"{v} (this pushes, {t} depends)")
        for v in sorted(ndep & set(opush)):
            score += 1.5 * opush[v]
            why.append(f"{v} ({t} pushes, this depends)")
        for v in sorted(ndep & odep):
            score += 0.5
            why.append(f"{v} (both depend)")
        if t in links:
            score += 100
            why.insert(0, "explicit link")
        if score > 0:
            out.append((score, t, why))
    return sorted(out, key=lambda x: (-x[0], x[1]))


def ledger_lines(var: str) -> list[str]:
    lines = []
    for t, m in manifests():
        for p in m.get("push", []):
            if p.get("var") == var or parent(p.get("var", "")) == var:
                facet = f" on {p['var']}" if p.get("var") != var else ""
                lines.append(f"- {p.get('provision')} (memo {t}) pushes {fmt_push(p)}{facet} — {p.get('note', '')}")
        for d in m.get("depend", []):
            if d.get("var") == var or parent(d.get("var", "")) == var:
                lines.append(f"- {d.get('provision')} (memo {t}) depends{' on ' + d['var'] if d.get('var') != var else ''} — {d.get('note', '')}")
    return lines


def register_lines(name: str) -> list[str]:
    return [l for l in read(HIST / name).splitlines() if l.startswith("- **")]


def positions_for(vars_: set[str]) -> list[str]:
    out = []
    for l in register_lines("positions.md"):
        m = re.search(r"vars:\s*([^·]+)", l)
        vs = {x.strip() for x in m.group(1).split(",")} if m else set()
        if vs & vars_ or not vs:
            out.append(l)
    return out


def latest_by_key(lines: list[str]) -> list[str]:
    seen = {}
    for l in lines:
        k = re.match(r"- \*\*([^*]+)\*\*", l)
        seen[k.group(1) if k else l] = l
    return list(seen.values())


def errata_for(tokens: set[str]) -> list[str]:
    out = []
    for p in sorted((ROOT / "errata").glob("E*.md")):
        s = read(p)
        m = re.search(r"^memos:\s*(.+)$", s, re.M)
        refs = {x.strip() for x in m.group(1).split(",")} if m else set()
        if refs & tokens or not refs:
            out.append(f"### {p.stem}\n{s.strip()}")
    return out


def provision_index_lines() -> list[str]:
    statuses = {}
    for t, m in manifests(("complete",)):
        for sc in m.get("status_change", []):
            statuses[sc.get("provision")] = f"{sc.get('status')} {sc.get('date', '')} (memo {t})".strip()
    lines = []
    for t, m in manifests(("part1", "part2", "complete")):
        for p in m.get("provision", []):
            st = statuses.get(p.get("id"), p.get("status", "active"))
            lines.append(f"- **{p.get('id')}** · {p.get('designation')} · {p.get('quantity')} · spaces {p.get('ceiling_spaces')} · "
                         f"{', '.join(p.get('systems', []))} · arrives {p.get('arrival')} · {st} · memo {t}")
    return lines


def chapter_digest(pid: str) -> str:
    """Exact extracts from a chapter: its overview, its event headers, and how the phase ends. No regeneration."""
    fm, _, body = parse_chapter(read(CHAP / f"{pid}.md"))
    title = re.search(r"^# (.+)$", body, re.M)
    first = re.search(r"^## ", body, re.M)
    overview = body[title.end():first.start()].strip() if title and first else ""
    ending = section(body, 2, "How the phase ends") or ""
    hdrs = [f"- {e['id']} · {e.get('title', '')} · {e.get('date', '')} · {e.get('place', '')} · {e.get('origin', '')}"
            for e in parse_events(body)]
    return (f"### {title.group(1) if title else pid}\n\n{vector_line(fm)}\n\n{overview}\n\n**Events:**\n" + "\n".join(hdrs)
            + f"\n\n**How the phase ends:** {ending.strip()}")


def cmd_pack(a):
    tok = a.work
    c = config()
    lim = c["limits"]
    if re.fullmatch(r"(?:CP|MT)\d{2}", tok):
        return pack_review(tok)
    if re.fullmatch(r"ST\d{2}", tok):
        return pack_study(tok)
    m = manifest(tok)
    npush, ndep = memo_vars(m)
    touched = set(npush) | ndep
    out_path = BUILD / "packs" / f"PACK-{tok}-part{a.part}.md"
    parts = []
    if a.part == 1:
        slugs = matching_studies(touched)
        parts.append(f"<!-- studies: {','.join(slugs)} -->\n# Context pack — memorandum {tok}, Part 1: the studies\n\n*Generated by fie.py from "
                     f"studies/ and this memorandum's manifest. Do not edit. Routing: the variables the manifest pushes and depends on.*")
        parts.append("## Studies on file\n\n" + ("\n".join(study_index_lines()) or "None yet."))
        if not slugs:
            parts.append("## Studies on this provision's variables\n\nNone shares a variable with the manifest. Nothing to load.")
        else:
            parts.append("## Studies on this provision's variables\n\nRead them before the research: they are the record's account of "
                         "the areas this provision enters, as it stands. Write the dossier against them — D7, D10, D13 and D16 especially "
                         "— and cite them as `studies/<slug>`; their figures keep their own tags.")
            size = sum(len(x) for x in parts)
            for s_ in slugs:
                full = study_render(s_)
                parts.append(full if size + len(full) <= lim["pack_chars"] else study_render(s_, short=True) +
                             f"\n\n*Loaded short (pack limit): read `studies/{s_}.md` for the phase sections you need.*")
                size += len(parts[-1])
    elif a.part == 2:
        r = route(tok)
        loaded, size = [], 0
        cards = []
        for score, t, why in r:
            if len(loaded) >= lim["pack_cards"]:
                break
            card = read(BUILD / "cards" / f"CARD-{t}.md")
            if not card:
                continue
            if size + len(card) > lim["pack_chars"] * 0.6:
                card = build_card(t, manifest(t), short=True)
                if size + len(card) > lim["pack_chars"] * 0.6:
                    break
            loaded.append(t)
            size += len(card)
            cards.append(card)
        parts.append(f"<!-- loaded: {','.join(loaded) or 'none'} -->")
        parts.append(f"# Context pack — memorandum {tok}, Part 2\n\n*Generated by fie.py from the manifests and cards. Do not edit. "
                     f"Routing: shared world variables (schema/VARIABLES.toml).*")
        parts.append("## Routing\n\n| Memo | Score | Loaded | Shared variables |\n|---|---|---|---|\n" +
                     "\n".join(f"| {t} | {s:.1f} | {'yes' if t in loaded else 'no'} | {'; '.join(w)} |" for s, t, w in r)
                     if r else "## Routing\n\nNo earlier memorandum shares a variable with this one.")
        not_loaded = [t for _, t, _ in r if t not in loaded]
        if not_loaded:
            parts.append(f"Not loaded (lower overlap): {', '.join(not_loaded)}. Pull detail with `fie.py grep` or by reading memos/MMM/.")
        parts.append("## Standing directives\n\n" + ("\n".join(register_lines("directives.md")) or "None."))
        er = errata_for(set(loaded))
        if er:
            parts.append("## Errata affecting loaded memoranda\n\n" + "\n\n".join(er))
        own = read(BUILD / "cards" / f"CARD-{tok}.md")
        parts.append("## This memorandum's own card (from Part 1 — read this, not part1.md)\n\n" + (own or "Not built yet: run fie.py build."))
        parts.append("## Cards\n\n" + ("\n\n---\n\n".join(cards) if cards else "None."))
        parts.append("## Variable ledgers\n\n" + "\n\n".join(
            f"### {v}\n" + ("\n".join(ledger_lines(v)) or "No earlier contributions.") for v in sorted(touched)))
        parts.append("## Settled positions on these variables\n\n" + ("\n".join(positions_for(touched)) or "None."))
        parts.append("## Provision index (every provision in theater)\n\n" + ("\n".join(provision_index_lines()) or "None yet."))
        parts.append("## Gap register (latest status)\n\n" + ("\n".join(latest_by_key(register_lines("gaps.md"))) or "None."))
        _, st_txt = studies_pack_section(touched, 2)
        if st_txt:
            parts.append(st_txt)
    elif a.part == 3:
        es = read(HIST / "endstate.toml")
        rows = []
        for p in phases():
            txt = read(CHAP / f"{p['id']}.md")
            fm, _, body = parse_chapter(txt)
            rows.append(f"| {p['id']} | {p['title']} | {fmt_ym(p['start'])} – {fmt_ym(p['end'])} | {fm.get('last_revised', '-')} | "
                        f"{len(parse_events(body))} | {words(body)} |")
        log = read(HIST / "TRAJECTORY-LOG.md")
        entries = re.split(r"(?=^## )", log, flags=re.M)[1:]
        p2 = read(work_dir(tok) / "part2.md")
        fr = [b for k, _, b in card_blocks(p2) if k == "findings"]
        total = sum(len(read(CHAP / f"{p['id']}.md")) for p in phases())
        full = total <= lim["chapters_full_read_chars"]
        parts.append(f"<!-- loaded: chapters -->\n# Context pack — memorandum {tok}, Part 3\n\n*Generated by fie.py. Do not edit.*")
        if full:
            parts.append(f"## Read next\n\nEvery chapter in `history/chapters/`, in phase order — the whole war as it now stands "
                         f"({total:,} characters, ~{total // 4:,} tokens).")
        else:
            parts.append(f"## Read next — digest mode\n\nThe chapters total {total:,} characters (~{total // 4:,} tokens), over the "
                         f"full-read limit. Read in full only the chapters you are likely to change (and the one before each, for its "
                         f"ending); for the rest, the digests below are exact extracts. Read any other chapter in full before you "
                         f"stage it.")
            parts.append("## Chapter digests\n\n" + "\n\n".join(chapter_digest(p["id"]) for p in phases()))
            parts.append("Read in full: only the chapters you will change. Stage and change them with one amend file (procedures/PART3.md).")
        parts.append("## Phases\n\n| Phase | Title | Dates | Last revised | Events | Words |\n|---|---|---|---|---|---|\n" + "\n".join(rows))
        parts.append("## End state now (history/endstate.toml)\n\n```toml\n" + es.strip() + "\n```")
        parts.append("## This memorandum's own card (Parts 1–2 — read this, not the part files)\n\n" + (read(BUILD / "cards" / f"CARD-{tok}.md") or "Not built yet: run fie.py build."))
        parts.append("## Standing directives\n\n" + ("\n".join(register_lines("directives.md")) or "None."))
        parts.append("## Settled positions on this memorandum's variables\n\n" + ("\n".join(positions_for(touched)) or "None."))
        parts.append("## Recurring persons\n\n" + ("\n".join(latest_by_key(register_lines("persons.md"))) or "None yet."))
        parts.append(f"## Trajectory Log — last {lim['log_entries_in_pack']} entries\n\n" +
                     ("".join(entries[-lim['log_entries_in_pack']:]).strip() or "No entries yet."))
        _, st_txt = studies_pack_section(touched, 3)
        if st_txt:
            parts.append(st_txt)
    else:
        die("--part must be 1, 2 or 3")
    text = "\n\n".join(parts) + "\n"
    if len(text) > lim["pack_chars"]:
        print(f"WARNING: pack is {len(text):,} characters, over the {lim['pack_chars']:,} limit")
    write(out_path, text)
    print(f"Wrote {rel(out_path)} ({len(text):,} characters, ~{len(text)//4:,} tokens)")


def pack_review(tok: str):
    lim = config()["limits"]
    kind = tok[:2]
    prev = [t for t in review_tokens(kind) if t < tok and review_done(t)]
    after = int(load_toml(work_dir(prev[-1]) / "review.toml").get("after_memo", "0")) if prev else 0
    done = [t for t, _ in manifests(("complete",))]
    since = [t for t in done if int(t) > after]
    parts = [f"# Context pack — {tok}\n\n*Generated by fie.py. Do not edit. Covers memoranda {since[0] if since else '-'}–{since[-1] if since else '-'} "
             f"(since {'the last ' + ('checkpoint' if kind == 'CP' else 'meta-checkpoint') if prev else 'the start'}).*"]
    if kind == "CP":
        n = len(review_tokens("CP"))
        ph = phase_ids()
        parts.append(f"## Coherence review this checkpoint\n\nPhase **{ph[(n - 1) % len(ph)]}** (rotating through {', '.join(ph)}).")
        swept = set()
        for t in review_tokens("CP"):
            for b in sum((block_bodies(read(f), "swept") for f in work_dir(t).glob("*.md")), []):
                swept |= set(re.findall(r"[A-Z]+\.[a-z_]+", b))
        counts = []
        for v in var_ids():
            k = len(ledger_lines(v))
            if k >= 2:
                counts.append((k, v))
        cand = [v for k, v in sorted(counts, reverse=True) if v not in swept][:5] or [v for k, v in sorted(counts, reverse=True)][:5]
        parts.append("## Interaction sweep — suggested variables\n\n" + ("\n\n".join(f"### {v}\n" + "\n".join(ledger_lines(v)) for v in cand) or "Too few provisions yet."))
    chains = []
    for t in since:
        for para in paragraphs(read(work_dir(t) / "part3.md")):
            if re.match(r"\*\*C\d{3}-\d+\*\*", para):
                chains.append(para)
    parts.append("## Causal chains from these memoranda\n\n" + ("\n\n".join(chains) or "None."))
    cards = [read(BUILD / "cards" / f"CARD-{t}.md") for t in since]
    parts.append("## Cards\n\n" + "\n\n---\n\n".join(c for c in cards if c))
    log = read(HIST / "TRAJECTORY-LOG.md")
    parts.append("## Trajectory Log\n\n" + (log.split("\n", 2)[2] if kind == "MT" else "".join(
        e for e in re.split(r"(?=^## )", log, flags=re.M)[1:] if any(f"Memo {t}" in e[:20] for t in since))))
    parts.append("## End state and its history\n\n```toml\n" + read(HIST / "endstate.toml").strip() + "\n```")
    parts.append("## Settled positions\n\n" + ("\n".join(register_lines("positions.md")) or "None."))
    parts.append("## Standing directives\n\n" + ("\n".join(register_lines("directives.md")) or "None."))
    parts.append("## Gap register (latest status)\n\n" + ("\n".join(latest_by_key(register_lines("gaps.md"))) or "None."))
    parts.append("## Provision index\n\n" + ("\n".join(provision_index_lines()) or "None."))
    if kind == "CP" and study_slugs():
        rows, qs = [], []
        for s_ in study_slugs():
            fm_s, _, b_s = parse_chapter(study_text(s_))
            dr = study_drift(s_)
            rows.append(f"| {s_} | {fm_s.get('as_of', '?')} | {dr['entries']} | {dr['drift']:.1f} | {dr['chapter_moves']} | "
                        f"{', '.join(dr['contradicted_by']) or '—'} | {'RE-RUN ADVISED' if dr['advise'] else 'fold'} |")
            q = (section(b_s, 2, "Questions for the record") or "").strip()
            if q:
                qs.append(f"### {s_}\n{q}")
        parts.append("## Studies\n\nFold every study with since-entries (step 8a): `fie.py study fold CPnn <slug>`. Advice is the script's, "
                     "from rules/CONFIG.toml [studies]; the checkpoint decides.\n\n| Study | As of memo | Since-entries | Largest drift "
                     "(midpoint) | Chapter moves recorded | Contradicted by | Advice |\n|---|---|---|---|---|---|---|\n" + "\n".join(rows)
                     + ("\n\n### Questions the studies raised\n\n" + "\n\n".join(qs) if qs else ""))
    elif kind == "MT" and study_slugs():
        parts.append("## Studies on file\n\n" + "\n".join(study_index_lines()))
    parts.append(build_enemy().replace("# The enemy's war", "## The enemy's war", 1).replace("\n## ", "\n### "))
    text = "\n\n".join(parts) + "\n"
    if len(text) > lim["pack_chars"]:
        print(f"WARNING: pack is {len(text):,} characters, over the {lim['pack_chars']:,} limit — read the cards in two passes")
    out = BUILD / "packs" / f"PACK-{tok}.md"
    write(out, text)
    print(f"Wrote {rel(out)} ({len(text):,} characters, ~{len(text)//4:,} tokens). Memoranda covered: {', '.join(since) or 'none'}")


# ----------------------------------------------------------------------------- chapters staging

def cmd_chapters(a):
    tok = a.work
    d = work_dir(tok) / "chapters"
    valid = phase_ids()
    for pid in a.phases:
        if pid not in valid:
            die(f"{pid} is not a current phase ({', '.join(valid)})")
        src = CHAP / f"{pid}.md"
        if not src.exists():
            die(f"{rel(src)} does not exist; run BASELINE")
        dst = d / f"{pid}.md"
        if dst.exists():
            print(f"{rel(dst)} already staged (kept)")
        else:
            d.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"Staged {rel(dst)} — edit it in place; do not rewrite unchanged passages")
    for pid in a.drop or []:
        p = d / f"{pid}.md"
        if p.exists():
            p.unlink()
            print(f"Dropped {rel(p)}")
    staged = sorted(p.stem for p in d.glob("P*.md")) if d.exists() else []
    if (work_dir(tok) / "manifest.toml").exists():
        set_manifest_field(tok, "phases_changed", "[" + ", ".join(f'"{p}"' for p in staged) + "]")
    print(f"Phases staged for {tok}: {', '.join(staged) or 'none'}")


def phase_for_date(d: str) -> str | None:
    k = date_key(d)
    if not k:
        return None
    ym = f"{k[0]:04d}-{k[1] or 1:02d}"
    for p in phases():
        if p["start"] <= ym <= p["end"]:
            return p["id"]
    return None


def cmd_amend(a):
    """Apply a file of whole event blocks and phase sections to the staged chapters in one step.
    Existing event IDs are replaced in place; new IDs are inserted in date order in the phase their date falls in;
    '## Pk · Overview', '## Pk · How the phase ends' and '## Pk · end_vector' replace those parts of chapter Pk."""
    tok = a.work
    d = work_dir(tok)
    src = read(Path(a.file) if Path(a.file).is_absolute() else ROOT / a.file)
    if not src.strip():
        die(f"{a.file} is empty or missing")
    blocks = []
    ms = list(re.finditer(r"^## (.+)$", src, re.M))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(src)
        blocks.append((m.group(1).strip(), src[m.end():end].strip("\n")))
    existing = all_events(staged_chapters(tok))
    texts = {}

    def chapter(pid):
        if pid not in texts:
            dst = d / "chapters" / f"{pid}.md"
            if not dst.exists():
                if not (CHAP / f"{pid}.md").exists():
                    die(f"chapter {pid} does not exist")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(CHAP / f"{pid}.md", dst)
                print(f"Staged {rel(dst)}")
            texts[pid] = read(dst)
        return texts[pid]

    done = []
    for head, body in blocks:
        em = re.match(r"(EV" + WORK_RE + r"-\d+) · (.+)$", head)
        pm = re.match(r"(P\d+) · (Overview|How the phase ends|end_vector|snapshot)\s*$", head)
        if em:
            eid = em.group(1)
            block = f"## {head}\n{body}\n\n"
            if eid in existing:
                pid = existing[eid][0]
                t = chapter(pid)
                fm, raw, b = parse_chapter(t)
                ev = next(e for e in parse_events(b) if e["id"] == eid)
                b = b[:ev["start"]] + block + b[ev["end"]:].lstrip("\n")
                texts[pid] = f"+++\n{raw}\n+++\n{b}"
                done.append(f"replaced {eid} in {pid}")
            else:
                fields = em.group(2).split(" · ")
                pid = phase_for_date(fields[-4]) if len(fields) >= 5 else None
                if not pid:
                    die(f"cannot place new event {eid}: its date '{fields[-4] if len(fields) >= 5 else '?'}' falls in no phase")
                t = chapter(pid)
                fm, raw, b = parse_chapter(t)
                k = date_key(fields[-4])
                at = None
                for e in parse_events(b):
                    ek = date_key(e.get("date", ""))
                    if ek and ek > k:
                        at = e["start"]
                        break
                if at is None:
                    end_sec = re.search(r"^## How the phase ends", b, re.M)
                    at = end_sec.start() if end_sec else len(b)
                b = b[:at] + block + b[at:]
                texts[pid] = f"+++\n{raw}\n+++\n{b}"
                existing[eid] = (pid, {})
                done.append(f"inserted {eid} in {pid}")
        elif pm:
            pid, what = pm.group(1), pm.group(2)
            t = chapter(pid)
            fm, raw, b = parse_chapter(t)
            if what in ("end_vector", "snapshot"):
                keys = vector_keys()
                if what == "snapshot" and not isinstance(fm.get("snapshot"), dict):
                    die(f"{pid} has no [snapshot] table: only a phase with a snapshot date in history/phases.toml carries one")
                for line in body.splitlines():
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    try:
                        kv = tomllib.loads(line)
                    except tomllib.TOMLDecodeError as e:
                        die(f"amend {pid} {what}: cannot read '{line[:70]}': {e}")
                    flat = {}
                    for k1, v1 in kv.items():
                        if isinstance(v1, dict) and not ({"low", "high", "conf"} & set(v1)):
                            flat.update({f"{k1}.{k2}": v2 for k2, v2 in v1.items()})
                        else:
                            flat[k1] = v1
                    for var, val in flat.items():
                        if var not in keys:
                            die(f"amend {pid} {what}: '{var}' is not a headline variable or one of its facets")
                        fm[what][var] = val
                raw = dump_front_matter(fm)
            elif what == "Overview":
                title = re.search(r"^# .+$", b, re.M)
                first = re.search(r"^## ", b[title.end():], re.M)
                cut = title.end() + first.start() if first else len(b)
                b = b[:title.end()] + "\n\n" + body + "\n\n" + b[cut:]
            else:
                sec = re.search(r"^## How the phase ends\n", b, re.M)
                nxt = re.search(r"^#{1,2} ", b[sec.end():], re.M) if sec else None
                endp = sec.end() + nxt.start() if nxt else len(b)
                b = (b[:sec.start()] if sec else b.rstrip() + "\n\n") + f"## How the phase ends\n{body}\n" + (b[endp:] if sec else "")
            texts[pid] = f"+++\n{raw}\n+++\n{b}"
            done.append(f"replaced {what} of {pid}")
        else:
            die(f"amend: heading '## {head[:60]}' is neither an event header nor '## Pk · Overview | How the phase ends | end_vector | snapshot'")
    for pid, t in texts.items():
        write(d / "chapters" / f"{pid}.md", re.sub(r"\n{3,}", "\n\n", t))
    staged = sorted(p.stem for p in (d / "chapters").glob("P*.md"))
    if (d / "manifest.toml").exists():
        set_manifest_field(tok, "phases_changed", "[" + ", ".join(f'"{p}"' for p in staged) + "]")
    print("\n".join(done))
    print(f"Phases staged for {tok}: {', '.join(staged)}")


def staged_chapters(tok: str) -> dict[str, str]:
    d = work_dir(tok) / "chapters"
    return {p.stem: read(p) for p in sorted(d.glob("P*.md"))} if d.exists() else {}


# ----------------------------------------------------------------------------- checks

def check_manifest(tok: str, m: dict, errors: list, warnings: list):
    c = config()
    vids = var_ids()
    for k in ["title", "received"]:
        if not str(m.get(k, "")).strip():
            errors.append(f"manifest: '{k}' is blank")
    if str(m.get("memo")) != tok:
        errors.append(f"manifest: memo = {m.get('memo')!r}, expected '{tok}'")
    provs = m.get("provision", [])
    if not provs:
        errors.append("manifest: no [[provision]]")
    pids = set()
    for i, p in enumerate(provs):
        lab = f"manifest provision {i + 1}"
        pid = p.get("id", "")
        if not re.fullmatch(rf"P{tok}[a-z]", pid):
            errors.append(f"{lab}: id '{pid}' should be P{tok}a, P{tok}b …")
        pids.add(pid)
        for k in ["designation", "category", "quantity", "ceiling_spaces", "arrival"]:
            if not str(p.get(k, "")).strip():
                errors.append(f"{lab} ({pid}): '{k}' is blank")
        if p.get("category") and p["category"] not in CATEGORIES:
            errors.append(f"{lab} ({pid}): category '{p['category']}' not in {', '.join(CATEGORIES)}")
        if not p.get("systems"):
            errors.append(f"{lab} ({pid}): systems is empty")
        for s in p.get("systems", []):
            if s not in SYSTEMS:
                errors.append(f"{lab} ({pid}): system '{s}' not in {', '.join(SYSTEMS)}")
        arr = str(p.get("arrival", ""))
        if arr and not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", arr):
            errors.append(f"{lab} ({pid}): arrival '{arr}' should be YYYY-MM or YYYY-MM-DD")
        elif arr and arr < c["campaign_opens"][:len(arr)]:
            errors.append(f"{lab} ({pid}): arrival {arr} is before the campaign opens ({c['campaign_opens']})")
        for k in ["quantity", "ceiling_spaces"]:
            if p.get(k) and not TAG_RE.search(str(p[k])):
                warnings.append(f"{lab} ({pid}): {k} '{p[k]}' has no provenance tag")
    pushed = set()
    for j, x in enumerate(m.get("push", [])):
        if x.get("var") not in vids:
            errors.append(f"manifest push {j + 1}: var '{x.get('var')}' is not in schema/VARIABLES.toml")
        if "band" in x:
            b = x.get("band")
            if int(tok) > LEGACY_LAST_MEMO:
                errors.append(f"manifest push {j + 1} ({x.get('var')}): 'band' is the old −3..+3 scale; from v1.0.8 write dlow, dhigh (or plow, phigh), at and conf in the variable's unit (schema/VARIABLES.toml)")
            elif not isinstance(b, int) or not -3 <= b <= 3 or b == 0:
                errors.append(f"manifest push {j + 1} ({x.get('var')}): band {b!r} must be a whole number from -3 to 3, not 0")
        elif int(tok) <= SCALE_LAST_MEMO:
            lo, hi = x.get("low"), x.get("high")
            if not (isinstance(lo, int) and isinstance(hi, int)) or not -SCALE <= lo <= hi <= SCALE:
                errors.append(f"manifest push {j + 1} ({x.get('var')}): low {lo!r} and high {hi!r} must be whole numbers with -{SCALE} ≤ low ≤ high ≤ {SCALE}")
            if x.get("conf") not in PUSH_CONFS:
                errors.append(f"manifest push {j + 1} ({x.get('var')}): conf {x.get('conf')!r} must be one of {', '.join(PUSH_CONFS)}")
        else:
            f = form(x)
            if f is None or f[0] == "low":
                errors.append(f"manifest push {j + 1} ({x.get('var')}): from v1.0.8 a push is a change in the variable's unit: dlow and dhigh, or plow and phigh (% of history's figure), with at = \"Pk\" (schema/VARIABLES.toml)")
            else:
                lo, hi = x.get(f[0]), x.get(f[1])
                if not (num(lo) and num(hi)) or lo > hi:
                    errors.append(f"manifest push {j + 1} ({x.get('var')}): {f[0]} {lo!r} and {f[1]} {hi!r} must be numbers with {f[0]} ≤ {f[1]}")
                elif lo == hi == 0:
                    errors.append(f"manifest push {j + 1} ({x.get('var')}): a push of 0 moves nothing — drop it or make it a depend")
            if x.get("at") and x.get("at") not in phase_ids():
                errors.append(f"manifest push {j + 1} ({x.get('var')}): at {x.get('at')!r} is not a current phase")
            elif not x.get("at"):
                warnings.append(f"manifest push {j + 1} ({x.get('var')}): no 'at' — say by the end of which phase the change is measured")
            if x.get("conf") not in PUSH_CONFS:
                errors.append(f"manifest push {j + 1} ({x.get('var')}): conf {x.get('conf')!r} must be one of {', '.join(PUSH_CONFS)}")
            if facet_map().get(x.get("var")):
                warnings.append(f"manifest push {j + 1} ({x.get('var')}): this variable has facets — push the facet(s) the provision acts on, or say in the note why it acts on all of them equally")
        if x.get("provision") not in pids:
            errors.append(f"manifest push {j + 1}: provision '{x.get('provision')}' is not in this manifest")
        if not str(x.get("note", "")).strip():
            warnings.append(f"manifest push {j + 1} ({x.get('var')}): no note")
        pushed.add(x.get("provision"))
    for j, x in enumerate(m.get("depend", [])):
        if x.get("var") not in vids:
            errors.append(f"manifest depend {j + 1}: var '{x.get('var')}' is not in schema/VARIABLES.toml")
        if x.get("provision") not in pids:
            errors.append(f"manifest depend {j + 1}: provision '{x.get('provision')}' is not in this manifest")
    for pid in pids - pushed:
        errors.append(f"manifest: {pid} pushes no variable — every provision moves something, or say why in §1")
    for sc in m.get("status_change", []):
        if not any(sc.get("provision") == p.get("id") for _, om in manifests(("complete",)) for p in om.get("provision", [])):
            errors.append(f"manifest status_change: '{sc.get('provision')}' is not an earlier provision")


def check_part(tok: str, part: int, stamping: bool = False) -> tuple[list, list, str, dict]:
    c = config()
    fl = c["floors"]
    errors, warnings, info = [], [], {}
    d = work_dir(tok)
    m = manifest(tok)
    check_manifest(tok, m, errors, warnings)
    text = read(d / f"part{part}.md")
    if not text.strip():
        errors.append(f"{rel(d)}/part{part}.md is missing or empty")
        return errors, warnings, "", info
    if "<!-- audit -->" not in text:
        errors.append(f"part{part}: the '<!-- audit -->' marker is missing from the top")
    lab = f"part{part}"
    srcs = sources_defined(tok)
    check_tags(text, errors, lab, sources=srcs, token=tok)
    desig = designations(text)
    dev = m.get("deviation", {}).get(f"part{part}", "none")
    prov_ids = [p.get("id") for p in m.get("provision", [])]

    if part == 1:
        secs = {re.search(r"— (P\d{3}[a-z])\s*$", h).group(1): b for h, b in sections(text, 2)
                if h.startswith("§1.") and re.search(r"— (P\d{3}[a-z])\s*$", h)}
        field_counts = []
        for pid in prov_ids:
            body = secs.get(pid)
            if body is None:
                errors.append(f"part1: no '## §1.n <designation> — {pid}' section")
                continue
            got = {}
            for h, b in sections(body, 3):
                mm = re.match(r"D(\d+) ·", h)
                if mm:
                    got[int(mm.group(1))] = b
            missing = [n for n in range(1, fl["dossier_fields"] + 1) if n not in got]
            empty = [n for n, b in got.items() if words(b) < 8]
            if missing:
                errors.append(f"part1 {pid}: missing fields D{', D'.join(map(str, missing))}")
            if empty:
                errors.append(f"part1 {pid}: fields D{', D'.join(map(str, empty))} are empty or a bare line")
            field_counts.append(f"{len(got) - len(empty)}/{fl['dossier_fields']}")
            kinds = {k for k, p, _ in card_blocks(body) if p == pid and _}
            for k in ["figures", "negative", "denies", "verdict"]:
                if k not in kinds:
                    errors.append(f"part1 {pid}: card:{k} block is missing or empty")
        unt = untagged_figures("\n".join(secs.values()))
        uniq = list(dict.fromkeys(unt))
        for u in uniq[:25]:
            k = unt.count(u)
            warnings.append(f"part1 untagged figure: “{u}”" + (f" (×{k})" if k > 1 else ""))
        if len(uniq) > 25:
            warnings.append(f"part1: {len(uniq) - 25} more untagged figures")
        used = {int(n) for n in re.findall(r"\[S(\d+)\]", text)}
        for n in sorted(srcs - used):
            warnings.append(f"sources.md: [S{n}] is never cited")
        if len(desig) < fl["designations_per_part"]:
            warnings.append(f"part1: ~{len(desig)} distinct designations, below the floor of {fl['designations_per_part']} (A11)")
        audit = (f"Audit — Memo {tok}, Part 1/3 · v{read(ROOT / 'VERSION').strip()} · provisions: {len(prov_ids)} ({', '.join(prov_ids)}) · "
                 f"dossier fields: {', '.join(field_counts) or '-'} (floor {fl['dossier_fields']}) · tagged figures: {len(TAG_RE.findall(strip_comments(text)))} · "
                 f"untagged warnings: {len(unt)} · sources: {len(srcs)} · designations: ~{len(desig)} (floor {fl['designations_per_part']}) · "
                 f"variables pushed: {len({x.get('var') for x in m.get('push', [])})} · structural deviation: {dev}")

    elif part == 2:
        if not status_at_least(m, "part1"):
            errors.append("Part 1 is not finished")
        for h in ["§2 Part A", "§2 Part B", "§2 Part C", "§2 Findings register", "§3 Changes to existing forces"]:
            if section(text, 2, h) is None:
                errors.append(f"part2: heading '## {h} …' is missing")
        pa = section(text, 2, "§2 Part A") or ""
        ec = re.findall(r"^#### (EC(\d{3})-(\d+)) · (.+)$", pa, re.M)
        for full, memo_no, _, _ in ec:
            if memo_no != tok:
                errors.append(f"part2: {full} should carry this memo's number ({tok})")
        live = [x for x in ec if "(abandoned)" not in x[3]]
        aband = [x for x in ec if "(abandoned)" in x[3]]
        need = fl["employment_concepts"] * max(1, len(prov_ids))
        if len(live) < need:
            warnings.append(f"part2: {len(live)} employment concepts, below the floor of {need} ({fl['employment_concepts']} per provision)")
        pb = section(text, 2, "§2 Part B") or ""
        chan = {h: b for h, b in sections(pb, 3)}
        filled = 0
        for ch in CHANNELS:
            if ch not in chan:
                errors.append(f"part2: channel '### {ch}' is missing")
            elif ch == "Open channel":
                filled += 1 if words(chan[ch]) >= 10 else 0
            elif words(chan[ch]) >= 25:
                filled += 1
            else:
                warnings.append(f"part2: channel '{ch}' has under 25 words — content or a defended null of two sentences")
        if filled < fl["channels"]:
            warnings.append(f"part2: {filled} channels with content, below the floor of {fl['channels']}")
        fids = []
        for para in paragraphs(text):
            mm = re.match(r"\*\*F(\d{3})-(\d+)(?:\s·\s[^*]+)?\*\*", para)
            if mm:
                if mm.group(1) != tok:
                    errors.append(f"part2: finding F{mm.group(1)}-{mm.group(2)} should carry this memo's number ({tok})")
                fids.append(int(mm.group(2)))
        if fids != list(range(1, len(fids) + 1)):
            errors.append(f"part2: findings must be numbered 1, 2, 3 … in order of appearance; found {fids}")
        reg = [b for k, _, b in card_blocks(text) if k == "findings"]
        reg_ids = set(int(x) for x in re.findall(rf"F{tok}-(\d+)", reg[0])) if reg else set()
        if not reg:
            errors.append("part2: card:findings block is missing")
        elif set(fids) != reg_ids:
            errors.append(f"part2: findings register lists {sorted(reg_ids)} but the text has {sorted(set(fids))}")
        if not [b for k, _, b in card_blocks(text) if k == "concepts" and b]:
            errors.append("part2: card:concepts block is missing or empty")
        cd = bool(re.search(r"\*\*F\d{3}-\d+ · Counter-directional\*\*", text)) or "<!-- cd:none -->" in text
        spe = bool(re.search(r"\*\*F\d{3}-\d+ · Strongest positive\*\*", text)) or "<!-- spe:modest -->" in text
        if not cd:
            errors.append("part2: no counter-directional finding and no '<!-- cd:none -->' — the search is mandatory")
        if not spe:
            errors.append("part2: no strongest positive effect and no '<!-- spe:modest -->' — the search is mandatory")
        s3 = section(text, 2, "§3 Changes to existing forces") or ""
        if words(s3) < 150:
            warnings.append("part2: §3 is under 150 words")
        if manifests(("complete",)) and "Prior provisions" not in s3 and not re.search(r"P\d{3}[a-z]", s3):
            warnings.append("part2: §3 names no earlier provision — the checklist includes every prior injected unit by name")
        if len(desig) < fl["designations_per_part"]:
            warnings.append(f"part2: ~{len(desig)} distinct designations, below the floor of {fl['designations_per_part']} (A11)")
        npush_, ndep_ = memo_vars(m)
        st_req = matching_studies(set(npush_) | ndep_)
        verdicts = {s_: v_ for s_, v_ in AGAINST_RE.findall(text)}
        if st_req:
            pa_heads = [h for h, _ in sections(section(text, 2, "§2 Part A") or "", 3)]
            if "Against the studies" not in pa_heads:
                errors.append(f"part2: '### Against the studies' is missing from §2 Part A — this provision touches the variables of {', '.join(st_req)}")
            for s_ in st_req:
                if s_ not in verdicts:
                    errors.append(f"part2: no '<!-- against {s_}: consistent -->' or '<!-- against {s_}: contradicts -->' — judge the pushes against that study and say which")
        for s_ in verdicts:
            if s_ not in study_slugs():
                errors.append(f"part2: '<!-- against {s_}: … -->' names no study in studies/")
        st_audit = ", ".join(f"{s_} {verdicts.get(s_, 'NOT JUDGED')}" for s_ in st_req) or "none on these variables"
        pack = read(BUILD / "packs" / f"PACK-{tok}-part2.md")
        loaded = re.search(r"<!-- loaded: (.*?) -->", pack)
        if not pack:
            warnings.append("part2: no context pack was built (fie.py pack NNN --part 2)")
        audit = (f"Audit — Memo {tok}, Part 2/3 · v{read(ROOT / 'VERSION').strip()} · cards loaded: {loaded.group(1) if loaded else 'none'} · "
                 f"channels: {filled}/10 (floor {fl['channels']}) · findings numbered: {len(fids)} · employment concepts: {len(live)}"
                 f"{f' + {len(aband)} abandoned' if aband else ''} (floor {need}) · counter-directional: "
                 f"{'yes' if re.search(r'· Counter-directional', text) else 'searched, none found'} · strongest positive: "
                 f"{'yes' if re.search(r'· Strongest positive', text) else 'searched, genuine assessment is modest'} · "
                 f"designations: ~{len(desig)} · studies: {st_audit} · structural deviation: {dev}")

    elif part == 3:
        if not status_at_least(m, "part2"):
            errors.append("Part 2 is not finished")
        staged = staged_chapters(tok)
        changed = [str(x) for x in m.get("phases_changed", [])]
        if sorted(changed) != sorted(staged):
            errors.append(f"manifest phases_changed {changed} does not match staged chapters {sorted(staged)}; use fie.py chapters")
        all_ids = all_events(staged)
        p2 = read(d / "part2.md")
        fid_set = set(re.findall(rf"F{tok}-\d+", p2))
        spe_id = re.search(rf"\*\*(F{tok}-\d+) · Strongest positive\*\*", p2)
        phs = phase_ids()
        clock_from = phs.index(fl["clock_from_phase"]) if fl["clock_from_phase"] in phs else 0
        per_phase_events, new_ops, free, paras_short, clocks, carried_ok, ripple = {}, 0, 0, [], 0, 0, []
        touched_text = ""
        if section(text, 2, "§4.0 The course of the war") is None:
            errors.append("part3: '## §4.0 The course of the war' is missing")
        else:
            w = words(section(text, 2, "§4.0"))
            lo, hi = c["limits"]["course_of_war_words"]
            if not lo <= w <= hi:
                warnings.append(f"part3: §4.0 is {w} words (guide {lo}–{hi})")
        for i, pid in enumerate(phs):
            sec = section(text, 2, f"§4.{pid} ")
            if sec is None:
                errors.append(f"part3: '## §4.{pid} …' is missing")
                continue
            if pid in staged:
                if f"<!-- chapter {pid} -->" not in sec:
                    errors.append(f"part3 §4.{pid}: revised phase lacks '<!-- chapter {pid} -->'")
                need = ["Mechanism", "Enemy response and initiative", "Causal chains", "Downstream"] + (["Clock"] if i >= clock_from else [])
                have = [h for h, _ in sections(sec, 3)]
                for h in need:
                    if h not in have:
                        errors.append(f"part3 §4.{pid}: '### {h}' is missing")
                if i >= clock_from and "Clock" in have:
                    clocks += 1
                lbl = f"chapter {pid} (staged)"
                check_chapter(staged[pid], pid, errors, warnings, lbl, all_ids)
                tev = touched_events(tok, pid, staged[pid])
                per_phase_events[pid] = len(tev)
                new_ops += sum(1 for e in tev if e.get("origin") == "NEW" and e.get("title", "").startswith("Operation"))
                free += sum(1 for e in tev if e.get("origin") == "FREE")
                for e in tev:
                    if e.get("ok") and e.get("origin") != "CANCELLED" and not initiative(e):
                        warnings.append(f"chapter {pid}: {e['id']} has no '*Initiative: enemy | allied | both | neither*' first line")
                if len(tev) < fl["events_per_full_phase"]:
                    warnings.append(f"part3 {pid}: {len(tev)} events created or changed, below the floor of {fl['events_per_full_phase']}")
                npar = sum(len(paragraphs(e["body"])) for e in tev) + len(paragraphs(sec))
                if npar < fl["paragraphs_per_full_phase"]:
                    paras_short.append(pid)
                    warnings.append(f"part3 {pid}: {npar} paragraphs, below the floor of {fl['paragraphs_per_full_phase']}")
                ttext = sec + "\n".join(e["text"] for e in tev)
                touched_text += ttext
                cited = set(re.findall(rf"F{tok}-\d+", ttext)) & fid_set
                if len(cited) >= fl["findings_carried_per_full_phase"]:
                    carried_ok += 1
                else:
                    warnings.append(f"part3 {pid}: carries no §2 finding by ID (floor {fl['findings_carried_per_full_phase']})")
                old_ids = {e["id"] for e in parse_events(parse_chapter(read(CHAP / f"{pid}.md"))[2])}
                new_ids = {e["id"] for e in parse_events(parse_chapter(staged[pid])[2])}
                for gone in sorted(old_ids - new_ids):
                    errors.append(f"chapter {pid}: event {gone} was deleted — mark it CANCELLED instead")
                for e in tev:
                    if e["id"] not in old_ids and not e["id"].startswith(f"EV{tok}-"):
                        errors.append(f"chapter {pid}: new event {e['id']} should be numbered EV{tok}-n")
                oldv = parse_chapter(read(CHAP / f"{pid}.md"))[0].get("end_vector", {})
                newv = parse_chapter(staged[pid])[0].get("end_vector", {})
                moved = [f"{k} {fmt_val(oldv.get(k))}→{fmt_val(newv.get(k))}" for k in newv
                         if rng(newv.get(k)) is not None and vkey(newv.get(k)) != vkey(oldv.get(k))]
                if moved and i + 1 < len(phs) and phs[i + 1] not in staged:
                    nsec = section(text, 2, f"§4.{phs[i + 1]} ") or ""
                    ripple.append(f"{pid}→{phs[i + 1]}")
                    if "<!-- ripple-addressed -->" not in nsec:
                        warnings.append(f"ripple: {pid}'s end vector moved ({'; '.join(moved)}) but {phs[i + 1]} is null without '<!-- ripple-addressed -->' — the null must answer the incoming change")
            else:
                if f"<!-- null {pid} -->" not in sec:
                    errors.append(f"part3 §4.{pid}: unrevised phase lacks '<!-- null {pid} -->' and its stated null")
                else:
                    w = words(sec)
                    lo, hi = c["limits"]["null_words"]
                    if not lo <= w <= hi:
                        warnings.append(f"part3 §4.{pid}: null is {w} words (guide {lo}–{hi}); a null is a defended claim, not padding")
        chains = []
        for para in paragraphs(text):
            mm = re.match(r"\*\*(C(\d{3})-\d+)\*\*\s*\[([^\]]+)\]", para)
            if mm:
                if mm.group(2) != tok:
                    errors.append(f"part3: chain {mm.group(1)} should carry this memo's number")
                if mm.group(3) not in LAGS:
                    errors.append(f"part3: chain {mm.group(1)} lag '[{mm.group(3)}]' must be one of {', '.join(LAGS)}")
                links = para.count("→")
                chains.append((mm.group(1), links))
                if links < fl["chain_links"]:
                    warnings.append(f"part3: chain {mm.group(1)} has {links} arrows; it must reach link {fl['chain_links']} ({fl['chain_links']} arrows)")
        full_chains = [c_ for c_, l in chains if l >= fl["chain_links"]]
        if len(full_chains) < fl["chains_per_memo"]:
            warnings.append(f"part3: {len(full_chains)} chains reaching link {fl['chain_links']}, below the floor of {fl['chains_per_memo']}")
        if len(chains) != len({c_ for c_, _ in chains}):
            errors.append("part3: duplicate chain IDs")
        init = text.count("<!-- initiative -->")
        if init < fl["enemy_initiative_per_memo"]:
            warnings.append(f"part3: {init} '<!-- initiative -->' markers, below the floor of {fl['enemy_initiative_per_memo']} (G3)")
        spe_grounded = "n/a (modest)" if "<!-- spe:modest -->" in p2 else (
            "yes" if spe_id and spe_id.group(1) in touched_text else "NO")
        if spe_grounded == "NO":
            warnings.append(f"part3: the strongest positive effect ({spe_id.group(1) if spe_id else '?'}) is not carried into any revised phase")
        for h in ["§4.H Historical comparison", "§4.N Net assessment", "§5 Delta ledger", "§6 Changed / not changed"]:
            if section(text, 2, h) is None:
                errors.append(f"part3: '## {h}' is missing")
        s6 = section(text, 2, "§6") or ""
        ch = sum(1 for l in (section(s6, 3, "What has changed") or "").splitlines() if re.match(r"\s*[-*] ", l))
        nch = sum(1 for l in (section(s6, 3, "What has not changed") or "").splitlines() if re.match(r"\s*[-*] ", l))
        if ch < fl["changed_items"]:
            warnings.append(f"part3 §6: {ch} changed items, below the floor of {fl['changed_items']}")
        if nch < fl["not_changed_items"]:
            warnings.append(f"part3 §6: {nch} not-changed items, below the floor of {fl['not_changed_items']}")
        logs = block_bodies(text, "log")
        if len(logs) != 1 or not logs[0]:
            errors.append("part3: exactly one non-empty <!-- log --> block is required")
        else:
            lo, hi = c["limits"]["log_words"]
            if not lo <= words(logs[0]) <= hi:
                warnings.append(f"part3: log entry is {words(logs[0])} words (guide {lo}–{hi})")
        check_register_blocks(text, tok, errors)
        npush_, ndep_ = memo_vars(m)
        st_req = matching_studies(set(npush_) | ndep_)
        check_study_blocks(text, tok, "part3", errors, st_req)
        es = load_toml(HIST / "endstate.toml")
        if es.get("rung") not in list("abcde") + ["off"]:
            errors.append(f"endstate.toml: rung '{es.get('rung')}' must be a–e or 'off'")
        if es.get("rung") == "off" and not es.get("off_ladder"):
            errors.append("endstate.toml: rung is 'off' but off_ladder does not name the outcome (G5)")
        es_changed = es.get("last_changed") == tok
        if es_changed and not any(h.get("by") == tok for h in es.get("history", [])):
            errors.append(f"endstate.toml: last_changed is {tok} but no [[history]] entry has by = \"{tok}\"")
        sup = check_rung(section(text, 2, "§4.N") or "", "part3 §4.N", errors)
        for pid_, st_ in staged.items():
            snap = parse_chapter(st_)[0].get("snapshot")
            if isinstance(snap, dict):
                unj = [k for k, v in snap.items() if isinstance(v, dict) and v.get("conf") == "unjudged" and "." not in k[len(parent(k)):]]
                if unj:
                    warnings.append(f"chapter {pid_}: the snapshot still has {len(unj)} unjudged headline variable(s) ({', '.join(unj[:4])}{'…' if len(unj) > 4 else ''}) — "
                                    f"a memorandum that revises this phase judges the Republic's state at the snapshot date (DIRMT01-3)")
        if not staged:
            warnings.append("part3: no phase revised — say in §4.N why the provision changes no phase")
        tot_ev = sum(per_phase_events.values())
        audit = (f"Audit — Memo {tok}, Part 3/3 · v{read(ROOT / 'VERSION').strip()} · phases revised: {len(staged)} ({', '.join(staged) or 'none'}), "
                 f"nulled: {len(phs) - len(staged)} · events created or changed: {tot_ev} "
                 f"({', '.join(f'{k} {v}' for k, v in per_phase_events.items()) or '-'}; floor {fl['events_per_full_phase']}/phase) · "
                 f"new operations: {new_ops} · chains reaching link {fl['chain_links']}: {len(full_chains)} (floor {fl['chains_per_memo']}) · "
                 f"phases carrying a §2 finding: {carried_ok}/{len(staged)} · strongest positive grounded: {spe_grounded} · "
                 f"clock stated: {clocks} phase(s) · enemy initiative: {init} · free play: {free} · ripple flags: {len(ripple)}"
                 f"{' (' + ', '.join(ripple) + ')' if ripple else ''} · end state: {'CHANGED' if es_changed else 'unchanged'} "
                 f"(rung {es.get('rung')}; rung test supports {sup}) · studies updated: {', '.join(s_ for s_, _ in STUDY_BLOCK.findall(text)) or 'none'} · "
                 f"structural deviation: {dev}")
    else:
        die("--part must be 1, 2 or 3")
    return errors, warnings, audit, info


def rung_conditions() -> list[dict]:
    return load_toml(ROOT / "rules" / "RUNGS.toml").get("condition", [])


def rung_test(text: str, label: str, errors: list) -> str:
    """Read the <!-- rungtest --> block: one line per condition in rules/RUNGS.toml,
    '- c2 · PASS · <evidence>'. Return the highest rung whose conditions all pass ('a' if none)."""
    conds = rung_conditions()
    blocks = block_bodies(text, "rungtest")
    if not blocks:
        errors.append(f"{label}: the <!-- rungtest --> … <!-- /rungtest --> block is missing (A9, rules/RUNGS.toml)")
        return "?"
    verdict = {}
    for l in [x.strip() for x in blocks[0].splitlines() if x.strip()]:
        mm = re.match(r"[-*]\s*\**([b-e]\d)\**\s*·\s*(PASS|FAIL|OPEN)\s*·\s*(\S.*)$", l)
        if not mm:
            errors.append(f"{label}: rung test line does not read '- c2 · PASS|FAIL|OPEN · evidence': “{l[:80]}”")
            continue
        verdict[mm.group(1)] = mm.group(2)
    for c in conds:
        if c["id"] not in verdict:
            errors.append(f"{label}: rung test has no verdict for {c['id']} ({c['text'][:60]}…)")
    supported = "a"
    for r in "bcde":
        ids = [c["id"] for c in conds if c["rung"] == r]
        if ids and all(verdict.get(i) == "PASS" for i in ids):
            supported = r
    return supported


def check_rung(text: str, label: str, errors: list) -> str:
    sup = rung_test(text, label, errors)
    es = load_toml(HIST / "endstate.toml")
    if sup != "?" and es.get("rung") not in ("off", sup):
        errors.append(f"endstate.toml: rung ({es.get('rung')}) is not the rung the test in {label} supports ({sup}) — "
                      f"change the end state, or the verdicts if the evidence says otherwise")
    return sup


def check_register_blocks(text: str, tok: str, errors: list):
    vids = var_ids()
    known_pos = {re.match(r"- \*\*(\S+)\*\*", l).group(1) for l in register_lines("positions.md")}
    for name, pat in [("positions", r"- \*\*(?:POS|REV)" + re.escape(tok) + r"-\d+\*\* · "),
                      ("persons", r"- \*\*[^*]+\*\* · "),
                      ("directives", r"- \*\*DIR" + re.escape(tok) + r"-\d+\*\* · "),
                      ("gaps", r"- \*\*G-\d+\*\* · "),
                      ("menu", r"- \*\*[^*]+\*\* · gaps: ")]:
        for b in block_bodies(text, name):
            for l in [x for x in b.splitlines() if x.strip()]:
                if not re.match(pat, l):
                    errors.append(f"{name} block: line does not match the register format: “{l[:90]}”")
                    continue
                if name == "positions":
                    mv = re.search(r"vars:\s*([^·]+)", l)
                    for v in ([x.strip() for x in mv.group(1).split(",")] if mv else []):
                        if v not in vids:
                            errors.append(f"positions block: unknown variable '{v}'")
                    if not mv:
                        errors.append(f"positions block: no 'vars:' in “{l[:60]}”")
                    if l.startswith("- **REV"):
                        r = re.search(r"reverses (POS\S+)", l)
                        if not r or r.group(1) not in known_pos:
                            errors.append(f"positions block: reversal must name an existing position: “{l[:80]}”")


def insert_audit(path: Path, audit: str):
    s = read(path)
    lines = s.splitlines()
    out, i = [], 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip() == "<!-- audit -->":
            if i + 1 < len(lines) and lines[i + 1].startswith("*Audit"):
                i += 1
            out.append(f"*{audit}*")
        i += 1
    write(path, "\n".join(out) + "\n")


def append_registers(text: str, tok: str, title: str):
    for name, fname in [("positions", "positions.md"), ("persons", "persons.md"),
                        ("directives", "directives.md"), ("gaps", "gaps.md")]:
        lines = [l for b in block_bodies(text, name) for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        cur = read(HIST / fname)
        add = [l for l in lines if l not in cur.splitlines()]
        if add:
            write(HIST / fname, cur.rstrip("\n") + "\n" + "\n".join(add) + "\n")
            print(f"Appended {len(add)} line(s) to history/{fname}")
    logs = block_bodies(text, "log")
    if logs and logs[0]:
        p = HIST / "TRAJECTORY-LOG.md"
        cur = read(p)
        head = f"## {'Memo ' + tok if re.fullmatch(r'\d{3}', tok) else tok} — {title}"
        entry = f"{head}\n\n{logs[0].strip()}\n"
        pat = re.compile(r"^" + re.escape(head.split(' — ')[0]) + r" — .*?(?=^## |\Z)", re.M | re.S)
        if pat.search(cur):
            cur = pat.sub(lambda _: entry + "\n", cur)
        else:
            cur = cur.rstrip("\n") + "\n\n" + entry
        write(p, cur)
        print("Wrote the Trajectory Log entry")
    menus = [l for b in block_bodies(text, "menu") for l in b.splitlines() if l.strip()]
    if menus:
        p = HIST / "menus.md"
        cur = read(p) or "# Provision menus\n\nOne menu per review, newest last. Written by fie.py from menu blocks.\n"
        head = f"## {tok} — {title}"
        entry = f"{head}\n\n" + "\n".join(menus) + "\n"
        pat = re.compile(r"^" + re.escape(head) + r"\n.*?(?=^## |\Z)", re.M | re.S)
        cur = pat.sub(lambda _: entry + "\n", cur) if pat.search(cur) else cur.rstrip("\n") + "\n\n" + entry
        write(p, cur)
        print(f"Wrote a provision menu of {len(menus)} item(s)")


def promote(tok: str):
    staged = staged_chapters(tok)
    for pid in staged:
        stamp_chapter(tok, pid, work_dir(tok) / "chapters" / f"{pid}.md")
    staged = staged_chapters(tok)
    for pid, txt in staged.items():
        before = work_dir(tok) / "before" / f"{pid}.md"
        if not before.exists() and read(CHAP / f"{pid}.md") != txt:
            write(before, read(CHAP / f"{pid}.md"))
        write(CHAP / f"{pid}.md", txt)
    if staged:
        write(HIST / ".last_work", tok + "\n")
        print(f"Promoted chapters {', '.join(staged)} to history/chapters/")


def report(errors, warnings, audit):
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
    if audit:
        print(f"\n{audit}")


def cmd_check(a):
    tok = a.work
    errors, warnings, audit, _ = check_part(tok, a.part)
    report(errors, warnings, audit)
    sys.exit(1 if errors else 0)


def cmd_finish(a):
    tok, part = a.work, a.part
    m = manifest(tok)
    if part == 3:
        for pid in staged_chapters(tok):
            stamp_chapter(tok, pid, work_dir(tok) / "chapters" / f"{pid}.md")
    errors, warnings, audit, _ = check_part(tok, part)
    report(errors, warnings, audit)
    if errors:
        print("\nNot finished: fix the errors and run finish again.")
        sys.exit(1)
    d = work_dir(tok)
    insert_audit(d / f"part{part}.md", audit)
    if part == 3:
        promote(tok)
        append_registers(read(d / "part3.md"), tok, m.get("title", ""))
        append_study_entries(read(d / "part3.md"), tok, m.get("title", ""))
    elif part == 2:
        append_registers(read(d / "part2.md"), tok, m.get("title", ""))
    else:
        append_registers(read(d / "part1.md"), tok, m.get("title", ""))
    set_manifest_field(tok, "status", '"' + {1: "part1", 2: "part2", 3: "complete"}[part] + '"')
    if part < 3:
        nxt = d / f"part{part + 1}.md"
        if not nxt.exists():
            phase_secs = "\n\n".join(f"## §4.{p['id']} {phase_heading(p)}" for p in phases())
            write(nxt, read(ROOT / "templates" / f"part{part + 1}.md").replace("NNN", tok).replace("PHASE_SECTIONS", phase_secs))
            print(f"Created {rel(nxt)} from the template")
    build_all(quiet=True)
    print(f"\nFinished Part {part} of memo {tok}.")
    if getattr(a, "push", False):
        git_commit_push(f"Memo {tok} Part {part}: {m.get('title', '')}")
    print(f"Send the user: build/memos/{tok}/Part-{part}.md" + (f" · build/memos/{tok}/CHANGES.md · build/WAR-HISTORY.md · history/TRAJECTORY-LOG.md" if part == 3 else ""))
    if part == 1 and matching_studies(set(memo_vars(m)[0]) | memo_vars(m)[1]):
        print("Studies on this memorandum's variables: " + ", ".join(matching_studies(set(memo_vars(m)[0]) | memo_vars(m)[1])) + " — Part 2 judges against them")
    if not getattr(a, "push", False):
        print(f"Then: git add -A && git commit -m \"Memo {tok} Part {part}\" && git push origin main")


# ----------------------------------------------------------------------------- baseline and reviews

def cmd_baseline(a):
    if a.init:
        vec = "\n".join(f'"{v}" = {{ dlow = 0, dhigh = 0, conf = "high", note = "the historical state" }}' for v in vector_keys())
        for p in phases():
            path = CHAP / f"{p['id']}.md"
            if path.exists():
                print(f"{rel(path)} exists (kept)")
                continue
            dates = f"{fmt_ym(p['start'])} – {fmt_ym(p['end'])}"
            t = read(ROOT / "templates" / "chapter.md")
            t = (t.replace("PID", p["id"]).replace("PTITLE", p["title"]).replace("PDATES", dates)
                 .replace("VECTOR", vec + (f"\n\n[snapshot]\n{vec}" if p.get("snapshot") else ""))
                 .replace("PHEADING", phase_heading(p)))
            write(path, t)
            print(f"Created {rel(path)}")
        return
    errors, warnings = [], []
    ids = all_events()
    for p in phases():
        path = CHAP / f"{p['id']}.md"
        txt = read(path)
        if not txt:
            errors.append(f"{rel(path)} missing")
            continue
        check_chapter(txt, p["id"], errors, warnings, rel(path), ids)
        fm, _, body = parse_chapter(txt)
        evs = parse_events(body)
        if len(evs) < 6:
            warnings.append(f"{rel(path)}: only {len(evs)} events")
        for e in evs:
            if e.get("ok") and (e["origin"] != "HIST" or not e["id"].startswith("EV000-")):
                errors.append(f"{rel(path)}: baseline event {e['id']} must be EV000-n with origin HIST")
        if any(form(v) != ("dlow", "dhigh") and rng(v) is not None or (form(v) == ("dlow", "dhigh") and rng(v) != (0, 0))
               for v in fm.get("end_vector", {}).values()):
            errors.append(f"{rel(path)}: baseline end_vector must be all zeros (it is the historical state)")
        if words(body) < 600:
            warnings.append(f"{rel(path)}: {words(body)} words — thin for a baseline chapter")
    report(errors, warnings, "")
    if errors:
        sys.exit(1)
    for p in phases():
        path = CHAP / f"{p['id']}.md"
        txt = read(path)
        fm, fm_raw, body = parse_chapter(txt)

        def fix(m):
            fields = m.group(2).split(" · ")
            fields[-1] = "000"
            return f"## {m.group(1)} · " + " · ".join(fields)
        write(path, f"+++\n{fm_raw}\n+++\n{EVENT_HDR.sub(fix, body)}")
    write(HIST / ".last_work", "000\n")
    build_all(quiet=True)
    if getattr(a, "push", False):
        git_commit_push("Baseline finished")
    print("Baseline finished. Send the user build/WAR-HISTORY.md, then: git add -A && git commit -m \"Baseline\" && git push origin main")


def cmd_review(a):
    tok = a.work
    d = work_dir(tok)
    kind = "TNA" if tok == "TNA" else tok[:2]
    if a.init:
        if d.exists() and (d / "review.toml").exists():
            print(f"{rel(d)} exists (kept)")
        else:
            done = [t for t, _ in manifests(("complete",))]
            write(d / "review.toml", f'work = "{tok}"\nkind = "{kind}"\nstatus = "open"\nafter_memo = "{done[-1] if done else "000"}"\n')
            for i in (1, 2) if kind in ("CP", "MT") else (1,):
                write(d / f"part{i}.md", f"<!-- {tok} part {i} -->\n# {tok} — Part {i}\n")
            print(f"Opened {rel(d)}/")
        return
    errors, warnings = [], []
    texts = {p.name: read(p) for p in sorted(d.glob("part*.md"))}
    if not texts or not all(t.strip() for t in texts.values()):
        errors.append(f"{rel(d)}: part files missing or empty")
    staged = staged_chapters(tok)
    ids = all_events(staged)
    for pid, txt in staged.items():
        stamp_chapter(tok, pid, d / "chapters" / f"{pid}.md")
        check_chapter(read(d / "chapters" / f"{pid}.md"), pid, errors, warnings, f"chapter {pid} (staged)", ids)
        old_ids = {e["id"] for e in parse_events(parse_chapter(read(CHAP / f"{pid}.md"))[2])}
        new_ids = {e["id"] for e in parse_events(parse_chapter(read(d / "chapters" / f"{pid}.md"))[2])}
        for gone in sorted(old_ids - new_ids):
            errors.append(f"chapter {pid}: event {gone} was deleted — mark it CANCELLED instead")
    for n, t in texts.items():
        check_tags(t, errors, f"{tok}/{n}")
        check_register_blocks(t, tok, errors)
        check_study_blocks(t, tok, f"{tok}/{n}", errors, [])
    sdir = d / "studies"
    for sp_ in sorted(sdir.glob("*.md")) if sdir.exists() else []:
        check_study(read(sp_), sp_.stem, f"study {sp_.stem} (staged)", errors, warnings, folding=True)
        fm_s = parse_chapter(read(sp_))[0]
        if fm_s.get("folded") != tok:
            errors.append(f"study {sp_.stem} (staged): folded = '{fm_s.get('folded')}', expected '{tok}'")
        old_fm, _, old_b = parse_chapter(study_text(sp_.stem))
        kept = {(k_, p_) for p_, t_ in (fm_s.get("values") or {}).items() if isinstance(t_, dict) for k_ in t_}
        for _, txt_ in since_entries(old_b):
            for k_, p_, _v in value_lines(txt_):
                if (k_, p_) not in kept:
                    warnings.append(f"study {sp_.stem} (staged): the since-entry value for {k_} in {p_} is not in the folded [values] — carry it or say in '## Judgments' why it was dropped")
    es = load_toml(HIST / "endstate.toml")
    if es.get("last_changed") == tok and not any(h.get("by") == tok for h in es.get("history", [])):
        errors.append(f"endstate.toml: last_changed is {tok} but no [[history]] entry for it")
    if es.get("last_changed") == tok:
        check_rung("\n".join(texts.values()), f"{tok} (it changes the end state)", errors)
    report(errors, warnings, "")
    if errors:
        sys.exit(1)
    promote(tok)
    promote_studies(tok)
    title = {"TNA": "Theater Needs Assessment", "CP": "Checkpoint", "MT": "Meta-checkpoint"}.get(kind, "Revision")
    for n, t in texts.items():
        append_registers(t, tok, title)
        append_study_entries(t, tok, title)
    rt = read(d / "review.toml") if (d / "review.toml").exists() else f'work = "{tok}"\nkind = "{kind}"\nstatus = "open"\nafter_memo = "000"\n'
    write(d / "review.toml", re.sub(r'^status\s*=.*$', 'status = "complete"', rt, flags=re.M))
    build_all(quiet=True)
    if getattr(a, "push", False):
        git_commit_push(f"{tok} finished")
    print(f"\n{tok} finished. Send the user its reading copy in build/reviews/{tok}/; then git add -A && git commit -m \"{tok}\" && git push origin main")


# ----------------------------------------------------------------------------- build

def demote(s: str, n: int) -> str:
    return re.sub(r"^(#{1,6}) ", lambda m: "#" * min(6, len(m.group(1)) + n) + " ", s, flags=re.M)


def mark_events(body: str, token: str) -> str:
    def f(m):
        fields = m.group(2).split(" · ")
        works = [w.strip() for w in fields[-1].split(",")] if len(fields) >= 5 else []
        return f"## ◆ {m.group(1)} · {m.group(2)}" if token in works else m.group(0)
    return EVENT_HDR.sub(f, body)


def vector_line(fm: dict) -> str:
    v = fm.get("end_vector", {})
    def differs(val):
        r = rng(val)
        if r is None:
            return False
        if form(val) is None or (form(val)[0] == "low" and "hist" not in val):
            return r != (0, 0)
        if form(val)[0] == "low":
            return "hist" not in val or r != (val["hist"], val["hist"])
        return r != (0, 0)
    moved = [f"{k} {fmt_val(val)}" for k, val in v.items() if differs(val)]
    return "*End of phase against the historical state: " + (" · ".join(moved) if moved else "as historical on every headline variable") + ".*"


def build_card(tok: str, m: dict, short: bool = False) -> str:
    """short: the pack's fallback when the full card will not fit — denies, verdict, pushes, findings, concepts."""
    p1, p2 = read(work_dir(tok) / "part1.md"), read(work_dir(tok) / "part2.md")
    cb1, cb2 = card_blocks(p1), card_blocks(p2)
    out = [f"# Card {tok} — {m.get('title')}",
           f"*Memorandum {tok} · status {m.get('status')} · full record: memos/{tok}/ · generated by fie.py*"]
    for p in m.get("provision", []):
        pid = p.get("id")
        out.append(f"## {pid} · {p.get('designation')}\n{p.get('quantity')} · spaces {p.get('ceiling_spaces')} · "
                   f"arrives {p.get('arrival')} · {', '.join(p.get('systems', []))} · {p.get('category')}")
        for k, lab in [x for x in [("figures", "Key figures"), ("negative", "Negative specification"), ("denies", "Denies the enemy"), ("verdict", "Verdict")]
                       if not (short and x[0] in ("figures", "negative"))]:
            b = [x for kk, pp, x in cb1 if kk == k and pp == pid]
            if b and b[0]:
                out.append(f"**{lab}.** {b[0]}" if k != "figures" else f"**{lab}.**\n{b[0]}")
        pushes = [f"{x['var']} {fmt_push(x)}" for x in m.get("push", []) if x.get("provision") == pid]
        deps = [x["var"] for x in m.get("depend", []) if x.get("provision") == pid]
        out.append(f"**Pushes:** {', '.join(pushes) or '-'} · **Depends on:** {', '.join(deps) or '-'}")
    for k, lab in [("findings", "Findings"), ("concepts", "Employment concepts"), ("interactions", "Interactions")]:
        b = [x for kk, _, x in cb2 if kk == k and x]
        if b:
            out.append(f"## {lab}\n{b[0]}")
    s = re.sub(r"\[S(\d+)\]", lambda mm: f"[M{tok}·S{mm.group(1)}]", "\n\n".join(out) + "\n")
    if short:
        return s.replace(f"# Card {tok} —", f"# Card {tok} (short: key figures and negative specifications omitted; full card in build/cards/) —", 1)
    lims = config()["limits"]
    lim = lims["card_chars_base"] + lims["card_chars_per_provision"] * len(m.get("provision", []))
    if len(s) > lim:
        print(f"WARNING: card {tok} is {len(s):,} characters, over the {lim:,} limit — tighten the card blocks in memo {tok}")
    return s


def reading_copy_part(tok: str, part: int) -> str:
    s = read(work_dir(tok) / f"part{part}.md")
    if part == 3:
        def inc(mm):
            pid = mm.group(1)
            txt = read(work_dir(tok) / "chapters" / f"{pid}.md")
            fm, _, body = parse_chapter(txt)
            body = re.sub(r"^# .*\n", "", body, count=1)
            body = mark_events(body, tok)
            return "### Chronicle\n\n" + vector_line(fm) + "\n\n" + demote(body, 2).strip() + "\n"
        s = re.sub(r"<!--\s*chapter (P\d+)\s*-->", inc, s)
    labels = {"log": "### Trajectory Log entry", "positions": "### Positions recorded", "persons": "### Persons recorded",
              "directives": "### Directives issued", "gaps": "### Gap register entries", "swept": "### Variables swept"}
    for name, lab in labels.items():
        s = re.sub(r"<!--\s*" + name + r"\s*-->(.*?)<!--\s*/" + name + r"\s*-->",
                   lambda mm, lab=lab: (lab + "\n\n" + mm.group(1).strip() + "\n") if mm.group(1).strip() else "", s, flags=re.S)
    card_labels = {"figures": "**Key figures — {pid}**", "interactions": "**Interactions with earlier provisions**",
                   "concepts": "**Employment concepts**"}

    def card(mm):
        kind, pid, body = mm.group(1), mm.group(2) or "", mm.group(3).strip()
        if not body:
            return ""
        lab = card_labels.get(kind)
        return (lab.format(pid=pid) + "\n\n" + body + "\n") if lab else body + "\n"
    s = re.sub(r"<!--\s*card:(\w+)(?:\s+(P\d{3}[a-z]))?\s*-->(.*?)<!--\s*/card\s*-->", card, s, flags=re.S)
    return strip_comments(s).strip() + "\n"


# ----------------------------------------------------------------------------- reader copies

SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
ORIGIN_WORDS = {"HIST": "historical", "HIST-ALT": "changed from history", "CANCELLED": "no longer happens",
                "NEW": "new", "FREE": "free play"}
REF_GROUP = re.compile(r"\s?\((?:see\s)?(?:(?:F\d{3}-\d+|G-\d+|POS\w+-\d+|REV\w+-\d+|DIR\w+-\d+|EV" + WORK_RE +
                       r"-\d+|C\d{3}-\d+|EC\d{3}-\d+|P\d{3}[a-z]|M-\d+|A\d{1,2}a?|G\d)(?:,\s*|;\s*|\s+and\s+)?)+\)")


def source_lines(path: Path) -> dict[int, str]:
    out = {}
    for m in re.finditer(r"^\[S(\d+)\]\s+(.+)$", read(path), flags=re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def for_reader(text: str, memo_sources: dict[int, str] | None = None) -> str:
    """The reading copy: same words, less apparatus. Provenance tags become numbered notes at the end, bare
    cross-reference IDs in parentheses are dropped, event headers become titles with a quiet line beneath.
    The record itself is untouched."""
    base = source_lines(HIST / "baseline-sources.md")
    memo_sources = memo_sources or {}
    notes, order = {}, []

    def note_for(inner: str) -> str | None:
        if inner in ("H", "D"):
            return None
        if inner == "U":
            return "Stipulated in the provision."
        if re.fullmatch(r"H\d+", inner):
            return "Source: " + base.get(int(inner[1:]), f"baseline source {inner[1:]}")
        if re.fullmatch(r"S\d+", inner):
            return "Source: " + memo_sources.get(int(inner[1:]), f"source {inner[1:]}")
        if inner.startswith("E:"):
            return "Estimate — " + inner[2:].strip()
        if inner.startswith("X-"):
            return f"The exercise's own judgment ({'memo ' + inner[2:] if inner[2:].isdigit() else inner[2:]}), not a measured figure."
        if re.fullmatch(r"M\d{3}(?:·S\d+)?", inner):
            return f"From memorandum {inner[1:4]}'s record."
        return None

    def number(n: str) -> str:
        if n not in notes:
            order.append(n)
            notes[n] = len(order)
        return str(notes[n]).translate(SUPERSCRIPT)

    out_paras = []
    for para in re.split(r"(\n\s*\n)", text):
        if not para.strip() or para.startswith("```"):
            out_paras.append(para)
            continue
        tags = list(TAG_RE.finditer(para))
        last = {}
        for m in tags:
            last[m.group(1)] = m.start()

        def tag(m):
            n = note_for(m.group(1))
            if n is None or last.get(m.group(1)) != m.start():
                return ""
            return number(n)
        para = TAG_RE.sub(tag, para)
        para = re.sub(r"[ \t]+([¹²³⁴⁵⁶⁷⁸⁹⁰.,;:)])", r"\1", para)
        para = re.sub(r"[ \t]{2,}", " ", para)
        para = REF_GROUP.sub("", para)
        para = re.sub(r"^\*\*(F\d{3}-\d+)\*\*\s+\*\*", r"**\1 · ", para)
        para = re.sub(r"^(\*\*F\d{3}-\d+)(?: · ([^*]+))?\*\*\s*\([A-Z, ]+\)\s*", lambda mm: mm.group(1) + (" · " + mm.group(2) if mm.group(2) else "") + "** ", para)

        def hdr(mm):
            hashes, mark, eid, rest = mm.group(1), mm.group(2) or "", mm.group(3), mm.group(4)
            f = rest.split(" · ")
            if len(f) < 5:
                return mm.group(0)
            title, date, place, origin = " · ".join(f[:-4]), f[-4], f[-3], f[-2]
            return f"{hashes} {mark}{title}\n*{date} · {place} · {ORIGIN_WORDS.get(origin, origin)} · {eid}*"
        para = re.sub(r"^(#{2,6}) (◆ )?(EV" + WORK_RE + r"-\d+) · (.+)$", hdr, para, flags=re.M)
        out_paras.append(para)
    body = "".join(out_paras)
    audit = re.search(r"^\*Audit — .*\*$\n?", body, re.M)
    if audit:
        body = body.replace(audit.group(0), "", 1).rstrip() + "\n\n---\n\n" + audit.group(0).strip() + "\n"
    if order:
        body = body.rstrip() + "\n\n## Notes\n\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(order, 1)) + "\n"
    return body


INITIATIVE_RE = re.compile(r"^\s*\*Initiative:\s*(enemy|allied|both|neither)\*", re.I)


def initiative(ev: dict) -> str | None:
    first = next((l for l in ev.get("body", "").splitlines() if l.strip()), "")
    m = INITIATIVE_RE.match(first)
    return m.group(1).lower() if m else None


def first_sentences(text: str, n: int = 2) -> str:
    t = " ".join(l.strip() for l in text.splitlines() if l.strip() and not INITIATIVE_RE.match(l) and not l.startswith("#"))
    parts = re.split(r"(?<=[.!?])\s+", strip_comments(t))
    return " ".join(parts[:n])[:600]


def build_enemy() -> str:
    rows, counts = [], {}
    for p in phases():
        _, _, body = parse_chapter(read(CHAP / f"{p['id']}.md"))
        c = counts.setdefault(p["id"], {"enemy": 0, "allied": 0, "both": 0, "neither": 0, "untagged": 0})
        for e in parse_events(body):
            if not e.get("ok"):
                continue
            ini = initiative(e)
            c[ini or "untagged"] += 1
            if ini in ("enemy", "both") and e.get("origin") != "CANCELLED":
                rows.append(f"### {e['title']}\n*{e['date']} · {e['place']} · {p['id']} · {ORIGIN_WORDS.get(e['origin'], e['origin'])} · {e['id']}*\n\n{first_sentences(e['body'])}")
    table = "| Phase | Enemy | Allied | Both | Neither | Untagged |\n|---|---|---|---|---|---|\n" + "\n".join(
        f"| {k} | {v['enemy']} | {v['allied']} | {v['both']} | {v['neither']} | {v['untagged']} |" for k, v in counts.items())
    pos = [l for l in register_lines("positions.md") if re.search(r"HANOI\.|ENEMY\.|PAVN\.|VC\.|VCI\.", l)]
    return ("# The enemy's war — Hanoi's decisions in sequence\n\n*Generated by fie.py from history/chapters: every event where the enemy held the initiative, "
            "in order, so his campaign can be read as one campaign. Events are tagged by their first line, `*Initiative: enemy | allied | both | neither*`.*\n\n"
            "## Who held the initiative, by phase\n\n" + table + "\n\n## The enemy's decisions\n\n" + ("\n\n".join(rows) or "No events tagged yet.")
            + "\n\n## Settled positions about the enemy\n\n" + ("\n".join(pos) or "None.") + "\n")


def build_changes(tok: str) -> str | None:
    """Before and after for every chapter passage this work changed, from its before/ snapshots and its chapters."""
    d = work_dir(tok)
    after_dir, before_dir = d / "chapters", d / "before"
    if not after_dir.exists():
        return None
    label = f"Memo {tok}" if re.fullmatch(r"\d{3}", tok) else tok
    out = [f"# What changed in the war — {label}", "*Generated by fie.py from this work's chapters and the chapters as they stood before it. "
           "New and changed events are given in full; the earlier text follows as a quotation.*"]
    es = load_toml(HIST / "endstate.toml")
    hist = es.get("history", [])
    for i, h in enumerate(hist):
        if h.get("by") == tok:
            prev = hist[i - 1].get("rung") if i else "?"
            out.append(f"## The end state\n\nRung ({prev}) → ({h.get('rung')}). {h.get('reason', '')}")
    vrows = []
    for pa in sorted(after_dir.glob("P*.md")):
        pid = pa.stem
        bt = read(before_dir / f"{pid}.md")
        if not bt:
            continue
        bfm, _, bb = parse_chapter(bt)
        afm, _, ab = parse_chapter(read(pa))
        for sec in ("end_vector", "snapshot"):
            for k, v in (afm.get(sec) or {}).items():
                ov = (bfm.get(sec) or {}).get(k)
                if v != ov:
                    vrows.append(f"| {pid}{' (snapshot)' if sec == 'snapshot' else ''} | {k} | {fmt_val(ov)} → {fmt_val(v)} |")
    if vrows:
        out.append("## Headline variables at each phase's end\n\n| Phase | Variable | Before → after |\n|---|---|---|\n" + "\n".join(vrows))
    for pa in sorted(after_dir.glob("P*.md")):
        pid = pa.stem
        bt = read(before_dir / f"{pid}.md")
        if not bt:
            continue
        _, _, bb = parse_chapter(bt)
        _, _, ab = parse_chapter(read(pa))
        old = {e["id"]: e for e in parse_events(bb)}
        sec = []
        for name in ["Overview", "How the phase ends"]:
            def part(body, nm):
                if nm == "Overview":
                    t = re.search(r"^# .+$", body, re.M)
                    f = re.search(r"^## ", body[t.end():], re.M) if t else None
                    return body[t.end():t.end() + f.start()].strip() if t and f else ""
                return (section(body, 2, "How the phase ends") or "").strip()
            o, n = part(bb, name), part(ab, name)
            if o != n:
                sec.append(f"### {name} (changed)\n\n{n}\n\n" + "\n".join("> " + l for l in o.splitlines()))
        for e in parse_events(ab):
            if not e.get("ok") or tok not in e.get("works", []):
                continue
            o = old.get(e["id"])
            kind = {"NEW": "New", "FREE": "New — free play", "CANCELLED": "No longer happens"}.get(e["origin"], "Changed")
            if o is None and kind == "Changed":
                kind = "New"
            text = e["body"].strip()
            block = f"### {kind}: {e['title']}\n*{e['date']} · {e['place']} · {e['id']}*\n\n{text}"
            if o is not None and event_key_text(o) != event_key_text(e):
                block += "\n\n**Before:**\n\n" + "\n".join("> " + l for l in o["body"].strip().splitlines())
            sec.append(block)
        if sec:
            title = re.search(r"^# (.+)$", ab, re.M)
            out.append(f"## {title.group(1) if title else pid}\n\n" + "\n\n".join(sec))
    return "\n\n".join(out) + "\n" if len(out) > 2 else None


def build_all(quiet: bool = False):
    BUILD.mkdir(exist_ok=True)
    say = (lambda *_: None) if quiet else print
    # index
    idx = ["# Provision index", "*Generated by fie.py from the manifests. Do not edit.*", ""] + (provision_index_lines() or ["None yet."])
    write(BUILD / "INDEX.md", "\n".join(idx) + "\n")
    # cards
    for t, m in manifests(("part1", "part2", "complete")):
        write(BUILD / "cards" / f"CARD-{t}.md", build_card(t, m))
    # ledgers
    led = ["# Variable ledgers", "*Generated by fie.py from the manifests. Do not edit.*"]
    vmap = {v["id"]: v for v in variables()}
    for vid in vmap:
        ls = ledger_lines(vid)
        if ls:
            led.append(f"## {vid} — {vmap[vid]['name']}\n*Higher means {vmap[vid]['higher']}.*\n\n" + "\n".join(ls))
    write(BUILD / "LEDGERS.md", "\n\n".join(led) + "\n")
    # events
    rows = ["# Event index", "*Generated by fie.py from history/chapters. Do not edit.*", "",
            "| Event | Phase | Date | Title | Place | Origin | Works |", "|---|---|---|---|---|---|---|"]
    for p in phases(include_retired=True):
        _, _, body = parse_chapter(read(CHAP / f"{p['id']}.md"))
        for e in parse_events(body):
            if e.get("ok"):
                rows.append(f"| {e['id']} | {p['id']} | {e['date']} | {e['title']} | {e['place']} | {e['origin']} | {','.join(e['works'])} |")
    write(BUILD / "EVENTS.md", "\n".join(rows) + "\n")
    # war history
    last = read(HIST / ".last_work").strip() or "000"
    es = load_toml(HIST / "endstate.toml")
    label = "the historical baseline" if last == "000" else (f"Memo {last}" if re.fullmatch(r"\d{3}", last) else last)
    wh = [f"# The War — as it stands after {label}",
          f"*Generated by fie.py from history/chapters. ◆ marks events created or changed in {label}.*",
          f"## End state\n\n**Rung ({es.get('rung')}) — {es.get('rung_label')}.**"
          + (f" Off the ladder: {es.get('off_ladder')}." if es.get("off_ladder") else "") + f" {es.get('summary')}\n\n"
          f"Saigon falls: {es.get('saigon_falls')}{' (' + es.get('saigon_falls_date') + ')' if es.get('saigon_falls_date') else ''} · "
          f"US combat forces: {es.get('us_combat_forces')} · Hanoi: {es.get('hanoi_posture')}",
          "| Phase | Title | Dates | Last revised | Events |\n|---|---|---|---|---|"]
    chap_txt = []
    for p in phases():
        fm, _, body = parse_chapter(read(CHAP / f"{p['id']}.md"))
        wh[-1] += f"\n| {p['id']} | {p['title']} | {fmt_ym(p['start'])} – {fmt_ym(p['end'])} | {fm.get('last_revised', '-')} | {len(parse_events(body))} |"
        if body.strip():
            b = mark_events(body, last)
            b = re.sub(r"^(# .*\n)", lambda mm: mm.group(1) + "\n" + vector_line(fm) + "\n", b, count=1)
            chap_txt.append(b.strip())
    write(BUILD / "WAR-HISTORY.md", for_reader("\n\n".join(wh) + "\n\n---\n\n" + "\n\n---\n\n".join(chap_txt) + "\n"))
    # reading copies
    for t in memo_tokens():
        m = load_toml(work_dir(t) / "manifest.toml")
        done_parts = {"open": 0, "part1": 1, "part2": 2, "complete": 3}.get(m.get("status"), 0)
        parts = []
        for i in range(1, done_parts + 1):
            rc = for_reader(reading_copy_part(t, i), source_lines(work_dir(t) / "sources.md"))
            write(BUILD / "memos" / t / f"Part-{i}.md", rc)
            parts.append(rc)
        if done_parts == 3:
            head = f"# Memorandum {t} — {m.get('title')}\n\n*COMUSMACV to CINCPAC · received {m.get('received')} · three parts*\n\n"
            whole = "\n\n---\n\n".join(reading_copy_part(t, i) for i in (1, 2, 3))
            write(BUILD / "memos" / t / f"MEMO-{t}.md", head + for_reader(whole, source_lines(work_dir(t) / "sources.md")))
    for d in sorted((ROOT / "reviews").glob("*")) + sorted((ROOT / "revisions").glob("*")):
        if d.is_dir():
            for p in sorted(d.glob("part*.md")):
                write(BUILD / "reviews" / d.name / p.name, for_reader(strip_comments(read(p)).strip() + "\n", source_lines(d / "sources.md")))
    write(BUILD / "ENEMY.md", for_reader(build_enemy()))
    idx_s = ["# Studies", "*Generated by fie.py from studies/. Each study is a deep account of one area of the war as the record stands; "
             "memoranda append dated since-entries and checkpoints fold them in. Do not edit.*", ""] + (study_index_lines() or ["None yet."])
    write(BUILD / "STUDIES.md", "\n".join(idx_s) + "\n")
    for s_ in study_slugs():
        txt_s = study_text(s_)
        fm_s, _, b_s = parse_chapter(txt_s)
        rc = study_render(s_, txt_s).replace("## Study: ", "# Study: ", 1)
        rc = re.sub(r"^### ", "## ", rc, flags=re.M)
        if fm_s.get("audit"):
            rc = rc.rstrip() + "\n\n---\n\n*" + str(fm_s["audit"]) + "*\n"
        write(BUILD / "studies" / f"{s_}.md", for_reader(rc, study_sources(b_s)))
    menus = read(HIST / "menus.md")
    if menus:
        last = re.split(r"(?=^## )", menus, flags=re.M)[-1]
        write(BUILD / "MENU.md", "# Next provisions — the latest menu\n\n*From the latest review's bill. Generated by fie.py.*\n\n" + last.replace("## ", "## From ", 1))
    for base in [ROOT / "memos", ROOT / "reviews", ROOT / "revisions"]:
        for d in sorted(base.glob("*")) if base.exists() else []:
            if d.is_dir():
                ch = build_changes(d.name)
                if ch:
                    dest = BUILD / ("memos" if base.name == "memos" else "reviews") / d.name / "CHANGES.md"
                    write(dest, for_reader(ch, source_lines(d / "sources.md")))
    say("Built: build/INDEX.md, build/cards/, build/LEDGERS.md, build/EVENTS.md, build/WAR-HISTORY.md, build/memos/, build/reviews/")


def cmd_build(_):
    build_all()


def cmd_grep(a):
    terms = [t.lower() for t in a.words]
    files = sorted(list((ROOT / "memos").rglob("*.md")) + list(HIST.rglob("*.md")) + list((ROOT / "reviews").rglob("*.md"))
                   + list((ROOT / "revisions").rglob("*.md")) + list((ROOT / "errata").glob("*.md")) + list(STUDIES.glob("*.md")))
    hits = 0
    for f in files:
        for i, line in enumerate(read(f).splitlines(), 1):
            low = line.lower()
            if all(t in low for t in terms):
                print(f"{rel(f)}:{i}: {line.strip()[:220]}")
                hits += 1
                if hits >= a.max:
                    print(f"… stopped at {a.max} hits; narrow the search")
                    return
    if not hits:
        print("No hits.")


# ----------------------------------------------------------------------------- main

def main():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet when piped into head
    ap = argparse.ArgumentParser(prog="fie.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status").set_defaults(f=cmd_status)
    sp.add_parser("new").set_defaults(f=cmd_new)
    p = sp.add_parser("pack")
    p.add_argument("work")
    p.add_argument("--part", type=int, default=0)
    p.set_defaults(f=cmd_pack)
    p = sp.add_parser("chapters")
    p.add_argument("work")
    p.add_argument("phases", nargs="*")
    p.add_argument("--drop", nargs="*")
    p.set_defaults(f=cmd_chapters)
    for name, fn in [("check", cmd_check), ("finish", cmd_finish)]:
        p = sp.add_parser(name)
        p.add_argument("work")
        p.add_argument("--part", type=int, required=True)
        p.add_argument("--push", action="store_true", help="after a clean finish, commit and push to main")
        p.set_defaults(f=fn)
    p = sp.add_parser("boot")
    p.add_argument("command", help="provision | continue | baseline | tna | checkpoint | meta | veto | erratum | study")
    p.set_defaults(f=cmd_boot)
    p = sp.add_parser("baseline")
    p.add_argument("--push", action="store_true")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--init", action="store_true")
    g.add_argument("--finish", action="store_true")
    p.set_defaults(f=cmd_baseline)
    p = sp.add_parser("review")
    p.add_argument("--push", action="store_true")
    p.add_argument("work")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--init", action="store_true")
    g.add_argument("--finish", action="store_true")
    p.set_defaults(f=cmd_review)
    sp.add_parser("build").set_defaults(f=cmd_build)
    p = sp.add_parser("amend")
    p.add_argument("work")
    p.add_argument("file")
    p.set_defaults(f=cmd_amend)
    p = sp.add_parser("study")
    p.add_argument("target", nargs="?", default="", help="STnn, or 'fold'")
    p.add_argument("args", nargs="*")
    p.add_argument("--init", action="store_true")
    p.add_argument("--finish", action="store_true")
    p.add_argument("--part", type=int, default=0)
    p.add_argument("--push", action="store_true")
    p.set_defaults(f=cmd_study)
    p = sp.add_parser("grep")
    p.add_argument("words", nargs="+")
    p.add_argument("--max", type=int, default=60)
    p.set_defaults(f=cmd_grep)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
