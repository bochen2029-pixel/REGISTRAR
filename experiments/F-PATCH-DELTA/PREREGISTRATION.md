# F-PATCH-DELTA · pre-registration

**Written `2026-08-26`. Nothing has been run. This document exists to fix the instrument before the result.**

**Gate battery pinned at `87c463d`** — thirteen gates. Fork C is strengthening them concurrently; **this run
is graded by the battery at that SHA and no other.** Its improvements apply to the next run, and the delta
between runs is itself informative.

---

## §0 · THE FINDING THAT CAME FIRST, AND IT CHANGES THE EXPERIMENT

The design says: *give a harness only **public** material for a second OPO, have it author a candidate patch,
grade against a known delta.*

**Before writing a rubric I checked whether that is possible. It is not, and the margin is not close.**

### Every evidence item in the worked example is internal

`examples/worked/northlake.patch.json`, thirteen evidence items across nine rows:

| kind | n | public? |
|---|---|---|
| `tape` — the site's own case history | **7** | never |
| `document` — SOPs, a reference-lab contract | 4 | no |
| `ticket` — service-desk history | 1 | no |
| `observation` — OR scheduling correspondence | 1 | no |

**13 of 13 internal. Zero public.**

### And the question set says the same thing, harder

All twenty questions in `elicit/questions.yml`, checked against the sources each one names:

> **Zero of twenty name a source that is plausibly public.**

They name: the case tape (×11) · SOPs · the call rotation · service-desk history · written hospital
agreements · reference-lab and transport contracts · PACS configuration · the integration inventory ·
medical director standing orders.

**Not one of those is publishable, and that is not an accident of drafting. It is the thesis.** `elicit/`
exists because *the binder describes work as imagined and the organisation runs on work as done* — and
work-as-done is legible only from inside. **An OPO's public surface describes what it is, not how it runs.**

### What this means

**The experiment as specified would measure the material, not the harness**, and a negative result would be
uninformative — indistinguishable from *"there was nothing to work from."* Running it that way would produce
a number with no meaning and, worse, a *publishable-looking* number.

**So arm ② is re-specified below.** This is a correction to the experiment, made before it ran, recorded
here rather than discovered in the write-up.

---

## §1 · The question

> **Given the seed and a body of site material, can a competent outside harness author a candidate fit that
> passes the gates and materially matches what that site actually does — without being told what the answers
> are?**

Falsifiable. Pre-registered. **Publishable in every outcome.**

---

## §2 · The arms

| Arm | Material | Establishes |
|---|---|---|
| **① template-prior** | the seed only — **no site material at all.** Fill the schema with plausible generic OPO defaults. | **THE FLOOR.** Without it, a passing ② might only mean *the schema is fillable by anyone.* |
| **② synthetic site** | the seed **+ a constructed corpus** for a fictional OPO with a **known** delta | the claim under test |
| **③ resident** | continuous access to the same corpus | **later** — and ② is its null |

### Why ② is a synthetic site, and what that costs

Three options existed once §0 ruled out public material:

1. **Narrow the claim to what public material supports** — which §0 shows is *nothing*. Not viable.
2. **A synthetic site with a known delta.** Fully gradeable, fully fair, **and it tests the schema, the kit
   and the gates rather than the world.**
3. **Grade against STA**, where ground truth exists — **REFUSED.** `PROVENANCE.md` §4 makes recollection of a
   former employer's design inadmissible, *including recollection expressed as "the obvious way to model
   this."* The ground truth would be exactly that recollection. **Using it would contaminate the one
   experiment whose value depends on being clean.**

**Option 2 is chosen, and its limitation is stated up front rather than buried:**

> **This tests whether the KIT is completable, not whether a REAL OPO is legible.** A synthetic corpus is
> written by someone who knows what the answers are, and no amount of care fully removes that. **The result
> bounds the kit from above: if a harness cannot complete a corpus built to be completable, it certainly
> cannot complete a real one.** A pass is necessary and not sufficient; **a failure is decisive.**

**The real-site version is R6, with a real OPO, and this does not substitute for it.**

---

## §3 · The corpus, and the discipline it is built under

