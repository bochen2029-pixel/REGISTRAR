#!/usr/bin/env python3
"""
Generate `targets.json` from `lifecycle.yml`.

The seed enumerates its own mutable surface: every `local_variation` entry in
the lifecycle is a legal patch target, and nothing else is. This script lifts
that list into a flat JSON index so the gates can run on a bare Python with
nothing installed, while the lifecycle itself stays human-readable YAML.

    python core/lifecycle/gen_targets.py           # write targets.json
    python core/lifecycle/gen_targets.py --check   # verify it is current

The generated file is committed. `--check` is what keeps it honest: if someone
adds a variation point to the lifecycle and forgets to regenerate, the gate
battery would silently refuse a legitimate target. The drift test catches that.

Requires pyyaml. Nothing else in this repository does.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIFECYCLE = os.path.join(HERE, "lifecycle.yml")
TARGETS = os.path.join(HERE, "targets.json")


def build() -> dict:
    try:
        import yaml
    except ImportError:
        print("pyyaml is required to regenerate targets.json (only for this script).", file=sys.stderr)
        raise SystemExit(3)

    with open(LIFECYCLE, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    targets: dict[str, dict] = {}
    for state in doc.get("states", []):
        for var in state.get("local_variation") or []:
            targets[var["id"]] = {
                "layer": var["layer"],
                "state": state["id"],
                "note": var.get("note", ""),
            }

    return {
        "$comment": (
            "GENERATED from lifecycle.yml by gen_targets.py. Do not edit by hand. "
            "This is the complete set of legal patch targets: the seed's declared "
            "mutable surface. A target absent from this file does not exist, and a "
            "patch row naming one fails the blast-radius gate."
        ),
        "schema_version": doc.get("schema_version"),
        "generated_from": "lifecycle.yml",
        "count": len(targets),
        "targets": dict(sorted(targets.items())),
    }


def main() -> int:
    fresh = build()
    if "--check" in sys.argv:
        if not os.path.exists(TARGETS):
            print("targets.json missing — run without --check")
            return 1
        with open(TARGETS, encoding="utf-8") as fh:
            current = json.load(fh)
        if current.get("targets") != fresh["targets"]:
            only_fresh = set(fresh["targets"]) - set(current.get("targets", {}))
            only_cur = set(current.get("targets", {})) - set(fresh["targets"])
            print("DRIFT: targets.json does not match lifecycle.yml")
            for t in sorted(only_fresh):
                print(f"  + {t}  (in lifecycle, missing from targets.json)")
            for t in sorted(only_cur):
                print(f"  - {t}  (in targets.json, gone from lifecycle)")
            return 1
        print(f"targets.json is current — {fresh['count']} targets")
        return 0

    with open(TARGETS, "w", encoding="utf-8") as fh:
        json.dump(fresh, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {TARGETS} — {fresh['count']} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
