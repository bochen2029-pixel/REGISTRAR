# F-RESIDENT-VS-FLOOR · pre-registration, v1

**`2026-08-27` · FROZEN BEFORE ANY JUDGE EXISTS.** No trained component has been built, no training data
prepared, no moment corpus generated. This document fixes the question, the arms, the metric, the
thresholds, and the invalidation conditions first — the same discipline as F-PATCH-DELTA, applied to the
experiment that decides whether the resident is real or theatre. **Where this document and a dated receipt
disagree, the receipt wins. Changing this file after any arm has run voids the run, not the file.**

---

## §1 · The question

`SPEC.md` §2b claims the dial cannot be set: surface-or-hold under a rate constraint makes a runtime
threshold a Lagrange multiplier, a scalar multiplier can only express a state-constant utility, and the
utility of speaking is violently state-dependent. The measured basis is `[M inherited]` — another domain's
streams. **This experiment converts the claim to in-domain `[M]` or prints its funeral:**

> **At a matched interruption budget, does a trained judge catch more of what matters on replayed donor
> cases than the deterministic floor does?**

## §2 · The arms

| Arm | What it is | Role |
|---|---|---|
| **A0 · the cron** | a fixed-cadence sweep (every N minutes, surface the top breach if any) | the outer null — *"if a resident does not beat a weekly cron on the site's own ledger, the resident is theatre"* (ROADMAP §8) |
| **A1 · the floor** | `floor/closure.py` + the budget-projection judge exactly as `demo/replay.py` runs it — deterministic, fixed WARN threshold | **the null that must be beaten** |
| **A2 · the resident** | a trained judge (small open-weight model, ≤16 GB card, local only) deciding surface-or-hold at each boundary over the same percept stream | the `[BET]` |

All three arms see **identical percept streams** — same cases, same boundaries, same budgets. No arm sees
the moment answer key.

## §3 · The corpus — replayed cases with planted moments

A moment-corpus builder (vault, `internal/f-resident/`, same discipline as the falsifier's) generates
replayed cases from `site_v4`-style tape with **planted moments** — instants that objectively deserved a
surfacing. Moment classes, fixed now:

1. **transitive-margin collapse** — no single timer breached; the chain implies the window is nearly gone
2. **silent stall** — no event for longer than the lapse threshold while the case is live
3. **contract breach** — a stage exceeds a hard documentary bound
4. **wrong-owner routing** — an event whose actor contradicts the mounted fit
5. **recovered margin** — a stage beats its budget materially (the *relief* class: the correct action is a
   downgrade/stand-down surfacing, which an alarm system cannot express)
6. **decoy** — a loud-looking event that deserves NOTHING (tests restraint; surfacing it costs budget)

Counts fixed before generation: **≥ 40 cases, ≥ 60 planted moments, ≥ 25 decoys**, class mix recorded in
the vault at build time. The builder asserts its own invariants (funnel reconciliation, clock-derived
flags) exactly as `build_site_v4.py` does. **Train/eval split by case id, frozen in the vault before any
training run; the eval half is never trained on, and the builder's seed is committed to the vault at
generation time.**

## §4 · The metric — catches at a matched interruption budget

- **Budget `B`**: interruptions per case. **Measured from arm A1 first** — the floor's natural operating
  point on the eval set defines `B`. A0 and A2 are then evaluated **at that same B** (their emission rule
  may rank candidate surfacings; only the top-B per case count).
- **A catch**: a surfacing within **30 minutes** of moment onset that **names the governing event or
  chain** (mechanically checked: the surfacing's cited event/constraint set intersects the planted
  moment's key set). Naming the wrong basis is not a catch.
- **A fabrication**: a surfacing citing an event, figure, or constraint that does not exist on the
  stream. **Zero tolerance — one fabrication fails the arm outright**, same asymmetry as the falsifier.
- Score per arm: **recall at budget B** on planted moments (primary) · decoy-surfacing rate (secondary,
  lower is better) · relief-class recall reported separately (it is the class alarms structurally miss).

## §5 · Thresholds — fixed now

- **A2 BEATS THE FLOOR** iff, on the frozen eval half: recall@B exceeds A1's by **≥ 0.15 absolute**, with
  **zero fabrications**, decoy rate no worse than A1 + 0.05, and the result holds across **two independent
  training seeds** (both must clear; one clearing is noise).
- **A1 must beat A0** by ≥ 0.15 recall@B or the floor itself is theatre against a cron and the entire
  §2b argument needs re-examination — publish that loudly if it happens.
- Anything else: **FAILS — the funeral prints**, per the standing kill condition: *if the deterministic
  closure catches nearly everything a trained disposition would, the disposition is theatre* (SPEC §2b,
  §6). The honest product is then the floor, shipped as the resident's final form.

## §6 · Invalidation — any of these voids the run

1. The judge trained on any eval-half case, or on the moment answer key in any form.
2. Budget B, the 30-minute window, class mix, or thresholds adjusted after any arm has run.
3. The moment corpus edited after the first arm runs (defects found are recorded, not fixed — the
   falsifier's rule).
4. An arm's emission rule tuned against eval-set results ("just one more retrain and re-eval" is the
   canonical leak — the two pre-registered seeds are the whole retrain allowance).
5. The percept streams differing between arms in any way beyond the judge itself.

## §7 · Pre-committed publication

Whichever outcome, published with: per-arm per-class recall tables, the budget B and how A1 set it, both
seeds' results, every fabrication verbatim if any exist, and the moment-corpus summary. A2 losing is a
*successful experiment* — it retires the resident honestly and promotes the floor, and the page's plate
changes first.

## §8 · Roles and the ledger

The corpus builder is disqualified from training or operating A2 on that corpus. The scorer is mechanical
(vault, alongside the key). Sessions that have read this §3–§5 may build arms but not author moment
placements. **This file is public by design; the answer key, the builder, and the split are vault-only.**

*Frozen 2026-08-27, before any judge, any corpus, any training run. The ladder decides what happens next.*
