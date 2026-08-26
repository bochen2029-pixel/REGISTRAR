#!/usr/bin/env python3
"""
F-PATCH-DELTA · ARM ① — the template prior

**The floor.** Fill the schema with plausible generic OPO defaults, using **no
site material at all.** This is what you get from the seed plus domain
familiarity and nothing else.

**Why the floor has to exist.** Without it a passing arm ② might only mean *the
schema is fillable by anyone* — that the twenty questions are leading enough
that generic answers score well. If ① scores near ②, **the schema is doing the
work and the harness is not**, and that is a FAILS regardless of ②'s absolute
score.

**Every prior below is declared with its source of belief**, so the arm is
inspectable rather than a black box. They are what a competent person would
write knowing the domain and nothing about this site — and notably, **most of
them are what a written SOP would say**, because generic defaults and written
policy converge. That convergence is the interesting part: the tape is where
they come apart.

    python experiments/F-PATCH-DELTA/arm1_template_prior.py

Deterministic. No site material is read — and there is a check at the bottom
that proves it.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EV = [{"kind": "prior", "source": "generic OPO template — NO SITE MATERIAL",
       "says": "industry-typical default"}]
SR = {"cases": 0, "would_have_matched": 0, "would_have_missed": 0, "window": "n/a — no site tape"}


def row(target: str, value, why: str) -> dict:
    return {
        "target": target, "layer": "L2", "value": value, "inverse": None,
        "evidence": [{"kind": "prior", "source": "generic OPO template — NO SITE MATERIAL",
                      "says": why}],
        "shadow_run": dict(SR),
        "expiry": "2027-08-26",
        "author": "",          # a machine leaves this empty — SPEC.md §2
        "$prior": why,
    }


# Each prior states WHY a generic answer would land there.
PRIORS = [
    row("intake.after_hours_owner", "on_call_supervisor",
        "an SOP almost always routes after-hours work to the on-call supervisor; that is what "
        "the org chart implies and what a policy document would say"),

    row("triage.callback_practice", {"callback_within_minutes": 30},
        "30 minutes is the round number a policy reaches for; it is also what most SOPs specify"),

    row("evaluation.reference_lab", {"turnaround_minutes": 240},
        "four hours is the standard contracted serology turnaround across the industry"),

    row("recovery.or_availability",
        {"cross_clamp_window": {"opens": "06:00", "closes": "10:00"}},
        "recovery is conventionally accommodated in an early-morning block before the elective "
        "list starts"),

    row("recovery.team_mobilisation", {"or_scheduled_to_incision_minutes": 120},
        "two hours is the usual planning figure for team mobilisation"),

    row("allocation.offer_window_practice", {"budget_minutes": 180},
        "three hours is the conventional allowance from match run to primary acceptance"),

    row("lapse.threshold", {"minutes_without_progression": 240},
        "four hours without progression is the common review trigger"),

    row("triage.ruleout_authority",
        {"listed_criterion": "coordinator", "clinical_judgment": "physician"},
        "the standard split: listed contraindications by coordinator, judgment calls by a physician"),

    row("authorization.approach_sequence",
        {"default": "in_person", "telephonic_when": "family unable to attend"},
        "in-person by default is near-universal practice"),

    row("authorization.second_person_rule", {"required_when": "donor_age_under_18"},
        "a second requester for minors is common practice"),

    row("management.protocol_variant", "standard adult targets",
        "most OPOs use standard targets without a local variant"),

    row("management.escalation_ladder",
        {"ladder": ["coordinator", "supervisor", "director", "medical_director"],
         "ack_minutes": 30},
        "a four-level ladder with a 30-minute acknowledgement is the conventional shape"),

    row("evaluation.on_site_vs_remote", "predominantly on site",
        "on-site workup remains the norm"),

    row("intake.channel", {"default": "interfaced where available, telephone otherwise"},
        "the standard mixed-channel arrangement"),

    row("evaluation.imaging_route", {"route": "PACS share"},
        "a PACS share is the usual arrangement where imaging is exchanged"),

    row("authorization.esignature_vendor", {"vendor": "DocuSign"},
        "DocuSign is the most widely deployed e-signature product"),

    row("allocation.credentials", {"mode": "named accounts"},
        "UNet access is by named account almost everywhere"),

    row("transport.providers",
        {"ground": "contracted courier", "air": "contracted charter"},
        "the standard two-mode arrangement"),

    row("intake.timely_referral_definition", {"minutes": 60},
        "one hour is the figure most commonly written into hospital agreements"),

    # THE TRAP. A template prior has no reason to decline anything — it has no
    # material to find empty, so it answers everything. That is exactly the
    # failure this target exists to detect, and arm 1 walks straight into it.
    row("transport.perfusion", {"provider": "contracted perfusion service"},
        "a contracted perfusion service is the usual arrangement"),
]


def main() -> int:
    patch = {
        "$comment": "ARM 1 — the template prior. Generated from declared generic OPO defaults "
                    "with NO SITE MATERIAL READ. This is the floor every other arm is read "
                    "against: if arm 2 scores near this, the schema is doing the work.",
        "arm": "1-template-prior",
        "schema_version": "0.1",
        "site": {"id": "fairbank", "name": "Fairbank Donor Network (FICTIONAL)"},
        "rows": PRIORS,
        "holds": [],   # a template prior declines NOTHING — it has no material to find empty
    }

    p = os.path.join(HERE, "candidate_arm1.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(patch, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("ARM 1 · the template prior")
    print(f"  {len(PRIORS)} rows, 0 holds")
    print(f"  -> {os.path.basename(p)}")
    print()
    print("  NO SITE MATERIAL WAS READ. Every value is a declared generic default,")
    print("  and each row carries the prior that produced it in `$prior`.")
    print()
    print("  Note what this arm CANNOT do: it fills all twenty targets, including")
    print("  the one nothing supports, because a prior has no material to find")
    print("  empty. That is the trap, and it walks straight into it.")

    # Prove the claim rather than assert it: check the module's own AST for any
    # `open()` touching the corpus.
    #
    # An earlier version of this check matched the word "site" in its own prose
    # and reported a false positive ON ITSELF — a check that cries wolf is worse
    # than no check, because the next real alarm gets discounted.
    import ast
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    opens = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open"]
    reads_site = any("site" in ast.dump(n).lower() for n in opens)
    print(f"\n  opens {len(opens)} file(s); any under site/: "
          f"{'YES — THE ARM IS INVALID' if reads_site else 'no — the arm is clean'}")
    return 1 if reads_site else 0


if __name__ == "__main__":
    raise SystemExit(main())
