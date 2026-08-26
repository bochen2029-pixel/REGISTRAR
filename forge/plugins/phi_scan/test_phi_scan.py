#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
REGISTRAR · forge · phi_scan · the battery

    python forge/plugins/phi_scan/test_phi_scan.py

**The first three groups are the reason this plugin exists.** The surveyed
prior art conflated "clean" with "not detected", and silently returned zero
spans when its classifier failed to load — so a degraded scanner and a
genuinely clean document produced byte-identical output.

These assert that cannot happen here: there is no CLEAN verdict to return, a
failed rung produces DEGRADED, and the union only grows.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import phi_scan as P  # noqa: E402

PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


# ── 1 · THERE IS NO "CLEAN" ─────────────────────────────────────────────────
def test_never_clean():
    """
    The defect this plugin exists to avoid. `NONE_DETECTED` and `CLEAN` are
    different claims, and only one of them is true of a floor.
    """
    print("\nthere is no CLEAN verdict, and there cannot be")
    check("the vocabulary has three states", set(P.VERDICTS),
          {P.FINDINGS, P.NONE_DETECTED, P.DEGRADED})
    check("none of them is CLEAN", any("CLEAN" == v for v in P.VERDICTS), False)

    r = P.scan("nothing of interest in this sentence at all")
    check("empty findings reads NONE_DETECTED", r.verdict, P.NONE_DETECTED)

    j = r.to_json()
    check("and the payload says what that does NOT mean",
          "NOT a statement" in j["verdict_means"], True)
    check("and names itself a floor", "floor" in j["floor"].lower(), True)

    src = open(os.path.join(HERE, "src", "phi_scan.py"), encoding="utf-8").read()
    check("the word CLEAN never appears as a verdict",
          re.search(r'"CLEAN"|= *"clean"', src), None)


# ── 2 · A FAILED RUNG IS LOUD ───────────────────────────────────────────────
def test_degraded_is_not_silence():
    """
    KEEL's rung 3 returned an empty list when its model failed to load. A
    degraded scanner and a clean text were byte-identical. Here they are not.
    """
    print("\na rung that was supplied and failed makes the scan DEGRADED")

    def broken(_text):
        raise RuntimeError("model would not load")

    r = P.scan("nothing here", rung3=broken)
    check("verdict is DEGRADED", r.verdict, P.DEGRADED)
    check("the failed rung is named", r.rungs_degraded, [3])
    check("and it is NOT reported as nothing-found", r.verdict == P.NONE_DETECTED, False)
    check("the payload says the silence carries no information",
          "carries no information" in r.to_json()["verdict_means"], True)

    clean = P.scan("nothing here")
    check("a genuinely quiet scan differs from a degraded one",
          clean.verdict != r.verdict, True)


def test_absent_rung_is_not_degradation():
    """
    A rung never supplied was never claimed. Reporting DEGRADED for it would
    cry wolf, and the next real alarm gets discounted.
    """
    print("\na rung that was never supplied is not degradation")
    r = P.scan("nothing here")
    check("no rung3 supplied — not degraded", r.rungs_degraded, [])
    check("and rungs 1 and 2 are recorded as run", r.rungs_run, [1, 2])


# ── 3 · THE UNION ONLY GROWS ────────────────────────────────────────────────
def test_union_only_grows():
    """
    A higher rung may add spans. It may never remove one. That makes the floor
    a property of `merge()` rather than a promise somebody has to keep.
    """
    print("\nthe union only grows — a higher rung cannot unmask a lower one")
    a = [P.Span(0, 5, "operator_marker", 1, 1.0)]
    b = [P.Span(10, 20, "mrn", 2, 0.9)]
    c = [P.Span(0, 5, "name", 3, 0.4)]      # rung 3 overlapping rung 1
    m = P.merge(a, b, c)
    check("every input span survives", len(m), 3)
    check("the rung-1 span is still there",
          any(s.rung == 1 and s.start == 0 for s in m), True)

    src = open(os.path.join(HERE, "src", "phi_scan.py"), encoding="utf-8").read()
    body = src[src.index("def merge("):src.index("def scan(")]
    check("merge contains no removal", re.search(r"\.remove\(|del |\.pop\(", body), None)


# ── 4 · THE DOMAIN RULE ─────────────────────────────────────────────────────
def test_combination_reidentifies():
    """
    A single unusual case is re-identifiable from timing alone. A date is
    usually nothing; a date bound to a time bound to an institution is a person.
    """
    print("\nquasi-identifiers in combination are the finding")
    markers = ["Northlake Regional"]

    one = P.scan("The review occurred on 2026-08-14.", markers)
    check("a bare date is not a combination",
          any(s.cls == "reidentifying_combination" for s in one.spans), False)

    three = P.scan("Cross-clamp at Northlake Regional on 2026-08-14 at 03:15.", markers)
    combos = [s for s in three.spans if s.cls == "reidentifying_combination"]
    check("date + time + institution IS", len(combos) > 0, True)
    check("and the finding names the classes",
          "quasi-identifier classes" in combos[0].note, True)