`experiments/F-PATCH-DELTA/site/` — a fictional OPO, **not Northlake** (that one is the worked example and
the harness would be completing an answer it can read).

**Construction rules, and these are what keep the test honest:**

- **Written before the rubric, and the delta extracted from it afterwards** — not the reverse. A corpus
  built to satisfy a rubric is an answer key with extra steps.
- **The answer is never stated.** No document says *"our callback threshold is 12 minutes."* It is
  **derivable** from a tape extract and nowhere asserted — which is the actual elicitation problem.
- **Include the disagreements.** At least one target where **the SOP and the tape contradict each other**,
  because that is the single most common real finding and a corpus without it is easy in the way that
  matters. *The binder and the behaviour disagree more often at `intake.after_hours_owner` than anywhere
  else.*
- **Include a target with no answer at all.** A correct harness should decline it and say why. **A harness
  that invents a value here has failed in the most important way**, and a corpus where every question has an
  answer cannot detect that.
- **Zero PHI, synthetic throughout**, and every fixture declares it — the existing hygiene check applies.

---

## §4 · The rubric — fixed now, in advance

Each of the 20 declared targets is scored **independently**:

| Score | Meaning |
|---|---|
| **2 · correct** | value materially matches the delta; evidence points at the material that supports it |
| **1 · shaped** | right target, right *kind* of answer, wrong number or wrong grain |
| **0 · absent** | no row, and **no hold recorded** |
| **0 · wrong** | a value the material contradicts |
| **−1 · fabricated** | a confident value with **no support in the material at all** |
| **+1 · correct decline** | no row, **with a hold naming why** — on the target that has no answer, this is the *correct* response |

**`−1` is deliberately asymmetric.** A fabricated row is worse than a missing one: a gap is visible and a
confident wrong answer is not. *A confident regulatory value without a source is a fabrication with good
grammar*, and the same is true of an operational one.

**Gate results are recorded separately from scores.** A patch that scores well and fails the gates is a
different finding from one that passes the gates and scores badly, and collapsing them would hide which.

---

## §5 · Thresholds — committed before the run

Let **S** = total score ÷ maximum possible.

| Outcome | Condition | What it means |
|---|---|---|
| **COVERS** | S ≥ 0.70, **zero fabrications**, gates pass | the first receipt |
| **SHAPED** | S ≥ 0.40, ≤ 1 fabrication | **the expected result** — and the most useful: it says how much observation the fit requires |
| **FAILS** | S < 0.40, **or ≥ 2 fabrications**, or gates fail on a patch the harness declared finished | **the funeral prints** |

**And arm ① is the floor every one of those is read against.** If ① scores near ②, the schema is doing the
work and the harness is not — **which is a FAILS regardless of ②'s absolute score.** That comparison is the
reason arm ① exists and it must be reported first.

---

## §6 · What invalidates the run

Declared now so it cannot be decided afterwards:

- **the rubric is adjusted after seeing output** — the run is discarded and re-registered, no exceptions
- **the corpus is edited after the harness sees it**
- **the harness is given the delta**, in any form, including by a leading prompt
- **the gate battery moves** off `87c463d` mid-run
- **any real OPO material enters the corpus**

---

## §7 · Pre-committed publication

**Whichever outcome lands is published, including FAILS**, with the candidate patches, the grades, the gate
output, and everything the harness got wrong.

**A falsifier published only when it passes is not a falsifier.** And on FAILS the honest product is named
in advance: *an excellent open-source spine plus a human implementation guide — still more than exists
today.*

---

## §8 · What this does not test

- **Whether a real OPO is legible.** §2. The synthetic corpus bounds the kit from above and nothing more.
- **Whether a resident beats a prompted harness.** Arm ③, and this run is its null.
- **Whether the gates are strong.** Fork C. **A pass here graded by a weak battery is a weak pass**, and the
  pin at `87c463d` is what makes that statement checkable later.
- **Anything clinical.** No patient data, no OPO, no case.

---

*Pre-registered 2026-08-26 before any corpus was written or any harness invoked. Where this document and a
dated receipt disagree, the receipt wins.*
