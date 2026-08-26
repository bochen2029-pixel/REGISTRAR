#!/usr/bin/env python3
"""
REGISTRAR · gates · patch validation
─────────────────────────────────────────────────────────────────────────────
The first gates, implemented. This is the object a completing harness is graded
by, and it is written to be read as an objective function: every refusal names
the defect in words, because a gate that says "invalid" teaches nothing.

THREE STATES, AND THEY ARE NOT TWO

    GREEN            verified to pass
    PASS-UNVERIFIED  THE CHECK DID NOT RUN — treat exactly as failure
    FAILED           verified to fail

Some gates cannot be decided from a patch file alone. Local invertibility needs
a runtime to apply the row and compare; shadow-run honesty needs the site's own
tape. **Those report PASS-UNVERIFIED rather than GREEN**, and this file is
deliberately built so that the validator demonstrates the discipline it
enforces: a checker that quietly reported GREEN for a check it never ran would
be the exact failure the three-state gate exists to prevent.

Zero dependencies for JSON patches. YAML patches additionally need pyyaml —
JSON is a subset of YAML, so the two formats validate identically.

    python gates/validate_patch.py examples/worked/northlake.patch.json
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, HERE)
TARGETS = os.path.join(ROOT, "core", "lifecycle", "targets.json")

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"

REQUIRED_FIELDS = ["target", "value", "inverse", "evidence", "shadow_run", "expiry", "author"]
TARGET_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")

# Phrases that assert local practice without evidence. Not exhaustive, and not
# meant to be: the evidence gate is the real check. These catch the confident
# generality a model reaches for when it has nothing to cite.
WEASEL = (
    "standard practice", "typically", "commonly", "usually", "most opos",
    "best practice", "industry standard", "generally", "in general", "as expected",
)


class Result:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, state: str, gate: str, detail: str = "") -> None:
        self.rows.append((state, gate, detail))

    @property
    def worst(self) -> str:
        states = {s for s, _, _ in self.rows}
        if FAILED in states:
            return FAILED
        if UNVERIFIED in states:
            return UNVERIFIED
        return GREEN

    def render(self) -> str:
        out = []
        for state, gate, detail in self.rows:
            dots = "." * max(2, 34 - len(gate))
            line = f"  {state:<16}{gate} {dots} {detail}".rstrip()
            out.append(line)
        return "\n".join(out)


def load_patch(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            try:
                import yaml
            except ImportError:
                raise SystemExit("YAML patch requires pyyaml; JSON patches need nothing.")
            return yaml.safe_load(fh)
        return json.load(fh)


def load_targets() -> dict:
    with open(TARGETS, encoding="utf-8") as fh:
        return json.load(fh)["targets"]


# ── the gates ───────────────────────────────────────────────────────────────
def validate(patch: dict, targets: dict) -> Result:
    r = Result()
    rows = patch.get("rows") or []

    # 1 · shape
    bad = []
    for i, row in enumerate(rows):
        missing = [f for f in REQUIRED_FIELDS if f not in row]
        if missing:
            bad.append(f"row {i} ({row.get('target', '?')}) missing {', '.join(missing)}")
    r.add(FAILED if bad else GREEN, "schema shape",
          "; ".join(bad) if bad else f"{len(rows)} rows, all seven fields present")

    # 2 · blast radius — the target must be one the seed declared
    off = [row.get("target") for row in rows if row.get("target") not in targets]
    if off:
        r.add(FAILED, "blast radius",
              f"{len(off)} row(s) name a target the seed does not declare: {', '.join(map(str, off))}")
    else:
        r.add(GREEN, "blast radius", "0 rows outside the declared mutable surface")

    # 3 · target syntax
    malformed = [t for t in (row.get("target") for row in rows) if t and not TARGET_RE.match(str(t))]
    r.add(FAILED if malformed else GREEN, "target syntax",
          ", ".join(malformed) if malformed else "all targets well-formed")

    # 4 · layer — L0/L1/L4 are unreachable by construction; this confirms it held
    l0 = [row["target"] for row in rows
          if row.get("target") in targets and targets[row["target"]]["layer"] not in ("L2", "L3")]
    r.add(FAILED if l0 else GREEN, "L0/L1/L4 immutability",
          ", ".join(l0) if l0 else "no row touches a layer it may not author")

    # 5 · inverse present
    no_inv = [row.get("target") for row in rows if "inverse" not in row]
    r.add(FAILED if no_inv else GREEN, "inverse declared",
          ", ".join(map(str, no_inv)) if no_inv else "every row carries an inverse")

    # 6 · inverse actually inverts — DECIDED, as of core/algebra.py
    #
    # This gate reported PASS-UNVERIFIED from the day it was written, on the
    # reasoning that T3 "needs a runtime". That was half true: applying a row
    # to a live instance needs one, but T3's hypothesis is POINTWISE —
    # p⁻(p(λ)) ≃ λ at the state where the row is applied — and the patch file
    # plus the seed determine that state exactly. It was computable all along.
    try:
        from algebra import check_all, rows_from_patch  # noqa: E402
        inv = check_all(rows_from_patch(patch))
        bad = [x for x in inv if not x.ok]
        if bad:
            r.add(FAILED, "local invertibility",
                  "; ".join(x.render() for x in bad))
        else:
            r.add(GREEN, "local invertibility",
                  f"{len(inv)} row(s): p⁻(p(λ)) ≃ λ at the state each is applied")
    except ImportError:
        r.add(UNVERIFIED, "local invertibility",
              "core/algebra.py not importable — T3 not computed")

    # 7 · evidence binding
    weak = []
    for row in rows:
        ev = row.get("evidence") or []
        if not ev:
            weak.append(f"{row.get('target')}: no evidence")
            continue
        for e in ev:
            if not e.get("source") or not e.get("says"):
                weak.append(f"{row.get('target')}: evidence missing source or says")
            elif any(w in str(e.get("says", "")).lower() for w in WEASEL):
                weak.append(f"{row.get('target')}: asserts generality, not this site ('{e['says'][:40]}…')")
    r.add(FAILED if weak else GREEN, "evidence binding",
          "; ".join(weak) if weak else "every row cites a source in the site's own material")

    # 8 · shadow run present, with a denominator
    nosr = []
    for row in rows:
        sr = row.get("shadow_run") or {}
        if not sr:
            nosr.append(f"{row.get('target')}: no shadow run")
        elif not sr.get("cases"):
            nosr.append(f"{row.get('target')}: shadow run has no denominator")
    r.add(FAILED if nosr else GREEN, "shadow run",
          "; ".join(nosr) if nosr else "every row replayed, every count has a denominator")

    # 9 · shadow run is truthful — NOT decidable here
    r.add(UNVERIFIED, "shadow-run fidelity",
          "needs the site's tape to confirm the replay actually happened")

    # 10 · expiry
    badexp = []
    for row in rows:
        e = row.get("expiry")
        try:
            _dt.date.fromisoformat(str(e))
        except Exception:
            badexp.append(f"{row.get('target')}: expiry {e!r} is not a date")
    r.add(FAILED if badexp else GREEN, "expiry",
          "; ".join(badexp) if badexp else "every row re-earns its place on a date")

    # 11 · totality on provision — the silent breaker of convergence
    partial = [row.get("target") for row in rows
               if isinstance(row.get("value"), dict) and row["value"].get("__partial__")]
    if partial:
        r.add(FAILED, "totality on provision",
              f"row(s) declare a partial application: {', '.join(map(str, partial))}")
    else:
        r.add(UNVERIFIED, "totality on provision",
              "structural check passed; whether application installs every declared key needs a runtime")

    # 11b · divergence — do the three layers of a row agree?
    #
    # Every row exists three times: what it SAYS (value), what it CITES
    # (evidence), what HAPPENED (shadow_run). Gates 7 and 8 check each
    # separately. Nothing checked that they agree — and the three fields are
    # formatted as one story, so a reviewer reads them as one. The catches live
    # in the disagreements.
    try:
        from divergence import validate as _div
        dstate, dmsgs = _div(patch)
        r.add(dstate, "divergence",
              "; ".join(dmsgs)[:200] if dmsgs
              else "value, evidence and replay tell the same story")
    except ImportError:
        r.add(UNVERIFIED, "divergence", "gates/divergence.py not importable")

    # 11c · schema conformance — does the file match the contract it claims?
    #
    # patch.schema.json shipped from the beginning and NOTHING EVER VALIDATED
    # AGAINST IT. That is why two defects sat in it undetected until an
    # independent completion run reported them: `derived_from` was documented by
    # gate 13 and undeclared here, and a declined target had no home. A schema
    # nothing runs is a document, not a contract.
    try:
        sys.path.insert(0, os.path.join(ROOT, "schema"))
        import json as _json

        from validate import SCHEMA as _S
        from validate import validate as _sv
        with open(_S, encoding="utf-8") as _fh:
            _root = _json.load(_fh)
        _fails = _sv(patch, _root, _root)
        r.add(FAILED if _fails else GREEN, "schema conformance",
              "; ".join(_fails[:3])[:200] if _fails
              else "valid against patch.schema.json")
    except Exception as _exc:
        r.add(UNVERIFIED, "schema conformance", f"validator unavailable: {_exc}")

    # 11d · accountability — a row or a hold for every declared target
    #
    # SILENCE IS NOT AN ANSWER. A target with neither could mean the harness
    # looked and found nothing, that it never looked, or that the site has no
    # local variation there — and a reviewer cannot tell which. The absences are
    # where the risk is, and nothing checked them until 2026-08-26.
    #
    # Found by measurement: F-PATCH-DELTA's arm-2 candidate accounted for 20 of
    # 20 unprompted, and the worked example was silent on 12 of 20.
    try:
        from accountability import validate as _acct
        _st, _msgs = _acct(patch)
        r.add(_st, "accountability", "; ".join(_msgs)[:200])
    except Exception as _exc:
        r.add(UNVERIFIED, "accountability", f"unavailable: {_exc}")

    # 11e · attest — does the CLAIM support the value?
    #
    # cite.py checks a QUOTE byte-exact. divergence checks the NUMBERS. Neither
    # reads the evidence AS PROSE — so a superseded rule offered for a current
    # value passed silently, measured 2026-08-26.
    try:
        from attest import validate as _att
        _st, _msgs = _att(patch)
        r.add(_st, "attest", "; ".join(_msgs)[:200])
    except Exception as _exc:
        r.add(UNVERIFIED, "attest", f"unavailable: {_exc}")

    # 12 · signature — the output commit
    unsigned = [row.get("target") for row in rows if not str(row.get("author") or "").strip()]
    if unsigned:
        r.add(UNVERIFIED, "signature",
              f"{len(unsigned)} row(s) unsigned — legal in a draft, fatal at mount")
    else:
        r.add(GREEN, "signature", "every row carries a named human")

    return r


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    patch = load_patch(argv[1])
    targets = load_targets()
    site = (patch.get("site") or {}).get("id", "?")
    rows = patch.get("rows") or []

    print(f"patch: {argv[1]}")
    print(f"site : {site}   rows: {len(rows)}\n")

    r = validate(patch, targets)
    print(r.render())

    print()
    if r.worst == GREEN:
        print("GREEN — every gate passed. A human may now read and sign it.")
        return 0
    if r.worst == UNVERIFIED:
        print("PASS-UNVERIFIED — nothing failed, but checks did not run.")
        print("  This is NOT a pass. Treat it exactly as failure until the")
        print("  unverified gates are run against a runtime and the site's tape.")
        return 2
    print("FAILED — the defects above are named. Fix the rows; nothing mounts.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
