# The drafts that were refused

**This is the most useful file in the repository, and it is the one most projects would delete.**

A worked example that only shows the finished artifact teaches a model to produce something that *looks*
like the finished artifact. What actually transfers is the shape of the refusals — what was wrong, what the
gate said about it, and why the fix is not "phrase it better."

Everything here is fictional. The gate output is real: run it yourself.

```bash
python gates/validate_patch.py examples/worked/rejected/01-off-surface.json
```

---

## 01 · Restating policy, and inventing a target

The likeliest first mistake. Both rows are well-formed, both are *true statements about organ procurement*,
and neither belongs in a patch file.

```
FAILED   blast radius ... 2 row(s) name a target the seed does not declare:
                          allocation.match_run_sequence, authorization.consent_required
```

**Why it is wrong.** `allocation.match_run_sequence` paraphrases OPTN policy. `authorization.consent_required`
restates a federal requirement. Both are already in the seed, and both are identical at every OPO — which is
the definition of L0. A patch row that duplicates the mandated layer creates a **second, divergent copy of the
law**, one that can drift out of date locally while the real one moves.

**The test that catches it before the gate does:** *would this row be true at all fifty-five organisations?*
If yes, it is not L2. It is not a fit; it is a fact, and the fact already shipped.

**Why the gate can be this blunt.** The seed declares its own mutable surface — 19 `local_variation` entries
in `core/lifecycle/lifecycle.yml`, lifted into `targets.json`. A target that is not in that list **does not
exist**. There is no argument to have and no configuration to widen.

---

## 02 · Grounded in nothing

The dangerous one, because it is fluent. Nothing here is malformed. A reviewer skimming would pass it.

```
FAILED   evidence binding ... evaluation.reference_lab: asserts generality, not this site
                              ('serology turnaround is typically around …');
                              allocation.offer_window_practice: no evidence
FAILED   shadow run ........ evaluation.reference_lab: shadow run has no denominator;
                              allocation.offer_window_practice: shadow run has no denominator
```

**Why it is wrong.** "Typically around 4 hours at most reference labs" is a prior, not a finding. It may even
be accurate on average — and it is still worthless, because **this fit is not about labs in general, it is
about the one laboratory this organisation actually sends specimens to.** In the accepted patch, that lab's
observed p75 is *six* hours, and the contract that says four is cited only so the gap is visible.

A fit built on the plausible number would compute every deadline two hours optimistic — **wrong in the
direction that loses organs.**

The second row is worse in a quieter way: `{"cases": 0}` and a bare `would_have_matched: 12`. A count with no
denominator is not a count, and a replay over zero cases is not a replay.

**What the harness should have done:** stopped. `AGENTS.md` §8 lists exactly this as a STOP condition —
the evidence is absent and the only way forward is to assume. Surfacing that is the job; filling the field
with something reasonable is the failure.

---

## 03 · No way back

```
FAILED   schema shape ..... row 0 (lapse.threshold) missing inverse
FAILED   inverse declared . lapse.threshold
FAILED   expiry ........... lapse.threshold: expiry 'when reviewed' is not a date
```

**Why it is wrong.** This row changes a value that already had one — the threshold was 240 — and does not say
how to get back to it. That is not an incomplete row. **It is not a row at all**: a patch row is a
`(change, inverse)` pair, and without the inverse it is not an element of the monoid, so `mount` is undefined
on it. See `SPEC.md` §3.

The consequence is concrete: retire this row later and the target is left *undefined* rather than restored to
240. The system does not return to the seed, and the containment result — every reachable state retires to
`λ₀` — no longer holds.

`"when reviewed"` fails for a related reason. **Nothing is permanent by default.** An expiry that is a
sentiment cannot demote a row that has drifted, so the row would sit there being quietly wrong forever.

**What the accepted version does:** `nl-008` supersedes the earlier draft and carries `inverse: {"minutes_without_progression": 240}` —
the previous value, so retirement restores it. A correction is a new row that supersedes. Never an edit.

---

## 04 · The silent one

The row a reviewer will not catch, which is why there is a gate for it.

```
FAILED   totality on provision ... row(s) declare a partial application: recovery.or_availability
```

**Why it is wrong.** The target requires a window — an open *and* a close. This row installs the open,
returns successfully, and stops. Nothing errors. Nothing looks wrong. The patch mounts.

And then **independent completions stop converging**, because the confluence result assumes every component is
*total on its provision*: an application that finishes has installed every key it declares. A row that
half-applies breaks that assumption with **no error, no symptom, and no failing test** — until something
downstream reads a key nobody wrote, at three in the morning, in a case that is already running.

**This is why it is a gate rather than a matter of authorial care.** It is the one failure mode where being
careful is not a defence, because there is nothing to notice.

If a row cannot be made total, **split it into rows that are.**

---

## What the accepted patch scores

```
python gates/validate_patch.py examples/worked/northlake.patch.json
```

Every decidable gate is `GREEN`. Two report **`PASS-UNVERIFIED`** — shadow-run fidelity and totality on
provision — because they cannot be *confirmed* from a file. They need the site's own tape to show a replay
actually happened, and a runtime to show that applying a row installs every key it declares.

