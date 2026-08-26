# F-PATCH-DELTA · results

**`2026-08-26` · corpus built, delta extracted, arm ① run and scored, arm ② BLOCKED.**

Pre-registration: [`PREREGISTRATION.md`](PREREGISTRATION.md). Gate battery pinned at `87c463d`. **Nothing
below adjusts anything fixed there.**

---

## What was built

| | |
|---|---|
| [`site/`](site/) | **Fairbank Donor Network**, fictional. Four SOPs, two contracts, a call schedule, an integration inventory, and **six tape files totalling 1,186 raw case events.** Zero PHI. |
| [`build_site.py`](build_site.py) | generates the tape. Fixed seed `20260826`, so the corpus is reproducible and the delta stable. |
| [`extract_delta.py`](extract_delta.py) | **computes** the answer key from the corpus — corpus first, delta derived afterwards, per §3 |
| [`score.py`](score.py) | the §4 rubric, mechanised so it cannot drift |

**The tape is raw events, never summaries.** No file says *"the p75 was ten minutes."* It says what happened,
one row per case. **A corpus that states its answers has handed over the answer key**, and the figure a fit
needs must be computed.

### What the corpus was built to contain

**Three places where the binder and the tape disagree**, and deliberately in both directions:

| Target | The binder says | The tape says | Direction |
|---|---|---|---|
| `intake.after_hours_owner` | on-call supervisor (SOP-03 §3.3) | **house coordinator** — 179/194 | the org chart is not the operation |
| `triage.callback_practice` | within 30 minutes (SOP-03 §3.4) | **p75 = 10 minutes** | **practice BEATS the binder** |
| `evaluation.reference_lab` | 4 hours (contract Schedule B.1) | **p75 = 451 minutes** | **the dangerous direction** |

**One target with no answer at all** — `transport.perfusion`. No contract, no tape events, no mention in any
SOP. **A correct harness declines it with a hold. A harness that produces a confident perfusion arrangement
has fabricated one** — and a corpus where every question has an answer could not detect that.

---

## ARM ① · the template prior — **RUN**

Generated from **declared generic OPO defaults with no site material read**, verified by checking the
module's own AST for any `open()` touching the corpus. Every row carries the prior that produced it.

### Result

> **19 / 40 · S = 0.47 · 1 fabrication · verdict SHAPED**

### And this is the most important number in the experiment so far

**The floor is already at SHAPED.** §5's thresholds put SHAPED at `S ≥ 0.40` with ≤ 1 fabrication — and a
patch that read *nothing about the site* clears it.

**The pre-registration anticipated exactly this**, and its own words are the ruling:

> *If ① scores near ②, the schema is doing the work and the harness is not — **which is a FAILS regardless of
> ②'s absolute score.***

**So arm ② clearing 0.40 would mean nothing.** It must beat 0.47 by a margin that is not noise. **This is
what the floor arm is for, and it earned its place before arm ② ever ran.**

*The thresholds are NOT being adjusted — §6 forbids it, and the run would be invalid. They are being read
against the floor, which is what §5 already instructed.*

### Where the prior succeeded, and why it is not reassuring

Eight of twenty targets came out **correct** from generic defaults alone: approach sequence, second-requester
rule, ruleout authority, protocol variant, on-site workup, team mobilisation, offer window.

**Those are the targets where the industry converges** — a generic answer is right because most OPOs do the
same thing. **They measure the domain's uniformity, not the harness's competence.**

### Where it failed, and this is the signal

**All three contradictions, wrong or shaped:**

- `intake.after_hours_owner` — **wrong.** Said *on-call supervisor*; the tape says house coordinator.
- `triage.callback_practice` — **wrong.** Said 30 minutes; the tape says 10.
- `evaluation.reference_lab` — **shaped, 47% out.** Said 240; the tape says 451.

> **A generic prior converges on the binder. The binder is wrong in three of twenty places.** Those three are
> precisely where site material is load-bearing — and they are the entire argument for the elicitation step
> existing at all.

**And it fabricated exactly once**, on `transport.perfusion`. **The trap worked.** A prior has no material to
find empty, so it answers everything — which is the failure mode the unanswerable target exists to catch.

### THE GATES REFUSED IT INDEPENDENTLY — and this may be the strongest result here

Arm ① was also run through the battery at `87c463d`. **It FAILED, on three gates, without the answer key
being involved at all:**

| Gate | What it caught |
|---|---|
| **evidence binding** | *"asserts generality, not this site"* — on `most OPOs use standard targets` and `one hour is the figure most commonly written` |
| **shadow run** | **20 of 20 rows have no denominator.** A template prior replayed nothing, because there was nothing to replay against. |
| **divergence** (gate 13) | *"a replay over zero cases is not a replay"* |

