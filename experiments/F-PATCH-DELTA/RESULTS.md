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

## DEVIATION, recorded before the arm-② candidate landed

**The gate battery moved off `87c463d` while arm ② was being authored.** Fork C landed a real behavioural
fix to gate 13 (`2d1ed0f` — `conservative` was laundering sample sizes and years into duration anchors),
plus witness machinery and six further exposure fixtures.

`PREREGISTRATION.md` §6 lists *"the gate battery moves off `87c463d` mid-run"* as an invalidation condition.
**Recording the deviation now rather than deciding about it after seeing the result.**

### Why it does not invalidate the score

**The score does not come from the gates.** It comes from the §4 rubric against `DELTA.json`. Gate results
are reported *separately*, by design and by the pre-registration's own instruction. So a moving battery
cannot move the score.

### What it does affect, and how it is handled

Arm ② read the gates **at HEAD** while authoring — the screenshot of its own trace shows it going to
*"the two gates I'll be graded hardest by."* That is a deviation from *"the repository at `87c463d`"*.

**It is not contaminating:** Fork C's fix is a general correction about which numbers may anchor a
conservative rounding. It says nothing about Fairbank, its contradictions, or its unanswerable target.

**Handling:** a worktree at `87c463d` is checked out alongside, so **the candidate is gated BOTH ways** —
at the pin, for the pre-registered comparison, and at HEAD, to see what the strengthened battery says.

**And that pair is not damage control; it is the thing Fork C's plan predicted:**

> *The delta between the two runs is itself informative: the same harness graded by a weak battery and then a
> strong one tells you how much of the first verdict was the battery.*

**We now get that measurement on the first run instead of the second.**

---

## ARM ② · **RUN — `S = 0.57`, zero fabrications, SHAPED**

A session that did not build the corpus, given the repo and `site/`. **It declined to score itself**, on the
grounds that reading per-target output would be the delta reaching the harness *"in any form"* — and it
skipped `PREREGISTRATION.md` entirely rather than reading around §3. **It also disclosed a `grep` hit under
`internal/` that it did not open.**

That discipline is worth recording separately from the score: **§6 was honoured by the subject, unprompted.**

### The numbers

| | Arm ① floor | Arm ② | |
|---|---|---|---|
| **score** | 19 / 40 | **23 / 40** | |
| **S** | 0.47 | **0.57** | **+0.10** |
| **fabrications** | 1 | **0** | the trap declined, not filled |
| **gates** | **FAILED** — 3 gates | **PASS-UNVERIFIED** — the terminal honest state | |

**Verdict per §5: SHAPED.** Which is what the pre-registration called *the expected result, and the most
useful*.

### Gate result — reported separately, as §4 requires

**Ten of thirteen GREEN at both batteries.** Three PASS-UNVERIFIED: `shadow-run fidelity` (needs the site's
tape), `totality on provision` (needs a runtime), and `signature` — **11 rows unsigned, which is correct.**
*A machine leaves `author` empty; the signature is the output commit.*

**Identical at HEAD and at the pinned `87c463d`.** The §6 deviation is therefore **neutralised**: Fork C's
gate-13 fix did not change the verdict on this patch. **That is the delta measurement Fork C's plan predicted
would be informative, and here it reads zero.**

### What separates it from the floor

**The floor and the candidate diverge exactly where the site departs from the industry**, which is the
completability thesis stated as a measurement:

| Target | Arm ① (generic) | Arm ② (from material) |
|---|---|---|
| `evaluation.reference_lab` | 240 — the contract | **450 against a true 451** |
| `triage.callback_practice` | 30 — the SOP | **10 against a true 10** |
| `intake.after_hours_owner` | on-call supervisor | **house_coordinator** |
| `transport.perfusion` | **fabricated a provider** | **declined, with a hold** |

**All three planted contradictions resolved to the tape rather than the binder. The unanswerable target was
declined rather than filled.** Those four targets are a 7-point swing, and they are the entire difference
between the two arms.

**And its reading of `triage.callback_practice` is sharper than the answer key's.** The delta records that
practice beats the binder. The candidate observed that **the SOP's 30-minute threshold is not merely
generous — it is *vacuous*: the slowest of 128 observed callbacks was 28 minutes, so the rule can never
fire.** That is a better finding than the one the corpus was built to contain.

### Where it lost points, and none of it is fabrication

**Eleven rows, nine declines, 20 of 20 targets accounted for.** It filed a row only where the site's own
history could replay it — and the rubric scores a decline at +1 against +2 for a correct answer, so **a
cautious patch is capped below a complete one by construction.**

Three targets scored **0 — "wrong, no key matches"** — `intake.channel`, `recovery.or_availability`,
`authorization.approach_sequence`. Inspection shows these are **scorer artifacts, not errors**: the candidate
recorded per-hospital detail the answer key encodes differently, and the mechanical key-match cannot see
agreement across two shapes. **The scorer is crude here, and saying so is more useful than a number that
implies it is not.**

---

## THE CORPUS HAD TWO DEFECTS. THE CANDIDATE FOUND BOTH. I PUT THEM THERE.

Neither was planted. Both are confirmed to the exact count:

**1 · `after_hours` is an independent coin flip, not a clock derivation.** `build_site.py` sets it with
`rng.random() < 0.46` while `arrived_hour` is drawn separately — so **197 of 420 rows carry a flag that
contradicts SOP-03's 07:00–19:00 business hours.** The candidate reported *197 of 420*. Exact.

**Its handling was better than the defect deserved:** rather than picking a reading, it cited the site's own
flag **and corroborated with the hour-stamped tickets, which do not share the defect** — and said in the row
that the two cannot be reconciled.

**2 · `H-1490` volume contradicts itself.** The inventory calls it low-volume at *"four referrals last
year"*; the tape carries **71**. The candidate reported *71*. Exact. And it noted **the tape is undated, so
the material cannot say which is stale** — declining to adjudicate rather than guessing.

### What this does to the result

**It makes it stronger, not weaker.** A corpus with unintended inconsistencies is **more like a real site**,
not less — real material contradicts itself constantly, and `elicit/method.md` exists because of exactly
that. The candidate was handed two contradictions nobody designed and **surfaced both rather than smoothing
either.**

**But it is a defect in the instrument and it is recorded as one.** A future run on this corpus inherits both,
and any comparison must account for them. `build_site.py` is not being corrected: **changing the corpus after
a run would invalidate the comparison**, and §6's spirit covers it even though its letter does not.

---

## Two seed defects the candidate found, unprompted

Reported without being asked, and **not fixed locally** — correctly, since §2 says a change to `core/` or
`schema/` is an issue against the repository:

**1 · `derived_from` is documented by a gate and rejected by the schema.** `gates/divergence.py` names it as
the sanctioned way to justify a computed figure; `schema/patch.schema.json` sets `additionalProperties:
false` and does not declare it. **A row using the gate's own escape hatch is schema-invalid.** And nothing in
the tree validates against that schema — `northlake.patch.json` itself uses `$comment`/`$note`, which strict
validation would reject.

**2 · The schema admits no home for a declined target.** Which is why the holds ride in `$holds`.

**And my scorer inherited defect 2**: it looked for `holds` and found nothing, because the key name was never
specified anywhere. **Accepting both is not a rubric change** — §4 asks whether a decline was recorded *with
a reason*, and the key it rides under is an encoding detail. Recorded in `score.py` so the decision is
auditable.

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
