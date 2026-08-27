#!/usr/bin/env python3
"""
F-BATTERY-STRENGTH · attribution — what did S = 0.57 actually measure?

Executes `PLAN_attribution.md`, whose thresholds were fixed before this ran.

**Axis A · gate-checkability.** Not a judgement call. For each row, apply the
`evidence-unrelated` mutation — replace every cited source with a sentence about
the cafeteria — and re-run the whole battery. KILLED means the gates can
mechanically tie that row to its evidence: **CHECKABLE**. SURVIVED means they
cannot: **BLIND**. This is the instrument from `mutate.py`, pointed one row at a
time at the candidates F-PATCH-DELTA actually graded.

**Axis B · how the score was earned.** From the scorer's own `per_target[].why`.

    python attribute.py <candidate> <result.json> [<candidate> <result.json> ...]

Reads only. Writes nothing anywhere.
"""

from __future__ import annotations

import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "gates"))

from validate_patch import FAILED, load_patch, load_targets, validate  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UNRELATED = "the cafeteria closes at eight on weekends"


def _failed_set(result):
    return {(g, d) for s, g, d in result.rows if s == FAILED}


def checkability(patch, targets):
    """target -> CHECKABLE | BLIND, by re-running the battery per row.

    CORRECTED 2026-08-26T23:12Z — the first version asked *did any gate FAIL?*
    and that is contaminated for any candidate whose baseline already fails.
    Arm 1 fails four gates before a single mutation (20 of 20 rows carry no
    denominator), so every arm-1 mutant was trivially 'killed' and its
    mechanised share came out 1.00 — an artifact of the instrument, not a
    property of the patch.

    The test is now a DELTA: a row is CHECKABLE when destroying its evidence
    introduces a failure the baseline did not already have. That question is
    well-posed whether or not the patch passes.
    """
    out = {}
    rows = patch.get("rows") or []
    base_failed = _failed_set(validate(patch, targets))
    for i, row in enumerate(rows):
        tgt = row.get("target")
        if not tgt or not row.get("evidence"):
            out[tgt] = "BLIND"          # nothing to tie it to at all
            continue
        m = copy.deepcopy(patch)
        for e in m["rows"][i]["evidence"]:
            if isinstance(e, dict):
                e["says"] = UNRELATED
        new = _failed_set(validate(m, targets)) - base_failed
        out[tgt] = "CHECKABLE" if new else "BLIND"
    return out


def how_scored(why: str) -> str:
    w = (why or "").lower()
    if re.search(r"\d+\s*(against|vs)\s*\d+|\(\d+%\)", w):
        return "numeric"
    if "key" in w:
        return "keys"
    if "fabricat" in w:
        return "fabricated"
    # ORDER IS LOAD-BEARING, corrected 2026-08-27 after audit A7.
    # `absent` MUST be tested before `hold`. score.py emits exactly one absent
    # string — "absent — no row and no hold" — and it contains "hold" inside
    # "no hold". With the old ordering, a target the harness went SILENT on was
    # reported as one it declined honestly: the exact inversion the
    # accountability gate exists to prevent ("silence is not an answer"),
    # committed by the instrument built to observe it.
    if w.startswith("absent") or "no row and no hold" in w:
        return "absent"
    if w.startswith("correct decline") or "hold" in w:
        return "declined"
    return "other"


def audit(cand_path, result_path, targets):
    patch = load_patch(cand_path)
    res = json.load(open(result_path, encoding="utf-8"))
    chk = checkability(patch, targets)

    rowset = {r.get("target") for r in (patch.get("rows") or [])}
    per = res.get("per_target") or []

    buckets = {}
    for pt in per:
        t, sc, why = pt.get("target"), pt.get("score", 0), pt.get("why", "")
        # only rows can be gate-checked; a decline/absence has no row to check
        cls = chk.get(t) if t in rowset else "NO-ROW"
        buckets.setdefault(cls, []).append((t, sc, how_scored(why), why))

    return res, buckets, rowset


