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
from witness import ENTANGLED, FLOOR, matrix  # noqa: E402

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
    witnesses("21-partial-isolated.json", "totality on provision", "partial")
    witnesses("22-no-value.json", "schema shape", "value")


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
              "06-unsigned.json", "21-partial-isolated.json", "22-no-value.json"):
        # `schema conformance` is a STRUCTURAL FLOOR beneath every gate, not a
        # peer of them. A file with `cases: 0` violates both the shadow-run gate
        # and the schema's `minimum: 1`; a file missing `value` violates both
        # schema shape and the schema's `required`. Counting the floor here
        # would be like counting "the JSON parsed" as a gate — the isolation
        # property this test protects is about the SEMANTIC gates, and it
        # survives intact once the floor is excluded.
        #
        # Narrowed 2026-08-26 when gate 14 landed. Narrowed, not weakened:
        # every fixture below still fires exactly one semantic gate.
        fired = [g for g in per_fixture.get(f, []) if g not in FLOOR]
        check(f"{f} fires exactly one", len(fired), 1)


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
    # FLOOR gates fire on any deliberately-minimal fragment and say nothing about
    # whether the SEMANTIC hole this fixture records is still open.
    semantic = [g for s, g, _ in r.rows if s == FAILED and g not in FLOOR]
    check("no SEMANTIC gate FAILS on it", semantic, [])
    # The overall verdict is now FAILED rather than PASS-UNVERIFIED, because
    # gate 15 refuses this fragment for not accounting for its targets. That is
    # a FLOOR refusal, not a semantic one — the hole this fixture records is
    # still open, which is what the assertion above establishes.
    check("and its verdict is not GREEN", r.worst != GREEN, True)

    with open(p, encoding="utf-8") as fh:
        doc = json.load(fh)
    check("it declares itself uncaught", "UNCAUGHT" in doc.get("$status", ""), True)
    check("and the row is genuinely partial",
          "closes" not in json.dumps(doc["rows"][0]["value"]), True)
    check("while its own evidence contains the missing value",
          "10:00" in json.dumps(doc["rows"][0]["evidence"]), True)


def test_uncaught_fixtures_are_still_uncaught():
    """
    Every *UNCAUGHT* fixture must STILL pass every gate.

    This test fails in BOTH directions, and that is the point:

      · if a fixture starts being caught, the exposure closed — **promote it**
        to a witness, rename it, and say which gate closed it. Leaving a caught
        fixture labelled UNCAUGHT would be a standing lie about coverage.
      · if the file disappears, someone deleted an exposure rather than fixing
        it, which is the failure mode this whole fork exists to prevent.

    A fixture retained as a known hole is only honest while the hole is real.
    """
    print("\nthe known exposures are still exposures")
    ambient = {"shadow-run fidelity", "totality on provision"} | FLOOR
    found = sorted(f for f in os.listdir(REJECTED) if "UNCAUGHT" in f)
    check("at least seven are retained", len(found) >= 7, True)

    # 20-adverse-replay IS NO LONGER SILENT. Gate 14 (schema conformance,
    # 2026-08-26) catches it: the fixture carries `shadow_run.cases` as a STRING
    # and the schema types it as an integer. Nothing in the tree validated
    # against patch.schema.json until that gate existed — which is precisely why
    # the hole was open.
    #
    # ONE OF THE SEVEN EXPOSURES IS CLOSED. Recorded here rather than by quietly
    # deleting the fixture: it is now a WITNESS for gate 14 instead of a hole,
    # and the filename still says UNCAUGHT because renaming it belongs to
    # whoever owns this battery.
    CLOSED = {"20-adverse-replay-UNCAUGHT.json": "schema conformance"}

    for f in found:
        r = validate(load_patch(os.path.join(REJECTED, f)), load_targets())
        tripped = [g for s, g, _ in r.rows if s != GREEN and g not in ambient]
        if f in CLOSED:
            # gate 14 is a FLOOR and so filtered from `tripped`; assert the
            # closure where the catch actually lives — the schema validator.
            import subprocess as _sp
            _r = _sp.run([sys.executable, os.path.join(ROOT, "schema", "validate.py"),
                          os.path.join(REJECTED, f)], capture_output=True, text=True)
            check(f"{f[:34]} NOW CAUGHT by {CLOSED[f]}", _r.returncode, 1)
        else:
            check(f"{f[:34]} still silent", tripped, [])


def test_every_uncaught_fixture_explains_itself():
    """
    A fixture nobody can read is a fixture nobody will act on. Each must say
    what it is, that it is uncaught, and who found it.
    """
    print("\nand each says what it is")
    for f in sorted(f for f in os.listdir(REJECTED) if "UNCAUGHT" in f):
        with open(os.path.join(REJECTED, f), encoding="utf-8") as fh:
            doc = json.load(fh)
        check(f"{f[:30]} declares UNCAUGHT", "UNCAUGHT" in doc.get("$status", ""), True)
        check(f"{f[:30]} names its finder", bool(doc.get("$found_by")), True)
        check(f"{f[:30]} says FICTIONAL", "FICTIONAL" in doc.get("$comment", ""), True)


def test_coverage_is_reported_not_asserted():
    """The battery's own coverage is a number this repository must print, not a
    property it may assume."""
    print("\ncoverage is measured")
    per_gate, _ = matrix()
    states = [i["state"] for i in per_gate.values()]
    check("fifteen gates", len(per_gate), 15)   # 14 schema conformance, 15 accountability
    check("at least nine cleanly witnessed", states.count("WITNESSED") >= 9, True)
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
              test_uncaught_fixtures_are_still_uncaught,
              test_every_uncaught_fixture_explains_itself,
              test_coverage_is_reported_not_asserted):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
