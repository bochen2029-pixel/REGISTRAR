#!/usr/bin/env python3
"""
REGISTRAR · demo · the replay board
─────────────────────────────────────────────────────────────────────────────
**Watch the loop.** One real case from the synthetic site (`site_v4`), played
back through the percept stream, with the floor judging at every boundary —
surfacing when a derived deadline tightens, holding (on the record, with the
margin) when the instant deserves nothing.

    python demo/replay.py                   play it, ~45 seconds
    python demo/replay.py --fast            no sleeps (CI, selftest)
    python demo/replay.py --case C-0123     a specific case
    python demo/replay.py --transcript F    also write the full transcript
    python demo/replay.py --selftest        run twice, assert byte-identical

WHAT IS REAL AND WHAT IS STAGED — stated, not implied

  REAL   the case (a row-set from site_v4's tape) · every duration on it ·
         the site figures the constraints use (folded from the full tape at
         startup) · the closure's arithmetic · the percept stream (this is
         the first case it has ever carried)
  [D]    the interleaving. The tape records durations, not wall-clock
         timestamps, so offsets BETWEEN events are composed for display and
         labeled [D] where they appear.

HOW THE JUDGE WORKS — the model, because it was got wrong once

  Constraints come in two kinds and the first draft conflated them. A HARD
  bound (the OR window, order-of-operations) is law: violated means breached,
  and the past pins to what actually happened — **a forecast never argues with
  history.** A BUDGET (the site's own p90s) is the projection: future stages
  are assumed to consume their budget, and the closure computes what that
  assumption implies — "for tonight's window, the match run must be in by
  HH:MM." That number is the marquee: nobody set it, no timer knows it, and
  `binding_path` recovers the chain that produced it from the same
  computation. When reality beats a budget (an offer in 78 minutes against a
  237 budget), slack comes BACK — the board shows that too, because a
  projection that only tightens is an alarm, not a judgment.

THE THREE THINGS THIS DEMONSTRATES

  1 · THE UNPROMPTED CATCH — a derived deadline, surfaced with its derivation.
  2 · SILENCE ON THE RECORD — every held boundary written with its margin.
  3 · THE MEASURES — folds over the same tape, denominators first; where a
      column is missing the board says NOT DERIVABLE rather than improvising.

Zero dependencies. Deterministic: `--selftest` replays twice and asserts the
transcripts byte-identical — replay determinism is a proof obligation
(SPEC §7), not a wish. Honest gap, on the record: `core/measures/` as a module
remains UNBUILT; the folds here are demo-grade and say so.
"""

from __future__ import annotations

import csv
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in ("floor", "percepts", "core"):
    sys.path.insert(0, os.path.join(ROOT, p))

from closure import REFERENCE, STN, hhmm  # noqa: E402
from stream import Stream  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SITE = os.path.join(ROOT, "experiments", "F-PATCH-DELTA", "site_v4", "tape")
OUT = os.path.join(HERE, "_out")

WARN_SLACK = 120   # surface when a projected deadline is within this
W = 78


# ── the tape, and the folds over it ─────────────────────────────────────────
def rows(name: str) -> list[dict]:
    with open(os.path.join(SITE, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def pct(xs: list[float], q: float) -> int:
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo))


def site_figures(t: dict) -> dict:
    lab = [float(w["minutes_drawn_to_resulted"]) for w in t["workup"]]
    mob = [float(r["minutes_or_scheduled_to_incision"]) for r in t["recovery"]
           if r["team"] == "in_house"]
    offer = [float(a["minutes_matchrun_to_primary_acceptance"]) for a in t["allocation"]]
    return {
        "lab_p75": pct(lab, .75), "lab_p90": pct(lab, .90), "lab_n": len(lab),
        "mob_p90": pct(mob, .90), "mob_n": len(mob),
        "offer_p90": pct(offer, .90), "offer_n": len(offer),
    }


