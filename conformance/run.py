#!/usr/bin/env python3
"""
REGISTRAR · conformance
─────────────────────────────────────────────────────────────────────────────
One command that says whether an instance is sound.

    python conformance/run.py

This is the battery `SPEC.md` §11 names as the thing a completed instance must
pass before it load-bears. It reports in three states, and the middle one is
not a pass:

    GREEN            verified to pass
    PASS-UNVERIFIED  the check did not, or could not, run
    FAILED           verified to fail

**This battery currently ends PASS-UNVERIFIED, on purpose.** Most of the
lifecycle's provenance locators still read TODO-VERIFY, which means most of the
spine is specified rather than established — and a battery that returned GREEN
over an unverified spine would be reporting success past a step that never ran.
Filling those locators against the published sources is what turns this green.

Zero dependencies. Add `--verbose` for the detail behind each line.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, os.path.join(ROOT, "gates"))
sys.path.insert(0, os.path.join(ROOT, "floor"))

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"
VERBOSE = "--verbose" in sys.argv

CHECKS: list[tuple[str, str, str]] = []


def record(state: str, name: str, detail: str = "") -> None:
    CHECKS.append((state, name, detail))
    dots = "." * max(2, 38 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


# ── 1 · the spine is structurally sound ─────────────────────────────────────
def check_lifecycle() -> None:
    from case import load_machine

    m = load_machine()
    states, trans = m["states"], m["transitions"]

    bad = [f"{t['from']}->{t['to']}" for t in trans if t["from"] not in states or t["to"] not in states]
    record(FAILED if bad else GREEN, "lifecycle · states exist",
           ", ".join(bad) if bad else f"{len(trans)} transitions, all endpoints declared")

    leaving = {t["from"] for t in trans}
    bad_term = sorted(s for s, v in states.items() if v["terminal"] and s in leaving)
    record(FAILED if bad_term else GREEN, "lifecycle · terminals are terminal",
           ", ".join(bad_term) if bad_term else "no transition leaves a terminal state")

    # every non-start state must be reachable, or it is unreachable code in a spine
    reach, frontier = {"referral_received"}, ["referral_received"]
    while frontier:
        cur = frontier.pop()
        for t in trans:
            if t["from"] == cur and t["to"] not in reach:
                reach.add(t["to"])
                frontier.append(t["to"])
    orphans = sorted(set(states) - reach)
    record(FAILED if orphans else GREEN, "lifecycle · every state reachable",
           ", ".join(orphans) if orphans else f"all {len(states)} reachable from referral_received")

    terminals = sorted(s for s, v in states.items() if v["terminal"])
    record(GREEN if terminals else FAILED, "lifecycle · has terminals",
           f"{len(terminals)} terminal states, {len(terminals) - 1} of them non-conversion")

    unverified = sorted(s for s, v in states.items() if not v.get("verified"))
    record(UNVERIFIED if unverified else GREEN, "lifecycle · provenance",
           f"{len(unverified)} of {len(states)} states still TODO-VERIFY — "
           f"specified, not established")
    if VERBOSE and unverified:
        for s in unverified:
            print(f"                     · {s}")


# ── 2 · generated artifacts have not drifted ────────────────────────────────
def check_generated() -> None:
    r = subprocess.run([sys.executable, os.path.join(ROOT, "core", "lifecycle", "gen_targets.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        record(GREEN, "generated · no drift", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "current")
    elif r.returncode == 3:
        record(UNVERIFIED, "generated · no drift", "pyyaml unavailable — regeneration not checked")
    else:
        record(FAILED, "generated · no drift", (r.stdout + r.stderr).strip().splitlines()[0])


# ── 3 · the tape ────────────────────────────────────────────────────────────
def check_tape() -> None:
    from tape import Tape, state_at

    tapes_dir = os.path.join(ROOT, "fixtures", "tapes")
    paths = sorted(os.path.join(tapes_dir, f) for f in os.listdir(tapes_dir) if f.endswith(".jsonl"))

    broken = []
    for p in paths:
        try:
            Tape.load(p)
        except Exception as exc:
            broken.append(f"{os.path.basename(p)}: {exc}")
    record(FAILED if broken else GREEN, "tape · hash chain intact",
           "; ".join(broken) if broken else f"{len(paths)} tapes verified end to end")

    # replay determinism: the same fold twice must agree exactly
    t = Tape.load(paths[0])
    a, b = state_at(t), state_at(t)
    hist_a = t.fold(lambda acc, e: acc + [e.digest], [])
    hist_b = t.fold(lambda acc, e: acc + [e.digest], [])
    record(GREEN if (a == b and hist_a == hist_b) else FAILED, "tape · replay determinism",
           "two independent folds agree byte for byte")

    # the interface must not have grown a way to mutate
    forbidden = [n for n in ("delete", "update", "remove", "truncate", "__setitem__", "pop")
                 if hasattr(Tape, n)]
    record(FAILED if forbidden else GREEN, "tape · append-only by type",
           f"Tape exposes {', '.join(forbidden)}" if forbidden
           else "no delete, no update — absent from the interface, not forbidden by policy")


# ── 4 · case replay ─────────────────────────────────────────────────────────
def check_replay() -> None:
    from case import ENFORCED, replay
    from tape import Tape

    clean = Tape.load(os.path.join(ROOT, "fixtures", "tapes", "clean-case.jsonl"))
    f = replay(clean)
    viol = [x for x in f if x.status == ENFORCED]
    record(FAILED if viol else GREEN, "replay · clean case passes",
           f"{len(viol)} violations" if viol else "no violation on a legal case")

    bad = Tape.load(os.path.join(ROOT, "fixtures", "tapes", "violating-case.jsonl"))
    f2 = replay(bad)
    viol2 = [x for x in f2 if x.status == ENFORCED]
    record(GREEN if viol2 else FAILED, "replay · refuses an illegal case",
           f"{len(viol2)} violations caught on a deliberately illegal tape")

    pend = [x for x in f2 if x.status != ENFORCED]
    record(UNVERIFIED if pend else GREEN, "replay · guard enforcement",
           f"{len(pend)} guard check(s) PENDING — element provenance is TODO-VERIFY")


# ── 5 · the gates ───────────────────────────────────────────────────────────
def check_gates() -> None:
    from validate_patch import FAILED as GF, load_patch, load_targets, validate

    worked = os.path.join(ROOT, "examples", "worked")
    r = validate(load_patch(os.path.join(worked, "northlake.patch.json")), load_targets())
    record(GREEN if GF not in {s for s, _, _ in r.rows} else FAILED,
           "gates · accepted patch", "no gate FAILED on the worked example")

    rejected = sorted(os.listdir(os.path.join(worked, "rejected")))
    refused = 0
    for f in rejected:
        rr = validate(load_patch(os.path.join(worked, "rejected", f)), load_targets())
        if rr.worst == GF:
            refused += 1
    record(GREEN if refused == len(rejected) else FAILED, "gates · refuses bad patches",
           f"{refused}/{len(rejected)} adversarial drafts refused")

    record(UNVERIFIED, "gates · undecidable from a file",
           "local invertibility, shadow-run fidelity, totality — need a runtime and the site's tape")


# ── 6 · the floor works with everything learned disabled ────────────────────
def check_floor() -> None:
    src = open(os.path.join(ROOT, "floor", "closure.py"), encoding="utf-8").read()
    banned = [b for b in ("import torch", "import numpy", "openai", "anthropic", "requests", "urllib")
              if b in src]
    record(FAILED if banned else GREEN, "floor · model-free",
           f"found {banned}" if banned else "no model or network imports; behaves identically with learned components off")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "floor", "test_closure.py")],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    record(GREEN if r.returncode == 0 else FAILED, "floor · closure battery", last)


# ── 7 · nothing site-specific is in the repository ──────────────────────────
def check_no_site_data() -> None:
    offenders = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "internal", "deepseek-harness-master")]
        for fn in filenames:
            if fn.endswith(".patch.yml") and "worked" not in dirpath:
                offenders.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))
    record(FAILED if offenders else GREEN, "hygiene · no site patch committed",
           ", ".join(offenders) if offenders else "no <site>.patch.yml outside the worked example")

    fixtures = os.path.join(ROOT, "fixtures")
    unmarked = []
    for dirpath, _, filenames in os.walk(fixtures):
        for fn in filenames:
            if fn.endswith((".json", ".jsonl")):
                text = open(os.path.join(dirpath, fn), encoding="utf-8").read(4000)
                if "SYNTHETIC" not in text.upper() and "synthetic" not in text:
                    unmarked.append(fn)
    record(FAILED if unmarked else GREEN, "hygiene · fixtures declare synthetic",
           ", ".join(unmarked) if unmarked else "every fixture states it carries no real data")


# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    print("REGISTRAR · conformance\n")
    for section, fn in (
        ("the spine", check_lifecycle),
        ("generated artifacts", check_generated),
        ("the tape (L4)", check_tape),
        ("case replay", check_replay),
        ("the gates", check_gates),
        ("the floor", check_floor),
        ("hygiene", check_no_site_data),
    ):
        print(f"{section}")
        fn()
        print()

    states = {s for s, _, _ in CHECKS}
    worst = FAILED if FAILED in states else (UNVERIFIED if UNVERIFIED in states else GREEN)
    n_f = sum(1 for s, _, _ in CHECKS if s == FAILED)
    n_u = sum(1 for s, _, _ in CHECKS if s == UNVERIFIED)
    n_g = sum(1 for s, _, _ in CHECKS if s == GREEN)

    print(f"{n_g} GREEN · {n_u} PASS-UNVERIFIED · {n_f} FAILED\n")
    if worst == FAILED:
        print("FAILED — this instance does not load-bear.")
        return 1
    if worst == UNVERIFIED:
        print("PASS-UNVERIFIED — nothing failed, but checks did not run.")
        print("  Most of the spine's provenance is still TODO-VERIFY, so most of it is")
        print("  specified rather than established. THIS IS NOT A PASS. Fill the locators")
        print("  against the published sources and run this again.")
        return 2
    print("GREEN — every check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
