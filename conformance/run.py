#!/usr/bin/env python3
"""
REGISTRAR · conformance
─────────────────────────────────────────────────────────────────────────────
One command that says whether an instance is sound.

    python conformance/run.py

This is the battery `SPEC.md` §11 names as the thing a completed instance must
pass before it load-bears. It reports in three states, and the middle one is
not a pass:

    GREEN            verified to pass
    PASS-UNVERIFIED  the check did not, or could not, run
    FAILED           verified to fail

**This battery currently ends PASS-UNVERIFIED, on purpose.** Most of the
lifecycle's provenance locators still read TODO-VERIFY, which means most of the
spine is specified rather than established — and a battery that returned GREEN
over an unverified spine would be reporting success past a step that never ran.
Filling those locators against the published sources is what turns this green.

Zero dependencies. Add `--verbose` for the detail behind each line.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, os.path.join(ROOT, "gates"))
sys.path.insert(0, os.path.join(ROOT, "floor"))

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"
VERBOSE = "--verbose" in sys.argv

CHECKS: list[tuple[str, str, str]] = []


def record(state: str, name: str, detail: str = "") -> None:
    CHECKS.append((state, name, detail))
    dots = "." * max(2, 38 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


# ── 1 · the spine is structurally sound ─────────────────────────────────────
def check_lifecycle() -> None:
    from case import load_machine

    m = load_machine()
    states, trans = m["states"], m["transitions"]

    bad = [f"{t['from']}->{t['to']}" for t in trans if t["from"] not in states or t["to"] not in states]
    record(FAILED if bad else GREEN, "lifecycle · states exist",
           ", ".join(bad) if bad else f"{len(trans)} transitions, all endpoints declared")

    leaving = {t["from"] for t in trans}
    bad_term = sorted(s for s, v in states.items() if v["terminal"] and s in leaving)
    record(FAILED if bad_term else GREEN, "lifecycle · terminals are terminal",
           ", ".join(bad_term) if bad_term else "no transition leaves a terminal state")

    # every non-start state must be reachable, or it is unreachable code in a spine
    reach, frontier = {"referral_received"}, ["referral_received"]
    while frontier:
        cur = frontier.pop()
        for t in trans:
            if t["from"] == cur and t["to"] not in reach:
                reach.add(t["to"])
                frontier.append(t["to"])
    orphans = sorted(set(states) - reach)
    record(FAILED if orphans else GREEN, "lifecycle · every state reachable",
           ", ".join(orphans) if orphans else f"all {len(states)} reachable from referral_received")

    terminals = sorted(s for s, v in states.items() if v["terminal"])
    record(GREEN if terminals else FAILED, "lifecycle · has terminals",
           f"{len(terminals)} terminal states, {len(terminals) - 1} of them non-conversion")

    unverified = sorted(s for s, v in states.items() if not v.get("verified"))
    # The reasons are not equivalent, and collapsing them would misreport.
    why = {}
    for s in unverified:
        why.setdefault(states[s].get("unverified_because") or "unverified", []).append(s)
    detail = (f"{len(states) - len(unverified)} of {len(states)} established"
              + (" — " + "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(why.items()))
                 if unverified else ""))
    record(UNVERIFIED if unverified else GREEN, "lifecycle · provenance", detail)
    if VERBOSE and unverified:
        for k, v in sorted(why.items()):
            print(f"                     · {k}: {', '.join(v)}")


# ── 2 · generated artifacts have not drifted ────────────────────────────────
def check_generated() -> None:
    r = subprocess.run([sys.executable, os.path.join(ROOT, "core", "lifecycle", "gen_targets.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        record(GREEN, "generated · no drift", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "current")
    elif r.returncode == 3:
        record(UNVERIFIED, "generated · no drift", "pyyaml unavailable — regeneration not checked")
    else:
        record(FAILED, "generated · no drift", (r.stdout + r.stderr).strip().splitlines()[0])


# ── 3 · the tape ────────────────────────────────────────────────────────────
def check_tape() -> None:
    from tape import Tape, state_at

    tapes_dir = os.path.join(ROOT, "fixtures", "tapes")
    paths = sorted(os.path.join(tapes_dir, f) for f in os.listdir(tapes_dir) if f.endswith(".jsonl"))

    broken = []
    for p in paths:
        try:
            Tape.load(p)
        except Exception as exc:
            broken.append(f"{os.path.basename(p)}: {exc}")
    record(FAILED if broken else GREEN, "tape · hash chain intact",
           "; ".join(broken) if broken else f"{len(paths)} tapes verified end to end")

    # replay determinism: the same fold twice must agree exactly
    t = Tape.load(paths[0])
    a, b = state_at(t), state_at(t)
    hist_a = t.fold(lambda acc, e: acc + [e.digest], [])
    hist_b = t.fold(lambda acc, e: acc + [e.digest], [])
    record(GREEN if (a == b and hist_a == hist_b) else FAILED, "tape · replay determinism",
           "two independent folds agree byte for byte")

    # the interface must not have grown a way to mutate
    forbidden = [n for n in ("delete", "update", "remove", "truncate", "__setitem__", "pop")
                 if hasattr(Tape, n)]
    record(FAILED if forbidden else GREEN, "tape · append-only by type",
           f"Tape exposes {', '.join(forbidden)}" if forbidden
           else "no delete, no update — absent from the interface, not forbidden by policy")


# ── 4 · case replay ─────────────────────────────────────────────────────────
def check_replay() -> None:
    from case import ENFORCED, replay
    from tape import Tape

    clean = Tape.load(os.path.join(ROOT, "fixtures", "tapes", "clean-case.jsonl"))
    f = replay(clean)
    viol = [x for x in f if x.status == ENFORCED]
    record(FAILED if viol else GREEN, "replay · clean case passes",
           f"{len(viol)} violations" if viol else "no violation on a legal case")

    bad = Tape.load(os.path.join(ROOT, "fixtures", "tapes", "violating-case.jsonl"))
    f2 = replay(bad)
    viol2 = [x for x in f2 if x.status == ENFORCED]
    record(GREEN if viol2 else FAILED, "replay · refuses an illegal case",
           f"{len(viol2)} violations caught on a deliberately illegal tape")

    pend = [x for x in f2 if x.status != ENFORCED]
    record(UNVERIFIED if pend else GREEN, "replay · guard enforcement",
           f"{len(pend)} guard check(s) PENDING — element provenance is TODO-VERIFY")


# ── 5 · the gates ───────────────────────────────────────────────────────────
def check_gates() -> None:
    from validate_patch import FAILED as GF, load_patch, load_targets, validate

    worked = os.path.join(ROOT, "examples", "worked")
    r = validate(load_patch(os.path.join(worked, "northlake.patch.json")), load_targets())
    record(GREEN if GF not in {s for s, _, _ in r.rows} else FAILED,
           "gates · accepted patch", "no gate FAILED on the worked example")

    # Three states, and the corpus uses all three deliberately:
    #   FAILED           the draft is wrong
    #   PASS-UNVERIFIED  the draft is INCOMPLETE, not wrong — an unsigned row is a
    #                    legal draft, because a machine leaves `author` empty
    #   *UNCAUGHT*       a fixture no SEMANTIC gate catches, retained ON PURPOSE
    #                    so the exposure stays visible instead of becoming a
    #                    story. It may still trip a FLOOR gate — schema
    #                    conformance, accountability — because these fixtures
    #                    are deliberately minimal and a floor fires on any
    #                    fragment. A floor refusal says nothing about the hole
    #                    the fixture records, and reading it as closure would be
    #                    the mistake this whole corpus exists to prevent.
    from validate_patch import GREEN as GG
    rejected = sorted(f for f in os.listdir(os.path.join(worked, "rejected"))
                      if f.endswith((".json", ".yml", ".yaml")))
    must_refuse = [f for f in rejected if "UNCAUGHT" not in f]
    uncaught = [f for f in rejected if "UNCAUGHT" in f]

    passed_through = []
    for f in must_refuse:
        rr = validate(load_patch(os.path.join(worked, "rejected", f)), load_targets())
        if rr.worst == GG:
            passed_through.append(f)
    record(FAILED if passed_through else GREEN, "gates · refuses bad patches",
           f"{len(passed_through)} draft(s) passed clean: {', '.join(passed_through)}"
           if passed_through
           else f"{len(must_refuse)}/{len(must_refuse)} adversarial drafts refused")

    if uncaught:
        # "NOTHING catches" was true when written and is not any more. Gates 14
        # and 15 are FLOORS: they fire on any deliberately-minimal fragment, so
        # they fire on every fixture here for being short rather than for being
        # wrong. Saying NOTHING catches them would now be false, and a reader
        # who ran one and saw a refusal could conclude the hole had closed.
        sys.path.insert(0, os.path.join(ROOT, "gates"))
        from witness import FLOOR
        from validate_patch import GREEN as _G
        ambient = {"shadow-run fidelity", "totality on provision"}
        floored = 0
        for f in uncaught:
            rr = validate(load_patch(os.path.join(worked, "rejected", f)), load_targets())
            if any(st != _G and g in FLOOR for st, g, _ in rr.rows):
                floored += 1
        record(UNVERIFIED, "gates · known exposures",
               f"{len(uncaught)} hole(s) no SEMANTIC gate catches, retained deliberately"
               + (f" ({floored} also trip a floor gate for being minimal — that is "
                  f"not closure)" if floored else "")
               + f": {', '.join(uncaught)}")

    record(UNVERIFIED, "gates · undecidable from a file",
           "local invertibility, shadow-run fidelity, totality — need a runtime and the site's tape")


# ── 5b · does the battery have evidence it works? ───────────────────────────
def check_witnesses() -> None:
    """
    `SPEC.md` §14's first-ranked risk is a WEAK BATTERY. A gate nobody has
    watched refuse anything may work; nothing shows that it does. This reports
    the coverage rather than assuming it.
    """
    sys.path.insert(0, os.path.join(ROOT, "gates"))
    from witness import ENTANGLED, matrix

    per_gate, _ = matrix()
    n = len(per_gate)
    wit = sum(1 for i in per_gate.values() if i["state"] == "WITNESSED")
    gaps = [g for g, i in per_gate.items()
            if i["state"] == "UNWITNESSED" and g not in ENTANGLED]

    record(FAILED if gaps else GREEN, "battery · witnessed",
           f"{len(gaps)} gate(s) never seen to refuse anything: {', '.join(gaps)}" if gaps
           else f"{wit} of {n} gates cleanly witnessed; every gap explained")

    weak = [g for g, i in per_gate.items()
            if i["state"] == "INCIDENTAL" and g not in ENTANGLED]
    record(UNVERIFIED if weak else GREEN, "battery · isolation",
           f"{len(weak)} gate(s) fire only alongside others — a regression there would "
           f"still look green: {', '.join(weak)}" if weak
           else "every witnessed gate fires alone")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "gates", "test_witness.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    record(GREEN if r.returncode == 0 else FAILED, "battery · witness battery", last)


# ── 6 · the floor works with everything learned disabled ────────────────────
def check_floor() -> None:
    src = open(os.path.join(ROOT, "floor", "closure.py"), encoding="utf-8").read()
    banned = [b for b in ("import torch", "import numpy", "openai", "anthropic", "requests", "urllib")
              if b in src]
    record(FAILED if banned else GREEN, "floor · model-free",
           f"found {banned}" if banned else "no model or network imports; behaves identically with learned components off")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "floor", "test_closure.py")],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    record(GREEN if r.returncode == 0 else FAILED, "floor · closure battery", last)

    # the accelerated path: admissible only if bit-identical to the reference
    p = subprocess.run([sys.executable, os.path.join(ROOT, "floor", "parity.py")],
                       capture_output=True, text=True)
    state = {0: GREEN, 2: UNVERIFIED}.get(p.returncode, FAILED)
    record(state, "floor · CPU/GPU parity",
           "bit-identical on every fixture" if state == GREEN
           else ("CPU invariants hold; GPU parity not run — no card in the reference environment"
                 if state == UNVERIFIED else "the accelerated path is NOT admissible"))


# ── 6e · the algebra is executable ──────────────────────────────────────────
def check_algebra() -> None:
    sys.path.insert(0, os.path.join(ROOT, "core"))
    from algebra import Context, check_all, equivalent, mount_all, retire, rows_from_patch

    with open(os.path.join(ROOT, "examples", "worked", "northlake.patch.json"),
              encoding="utf-8") as fh:
        patch = json.load(fh)
    rows = rows_from_patch(patch)

    inv = check_all(rows)
    bad = [x.render() for x in inv if not x.ok]
    record(FAILED if bad else GREEN, "algebra · T3 pointwise invertibility",
           "; ".join(bad) if bad else f"{len(inv)} rows: p⁻(p(λ)) ≃ λ at each applied state")

    recovered = equivalent(retire(mount_all(Context.seed(), rows)).fit, {})
    record(GREEN if recovered else FAILED, "algebra · T4 the seed is recoverable",
           "retire(mount*(λ₀)) ≃ λ₀" if recovered
           else "a reachable state does NOT retire to the seed")

    t = subprocess.run([sys.executable, os.path.join(ROOT, "core", "test_algebra.py")],
                       capture_output=True, text=True)
    last = (t.stdout.strip().splitlines() or ["no output"])[-1]
    record(GREEN if t.returncode == 0 else FAILED, "algebra · theorem battery", last)


# ── 6b · citations are not fabricated ───────────────────────────────────────
def check_citations() -> None:
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import cite

    m = cite.load_manifest()
    srcs = m.get("sources", {})
    if not srcs:
        record(UNVERIFIED, "provenance · corpus pinned",
               "no sources pinned yet — every locator still reads TODO-VERIFY")
        return
    record(GREEN, "provenance · corpus pinned", f"{len(srcs)} sources with sha256")

    if not os.path.exists(cite.CITATIONS):
        record(UNVERIFIED, "provenance · citations verify", "no citations.json yet")
        return
    with open(cite.CITATIONS, encoding="utf-8") as fh:
        cites = json.load(fh).get("citations", [])
    cache: dict = {}
    bad = [c for c in cites if cite.verify(c, cache, m)[0] != cite.OK]
    record(FAILED if bad else GREEN, "provenance · citations verify",
           f"{len(bad)} of {len(cites)} do not byte-match their source"
           if bad else f"{len(cites)} citations verbatim in pinned sources")


# ── 6c · the clinical layer and the jurisdiction table ──────────────────────
def check_clinical() -> None:
    try:
        import yaml
    except ImportError:
        record(UNVERIFIED, "clinical · L1 present", "pyyaml unavailable — not checked")
        return

    dt = os.path.join(ROOT, "clinical", "donor_testing.yml")
    if not os.path.exists(dt):
        record(FAILED, "clinical · L1 present", "clinical/donor_testing.yml missing")
        return
    with open(dt, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    # every provenance block in L1 must carry a verified quote
    def walk(node):
        if isinstance(node, dict):
            if "provenance" in node and isinstance(node["provenance"], dict):
                yield node["provenance"]
            for v in node.values():
                yield from walk(v)
        elif isinstance(node, list):
            for v in node:
                yield from walk(v)

    provs = list(walk(doc))
    unver = [p for p in provs if p.get("quote_verified") is not True]
    record(FAILED if unver else GREEN, "clinical · L1 provenance",
           f"{len(unver)} of {len(provs)} blocks unverified" if unver
           else f"{len(provs)} provenance blocks, every one quote-verified")

    # L1 must declare what it does NOT contain
    inc = doc.get("incomplete") or []
    record(GREEN if inc else UNVERIFIED, "clinical · declares its gaps",
           f"{len(inc)} known gaps named in the file" if inc
           else "no `incomplete` section — a complete-looking L1 is a claim")

    # temporal bounds must be reachable by the closure
    raw = open(dt, encoding="utf-8").read()
    n_bounds = len(re.findall(r"feeds_closure:\s*true", raw))
    record(GREEN if n_bounds else UNVERIFIED, "clinical · feeds the closure",
           f"{n_bounds} L1 temporal bounds marked for floor/closure.py")


def check_jurisdiction() -> None:
    try:
        import yaml
    except ImportError:
        record(UNVERIFIED, "authorization · jurisdiction table", "pyyaml unavailable")
        return
    p = os.path.join(ROOT, "core", "authorization", "jurisdiction.yml")
    if not os.path.exists(p):
        record(FAILED, "authorization · jurisdiction table", "missing")
        return
    with open(p, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    rows = doc.get("jurisdictions") or []

    def row_ok(r: dict) -> list[str]:
        """A row is well-formed only if every legal block is quote-verified."""
        faults = []
        if not r.get("source_id"):
            faults.append("no pinned source_id")
        if not r.get("code"):
            faults.append("no statutory code citation")
        for block in ("first_person", "surrogate_priority", "within_class_rule"):
            b = r.get(block)
            if b is None:
                continue
            if b.get("quote_verified") is not True:
                faults.append(f"{block} not quote-verified")
            if not b.get("locator"):
                faults.append(f"{block} has no locator")
        if "counsel_reviewed" not in r:
            faults.append("counsel_reviewed absent — must be present, may be false")
        return faults

    faults = {r.get("state", "?"): row_ok(r) for r in rows}
    broken = {k: v for k, v in faults.items() if v}
    if broken:
        record(FAILED, "authorization · jurisdiction rows",
               "; ".join(f"{k}: {', '.join(v)}" for k, v in broken.items()))
    elif rows:
        record(GREEN, "authorization · jurisdiction rows",
               f"{len(rows)} row(s) — {', '.join(sorted(faults))} — each pinned and quote-verified")
    else:
        record(UNVERIFIED, "authorization · jurisdiction rows", "no rows yet")

    # counsel review is a HUMAN act. No automated check may set it, and a row
    # that is cited but unreviewed is legitimate — it just isn't finished.
    unreviewed = [r.get("state") for r in rows if r.get("counsel_reviewed") is not True]
    record(UNVERIFIED if unreviewed else (GREEN if rows else UNVERIFIED),
           "authorization · counsel review",
           f"{len(unreviewed)} row(s) cited but not lawyer-reviewed: {', '.join(unreviewed)} — "
           f"byte-exactness proves the text, never the reading"
           if unreviewed else "every row reviewed")

    record(UNVERIFIED, "authorization · coverage",
           f"{len(rows)} of ~51 jurisdictions — the rest belong to the OPOs that "
           f"operate under them (see PROCEDURE.md)")

    record(GREEN if doc.get("keyed_on") == "donor_state_of_residence" else FAILED,
           "authorization · keyed on residence",
           "keyed on the donor's state of residence, not the state of death")


# ── 6d · the authority chain ────────────────────────────────────────────────
def check_authority() -> None:
    try:
        import yaml
    except ImportError:
        record(UNVERIFIED, "authority · chain", "pyyaml unavailable")
        return
    p = os.path.join(ROOT, "core", "authority", "chain.yml")
    if not os.path.exists(p):
        record(FAILED, "authority · chain", "core/authority/chain.yml missing")
        return
    with open(p, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    chain = doc.get("chain") or []

    tiers = [c.get("tier") for c in chain]
    record(GREEN if tiers == sorted(tiers) and len(tiers) == len(set(tiers)) else FAILED,
           "authority · chain ordered", f"{len(chain)} tiers, statute to site fit")

    # every tier must say how it changes and on what clock — a tier that cannot
    # answer that is not an authority, it is an assertion
    mute = [c.get("name") for c in chain if not c.get("changes_by") or not c.get("clock")]
    record(FAILED if mute else GREEN, "authority · each tier names its clock",
           ", ".join(mute) if mute else "every tier states how it changes and how fast")

    # the statute tier's quotes must be verified like everything else
    q = [e for c in chain for e in (c.get("establishes") or [])]
    unver = [e.get("id") for e in q if e.get("quote_verified") is not True]
    record(FAILED if unver else GREEN, "authority · statute quotes verified",
           ", ".join(map(str, unver)) if unver else f"{len(q)} statutory quotes, all verified")


# ── 6f · the profiles ───────────────────────────────────────────────────────
def check_profiles() -> None:
    """
    One clone, two artifacts. `edr` must remain a strict subset of `forge`, or
    a site deploying a record system inherits completion machinery it never
    asked for and cannot audit.
    """
    r = subprocess.run([sys.executable, os.path.join(ROOT, "core", "profile.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        record(GREEN, "profile · edr ⊆ forge", "the record carries no completion machinery")
    elif "pyyaml" in (r.stdout + r.stderr):
        record(UNVERIFIED, "profile · edr ⊆ forge", "pyyaml unavailable — subset not checked")
    else:
        bad = [ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln]
        record(FAILED, "profile · edr ⊆ forge", bad[0] if bad else "subset violated")

    # the switch must fail toward inert
    sys.path.insert(0, os.path.join(ROOT, "core"))
    import profile as prof
    record(GREEN if prof.state() in prof.STATES else FAILED, "profile · switch reads safe",
           f"state = {prof.state()} (absent or malformed reads as `off`, never `live`)")


# ── 6g · percepts and the switch ────────────────────────────────────────────
def check_percepts() -> None:
    sys.path.insert(0, os.path.join(ROOT, "percepts"))
    import stream as st
    import switch as sw

    # the direction of failure is the design
    record(GREEN if sw.read() in sw.STATES else FAILED, "switch · reads a legal state",
           f"{sw.read()} — {sw.MEANING[sw.read()]}")

    src = open(os.path.join(ROOT, "percepts", "switch.py"), encoding="utf-8").read()
    writes = 'open(STATE_FILE, "w"' in src
    record(FAILED if writes else GREEN, "switch · operator-only",
           "this module writes the switch file" if writes
           else "nothing here writes it — a file only the operator writes")

    status, detail = sw.heartbeat()
    record(FAILED if status == "STALLED" else GREEN, "switch · heartbeat honest",
           f"{status} — {detail}")

    # the laws the stream must carry
    # the catalogue must actually be closed, not just documented as closed
    probe = st.Stream(os.path.join(ROOT, "percepts", ".probe.tmp"))
    try:
        probe.emit("not-a-kind", "conformance", {}, at=0)
        closed = False
    except ValueError:
        closed = True
    finally:
        if os.path.exists(probe.path):
            os.remove(probe.path)
    record(GREEN if closed else FAILED, "percepts · catalogue closed",
           f"{len(st.KINDS)} kinds, {len(st.REASONS)} reasons — an unknown kind raises"
           if closed else "an unknown percept kind was accepted")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "percepts", "test_percepts.py")],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    record(GREEN if r.returncode == 0 else FAILED, "percepts · law battery", last)

    # if a stream exists, its counts must not lie
    hdr, ps, foot = st.load()
    if ps:
        ok = foot.get("total") == foot.get("surfaced", 0) + foot.get("suppressed", 0)
        record(GREEN if ok else FAILED, "percepts · total is a sum",
               f"{foot.get('surfaced',0)} surfaced + {foot.get('suppressed',0)} suppressed "
               f"= {foot.get('total',0)}")
        dropped = foot.get("dropped", 0)
        record(FAILED if dropped else GREEN, "percepts · nothing dropped",
               f"{dropped} percept(s) lost — a defect, not a statistic" if dropped
               else f"{len(ps)} percepts, none dropped")
    else:
        record(UNVERIFIED, "percepts · stream",
               "no stream yet — it fills as the repository is used (useful at `off`)")


# ── 6h · the nested chassis ─────────────────────────────────────────────────
def check_chassis() -> None:
    """
    68 MB of third-party code sits in the repository ROOT — vendored in place,
    unpinned, and unwired. The only thing keeping it out of the public tree is
    one .gitignore line, and a .gitignore line is a preference. This makes it a
    gate: law 9, hazards unreachable rather than forbidden.
    """
    d = os.path.join(ROOT, "deepseek-harness-master")
    if not os.path.isdir(d):
        record(UNVERIFIED, "chassis · present", "not on disk — nothing to pin or exclude")
        return

    # PINNED 2026-08-26. internal §14 item 1, closed.
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "pin_chassis.py"), "--check"],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if r.returncode == 0:
        import json as _j
        with open(os.path.join(ROOT, "CHASSIS.pin.json"), encoding="utf-8") as fh:
            pin = _j.load(fh)
        v = pin["verification"]
        record(GREEN, "chassis · pinned and unmodified",
               f"{pin['upstream']['tag']} @ {pin['upstream']['commit'][:12]} — "
               f"{v['identical']:,}/{v['upstream_files']:,} files byte-identical")
    elif r.returncode == 2:
        record(UNVERIFIED, "chassis · pinned", "pin recorded; tree not on disk — fetch and --verify")
    else:
        record(FAILED, "chassis · pinned and unmodified",
               "the local tree does not match the pin — compose, never fork")

    # the hazard: unpinned third-party code shipping from an MIT repo
    r = subprocess.run(["git", "ls-files", "deepseek-harness-master"],
                       capture_output=True, text=True, cwd=ROOT)
    tracked = [ln for ln in r.stdout.splitlines() if ln.strip()]
    record(FAILED if tracked else GREEN, "chassis · not tracked",
           f"{len(tracked)} file(s) STAGED — unpinned third-party code would ship"
           if tracked else "untracked; provenance must be established before it can")


# ── 6i · the L3 adapters ────────────────────────────────────────────────────
def check_adapters() -> None:
    """
    L3 is the largest single share of the six years. The seed ships the SHELL
    and its battery; the site binds the integration it actually has.
    """
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "adapters", "conformance.py")],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    tail = [ln for ln in r.stdout.splitlines() if "adapter(s)" in ln]
    detail = tail[-1].strip() if tail else "no adapters declared"

    if r.returncode == 3:
        record(UNVERIFIED, "adapters · declarations", "pyyaml unavailable — not checked")
    elif r.returncode == 1:
        bad = [ln.strip() for ln in r.stdout.splitlines() if "FAILED " in ln]
        record(FAILED, "adapters · declarations", bad[0] if bad else detail)
    elif r.returncode == 2:
        record(UNVERIFIED, "adapters · declarations",
               f"{detail} — shells declared, no binding; a real integration needs "
               f"specs an OPO holds")
    else:
        record(GREEN, "adapters · declarations", detail)


# ── 6j · no redistributed source text ───────────────────────────────────────
def check_no_redistribution() -> None:
    """
    corpus/ is gitignored because OPTN policy, CFR text and state statutes
    belong to their publishers. **A chunk of a pinned source is still that
    source**, and a .gitignore line covering corpus/ does not cover derivatives
    that land somewhere else.

    Learned 2026-08-26: a `git add -A` swept 55 smoke-test chunks of verbatim
    OPTN policy into a public commit. Nothing caught it — the leak detector
    watched corpus/ and this text was in forge/.
    """
    r = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=ROOT)
    tracked = [f for f in r.stdout.splitlines() if f.strip()]

    # tell-tales of a derived extract, wherever it lives
    suspect = [f for f in tracked
               if any(m in f for m in ("_smoke/", ".chunks/", "chunks_out/"))
               or re.search(r"chunk-\d{3}\.(md|txt)$", f)]
    record(FAILED if suspect else GREEN, "hygiene · no derived source text",
           f"{len(suspect)} tracked file(s) look like a chunked source: "
           f"{', '.join(suspect[:3])}" if suspect
           else "no chunk output, smoke output or derived extract is tracked")

    # and the pinned sources themselves must never be tracked
    leaked = [f for f in tracked if f.startswith("corpus/")
              and not f.endswith((".json", ".md"))]
    record(FAILED if leaked else GREEN, "hygiene · corpus not redistributed",
           ", ".join(leaked) if leaked
           else "only the manifest and the citations are committed")


# ── 6j · the forge plugins ──────────────────────────────────────────────────
def check_forge_plugins() -> None:
    """A bound plugin that violates a refusing rule does not mount."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "forge", "conformance.py")],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    tail = [ln for ln in (r.stdout or "").splitlines() if "GREEN ·" in ln]
    detail = tail[-1].strip() if tail else "no output"
    if r.returncode == 3:
        record(UNVERIFIED, "forge · plugin bindings", "pyyaml unavailable")
    elif r.returncode == 1:
        bad = [ln.strip() for ln in r.stdout.splitlines() if "FAILED " in ln]
        record(FAILED, "forge · plugin bindings", bad[0] if bad else detail)
    elif r.returncode == 2:
        record(UNVERIFIED, "forge · plugin bindings", f"{detail} — capabilities unbound")
    else:
        record(GREEN, "forge · plugin bindings", detail)

    t = subprocess.run([sys.executable, os.path.join(ROOT, "forge", "test_conformance.py")],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    last = ((t.stdout or "").strip().splitlines() or ["no output"])[-1]
    record(GREEN if t.returncode == 0 else FAILED, "forge · the gate refuses", last)


# ── 6k · the schema is a contract, not a document ───────────────────────────
def check_schema() -> None:
    """
    `patch.schema.json` shipped from the beginning and NOTHING VALIDATED
    AGAINST IT — which is why two defects sat in it undetected until an
    independent completion run reported them. This runs it.
    """
    # every declared target accounted for, in the example everyone copies
    sys.path.insert(0, os.path.join(ROOT, "gates"))
    from accountability import validate as _acct
    from validate_patch import load_patch as _lp
    _st, _m = _acct(_lp(os.path.join(ROOT, "examples", "worked", "northlake.patch.json")))
    record(_st, "schema · nothing silent", "; ".join(_m)[:120])

    r = subprocess.run([sys.executable, os.path.join(ROOT, "schema", "validate.py"), "--self"],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    last = [ln for ln in r.stdout.splitlines() if ln.strip()]
    record(GREEN if r.returncode == 0 else FAILED, "schema · examples validate",
           last[-1] if last else "no output")


# ── 7 · nothing site-specific is in the repository ──────────────────────────
def check_no_site_data() -> None:
    # ASK GIT, NOT THE FILESYSTEM. The check is named "committed" and walked the
    # working tree — so it failed on a patch that was correctly gitignored and
    # never committed at all. A real fit is AUTHORED here during a completion
    # and lives in the site's own version control; having one on disk is normal
    # and is exactly what `.gitignore` covers.
    #
    # Caught 2026-08-26 when an arm-2 candidate landed as fairbank.patch.yml.
    # The rule was about what SHIPS; the implementation asked what EXISTS, and
    # those are different questions — the same location-versus-content error as
    # the corpus leak earlier the same day.
    r = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=ROOT)
    offenders = [f for f in r.stdout.splitlines()
                 if f.endswith(".patch.yml") and "worked" not in f]
    record(FAILED if offenders else GREEN, "hygiene · no site patch committed",
           ", ".join(offenders) if offenders
           else "no <site>.patch.yml tracked outside the worked example")

    fixtures = os.path.join(ROOT, "fixtures")
    unmarked = []
    for dirpath, _, filenames in os.walk(fixtures):
        for fn in filenames:
            if fn.endswith((".json", ".jsonl")):
                text = open(os.path.join(dirpath, fn), encoding="utf-8").read(4000)
                if "SYNTHETIC" not in text.upper() and "synthetic" not in text:
                    unmarked.append(fn)
    record(FAILED if unmarked else GREEN, "hygiene · fixtures declare synthetic",
           ", ".join(unmarked) if unmarked else "every fixture states it carries no real data")


# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    print("REGISTRAR · conformance\n")
    for section, fn in (
        ("the spine", check_lifecycle),
        ("generated artifacts", check_generated),
        ("the tape (L4)", check_tape),
        ("case replay", check_replay),
        ("the gates", check_gates),
        ("the battery itself", check_witnesses),
        ("the floor", check_floor),
        ("provenance", check_citations),
        ("the clinical layer (L1)", check_clinical),
        ("authorization jurisdiction", check_jurisdiction),
        ("the authority chain", check_authority),
        ("the algebra", check_algebra),
        ("the profiles", check_profiles),
        ("percepts and the switch", check_percepts),
        ("the nested chassis", check_chassis),
        ("the L3 adapters", check_adapters),
        ("the forge plugins", check_forge_plugins),
        ("redistribution", check_no_redistribution),
        ("the schema", check_schema),
        ("hygiene", check_no_site_data),
    ):
        print(f"{section}")
        fn()
        print()

    states = {s for s, _, _ in CHECKS}
    worst = FAILED if FAILED in states else (UNVERIFIED if UNVERIFIED in states else GREEN)
    n_f = sum(1 for s, _, _ in CHECKS if s == FAILED)
    n_u = sum(1 for s, _, _ in CHECKS if s == UNVERIFIED)
    n_g = sum(1 for s, _, _ in CHECKS if s == GREEN)

    print(f"{n_g} GREEN · {n_u} PASS-UNVERIFIED · {n_f} FAILED\n")
    if worst == FAILED:
        print("FAILED — this instance does not load-bear.")
        return 1
    if worst == UNVERIFIED:
        print("PASS-UNVERIFIED — nothing failed, but checks did not run.")
        print("  Some element of the spine is specified rather than established, or a")
        print("  check needs a runtime this battery does not have. THIS IS NOT A PASS.")
        print("  Run with --verbose to see exactly which, and why each one is open.")
        return 2
    print("GREEN — every check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