def pick_case(t: dict, want: str | None) -> dict:
    """
    Deterministic: an H-1207 in-house recovery case (the evening OR block is
    the binding constraint there), arriving in the morning so the same-evening
    chain is tight without being theatre. Tie-break: longest lab turnaround,
    then case id.
    """
    ref = {r["referral_id"]: r for r in t["referrals"]}
    wu = {w["case_id"]: w for w in t["workup"]}
    al = {a["case_id"]: a for a in t["allocation"]}
    au = {a["case_id"]: a for a in t["authorization"]}
    cands = []
    for r in t["recovery"]:
        cid = r["case_id"]
        if cid not in wu or cid not in al or cid not in au:
            continue
        w = wu[cid]
        rf = ref.get(w["referral_id"])
        if rf is None:
            continue
        c = {"case": cid, "recovery": r, "workup": w, "alloc": al[cid],
             "auth": au[cid], "ref": rf}
        if want:
            if cid == want:
                return c
            continue
        if (r["hospital"] == "H-1207" and r["team"] == "in_house"
                and 7 <= int(rf["arrived_hour"]) <= 10):
            cands.append(c)
    if want:
        raise SystemExit(f"case {want!r} not found with a full row-set")
    if not cands:
        raise SystemExit("no H-1207 morning in-house recovery case — corpus changed?")
    cands.sort(key=lambda c: (-float(c["workup"]["minutes_drawn_to_resulted"]), c["case"]))
    return cands[0]


# ── rendering ───────────────────────────────────────────────────────────────
class Board:
    def __init__(self, sleepy: bool):
        self.lines: list[str] = []
        self.sleepy = sleepy

    def say(self, text: str = "", beat: float = 0.0) -> None:
        for ln in text.split("\n"):
            print(ln)
            self.lines.append(ln)
        if self.sleepy and beat:
            time.sleep(beat)

    def rule(self, ch: str = "─") -> None:
        self.say(ch * W)


def clock(wall0: int, minute: int) -> str:
    return hhmm(wall0 + minute)


# ── the judge: hard bounds pin to history, budgets project the future ───────
def projection(fig: dict, done: dict[str, int], wall0: int) -> STN:
    s = STN()
    # HARD, L2 — the site's own OR window (its tape, 13/13 evening clamps)
    clamp_close = (23 * 60) - wall0 + (1440 if (23 * 60) < wall0 else 0)
    s.window("cross_clamp", clamp_close - 240, clamp_close,
             "H-1207 evening OR block 19:00–23:00 · the site's own tape", "L2")

    def stage(later: str, earlier: str, budget: int, label: str, layer: str) -> None:
        """
        A future stage is ASSUMED TO CONSUME its budget — at_least, never an
        equality. That is what creates backward pressure from the window: the
        earliest feasible clamp is the sum of remaining budgets, and the margin
        between that and 23:00 is the number a coordinator actually needs. A
        pinned stage is history and gets no forecast at all.
        """
        if later in done:
            return                       # a forecast never argues with history
        s.at_least(later, earlier, budget, label, layer)

    stage("serology_resulted", "workup_drawn", fig["lab_p90"],
          f"lab p90 {fig['lab_p90']}m · site tape n={fig['lab_n']} (contract says 240)", "L3")
    stage("match_run", "serology_resulted", 15,
          "serology gates the match run · +15m [D]", "L1")
    stage("primary_acceptance", "match_run", fig["offer_p90"],
          f"offer budget p90 {fig['offer_p90']}m · site tape n={fig['offer_n']}", "L2")
    stage("or_scheduled", "primary_acceptance", 15, "scheduling gap 15m [D]", "L2")
    stage("incision", "or_scheduled", fig["mob_p90"],
          f"mobilisation p90 {fig['mob_p90']}m · site tape n={fig['mob_n']} in-house", "L2")
    stage("cross_clamp", "incision", 30, "incision to clamp 30m [D]", "L1")

    for name, at in done.items():        # history, pinned exactly
        s.at_most(name, REFERENCE, at, "occurred", "")
        s.at_least(name, REFERENCE, at, "occurred", "")
    return s


