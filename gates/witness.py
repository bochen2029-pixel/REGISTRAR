#!/usr/bin/env python3
"""
REGISTRAR · gates · witness coverage
─────────────────────────────────────────────────────────────────────────────
**Which gates have evidence they can fire, and which are only asserted?**

`SPEC.md` §14 ranks the risks and puts this first:

> The central risk is not a wrong patch. It is a **weak battery**. A foreign
> harness produces confident, plausible, wrong work all day, and the gates are
> the only thing between that and an organisation where wrong loses an organ.

A gate with no adversarial fixture is a gate nobody has watched refuse
anything. It may work. Nothing shows that it does.

WHAT COUNTS AS A WITNESS, AND WHY THE DEFINITION IS STRICT

A witness is a fixture that fires **exactly one** gate. That is not fussiness:

    A fixture that trips three gates proves that SOMETHING refused it. It does
    not prove WHICH — and if one of those three silently stopped working, the
    fixture would still fail, still be green, and still tell you nothing.

So this tool separates three states, and the middle one is the interesting one:

    WITNESSED     a fixture fires this gate ALONE — unambiguous evidence
    INCIDENTAL    a fixture fires it, but fires other gates too. The gate is
                  exercised; it is not isolated. **A regression here hides.**
    UNWITNESSED   nothing in the corpus fires it. It has never been seen to
                  refuse anything.

    UNDECIDABLE   the gate cannot be decided from a file at all and reports
                  PASS-UNVERIFIED by design. Not a gap — honest.

    python gates/witness.py            the matrix
    python gates/witness.py --check    non-zero if any gate is unwitnessed

Zero dependencies.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from validate_patch import (  # noqa: E402
    FAILED, GREEN, UNVERIFIED, load_patch, load_targets, validate,
)

REJECTED = os.path.join(ROOT, "examples", "worked", "rejected")
WORKED = os.path.join(ROOT, "examples", "worked", "northlake.patch.json")

WITNESSED, INCIDENTAL, UNWITNESSED, UNDECIDABLE = (
    "WITNESSED", "INCIDENTAL", "UNWITNESSED", "UNDECIDABLE")

# STRUCTURAL FLOORS — gates that answer "is this a well-formed patch at all",
# beneath every semantic gate rather than beside them.
#
# A floor fires under any malformation that also violates the contract's shape,
# so counting it as a peer entangles otherwise-clean witnesses wholesale. It is
# excluded from the isolation measurement for the same reason "the JSON parsed"
# is not counted as a gate.
#
# `schema conformance` landed 2026-08-26, after nothing in the tree had ever
# validated against `patch.schema.json` — which is why two defects sat in that
# schema undetected until an independent completion run reported them.
FLOOR = {"schema conformance"}

# Gates that CANNOT be isolated, and why. Recording this is not an excuse — it
# is the finding. A fixture author who does not know these will chase an
# impossible fixture, and a reader who does not know them will read "incidental"
# as sloppiness rather than structure.
ENTANGLED = {
    "target syntax": (
        "blast radius always fires alongside: a syntactically malformed target is "
        "BY DEFINITION not a declared target, so it can never be isolated. The "
        "syntax gate earns its place by TEACHING rather than catching — 'your "
        "target has capital letters' is actionable where 'that target does not "
        "exist' is not."),
    "inverse declared": (
        "schema shape always fires alongside: the gate fires only when the "
        "`inverse` KEY IS ABSENT, and an absent required field trips schema "
        "shape first. Verified, not assumed. `10-no-way-back` witnesses the "
        "adjacent and isolable defect — an inverse that is PRESENT and wrong — "
        "which is the failure a harness is far likelier to produce."),
    "L0/L1/L4 immutability": (
        "UNREACHABLE from any patch file. It fires only when a target is DECLARED "
        "and its layer is not L2/L3 — but every entry in targets.json is lifted "
        "from a local_variation, and all twenty are L2/L3. It is a SEED invariant "
        "living in a patch validator. Witnessed by a synthetic-targets test "
        "instead; see test_witness.py."),
}


def all_gates() -> list[str]:
    """The gate names, in the order the validator emits them."""
    r = validate(load_patch(WORKED), load_targets())
    return [g for _, g, _ in r.rows]


def half_decidable() -> set[str]:
    """
    Gates that report PASS-UNVERIFIED on a patch with nothing wrong with it.

    **They are not therefore undecidable.** A gate can be undecidable in the
    AFFIRMATIVE and perfectly decidable in the NEGATIVE:

        `totality on provision` cannot confirm that application installs every
        declared key — that needs a runtime. It can absolutely catch a row that
        installs only some of them, and `04-partial` proves it does.

    So this returns the gates that cannot *confirm*, and the caller must still
    check whether anything makes them *refuse*. Conflating the two would have
    written off a gate that has a clean witness — which is what the first
    version of this tool did, on its first run.
    """
    r = validate(load_patch(WORKED), load_targets())
    return {g for s, g, _ in r.rows if s == UNVERIFIED}


def fixtures() -> dict[str, dict]:
    out = {}
    if not os.path.isdir(REJECTED):
        return out
    for fn in sorted(os.listdir(REJECTED)):
        if fn.endswith((".json", ".yml", ".yaml")):
            out[fn] = load_patch(os.path.join(REJECTED, fn))
    return out


# Gates that report PASS-UNVERIFIED on EVERY patch, good or bad. They are
# background noise in this matrix — a fixture cannot be said to have witnessed
# them, because they say the same thing regardless of what it contains.
def ambient() -> dict[str, str]:
    """
    What each gate says about a patch with nothing wrong with it.

    Returned as gate -> state, not a bare set, because **suppression has to
    compare states.** `totality on provision` is PASS-UNVERIFIED on every clean
    patch — ambient noise — and FAILED on `04-partial`, which is a real
    refusal. Subtracting the gate by NAME erased that witness; subtracting it
    only when the state MATCHES keeps it.
    """
    r = validate(load_patch(WORKED), load_targets())
    return {g: st for st, g, _ in r.rows if st != GREEN}


def fired_by(patch: dict, targets: dict,
             ignore: dict[str, str] | None = None) -> tuple[list[str], dict[str, str]]:
    """
    Which gates left GREEN on this patch, and what each said.

    **Not only the ones that FAILED.** A gate's correct refusal is sometimes the
    MIDDLE state: `signature` reports PASS-UNVERIFIED for an unsigned row,
    because `AGENTS.md` has a machine leave `author` empty and the signature is
    the output commit — so unsigned is *not yet*, never *wrong*. A gate that
    FAILED there would refuse the very artifact a harness is meant to produce.

    Counting only FAILED made the first version of this tool report an unsigned
    fixture as **silent**, when the gate had refused it correctly.
    """
    ignore = ignore or {}
    r = validate(patch, targets)
    # a gate counts as refusing only if it says something DIFFERENT here than it
    # says about a clean patch
    out = [(g, st, d) for st, g, d in r.rows
           if st != GREEN and ignore.get(g) != st]
    return [g for g, _, _ in out], {g: f"{st}: {d}" for g, st, d in out}


def matrix() -> tuple[dict[str, dict], dict[str, list[str]]]:
    """(gate -> {state, by, incidental_by}, fixture -> gates it fires)"""
    targets = load_targets()
    gates = all_gates()
    undec = half_decidable()
    noise = ambient()

    per_fixture: dict[str, list[str]] = {}
    for name, patch in fixtures().items():
        fired, _ = fired_by(patch, targets, ignore=noise)
        per_fixture[name] = fired

    per_gate: dict[str, dict] = {}
    for g in gates:
        # "Isolated by f" means: f fires g, and f fires no OTHER SEMANTIC gate.
        #
        # A STRUCTURAL FLOOR does not count as "another gate" — unless g IS the
        # floor, in which case it is judged like anything else. `schema
        # conformance` (gate 14, 2026-08-26) fires under any malformation that
        # also violates the contract's shape: `cases: 0` trips both it and the
        # shadow-run gate; a missing `value` trips both it and schema shape.
        # Counted as a peer, it entangled three cleanly-witnessed gates at a
        # stroke; erased entirely, it could never be witnessed itself. Excluding
        # it only from OTHER gates' isolation is what makes both true at once.
        def _others(fired: list[str], g: str = g) -> list[str]:
            return [x for x in fired if x != g and x not in FLOOR]

        alone = [f for f, fired in per_fixture.items() if g in fired and not _others(fired)]
        among = [f for f, fired in per_fixture.items() if g in fired and _others(fired)]
        # Evidence first, decidability second. A gate that refuses something is
        # witnessed even if it cannot confirm — see half_decidable().
        if alone:
            state = WITNESSED
        elif among:
            state = INCIDENTAL
        elif g in undec:
            state = UNDECIDABLE
        else:
            state = UNWITNESSED
        per_gate[g] = {"state": state, "by": alone, "incidental_by": among,
                       "cannot_confirm": g in undec}

    return per_gate, per_fixture


def report() -> int:
    per_gate, per_fixture = matrix()

    print("REGISTRAR · gates · witness coverage\n")
    print("A witness is a fixture that fires EXACTLY ONE gate. A fixture firing several")
    print("proves something refused the patch — not which thing, and a regression hides there.\n")

    width = max(len(g) for g in per_gate)
    for g, info in per_gate.items():
        st = info["state"]
        mark = {WITNESSED: "ok    ", INCIDENTAL: "weak  ",
                UNWITNESSED: "NONE  ", UNDECIDABLE: "n/a   "}[st]
        who = (", ".join(info["by"]) if info["by"]
               else ", ".join(info["incidental_by"]) if info["incidental_by"]
               else "")
        note = {
            WITNESSED: who + ("  (refuses, but cannot confirm)" if info["cannot_confirm"] else ""),
            INCIDENTAL: (f"entangled by construction — {who}" if g in ENTANGLED
                         else f"only alongside others — {who}"),
            UNWITNESSED: ("unreachable from a patch — see ENTANGLED" if g in ENTANGLED
                          else "no fixture has ever made this gate refuse anything"),
            UNDECIDABLE: "cannot confirm AND nothing makes it refuse — needs a runtime or the tape",
        }[st]
        print(f"  {mark}{g:<{width}}  {note}")

    print("\nfixtures, and how many gates each fires:")
    for f, fired in per_fixture.items():
        n = len(fired)
        tag = "clean" if n == 1 else ("silent!" if n == 0 else f"{n} gates — ambiguous")
        print(f"  {f:<24} {tag}")
        if n > 1:
            print(f"      {', '.join(fired)}")

    counts = {k: sum(1 for i in per_gate.values() if i["state"] == k)
              for k in (WITNESSED, INCIDENTAL, UNWITNESSED, UNDECIDABLE)}
    total = len(per_gate)
    print(f"\n{total} gates · {counts[WITNESSED]} witnessed · {counts[INCIDENTAL]} incidental · "
          f"{counts[UNWITNESSED]} unwitnessed · {counts[UNDECIDABLE]} undecidable")

    real_gaps = [g for g, i in per_gate.items()
                 if i["state"] == UNWITNESSED and g not in ENTANGLED]
    structural = [g for g, i in per_gate.items()
                  if i["state"] in (UNWITNESSED, INCIDENTAL) and g in ENTANGLED]

    if real_gaps:
        print(f"\n{len(real_gaps)} gate(s) have NEVER been seen to refuse anything: "
              f"{', '.join(real_gaps)}")
        print("  That is the repository's own first-ranked risk, sitting in the open.")
    if structural:
        print(f"\n{len(structural)} gate(s) cannot be isolated BY CONSTRUCTION, and each says why:")
        for g in structural:
            print(f"    {g} — {ENTANGLED[g].split('.')[0]}.")
    weak = [g for g, i in per_gate.items()
            if i["state"] == INCIDENTAL and g not in ENTANGLED]
    if weak:
        print(f"\n{len(weak)} gate(s) fire only alongside others: {', '.join(weak)}")
        print("  If one stopped working, its fixture would still fail and still look green.")

    return 1 if real_gaps else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(report())
    raise SystemExit(report())
