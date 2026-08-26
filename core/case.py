#!/usr/bin/env python3
"""
REGISTRAR · core · case replay
─────────────────────────────────────────────────────────────────────────────
Replay a case tape against the mandated lifecycle and report what was illegal.

This is where the spine stops being a document and starts refusing things. It
answers three questions, and it is careful about which of them it is actually
entitled to answer:

  1. Did the case only ever move along declared transitions?   ENFORCED
  2. Did anything leave a terminal state?                      ENFORCED
  3. Were the guarding elements complete before each move?     DEPENDS

The third is where the honesty lives. A guard is only enforceable if the
element it names has a verified provenance locator. Most do not yet — they read
TODO-VERIFY in `lifecycle.yml`, and per `PROVENANCE.md` §2 **an element with an
unverified locator is not implemented; it is a TODO.** So this module reports
those as PENDING rather than passing or failing them.

That distinction is the entire difference between a system that enforces policy
and one that enforces its author's recollection of policy. Filling those
locators against the published sources is what converts a PENDING into a check.

Zero dependencies. Reads the generated `lifecycle.json`, never the YAML.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from tape import Tape, TamperEvident  # noqa: E402

MACHINE = os.path.join(HERE, "lifecycle", "lifecycle.json")
START = "referral_received"

ENFORCED, PENDING = "ENFORCED", "PENDING"


@dataclass(frozen=True)
class Finding:
    seq: int
    rule: str
    status: str       # ENFORCED (a real violation) | PENDING (cannot be checked yet)
    detail: str

    def render(self) -> str:
        mark = "VIOLATION" if self.status == ENFORCED else "PENDING  "
        return f"  {mark}  seq {self.seq:>3}  {self.rule:<26} {self.detail}"


def load_machine(path: str = MACHINE) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def replay(tape: Tape, machine: dict | None = None) -> list[Finding]:
    """
    Walk the tape. Return findings, most of which should be none.

    Note what this does NOT do: it does not repair, reorder, infer a missing
    transition, or decide what the case "meant". It reports. The record is
    written by people; this reads it.
    """
    m = machine or load_machine()
    states, edges = m["states"], m["transitions"]
    legal = {(t["from"], t["to"]): t.get("guard") or [] for t in edges}

    findings: list[Finding] = []
    current = START
    established: set[str] = set()

    for e in tape.current():
        if e.kind == "element":
            name = e.body.get("element")
            if name:
                established.add(name)
            continue

        if e.kind != "transition":
            continue

        src = e.body.get("from", current)
        dst = e.body.get("to")

        # ── 1 · the states must exist ──────────────────────────────────────
        for role, s in (("from", src), ("to", dst)):
            if s not in states:
                findings.append(Finding(e.seq, "unknown state", ENFORCED,
                                        f"{role}={s!r} is not a state in the lifecycle"))
        if src not in states or dst not in states:
            current = dst or current
            continue

        # ── 2 · nothing leaves a terminal ──────────────────────────────────
        if states[src]["terminal"]:
            findings.append(Finding(e.seq, "exit from terminal", ENFORCED,
                                    f"{src} is terminal; the case cannot move to {dst}"))

        # ── 3 · the edge must be declared ──────────────────────────────────
        if (src, dst) not in legal:
            findings.append(Finding(e.seq, "undeclared transition", ENFORCED,
                                    f"{src} -> {dst} is not a transition the lifecycle declares"))
        else:
            # ── 4 · guards, but only where we are entitled to enforce ──────
            for g in legal[(src, dst)]:
                if g in established:
                    continue
                enforceable = states[dst].get("verified", False)
                findings.append(Finding(
                    e.seq, "guard not satisfied",
                    ENFORCED if enforceable else PENDING,
                    f"{src} -> {dst} requires {g!r}, which the tape has not established"
                    + ("" if enforceable else "  [element provenance is TODO-VERIFY]"),
                ))

        current = dst

    return findings


def summarise(tape: Tape, findings: list[Finding]) -> dict:
    violations = [f for f in findings if f.status == ENFORCED]
    pending = [f for f in findings if f.status == PENDING]
    return {
        "case": tape.case_id,
        "entries": len(tape),
        "superseded": len(tape.superseded()),
        "chain": "intact" if tape.intact else "BROKEN",
        "violations": len(violations),
        "pending": len(pending),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    try:
        tape = Tape.load(argv[1])
    except TamperEvident as exc:
        print(f"TAMPER-EVIDENT: {exc}")
        return 1

    findings = replay(tape)
    s = summarise(tape, findings)

    print(f"case {s['case']} — {s['entries']} entries "
          f"({s['superseded']} superseded, still on the tape), chain {s['chain']}\n")

    if not findings:
        print("  no findings: every transition was declared, and every enforceable guard was met")
    else:
        for f in findings:
            print(f.render())

    print()
    if s["violations"]:
        print(f"{s['violations']} violation(s). The record says this case moved in a way the lifecycle "
              f"does not permit.")
    if s["pending"]:
        print(f"{s['pending']} check(s) PENDING — the guarding element's provenance locator is still "
              f"TODO-VERIFY,")
        print("  so this validator is not entitled to enforce it. That is not a pass.")
    return 1 if s["violations"] else (2 if s["pending"] else 0)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
