#!/usr/bin/env python3
"""
REGISTRAR · F-BATTERY-STRENGTH · mutation testing for the gate battery

**The repository's own top-ranked risk is a weak battery, and the battery has
never been measured.**

`SPEC.md` §14 and the page's counterweights both say it: *the central risk is not
a wrong patch — it is a weak battery*, because a foreign harness produces
confident, plausible, wrong work and the gates are all that stands between that
and an organisation where wrong loses an organ.

What exists today is seven `*-UNCAUGHT.json` fixtures, and `conformance/run.py`
reports them with unusual honesty — *7 hole(s) no SEMANTIC gate catches, retained
deliberately (7 also trip a floor gate for being minimal — that is not closure)*.

**But those seven were found by hand, by the people who wrote the gates.** That
method finds the holes someone could imagine. It cannot estimate the ones nobody
thought of, and — the part that matters — **it produces no denominator.** A
battery with seven known holes and an unknown total is not a measured battery.

F-PATCH-DELTA inherits the problem directly. `S = 0.57` was graded BY this
battery. A grader of unmeasured strength leaves the score's meaning unmeasured
too: a pass could mean the harness did well, or that the battery is easy, and
nothing on the plate distinguishes those.

WHAT THIS DOES

Mutation testing, the standard instrument for exactly this question. Take the
worked patch — which the battery accepts — introduce one **named defect** at a
time, and re-run the gates. A mutant the battery FAILS is *killed*. A mutant it
accepts *survived*, and every survivor is a defect this repository would mount.

    python experiments/F-BATTERY-STRENGTH/mutate.py            summary
    python experiments/F-BATTERY-STRENGTH/mutate.py --survivors  each one, in full
    python experiments/F-BATTERY-STRENGTH/mutate.py --json       machine-readable

HONESTY CONSTRAINTS, because a mutation score is easy to inflate

  1 · **Every mutant states its defect in words.** If the defect cannot be
      stated, the mutation is not a defect — it is an *equivalent mutant*, and
      counting it as a hole would inflate the score in the flattering direction.
      Operators here were written defect-first: the sentence came before the code.

  2 · **The kill criterion is FAILED, never PASS-UNVERIFIED.** Three gates report
      PASS-UNVERIFIED because they cannot be decided from a file. Counting those
      as kills is precisely the three-states-collapsed-into-two failure this
      repository has a gate against. A mutant that only trips an undecidable gate
      has NOT been caught.

  3 · **Deterministic.** No RNG. Same input, same mutants, same verdicts — the
      replay-determinism discipline applies to instruments too.

  4 · **A survivor is a CANDIDATE hole, not a confirmed one.** Some survivors will
      be equivalent mutants that slipped constraint 1. They are printed in full so
      a human can judge, never silently counted as findings.

  [NULL] — the seven hand-found fixtures. If mutation surfaces nothing they did
  not already cover, the hand method was sufficient, that is a real result, and
  this experiment prints its own funeral.

Zero dependencies. Reads only; writes nothing.
"""

from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "gates"))

from validate_patch import FAILED, load_patch, load_targets, validate  # noqa: E402

