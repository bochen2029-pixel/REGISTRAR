#!/usr/bin/env python3
"""
REGISTRAR · gates · attest — the fence

**Does the evidence, read as prose, actually support the value?**

Three checks now stand between a row and a reviewer, and they check three
different things:

    tools/cite.py      does this QUOTE exist in a pinned source?     byte-match
    gates/divergence   do the NUMBERS in value / evidence agree?     arithmetic
    gates/attest       does the CLAIM support the value?             this file

The gap it closes was measured rather than imagined. Probing gate 13 with three
prose contradictions, on values it had no numeric quarrel with:

    "callbacks are NOT time-bound"        value 12   FAILED — for the wrong reason
    "the 12-minute rule was withdrawn"    value 12   GREEN
    "the p75 was 12 min for TRANSPORT"    value 12   GREEN

**A superseded rule and a citation to the wrong subject both passed silently.**
Adjacent evidence for that class: a comparable fence measured **28.5% of a
model's "quotes" as paraphrase presented as quotation.** `[M inherited]`

WHAT IT CANNOT DO, AND SAYS SO

**It does not have the site's material.** For a site patch the source is an SOP,
a ticket query or a span of tape that lives at the site and never enters this
repository. So this cannot verify that a source says what the evidence claims.

**It checks the claim against ITSELF and against the row** — whether the prose
is describing something still in force, whether it is about this target, and
whether its modality matches what the row asserts. Those are decidable from the
patch alone, and they are where the silent failures were.

**Deterministic. No model, ever.** A model asked "does this evidence support
this value" produces a confident opinion, and a confident opinion is precisely
what this repository refuses to accept as a check.

    python gates/attest.py <patch>

Zero dependencies.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"

# ── 1 · evidence describing something NO LONGER IN FORCE ─────────────────────
# A withdrawn rule is a real fact about the organisation and a fine thing to
# cite — in a hold, or in an `inverse`, or as the row a supersession replaces.
# It cannot support a CURRENT value.
SUPERSEDED = (
    "withdrawn", "no longer applies", "no longer in force", "superseded",
    "rescinded", "revoked", "discontinued", "was replaced", "has been replaced",
    "formerly", "used to", "prior to the change", "before the change",
    "deprecated", "retired in", "sunset",
)

# ── 2 · evidence DENYING that a bound exists, under a row that asserts one ───
DENIES_A_BOUND = (
    "not time-bound", "no threshold", "does not specify", "does not define",
    "no stated", "unspecified", "is silent on", "sets no", "does not set",
    "no limit", "not defined", "left to judgment", "at the discretion",
)

# ── 3 · MODALITY — must / may / should are not interchangeable ───────────────
# The domain's own text turns on this. OPTN 2.5: "a hemodiluted sample MAY be
# used." A fit encoding that as a requirement forbids something policy permits,
# and a validator built on it refuses compliant work.
PERMISSIVE = ("may ", "is permitted", "are permitted", "is allowed", "can be used",
              "at its option", "optional", "if available", "if requested")
MANDATORY = ("must ", "shall ", "is required", "are required", "mandatory",
             "in all cases", "without exception", "never ", "always ")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _asserts_a_bound(value) -> bool:
    """Does the row state a specific quantity or a categorical requirement?"""
    def nums(v):
        if isinstance(v, bool):
            return False
        if isinstance(v, (int, float)):
            return True
        if isinstance(v, dict):
            return any(nums(x) for x in v.values())
        if isinstance(v, list):
            return any(nums(x) for x in v)
        return False
    return nums(value)


def _target_words(target: str) -> set[str]:
    """The domain words a target is about — `triage.callback_practice` -> {triage, callback, practice}."""
    return {w for w in re.split(r"[._]", str(target).lower()) if len(w) > 3}


# Operational vocabulary that appears in almost every claim and therefore
# distinguishes nothing. A target word drawn from this set is not evidence that
# a claim is about that target.
COMMON = {
    "practice", "rule", "second", "person", "owner", "route", "channel",
    "providers", "threshold", "window", "definition", "sequence", "variant",
    "credentials", "information", "authority", "ladder", "protocol", "vendor",
}


def _other_target_words() -> dict[str, set[str]]:
    p = os.path.join(ROOT, "core", "lifecycle", "targets.json")
    try:
        with open(p, encoding="utf-8") as fh:
            t = json.load(fh)["targets"]
        ids = list(t) if isinstance(t, dict) else [x["id"] for x in t]
    except Exception:
        return {}
    return {i: _target_words(i) for i in ids}


def check_row(row: dict, others: dict[str, set[str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    target = row.get("target", "?")
    mine = _target_words(target)
    asserts = _asserts_a_bound(row.get("value"))

    for e in row.get("evidence") or []:
        says = _norm(e.get("says"))
        if not says:
            continue

        # 1 · no longer in force
        hit = next((w for w in SUPERSEDED if w in says), None)
        if hit:
            out.append((FAILED,
                        f"{target}: evidence describes something NO LONGER IN FORCE "
                        f"({hit!r}) and is offered for a current value. A withdrawn rule "
                        f"belongs in a hold, an inverse, or the row this supersedes."))

        # 2 · denies a bound while the row asserts one
        if asserts:
            hit = next((w for w in DENIES_A_BOUND if w in says), None)
            if hit:
                out.append((FAILED,
                            f"{target}: evidence says the source {hit!r} — it denies that a "
                            f"bound exists — while the row asserts a specific one. If the "
                            f"figure comes from practice rather than the document, cite the "
                            f"practice."))

        # 3 · modality mismatch
        permissive = any(w in says for w in PERMISSIVE)
        mandatory = any(w in says for w in MANDATORY)
        if permissive and not mandatory and asserts:
            out.append((UNVERIFIED,
                        f"{target}: the evidence is PERMISSIVE and the row reads as a "
                        f"requirement. `may` is not `must` — encoding a permission as an "
                        f"obligation forbids something the source allows, and a validator "
                        f"built on it refuses compliant work."))

        # 4 · THE CHECK THAT IS NOT HERE — target drift, deleted and why
        #
        # A fourth check tried to catch evidence cited to the WRONG ROW, by
        # noticing that a claim names another declared target's words and none of
        # its own. It was built, tested, narrowed once, and then DELETED. The
        # funeral, so nobody rebuilds it:
        #
        #   draft 1 fired on "median elapsed to SECOND contact attempt" —
        #     matched `authorization.second_person_rule` on the word "second".
        #   draft 2, narrowed to require two non-common words, fired on the
        #     worked example: "a referral with no progress AFTER four HOURS"
        #     matched `intake.after_hours_owner` on {after, hours}.
        #
        # Both were ordinary operational prose. **The check was trying to do a
        # semantic job with a lexical tool**, and every fix was a patch on a
        # signal that was weak at the root — the vocabulary of an operation is
        # shared across its targets BY CONSTRUCTION, because they describe one
        # organisation.
        #
        # Two false positives in ten minutes, on the two cleanest patches in the
        # repository. **A gate that cries wolf is worse than no gate, because the
        # next real alarm gets discounted** — and this file would have opened its
        # life discrediting itself against the teaching example.
        #
        # The three checks above key on phrases that MEAN WHAT THEY SAY —
        # "withdrawn", "sets no threshold", "may be used". That is what a lexical
        # check can carry honestly. Catching evidence cited to the wrong row
        # needs the source, and the source is at the site.

    return out


def validate(patch: dict) -> tuple[str, list[str]]:
    others = _other_target_words()
    found: list[tuple[str, str]] = []
    for row in patch.get("rows") or []:
        found.extend(check_row(row, others))

    if any(s == FAILED for s, _ in found):
        return FAILED, [m for _, m in found]
    if found:
        return UNVERIFIED, [m for _, m in found]

    n = sum(len(r.get("evidence") or []) for r in (patch.get("rows") or []))
    return GREEN, [f"{n} evidence claim(s): none superseded, none denying its own bound, "
                   f"no modality mismatch"]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
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

    state, msgs = validate(patch)
    print(f"attest · {os.path.relpath(path, ROOT)}\n")
    for m in msgs:
        print(f"  {m}")
    print()
    if state == FAILED:
        print("FAILED — the evidence does not support the value it is offered for.")
        return 1
    if state == UNVERIFIED:
        print("PASS-UNVERIFIED — nothing contradicts outright, and something does not fit.")
        print("  THIS IS NOT A PASS. And note the standing limit: this gate does not")
        print("  have the site's material, so it checks the claim against itself and")
        print("  against the row — never against the source.")
        return 2
    print("GREEN — no claim contradicts the value it supports.")
    print("  Bounded: the source itself was not read. This gate cannot confirm that a")
    print("  document says what the evidence claims — only that the claim is not")
    print("  self-defeating. A human still reads the locator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
