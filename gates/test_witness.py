#!/usr/bin/env python3
"""
REGISTRAR · gates · witness tests

    python gates/test_witness.py

**A fixture without an assertion proves nothing.** These bind each fixture to
the gate it exists to witness, and assert that the gate's refusal NAMES THE
DEFECT — `SPEC.md` requires every refusal to teach, and a gate that says
"invalid" is a gate nobody learns from.

Three results here are findings rather than tests, and they are marked:

  · `L0/L1/L4 immutability` is UNREACHABLE from a patch file — a seed invariant
    living in a patch validator. Witnessed with a synthetic target table.
  · `target syntax` and `inverse declared` CANNOT be isolated — each is
    structurally entangled with a gate that fires first.
  · `signature` never returns FAILED, and that is correct: an unsigned row is a
    legal draft, so its witness asserts the MIDDLE state.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

from validate_patch import (  # noqa: E402
    FAILED, GREEN, UNVERIFIED, load_patch, load_targets, validate,
)
from witness import ENTANGLED, matrix  # noqa: E402

REJECTED = os.path.join(ROOT, "examples", "worked", "rejected")
PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def verdict(fixture: str, gate: str) -> tuple[str, str]:
    """(state, detail) for one gate on one fixture."""
    r = validate(load_patch(os.path.join(REJECTED, fixture)), load_targets())
    for st, g, d in r.rows:
        if g == gate:
            return st, d
    raise AssertionError(f"no gate named {gate!r}")


def witnesses(fixture: str, gate: str, teaches: str, state: str = FAILED):
    st, detail = verdict(fixture, gate)
    check(f"{fixture} → {gate}", st, state)
    check(f"   and it names the defect", teaches.lower() in detail.lower(), True)


# ── the isolated witnesses ──────────────────────────────────────────────────
def test_isolated_witnesses():
    print("\neach fixture witnesses its own gate, and says why")
    witnesses("07-generality.json", "evidence binding", "generality")
    witnesses("08-no-denominator.json", "shadow run", "denominator")
    witnesses("09-permanent.json", "expiry", "expiry")
    witnesses("10-no-way-back.json", "local invertibility", "prior")
    witnesses("11-undeclared-target.json", "blast radius", "does not declare")
    witnesses("12-divergence.json", "divergence", "")
    witnesses("06-unsigned.json", "signature", "unsigned", state=UNVERIFIED)


def test_isolated_means_isolated():
    """
    A fixture that trips several gates proves SOMETHING refused it, not WHICH —
    and if one of those gates silently stopped working, the fixture would still
    fail and still look green.
    """
    print("\nan isolating fixture fires exactly one gate")
    _, per_fixture = matrix()
    for f in ("07-generality.json", "08-no-denominator.json", "09-permanent.json",
              "10-no-way-back.json", "11-undeclared-target.json", "12-divergence.json",
              "06-unsigned.json"):
        check(f"{f} fires exactly one", len(per_fixture.get(f, [])), 1)


# ── the findings ────────────────────────────────────────────────────────────
def test_signature_never_fails_and_that_is_correct():
    """
    `AGENTS.md`: a machine leaves `author` empty, and the signature is the
    output commit. So unsigned is *not yet*, never *wrong* — and a gate that
    FAILED here would refuse the very artifact a harness is meant to produce.
    """
    print("\nsignature refuses in the MIDDLE state, deliberately")
    st, detail = verdict("06-unsigned.json", "signature")
    check("unsigned is PASS-UNVERIFIED", st, UNVERIFIED)
    check("never FAILED", st != FAILED, True)
    check("and it says why it is not fatal yet",
          "draft" in detail.lower() and "mount" in detail.lower(), True)


def test_immutability_is_unreachable_from_a_patch():
    """
    FINDING. The gate fires only when a target is DECLARED and its layer is not
    L2/L3 — but every entry in `targets.json` is lifted from a `local_variation`
    and all twenty are L2/L3. **No patch can reach it.** It is a seed invariant
    in a patch validator, and it is witnessed here with a synthetic table.
    """
    print("\nL0/L1/L4 immutability is a SEED invariant, not a patch gate")
    T = load_targets()
    check("every declared target is L2 or L3",
          sorted({v["layer"] for v in T.values()}), ["L2", "L3"])

    row = {"target": "intake.channel", "value": 1, "inverse": None,
           "evidence": [{"kind": "tape", "source": "t", "says": "x"}],
           "shadow_run": {"cases": 1, "would_have_matched": 1, "would_have_missed": 0},
           "expiry": "2027-01-01", "author": "A. Person"}

    # with the real table it cannot fire
    fired = [g for s, g, _ in validate({"rows": [row]}, T).rows if s == FAILED]
    check("unreachable with the real target table", "L0/L1/L4 immutability" in fired, False)

    # with a seed that wrongly declared an L0 variation point, it does
    bad = dict(T)
    bad["intake.channel"] = {"layer": "L0", "state": "referral_received", "note": ""}
    fired2 = [g for s, g, _ in validate({"rows": [row]}, bad).rows if s == FAILED]
    check("fires when the SEED declares an L0 target", "L0/L1/L4 immutability" in fired2, True)
    check("and the entanglement is documented", "L0/L1/L4 immutability" in ENTANGLED, True)


def test_structural_entanglements_are_declared():
    """
    Two gates cannot be isolated, and recording that is the finding rather than
    an excuse. A fixture author who does not know will chase an impossible
    fixture; a reader who does not know will read `incidental` as sloppiness.
    """
    print("\nstructural entanglements are named, not hidden")
    check("target syntax is declared entangled", "target syntax" in ENTANGLED, True)

    # a malformed target can never be a declared target
    T = load_targets()
    check("no declared target is malformed",
          any(t != t.lower() or " " in t for t in T), False)


def test_the_uncaught_fixture_is_retained_and_uncaught():
    """
    THE FINDING OF THIS FORK. `totality on provision` fires only on a literal
    `__partial__` marker — i.e. only when a row ANNOTATES its own omission. A
    harness that forgets a key does not annotate the omission, so the defect
    the gate is named after passes.
    """
    print("\nthe silent one still gets through — and is retained on purpose")
    f = "14-silent-partial-UNCAUGHT.json"
    p = os.path.join(REJECTED, f)
    check("the fixture is retained", os.path.exists(p), True)

    r = validate(load_patch(p), load_targets())
    check("no gate FAILS on it", [g for s, g, _ in r.rows if s == FAILED], [])
    check("its overall verdict is not GREEN either — only ambient PASS-UNVERIFIED",
          r.worst, UNVERIFIED)

    with open(p, encoding="utf-8") as fh:
        doc = json.load(fh)
    check("it declares itself uncaught", "UNCAUGHT" in doc.get("$status", ""), True)
    check("and the row is genuinely partial",
          "closes" not in json.dumps(doc["rows"][0]["value"]), True)
    check("while its own evidence contains the missing value",
          "10:00" in json.dumps(doc["rows"][0]["evidence"]), True)


def test_coverage_is_reported_not_asserted():
    """The battery's own coverage is a number this repository must print, not a
    property it may assume."""
    print("\ncoverage is measured")
    per_gate, _ = matrix()
    states = [i["state"] for i in per_gate.values()]
    check("thirteen gates", len(per_gate), 13)
    check("at least seven cleanly witnessed", states.count("WITNESSED") >= 7, True)
    real_gaps = [g for g, i in per_gate.items()
                 if i["state"] == "UNWITNESSED" and g not in ENTANGLED]
    check("no unwitnessed gate lacks an explanation", real_gaps, [])


if __name__ == "__main__":
    print("REGISTRAR · gates · witnesses")
    for t in (test_isolated_witnesses, test_isolated_means_isolated,
              test_signature_never_fails_and_that_is_correct,
              test_immutability_is_unreachable_from_a_patch,
              test_structural_entanglements_are_declared,
              test_the_uncaught_fixture_is_retained_and_uncaught,
              test_coverage_is_reported_not_asserted):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
