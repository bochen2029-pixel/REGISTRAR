#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Bo Chen
"""
REGISTRAR · forge · phi_scan
─────────────────────────────────────────────────────────────────────────────
Flag protected health information before it reaches a frontier model route, a
log line, a commit message, or an evidence field.

**THIS IS A HIGH-RECALL FLOOR. IT IS NEVER A GUARANTEE.**

    That sentence is the contract, not a disclaimer. A scanner presented as a
    guarantee is worse than no scanner at all, because it retires the human
    caution that was doing the actual work — somebody stops reading the diff
    because the tool said it was fine.

    So: **this tool never reports that text is clean.** It reports what it
    FOUND, and which rungs actually RAN. Those are different claims, and the
    surveyed prior art conflated them — its scanner returned zero spans both
    when a document was genuinely free of PHI and when its classifier failed to
    load, with only a line on stderr to distinguish the two. That is the same
    shape as a stalled resident being indistinguishable from a quiet one, and
    it is the single defect this implementation exists to avoid.

THE RUNGS — an ordinal naming EPISTEMIC TYPE, not strength

    rung 1  OPERATOR MARKERS. Exact strings the operator froze: their own
            people, sites, systems. **Agent-frozen** — the tool supplies the
            mechanism and never the policy. A model may not edit this list.

    rung 2  STRUCTURED PATTERNS with validators. Record numbers, dates,
            identifiers, contacts. Deterministic, checksum-verified where a
            checksum exists.

            **Rungs 1 and 2 together are the ORACLE: a non-model assertion
            that PHI is present.**

    rung 3  A PROBABILISTIC PASS. Not implemented here, and the socket is
            documented rather than stubbed. When one exists it is **a
            verification pass, not an oracle** — additive, and NEVER SOLE.

    **The union only grows.** A higher rung may add spans; it may never remove
    one. That makes the floor a property of the type rather than a promise
    somebody has to keep, and `merge()` enforces it.

WHAT THIS IS NOT

    This is a **mask** — it finds spans. Refusing to send something to a
    frontier route is a **gate**. Two jobs, different consequences, and merging
    them is how a redaction becomes an authorisation.

    The domain rule that matters most: **a single unusual case is
    re-identifiable from timing alone.** Names are the easy part. A date bound
    to an institution bound to a procedure identifies a person to anyone who
    was there, and `combination` exists for exactly that.

    python phi_scan.py --text "…"            scan a string
    python phi_scan.py --path FILE [--json]  scan a file
    python phi_scan.py --markers FILE …      supply the operator's rung-1 list

Stdlib only. No network. Every path is an argument.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# THE VERDICT — three states, and none of them is "clean"
# ─────────────────────────────────────────────────────────────────────────────
FINDINGS = "FINDINGS"            # PHI-shaped material was found
NONE_DETECTED = "NONE_DETECTED"  # the rungs that ran found nothing. NOT "clean".
DEGRADED = "DEGRADED"            # a rung did not run — this scan is incomplete

VERDICTS = (FINDINGS, NONE_DETECTED, DEGRADED)


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    cls: str
    rung: int
    confidence: float          # of the DETECTOR, never of the absence
    note: str = ""

    def label(self) -> dict:
        """
        The audit record. **Labels, never values** — an audit trail that quotes
        the PHI it found has created a second copy of it in the log.
        """
        return {"class": self.cls, "rung": self.rung, "confidence": self.confidence,
                "start": self.start, "end": self.end, "chars": self.end - self.start}


@dataclass
class ScanResult:
    verdict: str
    spans: list[Span] = field(default_factory=list)
    rungs_run: list[int] = field(default_factory=list)
    rungs_degraded: list[int] = field(default_factory=list)
    chars: int = 0

    @property
    def found(self) -> bool:
        return bool(self.spans)

    def classes(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self.spans:
            out[s.cls] = out.get(s.cls, 0) + 1
        return out

    def to_json(self) -> dict:
        return {
            "verdict": self.verdict,
            "verdict_means": {
                FINDINGS: "PHI-shaped material was found. Act on it.",
                NONE_DETECTED: ("The rungs that ran found nothing. This is NOT a statement "
                                "that the text is clean — only that this floor did not "
                                "catch anything."),
                DEGRADED: ("A rung did not run. The scan is INCOMPLETE and its silence "
                           "carries no information at all."),
            }[self.verdict],
            "rungs_run": self.rungs_run,
            "rungs_degraded": self.rungs_degraded,
            "chars_scanned": self.chars,
            "classes": self.classes(),
            "findings": [s.label() for s in self.spans],   # labels, never values
            "floor": ("This is a high-recall floor and never a guarantee. Absence of a "
                      "finding is not evidence of absence."),
        }


# ─────────────────────────────────────────────────────────────────────────────
# RUNG 2 — the structured oracle
# ─────────────────────────────────────────────────────────────────────────────
def _luhn(digits: str) -> bool:
    d = [int(c) for c in digits if c.isdigit()]
    if len(d) < 2:
        return False
    total, alt = 0, False
    for n in reversed(d):
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


def _npi_valid(npi: str) -> bool:
    """NPI carries a Luhn check digit over the number prefixed with 80840."""
    return len(npi) == 10 and _luhn("80840" + npi)


# (class, pattern, confidence, validator)
PATTERNS: list[tuple[str, re.Pattern, float, object]] = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), 0.95, None),
    ("npi", re.compile(r"\b\d{10}\b"), 0.90, lambda m: _npi_valid(m.group(0))),
    ("mrn", re.compile(r"\b(?:MRN|MR#|MedRec|Record\s*(?:No|#))\s*[:#]?\s*([A-Z]?\d{5,12})\b", re.I),
     0.92, None),
    ("donor_id", re.compile(r"\b(?:UNOS|OPTN|DONOR|DIN)\s*(?:ID)?\s*[:#-]?\s*([A-Z]{0,3}\d{3,10})\b", re.I),
     0.90, None),
    ("accession", re.compile(r"\b(?:ACC|Accession)\s*[:#]?\s*([A-Z0-9-]{6,16})\b", re.I), 0.80, None),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), 0.95, None),
    ("phone", re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)"), 0.85, None),
    ("payment_card", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), 0.85, lambda m: _luhn(m.group(0))),
    # dates, several notations
    ("date", re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), 0.55, None),
    ("date", re.compile(r"(?<!\d)\d{1,2}/\d{1,2}/\d{2,4}(?!\d)"), 0.55, None),
    ("date", re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b"),
     0.55, None),
    ("time", re.compile(r"(?<!\d)(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?!\d)"), 0.35, None),
    ("age_over_89", re.compile(r"\b(?:9\d|1\d\d)\s*(?:years?\s*old|y/?o|yo)\b", re.I), 0.90, None),
]


def rung2(text: str) -> list[Span]:
    """
    Deterministic, structured, validated where a validator exists.

    Confidence here is a property **of the detector**, never of the absence of
    other PHI. A `date` scores low alone because a date alone is often nothing —
    and it is `combination` below that decides when it stops being nothing.
    """
    out: list[Span] = []
    for cls, pat, conf, valid in PATTERNS:
        for m in pat.finditer(text):
            if valid and not valid(m):
                continue
            out.append(Span(m.start(), m.end(), cls, 2, conf))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# RUNG 1 — the operator's frozen list
# ─────────────────────────────────────────────────────────────────────────────
def rung1(text: str, markers: list[str]) -> list[Span]:
    """
    Exact strings the operator froze: their own staff, their donor hospitals,
    their systems.

    **Agent-frozen.** The tool supplies the mechanism; the operator supplies the
    policy. Nothing here infers a marker, and a model may not edit the list —
    which is what makes this the highest-confidence rung despite being the
    simplest.
    """
    out: list[Span] = []
    low = text.lower()
    for mk in markers:
        mk = mk.strip()
        if len(mk) < 3:
            continue          # a two-character marker matches everything
        needle = mk.lower()
        i = low.find(needle)
        while i >= 0:
            out.append(Span(i, i + len(mk), "operator_marker", 1, 1.0, "frozen by the operator"))
            i = low.find(needle, i + 1)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# COMBINATION — the domain rule that matters most
# ─────────────────────────────────────────────────────────────────────────────
QUASI = {"date", "time", "institution", "age_over_89", "operator_marker"}


def combinations(text: str, spans: list[Span], window: int = 240,
                 need: int = 3) -> list[Span]:
    """
    Distinct quasi-identifier classes close together re-identify.

    **A single unusual case is re-identifiable from timing alone.** A date is
    usually nothing. A date, a time and an institution within a couple of
    sentences identify a person to anyone who was in the building — and no
    individual pattern above scores that high, because individually none of them
    should.

    This is why a scanner built only on "find the names" misses the disclosure
    that actually happens in an operational document.
    """
    out: list[Span] = []
    ordered = sorted((s for s in spans if s.cls in QUASI), key=lambda s: s.start)
    for i, anchor in enumerate(ordered):
        near = [s for s in ordered[i:] if s.start - anchor.start <= window]
        kinds = {s.cls for s in near}
        if len(kinds) >= need:
            end = max(s.end for s in near)
            out.append(Span(anchor.start, end, "reidentifying_combination", 2, 0.80,
                            f"{len(kinds)} quasi-identifier classes within {window} chars: "
                            + ", ".join(sorted(kinds))))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# MERGE — additive only, and that is structural
# ─────────────────────────────────────────────────────────────────────────────
def merge(*groups: list[Span]) -> list[Span]:
    """
    Union of every rung's spans.

    **The union only grows.** A higher rung may add; it may never remove. That
    is what makes the floor a property of this function rather than a promise
    somebody has to remember — there is no code path here that drops a span
    contributed by a lower rung.
    """
    out: list[Span] = []
    for g in groups:
        out.extend(g)
    return sorted(out, key=lambda s: (s.start, s.end, s.cls))


# ─────────────────────────────────────────────────────────────────────────────
def scan(text: str, markers: list[str] | None = None,
         rung3=None) -> ScanResult:
    """
    Run the rungs and report what they found and which of them ran.

    `rung3` is a socket. If a caller supplies one and it raises, the scan is
    **DEGRADED** — never silently short. A scan whose scanner did not run is not
    a scan, and its silence carries no information.
    """
    markers = markers or []
    ran: list[int] = []
    degraded: list[int] = []

    r1 = rung1(text, markers)
    ran.append(1)

    r2 = rung2(text)
    ran.append(2)

    r3: list[Span] = []
    if rung3 is not None:
        try:
            r3 = [Span(s.start, s.end, s.cls, 3, s.confidence, "probabilistic; additive, never sole")
                  for s in rung3(text)]
            ran.append(3)
        except Exception:
            degraded.append(3)
    # rung 3 absent is NOT degradation — it was never claimed. Only a rung that
    # was supplied and then failed makes the scan incomplete.

    combos = combinations(text, merge(r1, r2))
    spans = merge(r1, r2, r3, combos)

    if degraded:
        verdict = DEGRADED
    elif spans:
        verdict = FINDINGS
    else:
        verdict = NONE_DETECTED

    return ScanResult(verdict, spans, ran, degraded, len(text))


def scan_path(path: str, markers: list[str] | None = None) -> ScanResult:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return scan(fh.read(), markers)


def load_markers(path: str) -> list[str]:
    """One marker per line. Comments with `#`. Operator-authored, agent-frozen."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


