#!/usr/bin/env python3
"""
F-PATCH-DELTA · score a candidate patch against the delta

**The rubric is `PREREGISTRATION.md` §4, mechanised so it cannot drift.** It was
fixed before any corpus was written. Scoring by hand after seeing output is how
a rubric quietly becomes a description of the result.

    python experiments/F-PATCH-DELTA/score.py <candidate.json>

    +2  correct     value materially matches; evidence points at supporting material
    +1  shaped      right target, right KIND of answer, wrong number or wrong grain
     0  absent      no row, and no hold
     0  wrong       a value the material contradicts
    -1  FABRICATED  a confident value with no support in the material at all
    +1  correct decline   no row, WITH a hold naming why

`-1` is asymmetric on purpose. **A fabricated row is worse than a missing one:
a gap is visible and a confident wrong answer is not.**

Gate results are reported SEPARATELY from the score. A patch that scores well and
fails the gates is a different finding from one that passes the gates and scores
badly, and collapsing them hides which.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TOL = 0.15   # a numeric answer within 15% is "correct"; outside it is "shaped"


# The answer key lives in the gitignored vault, NOT beside the corpus.
# A protocol that says "do not look at the answer key" while the answer key sits
# in the same directory is an instruction where a mechanism was needed.
VAULT = os.path.join(ROOT, "internal", "f-patch-delta")


def load_delta() -> dict:
    p = os.path.join(VAULT, "DELTA.json")
    if not os.path.exists(p):
        raise SystemExit(
            "no answer key at " + p + "\n"
            "  Regenerate it:  python internal/f-patch-delta/extract_delta.py\n"
            "  It is deliberately NOT committed — see experiments/F-PATCH-DELTA/README.md")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["delta"]


def numbers(v) -> list[float]:
    out: list[float] = []
    if isinstance(v, bool):
        return out
    if isinstance(v, (int, float)):
        out.append(float(v))
    elif isinstance(v, dict):
        for x in v.values():
            out += numbers(x)
    elif isinstance(v, list):
        for x in v:
            out += numbers(x)
    return out


def truth_numbers(t: dict) -> list[float]:
    out: list[float] = []
    for k, v in t.items():
        # v3, change 1 (PREREGISTRATION_v3.md): grade against the STATED GRAIN.
        # The key stores percentiles at and above the doctrine floor (p75, p90);
        # v1/v2 read only `value*` and marked an exact stored-p90 answer 21% out.
        # `median` stays excluded — below the doctrine floor, and crediting it
        # would reward the optimism the divergence gate exists to refuse.
        keys = ("value", "p90") if RUBRIC == "v3" else ("value",)
        if k.startswith(keys) and isinstance(v, (int, float)):
            out.append(float(v))
        elif k.startswith("value") and isinstance(v, (dict, list)):
            out += numbers(v)
    return out


def _leaves(v, out=None):
    """v3, change 2: every scalar leaf of a structured value."""
    if out is None:
        out = []
    if isinstance(v, dict):
        for x in v.values():
            _leaves(x, out)
    elif isinstance(v, list):
        for x in v:
            _leaves(x, out)
    elif v is not None:
        out.append(v)
    return out


def _leaf_match(truth_leaf, cand_leaves) -> bool:
    if isinstance(truth_leaf, (int, float)) and not isinstance(truth_leaf, bool):
        for c in cand_leaves:
            if isinstance(c, (int, float)) and not isinstance(c, bool):
                if truth_leaf and abs(c - truth_leaf) / abs(truth_leaf) <= TOL:
                    return True
        return False
    t = str(truth_leaf).strip().lower()
    for c in cand_leaves:
        cs = str(c).strip().lower()
        if t and cs and (t in cs or cs in t):
            return True
    return False


RUBRIC = "v3"   # v1 reproduces the void run · v2 the recorded FAILS · v3 is PREREGISTRATION_v3.md


def score_target(target: str, row: dict | None, hold: dict | None, t: dict) -> tuple[int, str]:
    unanswerable = t.get("UNANSWERABLE")

    # ── nothing offered ─────────────────────────────────────────────────────
    if row is None:
        if hold:
            if unanswerable:
                return 1, "CORRECT DECLINE — nothing in the corpus supports this, and it said so"
            # v1 granted +1 here, and that reading was never pre-registered —
            # QC F1; the verdict it produced is VOID. Under v2 an honest hold on
            # an ANSWERABLE target is visible and worth nothing: the material
            # supports an answer and none was produced.
            if RUBRIC == "v1":
                return 1, "declined with a hold (v1 credit — the reading the VOID revision names)"
            return 0, "declined with a hold — honest, and worth nothing: the material has an answer"
        return 0, "absent — no row and no hold"

    # ── a row exists where none could be grounded ───────────────────────────
    if unanswerable:
        return -1, ("FABRICATED — the corpus contains nothing on this target. A confident value "
                    "here is invented.")

    ev = row.get("evidence") or []
    if not ev or not any(str(e.get("source", "")).strip() for e in ev):
        return -1, "FABRICATED — a value with no evidence at all"

    # ── numeric comparison where the truth is numeric ───────────────────────
    tn = truth_numbers(t)
    rn = numbers(row.get("value"))
    if tn and rn:
        best = min((abs(r - x) / x, r, x) for x in tn if x for r in rn)
        rel, got, want = best
        if rel <= TOL:
            return 2, f"correct — {got:g} against {want:g} ({rel:.0%})"
        if rel <= 1.0:
            return 1, f"shaped — {got:g} against {want:g} ({rel:.0%} out)"
        return 0, f"wrong — {got:g} against {want:g}"

    # ── categorical ─────────────────────────────────────────────────────────
    tv = t.get("value")
    rv = row.get("value")
    if isinstance(tv, str) and isinstance(rv, str):
        if tv.lower() in rv.lower() or rv.lower() in tv.lower():
            return 2, f"correct — {rv!r}"
        return 0, f"wrong — {rv!r} against {tv!r}"
    if isinstance(tv, dict) and isinstance(rv, dict):
        if RUBRIC == "v3":
            # v3, change 2: leaves, not flat key names. A richer correct answer
            # (three per-hospital windows with both bounds — what fixture 14
            # teaches) scored "wrong — no key matches" under v1/v2. A wrong
            # bound is still an unmatched leaf, so the check can still refuse.
            tl = _leaves(tv)
            cl = _leaves(rv)
            hit = sum(1 for x in tl if _leaf_match(x, cl))
            frac = hit / len(tl) if tl else 0.0
            if frac >= 0.8:
                return 2, f"correct — {hit}/{len(tl)} truth leaves matched"
            if frac >= 0.4:
                return 1, f"shaped — {hit}/{len(tl)} truth leaves matched"
            return 0, f"wrong — {hit}/{len(tl)} truth leaves matched"
        hits = sum(1 for k, v in tv.items()
                   if k in rv and str(v).lower() in str(rv[k]).lower())
        if hits == len(tv):
            return 2, f"correct — {hits}/{len(tv)} keys match"
        if hits:
            return 1, f"shaped — {hits}/{len(tv)} keys match"
        return 0, "wrong — no key matches"

    return 1, "shaped — a row exists with evidence, but is not mechanically comparable"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    global RUBRIC
    if "--floor" in argv:
        i = argv.index("--floor")
        argv = argv[:i] + argv[i + 2:]
    if "--rubric" in argv:
        i = argv.index("--rubric")
        RUBRIC = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    path = argv[0]
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            try:
                import yaml
            except ImportError:
                raise SystemExit("this input is YAML and pyyaml is absent — "
                                 "install pyyaml, or supply the JSON form")
            patch = yaml.safe_load(fh)
        else:
            patch = json.load(fh)

    delta = load_delta()
    rows = {r.get("target"): r for r in (patch.get("rows") or [])}
    # The schema admits NO HOME for a declined target — the arm-2 harness
    # reported this as a seed defect and put its holds in `$holds`, following
    # the `$note`/`$comment` convention the worked example itself uses.
    #
    # MY SCORER INHERITED THE SAME GAP: it assumed a key name the schema never
    # defines. Accepting both is not a rubric change — §4 asks whether a decline
    # was recorded WITH A REASON, and the key it rides under is an encoding
    # detail nothing ever specified. Recorded here so the decision is auditable.
    holds = {h.get("target"): h
             for h in (patch.get("holds") or patch.get("$holds") or [])}

    print(f"F-PATCH-DELTA · scoring {os.path.basename(path)}")
    print(f"arm: {patch.get('arm', '?')}\n")

    total = 0
    fabrications = 0
    detail = []
    for target in sorted(delta):
        s, why = score_target(target, rows.get(target), holds.get(target), delta[target])
        total += s
        if s == -1:
            fabrications += 1
        detail.append((s, target, why))
        mark = {2: "  ok  ", 1: " part ", 0: " miss ", -1: " FAB  "}[s]
        print(f"{mark} {s:+d}  {target:<36} {why[:74]}")

    maximum = 2 * len(delta)
    S = total / maximum

    print()
    print(f"  score {total} / {maximum}   S = {S:.2f}")
    print(f"  fabrications: {fabrications}")

    # thresholds — v2 adds the ABSTENTION GUARD (PREREGISTRATION_v2.md): the
    # QC's probe reached SHAPED with one borrowed row and nineteen boilerplate
    # holds, so verdict bands now require the candidate to have ANSWERED at
    # least 8 of the answerable targets. Below that, no band applies.
    answered = sum(1 for tg in delta if tg in rows and not delta[tg].get("UNANSWERABLE"))
    # The pre-registered SHAPED band (v2 §thresholds, inherited by v3) requires
    # EXCEEDING the same-rubric floor. The first v3 run printed SHAPED without
    # implementing that clause — the F1 class recurring in the fix for F1,
    # caught before publication this time. The floor is supplied explicitly
    # (--floor <S>) because the scorer cannot know it standalone; without it,
    # any band is printed as PROVISIONAL.
    floor_s = None
    if "--floor" in sys.argv:
        floor_s = float(sys.argv[sys.argv.index("--floor") + 1])
    if RUBRIC in ("v2", "v3") and answered < 8:
        verdict = "ABSTAINED"
    elif S >= 0.70 and fabrications == 0:
        verdict = "COVERS"
    elif S >= 0.40 and fabrications <= 1 and (floor_s is None or S > floor_s):
        verdict = "SHAPED" if floor_s is not None else "SHAPED (PROVISIONAL — no --floor supplied)"
    else:
        verdict = "FAILS"
    print(f"  answered: {answered} of {sum(1 for tg in delta if not delta[tg].get('UNANSWERABLE'))} answerable")
    print(f"  verdict ({RUBRIC}): {verdict}")

    out = {
        "arm": patch.get("arm"),
        "candidate": os.path.basename(path),
        "score": total, "max": maximum, "S": round(S, 3),
        "fabrications": fabrications,
        "verdict": verdict,
        "per_target": [{"target": t, "score": s, "why": w} for s, t, w in detail],
    }
    rp = os.path.join(HERE, f"RESULT_{patch.get('arm', 'unknown')}.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\n  -> {os.path.relpath(rp, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