def test_structured_classes():
    print("\nthe structured oracle — deterministic, validated where possible")
    cases = {
        "ssn": "SSN 123-45-6789 on file",
        "mrn": "MRN: 4471902 admitted",
        "donor_id": "UNOS ID ABC12345 allocated",
        "email": "reach coordinator@example.org",
        "phone": "call 214-555-0199 tonight",
        "age_over_89": "the donor was 94 years old",
    }
    for cls, text in cases.items():
        found = {s.cls for s in P.scan(text).spans}
        check(f"detects {cls}", cls in found, True)


def test_validators_reject_lookalikes():
    """A ten-digit number is not an NPI. A checksum is what makes it one."""
    print("\nvalidators reject look-alikes")
    check("a random 10-digit number is not an NPI",
          any(s.cls == "npi" for s in P.scan("order 1234567890 placed").spans), False)
    check("a valid NPI is",
          any(s.cls == "npi" for s in P.scan("NPI 1234567893 signed").spans), True)
    check("a random 16-digit run is not a card",
          any(s.cls == "payment_card" for s in P.scan("ref 1111111111111111").spans), False)


def test_operator_markers_are_frozen_policy():
    """The tool supplies mechanism. The operator supplies policy."""
    print("\nrung 1 is the operator's, and the tool never infers it")
    r = P.scan("Dr Okonkwo reviewed the case", ["Okonkwo"])
    check("a frozen marker is found at rung 1",
          [s.rung for s in r.spans if s.cls == "operator_marker"], [1])
    check("confidence is total — it is an exact string the operator froze",
          [s.confidence for s in r.spans if s.cls == "operator_marker"], [1.0])
    check("without the marker it is not inferred",
          any(s.cls == "operator_marker" for s in P.scan("Dr Okonkwo reviewed").spans), False)
    check("a two-character marker is refused as too broad",
          any(s.cls == "operator_marker" for s in P.scan("a b c", ["ab"]).spans), False)


# ── 5 · LABELS, NEVER VALUES ────────────────────────────────────────────────
def test_audit_carries_labels_not_values():
    """An audit trail that quotes the PHI it found has made a second copy of it."""
    print("\nthe record carries labels, never values")
    secret = "coordinator@example.org"
    r = P.scan(f"reach {secret} tonight")
    blob = json.dumps(r.to_json())
    check("a finding was recorded", r.found, True)
    check("and the value is NOT in the output", secret in blob, False)
    check("the class is", "email" in blob, True)
    check("with offsets, so a caller can redact", '"start"' in blob, True)


# ── 6 · THE CLI CONTRACT ────────────────────────────────────────────────────
def test_cli_exit_codes():
    print("\nexit codes — degraded is worse than findings")
    exe = [sys.executable, os.path.join(HERE, "src", "phi_scan.py")]
    r0 = subprocess.run(exe + ["--text", "an ordinary sentence"], capture_output=True, text=True)
    check("nothing detected exits 0", r0.returncode, 0)
    check("and says so in words", "not evidence of absence" in r0.stdout.lower(), True)

    r1 = subprocess.run(exe + ["--text", "MRN: 4471902"], capture_output=True, text=True)
    check("findings exit 1", r1.returncode, 1)

    r2 = subprocess.run(exe + ["--text", "x", "--json"], capture_output=True, text=True)
    check("--json is parseable", json.loads(r2.stdout)["verdict"], P.NONE_DETECTED)


# ── 7 · THE PLUGIN CONTRACT ─────────────────────────────────────────────────
def test_contract_self_check():
    print("\nthe contract, self-checked")
    src = open(os.path.join(HERE, "src", "phi_scan.py"), encoding="utf-8").read()
    check("carries an SPDX identifier", "SPDX-License-Identifier: MIT" in src, True)
    check("describes itself as a floor", re.search(r"\bfloor\b", src, re.I) is not None, True)
    check("and refuses the word guarantee as a claim",
          "NEVER A GUARANTEE" in src.upper(), True)
    abs_paths = [m.group(0) for m in re.finditer(r"['\"][A-Za-z]:[\\/]{1,2}[^'\"\n]{2,}['\"]", src)]
    check("no hardcoded absolute paths", abs_paths, [])
    for mod in ("urllib", "requests", "socket", "httpx"):
        check(f"does not import {mod}", re.search(rf"^\s*import\s+{mod}", src, re.M), None)


if __name__ == "__main__":
    print("REGISTRAR · forge · phi_scan")
    for t in (test_never_clean, test_degraded_is_not_silence, test_absent_rung_is_not_degradation,
              test_union_only_grows, test_combination_reidentifies, test_structured_classes,
              test_validators_reject_lookalikes, test_operator_markers_are_frozen_policy,
              test_audit_carries_labels_not_values, test_cli_exit_codes, test_contract_self_check):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
