#!/usr/bin/env python3
"""
REGISTRAR · core · the tape (L4)
─────────────────────────────────────────────────────────────────────────────
The case record. Append-only, hash-chained, exportable in full at any moment
without asking anyone's permission.

THE SIGNATURE IS THE POINT

There is no `delete` in this module. There is no `update`. They are not
forbidden by a policy that could be relaxed under deadline — they are **absent
from the interface**, which is the difference between a rule and a type. A
correction is a new entry that supersedes an older one; the older one remains
readable forever, because in a domain with mandated case review, what the
record *used to say* is evidence.

    K = E*                     the free monoid on entries
    append : K × E → K         the only arrow in

Every view — a board, a workup screen, a graded ratio — is a deterministic fold
over this. That turns replay determinism from a wish into a proof obligation:
two independent folds over one tape must agree byte for byte, and there is a
test that asserts it.

HASH CHAINING
    Each entry carries the digest of the entry before it. Altering or removing
    anything in the middle breaks every digest after it, which is detectable in
    a single pass. This is not tamper-PROOF — nothing on a disk you own is —
    it is tamper-EVIDENT, which is the property an auditor actually needs.

Zero dependencies. Python 3.9+.

THIS IS THE COMMITTED PLANE.

`SPEC.md` §2b names three: **committed** (this file — append-only, hash-chained,
owned), **forming** (candidate surfacings and rows, abortable, never persisted),
and **felt** (disposition in weights, coefficients on the tape, never a percept).

**Only commits kill.** Forming evidence may pause a judgment; only a commit ends
one. Every view in this system is a deterministic fold over this file, and that
is not a convention — it is the reason a killed process re-folds its knowledge
rather than losing it.

No code changed when the architecture was re-founded. **This was already right;
it only lacked its name.**
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Iterator, TypeVar

GENESIS = "0" * 64
T = TypeVar("T")


def _digest(prev: str, payload: str) -> str:
    """blake2b over (previous digest, canonical payload). Canonical => reproducible."""
    h = hashlib.blake2b(digest_size=32)
    h.update(prev.encode("utf-8"))
    h.update(b"\x00")
    h.update(payload.encode("utf-8"))
    return h.hexdigest()


def _canonical(obj: Any) -> str:
    """Sorted keys, no incidental whitespace. Two equal entries hash equal."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Entry:
    seq: int
    kind: str
    at: int          # whole minutes from the case reference — see floor/closure.py
    body: dict
    prev: str
    digest: str

    def to_json(self) -> str:
        return _canonical(
            {"seq": self.seq, "kind": self.kind, "at": self.at,
             "body": self.body, "prev": self.prev, "digest": self.digest}
        )

    @staticmethod
    def payload(seq: int, kind: str, at: int, body: dict) -> str:
        return _canonical({"seq": seq, "kind": kind, "at": at, "body": body})


class TamperEvident(Exception):
    """The chain does not verify. Says which entry, and why."""


