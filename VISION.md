# What this is, and why it is shaped this way

**Tracked on purpose.** The canonical statement of this architecture lived only in `internal/`, which is
gitignored — so **a clone received the machinery and not the reasoning.** Anyone can then maintain the code
correctly while the thing it is *for* drifts, and that has already happened once.

For the full argument with its receipts: `SPEC.md` §2b, `ROADMAP.md`, and — on this machine only —
`internal/FUSOR_AT_THE_CENTER_v1.0_REFOUNDING.md`.

---

## It is a resident, not a form

**An electronic donor record is a case under a clock, and almost everything that goes wrong goes wrong in the
interval between two events — when no single field is wrong.**

So the object is a **loop**: the world enters continuously, the system judges at each boundary whether this
instant deserves a coordinator's attention, and **what it decides — including every decision to stay silent —
goes on an append-only tape.**

**This is not aspiration. `floor/closure.py` already does it**, with a deterministic judge: it perceives a
case, computes a deadline no human computed, and **surfaces it unprompted** — *"the serology had to be drawn
at 22:15; it is 23:40."* No timer fired. Nobody asked.

> **That is an emit decision. The record was always a resident; the floor is its simplest possible mind.**

Everything above that is the same loop with a trained judge instead of a fixed one — which is why **the floor
is the null a resident must beat, not the thing it replaces.**

---

## The fence is on ACTION, never on perception

Read the seven prohibitions in `SPEC.md` §8 and notice what is **not** among them: *perceive, notice,
compute, surface.*

**They are a list of acts** — determine, allocate, contact, sign, send, delete, rank. Perception cannot be on
that list, because **perceiving a case and surfacing what it finds is the product.**

**This distinction took four attempts to state correctly**, and each failed attempt fenced perception and
then retreated one radius. It is recorded because the error is easy and recurring: *a proposal that limits
what the system may NOTICE is repeating it.*

**And the fence cuts opposite to intuition.** A resident is **more** compliant with the clinical-decision-
support carve-out than a threshold alarm, because the carve-out turns on **presenting the basis** so a
professional can independently review. An alarm presents a number. **The closure presents the argmin path** —
the chain of constraints that produced the deadline, recovered from the same computation.

---

## Three radii, one shape

| radius | what enters | the judgment | the seam |
|---|---|---|---|
| **the case** | labs, transitions, timers, elapsed time | does this instant deserve attention? | the board — **nothing acts** |
| **the fit** | SOPs, tickets, gate refusals, drift | is there enough here to propose a row? | the gates, **and a signature** |
| **the seed** | findings across fifty-five sites | should the seed declare this variation point? | upstream, **human-authored** |

**A completing harness is radius 2 of the loop it is reading about** — `AGENTS.md` §7c — and three
consequences follow that are not obvious from outside:

- **Silence is world at radius 2 as well.** An unanswerable target is a *finding*, not an absence, by the
  same law that makes elapsed time a percept at radius 1. The `accountability` gate refuses a patch silent on
  any declared target.
- **Its output is a proposal, never a mount.** The seam is the gate battery **plus a human signature**,
  exactly as the seam below the case is a coordinator.
- **An undeclared variation point goes UP, not sideways.** It is a proposal to the seed, for all fifty-five —
  never a patch row. **The blast-radius gate refuses it otherwise**, because the seed's fixed variation list
  is what bounds what any agent can reach. *That bound is what makes T4 hold.*

---

## The argument this buys

**Alert fatigue is the most documented failure in clinical software, and it is not a tuning problem.**

Maximising over surface-or-hold under a rate constraint makes a runtime threshold **exactly the Lagrange
multiplier** on that constraint — and a scalar multiplier can only express a utility that is *constant in
state*, while the utility of speaking is violently state-dependent. **The same unfilled field deserves
nothing at hour two of a workup and a page at hour nine when the OR window is closing.**

No threshold is right in both cases, which is why every records system's alert configuration is a permanent
unwinnable tuning project and why coordinators mute things.

Measured `[M inherited — another domain's streams; the transfer to this one is a bet]`: the best fixed
threshold caught **36 of 39** and was **deaf exactly where it mattered**; zero bias fired **921 times per
hour**; dedup ratio **1.07**, so the flood is *breadth* — roughly 59 distinct, individually defensible
conditions per hour. **You cannot dedupe, cool, or filter your way out of breadth.** Absorbed into weights
rather than wrapped around: **63.4% → 6.7%** per decision boundary, catches kept.

---

## What is deliberately not built

**`core/resident/` does not exist.** It is `[SPEC]`, gated in `ROADMAP.md` §8, and **unblocked now that the
completion falsifier has returned** — but every receipt behind it was measured on development streams, not
donor cases, and **that transfer is a bet in every case.**

The floor is the null it must beat. **If the deterministic closure catches nearly everything a trained
disposition would, the resident is theatre and the funeral prints.**

---

*Nothing here has run inside an OPO. No patient data has touched any part of it. The completion falsifier has
run against a **synthetic** site — which bounds the kit from above and says nothing about whether a real one
is legible.*
