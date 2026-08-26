#!/usr/bin/env python3
"""
REGISTRAR · gates · divergence
─────────────────────────────────────────────────────────────────────────────
**Every patch row exists three times, and nothing was checking that they agree.**

    what it SAYS        `value`       — what the fit claims to be
    what it CITES       `evidence`    — the sources offered for it
    what HAPPENED       `shadow_run`  — the replay against the site's history

The twelve existing gates check each layer *separately*. Evidence binding
confirms a source exists and says something. Shadow run confirms a denominator
exists. **Nothing catches a row whose value says 90, whose evidence says 240,
and whose replay tested a third thing.**

That row passes today, and it will keep passing, because **the three fields are
formatted as one story and a reviewer reads them as one.** The disagreements are
exactly what formatting hides.

WHY THIS IS A GATE AND NOT A REVIEW ITEM

A human reading a finished patch sees rows. The divergence is invisible unless
you hold three fields side by side and do arithmetic — which is precisely the
thing a machine is better at and a tired reviewer is worst at.

WHAT IT REFUSES, AND WHAT IT DELIBERATELY DOES NOT

It does **not** demand a value appear verbatim in its evidence. A row can
legitimately state a figure the sources do not contain literally — a p75
computed from a distribution, a threshold rounded to a usable number. **It
demands derivability with a stated method.** A row may declare `derived_from`
naming the computation, and that satisfies the check.

The risk is that `derived_from` becomes a rubber stamp. It is watched: a
declaration that names no method is refused, and **if the field turns into a
formality the funeral prints and this gate is rewritten or deleted.** `[BET]`

Zero dependencies.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"

# A number, with optional unit, as it appears in prose.
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|h|hrs?|%|percent)?", re.I)

# "6h04m", "4 hours", "90 minutes" — normalise to minutes where a unit is given.
TO_MIN = {"minute": 1, "minutes": 1, "min": 1, "mins": 1,
          "hour": 60, "hours": 60, "h": 60, "hr": 60, "hrs": 60}

# Evidence is PROSE, and prose says "four hours" far more often than "240
# minutes". Reading only digits made a correct row look divergent.
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12,
            "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
            "forty-five": 45, "sixty": 60, "ninety": 90}


def _minutes(unit: str) -> int:
    """Minutes per unit, tolerant of plurals and trailing punctuation."""
    u = (unit or "").strip().lower().rstrip(".").rstrip("s")
    return TO_MIN.get(u, TO_MIN.get(u + "s", 0))


def numbers_in(text: str) -> set[float]:
    """
    Every number a piece of prose states, plus its minute-equivalent.

    **Evidence is prose**, and prose says "four hours" far more often than
    "240 minutes". Reading only digits made a correct row look divergent —
    found on the worked example, where a draft row asserted 240 while citing a
    source that said *four hours*. Same figure, two notations.
    """
    text = text or ""
    out: set[float] = set()

    # digits, with an optional unit
    for m in NUM.finditer(text):
        try:
            v = float(m.group(1))
        except ValueError:
            continue
        out.add(v)
        mins = _minutes(m.group(2) or "")
        if mins:
            out.add(v * mins)

    # composite durations: 6h04m -> 364
    for m in re.finditer(r"(\d+)\s*h(?:ours?)?\s*(\d{1,2})\s*m", text, re.I):
        out.add(float(m.group(1)) * 60 + float(m.group(2)))

    # spelled-out quantities: "four hours" -> 4 and 240
    for m in re.finditer(r"\b([a-z]+(?:-[a-z]+)?)\s+(minutes?|mins?|hours?|hrs?)\b",
                         text, re.I):
        n = WORD_NUM.get(m.group(1).lower())
        if n is None:
            continue
        out.add(float(n))
        mins = _minutes(m.group(2))
        if mins:
            out.add(float(n) * mins)

    return out


# Keys whose values are IDENTIFIERS or CLOCK TIMES, not quantities. A hospital
# number is not a measurement, and demanding evidence for it is the gate being
# wrong rather than the row. Found on the first run against the worked example.
NOT_A_QUANTITY = re.compile(
    r"(^|_)(id|code|number|hospital|site|facility|npi|mrn|account|version|"
    r"opens|closes|window|at|time|start|end)($|_)", re.I)


def numbers_of(value, key: str = "") -> set[float]:
    """
    Every number a row's value ASSERTS, at any depth.

    An identifier is not an assertion. `hospital: "1147"` claims nothing that
    evidence could corroborate, and a clock time like "06:00" is a boundary the
    evidence states in its own notation rather than as a quantity.
    """
    out: set[float] = set()
    if key and NOT_A_QUANTITY.search(key):
        return out
    if isinstance(value, bool):
        return out
    if isinstance(value, (int, float)):
        out.add(float(value))
    elif isinstance(value, str):
        if not re.fullmatch(r"\s*\d+\s*", value):
            out |= numbers_in(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            out |= numbers_of(v, k)
    elif isinstance(value, list):
        for v in value:
            out |= numbers_of(v, key)
    return out


def parse_window(w: str) -> tuple[_dt.date, _dt.date] | None:
    try:
        a, b = str(w).split("/")
        return _dt.date.fromisoformat(a.strip()), _dt.date.fromisoformat(b.strip())
    except Exception:
        return None


def check_row(row: dict) -> list[tuple[str, str]]:
    """Returns [(severity, message)] — empty when the three layers agree."""
    out: list[tuple[str, str]] = []
    target = row.get("target", "?")
    ev = row.get("evidence") or []
    sr = row.get("shadow_run") or {}

    ev_text = " ".join(str(e.get("says", "")) for e in ev)
    ev_nums = numbers_in(ev_text)

    # The value only. NOT the inverse — an inverse restores a PRIOR state, and
    # the evidence for it lives with the row it supersedes, not this one.
    # (Caught on the worked example: nl-008 sets 90 and its inverse restores
    # 240, both of which its evidence happens to state. Scanning the whole row
    # made a correct row look divergent — an accounting artifact, not a finding.
    # A gate that cries wolf is worse than no gate, because the next real alarm
    # gets discounted.)
    val_nums = numbers_of(row.get("value"))

    # ── 1 · does the value's number appear in, or derive from, the evidence? ──
    if val_nums:
        unaccounted = {v for v in val_nums if v not in ev_nums}
        # a stated derivation is a legitimate answer, IF it names a method
        derived = str(row.get("derived_from", "")).strip()
        if unaccounted and not derived:
            # A value ROUNDED UP from its evidence is conservative, and this
            # repository's own rule says to be: "use p75 or higher, and p90
            # where the figure feeds a latest safe start — a latest-start
            # computation must assume the worst case or it is not a guarantee."
            # 120 from a p75 of 118, or 180 from a p90 of 174, is the rule being
            # FOLLOWED. Flagging it was the gate misreading conservatism as
            # divergence. Rounding DOWN is the dangerous direction, and that
            # still fails.
            conservative = {v for v in unaccounted
                            if any(e <= v <= e * 1.25 for e in ev_nums)}
            optimistic = {v for v in unaccounted - conservative
                          if any(v < e for e in ev_nums)}
            hard = sorted(unaccounted - conservative - optimistic)

            if optimistic:
                out.append((FAILED,
                            f"{target}: value {sorted(optimistic)} is BELOW its cited figure — "
                            f"rounding toward optimism computes deadlines that are wrong in "
                            f"the direction that loses organs"))
            if hard:
                out.append((FAILED,
                            f"{target}: value asserts {hard} — no cited source contains "
                            f"or approximates it, and no `derived_from` explains it"))
        elif unaccounted and derived:
            if len(derived) < 12 or not re.search(r"p\d\d|percentile|median|mean|max|min|round|budget|worst",
                                                  derived, re.I):
                out.append((FAILED,
                            f"{target}: `derived_from` does not name a method — "
                            f"{derived!r} is a formality, not a derivation"))

    # ── 2 · does the shadow run's arithmetic hold? ──────────────────────────
    cases = sr.get("cases")
    matched = sr.get("would_have_matched")
    missed = sr.get("would_have_missed")
    if isinstance(cases, int) and isinstance(matched, int):
        if matched > cases:
            out.append((FAILED,
                        f"{target}: shadow run matched {matched} of {cases} — "
                        f"the numerator exceeds its denominator"))
        if isinstance(missed, int) and matched + missed != cases:
            out.append((FAILED,
                        f"{target}: shadow run {matched} matched + {missed} missed "
                        f"≠ {cases} cases — the counts do not close"))

    # ── 3 · does the evidence's own n agree with the replay's? ──────────────
    ev_n = set()
    for e in ev:
        for m in re.finditer(r"\bn\s*=\s*(\d+)", str(e.get("source", "")) + " " + str(e.get("says", "")), re.I):
            ev_n.add(int(m.group(1)))
    if ev_n and isinstance(cases, int) and cases not in ev_n:
        out.append((UNVERIFIED,
                    f"{target}: evidence cites n={sorted(ev_n)} but the replay ran "
                    f"{cases} cases — different populations, or a transcription slip"))

    # ── 4 · does the replay's window overlap the evidence's? ────────────────
    win = parse_window(sr.get("window", ""))
    if win:
        ev_years = {int(y) for y in re.findall(r"\b(20\d\d)\b", ev_text)}
        if ev_years:
            span = set(range(win[0].year, win[1].year + 1))
            if not (ev_years & span):
                out.append((UNVERIFIED,
                            f"{target}: evidence speaks of {sorted(ev_years)} and the replay "
                            f"covers {sorted(span)} — the row was tested on a period its "
                            f"sources do not describe"))

    # ── 5 · a row that claims practice but replayed nothing ────────────────
    if isinstance(cases, int) and cases == 0:
        out.append((FAILED, f"{target}: a replay over zero cases is not a replay"))

    return out


def validate(patch: dict) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for row in patch.get("rows") or []:
        findings.extend(check_row(row))

    if any(s == FAILED for s, _ in findings):
        state = FAILED
    elif findings:
        state = UNVERIFIED
    else:
        state = GREEN
    return state, [m for _, m in findings]


def main(argv: list[str]) -> int:
    import json
    if not argv:
        print(__doc__)
        return 2

    path = argv[0]
    with open(path, encoding="utf-8") as fh:
        patch = json.load(fh) if path.endswith(".json") else __import__("yaml").safe_load(fh)

    state, msgs = validate(patch)
    n = len(patch.get("rows") or [])
    print(f"divergence · {path}   {n} rows\n")

    if state == GREEN:
        print(f"  GREEN — every row's value, evidence and replay tell the same story.")
        return 0
    for m in msgs:
        print(f"  {m}")
    print()
    if state == FAILED:
        print("FAILED — a row says one thing, cites another, and tested a third.")
        print("  The catches live in the disagreements; formatting is what hides them.")
        return 1
    print("PASS-UNVERIFIED — nothing contradicts outright, and something does not line up.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
