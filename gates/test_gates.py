#!/usr/bin/env python3
"""
REGISTRAR · gates · tests

    python gates/test_gates.py

Asserts that the battery refuses what it claims to refuse. A gate suite that
only tests the passing case tests nothing: the whole value of this layer is in
what it declines.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from validate_patch import FAILED, GREEN, UNVERIFIED, load_patch, load_targets, validate  # noqa: E402

WORKED = os.path.join(ROOT, "examples", "worked")
REJECTED = os.path.join(WORKED, "rejected")

PASS, FAIL = [], []


def check(name: str, got, want) -> None:
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def state_of(result, gate: str) -> str:
    for s, g, _ in result.rows:
        if g == gate:
            return s
    return "MISSING"


def run(path: str):
    return validate(load_patch(path), load_targets())


# ─────────────────────────────────────────────────────────────────────────────
def test_accepted_patch() -> None:
    print("\nthe accepted patch")
    r = run(os.path.join(WORKED, "northlake.patch.json"))

    for gate in ("schema shape", "blast radius", "target syntax", "L0/L1/L4 immutability",
                 "inverse declared", "evidence binding", "shadow run", "expiry", "signature"):
        check(f"{gate} is GREEN", state_of(r, gate), GREEN)

    check("nothing FAILED", FAILED in {s for s, _, _ in r.rows}, False)
    # and the point of the whole exercise:
    check("overall is PASS-UNVERIFIED, not GREEN", r.worst, UNVERIFIED)


def test_undecidable_gates_say_so() -> None:
    """
    The three gates that cannot be decided from a file must report
    PASS-UNVERIFIED. If one of them ever reports GREEN, this validator has
    started committing the error it exists to prevent.
    """
    print("\nundecidable gates report PASS-UNVERIFIED, never GREEN")
    r = run(os.path.join(WORKED, "northlake.patch.json"))
    for gate in ("local invertibility", "shadow-run fidelity", "totality on provision"):
        check(f"{gate}", state_of(r, gate), UNVERIFIED)


def test_off_surface_refused() -> None:
    print("\n01 · targets the seed does not declare")
    r = run(os.path.join(REJECTED, "01-off-surface.json"))
    check("blast radius FAILED", state_of(r, "blast radius"), FAILED)
    check("overall FAILED", r.worst, FAILED)
    detail = next(d for s, g, d in r.rows if g == "blast radius")
    check("names both offending targets", "match_run_sequence" in detail and "consent_required" in detail, True)


def test_ungrounded_refused() -> None:
    print("\n02 · plausible and grounded in nothing")
    r = run(os.path.join(REJECTED, "02-ungrounded.json"))
    check("evidence binding FAILED", state_of(r, "evidence binding"), FAILED)
    check("shadow run FAILED", state_of(r, "shadow run"), FAILED)
    detail = next(d for s, g, d in r.rows if g == "evidence binding")
    check("catches generality asserted as evidence", "generality" in detail, True)
    check("catches the missing denominator",
          "no denominator" in next(d for s, g, d in r.rows if g == "shadow run"), True)


def test_missing_inverse_refused() -> None:
    print("\n03 · no way back")
    r = run(os.path.join(REJECTED, "03-no-inverse.json"))
    check("schema shape FAILED", state_of(r, "schema shape"), FAILED)
    check("inverse declared FAILED", state_of(r, "inverse declared"), FAILED)
    check("expiry FAILED (not a date)", state_of(r, "expiry"), FAILED)


def test_partial_application_refused() -> None:
    print("\n04 · the silent one")
    r = run(os.path.join(REJECTED, "04-partial.json"))
    check("totality on provision FAILED", state_of(r, "totality on provision"), FAILED)
    # everything else about this row is fine, which is exactly why it needs a gate
    check("blast radius still GREEN", state_of(r, "blast radius"), GREEN)
    check("evidence still GREEN", state_of(r, "evidence binding"), GREEN)


def test_targets_match_lifecycle() -> None:
    """
    targets.json is generated. If the lifecycle grows a variation point and
    nobody regenerates, the gate would silently refuse a legitimate target.
    """
    print("\ntargets.json has not drifted from lifecycle.yml")
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("  skip  (pyyaml unavailable — regeneration check needs it; gates themselves do not)")
        return
    sys.path.insert(0, os.path.join(ROOT, "core", "lifecycle"))
    import gen_targets  # noqa: E402

    fresh = gen_targets.build()["targets"]
    with open(os.path.join(ROOT, "core", "lifecycle", "targets.json"), encoding="utf-8") as fh:
        current = json.load(fh)["targets"]
    check("targets.json is current", current, fresh)


def test_every_target_has_a_question() -> None:
    """
    elicit/questions.yml is keyed to the declared surface. A variation point
    with no question is a part of the operation nobody will be asked about.
    """
    print("\nevery declared target has a question")
    try:
        import yaml
    except ImportError:
        print("  skip  (pyyaml unavailable)")
        return
    with open(os.path.join(ROOT, "elicit", "questions.yml"), encoding="utf-8") as fh:
        qs = yaml.safe_load(fh)["questions"]
    asked = {q["target"] for q in qs}
    declared = set(load_targets())

    check("no target is unasked", sorted(declared - asked), [])
    check("no question asks about a target that does not exist", sorted(asked - declared), [])
    check("every question names its sources", all(q.get("sources") for q in qs), True)
    check("every question names its trap", all(q.get("trap") for q in qs), True)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("REGISTRAR · gates")
    for t in (
        test_accepted_patch,
        test_undecidable_gates_say_so,
        test_off_surface_refused,
        test_ungrounded_refused,
        test_missing_inverse_refused,
        test_partial_application_refused,
        test_targets_match_lifecycle,
        test_every_target_has_a_question,
    ):
        t()

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
