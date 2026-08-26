#!/usr/bin/env python3
"""
REGISTRAR · gates · divergence tests

    python gates/test_divergence.py

**A gate is only worth its refusals**, so most of these are refusals. The two
that assert acceptance are the more delicate ones: a gate that cries wolf is
worse than no gate, because the next real alarm gets discounted.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from divergence import FAILED, GREEN, UNVERIFIED, numbers_in, numbers_of, validate  # noqa: E402

PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def row(**kw):
    base = {"target": "x.y", "value": {"m": 10},
            "evidence": [{"source": "s", "says": "10 minutes"}],
            "shadow_run": {"cases": 10, "would_have_matched": 10, "would_have_missed": 0}}
    base.update(kw)
    return {"rows": [base]}


# ── what it must refuse ─────────────────────────────────────────────────────
def test_refuses_contradiction():
    print("\nrefuses a value its evidence contradicts")
    st, msgs = validate(row(value={"m": 90},
                            evidence=[{"source": "s", "says": "the threshold is 240 minutes"}]))
    check("a value below its cited figure FAILS", st, FAILED)
    check("and names the direction", any("BELOW" in m or "optimis" in m for m in msgs), True)


def test_refuses_optimistic_rounding():
    """
    Rounding DOWN from the evidence is the dangerous direction: it computes
    deadlines that are wrong in the way that loses organs.
    """
    print("\nrefuses optimistic rounding")
    st, _ = validate(row(value={"turnaround_minutes": 240},
                         evidence=[{"source": "tape", "says": "observed p75 was 364 minutes"}],
                         shadow_run={"cases": 402, "would_have_matched": 402, "would_have_missed": 0}))
    check("240 against an observed 364 FAILS", st, FAILED)


def test_refuses_arithmetic_that_does_not_close():
    print("\nrefuses a shadow run whose arithmetic does not hold")
    st, msgs = validate(row(shadow_run={"cases": 100, "would_have_matched": 80, "would_have_missed": 5}))
    check("80 + 5 != 100 FAILS", st, FAILED)
    check("and says so", any("do not close" in m for m in msgs), True)

    st2, _ = validate(row(shadow_run={"cases": 10, "would_have_matched": 40}))
    check("a numerator above its denominator FAILS", st2, FAILED)


def test_refuses_empty_replay():
    print("\nrefuses a replay over nothing")
    st, msgs = validate(row(shadow_run={"cases": 0, "would_have_matched": 0}))
    check("zero cases FAILS", st, FAILED)
    check("and names it", any("not a replay" in m for m in msgs), True)


def test_refuses_rubber_stamp_derivation():
    """
    `derived_from` exists so a legitimately computed figure can pass. The risk
    is that it becomes a formality — so a declaration naming no method fails.
    """
    print("\nrefuses a derivation that names no method")
    st, msgs = validate(row(value={"m": 999}, derived_from="computed",
                            evidence=[{"source": "s", "says": "observed 12 minutes"}]))
    check("'computed' FAILS", st, FAILED)
    check("and says why", any("formality" in m for m in msgs), True)

    st2, _ = validate(row(value={"m": 999}, derived_from="p90 of the observed distribution, rounded up",
                          evidence=[{"source": "s", "says": "observed 12 minutes"}]))
    check("a named method passes", st2, GREEN)


def test_flags_population_mismatch():
    print("\nflags a replay run on a different population")
    st, msgs = validate(row(evidence=[{"source": "tape n=402", "says": "p75 was 10 minutes"}],
                            shadow_run={"cases": 311, "would_have_matched": 300, "would_have_missed": 11}))
    check("n=402 vs 311 cases is UNVERIFIED", st, UNVERIFIED)
    check("and names both", any("402" in m and "311" in m for m in msgs), True)


# ── what it must NOT refuse ─────────────────────────────────────────────────
def test_accepts_conservative_rounding():
    """
    THE DELICATE ONE. This repository's own rule is to round UP — *use p75 or
    higher, and p90 where the figure feeds a latest safe start.* A gate that
    flagged that would be punishing the rule being followed.
    """
    print("\naccepts conservative rounding — the house rule")
    st, _ = validate(row(value={"or_scheduled_to_incision_minutes": 120},
                         evidence=[{"source": "tape", "says": "p75 elapsed was 118 minutes; longest was 186"}],
                         shadow_run={"cases": 57, "would_have_matched": 43, "would_have_missed": 14}))
    check("120 from a p75 of 118 passes", st, GREEN)

    st2, _ = validate(row(value={"budget_minutes": 180},
                          evidence=[{"source": "tape", "says": "p90 elapsed was 174 minutes"}],
                          shadow_run={"cases": 88, "would_have_matched": 79, "would_have_missed": 9}))
    check("180 from a p90 of 174 passes", st2, GREEN)


def test_identifiers_are_not_assertions():
    """A hospital number is not a measurement, and demanding evidence for it
    would be the gate being wrong rather than the row."""
    print("\nidentifiers are not assertions")
    check("a hospital id is not a quantity", numbers_of({"hospital": "1147"}), set())
    check("nor a clock window", numbers_of({"cross_clamp_window": {"opens": "06:00"}}), set())
    check("but a duration is", numbers_of({"turnaround_minutes": 360}), {360.0})


def test_prose_units():
    """Evidence is prose. 'four hours' and '240 minutes' are the same figure."""
    print("\nprose says four hours, not 240 minutes")
    check("four hours reads as 240", 240.0 in numbers_in("reviewed after four hours"), True)
    check("6h04m reads as 364", 364.0 in numbers_in("observed p75 was 6h04m"), True)
    check("4 hours reads as 240", 240.0 in numbers_in("contracted turnaround is 4 hours"), True)


def test_conservative_anchors_on_durations():
    """
    REGRESSION, from an adversarial sweep on 2026-08-26.

    The `conservative` branch accepted any value within +25% of ANY number in
    the evidence prose — and `numbers_in` is undifferentiated, so a sample size,
    a case count and a YEAR sat in the same set as the measurement. For

        "across 402 resulted panels in 2025 the observed p75 was 6h04m"

    the anchors were {6, 360, 364, 402, 2025}. Since evidence prose almost
    always carries an `n`, most arbitrary durations could be licensed by the
    sample size of the study that fails to support them — and a year licensed
    anything up to 2531.
    """
    print("\nconservative rounding anchors on durations, not on any stray number")
    from divergence import durations_in, numbers_in
    ev = "across 402 resulted panels in 2025 the observed p75 was 6h04m"
    check("the old anchor set contained the sample size", 402.0 in numbers_in(ev), True)
    check("and the year", 2025.0 in numbers_in(ev), True)
    check("durations_in admits neither", {402.0, 2025.0} & durations_in(ev), set())
    check("but keeps the measurement", 364.0 in durations_in(ev), True)

    # a duration nowhere near any duration in the evidence must FAIL,
    # even when a sample size would once have licensed it
    st, _ = validate(row(target="evaluation.reference_lab",
                         value={"lab": "nl", "turnaround_minutes": 500},
                         evidence=[{"source": "tape",
                                    "says": "across 402 resulted panels the observed p75 was 60 minutes"}],
                         shadow_run={"cases": 402, "would_have_matched": 402,
                                     "would_have_missed": 0}))
    check("500 minutes against a p75 of 60 FAILS", st, FAILED)

    # and the house rule still passes
    st2, _ = validate(row(value={"or_scheduled_to_incision_minutes": 120},
                          evidence=[{"source": "tape", "says": "p75 elapsed was 118 minutes"}],
                          shadow_run={"cases": 57, "would_have_matched": 43,
                                      "would_have_missed": 14}))
    check("120 from a p75 of 118 minutes still passes", st2, GREEN)


def test_the_worked_example_passes():
    """
    The shipped example must pass its own gate. It did not, on the first three
    runs — and each finding was the GATE being wrong, not the rows: identifiers
    treated as claims, conservative rounding treated as divergence, and a
    spelled-out quantity unread.
    """
    print("\nthe worked example passes its own gate")
    with open(os.path.join(ROOT, "examples", "worked", "northlake.patch.json"),
              encoding="utf-8") as fh:
        patch = json.load(fh)
    st, msgs = validate(patch)
    check("GREEN", st, GREEN)
    check("with nothing to report", msgs, [])


def test_the_rejected_drafts():
    """The adversarial corpus must still be refused — by some gate, and this
    one adds a reason where it has one."""
    print("\nthe rejected drafts")
    d = os.path.join(ROOT, "examples", "worked", "rejected")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as fh:
            st, msgs = validate(json.load(fh))
        print(f"        {fn:<26} {st}" + (f"  {msgs[0][:60]}" if msgs else ""))
    check("02-ungrounded is caught by divergence too",
          validate(json.load(open(os.path.join(d, "02-ungrounded.json"), encoding="utf-8")))[0]
          in (FAILED, UNVERIFIED), True)


if __name__ == "__main__":
    print("REGISTRAR · gates · divergence")
    for t in (test_refuses_contradiction, test_refuses_optimistic_rounding,
              test_refuses_arithmetic_that_does_not_close, test_refuses_empty_replay,
              test_refuses_rubber_stamp_derivation, test_flags_population_mismatch,
              test_accepts_conservative_rounding, test_conservative_anchors_on_durations,
              test_identifiers_are_not_assertions,
              test_prose_units, test_the_worked_example_passes, test_the_rejected_drafts):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