def report(name, res, buckets, rowset):
    print(f"\n{'='*74}\n{name}   S = {res.get('S')}   "
          f"score {res.get('score')}/{res.get('max')}   verdict {res.get('verdict')}\n{'='*74}")

    earned_by = {}
    for cls in ("CHECKABLE", "BLIND", "NO-ROW"):
        rows = buckets.get(cls, [])
        if not rows:
            continue
        pos = sum(s for _, s, _, _ in rows if s > 0)
        neg = sum(s for _, s, _, _ in rows if s < 0)
        earned_by[cls] = pos
        print(f"\n  {cls}  —  {len(rows)} target(s), earned {pos:+d}, lost {neg:+d}")
        for t, s, mode, why in sorted(rows, key=lambda x: -x[1]):
            print(f"     {s:+d}  {mode:<11} {t:<44} {why[:44]}")

    total_earned = sum(earned_by.values()) or 1
    with_row = earned_by.get("CHECKABLE", 0) + earned_by.get("BLIND", 0)
    M = earned_by.get("CHECKABLE", 0) / with_row if with_row else 0.0

    print(f"\n  earned by CHECKABLE rows   {earned_by.get('CHECKABLE',0):+d}")
    print(f"  earned by BLIND rows       {earned_by.get('BLIND',0):+d}")
    print(f"  earned by declines/absent  {earned_by.get('NO-ROW',0):+d}  (no row to gate-check)")
    print(f"\n  M = CHECKABLE / (CHECKABLE + BLIND) = {M:.2f}   "
          f"grain: rubric points, denominator {with_row}")
    return M, earned_by


def main(argv):
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__)
        return 1
    targets = load_targets()
    out = []
    for i in range(0, len(argv), 2):
        cand, resj = argv[i], argv[i + 1]
        res, buckets, rowset = audit(cand, resj, targets)
        M, earned = report(os.path.basename(cand), res, buckets, rowset)
        out.append((os.path.basename(cand), res.get("S"), M, earned))

    if len(out) == 2:
        print(f"\n{'='*74}\nTHE CROSS — PLAN §3, applied without adjustment\n{'='*74}")
        (n1, s1, m1, e1), (n2, s2, m2, e2) = out
        print(f"\n  {'':<26}{n1:<28}{n2}")
        print(f"  {'S':<26}{s1:<28}{s2}")
        print(f"  {'M (mechanised share)':<26}{m1:<28.2f}{m2:.2f}")
        print(f"  {'earned · CHECKABLE':<26}{e1.get('CHECKABLE',0):<+28d}{e2.get('CHECKABLE',0):+d}")
        print(f"  {'earned · BLIND':<26}{e1.get('BLIND',0):<+28d}{e2.get('BLIND',0):+d}")

        d_chk = e2.get("CHECKABLE", 0) - e1.get("CHECKABLE", 0)
        d_bld = e2.get("BLIND", 0) - e1.get("BLIND", 0)
        d_tot = d_chk + d_bld
        print(f"\n  THE DELTA between arms:  CHECKABLE {d_chk:+d}   BLIND {d_bld:+d}   total {d_tot:+d}")
        # RETRACTED 2026-08-27. Earlier versions of this tool printed a "share
        # of the delta the gates could mechanically check" here, and both
        # ATTRIBUTION.md and LOG.md asserted the retraction was "left in the
        # tool with the note beside it". IT WAS NOT — audit A4 found zero
        # retraction text in this file. A claimed receipt that does not exist is
        # worse than a quiet edit. The note is now actually here.
        print("  share of that delta the gates could check:  RETRACTED — not computable.")
        print("    The arms are not comparable bucket-by-bucket: arm 1 has zero")
        print("    declines and arm 2 has nine, so the denominator changes sign.")
        print("    A number that cannot be computed is refused visibly, not omitted.")

        m = m2
        verdict = ("EARNED — the oracle carried it" if m >= 0.70 else
                   "MIXED — the claim is partial and must say so" if m >= 0.40 else
                   "RUBRIC-DOMINATED — the mechanical-oracle property is weaker "
                   "than advertised for this layer")
        print(f"\n  PRE-REGISTERED VERDICT (M = {m:.2f}):  {verdict}")

        if m1 < m2:
            print("\n  And the §3 additional check FIRED: the floor arm draws MORE of its")
            print("  score from BLIND rows than the site-corpus arm does — the blind class")
            print("  is where an ungrounded prior most easily hides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
