#!/usr/bin/env python3
"""
REGISTRAR · percepts · the switch
─────────────────────────────────────────────────────────────────────────────
`registrar.state` — **off | shadow | live** — a file only the operator writes.

    off      exactly today's repository. INERT MID-FLIGHT: not "paused", not
             "disabled" — no writes. The seed, the floor, the gates, the tape,
             computed on demand with nobody home.
    shadow   the stream records what would have been surfaced, beside what a
             human actually did. Nothing reaches anyone. **This is where `live`
             is earned, catch by catch, on the site's own cases.**
    live     surfacings reach a person. NEVER that anything acts — the fence is
             on action, and `live` does not move it (SPEC.md §8).

WHY A FILE, AND WHY ONLY THE OPERATOR

This repository's law 9: hazards are made unreachable, not forbidden. A
three-position control that lives in a file the operator writes is a *physical
fact* of the deployment — not a preference, not a config key some process can
flip, and not something a completing harness can reach. `core/profile.py` reads
it; nothing here writes it.

THE DIRECTION OF FAILURE IS THE DESIGN

A missing file reads `off`. A malformed file reads `off`. A file containing
something unrecognised reads `off`. **An unreadable switch must fail toward
inert, never toward live** — and that asymmetry is the single most important
line in this module.

THE HEARTBEAT, AND WHY STALENESS IS LOUD

`registrar.heartbeat.json` is written by whatever is running. Staleness beyond
three beats reads **STALLED**, and STALLED is reported as a fault rather than
as quiet. A resident that has died looks exactly like a resident with nothing
to say, and those must never be the same reading.

Every flip is appended to the percept stream. The switch has a history.

    python percepts/switch.py                 read it
    python percepts/switch.py --require live  exit non-zero unless live

Zero dependencies.
"""

from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

STATE_FILE = os.path.join(ROOT, "registrar.state")
BEAT_FILE = os.path.join(ROOT, "registrar.heartbeat.json")

OFF, SHADOW, LIVE = "off", "shadow", "live"
STATES = (OFF, SHADOW, LIVE)

BEAT_SECONDS = 60
STALE_BEATS = 3

MEANING = {
    OFF:    "inert mid-flight — no writes. Today's repository exactly.",
    SHADOW: "records what would have been surfaced. Nothing reaches anyone.",
    LIVE:   "surfacings reach a person. Never that anything acts.",
}


def read() -> str:
    """
    The switch. **Fails toward inert in every failure mode**, deliberately:
    missing, unreadable, empty, malformed, or unrecognised all read `off`.
    """
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            raw = fh.read().strip()
    except Exception:
        return OFF
    if not raw:
        return OFF
    word = raw.split()[0].strip().lower()
    return word if word in STATES else OFF


def is_inert() -> bool:
    return read() == OFF


def require(state: str) -> None:
    """
    Guard for anything that must not run below a given position.

    The message names what the position means rather than restating the rule,
    because a refusal that teaches nothing is a refusal somebody works around.
    """
    cur = read()
    if cur != state:
        raise SystemExit(
            f"this requires `{state}` and the switch reads `{cur}`.\n"
            f"  {state}: {MEANING[state]}\n"
            f"  {cur}: {MEANING[cur]}\n"
            f"  The switch is {STATE_FILE} — a file only the operator writes."
        )


# ── the heartbeat ───────────────────────────────────────────────────────────
def beat(who: str = "registrar") -> None:
    """Write a heartbeat atomically. Never blocks a caller; never raises."""
    tmp = BEAT_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"who": who, "at": time.time(), "state": read()}, fh)
        os.replace(tmp, BEAT_FILE)
    except Exception:
        pass


def heartbeat() -> tuple[str, str]:
    """
    Returns (status, detail). Status is `beating` | `STALLED` | `absent`.

    STALLED is a FAULT and is reported as one. **A resident that has died looks
    exactly like a resident with nothing to say**, and conflating those is how
    a system reports health it does not have.
    """
    if read() == OFF:
        return "absent", "switch is off — nothing should be beating"
    try:
        with open(BEAT_FILE, encoding="utf-8") as fh:
            d = json.load(fh)
        age = time.time() - float(d.get("at", 0))
    except Exception:
        return "STALLED", "no heartbeat file, and the switch is not off"
    limit = BEAT_SECONDS * STALE_BEATS
    if age > limit:
        return "STALLED", (f"last beat {int(age)}s ago, limit {limit}s "
                           f"({STALE_BEATS} beats) — FAIL LOUD, not quiet")
    return "beating", f"last beat {int(age)}s ago"


# ── flipping it, which is an event with a history ───────────────────────────
def record_flip(previous: str, current: str, stream_path: str | None = None) -> None:
    """
    Append the flip to the percept stream. The switch has a history, and a
    deployment that cannot say when it went live cannot answer for what it did.
    """
    if previous == current:
        return
    try:
        from stream import DEFAULT_STREAM, Stream
        s = Stream(stream_path or DEFAULT_STREAM)
        if not os.path.exists(s.path):
            s.open()
        s.emit("surface", "switch",
               {"from": previous, "to": current, "meaning": MEANING[current]},
               reason="f")
    except Exception:
        pass


def main(argv: list[str]) -> int:
    if "--require" in argv:
        require(argv[argv.index("--require") + 1])
        return 0

    cur = read()
    exists = os.path.exists(STATE_FILE)

    print(f"switch:  {cur}")
    print(f"         {MEANING[cur]}")
    print(f"file:    {STATE_FILE}{'' if exists else '   (absent — reads as off)'}")

    status, detail = heartbeat()
    mark = "FAULT" if status == "STALLED" else "     "
    print(f"beat:    {mark} {status} — {detail}")

    if cur == OFF:
        print("\nAt `off` this is the whole repository and it is a complete product:")
        print("  the seed, the floor, the gates, the tape — computed on demand.")
        print("  Everything above it is optional, and nothing above it is running.")

    return 1 if status == "STALLED" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
