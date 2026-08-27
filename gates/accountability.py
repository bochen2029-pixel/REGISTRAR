#!/usr/bin/env python3
"""
REGISTRAR · gates · accountability

**Every declared variation point must be accounted for: a row, or a hold. Never
silence.**

The seed enumerates its own mutable surface — twenty `local_variation` points,
lifted into `targets.json`. A completion may answer a target, or decline it and
say why. **What it may not do is say nothing**, because silence is
indistinguishable from three very different things:

  · the harness looked and found nothing            → a hold, and a finding
  · the harness never looked                        → incomplete work
  · the site genuinely has no local variation there → also a hold

A reviewer reading a patch with eight rows cannot tell which of those produced
the twelve absences. **The absences are where the risk is**, and they were the
one thing nothing in this repository checked.

FOUND BY MEASUREMENT, NOT BY INSPECTION. F-PATCH-DELTA's arm-② candidate
accounted for **20 of 20** targets — 11 rows and 9 holds — and it did that
because it chose to, not because anything required it. Checking the worked
example against the same standard showed **8 rows and 12 silences.** The
teaching example was demonstrating the defect.

This is `REJECTED.md`'s *"silent one"* at the file level rather than the row
level: **no error, no symptom, and a reviewer with no way to know.**

    python gates/accountability.py <patch>

Zero dependencies.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"


def declared_targets() -> set[str]:
    with open(os.path.join(ROOT, "core", "lifecycle", "targets.json"), encoding="utf-8") as fh:
        t = json.load(fh)["targets"]
    return set(t) if isinstance(t, dict) else {x["id"] for x in t}


def holds_of(patch: dict) -> list[dict]:
    """
    `holds` is the declared field. `$holds` is accepted because the schema had
    no home for a decline until 2026-08-26, and a patch written before that had
    nowhere else to put one.
    """
    return list(patch.get("holds") or patch.get("$holds") or [])


def validate(patch: dict) -> tuple[str, list[str]]:
    declared = declared_targets()
    filed = {r.get("target") for r in (patch.get("rows") or [])}
    held = {h.get("target") for h in holds_of(patch)}

    silent = sorted(declared - filed - held)
    both = sorted(filed & held)
    unknown = sorted(t for t in (held - declared) if t)

    msgs: list[str] = []
    if silent:
        msgs.append(
            f"{len(silent)} declared target(s) neither answered nor declined: "
            + ", ".join(silent[:6]) + (" …" if len(silent) > 6 else ""))
    if both:
        # A target cannot be both answered and declined. One of the two is stale.
        msgs.append(f"answered AND declined: {', '.join(both)}")
    if unknown:
        msgs.append(f"held target(s) the seed does not declare: {', '.join(unknown)}")

    # A hold with no search behind it is an omission wearing a label.
    # `reason` is the declared field; `why` is accepted because the schema had no
    # home for a decline until 2026-08-26. The shape itself came from an
    # independent completion run rather than from this repository guessing.
    thin = [h.get("target") for h in holds_of(patch)
            if len(str(h.get("searched", "")).strip()) < 3
            or len(str(h.get("reason") or h.get("why") or "").strip()) < 3]
    if thin:
        msgs.append(f"hold(s) missing `searched` or `why`: {', '.join(str(t) for t in thin)}")

    if silent or both or unknown or thin:
        return FAILED, msgs

    return GREEN, [f"{len(filed)} answered + {len(held)} declined = "
                   f"{len(declared)} declared; nothing silent"]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    path = argv[0]
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            try:
                import yaml
            except ImportError:
                raise SystemExit("this input is YAML and pyyaml is absent — "
                                 "install pyyaml, or supply the JSON form")
            patch = yaml.safe_load(fh)
        else:
            patch = json.load(fh)

    state, msgs = validate(patch)
    print(f"accountability · {os.path.relpath(path, ROOT)}\n")
    for m in msgs:
        print(f"  {m}")
    print()
    if state == FAILED:
        print("FAILED — silence is not an answer.")
        print("  A target with no row and no hold could mean the harness looked and")
        print("  found nothing, or that it never looked. A reviewer cannot tell, and")
        print("  the absences are where the risk is.")
        return 1
    print("GREEN — every declared target is accounted for.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