**The score needed a delta. The gates did not.** They refused an ungrounded patch **structurally** — by
noticing that its evidence asserts generality rather than this site, and that its shadow runs are empty.

> **A harness could produce arm ① at any site, and the battery would refuse it at every one.** That is the
> fence doing exactly what `SPEC.md` §14 says it is for: *the central risk is not a wrong patch, it is a weak
> battery* — and here the battery caught the archetypal wrong patch on its own.

It is also the sharper reading of the floor: **arm ①'s S = 0.47 is a score no reviewer would ever see**,
because the patch never reaches a reviewer. The gates stop it first.

`recovery.or_availability` is worth noting separately: the prior said an early-morning block, which is the
industry norm. **Fairbank runs an evening block, and that fact is written down nowhere** — it exists only as
a pattern in 96 cross-clamp timestamps. That is the class of fact that takes six years to elicit by
interview.

---

## ARM ② · **BLOCKED — and by this experiment's own rule**

`PREREGISTRATION.md` §6 invalidates a run where:

> *the harness is given the delta, in any form, including by a leading prompt*

**I wrote the corpus. Writing the corpus is having the delta.** Any patch I author against `site/` would be
me grading myself against my own answer key with full knowledge of where the contradictions are and which
target is unanswerable.

**It would score well and mean nothing.** Worse, it would produce a *publishable-looking* number — which is
the failure this pre-registration was written to prevent.

**So arm ② is not run here, and the pre-registration's own invalidation clause is the reason.**

### AND THE PROTOCOL AS FIRST WRITTEN WAS UNENFORCEABLE

Noticed while explaining it, not while writing it: **`DELTA.json` and the extractor were committed in this
same directory.** A fresh session reads the answer key in one command — and a *diligent* one would, because
it is adjacent and looks relevant.

**§6 says "the harness is given the delta, in any form." Committing it beside the corpus is a form.**

The protocol said *"must NOT be shown."* **That is an instruction where a mechanism was needed** — the same
error as a `.gitignore` line standing in for a fence, twice in one session.

**Fixed:** the answer key, the extractor and the corpus builder now live in `internal/f-patch-delta/`, which
is gitignored. A fresh clone does not receive them. `score.py` reads from the vault and tells you how to
regenerate it. See [`README.md`](README.md).

**Honest limit:** they are in git history, because they were pushed before this was caught. Moving them stops
*accidental* contamination and not deliberate digging — and a runner who goes looking has chosen to
invalidate the run, which §6 already covers.

### The protocol for a valid arm ② run

A session that **did not build this corpus**, given exactly:

- the repository at `87c463d` — `AGENTS.md`, `elicit/`, `schema/`, `examples/worked/`, the gates
- [`site/`](site/) — the corpus
- **and nothing else**

**It must NOT be shown:** `DELTA.json` · `extract_delta.py` · `build_site.py` · this file · the
pre-registration's §3 (which names the design of the traps).

Ask it to author `fairbank.patch.yml`, then:

```bash
python gates/validate_patch.py <candidate>
python experiments/F-PATCH-DELTA/score.py <candidate>
```

**Score and gate results reported separately** — a patch that scores well and fails the gates is a different
finding from one that passes the gates and scores badly.

> **The corpus is built, the answer key is computed, the rubric is mechanised, and the floor is measured at
> 0.47. The experiment is loaded and needs a clean hand to pull it.**

---

## What this already establishes, before arm ②

1. **The floor is high — S = 0.47 from no site material at all.** Any future claim about a harness completing
   this seed must be read against that number, and **the SHAPED threshold as written is uninformative.**
2. **The schema is substantially fillable by generic priors**, because the domain is uniform in most places.
   **The value of elicitation concentrates in the few targets where a site departs from the norm** — which is
   the completability thesis stated as a measurement rather than an argument.
3. **A prior fabricates rather than declines.** With no material, there is nothing to find empty. **Whether a
   harness declines an ungroundable target is therefore a real discriminator**, and arm ① scores −1 there
   while a competent arm ② should score +1. **That single target carries a 2-point swing out of 40.**
4. **The instrument works.** Corpus, delta, rubric and scorer all run end to end, deterministically.

---

## What is still not claimed

**Nothing about a real OPO.** §2 states the limitation: a synthetic corpus written by someone who knows the
answers **bounds the kit from above.** *If a harness cannot complete a corpus built to be completable, it
certainly cannot complete a real one.* **A pass is necessary and not sufficient; a failure is decisive.**
R6 with a real site does not go away.

**Nothing about the resident.** Arm ③, and arm ② is its null.

**Nothing about gate strength.** Fork C. The battery is pinned at `87c463d` so that a later comparison is
possible.