BUDGETS = {
    "serology_resulted": lambda f: f["lab_p90"],
    "match_run": lambda f: 15,
    "primary_acceptance": lambda f: f["offer_p90"],
    "or_scheduled": lambda f: 15,
    "incision": lambda f: f["mob_p90"],
    "cross_clamp": lambda f: 30,
}
BUDGET_LABEL = {
    "serology_resulted": "lab p90 {lab_p90}m (n={lab_n}; contract says 240)",
    "match_run": "serology gates the match run · 15m [D]",
    "primary_acceptance": "offer budget p90 {offer_p90}m (n={offer_n})",
    "or_scheduled": "scheduling gap 15m [D]",
    "incision": "mobilisation p90 {mob_p90}m (n={mob_n}, in-house)",
    "cross_clamp": "incision to clamp 30m [D]",
}

# HARD bounds checked against history — a breach is a finding, never infeasibility.
HARD = [("serology_resulted", "workup_drawn", 240,
         "reference-lab CONTRACT: four hours (Schedule B) — the binder's promise")]


def replay(case: dict, fig: dict, board: Board, stream_path: str) -> dict:
    ref, w, al, rec = case["ref"], case["workup"], case["alloc"], case["recovery"]
    wall0 = int(ref["arrived_hour"]) * 60

    t_draw = 90
    t_resulted = t_draw + round(float(w["minutes_drawn_to_resulted"]))
    t_match = t_resulted + 15
    t_accept = t_match + round(float(al["minutes_matchrun_to_primary_acceptance"]))
    t_orsched = t_accept + 20
    t_incision = t_orsched + round(float(rec["minutes_or_scheduled_to_incision"]))
    t_clamp_wall = int(rec["cross_clamp_hour"]) * 60 + int(rec["cross_clamp_minute"])
    t_clamp = t_clamp_wall - wall0 + (1440 if t_clamp_wall < wall0 else 0)

    timeline = [
        (0, "referral", f"referral {ref['referral_id']} · {rec['hospital']} · "
                        f"arrived {clock(wall0, 0)}"),
        (t_draw, "workup_drawn", "serology panel drawn  [offset D]"),
        (t_resulted, "serology_resulted",
         f"panel resulted — {w['minutes_drawn_to_resulted']}m at {w['lab']}  (REAL)"),
        (t_match, "match_run", "match run submitted  [+15m D]"),
        (t_accept, "primary_acceptance",
         f"primary acceptance — the offer took {al['minutes_matchrun_to_primary_acceptance']}m  (REAL)"),
        (t_orsched, "or_scheduled", "OR requested at the donor hospital  [offset D]"),
        (t_incision, "incision",
         f"incision — mobilisation took {rec['minutes_or_scheduled_to_incision']}m  (REAL)"),
        (t_clamp, "cross_clamp",
         f"cross-clamp — REAL wall-clock from the tape"),
    ]

    st = Stream(path=stream_path, capacity=10_000)
    st.open()
    st.declare_self("board")

    done: dict[str, int] = {}
    surfaced_for: set[str] = set()
    breached: set[str] = set()
    marquee = ""
    last_slack: dict[str, int] = {}

    board.rule("═")
    board.say(f"REPLAY · case {case['case']} · Fairbank Donor Network · site_v4 (synthetic)")
    board.say("the floor judging at every boundary — every silence on the record")
    board.rule("═")
    board.say()

    for at, name, desc in timeline:
        st.emit("tick", "world", {"event": name}, at=at)
        if name != "referral":
            done[name] = at
        board.say(f"{clock(wall0, at):>8}  ● {desc}", beat=0.9)

        # hard bounds vs history — the breach is a finding
        for later, earlier, bound, label in HARD:
            if later in done and earlier in done and later not in breached:
                actual = done[later] - done[earlier]
                if actual > bound:
                    breached.add(later)
                    st.emit("surface", "board",
                            {"breach": label, "bound": bound, "actual": actual},
                            reason="b", at=at)
                    board.say()
                    board.say("  ▲ SURFACE — CONTRACT BREACHED, on the record:")
                    board.say(f"      {label}")
                    board.say(f"      promised {bound}m · took {actual}m · "
                              f"the site's own p90 ({fig['lab_p90']}m) already said the")
                    board.say(f"      promise was optimistic. The binder is not the operation.",
                              beat=1.2)

        closure = projection(fig, done, wall0).close()
        if not closure.consistent:
            cyc = closure.negative_cycle() or []
            key = "·".join(cyc)
            if key not in surfaced_for:
                surfaced_for.add(key)
                st.emit("surface", "board", {"infeasible": cyc}, reason="b", at=at)
                board.say("  ▲ SURFACE — under the site's own budgets, tonight's window is")
                board.say("    UNREACHABLE: " + " → ".join(cyc))
            board.say()
            continue

        # THE STATE VARIABLE: how much of tonight's window survives if every
        # remaining stage consumes its p90 budget. Violently state-dependent —
        # exactly what §2b says the utility of speaking is.
        margin = None
        if "cross_clamp" not in done:
            margin = closure.latest("cross_clamp") - closure.earliest("cross_clamp")
        nxt = next((n for _t, n, _d in timeline
                    if n != "referral" and n not in done), None)

        if margin is not None and nxt is not None:
            prev = last_slack.get("margin")
            last_slack["margin"] = margin
            head = ""

            if margin < WARN_SLACK and "margin" not in surfaced_for:
                surfaced_for.add("margin")
                head = (f"under the site's own budgets, tonight's window has "
                        f"{margin}m of margin")
            elif margin < WARN_SLACK and prev is not None and prev - margin >= 30:
                head = (f"the margin NARROWED: {prev}m → {margin}m — a stage "
                        f"overran its budget")
            elif prev is not None and margin - prev >= 60:
                head = (f"margin RETURNED: {prev}m → {margin}m — a stage beat its "
                        f"budget. slack can come back; an alarm cannot say so")

            if head:
                st.emit("deadline", "closure",
                        {"event": nxt, "latest": closure.latest(nxt)}, at=at)
                st.emit("surface", "board",
                        {"window_margin": margin, "next": nxt,
                         "next_by": closure.latest(nxt)}, reason="b", at=at)
                board.say()
                board.say("┌" + "─" * (W - 2) + "┐")
                board.say(f"  ▲ SURFACE — {head}")
                board.say(f"    {nxt} must be in by {clock(wall0, closure.latest(nxt))} — "
                          f"nobody set that deadline. it is")
                board.say("    the transitive consequence of:")
                run = at
                board.say(f"        {'now':<52}{clock(wall0, run):>8}")
                for _t2, n2, _d2 in timeline:
                    if n2 == "referral" or n2 in done:
                        continue
                    b = BUDGETS.get(n2)
                    if b is None:
                        continue
                    amt = b(fig)
                    run += amt
                    board.say(f"        + {BUDGET_LABEL[n2].format(**fig):<50}{clock(wall0, run):>8}")
                board.say(f"        {'window closes':<52}"
                          f"{clock(wall0, closure.latest('cross_clamp')):>8}")
                board.say("    every budget above is the site's own tape. the chain is the")
                board.say("    finding — the catch a flat list of timers cannot make.")
                board.say("└" + "─" * (W - 2) + "┘", beat=1.6)
                if not marquee:
                    marquee = (f"{margin}m of window margin, derived at "
                               f"{clock(wall0, at)}; {nxt} due by "
                               f"{clock(wall0, closure.latest(nxt))}")
            else:
                st.emit("hold", "board",
                        {"window_margin": margin, "next": nxt}, reason="b", at=at)
                board.say(f"          · held — window margin {margin}m under the site's "
                          f"own budgets. on the record.", beat=0.35)
        elif margin is None:
            close_at = (23 * 60) - wall0 + (1440 if (23 * 60) < wall0 else 0)
            board.say(f"          case closed {close_at - at}m inside the window.", beat=0.5)
        board.say()

    foot = st.close()
    return {"foot": foot, "marquee": marquee}