# ─────────────────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Flag PHI. A high-recall FLOOR — never a guarantee.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text")
    src.add_argument("--path")
    ap.add_argument("--markers", action="append", default=[],
                    help="file of operator-frozen exact strings (repeatable)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    markers: list[str] = []
    for m in a.markers:
        markers.extend(load_markers(m))

    r = scan_path(a.path, markers) if a.path else scan(a.text, markers)

    if a.json:
        print(json.dumps(r.to_json(), indent=2, ensure_ascii=False))
    else:
        print(f"verdict: {r.verdict}")
        print(f"rungs run: {r.rungs_run}" + (f"  DEGRADED: {r.rungs_degraded}"
                                             if r.rungs_degraded else ""))
        for cls, n in sorted(r.classes().items()):
            print(f"  {n:>4}  {cls}")
        if r.verdict == NONE_DETECTED:
            print("\nNothing was detected by the rungs that ran.")
            print("That is NOT a statement that this text is free of PHI.")
            print("This is a floor. Absence of a finding is not evidence of absence.")
        elif r.verdict == DEGRADED:
            print("\nA rung did not run. This scan is INCOMPLETE and its silence")
            print("carries no information. Do not treat it as a result.")

    # exit codes: 0 nothing detected · 1 findings · 2 degraded (worse than findings,
    # because findings are actionable and an incomplete scan is not)
    return {NONE_DETECTED: 0, FINDINGS: 1, DEGRADED: 2}[r.verdict]


if __name__ == "__main__":
    # The forge fence, wired — QC F5 found require_forge() with zero callers,
    # and a fence nobody invokes is law 9 verbatim. A deployed record must
    # not carry completion machinery that RUNS; the guard names the escape.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "core"))
    from profile import require_forge
    require_forge("forge/plugins/phi_scan/src/phi_scan.py")
    raise SystemExit(main(sys.argv[1:]))
