#!/usr/bin/env python3
"""
REGISTRAR · percepts · collect
─────────────────────────────────────────────────────────────────────────────
Run the repository's own checks and record what they found.

This is what makes `percepts/` a completion log rather than an empty file. The
gates already name defects; the replay already finds violations; the closure
already derives deadlines nobody wrote down. **Until now each printed and
returned.** This collects them onto one append-only stream, in order, with the
reason each judgment happened.

    python percepts/collect.py <patch.json> [--tape t.jsonl] [--case c.json]

Runs at `off`. Nothing needs to be home — a completion that spans a week now
has a record of what it hit, when, and what it declined.

Zero dependencies.
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for d in ("core", "gates", "floor", "percepts"):
    sys.path.insert(0, os.path.join(ROOT, d))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from stream import DEFAULT_STREAM, Stream, report   # noqa: E402
import switch                                        # noqa: E402


def collect(patch_path: str | None, tape_path: str | None,
            case_path: str | None, stream_path: str = DEFAULT_STREAM) -> dict:
    s = Stream(stream_path)
    if not os.path.exists(stream_path):
        s.open()
    # law 6: our own output is never world
    s.declare_self("stream", "switch")

    s.emit("surface", "switch",
           {"state": switch.read(), "meaning": switch.MEANING[switch.read()]}, reason="f")

    # ── the gates ───────────────────────────────────────────────────────────
    if patch_path:
        from validate_patch import FAILED, UNVERIFIED, load_patch, load_targets, validate
        r = validate(load_patch(patch_path), load_targets())
        for state, gate, detail in r.rows:
            if state == FAILED:
                # a refusal is a percept: the defect, named in words
                s.emit("gate", "gates.validate_patch",
                       {"gate": gate, "verdict": state, "defect": detail}, reason="b")
            elif state == UNVERIFIED:
                # PASS-UNVERIFIED is a HOLD — considered, not decided. Recording
                # it as a pass would be the exact failure the three-state gate
                # exists to prevent.
                s.emit("hold", "gates.validate_patch",
                       {"gate": gate, "verdict": state, "why": detail}, reason="b")

        # expiries: a row that must re-earn its place
        import datetime as _dt
        today = _dt.date.today()
        for row in (load_patch(patch_path).get("rows") or []):
            try:
                exp = _dt.date.fromisoformat(str(row.get("expiry")))
            except Exception:
                continue
            days = (exp - today).days
            if days <= 90:
                s.emit("expiry", "schema",
                       {"target": row.get("target"), "expiry": str(exp), "days_left": days},
                       reason="t")

    # ── the replay ──────────────────────────────────────────────────────────
    if tape_path:
        from case import ENFORCED, replay
        from tape import Tape
        t = Tape.load(tape_path)
        for f in replay(t):
            s.emit("violation" if f.status == ENFORCED else "hold", "core.case",
                   {"rule": f.rule, "status": f.status, "detail": f.detail, "seq": f.seq},
                   reason="b")

    # ── the closure ─────────────────────────────────────────────────────────
    if case_path:
        from closure import hhmm, load_case
        stn, doc = load_case(case_path)
        c = stn.close()
        if not c.consistent:
            s.emit("violation", "floor.closure",
                   {"case": doc.get("id"), "infeasible": True,
                    "cycle": c.negative_cycle()}, reason="f")
        else:
            now = doc.get("now")
            for name in (doc.get("watch") or []):
                latest = c.latest(name)
                # a deadline nobody wrote down IS the finding
                body = {"case": doc.get("id"), "event": name, "latest": hhmm(latest),
                        "derived": True}
                if now is not None:
                    slack = c.slack(name, now)
                    body["slack_minutes"] = slack
                    if slack < 0:
                        body["breached"] = True
                        s.emit("deadline", "floor.closure", body, reason="b")
                        continue
                s.emit("hold", "floor.closure", body, reason="n")

    return s.close()


def main(argv: list[str]) -> int:
    def opt(flag):
        return argv[argv.index(flag) + 1] if flag in argv else None
    pos = [a for a in argv if not a.startswith("--")
           and (not argv.index(a) or argv[argv.index(a) - 1] not in ("--tape", "--case", "--stream"))]
    patch = pos[0] if pos else None
    out = opt("--stream") or DEFAULT_STREAM

    summary = collect(patch, opt("--tape"), opt("--case"), out)
    print()
    report(out)
    print()
    if summary["dropped"]:
        print(f"{summary['dropped']} percept(s) DROPPED — a defect, not a statistic.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
