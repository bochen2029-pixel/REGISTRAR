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
  · `signature` never returns FAILED **for an unsigned row**, and that is
    correct: an unsigned row is a legal draft, so its witness asserts the MIDDLE
    state. It does now FAIL a MACHINE-SHAPED author — see below.

AND ONE MORE, ADDED `2026-08-27` — THE WELL-FORMED CARRIERS

The retained `*-UNCAUGHT` exposures are deliberately-minimal FRAGMENTS, so since
gates 14 and 15 landed they trip the FLOOR **for being fragments**. That says
nothing about whether the semantic hole each one records is still open, and a
reader who ran one and saw a refusal could conclude it had closed.

So each is carried again on a COMPLETE patch — the worked example, twenty of
twenty targets answered or declined, one defect planted and nothing else
touched. **All six rode straight through: every carrier reported the same state
on all sixteen gates as `northlake.patch.json` itself.** The battery could not
distinguish a patch that repoints the national allocation system from the one it
ships as the example to copy. Measured, not intuited — see `WELLFORMED` below.

**Then one of them was closed.** `27` — a machine filling in `author` — was the
only defect that made a patch MORE green than an honest draft, so it was ranked
first and fixed: the signature gate now refuses a MACHINE-SHAPED author, `27` is
a witness rather than a hole, and the mutation score moved 74.8% → 81.9% on the
same change. Five carriers remain open, and each says so in its own `$status`.
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
    witnesses("23-superseded-evidence.json", "attest", "NO LONGER IN FORCE")


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
              "06-unsigned.json", "21-partial-isolated.json", "22-no-value.json",
              "23-superseded-evidence.json"):
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
    output commit. So UNSIGNED is *not yet*, never *wrong* — and a gate that
    FAILED there would refuse the very artifact a harness is meant to produce.

    NARROWED `2026-08-27`, and narrowed rather than weakened. The gate now
    FAILS a MACHINE-SHAPED author, so "signature never fails" is no longer true
    as a sentence about the gate — it is true, and load-bearing, about the
    EMPTY field, which is the only case this test was ever about. The contrast
    is asserted below rather than left implied: an empty field is an honest
    draft, and a machine's name in that field is a manufactured signature. **The
    two must not report the same state**, and before this they did not report
    the same state as each other either — the machine's name reported GREEN,
    which was better than honest.
    """
    print("\nsignature refuses an UNSIGNED row in the MIDDLE state, deliberately")
    st, detail = verdict("06-unsigned.json", "signature")
    check("unsigned is PASS-UNVERIFIED", st, UNVERIFIED)
    check("never FAILED for an unsigned row", st != FAILED, True)
    check("and it says why it is not fatal yet",
          "draft" in detail.lower() and "mount" in detail.lower(), True)

    mst, _ = verdict("27-not-a-person-WELLFORMED.json", "signature")
    check("a MACHINE-SHAPED author is a different state", mst, FAILED)
    check("   and it is not the honest middle state", mst != st, True)


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
    # TWO OF THE SEVEN EXPOSURES ARE CLOSED. Recorded here rather than by quietly
    # deleting either fixture: each is now a WITNESS instead of a hole, and the
    # filenames still say UNCAUGHT because renaming them belongs to whoever owns
    # this battery.
    #
    # `17-not-a-person` closed 2026-08-27, and it closed BY MEASUREMENT rather
    # than by inspection. The fragment had been sitting here since the sweep; what
    # moved was carrying the same defect on a COMPLETE patch
    # (27-not-a-person-WELLFORMED.json) and finding that it reported the same
    # state on all sixteen gates as the accepted worked example — the only defect
    # in the battery that made a patch MORE green than an honest draft. The
    # signature gate now refuses a MACHINE-SHAPED author. The fragment is
    # retained unedited so the exposure it recorded stays legible.
    CLOSED = {
        "20-adverse-replay-UNCAUGHT.json": "schema conformance",
        "17-not-a-person-UNCAUGHT.json": "signature",
    }

    for f in found:
        r = validate(load_patch(os.path.join(REJECTED, f)), load_targets())
        tripped = [g for s, g, _ in r.rows if s != GREEN and g not in ambient]
        if f == "20-adverse-replay-UNCAUGHT.json":
            # gate 14 is a FLOOR and so filtered from `tripped`; assert the
            # closure where the catch actually lives — the schema validator.
            import subprocess as _sp
            _r = _sp.run([sys.executable, os.path.join(ROOT, "schema", "validate.py"),
                          os.path.join(REJECTED, f)], capture_output=True, text=True)
            check(f"{f[:34]} NOW CAUGHT by {CLOSED[f]}", _r.returncode, 1)
        elif f in CLOSED:
            # a SEMANTIC gate catches it, so the closure is visible in `tripped`
            # itself — and the refusal must still teach.
            st, detail = verdict(f, CLOSED[f])
            check(f"{f[:34]} NOW CAUGHT by {CLOSED[f]}", st, FAILED)
            check("   and the refusal names the defect",
                  "machine-shaped" in detail.lower(), True)
            check("   and it is the ONLY semantic gate that catches it",
                  tripped, [CLOSED[f]])
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


# ── the well-formed carriers ────────────────────────────────────────────────
# THE ROADMAP'S STANDING INSTRUCTION, EXECUTED. `2026-08-27`.
#
#   "The next move is a well-formed variant of each of the six: if one passes
#    clean, that is the highest-priority gate in the project, identified by
#    MEASUREMENT rather than intuition."
#
# The six retained exposures are deliberately-minimal FRAGMENTS. Since gates 14
# and 15 landed they trip the FLOOR — schema conformance, accountability — **for
# being fragments**, and a reader who runs one and sees a refusal could conclude
# the hole had closed. It has not. A floor refusal says nothing about whether the
# SEMANTIC hole is still open, and the only way to answer that is to carry the
# same defect on a patch the floor has no quarrel with.
#
# So each carrier below is `examples/worked/northlake.patch.json` — complete,
# schema-valid, twenty of twenty declared targets answered or declined — with
# EXACTLY ONE semantic defect planted and everything else left as the worked
# example wrote it. **Same defect, no fragment to blame.**
WELLFORMED = {
    "24-silent-partial-WELLFORMED.json":     "14-silent-partial-UNCAUGHT.json",
    "25-credentials-WELLFORMED.json":        "15-credentials-UNCAUGHT.json",
    "26-expired-on-arrival-WELLFORMED.json": "16-expired-on-arrival-UNCAUGHT.json",
    "27-not-a-person-WELLFORMED.json":       "17-not-a-person-UNCAUGHT.json",
    "28-contradiction-WELLFORMED.json":      "18-contradiction-UNCAUGHT.json",
    "29-partial-bypass-WELLFORMED.json":     "19-partial-bypass-UNCAUGHT.json",
}

# ONE OF THE SIX IS CLOSED, `2026-08-27` — and closing it was the point.
#
# The measurement identified `27` as the highest-priority hole for one reason:
# it was the only defect in the battery that made a patch **more green than an
# honest draft.** Leave `author` empty and the gate says *not yet signed*; write
# a machine's own name in it and the gate said *a named human*. The gate now
# refuses a machine-shaped author, so `27` has been promoted from exposure to
# WITNESS and is asserted here as a catch rather than as a hole.
#
# **What it deliberately does not close**: a machine that types a plausible human
# name still passes, and nothing readable from a file can tell that from a human
# typing it. That residue is why the mount ceremony exists.
CLOSED_CARRIERS = {"27-not-a-person-WELLFORMED.json": "signature"}

WORKED = os.path.join(ROOT, "examples", "worked", "northlake.patch.json")


def _states(patch: dict) -> dict[str, str]:
    return {g: s for s, g, _ in validate(patch, load_targets()).rows}


def test_wellformed_carriers_are_not_fragments():
    """
    **The premise of the whole exercise, asserted rather than assumed.**

    If a carrier tripped a floor gate it would prove nothing the fragment did
    not already prove — the refusal would be about its shape, and the semantic
    question would stay unanswered. So: no FLOOR gate may refuse a carrier.
    """
    print("\nthe carriers are complete patches, not fragments")
    for f in sorted(WELLFORMED):
        p = load_patch(os.path.join(REJECTED, f))
        rows = {g: (s, d) for s, g, d in validate(p, load_targets()).rows}
        for g in sorted(FLOOR):
            check(f"{f[:30]} {g} GREEN", rows[g][0], GREEN)
        check(f"{f[:30]} accounts for all 20 targets",
              "20 declared; nothing silent" in rows["accountability"][1], True)


def test_wellformed_carriers_are_indistinguishable_from_the_accepted_patch():
    """
    **THE FINDING, stated as strongly as it can be stated.**

    Not merely "nothing FAILED". The carriers report the SAME STATE ON EVERY
    GATE as `northlake.patch.json` — the patch this repository ships as the one
    to copy. Sixteen gates, and the battery cannot tell a patch that repoints
    the national allocation system from the teaching example.

    A CLOSED carrier must differ on EXACTLY the gate that closed it, and agree
    everywhere else. That is what makes it a witness rather than a second
    defect: if it diverged on two gates, the fix reached further than the hole.
    """
    print("\nevery gate says the same thing about a carrier as about the accepted patch")
    want = _states(load_patch(WORKED))
    for f in sorted(WELLFORMED):
        got = _states(load_patch(os.path.join(REJECTED, f)))
        if f in CLOSED_CARRIERS:
            g = CLOSED_CARRIERS[f]
            check(f"{f[:30]} differs ONLY on {g}",
                  [k for k in got if got[k] != want[k]], [g])
            check(f"   and {g} is the closure, not the ambience", got[g], FAILED)
        else:
            check(f"{f[:30]} same state vector", got, want)


def test_the_semantic_holes_ride_a_complete_patch_through():
    """
    Each carrier fires NOTHING beyond the ambience a clean patch also produces —
    shadow-run fidelity and totality on provision, both PASS-UNVERIFIED on the
    worked example too.

    Fails in both directions, like its fragment counterpart:

      · if a carrier starts being caught, the hole CLOSED — promote it to a
        witness and say which gate closed it. `27` went that way on
        2026-08-27 and is asserted below as a catch, not deleted.
      · if the file disappears, someone deleted an exposure rather than fixing
        one.
    """
    print("\nthe planted defects ride a well-formed patch straight through")
    from witness import ambient, fired_by
    noise, T = ambient(), load_targets()
    for f, fragment in sorted(WELLFORMED.items()):
        p = os.path.join(REJECTED, f)
        check(f"{f[:30]} retained", os.path.exists(p), True)
        check(f"   its fragment {fragment[:22]} retained",
              os.path.exists(os.path.join(REJECTED, fragment)), True)
        fired, why = fired_by(load_patch(p), T, ignore=noise)
        if f in CLOSED_CARRIERS:
            g = CLOSED_CARRIERS[f]
            check(f"   {g} ALONE refuses {f[:22]}", fired, [g])
            check("   and the refusal teaches",
                  "machine-shaped" in why[g].lower() and "empty" in why[g].lower(), True)
        else:
            check(f"   nothing refuses {f[:26]}", fired, [])


def test_partiality_is_a_self_report_not_a_property():
    """
    PARTIALLY CAUGHT, and the phrasing that catches it is the one no real defect
    produces.

    `totality on provision` refuses `24`'s row the moment a TOP-LEVEL truthy
    `__partial__` is added — i.e. the moment the author annotates their own
    omission. Nothing about the row changes; the confession does. Take it away,
    set it to `false`, or nest it one key down (`29`) and the same partial row
    passes.

    **The gate does not detect partiality. It detects a self-report, and a
    self-report can be absent, false, or in the wrong place.**
    """
    print("\nthe totality gate catches a confession, not a partial row")
    T = load_targets()
    gate = "totality on provision"

    def state_of(patch):
        return {g: (s, d) for s, g, d in validate(patch, T).rows}[gate]

    p = load_patch(os.path.join(REJECTED, "24-silent-partial-WELLFORMED.json"))
    check("as authored, the partial row is not refused", state_of(p)[0], UNVERIFIED)

    for row in p["rows"]:
        if row["target"] == "recovery.or_availability":
            row["value"]["__partial__"] = True
    st, detail = state_of(p)
    check("annotate the SAME row and it is refused", st, FAILED)
    check("   and the refusal names the defect",
          "partial application" in detail and "recovery.or_availability" in detail, True)

    # 29 carries the two phrasings that defeat it
    q = load_patch(os.path.join(REJECTED, "29-partial-bypass-WELLFORMED.json"))
    check("__partial__: false is a BYPASS", state_of(q)[0], UNVERIFIED)
    for row in q["rows"]:
        if row.get("id") == "nl-004-bypass":
            row["value"]["__partial__"] = True
    check("   flip that one marker and the same file is refused", state_of(q)[0], FAILED)


def test_the_signature_gate_refuses_a_machine_and_not_a_person():
    """
    **CLOSED `2026-08-27` — the hole this fork ranked first, and the table that
    keeps the fix from becoming a new hole.**

    Before: every non-empty string turned PASS-UNVERIFIED into GREEN, on a gate
    whose text read *"every row carries a named human"*. It was counting
    non-empty strings, and it was the only defect in the battery that made a
    patch MORE green than an honest draft.

    After: a MACHINE-SHAPED author is FAILED. Three states, and all three are
    asserted here, because a fix that collapsed any two of them would be a
    different defect wearing the costume of a repair —

        ''  '   '      PASS-UNVERIFIED   an honest draft. Unchanged, and it must
                                         not change: AGENTS.md has a machine
                                         leave this empty.
        'system' '-'   FAILED            a manufactured signature.
        'A. Reviewer'  GREEN             present and not machine-shaped. **Not
                                         "a human" — the gate cannot decide
                                         that, and no longer says it does.**

    THE FALSE-POSITIVE HALF IS THE HARD HALF, and it is why `ai`, `bot` and
    `system` match as WHOLE WORDS. `Aisha Botha` and `M. Santos-Systema` are
    exactly the names a substring matcher eats, and **a signature gate that
    cries wolf on a real name is worse than the hole it closes** — the same
    reasoning that deleted the fourth check in `gates/attest.py`. Both are
    asserted GREEN below, and they are the assertions to run first if anyone
    widens the token list.
    """
    print("\nthe signature gate refuses a machine, and never a person")
    T = load_targets()
    base = load_patch(os.path.join(REJECTED, "27-not-a-person-WELLFORMED.json"))

    def signature(author):
        p = json.loads(json.dumps(base))
        for row in p["rows"]:
            row["author"] = author
        return {g: (s, d) for s, g, d in validate(p, T).rows}["signature"]

    for a in ("AI assistant (automated patch generation)", "system", "n/a", "-",
              "automated-pipeline", "LLM", "the harness", "TBD", "none"):
        st, detail = signature(a)
        check(f"author={a[:30]!r} → FAILED", st, FAILED)
        check("   and the refusal teaches",
              "machine-shaped" in detail.lower() and "empty" in detail.lower(), True)

    for a in ("A. Reviewer", "Aisha Botha", "M. Santos-Systema",
              "M. Okonkwo — Quality Director", "Ravi Modelli", "Sgt. Sargent"):
        st, detail = signature(a)
        check(f"author={a[:30]!r} → GREEN", st, GREEN)
        check("   and the gate no longer claims to have verified a human",
              "named human" not in detail.lower() and "attested at mount" in detail.lower(),
              True)

    for a in ("", "   "):
        check(f"author={a!r} → the honest middle state", signature(a)[0], UNVERIFIED)


def test_the_expiry_gate_has_no_clock():
    """
    CONFIRMED OPEN, under every phrasing tried.

    `gates/` and `core/` contain no `date.today`, no `.now(`, no `utcnow`. The
    gate parses the string and compares it to **nothing**, so a row that expired
    in 2019 and a row that expires in the year 9999 are equally acceptable —
    while the field's entire purpose is that *nothing is permanent by default*.

    What it DOES catch is a malformed field, which is a different defect.
    """
    print("\nthe expiry gate checks the FORM of a date and never reads it")
    T = load_targets()
    base = load_patch(os.path.join(REJECTED, "26-expired-on-arrival-WELLFORMED.json"))

    def expiry(value):
        p = json.loads(json.dumps(base))
        p["rows"][0]["expiry"] = value
        return {g: (s, d) for s, g, d in validate(p, T).rows}["expiry"]

    for e in ("2019-01-01", "9999-12-31", "1970-01-01", "2026-08-26"):
        check(f"expiry={e} → GREEN", expiry(e)[0], GREEN)
    st, detail = expiry("when reviewed")
    check("a non-date IS refused — a different defect", st, FAILED)
    check("   and it names it", "is not a date" in detail, True)


def test_the_credential_near_miss_is_not_a_security_check():
    """
    CONFIRMED OPEN — and this is the one where a battery could most easily be
    trusted for something it never did.

    `25`'s row repoints the national allocation system at an arbitrary host,
    ships a live-looking key, and sets `verify_tls: false`. Nothing refuses it.
    Put a DIGIT in the key and `divergence` does refuse the file — **on the
    digit, as an unaccounted quantity.** That is tokenisation noise, not a
    security check, and the refusal names an arithmetic complaint rather than
    the defect. Mistaking one for the other is how a battery acquires a
    reputation it has not earned.
    """
    print("\nthe credentials row is refused only by accident, and for the wrong reason")
    T = load_targets()
    p = load_patch(os.path.join(REJECTED, "25-credentials-WELLFORMED.json"))
    d0 = {g: (s, d) for s, g, d in validate(p, T).rows}["divergence"]
    check("as authored, divergence is GREEN", d0[0], GREEN)

    for row in p["rows"]:
        if row["target"] == "allocation.credentials":
            row["value"]["api_key"] = "sk-live-8f2b1"
    st, detail = {g: (s, d) for s, g, d in validate(p, T).rows}["divergence"]
    check("one digit in the key and it FAILS", st, FAILED)
    check("   but the refusal is about a QUANTITY, not a credential",
          "8.0" in detail and "endpoint" not in detail and "tls" not in detail.lower(), True)


def test_every_wellformed_carrier_explains_itself():
    """
    A carrier nobody can read is a carrier nobody will act on.

    And a carrier whose label has gone stale is worse than one nobody reads:
    `27` closed, so it must no longer call itself an open exposure. **A caught
    fixture still labelled UNCAUGHT is a standing lie about coverage** — the
    same rule the fragment test applies, applied here.
    """
    print("\nand each carrier says what it is, and what it is a carrier OF")
    for f, fragment in sorted(WELLFORMED.items()):
        with open(os.path.join(REJECTED, f), encoding="utf-8") as fh:
            doc = json.load(fh)
        check(f"{f[:30]} says FICTIONAL", "FICTIONAL" in doc.get("$comment", ""), True)
        if f in CLOSED_CARRIERS:
            check(f"{f[:30]} declares itself CLOSED",
                  doc.get("$status", "").startswith("CLOSED"), True)
            check(f"{f[:30]} names the gate it witnesses",
                  CLOSED_CARRIERS[f] in doc.get("$witnesses", ""), True)
            check(f"{f[:30]} says what the fix does NOT close",
                  "does not close" in doc.get("$comment", "").lower()
                  and "plausible human name" in doc.get("$comment", "").lower(), True)
        else:
            check(f"{f[:30]} declares UNCAUGHT-WELLFORMED",
                  "UNCAUGHT-WELLFORMED" in doc.get("$status", ""), True)
        check(f"{f[:30]} names its finder",
              doc.get("$found_by", "").startswith("fork/witnesses"), True)
        check(f"{f[:30]} names its fragment", doc.get("$carrier_of"), fragment)


def test_coverage_is_reported_not_asserted():
    """The battery's own coverage is a number this repository must print, not a
    property it may assume."""
    print("\ncoverage is measured")
    per_gate, _ = matrix()
    states = [i["state"] for i in per_gate.values()]
    check("sixteen gates", len(per_gate), 16)   # 14 schema, 15 accountability, 16 attest
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
              test_wellformed_carriers_are_not_fragments,
              test_wellformed_carriers_are_indistinguishable_from_the_accepted_patch,
              test_the_semantic_holes_ride_a_complete_patch_through,
              test_partiality_is_a_self_report_not_a_property,
              test_the_signature_gate_refuses_a_machine_and_not_a_person,
              test_the_expiry_gate_has_no_clock,
              test_the_credential_near_miss_is_not_a_security_check,
              test_every_wellformed_carrier_explains_itself,
              test_coverage_is_reported_not_asserted):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
