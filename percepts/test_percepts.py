#!/usr/bin/env python3
"""
REGISTRAR · percepts · tests

    python percepts/test_percepts.py

Each test asserts one of the laws ported from the reference implementation.
Several assert a DIRECTION OF FAILURE rather than a behaviour — those are the
ones that matter, because a switch that fails toward `live` is a defect no
amount of correct behaviour compensates for.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import stream as st      # noqa: E402
import switch as sw      # noqa: E402

PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def tmp_stream(capacity: int = 10_000):
    s = st.Stream(os.path.join(tempfile.mkdtemp(), "s.jsonl"), capacity=capacity)
    s.open()
    return s


# ── law 1 ───────────────────────────────────────────────────────────────────
def test_silence_is_world():
    """
    Elapsed time enters as a percept. THE MAIN CASE in this domain, because an
    interval produces no event to react to and a stream of events alone cannot
    represent the thing that most often goes wrong.
    """
    print("\nlaw 1 · silence is world, not absence")
    s = tmp_stream()
    s.emit("gate", "g", {}, at=0)
    s.emit("gate", "g", {}, at=200)
    _, ps, _ = st.load(s.path)
    ticks = [p for p in ps if p.kind == "tick"]
    check("a gap emits a tick", len(ticks), 1)
    check("the tick carries its size", ticks[0].body["gap_minutes"], 200)

    s2 = tmp_stream()
    s2.emit("gate", "g", {}, at=0)
    s2.emit("gate", "g", {}, at=5)
    _, ps2, _ = st.load(s2.path)
    check("a small gap emits none", [p for p in ps2 if p.kind == "tick"], [])


# ── law 3 ───────────────────────────────────────────────────────────────────
def test_a_drop_is_loud():
    """A silently dropped percept is the turn reborn inside the loop."""
    print("\nlaw 3 · a drop is counted loudly")
    s = tmp_stream(capacity=3)
    for i in range(6):
        s.emit("gate", "g", {"i": i}, at=i)
    foot = s.close()
    check("drops are counted", foot["dropped"] > 0, True)
    _, ps, _ = st.load(s.path)
    drops = [p for p in ps if p.kind == "drop"]
    check("and each is ON THE STREAM", len(drops) > 0, True)
    check("naming the loss", drops[0].body.get("lost"), 1)


# ── law 4 ───────────────────────────────────────────────────────────────────
def test_added_never_conflated():
    """
    total = surfaced + suppressed, BY ADDITION. The reference implementation
    once double-logged these, and the count lied in the flattering direction
    until somebody added them separately.
    """
    print("\nlaw 4 · surfaced and suppressed are added, never conflated")
    s = tmp_stream()
    for _ in range(3):
        s.emit("surface", "x", {}, at=1)
    for _ in range(7):
        s.emit("hold", "x", {}, at=1)
    f = s.close()
    check("surfaced", f["surfaced"], 3)
    check("suppressed", f["suppressed"], 7)
    check("total is the SUM", f["total"], 10)
    check("suppressed is not folded into surfaced", f["surfaced"] != f["total"], True)


# ── law 5 ───────────────────────────────────────────────────────────────────
def test_reasons_are_recorded():
    """Without the reason, a corpus of judgments cannot be re-swept later."""
    print("\nlaw 5 · every judgment records why it happened")
    s = tmp_stream()
    s.emit("gate", "g", {}, reason="b", at=1)
    s.emit("gate", "g", {}, reason="c", at=1)
    _, ps, _ = st.load(s.path)
    check("the reason survives the round trip",
          {p.reason for p in ps if p.kind == "gate"}, {"b", "c"})
    check("coarsened judgments are findable", len(st.coarsened(ps)), 1)
    check("and `c` means delayed, never dropped",
          "never dropped" in st.REASONS["c"] or "no percept" in st.REASONS["c"].lower()
          or "Judgment was delayed" in st.REASONS["c"], True)


# ── law 6 ───────────────────────────────────────────────────────────────────
def test_no_self_ingest():
    """A surfacing that re-enters as a percept is a feedback loop that looks
    like activity."""
    print("\nlaw 6 · never ingest your own output as world")
    s = tmp_stream()
    s.declare_self("me")
    check("own non-judgment output is refused", s.emit("gate", "me", {}, at=1), None)
    check("own surfacings still record", s.emit("surface", "me", {}, at=1) is not None, True)


# ── law 7 ───────────────────────────────────────────────────────────────────
def test_header_declares_semantics():
    """A reader that was not there when it was written must read it correctly."""
    print("\nlaw 7 · the header declares its own semantics")
    s = tmp_stream()
    s.emit("gate", "g", {}, at=1)
    s.close()
    hdr, _, _ = st.load(s.path)
    check("total is defined", "ADDITION" in hdr.get("total_def", ""), True)
    check("a drop is defined", "counted" in hdr.get("drop_def", ""), True)
    check("a tick is defined", "not the absence" in hdr.get("tick_def", ""), True)
    check("the kind catalogue ships", len(hdr.get("kinds", {})), len(st.KINDS))


# ── the switch, and the direction it fails ──────────────────────────────────
def test_switch_fails_toward_inert():
    """
    THE MOST IMPORTANT ASSERTION IN THIS FILE.

    Every failure mode must read `off`. A switch that fails toward `live` is a
    defect no amount of correct behaviour compensates for.
    """
    print("\nthe switch fails toward inert, in every mode")
    d = tempfile.mkdtemp()
    real = sw.STATE_FILE
    try:
        sw.STATE_FILE = os.path.join(d, "registrar.state")
        check("absent reads off", sw.read(), sw.OFF)

        for content, label in ((" ", "empty"), ("banana", "unrecognised"),
                               ("LIVE!!", "malformed"), ("��", "garbage")):
            with open(sw.STATE_FILE, "w", encoding="utf-8", errors="replace") as fh:
                fh.write(content)
            check(f"{label} reads off", sw.read(), sw.OFF)

        for good, want in (("off", "off"), ("shadow", "shadow"), ("live", "live"),
                           ("  LIVE  ", "live"), ("live # a comment", "live")):
            with open(sw.STATE_FILE, "w", encoding="utf-8") as fh:
                fh.write(good)
            check(f"{good.strip()!r} reads {want}", sw.read(), want)
    finally:
        sw.STATE_FILE = real


def test_stalled_is_a_fault():
    """
    A resident that has died looks exactly like a resident with nothing to say.
    Conflating those reports health the system does not have.
    """
    print("\na stalled heartbeat is a FAULT, not quiet")
    d = tempfile.mkdtemp()
    rs, rb = sw.STATE_FILE, sw.BEAT_FILE
    try:
        sw.STATE_FILE = os.path.join(d, "registrar.state")
        sw.BEAT_FILE = os.path.join(d, "beat.json")

        with open(sw.STATE_FILE, "w", encoding="utf-8") as fh:
            fh.write("off")
        check("off expects no beat", sw.heartbeat()[0], "absent")

        with open(sw.STATE_FILE, "w", encoding="utf-8") as fh:
            fh.write("live")
        check("live with no beat is STALLED", sw.heartbeat()[0], "STALLED")

        with open(sw.BEAT_FILE, "w", encoding="utf-8") as fh:
            json.dump({"who": "t", "at": time.time() - 9999}, fh)
        check("an old beat is STALLED", sw.heartbeat()[0], "STALLED")

        with open(sw.BEAT_FILE, "w", encoding="utf-8") as fh:
            json.dump({"who": "t", "at": time.time()}, fh)
        check("a fresh beat is beating", sw.heartbeat()[0], "beating")
    finally:
        sw.STATE_FILE, sw.BEAT_FILE = rs, rb


def test_off_writes_nothing():
    """`off` is INERT MID-FLIGHT — not paused, not disabled. No writes."""
    print("\noff is inert, not merely quiet")
    check("is_inert agrees with read", sw.is_inert(), sw.read() == sw.OFF)
    src = open(os.path.join(HERE, "switch.py"), encoding="utf-8").read()
    check("nothing here writes the switch file", 'open(STATE_FILE, "w"' not in src, True)


def test_catalogue_is_closed():
    """An unknown percept kind is a bug in the caller, not a new category."""
    print("\nthe percept catalogue is closed")
    s = tmp_stream()
    try:
        s.emit("vibes", "x", {}, at=1)
        check("unknown kind raises", False, True)
    except ValueError as e:
        check("unknown kind raises", "closed" in str(e), True)


def test_it_is_useful_at_off():
    """
    The test every interval surface here must pass: no surface may exist that
    only makes sense at `live`.
    """
    print("\nuseful at off — the interval-surface test")
    check("the switch reads off by default", sw.read(), sw.OFF)
    s = tmp_stream()
    s.emit("gate", "gates.validate_patch", {"gate": "evidence binding", "defect": "no source"},
           reason="b", at=1)
    _, ps, foot = st.load(s.path)
    check("percepts record with nobody home", len(ps), 1)
    check("and the defect survives", ps[0].body["defect"], "no source")


if __name__ == "__main__":
    print("REGISTRAR · percepts")
    for t in (test_silence_is_world, test_a_drop_is_loud, test_added_never_conflated,
              test_reasons_are_recorded, test_no_self_ingest, test_header_declares_semantics,
              test_switch_fails_toward_inert, test_stalled_is_a_fault,
              test_off_writes_nothing, test_catalogue_is_closed, test_it_is_useful_at_off):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
