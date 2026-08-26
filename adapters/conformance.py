#!/usr/bin/env python3
"""
REGISTRAR · adapters · conformance
─────────────────────────────────────────────────────────────────────────────
An adapter that cannot demonstrate it survives a **malformed** message, a
**late** result, and a result arriving **after disposition** does not mount.

Those three are universal — required of every adapter whether or not its author
expected them — and each is here for a reason from the domain rather than from
software taste:

  malformed          every interface emits garbage eventually, and a HALF-PARSED
                     result is a fabricated clinical fact wearing the formatting
                     of a real one.

  late               **the normal case here, not the edge.** The whole reason
                     floor/closure.py exists is that the failure is almost
                     always the interval.

  post-disposition   OPTN Policy 2.12 REQUIRES post-procurement results be
                     obtained and reported — *disposition does not close the
                     case.* An adapter that drops these is non-compliant, not
                     merely lossy.

THIS FILE CHECKS THE DECLARATION, NOT A LIVE INTERFACE.

    Every binding in this repository is `null` and will stay that way: a real
    Epic or Cerner integration needs interface specifications an OPO holds, and
    **inventing one would be exactly the fabrication tools/cite.py exists to
    prevent.** What is checkable without a binding is whether the adapter has
    DECLARED what it does, what it refuses, what it costs, and what it
    replaces — and that turns out to be most of what goes wrong.

    An unbound adapter reports PASS-UNVERIFIED. That is the honest state, not a
    degraded one.

    python adapters/conformance.py
    python adapters/conformance.py --adapter lab

Zero dependencies beyond pyyaml, which only this checker needs.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"

# Required of every adapter, whatever it connects to.
UNIVERSAL = {
    "malformed": "a message that does not parse — never partially parse",
    "late": "a result after the deadline it informs — the normal case here",
    "post_disposition": "a result after the case closed — OPTN 2.12 requires it be reported",
}

# An adapter may only claim to produce elements the lifecycle declares.
def declared_elements() -> set[str]:
    import json
    p = os.path.join(ROOT, "core", "lifecycle", "lifecycle.json")
    with open(p, encoding="utf-8") as fh:
        m = json.load(fh)
    out: set[str] = set()
    for t in m.get("transitions", []):
        out.update(t.get("guard") or [])
    for s in m.get("states", {}).values():
        out.update(s.get("requires_elements") or [])
    return out


RESULTS: list[tuple[str, str, str]] = []


def record(state: str, name: str, detail: str = "") -> None:
    RESULTS.append((state, name, detail))
    dots = "." * max(2, 36 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


def check_adapter(name: str, doc: dict, elements: set[str]) -> None:
    print(f"\nadapter · {name}")

    # ── 1 · declares what it ingests ────────────────────────────────────────
    ing = doc.get("ingests") or {}
    record(GREEN if ing.get("source") else FAILED, "declares a source",
           ing.get("source", "no `ingests.source`"))

    # version specificity: the failure that makes a fit stop fitting silently
    unbound = [k for k in ("transport", "format") if ing.get(k) is None]
    record(UNVERIFIED if unbound else GREEN, "transport and format",
           f"{', '.join(unbound)} unbound — site-declared, WITH the version"
           if unbound else f"{ing.get('transport')} / {ing.get('format')}")

    # ── 2 · produces a closed list, and never a transition ──────────────────
    prod = doc.get("produces") or []
    claimed = {p.get("element") for p in prod if isinstance(p, dict)}
    record(GREEN if claimed else FAILED, "produces a closed list",
           f"{len(claimed)} element(s)" if claimed
           else "an adapter that could produce anything is a write path")

    unknown = sorted(e for e in claimed if e and e not in elements)
    record(FAILED if unknown else GREEN, "elements exist in the lifecycle",
           f"not declared by the seed: {', '.join(unknown)}" if unknown
           else "every claimed element is one the spine knows")

    forbidden = doc.get("may_not_produce") or []
    has_transition_bar = any("transition" in str(f).lower() for f in forbidden)
    record(GREEN if has_transition_bar else FAILED, "never produces a transition",
           "declared — the adapter observes, the spine decides"
           if has_transition_bar else "must declare it cannot produce transitions")

    # ── 3 · the three universal failure modes ───────────────────────────────
    modes = {m.get("id"): m for m in (doc.get("failure_modes") or []) if isinstance(m, dict)}
    missing = sorted(k for k in UNIVERSAL if k not in modes)
    record(FAILED if missing else GREEN, "the three universal failures",
           f"undeclared: {', '.join(missing)}" if missing
           else "malformed · late · post-disposition, each with a `must`")

    mute = sorted(k for k, m in modes.items() if not (m.get("must") or "").strip())
    record(FAILED if mute else GREEN, "each failure names its response",
           f"no `must`: {', '.join(mute)}" if mute
           else f"{len(modes)} failure mode(s), each says what it does")

    # ── 4 · latency, and the rule that makes it useful ──────────────────────
    lat = doc.get("latency") or {}
    if lat:
        obs, con = lat.get("observed"), lat.get("contracted")
        if obs is None:
            record(UNVERIFIED, "latency observed",
                   "unbound — and the OBSERVED figure is the authoritative one")
        else:
            record(GREEN, "latency observed", f"observed {obs}, contracted {con}")
        record(GREEN if "optimistic" in (lat.get("rule") or "") else UNVERIFIED,
               "latency rule stated",
               "observed is authoritative; contracted is cited so the gap is visible"
               if "optimistic" in (lat.get("rule") or "") else "no rule declared")

    # ── 5 · the null, keyed `beats` ─────────────────────────────────────────
    # A bare `null:` key parses as the None KEY in YAML, so the field silently
    # vanishes and the adapter reads as having declared nothing. Caught on the
    # first run of the first adapter. The checker now REFUSES the trap rather
    # than tolerating it, so no future adapter can lose a field to it.
    if None in doc:
        record(FAILED, "reserved key",
               "a bare `null:` key parsed as None and its contents were lost — use `beats:`")
    beats = doc.get("beats") or {}
    record(GREEN if beats.get("what") else FAILED, "names its null",
           beats.get("what", "no `beats` — an adapter that cannot name what it "
                             "replaces cannot show it beats it")[:70])
    record(GREEN if beats.get("kill_condition") else FAILED, "names its kill condition",
           "stated — if the null wins, the funeral prints"
           if beats.get("kill_condition") else "no kill condition")

    # ── 6 · provenance ──────────────────────────────────────────────────────
    prov = doc.get("provenance") or {}
    record(GREEN if prov.get("rule") else FAILED, "provenance rule",
           "public docs, a published standard, or a spec that stays at the site"
           if prov.get("rule") else "no provenance rule")

    # ── 7 · the binding ─────────────────────────────────────────────────────
    b = doc.get("binding")
    if b is None:
        record(UNVERIFIED, "binding",
               "null — the shell is real; a real integration needs specs an OPO holds")
    else:
        need = [k for k in ("version", "source", "pin", "entry", "licence") if not b.get(k)]
        record(FAILED if need else GREEN, "binding complete",
               f"missing {', '.join(need)}" if need else f"{b.get('licence')}, pinned")
        if not need and not b.get("licence"):
            record(FAILED, "binding licence",
                   "a binding without a licence cannot mount into an MIT tree")


def main(argv: list[str]) -> int:
    only = argv[argv.index("--adapter") + 1] if "--adapter" in argv else None

    try:
        import yaml
    except ImportError:
        print("adapters/conformance.py needs pyyaml (only this checker does)")
        return 3

    elements = declared_elements()
    print("REGISTRAR · adapters · conformance")
    print(f"the spine declares {len(elements)} guard elements an adapter may produce")

    found = 0
    for entry in sorted(os.listdir(HERE)):
        d = os.path.join(HERE, entry)
        y = os.path.join(d, "adapter.yml")
        if not os.path.isdir(d) or not os.path.exists(y):
            continue
        if only and entry != only:
            continue
        with open(y, encoding="utf-8") as fh:
            check_adapter(entry, yaml.safe_load(fh), elements)
        found += 1

    if not found:
        print("\nno adapters declared.")
        print("`adapters/` is the largest single share of the six years, and it is")
        print("empty on purpose until a shape exists. See CONTRACT.md.")
        return 0

    states = {s for s, _, _ in RESULTS}
    n_g = sum(1 for s, _, _ in RESULTS if s == GREEN)
    n_u = sum(1 for s, _, _ in RESULTS if s == UNVERIFIED)
    n_f = sum(1 for s, _, _ in RESULTS if s == FAILED)
    print(f"\n{n_g} GREEN · {n_u} PASS-UNVERIFIED · {n_f} FAILED   ({found} adapter(s))")

    if FAILED in states:
        print("\nFAILED — an adapter that cannot declare what it refuses does not mount.")
        return 1
    if UNVERIFIED in states:
        print("\nPASS-UNVERIFIED — the declarations hold and no binding exists.")
        print("  That is the honest state: the shell is real, and a real integration")
        print("  needs interface specifications an OPO holds. THIS IS NOT A PASS.")
        return 2
    print("\nGREEN — declared and bound.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
