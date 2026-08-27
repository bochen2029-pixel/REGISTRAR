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
                # FOURTH greedy matcher, same lesson as `gates` above. A surface
                # legitimately says "the 2/15 states, which are open for
                # non-equivalent reasons" — that is a claim about the COMPLEMENT
                # (2 open, therefore 13 verified) and this pattern read it as a
                # verified-count and cried wolf on ROADMAP.md. The exclude is the
                # mechanism; widening the pattern would not have helped, because
                # the two phrasings are identical in shape and differ only in
                # which side of the fraction the surface is talking about.
                # `\s+` and not ` ` — the first version of this exclude required a
                # literal space and the phrasing it was written for wrapped across
                # a line break, so it matched nothing and the wolf stayed cried.
                # 2026-08-26, SECOND correction, from an adversarial audit that
                # built the counter-examples and ran them. The exclude above was
                # too wide in two ways and the combination was worse than the
                # false positive it fixed:
                #   * `[^.]*?` excludes a literal DOT, not "any char" — so it
                #     crossed newlines, and in a markdown table (few periods) the
                #     deletion ran ~88 chars past the phrase, swallowing a
                #     legitimate `13/15` further down.
                #   * `open` was unanchored and matched inside `open-source`.
                # Measured effect: a surface saying `11/15 states established`
                # returned GREEN with `states_verified` absent from the output —
                # a genuinely stale number the gate CAUGHT before the exclude and
                # missed after it. Now bounded to one line, capped, word-anchored.
                "exclude": [r"(?:the )?\d+ ?/ ?15\s+states\b[^.\n]{0,60}?\b(?:open|unverified|remaining)\b"],
                "note": "the remaining two are open for NON-EQUIVALENT reasons and a "
                        "surface that says '2 unverified' without them misreports",
            },
            # The complement, added with the fix above. An exclude only makes a
            # phrasing invisible; it does not check it. Without this claim the
            # open/unverified form was checked by NOTHING, which converted a
            # false positive into an unguarded claim — a worse trade.
            "states_open": {
                "value": len(lc) - verified,
                "pattern": r"(\d+) ?/ ?15\s+states\b[^.\n]{0,60}?\b(?:open|unverified|remaining)\b",
                "note": "the complement of states_verified; open for non-equivalent "
                        "reasons — known-incomplete (authorization) and design-choice "
                        "(referral_lapsed) — and a surface that merges them misreports",
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
            # ── battery strength ────────────────────────────────────────────
            # SPEC.md §12 ranks a weak battery as the central risk, and until
            # F-BATTERY-STRENGTH it had no number — only seven hand-found holes
            # with no denominator. These are DERIVED, never typed, for the
            # reason that makes them worth gating at all: the score moves
            # whenever `gates/` moves. A gate fix that lowers it has traded
            # coverage for accuracy, and a hardcoded figure would hide that.
            # ~0.3 s to compute.
            **_mutation_claims(),
        },
        "not_derivable_here": {
            "$note": "Claims a surface may carry that this file cannot check, listed so "
                     "their absence is not read as coverage.",
            "items": [
                "the F-PATCH-DELTA verdict — VOID-BY-AMBIGUITY, dual-printed (0.57 ∥ 0.375) on the "
                "surfaces; the answer key is vaulted in internal/ and the prose verdicts in the "
                "tracked RESULTS.md are not parseable by this file's numeric patterns",
                "every substrate row — measured in another domain, on another bench",
                "anything about a real OPO, because nothing has run inside one",
            ],
        },
    }


def _mutation_claims() -> dict:
    """Battery strength, derived by running the mutation harness.

    Returns {} if the harness is absent, so a clone that does not carry the
    experiment still gets a green claims file rather than a crash — the claim
    simply is not asserted, which is the honest state.
    """
    import importlib.util
    mp = os.path.join(ROOT, "experiments", "F-BATTERY-STRENGTH", "mutate.py")
    if not os.path.exists(mp):
        return {}
    try:
        spec = importlib.util.spec_from_file_location("_fbs_mutate", mp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _, results = mod.run()
        total = len(results)
        killed = sum(1 for r in results if r["verdict"] == "KILLED")
        if not total:
            return {}
        return {
            "mutation_score_pct": {
                "value": round(killed / total * 100, 1),
                "pattern": r"mutation score[^0-9]{0,24}(\d+\.\d)\s*%",
            },
            "mutation_denominator": {
                "value": total,
                "pattern": r"\*\*(\d+)\*\* mutants",
            },
            "mutation_survivors": {
                "value": total - killed,
                "pattern": r"\*\*(\d+) — defects",
            },
        }
    except Exception:
        return {}


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
    stale, unchecked, checked = [], [], 0
    for name, c in claims.items():
        pat = c.get("pattern")
        if not pat:
            continue
        blob = text
        suppressed = 0
        for ex in c.get("exclude") or []:
            blob, n = re.subn(ex, " ", blob, flags=re.I)  # a phrasing that only looks like this claim
            suppressed += n
        # re.I: the founding stale number lived in a CAPS fineprint ("41 CITATIONS")
        # and the case-sensitive matcher blessed it — QC F2. A claim is a claim
        # in any case the page chooses to shout it in.
        found = {_int(m) for m in re.findall(pat, blob, re.I)}
        found.discard(None)
        if not found:
            # THREE STATES, NEVER TWO — enforced here, in the file that enforces it.
            # "The surface never made this claim" and "every occurrence of it was
            # excluded" are different facts. Reporting the second as the first
            # drops a claim silently: not counted, not flagged, invisible. That is
            # the middle state collapsing into the first, which is the exact
            # failure this repository names as its own first law.
            if suppressed and re.search(pat, text):
                unchecked.append(name)
                print(f"  UNCHECKED  {name}: every occurrence excluded here — NOT a pass")
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
    if unchecked:
        print(f"PASS-UNVERIFIED — {len(unchecked)} claim(s) went unchecked on this surface:")
        for name in unchecked:
            print(f"  · {name} — present, but every occurrence was excluded")
        print("  An exclude makes a phrasing invisible; it does not verify it. A surface")
        print("  where a claim is excluded and nothing else checks it is UNGUARDED, and")
        print("  reporting that as GREEN is how a gate stops being one.")
        return 2
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
