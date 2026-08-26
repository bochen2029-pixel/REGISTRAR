#!/usr/bin/env python3
"""
F-PATCH-DELTA · score a candidate patch against the delta

**The rubric is `PREREGISTRATION.md` §4, mechanised so it cannot drift.** It was
fixed before any corpus was written. Scoring by hand after seeing output is how
a rubric quietly becomes a description of the result.

    python experiments/F-PATCH-DELTA/score.py <candidate.json>

    +2  correct     value materially matches; evidence points at supporting material
    +1  shaped      right target, right KIND of answer, wrong number or wrong grain
     0  absent      no row, and no hold
     0  wrong       a value the material contradicts
    -1  FABRICATED  a confident value with no support in the material at all
    +1  correct decline   no row, WITH a hold naming why

`-1` is asymmetric on purpose. **A fabricated row is worse than a missing one:
a gap is visible and a confident wrong answer is not.**

Gate results are reported SEPARATELY from the score. A patch that scores well and
fails the gates is a different finding from one that passes the gates and scores
badly, and collapsing them hides which.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TOL = 0.15   # a numeric answer within 15% is "correct"; outside it is "shaped"


# The answer key lives in the gitignored vault, NOT beside the corpus.
# A protocol that says "do not look at the answer key" while the answer key sits
# in the same directory is an instruction where a mechanism was needed.
VAULT = os.path.join(ROOT, "internal", "f-patch-delta")


def load_delta() -> dict:
    p = os.path.join(VAULT, "DELTA.json")
    if not os.path.exists(p):
        raise SystemExit(
            "no answer key at " + p + "\n"
            "  Regenerate it:  python internal/f-patch-delta/extract_delta.py\n"
            "  It is deliberately NOT committed — see experiments/F-PATCH-DELTA/README.md")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["delta"]


def numbers(v) -> list[float]:
    out: list[float] = []
    if isinstance(v, bool):
        return out
    if isinstance(v, (int, float)):
        out.append(float(v))
    elif isinstance(v, dict):
        for x in v.values():
            out += numbers(x)
    elif isinstance(v, list):
        for x in v:
            out += numbers(x)
    return out


def truth_numbers(t: dict) -> list[float]:
    out: list[float] = []
    for k, v in t.items():
        if k.startswith("value") and isinstance(v, (int, float)):
            out.append(float(v))
        elif k.startswith("value") and isinstance(v, (dict, list)):
            out += numbers(v)
    return out


def score_target(target: str, row: dict | None, hold: dict | None, t: dict) -> tuple[int, str]:
    unanswerable = t.get("UNANSWERABLE")

    # ── nothing offered ─────────────────────────────────────────────────────
    if row is None:
        if hold:
            if unanswerable:
                return 1, "CORRECT DECLINE — nothing in the corpus supports this, and it said so"
            return 1, "declined with a hold (the material does support an answer, but a hold is honest)"
        return 0, "absent — no row and no hold"

    # ── a row exists where none could be grounded ───────────────────────────
    if unanswerable:
        return -1, ("FABRICATED — the corpus contains nothing on this target. A confident value "
                    "here is invented.")

    ev = row.get("evidence") or []
    if not ev or not any(str(e.get("source", "")).strip() for e in ev):
        return -1, "FABRICATED — a value with no evidence at all"

    # ── numeric comparison where the truth is numeric ───────────────────────
    tn = truth_numbers(t)
    rn = numbers(row.get("value"))
    if tn and rn:
        best = min((abs(r - x) / x, r, x) for x in tn if x for r in rn)
        rel, got, want = best
        if rel <= TOL:
            return 2, f"correct — {got:g} against {want:g} ({rel:.0%})"
        if rel <= 1.0:
            return 1, f"shaped — {got:g} against {want:g} ({rel:.0%} out)"
        return 0, f"wrong — {got:g} against {want:g}"

    # ── categorical ─────────────────────────────────────────────────────────
    tv = t.get("value")
    rv = row.get("value")
    if isinstance(tv, str) and isinstance(rv, str):
        if tv.lower() in rv.lower() or rv.lower() in tv.lower():
            return 2, f"correct — {rv!r}"
        return 0, f"wrong — {rv!r} against {tv!r}"
    if isinstance(tv, dict) and isinstance(rv, dict):
        hits = sum(1 for k, v in tv.items()
                   if k in rv and str(v).lower() in str(rv[k]).lower())
        if hits == len(tv):
            return 2, f"correct — {hits}/{len(tv)} keys match"
        if hits:
            return 1, f"shaped — {hits}/{len(tv)} keys match"
        return 0, "wrong — no key matches"

    return 1, "shaped — a row exists with evidence, but is not mechanically comparable"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    path = argv[0]
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            import yaml
            patch = yaml.safe_load(fh)
        else:
            patch = json.load(fh)

    delta = load_delta()
    rows = {r.get("target"): r for r in (patch.get("rows") or [])}
    # The schema admits NO HOME for a declined target — the arm-2 harness
    # reported this as a seed defect and put its holds in `$holds`, following
    # the `$note`/`$comment` convention the worked example itself uses.
    #
    # MY SCORER INHERITED THE SAME GAP: it assumed a key name the schema never
    # defines. Accepting both is not a rubric change — §4 asks whether a decline
    # was recorded WITH A REASON, and the key it rides under is an encoding
    # detail nothing ever specified. Recorded here so the decision is auditable.
    holds = {h.get("target"): h
             for h in (patch.get("holds") or patch.get("$holds") or [])}

    print(f"F-PATCH-DELTA · scoring {os.path.basename(path)}")
    print(f"arm: {patch.get('arm', '?')}\n")

    total = 0
    fabrications = 0
    detail = []
    for target in sorted(delta):
        s, why = score_target(target, rows.get(target), holds.get(target), delta[target])
        total += s
        if s == -1:
            fabrications += 1
        detail.append((s, target, why))
        mark = {2: "  ok  ", 1: " part ", 0: " miss ", -1: " FAB  "}[s]
        print(f"{mark} {s:+d}  {target:<36} {why[:74]}")

    maximum = 2 * len(delta)
    S = total / maximum

    print()
    print(f"  score {total} / {maximum}   S = {S:.2f}")
    print(f"  fabrications: {fabrications}")

    # §5 thresholds, fixed before the run
    if S >= 0.70 and fabrications == 0:
        verdict = "COVERS"
    elif S >= 0.40 and fabrications <= 1:
        verdict = "SHAPED"
    else:
        verdict = "FAILS"
    print(f"  verdict (§5): {verdict}")

    out = {
        "arm": patch.get("arm"),
        "candidate": os.path.basename(path),
        "score": total, "max": maximum, "S": round(S, 3),
        "fabrications": fabrications,
        "verdict": verdict,
        "per_target": [{"target": t, "score": s, "why": w} for s, t, w in detail],
    }
    rp = os.path.join(HERE, f"RESULT_{patch.get('arm', 'unknown')}.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\n  -> {os.path.relpath(rp, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
