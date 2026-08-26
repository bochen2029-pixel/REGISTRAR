#!/usr/bin/env python3
"""
REGISTRAR · percepts · the stream
─────────────────────────────────────────────────────────────────────────────
The deltas this repository already computes, on one append-only stream.

Today they are computed and dropped on the floor. `gates/validate_patch.py`
names a defect and returns; `core/case.py` finds a violation and prints it;
`floor/closure.py` derives a deadline nobody wrote down. **Nothing is home to
receive any of it**, so a completion that spans a week has no record of what it
hit, when, or what it declined.

This is that record. At `registrar.state = off` it is simply a completion log —
useful with nobody home, which is the test every interval surface here has to
pass (`SPEC.md` §2b).

THE LAWS, AND WHERE THEY COME FROM

Ported from the reference implementation of this loop (`fusord.cpp`, S0/Phase A,
the estate's first live loop). The C++ is not transferable — llama.cpp, Windows,
a GPU — but the laws are, and every one of them was learned by running it:

  1 · SILENCE IS WORLD, NOT ABSENCE. Elapsed time enters as a percept, not as
      a question waiting to be answered. **In this domain that is the main
      case**: the failure is almost always the interval, and an interval
      produces no event to react to.

  2 · INGEST IS UNCONDITIONAL; ONLY JUDGMENT CADENCE IS MODULATED. Under
      backlog, judgment COARSENS — it never sheds input. *"Delay a judgment,
      never drop a percept."* Measured the hard way: probe cost alone put the
      reference loop ~10 s behind the world, with zero emissions.

  3 · A DROP IS COUNTED LOUDLY. If the buffer ever overflows, the loss is
      recorded and reported. **A silently dropped percept is the turn reborn
      inside the loop**, and it is worse than a turn because nobody can see it.

  4 · SURFACED AND SUPPRESSED ARE ADDED, NEVER CONFLATED. `total = surfaced +
      suppressed`, by addition. The reference implementation carries this note
      against a bug it already found: the two were once double-logged and the
      count lied in the flattering direction.

  5 · EVERY JUDGMENT RECORDS WHY IT HAPPENED. Not just what fired — which rule
      fired it. Without the reason, a corpus of judgments cannot be re-swept
      under a different rule later.

  6 · NEVER INGEST YOUR OWN OUTPUT AS WORLD. A surfacing that re-enters as a
      percept is a feedback loop that looks like activity.

  7 · THE HEADER DECLARES ITS OWN SEMANTICS. What `total` means, what the
      reasons are, what version wrote it — so the stream can be read correctly
      by something that was not there when it was written.

Zero dependencies. Append-only. Python 3.9+.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

STREAM_VERSION = "0.1"
DEFAULT_STREAM = os.path.join(HERE, "stream.jsonl")

# ─────────────────────────────────────────────────────────────────────────────
# WHAT A PERCEPT IS
#   A delta the repository computed. Not an interpretation of one.
# ─────────────────────────────────────────────────────────────────────────────
KINDS = {
    "gate":      "a gate refused a row, with the defect named in words",
    "expiry":    "a mounted row reached the date it must re-earn its place",
    "violation": "a replay found a transition the lifecycle does not permit",
    "deadline":  "the closure derived a bound nobody wrote down",
    "drift":     "a mounted row no longer matches what the tape shows",
    "tick":      "elapsed time. SILENCE IS WORLD — see law 1.",
    "hold":      "considered and declined, with the reason",
    "surface":   "raised to a human",
    "drop":      "the buffer overflowed. LAW 3 — this must never be silent.",
}

# Why a judgment happened. Ported from the reference implementation's reason
# codes, because a corpus without them cannot be re-swept under a later rule.
REASONS = {
    "b": "a boundary — the natural end of something",
    "n": "the count cap — enough has accumulated",
    "t": "the time cap — long enough has passed",
    "f": "final — the source said it was done",
    "c": "COARSENED under backlog. Judgment was delayed; no percept was dropped.",
    "m": "a checkpoint",
}


@dataclass(frozen=True)
class Percept:
    seq: int
    at: int              # whole minutes from the stream's reference
    kind: str
    source: str          # which component computed it
    body: dict
    reason: str = ""     # a REASONS code, where a judgment was involved

    def to_json(self) -> str:
        d = {"seq": self.seq, "at": self.at, "kind": self.kind,
             "source": self.source, "body": self.body}
        if self.reason:
            d["reason"] = self.reason
        return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Stream:
    """
    An append-only percept stream.

    NOT a queue and not a bus: nothing consumes from it, and writing never
    blocks a caller. A component that computed something calls `emit` and
    carries on. That is law 2 — the world never dilates for a slow reader.
    """

    def __init__(self, path: str = DEFAULT_STREAM, capacity: int = 10_000) -> None:
        self.path = path
        self.capacity = capacity
        self._seq = 0
        self._surfaced = 0
        self._suppressed = 0
        self._dropped = 0            # law 3 — counted, and reported at close
        self._self_ids: set[str] = set()
        self._t0 = time.time()
        self._last_at = 0

    # ── the header ──────────────────────────────────────────────────────────
    def open(self) -> None:
        """
        Write the header, which declares the stream's own semantics (law 7).

        A reader that was not present when this was written must be able to
        interpret it correctly — including what `total` means, which is the
        exact thing the reference implementation got wrong once.
        """
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        hdr = {
            "k": "hdr",
            "stream_version": STREAM_VERSION,
            "kinds": KINDS,
            "reasons": REASONS,
            "total_def": "total = surfaced + suppressed, BY ADDITION, never by conflation",
            "drop_def": "a drop is a lost percept and is counted; silence here would be a lie",
            "tick_def": "elapsed time is a percept, not the absence of one",
            "note": "append-only. a reader folds it; nothing rewrites it.",
        }
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(hdr, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False) + "\n")

    # ── the only arrow in ───────────────────────────────────────────────────
    def emit(self, kind: str, source: str, body: dict | None = None,
             reason: str = "", at: int | None = None) -> Percept | None:
        """
        Record a percept. Never blocks, never raises on a full buffer.

        Returns None only if the percept was DROPPED — and a drop is itself
        recorded, because law 3 says the loss must be loud.
        """
        if kind not in KINDS:
            raise ValueError(f"unknown percept kind {kind!r} — the catalogue is closed")

        # law 6: our own output is not world
        if source in self._self_ids and kind not in ("surface", "hold"):
            return None

        minute = at if at is not None else int((time.time() - self._t0) // 60)

        # law 1: silence before this delta becomes world
        self._tick_if_gap(minute)

        if self._seq >= self.capacity:
            self._dropped += 1
            self._write(Percept(self._seq, minute, "drop", "stream",
                                {"lost": 1, "capacity": self.capacity,
                                 "note": "LAW 3 — a silently dropped percept is the turn "
                                         "reborn inside the loop"}))
            return None

        p = Percept(self._seq, minute, kind, source, dict(body or {}), reason)
        self._write(p)
        if kind == "surface":
            self._surfaced += 1
        elif kind == "hold":
            self._suppressed += 1
        self._last_at = minute
        return p

    def _tick_if_gap(self, minute: int, gap_minutes: int = 60) -> None:
        """
        Law 1. Elapsed time enters the stream as world.

        This is the whole reason `percepts/` is not just a log. A case that
        stops moving produces no event — the absence IS the finding, and a
        stream that only records events cannot represent it.
        """
        gap = minute - self._last_at
        if gap >= gap_minutes and self._seq > 0:
            self._write(Percept(self._seq, minute, "tick", "stream",
                                {"gap_minutes": gap,
                                 "note": "silence is world, not absence"}))
            self._last_at = minute

    def _write(self, p: Percept) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(p.to_json() + "\n")
        self._seq += 1

    # ── close, and the counts that must not lie ─────────────────────────────
    def close(self) -> dict:
        """
        The footer. `total = surfaced + suppressed`, by addition (law 4), and
        the drop count stated whether or not it is zero (law 3).
        """
        summary = {
            "k": "end",
            "seq": self._seq,
            "surfaced": self._surfaced,
            "suppressed": self._suppressed,
            "total": self._surfaced + self._suppressed,
            "dropped": self._dropped,
            "elapsed_minutes": int((time.time() - self._t0) // 60),
        }
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(summary, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False) + "\n")
        return summary

    def declare_self(self, *ids: str) -> None:
        """Law 6 — sources whose output must never re-enter as world."""
        self._self_ids.update(ids)


# ── reading: every view is a fold ───────────────────────────────────────────
def load(path: str = DEFAULT_STREAM) -> tuple[dict, list[Percept], dict]:
    """Returns (header, percepts, footer-or-running-summary)."""
    hdr, out, foot = {}, [], {}
    if not os.path.exists(path):
        return hdr, out, foot
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("k") == "hdr":
                hdr = d
            elif d.get("k") == "end":
                foot = d
            else:
                out.append(Percept(d["seq"], d["at"], d["kind"], d["source"],
                                   d.get("body", {}), d.get("reason", "")))
    if not foot and out:
        s = sum(1 for p in out if p.kind == "surface")
        h = sum(1 for p in out if p.kind == "hold")
        foot = {"k": "running", "seq": len(out), "surfaced": s, "suppressed": h,
                "total": s + h, "dropped": sum(1 for p in out if p.kind == "drop")}
    return hdr, out, foot


def fold(percepts: list[Percept], step, initial):
    acc = initial
    for p in percepts:
        acc = step(acc, p)
    return acc


def by_kind(percepts: list[Percept]) -> dict[str, int]:
    out: dict[str, int] = {}
    for p in percepts:
        out[p.kind] = out.get(p.kind, 0) + 1
    return out


def coarsened(percepts: list[Percept]) -> list[Percept]:
    """
    Judgments made under backlog (reason `c`). Law 2 says these are legitimate —
    judgment coarsened, nothing was dropped — but they are recorded so the
    corpus shows where the loop was under pressure.
    """
    return [p for p in percepts if p.reason == "c"]


# ── the report ──────────────────────────────────────────────────────────────
def report(path: str = DEFAULT_STREAM) -> int:
    hdr, ps, foot = load(path)
    if not ps and not hdr:
        print(f"no stream at {path}")
        print("\nAt `off` this file is a completion log: what the gates refused, what")
        print("expired, what the closure derived, and what was considered and declined.")
        print("It fills as the repository is used. Nothing needs to be running.")
        return 0

    print(f"percepts: {path}")
    print(f"stream_version {hdr.get('stream_version', '?')}   {len(ps)} entries\n")

    counts = by_kind(ps)
    for k in sorted(counts):
        print(f"  {counts[k]:>5}  {k:<10} {KINDS.get(k, '')}")

    print()
    surfaced, suppressed = foot.get("surfaced", 0), foot.get("suppressed", 0)
    print(f"  surfaced   {surfaced}")
    print(f"  suppressed {suppressed}   ← considered and declined, on the record")
    print(f"  total      {surfaced + suppressed}   (by addition, never conflated)")

    dropped = foot.get("dropped", 0)
    if dropped:
        print(f"\n  DROPPED    {dropped}   ← percepts lost. This is a defect, not a statistic.")
    else:
        print(f"  dropped    0")

    c = coarsened(ps)
    if c:
        print(f"\n  {len(c)} judgment(s) coarsened under backlog — delayed, never dropped")

    return 1 if dropped else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    raise SystemExit(report(args[0] if args else DEFAULT_STREAM))