PATCH = os.path.join(ROOT, "examples", "worked", "northlake.patch.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ── mutation operators ──────────────────────────────────────────────────────
# Each yields (defect_in_words, mutated_patch). The sentence is written FIRST;
# if a mutation cannot carry one, it does not belong here (constraint 1).

def _rows(p):
    return p.get("rows") or []


def op_evidence_strip(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["evidence"] = []
        yield (f"row {row['id']} asserts local practice with NO cited source", m)


def op_evidence_unrelated(p):
    for i, row in enumerate(_rows(p)):
        if not row.get("evidence"):
            continue
        m = copy.deepcopy(p)
        for e in m["rows"][i]["evidence"]:
            e["says"] = "the cafeteria closes at eight on weekends"
        yield (f"row {row['id']} cites sources that do not say what it claims", m)


def op_shadow_strip(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["shadow_run"] = {}
        yield (f"row {row['id']} was never replayed against site history", m)


def op_shadow_zero(p):
    for i, row in enumerate(_rows(p)):
        if not isinstance(row.get("shadow_run"), dict):
            continue
        m = copy.deepcopy(p)
        m["rows"][i]["shadow_run"]["cases"] = 0
        yield (f"row {row['id']} claims a replay over ZERO cases", m)


def op_shadow_over_unity(p):
    for i, row in enumerate(_rows(p)):
        sr = row.get("shadow_run")
        if not isinstance(sr, dict) or "cases" not in sr:
            continue
        m = copy.deepcopy(p)
        m["rows"][i]["shadow_run"]["would_have_matched"] = int(sr["cases"]) + 40
        yield (f"row {row['id']} matched MORE cases than it replayed", m)


def op_shadow_inflate(p):
    """The quiet one: a plausible but false denominator."""
    for i, row in enumerate(_rows(p)):
        sr = row.get("shadow_run")
        if not isinstance(sr, dict) or "cases" not in sr:
            continue
        m = copy.deepcopy(p)
        m["rows"][i]["shadow_run"]["cases"] = int(sr["cases"]) * 7
        yield (f"row {row['id']} inflates its denominator 7x — the ratio now lies", m)


def op_inverse_identity(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["inverse"] = row.get("value")
        yield (f"row {row['id']} inverse equals its value — there is no way back", m)


def op_inverse_fabricate(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["inverse"] = "prior_value_nothing_established"
        yield (f"row {row['id']} inverse names a state nothing established", m)


def op_expiry_past(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["expiry"] = "2020-01-01"
        yield (f"row {row['id']} is expired on arrival", m)


def op_expiry_strip(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i].pop("expiry", None)
        yield (f"row {row['id']} is permanent by default", m)


def op_author_machine(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["author"] = "automated completion agent v2"
        yield (f"row {row['id']} was SIGNED BY A MACHINE", m)


def op_target_undeclared(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["target"] = "workflow.invented_variation_point"
        yield (f"row {row['id']} targets a point the seed never declared", m)


def op_target_reaches_l0(p):
    for i, row in enumerate(_rows(p)):
        m = copy.deepcopy(p)
        m["rows"][i]["target"] = "core.lifecycle.referral.required_elements"
        yield (f"row {row['id']} reaches into L0 — federal law", m)


def op_weasel(p):
    for i, row in enumerate(_rows(p)):
        if not row.get("evidence"):
            continue
        m = copy.deepcopy(p)
        m["rows"][i]["evidence"][0]["says"] = (
            "standard practice at most OPOs; typically the supervisor owns this"
        )
        yield (f"row {row['id']} substitutes industry generality for site evidence", m)


def op_value_contradicts_evidence(p):
    for i, row in enumerate(_rows(p)):
        if not isinstance(row.get("value"), str):
            continue
        m = copy.deepcopy(p)
        m["rows"][i]["value"] = "night_shift_registrar"
        yield (f"row {row['id']} states a value its own evidence contradicts", m)


def op_numeric_round_down(p):
    """Optimism computes deadlines wrong in the direction that loses organs."""
    for i, row in enumerate(_rows(p)):
        v = row.get("value")
        if not isinstance(v, dict):
            continue
        for k, n in v.items():
            if isinstance(n, (int, float)) and not isinstance(n, bool) and n > 10:
                m = copy.deepcopy(p)
                m["rows"][i]["value"][k] = type(n)(n * 0.6)
                yield (f"row {row['id']}.{k} rounded DOWN 40% — optimistic deadline", m)
                break


def op_duplicate_conflict(p):
    rows = _rows(p)
    if not rows:
        return
    m = copy.deepcopy(p)
    dup = copy.deepcopy(rows[0])
    dup["id"] = dup["id"] + "-dup"
    dup["value"] = "a_different_answer_entirely"
    m["rows"].append(dup)
    yield (f"two rows set {rows[0]['target']} to different values", m)


def op_holds_strip(p):
    if not p.get("holds"):
        return
    m = copy.deepcopy(p)
    m["holds"] = []
    yield ("every declined target went silent — accountability erased", m)


def op_hold_without_reason(p):
    if not p.get("holds"):
        return
    m = copy.deepcopy(p)
    for h in m["holds"]:
        h.pop("searched", None)
        h.pop("reason", None)
    yield ("holds declare no search and no reason — an unfalsifiable decline", m)


OPERATORS = [
    ("evidence-strip", op_evidence_strip),
    ("evidence-unrelated", op_evidence_unrelated),
    ("shadow-strip", op_shadow_strip),
    ("shadow-zero", op_shadow_zero),
    ("shadow-over-unity", op_shadow_over_unity),
    ("shadow-inflate", op_shadow_inflate),
    ("inverse-identity", op_inverse_identity),
    ("inverse-fabricate", op_inverse_fabricate),
    ("expiry-past", op_expiry_past),
    ("expiry-strip", op_expiry_strip),
    ("author-machine", op_author_machine),
    ("target-undeclared", op_target_undeclared),
    ("target-reaches-l0", op_target_reaches_l0),
    ("weasel", op_weasel),
    ("value-contradicts", op_value_contradicts_evidence),
    ("numeric-round-down", op_numeric_round_down),
    ("duplicate-conflict", op_duplicate_conflict),
    ("holds-strip", op_holds_strip),
    ("hold-no-reason", op_hold_without_reason),
]


# ── the run ─────────────────────────────────────────────────────────────────
def run():
    base = load_patch(PATCH)
    targets = load_targets()

    baseline = validate(base, targets)
    if baseline.worst == FAILED:
        print("BASELINE FAILS. The worked example is not accepted by the battery;")
        print("mutation scoring is meaningless until that is fixed.")
        print(baseline.render())
        raise SystemExit(2)

    results = []
    for op_name, fn in OPERATORS:
        for defect, mutant in fn(base):
            try:
                r = validate(mutant, targets)
                failed_by = [g for s, g, _ in r.rows if s == FAILED]
            except Exception as exc:                       # a crash is not a kill
                results.append({"operator": op_name, "defect": defect,
                                "verdict": "ERROR", "killed_by": [],
                                "detail": f"{type(exc).__name__}: {exc}"})
                continue
            results.append({
                "operator": op_name, "defect": defect,
                "verdict": "KILLED" if failed_by else "SURVIVED",
                "killed_by": failed_by,
                "detail": "",
            })
    return baseline, results


def main(argv):
    baseline, results = run()
    total = len(results)
    killed = [r for r in results if r["verdict"] == "KILLED"]
    survived = [r for r in results if r["verdict"] == "SURVIVED"]
    errored = [r for r in results if r["verdict"] == "ERROR"]

    if "--json" in argv:
        print(json.dumps({"total": total, "killed": len(killed),
                          "survived": len(survived), "errored": len(errored),
                          "results": results}, indent=2))
        return 0

    print("F-BATTERY-STRENGTH · mutation score for the gate battery\n")
    print(f"  baseline (the worked example)   {baseline.worst}")
    print(f"  mutants generated               {total}")
    print(f"  KILLED   (a gate FAILED)        {len(killed)}")
    print(f"  SURVIVED (battery accepted it)  {len(survived)}")
    if errored:
        print(f"  ERRORED  (crash, not a kill)    {len(errored)}")
    score = (len(killed) / total * 100) if total else 0.0
    print(f"\n  mutation score                  {score:.1f}%  "
          f"({len(killed)}/{total}) — grain: one named defect per mutant")

    print("\n  by operator")
    for op_name, _ in OPERATORS:
        rs = [r for r in results if r["operator"] == op_name]
        if not rs:
            continue
        k = sum(1 for r in rs if r["verdict"] == "KILLED")
        mark = "  " if k == len(rs) else ("**" if k == 0 else " ~")
        print(f"  {mark} {op_name:<22} {k}/{len(rs)} killed")

    if survived:
        print(f"\n  ** {len(survived)} SURVIVOR(S) — defects this battery would mount **")
        seen = set()
        for r in survived:
            if r["operator"] in seen and "--survivors" not in argv:
                continue
            seen.add(r["operator"])
            print(f"     [{r['operator']}] {r['defect']}")
        if "--survivors" not in argv and len(survived) > len(seen):
            print(f"     … --survivors for all {len(survived)}")
        print("\n  A survivor is a CANDIDATE hole. Some may be equivalent mutants —")
        print("  judge each before it becomes a fixture. Counting them unread would")
        print("  be the same error as counting PASS-UNVERIFIED as a pass.")
    else:
        print("\n  No survivors. The battery killed every named defect —")
        print("  and the hand-written fixture set was sufficient. Print the funeral.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
