#!/usr/bin/env python3
"""
REGISTRAR · core · profiles
─────────────────────────────────────────────────────────────────────────────
One clone, two artifacts. The profile decides what mounts.

    edr    (default)  the deployed record — coordinators, at three in the morning
    forge             the machinery that completes the seed into one site's shape

**`edr` is a strict subset of `forge`, and that is checked rather than trusted.**
It is the property that lets a site deploy a record system without inheriting
completion machinery it never asked for and cannot audit. If forge-only tooling
ever appears in the edr profile, `--check` fails and conformance fails with it.

TWO AXES, AND CONFUSING THEM IS EASY

    the profile      says WHAT MOUNTS       — a property of the deployment
    registrar.state  says WHO IS HOME       — off | shadow | live, a property
                                              of the moment, operator-written

`edr` + `off` is the default and a complete product: the seed, the floor, the
gates, the tape, computed on demand with nobody home. Everything above it is
optional.

    python core/profile.py                   what is active, and what it mounts
    python core/profile.py --profile forge   what the forge would mount
    python core/profile.py --check           is edr still a strict subset?
    python core/profile.py --explain elicit/ why is this not in the record?

Zero dependencies for reading the active profile. `--check` and `--explain`
parse the YAML and need pyyaml, like the other generators.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROFILES = os.path.join(ROOT, "profiles")
STATE_FILE = os.path.join(ROOT, "registrar.state")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_PROFILE = "edr"
STATES = ("off", "shadow", "live")


# ── the active profile ──────────────────────────────────────────────────────
def active_profile() -> str:
    """
    The profile in force. Environment, then default.

    Deliberately NOT a file the forge can write: a completion runs *inside* the
    forge profile and must not be able to widen it. Compare `registrar.state`,
    which is a file — but one only the operator writes.
    """
    p = os.environ.get("REGISTRAR_PROFILE", DEFAULT_PROFILE).strip().lower()
    return p if p in ("edr", "forge") else DEFAULT_PROFILE


def state() -> str:
    """
    Who is home. `off` unless the operator's file says otherwise.

    Reading a malformed or missing file yields `off`. That direction is not an
    accident: an unreadable switch must fail toward inert, never toward live.
    """
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            v = fh.read().strip().split()[0].lower()
        return v if v in STATES else "off"
    except Exception:
        return "off"


def is_forge() -> bool:
    return active_profile() == "forge"


def require_forge(what: str) -> None:
    """
    Guard for forge-only entry points.

    Called at the top of anything that must not run in a deployed record. The
    message names the reason rather than the rule, because a refusal that
    teaches nothing is a refusal somebody works around.
    """
    if not is_forge():
        raise SystemExit(
            f"{what} is forge-only, and this instance is running the '{active_profile()}' profile.\n"
            f"  The forge is the machinery that COMPLETES the seed — run once, by a site's IT team,\n"
            f"  and then never again. A deployed record does not need it and should not carry it.\n"
            f"  To run the completion:  REGISTRAR_PROFILE=forge python {what}"
        )


# ── reading the declarations ────────────────────────────────────────────────
def load(profile: str) -> dict:
    try:
        import yaml
    except ImportError:
        raise SystemExit("reading a profile declaration needs pyyaml (only this script does)")
    with open(os.path.join(PROFILES, f"{profile}.yml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _paths(entry: dict) -> list[str]:
    p = entry.get("path")
    if p is None:
        return []
    return list(p) if isinstance(p, list) else [p]


def mounted_paths(profile: str) -> set[str]:
    """Every path a profile mounts, including what it inherits."""
    doc = load(profile)
    out: set[str] = set()
    for key in ("mounts", "interval"):
        for e in doc.get(key) or []:
            out.update(_paths(e))
    parent = doc.get("extends")
    if parent:
        out |= mounted_paths(parent)
    return out


def excluded_paths(profile: str) -> dict[str, str]:
    doc = load(profile)
    return {p: (e.get("why") or "").strip()
            for e in (doc.get("excluded") or []) for p in _paths(e)}


# ── the check that matters ──────────────────────────────────────────────────
def check() -> int:
    edr, forge = mounted_paths("edr"), mounted_paths("forge")

    print("profile · subset")
    leaked = sorted(edr - forge)
    if leaked:
        print(f"  FAIL  edr mounts {len(leaked)} path(s) forge does not: {', '.join(leaked)}")
        print("        edr must be a STRICT SUBSET; a record cannot mount what the forge lacks.")
        return 1
    print(f"  ok    edr ({len(edr)}) ⊆ forge ({len(forge)})")

    # the real hazard: forge-only machinery appearing in the deployed record
    print("\nprofile · no completion machinery in the record")
    forge_only = {"forge/", "elicit/", "tools/cite.py", "corpus/", "examples/worked/",
                  "core/authorization/PROCEDURE.md", "core/authorization/fetch_states.py"}
    bled = sorted(p for p in edr if p in forge_only)
    if bled:
        print(f"  FAIL  the edr profile mounts forge machinery: {', '.join(bled)}")
        print("        A site deploying a record would inherit completion tooling it")
        print("        never asked for and cannot audit.")
        return 1
    print(f"  ok    {len(forge_only)} forge-only path(s), none in the record")

    # every exclusion must say why — an unexplained exclusion is an accident
    print("\nprofile · every exclusion carries its reason")
    mute = [p for p, why in excluded_paths("edr").items() if len(why) < 20]
    if mute:
        print(f"  FAIL  exclusions with no reason: {', '.join(mute)}")
        return 1
    print(f"  ok    {len(excluded_paths('edr'))} exclusions, each explained")

    # the forge must refuse the things that are refused by rule, not by taste
    print("\nprofile · the forge's refused capabilities are declared")
    refused = {r["id"] for r in (load("forge").get("refused") or [])}
    need = {"live_audio_video", "egress_site_material", "write_outside_fit"}
    missing = sorted(need - refused)
    if missing:
        print(f"  FAIL  the forge does not refuse: {', '.join(missing)}")
        return 1
    print(f"  ok    {len(refused)} refused: {', '.join(sorted(refused))}")

    print("\nGREEN — the record and the forge are one clone and two artifacts.")
    return 0


def explain(path: str) -> int:
    why = excluded_paths("edr").get(path.rstrip("/") + "/") or excluded_paths("edr").get(path)
    if why:
        print(f"{path} is NOT in the deployed record.\n\n  {why}")
        return 0
    if path in mounted_paths("edr"):
        print(f"{path} mounts in the record (edr profile).")
        return 0
    if path in mounted_paths("forge"):
        print(f"{path} mounts in the forge only.\n\n  Run: REGISTRAR_PROFILE=forge …")
        return 0
    print(f"{path} is not named by either profile.")
    return 1


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    if "--explain" in argv:
        return explain(argv[argv.index("--explain") + 1])

    prof = argv[argv.index("--profile") + 1] if "--profile" in argv else active_profile()
    doc = load(prof)

    print(f"profile: {prof}{'  (default)' if doc.get('default') else ''}")
    print(f"state:   {state()}   ({STATE_FILE if os.path.exists(STATE_FILE) else 'no state file — off'})")
    print(f"\n{doc.get('description', '')}\n")

    for e in doc.get("mounts") or []:
        print(f"  mount   {', '.join(_paths(e)) or e['id']}")
    if doc.get("extends"):
        print(f"  extends {doc['extends']}  (+{len(mounted_paths(doc['extends']))} paths)")
    for e in doc.get("interval") or []:
        st = e.get("status", "")
        print(f"  interval {', '.join(_paths(e))}  [{st}]" if st else f"  interval {', '.join(_paths(e))}")
    for c in doc.get("capabilities") or []:
        req = "required" if c.get("required") else "optional"
        print(f"  needs   {c['id']}  ({req})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