*(Local invertibility was the third until `core/algebra.py` landed. It had reported PASS-UNVERIFIED on the
reasoning that T3 "needs a runtime" — half true, and unquestioned for weeks. T3's hypothesis is **pointwise**,
and the patch file plus the seed determine that state exactly. It was computable all along.)*

**The validator therefore exits non-zero on a patch with nothing wrong with it**, and says so:

> PASS-UNVERIFIED — nothing failed, but checks did not run. This is NOT a pass.

That is deliberate, and it is the lesson the whole battery exists to teach. `GREEN`, `PASS-UNVERIFIED` and
`FAILED` are three different states. **A checker that reported GREEN for a check it never ran would be
committing the exact error the three-state gate exists to prevent** — so this one refuses to, about itself.


---

# The witness audit

**`2026-08-26`.** `SPEC.md` §14 ranks the risks and puts one first:

> **The central risk is not a wrong patch. It is a weak battery.** A foreign harness produces confident,
> plausible, wrong work all day, and the gates are the only thing between that and an organisation where
> wrong loses an organ.

That risk was **unmeasured**, and worse than unmeasured: the four fixtures that existed were written by the
same author as the gates they test. A battery validated only against adversaries its own author imagined has
exactly its author's blind spots.

So the battery was audited against itself. `python gates/witness.py` reports the result, and conformance
carries it, because **coverage is a number this repository must print rather than a property it may assume.**

## What a witness is, and why the definition is strict

> **A witness is a fixture that fires exactly one gate.**

Not fussiness. A fixture that trips three gates proves that *something* refused the patch — **not which**.
And if one of those three silently stopped working, the fixture would still fail, still be green, and still
tell you nothing.

By that definition the starting position was **one** cleanly witnessed gate out of thirteen. Every other
fixture fired two to four gates at once, mostly because all four were unsigned and `signature` rode along
with everything.

**Now: seven cleanly witnessed, three entangled by construction, one uncaught and retained.**

## Three gates cannot be isolated, and that is structural

Recording this is the finding, not an excuse. **A fixture author who does not know will chase an impossible
fixture; a reader who does not know will read "incidental" as sloppiness.**

**`target syntax`** — a syntactically malformed target is *by definition* not a declared target, so
`blast radius` always fires alongside it. It cannot be isolated, ever. **Its value is teaching, not
catching:** *"your target has capital letters"* is actionable where *"that target does not exist"* is not.

**`inverse declared`** — it fires only when the `inverse` KEY is absent, and an absent required field always
trips `schema shape` first. Same entanglement, same conclusion.

**`L0/L1/L4 immutability`** — **unreachable from any patch file.** It fires only when a target is *declared*
**and** its layer is not L2/L3 — but every entry in `targets.json` is lifted from a `local_variation`, and
all twenty are L2/L3. A row naming an undeclared target is caught by blast radius first; a row naming a
declared one is L2/L3 by construction.

> **It is a seed invariant living in a patch validator.** It would fire only if the *seed* declared an
> L0/L1/L4 variation point — which is a defect in `lifecycle.yml`, not in anyone's patch. It is witnessed
> with a synthetic target table in `test_witness.py`, and it should probably move to conformance, where seed
> invariants live.

## `signature` refuses in the middle state, and that is correct

It never returns `FAILED`, and it must not. `AGENTS.md` has **a machine leave `author` empty**, and the
signature is the output commit — so unsigned is *not yet*, never *wrong*. **A gate that FAILED there would
refuse the very artifact a harness is meant to produce.**

Its witness therefore asserts `PASS-UNVERIFIED`. The first version of the audit tool counted only `FAILED`
and reported the unsigned fixture as **silent**, when the gate had refused it correctly.

---

# What still gets through

## `14-silent-partial-UNCAUGHT.json` — retained, uncaught, on purpose

**The most valuable output of the audit, and it is a fixture that passes.**

`REJECTED.md` has always named *the silent one* as the worst shape a defect can take — a row that installs
half of what it declares and stops convergence with no error and no symptom. `totality on provision` is the
gate written to catch it.

**It fires only when a row carries a literal `__partial__` marker.** That is, only when the author
**annotates their own omission** — and a harness that forgets a key does not annotate the omission. The
gate catches honest mistakes and misses real ones.

The fixture is an operating-room window with an **opening time and no closing time**. It is signed, grounded,
replayed, invertible, on the declared surface, syntactically valid, and its numbers agree with its sources.
**Its own cited evidence says `06:00-10:00` twice.** The value carries only the `06:00`.

**Thirteen gates. None of them refuse it.**

`divergence` does not catch it either, and for a reason worth stating: clock times were deliberately excluded
from quantity comparison after an earlier false positive, where the gate flagged a hospital identifier as an
unsupported claim. **The exclusion that made gate 13 correct is what makes it blind here.**

**Do not delete this file, and do not make it pass by weakening anything.** It is retained so the exposure
stays visible instead of becoming a story — the same reason the expired regime is kept in `citations.json`.

## The shape of the remaining exposure

Completeness cannot be checked from a file. **Nothing in a patch says what a full value for a target looks
like** — the seed declares *that* `recovery.or_availability` is a variation point, not *what shape* an answer
must have.

Closing it properly means the seed declaring a schema per target, so a partial answer is a type error rather
than a silent one. **That is a change to the seed, not to the battery**, and it is out of this fork's
partition — recorded here as the next thing anyone hunting this should read.
