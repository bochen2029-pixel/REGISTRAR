#!/usr/bin/env python3
"""
F-PATCH-DELTA · is the experiment well-posed?

The design said "give a harness only PUBLIC material for a second OPO." This
answers whether that is possible, **by counting rather than by reasoning** — and
the answer changed the experiment. See `PREREGISTRATION.md` §0.

    python experiments/F-PATCH-DELTA/audit_public_material.py

Re-run it whenever `elicit/questions.yml` or the worked example changes. **If it
ever reports a non-zero public count, the arm-② decision must be revisited.**
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Words that would appear if a source were publishable. Deliberately generous —
# a generous test that still returns zero is a stronger finding than a strict one.
PUBLIC_HINT = ("public", "website", "press", "cms ", "srtr", "optn report",
               "published", "annual report", "form 990", "news")


def main() -> int:
    print("F-PATCH-DELTA · can the experiment use public material?")
    print()

    with open(os.path.join(ROOT, "examples", "worked", "northlake.patch.json"),
              encoding="utf-8") as fh:
        patch = json.load(fh)

    ev = [e for r in patch.get("rows", []) for e in (r.get("evidence") or [])]
    kinds: dict[str, int] = {}
    pub_ev = 0
    for e in ev:
        k = e.get("kind", "?")
        kinds[k] = kinds.get(k, 0) + 1
        blob = (str(e.get("source", "")) + " " + str(e.get("says", ""))).lower()
        if any(h in blob for h in PUBLIC_HINT):
            pub_ev += 1

    print("the worked example's evidence, by kind:")
    for k, n in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {n:>3}  {k}")
    print()
    print(f"  {pub_ev} of {len(ev)} evidence items are plausibly public")
    print()

    try:
        import yaml
    except ImportError:
        print("(pyyaml unavailable - question audit skipped)")
        return 0

    with open(os.path.join(ROOT, "elicit", "questions.yml"), encoding="utf-8") as fh:
        qs = yaml.safe_load(fh)["questions"]

    pub_q = [q["target"] for q in qs
             if any(h in " ".join(str(s).lower() for s in (q.get("sources") or []))
                    for h in PUBLIC_HINT)]

    print(f"  {len(pub_q)} of {len(qs)} elicit questions name a plausibly public source")
    for t in pub_q:
        print(f"    {t}")

    print()
    print("-" * 70)

    if pub_ev == 0 and not pub_q:
        print("FINDING: nothing a patch row rests on is public.")
        print()
        print("  An OPO's public surface describes WHAT IT IS, not HOW IT RUNS. The")
        print("  elicitation targets the case tape, SOPs, the call rotation, service-desk")
        print("  history, written hospital agreements, and lab and transport contracts -")
        print("  none publishable, and that is the THESIS rather than an oversight.")
        print()
        print("  The experiment as originally specified would have measured the MATERIAL")
        print("  rather than the harness, and a negative result would be uninformative.")
        print("  Arm 2 is a synthetic site instead - PREREGISTRATION.md section 2,")
        print("  including what that costs and what it therefore cannot claim.")
        return 0

    print("Some public material exists. REVISIT the arm-2 decision before running.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
