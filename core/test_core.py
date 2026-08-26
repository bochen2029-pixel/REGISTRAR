#!/usr/bin/env python3
"""
REGISTRAR · core · tests

    python core/test_core.py

The tape's value is entirely in what it refuses to let you do, so most of these
assert absences rather than behaviours.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from case import ENFORCED, PENDING, load_machine, replay  # noqa: E402
from tape import GENESIS, Tape, TamperEvident, state_at, timeline  # noqa: E402

TAPES = os.path.join(ROOT, "fixtures", "tapes")
PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name); print(f"  ok    {name}")
    else:
        FAIL.append(name); print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


# ─────────────────────────────────────────────────────────────────────────────
def test_append_only_by_type():
    """
    The central claim of L4: delete and update are ABSENT FROM THE INTERFACE,
    not forbidden by a policy someone can relax at 3 a.m. If any of these ever
    appear, the record has stopped being a record.
    """
    print("\nappend-only is a type, not a rule")
    for name in ("delete", "update", "remove", "truncate", "pop", "clear", "__setitem__", "__delitem__"):
        check(f"Tape has no .{name}", hasattr(Tape, name), False)


def test_chain():
    print("\nhash chain")
    t = Tape("T")
    check("empty head is genesis", t.head, GENESIS)
    e1 = t.append("transition", 0, {"to": "referral_triaged"})
    e2 = t.append("transition", 10, {"to": "evaluation"})
    check("first entry links to genesis", e1.prev, GENESIS)
    check("second links to the first", e2.prev, e1.digest)
    check("head is the last digest", t.head, e2.digest)
    check("chain verifies", t.intact, True)

    # identical content in a different tape produces identical digests
    u = Tape("T")
    u.append("transition", 0, {"to": "referral_triaged"})
    u.append("transition", 10, {"to": "evaluation"})
    check("digests are reproducible across tapes", u.head, t.head)


def test_tamper_is_evident():
    print("\ntamper evidence")
    src = os.path.join(TAPES, "clean-case.jsonl")
    lines = open(src, encoding="utf-8").read().splitlines()
    d = json.loads(lines[6]); d["at"] = 999
    lines[6] = json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    tmp = os.path.join(TAPES, ".tampered.tmp")
    open(tmp, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    try:
        Tape.load(tmp)
        check("altered body is detected", False, True)
    except TamperEvident as exc:
        check("altered body is detected", "altered" in str(exc), True)
        check("the failing entry is named", "entry 5" in str(exc), True)
    finally:
        os.remove(tmp)


def test_correction_is_an_append():
    """A correction never edits. The superseded entry stays readable forever."""
    print("\ncorrection is an append")
    t = Tape("T")
    t.append("note", 0, {"text": "first"})
    t.append("note", 5, {"text": "second"})
    before = len(t)
    t.correct(0, "note", 9, {"text": "corrected"})

    check("the tape grew", len(t), before + 1)
    check("the original is still there", t[0].body["text"], "first")
    check("it is marked superseded", 0 in t.superseded(), True)
    check("current() omits it", [e.seq for e in t.current()], [1, 2])
    check("the full record still has it", [e.seq for e in t], [0, 1, 2])
    check("chain still verifies", t.intact, True)


def test_fold_determinism():
    print("\nfolds are deterministic")
    t = Tape.load(os.path.join(TAPES, "clean-case.jsonl"))
    check("state_at is stable", state_at(t), state_at(t))
    check("two folds agree", t.fold(lambda a, e: a + [e.digest], []),
          t.fold(lambda a, e: a + [e.digest], []))
    check("clean case ends closed", state_at(t), "reporting_closed")
    check("timeline is ordered", [x[0] for x in timeline(t)] == sorted(x[0] for x in timeline(t)), True)


def test_export_is_lossless():
    print("\nexport is always available and lossless")
    t = Tape.load(os.path.join(TAPES, "clean-case.jsonl"))
    tmp = os.path.join(TAPES, ".roundtrip.tmp")
    t.save(tmp)
    try:
        u = Tape.load(tmp)
        check("round-trips exactly", u.to_jsonl(), t.to_jsonl())
        check("head survives", u.head, t.head)
        check("case id survives", u.case_id, t.case_id)
    finally:
        os.remove(tmp)


def test_replay_accepts_legal():
    print("\nreplay · a legal case")
    t = Tape.load(os.path.join(TAPES, "clean-case.jsonl"))
    f = replay(t)
    check("no violations", [x for x in f if x.status == ENFORCED], [])


def test_replay_refuses_illegal():
    print("\nreplay · an illegal case")
    t = Tape.load(os.path.join(TAPES, "violating-case.jsonl"))
    f = replay(t)
    rules = {x.rule for x in f if x.status == ENFORCED}
    check("catches the undeclared transition", "undeclared transition" in rules, True)
    check("catches the exit from a terminal", "exit from terminal" in rules, True)
    check("at least three violations", len([x for x in f if x.status == ENFORCED]) >= 3, True)


def test_unverified_guards_are_pending_not_passing():
    """
    The honesty check. A guard whose element provenance is TODO-VERIFY must be
    reported PENDING — never silently passed, and never enforced as if it were
    established policy. If this ever flips to enforcement without the locator
    being filled, the validator has started enforcing its author's recollection.
    """
    print("\nguard enforcement follows provenance, not opinion")
    m = load_machine()
    verified = [s for s, v in m["states"].items() if v.get("verified")]
    unverified = [s for s, v in m["states"].items() if not v.get("verified")]
    check("the machine form carries the verified flag", bool(verified), True)

    # Build one tape that trips a guard into a VERIFIED destination and another
    # into an UNVERIFIED one, so this asserts the RULE rather than today's counts.
    # (An earlier version of this test asserted "some guard is PENDING" and broke
    #  the moment a locator was filled — which was the machinery working, not a
    #  regression. Test the mechanism.)
    def guard_status(dst: str) -> str | None:
        edge = next((t for t in m["transitions"]
                     if t["to"] == dst and t.get("guard")), None)
        if edge is None:
            return None
        tape = Tape("probe")
        tape.append("transition", 0, {"from": edge["from"], "to": dst})  # guard unmet
        hits = [f for f in replay(tape, m) if f.rule == "guard not satisfied"]
        return hits[0].status if hits else None

    v_dst = next((s for s in verified if guard_status(s)), None)
    u_dst = next((s for s in unverified if guard_status(s)), None)

    if v_dst:
        check(f"guard into a VERIFIED state ({v_dst}) is ENFORCED", guard_status(v_dst), ENFORCED)
    if u_dst:
        check(f"guard into an UNVERIFIED state ({u_dst}) is PENDING", guard_status(u_dst), PENDING)
        # and it must say why, so nobody mistakes PENDING for a pass
        tape = Tape("probe")
        edge = next(t for t in m["transitions"] if t["to"] == u_dst and t.get("guard"))
        tape.append("transition", 0, {"from": edge["from"], "to": u_dst})
        pend = [f for f in replay(tape, m) if f.status == PENDING]
        check("PENDING says why", all("TODO-VERIFY" in f.detail for f in pend), True)
    else:
        print("  note  every guarded state is now verified — nothing left to hold PENDING")


def test_machine_matches_source():
    print("\nlifecycle.json is generated, not hand-edited")
    m = load_machine()
    check("declares its source", m.get("generated_from"), "lifecycle.yml")
    check("warns against hand-editing", "Do not edit by hand" in m.get("$comment", ""), True)
    check("states and transitions present", bool(m["states"]) and bool(m["transitions"]), True)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("REGISTRAR · core")
    for t in (test_append_only_by_type, test_chain, test_tamper_is_evident,
              test_correction_is_an_append, test_fold_determinism, test_export_is_lossless,
              test_replay_accepts_legal, test_replay_refuses_illegal,
              test_unverified_guards_are_pending_not_passing, test_machine_matches_source):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