# ── the measures ────────────────────────────────────────────────────────────
def measures(t: dict, board: Board) -> None:
    board.rule("═")
    board.say("MEASURES — folds over the full site_v4 tape (T5: denominator first)")
    board.say("demo-grade folds; core/measures/ as a module is UNBUILT, and this says so")
    board.rule()
    refs = t["referrals"]
    prog = [r for r in refs if r["progressed"] == "1"]
    board.say(f"  referrals on tape                 {len(refs)}   (referrals.csv)")
    board.say(f"  progressed to case                {len(prog)}/{len(refs)}"
              f"   = {100 * len(prog) // len(refs)}%")
    board.say(f"  recoveries                        {len(t['recovery'])}/{len(prog)}"
              f" progressed   = {100 * len(t['recovery']) // len(prog)}%")
    lab = [float(x["minutes_drawn_to_resulted"]) for x in t["workup"]]
    board.say(f"  reference-lab p75 / p90           {pct(lab, .75)}m / {pct(lab, .90)}m"
              f"   (n={len(lab)}; contract: 240m)")
    cb = [float(r["minutes_to_second_contact"]) for r in refs
          if r["minutes_to_second_contact"]]
    board.say(f"  second-contact p75                {pct(cb, .75)}m   (n={len(cb)}; SOP bound: 30m)")
    board.say("  authorization rate                NOT DERIVABLE — authorization.csv has no")
    board.say("                                    outcome column; a ratio without its")
    board.say("                                    denominator is not a measure (T5).")


