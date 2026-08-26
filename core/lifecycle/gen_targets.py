#!/usr/bin/env python3
"""
Generate the machine-readable forms of `lifecycle.yml`.

Emits two files, both committed:

  targets.json    the declared mutable surface — every legal patch target
  lifecycle.json  states, transitions and guards, for the runtime

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
MACHINE = os.path.join(HERE, "lifecycle.json")


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


def build_machine() -> dict:
    """States, transitions and guards — what the runtime needs, without the prose."""
    try:
        import yaml
    except ImportError:
        print("pyyaml is required to regenerate (only for this script).", file=sys.stderr)
        raise SystemExit(3)

    with open(LIFECYCLE, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    states = {}
    for st in doc.get("states", []):
        states[st["id"]] = {
            "name": st.get("name", st["id"]),
            "terminal": bool(st.get("terminal")),
            "grain": st.get("grain", "case"),
            "concurrent_with": st.get("concurrent_with") or [],
            "requires_elements": st.get("requires_elements") or [],
            # an element whose locator is unverified is a TODO, not a mandate —
            # the runtime must know which is which
            "verified": all(
                (p or {}).get("locator") not in (None, "TODO-VERIFY")
                for p in (st.get("provenance") or [])
            ) if st.get("provenance") else False,
        }

    transitions = [
        {"from": t["from"], "to": t["to"], "guard": t.get("guard") or []}
        for t in doc.get("transitions", [])
    ]

    return {
        "$comment": (
            "GENERATED from lifecycle.yml by gen_targets.py. Do not edit by hand. "
            "`verified: false` means the element's provenance locator is still "
            "TODO-VERIFY — per PROVENANCE.md §2 that element is not implemented, "
            "and no validator may enforce it."
        ),
        "schema_version": doc.get("schema_version"),
        "generated_from": "lifecycle.yml",
        "states": states,
        "transitions": transitions,
    }


def main() -> int:
    fresh = build()
    machine = build_machine()
    if "--check" in sys.argv:
        if not os.path.exists(TARGETS):
            print("targets.json missing — run without --check")
            return 1
        with open(TARGETS, encoding="utf-8") as fh:
            current = json.load(fh)
        drift = False
        if os.path.exists(MACHINE):
            with open(MACHINE, encoding="utf-8") as fh:
                cur_m = json.load(fh)
            if cur_m.get("states") != machine["states"] or cur_m.get("transitions") != machine["transitions"]:
                print("DRIFT: lifecycle.json does not match lifecycle.yml")
                drift = True
        else:
            print("lifecycle.json missing — run without --check")
            drift = True
        if current.get("targets") != fresh["targets"]:
            only_fresh = set(fresh["targets"]) - set(current.get("targets", {}))
            only_cur = set(current.get("targets", {})) - set(fresh["targets"])
            print("DRIFT: targets.json does not match lifecycle.yml")
            for t in sorted(only_fresh):
                print(f"  + {t}  (in lifecycle, missing from targets.json)")
            for t in sorted(only_cur):
                print(f"  - {t}  (in targets.json, gone from lifecycle)")
            drift = True
        if drift:
            return 1
        print(f"current — {fresh['count']} targets, {len(machine['states'])} states, "
              f"{len(machine['transitions'])} transitions")
        return 0

    with open(TARGETS, "w", encoding="utf-8") as fh:
        json.dump(fresh, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(MACHINE, "w", encoding="utf-8") as fh:
        json.dump(machine, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote targets.json — {fresh['count']} targets")
    print(f"wrote lifecycle.json — {len(machine['states'])} states, {len(machine['transitions'])} transitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
