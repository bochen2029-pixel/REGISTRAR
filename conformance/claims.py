#!/usr/bin/env python3
"""
REGISTRAR · conformance · the claims file

**Every number this repository asserts in public, derived from the repository
itself.**

Built because the same failure happened three times in one day, and none of it
was caught by a check:

  · the hardware line asked for 24–32 GB while everything was proven on 16
  · the corpus gitignore covered a LOCATION while the rule was about CONTENT
  · **the public page claimed nine gates in one place and twelve in another
    while the battery had sixteen, reported 41 citations against 44, and showed
    the completion falsifier as UNRUN hours after it returned**

Each was true when written and stopped being true while nobody looked. **This
repository gates everything except its own public surface**, and the discipline
it relies on instead — *the plate changes first and the prose follows* — has now
failed three times. That is the argument for a check rather than a resolution.

HOW IT WORKS, AND WHY IT IS NOT COUPLED TO ANY PAGE

`CLAIMS.json` is generated from the repository — gate count by running the
battery, citations by counting them, states by reading the lifecycle. **A
rendering surface is then checked against that file rather than against
somebody's memory.**

That indirection is the point. REGISTRAR does not know about any website, and a
check that reached into one would fail for every stranger who clones this. **A
surface that renders these claims checks itself against the file; a surface that
does not exist reports PASS-UNVERIFIED, which is the honest state.**

    python conformance/claims.py --emit          regenerate CLAIMS.json
    python conformance/claims.py --check         is CLAIMS.json current?
    python conformance/claims.py --surface <f>   does that file agree with it?

Zero dependencies.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CLAIMS.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# A surface may spell a small number in words. Both forms must agree with the file.
WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
    8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty",
}
FROM_WORD = {v: k for k, v in WORDS.items()}


def _int(tok: str) -> int | None:
    tok = tok.strip().lower()
    if tok.isdigit():
        return int(tok)
    return FROM_WORD.get(tok)


# ── deriving each claim from the repository ─────────────────────────────────
def derive(with_battery: bool = True) -> dict:
    """
    `with_battery=False` skips the subprocess that runs the whole conformance
    battery — which is what the battery itself must pass when it calls this,
    because a check that runs the run it is part of does not terminate. Learned
    by timing out twice rather than by failing.
    """
    env = dict(os.environ, PYTHONIOENCODING="utf-8")

    # gates: count what the battery actually reports on the worked example
    r = subprocess.run([sys.executable, os.path.join(ROOT, "gates", "validate_patch.py"),
                        os.path.join(ROOT, "examples", "worked", "northlake.patch.json")],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    lines = [ln for ln in r.stdout.splitlines()
             if re.match(r"^  (GREEN|FAILED|PASS-UNVERIFIED)\s", ln)]
    gates = len(lines)

    # "N gates report PASS-UNVERIFIED" is a claim about A MACHINE-AUTHORED DRAFT,
    # not about the signed worked example — and deriving it from the signed one
    # gave 2 where a surface honestly said 3, because `signature` is GREEN once a
    # human has signed and PASS-UNVERIFIED before.
    #
    # The check was right that the numbers differed and wrong about which subject
    # each described. Fixed by deriving the same subject the claim is about: the
    # worked example with its signatures stripped, which is exactly what a
    # completion hands to a reviewer.
    sys.path.insert(0, os.path.join(ROOT, "gates"))
    sys.path.insert(0, os.path.join(ROOT, "core"))
    try:
        from validate_patch import UNVERIFIED as _U
        from validate_patch import load_patch, load_targets
        from validate_patch import validate as _v
        draft = load_patch(os.path.join(ROOT, "examples", "worked", "northlake.patch.json"))
        for row in draft.get("rows") or []:
            row["author"] = ""                       # a machine leaves it empty
        gates_unverified = sum(1 for st, _, _ in _v(draft, load_targets()).rows if st == _U)
    except Exception:
        gates_unverified = 0

    with open(os.path.join(ROOT, "corpus", "citations.json"), encoding="utf-8") as fh:
        citations = len(json.load(fh)["citations"])
    with open(os.path.join(ROOT, "corpus", "MANIFEST.json"), encoding="utf-8") as fh:
        m = json.load(fh)
        srcs = m["sources"]
        sources = len(srcs) if isinstance(srcs, list) else len(list(srcs))

    with open(os.path.join(ROOT, "core", "lifecycle", "lifecycle.json"), encoding="utf-8") as fh:
        lc = json.load(fh)["states"]
    verified = sum(1 for v in lc.values() if v.get("verified"))

    # the battery's own three-state summary
    if with_battery:
        b = subprocess.run([sys.executable, os.path.join(ROOT, "conformance", "run.py")],
                           capture_output=True, text=True, encoding="utf-8", env=env)
    else:
        b = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    # ANCHOR TO THE LINE START. Sub-batteries (adapters, forge) print their own
    # summaries INSIDE a detail line, so a bare search finds "10 GREEN · 3
    # PASS-UNVERIFIED" from the adapter checker rather than the battery's own
    # total. Caught on the first run of this file — a claims file that reported
    # a sub-battery as the whole would have been the drift it exists to prevent,
    # generated automatically and therefore trusted.
    mt = re.findall(r"^(\d+) GREEN · (\d+) PASS-UNVERIFIED · (\d+) FAILED",
                    b.stdout, re.M)
    green, unver, failed = (int(mt[-1][0]), int(mt[-1][1]), int(mt[-1][2])) if mt else (0, 0, 0)

    rejected = os.path.join(ROOT, "examples", "worked", "rejected")
    fixtures = len([f for f in os.listdir(rejected) if f.endswith(".json")]) \
        if os.path.isdir(rejected) else 0

    return {
        "$comment": "GENERATED from the repository by conformance/claims.py. Do not edit by "
                    "hand — a hand-edited claims file is the drift it exists to prevent, "
                    "wearing the costume of the fix.",
        "generated_by": "conformance/claims.py",
        "claims": {
            "gates": {
                "value": gates,
                "pattern": r"(\w+) gates",
                # A surface legitimately says "three gates report PASS-UNVERIFIED",
                # which is a claim about a SUBSET and was flagged as stale by a
                # pattern that could not tell the two apart. Third greedy matcher
                # in one day — see gates/attest.py, where the fourth check was
                # DELETED for the same reason. A checker that cries wolf is worse
                # than none, and the mechanism is the fix, not the pattern.
                "exclude": [r"\w+ gates report", r"\w+ gates are ", r"\w+ gates that "],
                "note": "every gate the battery reports on the worked example",
            },
            "gates_unverified": {
                "value": gates_unverified,
                "pattern": r"(\w+) gates report",
                "note": "the subset that cannot be decided from a file — and PASS-UNVERIFIED "
                        "IS NOT A PASS",
            },
            "citations": {
                "value": citations,
                "pattern": r"(\d+) citations",
                "note": "byte-exact against pinned sources",
            },
            "pinned_sources": {
                "value": sources,
                "pattern": r"(\d+) pinned sources",
            },
            "states_verified": {
                "value": verified,
                "of": len(lc),
                "pattern": r"(\d+) ?/ ?15",
                "note": "the remaining two are open for NON-EQUIVALENT reasons and a "
                        "surface that says '2 unverified' without them misreports",
            },
            # THE BATTERY TOTAL IS A PROPERTY OF A CONFIGURATION, NOT A CONSTANT.
            # `claims · public surface` reports GREEN when REGISTRAR_SURFACE
            # points at a rendered page and PASS-UNVERIFIED when it does not, so
            # the totals move by one between the two. Recorded in the DEFAULT
            # configuration — no surface — because that is what a stranger
            # cloning this repository runs, and a number on a public page must
            # be the one they can reproduce.
            "battery_configuration": {"value": "default — no REGISTRAR_SURFACE set"},
            "battery_green": {"value": green, "pattern": r"(\d+) G ·"},
            "battery_unverified": {"value": unver, "pattern": r"· (\d+) PU"},
            "battery_failed": {"value": failed, "pattern": r"· (\d+) F\b"},
            "adversarial_fixtures": {
                "value": fixtures,
                "pattern": r"(\d+) adversarial fixtures",
            },
        },
        "not_derivable_here": {
            "$note": "Claims a surface may carry that this file cannot check, listed so "
                     "their absence is not read as coverage.",
            "items": [
                "the F-PATCH-DELTA result — it lives in internal/, gitignored, and a "
                "clone does not receive it",
                "every substrate row — measured in another domain, on another bench",
                "anything about a real OPO, because nothing has run inside one",
            ],
        },
    }


def emit() -> int:
    d = derive()
    with open(CLAIMS, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    c = d["claims"]
    print(f"CLAIMS.json written — {len(c)} claims")
    for k, v in c.items():
        print(f"  {k:<22} {v['value']}")
    return 0


def check() -> int:
    """Has the repository moved without the claims file moving with it?"""
    if not os.path.exists(CLAIMS):
        print("no CLAIMS.json — run --emit")
        return 1
    with open(CLAIMS, encoding="utf-8") as fh:
        old = json.load(fh)["claims"]
    new = derive()["claims"]

    drift = [(k, old.get(k, {}).get("value"), v["value"])
             for k, v in new.items() if old.get(k, {}).get("value") != v["value"]]
    if drift:
        print(f"CLAIMS.json is STALE — {len(drift)} claim(s) moved:")
        for k, was, now in drift:
            print(f"    {k}: {was} → {now}")
        print("\n  Run --emit, and update every surface that renders these.")
        return 1
    print(f"CLAIMS.json current — {len(new)} claims agree with the repository")
    return 0


def surface(path: str) -> int:
    """Does a rendering surface agree with the claims file?"""
    if not os.path.exists(path):
        print(f"no surface at {path} — nothing to check")
        return 2
    with open(CLAIMS, encoding="utf-8") as fh:
        claims = json.load(fh)["claims"]
    text = open(path, encoding="utf-8", errors="replace").read()

    print(f"surface · {os.path.basename(path)}\n")
    stale, checked = [], 0
    for name, c in claims.items():
        pat = c.get("pattern")
        if not pat:
            continue
        blob = text
        for ex in c.get("exclude") or []:
            blob = re.sub(ex, " ", blob)     # a phrasing that only looks like this claim
        found = {_int(m) for m in re.findall(pat, blob)}
        found.discard(None)
        if not found:
            continue                       # the surface does not make this claim
        checked += 1
        want = c["value"]
        wrong = sorted(x for x in found if x != want)
        if wrong:
            stale.append((name, wrong, want))
            print(f"  STALE  {name}: surface says {wrong}, repository says {want}")
        else:
            print(f"  ok     {name}: {want}")

    print()
    if stale:
        print(f"FAILED — {len(stale)} stale claim(s) on a public surface.")
        print("  A claim that was true when written and is not true now is the failure")
        print("  this check exists for. It has happened three times.")
        return 1
    if not checked:
        print("PASS-UNVERIFIED — the surface makes none of these claims in a form this")
        print("  can read. That is not a pass: it may be phrasing them another way.")
        return 2
    print(f"GREEN — {checked} claim(s) on this surface agree with the repository.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--emit" in a:
        raise SystemExit(emit())
    if "--surface" in a:
        raise SystemExit(surface(a[a.index("--surface") + 1]))
    raise SystemExit(check())
