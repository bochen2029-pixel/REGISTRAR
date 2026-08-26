# ATTRIBUTION — what `S = 0.57` actually measured

**Run `2026-08-26` · executes `PLAN_attribution.md`, whose thresholds were fixed before any number
existed · `python experiments/F-BATTERY-STRENGTH/attribute.py <candidate> <result> …` · reads only.**

---

## The verdict, applied without adjustment

**M** = share of a candidate's *earned row-points* sitting on rows the battery can mechanically tie
to their evidence.

| | arm 1 · template prior | arm 2 · site corpus |
|---|---|---|
| `S` | 0.475 | **0.575** |
| **M** | **0.20** | **0.64** |
| earned · CHECKABLE | +4 | +9 |
| earned · BLIND | **+16** | +5 |
| earned · declines | 0 | +9 |

> ### PLAN §3 verdict at M = 0.64: **MIXED — the claim is partial and must say so.**

The mechanical-oracle property — one of the four that make it safe to hand this to a machine, and
**the only one that is not a theorem** — carries roughly two-thirds of the arm-2 result. The
remaining third rests on a human reading a rubric. That is not a failure. It is the first time the
property has had a denominator, and the honest form of the claim is now *partial*, not absolute.

## The finding that matters more, and it was pre-registered as the one to look for

PLAN §3 named an additional check in advance:

> *If arm 1 — the floor, which read no site material — draws a **higher** share of its score from
> BLIND rows than arm 2 does, that is evidence the blind class is where an ungrounded prior most
> easily hides.*

**It fired.**

| | share of earned points on rows the gates CANNOT evidence-check |
|---|---|
| arm 1 · read **no site material at all** | **80 %** (16 of 20) |
| arm 2 · read the site corpus | 36 % (5 of 14) |

**The template prior earned four fifths of its score on rows the battery cannot tie to any
evidence.** That is the archetypal ungrounded completion — confident, plausible, sourced from a prior
rather than from the site — and the blind class is exactly where it lives.

The gates did refuse arm 1 outright, on *evidence binding*, *shadow run*, *divergence* and *schema
conformance*. **The refusal held. But it did not come from the rows where the score was.** The
battery caught arm 1 for having no denominators and for weasel words — structural tells — not by
finding its assertions unsupported, because for 16 of its 20 rows it has no mechanism to do so.

> **A completion that supplied denominators and avoided weasel phrasing would have kept 80 % of that
> score with nothing behind it.** That is the shape of the confident, plausible, wrong patch
> `SPEC.md` §14 ranks as the central risk, and it enters through the class this audit names.

## And the reading of F-PATCH-DELTA changes

Arm 2 beat arm 1 by 4 points. The composition is not what "0.57 versus 0.47" suggests:

- **+9 came from declines** — nine targets arm 2 refused *with a hold*, at +1 each. Arm 1 filed none.
- **−11 on checkable rows** — arm 2 authored *fewer* well-evidenced numeric rows than the prior did.
- **+1** from arm 1's fabrication penalty, which arm 2 did not incur.

**Arm 2's advantage came primarily from knowing what it did not know.** That is a real and valuable
property — `AGENTS.md` §7b is built around it, and *a gap is visible where a confident wrong answer is
not* — but it is a different claim from *the site corpus let it author better values*, and the plate
currently reads as the latter.

## What this audit got wrong, corrected mid-run

**The first version of the instrument was contaminated and its first numbers were artifacts.**

Axis A originally asked *did any gate FAIL after destroying this row's evidence?* Arm 1 fails four
gates **before any mutation** — so every arm-1 mutant was trivially "killed" and arm 1's mechanised
share came out **1.00**, which is not merely wrong but wrong in the flattering direction: it would
have made the ungrounded prior look perfectly gate-covered.

Corrected to a **delta**: a row is CHECKABLE only when destroying its evidence introduces a failure
the baseline did not already carry. Under that test arm 1's M is **0.20**. *Found by running it
against a patch that already failed — not by reading the code.*

**One metric is retracted rather than reported.** `attribute.py` prints a "share of the delta the
gates could mechanically check" of −83 %. It is meaningless: arm 1 has zero declines and arm 2 has
nine, so the arms are not structurally comparable bucket-by-bucket and the denominator changes sign.
**The comparison that survives is M itself.** The line is left in the tool with this note rather than
quietly deleted.

## What follows

1. **`experiments/F-PATCH-DELTA/RESULTS.md` gains M = 0.64** beside `S = 0.575`. A score reported
   without the mechanised share of its own grading is a number without a denominator.
2. **The real-site pre-registration must name M and the blind class**, the way it already pins the
   gate battery by SHA. The instrument's coverage is now known; running without stating it wastes
   the protocol.
3. **The blind class outranks the 18 easy survivors.** `expiry` and `author` are one-line fixes.
   *An assertion the gates cannot tie to evidence is where 80 % of an ungrounded prior's score
   lived*, and that is a design decision — require a `derived_from` method for non-numeric values,
   require the evidence quote to contain the value's own token, or move the class to the undecidable
   three so it is at least **visible**. It is currently invisible, which is the worst of the three.
4. **Re-run after any `gates/` change.** M is a regression instrument on coverage, as the mutation
   score is on strength.

---

*No PHI. The answer key never entered a git worktree — arm 2's per-target scores were read from the
vault's existing `RESULT_2-site-corpus.json` via a scratch copy outside every tree, and nothing in
`C:\REGISTRAR` or any other worktree was written by this audit.*