class Tape:
    """
    One donor case. Construct empty, or open an existing file.

    Note what this class does NOT expose: no delete, no update, no truncate, no
    __setitem__. That is the whole design.
    """

    def __init__(self, case_id: str, entries: list[Entry] | None = None) -> None:
        self.case_id = case_id
        self._entries: list[Entry] = list(entries or [])

    # ── the only arrow in ───────────────────────────────────────────────────
    def append(self, kind: str, at: int, body: dict | None = None) -> Entry:
        body = dict(body or {})
        seq = len(self._entries)
        prev = self._entries[-1].digest if self._entries else GENESIS
        payload = Entry.payload(seq, kind, at, body)
        e = Entry(seq=seq, kind=kind, at=at, body=body, prev=prev, digest=_digest(prev, payload))
        self._entries.append(e)
        return e

    def correct(self, supersedes_seq: int, kind: str, at: int, body: dict | None = None) -> Entry:
        """
        A correction. Note that it is an APPEND: the superseded entry stays on
        the tape, readable forever. Nothing is edited and nothing disappears.
        """
        if not 0 <= supersedes_seq < len(self._entries):
            raise IndexError(f"no entry at seq {supersedes_seq}")
        b = dict(body or {})
        b["supersedes"] = supersedes_seq
        return self.append(kind, at, b)

    # ── reading ─────────────────────────────────────────────────────────────
    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[Entry]:
        return iter(self._entries)

    def __getitem__(self, i: int) -> Entry:
        return self._entries[i]

    @property
    def head(self) -> str:
        return self._entries[-1].digest if self._entries else GENESIS

    def superseded(self) -> set[int]:
        return {e.body["supersedes"] for e in self._entries if "supersedes" in e.body}

    def current(self) -> list[Entry]:
        """Entries no later entry has superseded. The superseded ones are still there."""
        dead = self.superseded()
        return [e for e in self._entries if e.seq not in dead]

    # ── the fold ────────────────────────────────────────────────────────────
    def fold(self, step: Callable[[T, Entry], T], initial: T, *, include_superseded: bool = False) -> T:
        """
        A deterministic fold over the tape. Every view in this system is one of
        these, which is what makes replay determinism checkable rather than
        aspirational.
        """
        acc = initial
        for e in (self._entries if include_superseded else self.current()):
            acc = step(acc, e)
        return acc

    # ── integrity ───────────────────────────────────────────────────────────
    def verify(self) -> None:
        """Walk the chain. Raise on the first entry that does not verify."""
        prev = GENESIS
        for i, e in enumerate(self._entries):
            if e.seq != i:
                raise TamperEvident(f"entry {i}: seq is {e.seq}; entries are missing or reordered")
            if e.prev != prev:
                raise TamperEvident(f"entry {i} ({e.kind}): prev digest does not match entry {i - 1}")
            want = _digest(e.prev, Entry.payload(e.seq, e.kind, e.at, e.body))
            if e.digest != want:
                raise TamperEvident(f"entry {i} ({e.kind}): body has been altered since it was written")
            prev = e.digest

    @property
    def intact(self) -> bool:
        try:
            self.verify()
            return True
        except TamperEvident:
            return False

    # ── export — always available, never negotiated ─────────────────────────
    def to_jsonl(self) -> str:
        """
        The whole record, one entry per line. Your data is a folder you can walk
        away with; this is that sentence implemented.
        """
        return "".join(e.to_json() + "\n" for e in self._entries)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_canonical({"case_id": self.case_id}) + "\n")
            fh.write(self.to_jsonl())

    @classmethod
    def load(cls, path: str) -> "Tape":
        with open(path, encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        header = json.loads(lines[0])
        entries = []
        for ln in lines[1:]:
            d = json.loads(ln)
            entries.append(Entry(seq=d["seq"], kind=d["kind"], at=d["at"],
                                 body=d["body"], prev=d["prev"], digest=d["digest"]))
        t = cls(header["case_id"], entries)
        t.verify()
        return t


# ── a fold anyone can read, as the worked example of the idea ───────────────
def state_at(tape: Tape) -> str | None:
    """The case's current lifecycle state: a fold, like everything else."""
    return tape.fold(
        lambda acc, e: e.body.get("to", acc) if e.kind == "transition" else acc,
        None,
    )


def timeline(tape: Tape) -> list[tuple[int, str]]:
    """(minute, state) for every transition. Feeds floor/closure.py."""
    return tape.fold(
        lambda acc, e: acc + [(e.at, e.body["to"])] if e.kind == "transition" else acc,
        [],
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    t = Tape.load(sys.argv[1])
    print(f"case {t.case_id} — {len(t)} entries, head {t.head[:16]}…")
    print(f"chain: {'INTACT' if t.intact else 'BROKEN'}")
    print(f"state: {state_at(t)}")
    sup = t.superseded()
    if sup:
        print(f"superseded (still on the tape): {sorted(sup)}")