def run_once(fast: bool, want_case: str | None, stream_path: str,
             display: str | None = None) -> list[str]:
    # a replay writes a FRESH stream — this is a rendering of a tape, not a
    # live tape, and two renderings must not interleave in one file
    if os.path.exists(stream_path):
        os.remove(stream_path)
    t = {n: rows(f"{n}.csv") for n in
         ("referrals", "workup", "allocation", "authorization", "recovery")}
    fig = site_figures(t)
    board = Board(sleepy=not fast)
    case = pick_case(t, want_case)

    board.say()
    r = replay(case, fig, board, stream_path)
    measures(t, board)

    board.rule("═")
    f = r["foot"]
    board.say(f"THE TAPE — surfaced {f['surfaced']} · held {f['suppressed']} · "
              f"total {f['total']} (by addition, never conflation) · dropped {f['dropped']}")
    if r["marquee"]:
        board.say(f"the catch: {r['marquee']}. derived, cited, unasked.")
    board.say(f"stream: {display or os.path.relpath(stream_path, ROOT)} — the first "
              f"case the percept stream has ever carried")
    board.rule("═")
    return board.lines


def main(argv: list[str]) -> int:
    fast = "--fast" in argv or "--selftest" in argv
    want = argv[argv.index("--case") + 1] if "--case" in argv else None
    os.makedirs(OUT, exist_ok=True)

    if "--selftest" in argv:
        # two distinct files, one display name — the FIRST selftest run failed
        # on its own footer: the transcripts differed by the stream filename.
        # The determinism harness caught the harness; kept as a comment because
        # that is the check working, not an embarrassment to hide.
        a = run_once(True, want, os.path.join(OUT, "selftest_a.jsonl"),
                     "demo/_out/stream.jsonl")
        print("\n… second replay …\n")
        b = run_once(True, want, os.path.join(OUT, "selftest_b.jsonl"),
                     "demo/_out/stream.jsonl")
        for pth in ("selftest_a.jsonl", "selftest_b.jsonl"):
            os.remove(os.path.join(OUT, pth))
        if a == b:
            print(f"\nSELFTEST GREEN — two replays, {len(a)} transcript lines, byte-identical.")
            return 0
        print("\nSELFTEST FAILED — replays diverged. Replay determinism is broken.")
        return 1

    lines = run_once(fast, want, os.path.join(OUT, "stream.jsonl"))
    if "--transcript" in argv:
        p = argv[argv.index("--transcript") + 1]
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"\ntranscript → {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
