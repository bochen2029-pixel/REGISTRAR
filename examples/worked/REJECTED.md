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

Every decidable gate is `GREEN`. Three report **`PASS-UNVERIFIED`** — local invertibility, shadow-run
fidelity, and totality — because they cannot be decided from a file. They need a runtime to apply the row and
compare, and they need the site's own tape to confirm a replay actually happened.

**The validator therefore exits non-zero on a patch with nothing wrong with it**, and says so:

> PASS-UNVERIFIED — nothing failed, but checks did not run. This is NOT a pass.

That is deliberate, and it is the lesson the whole battery exists to teach. `GREEN`, `PASS-UNVERIFIED` and
`FAILED` are three different states. **A checker that reported GREEN for a check it never ran would be
committing the exact error the three-state gate exists to prevent** — so this one refuses to, about itself.
