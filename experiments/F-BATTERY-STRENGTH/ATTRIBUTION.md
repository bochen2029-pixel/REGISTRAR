# ATTRIBUTION — **WITHDRAWN 2026-08-27**

**This document previously reported that the ungrounded arm of F-PATCH-DELTA earned 80 % of its
score on rows the gate battery cannot tie to evidence, and that this located where a
confident-but-baseless completion hides. That finding is refuted. It is withdrawn, not corrected,
because patching the numbers would preserve a causal claim that does not survive.**

The prior text is recoverable at commit `075b2b4`. Nothing is rewritten — house rule: corrections
are new entries with the reason.

---

## Why it is withdrawn rather than repaired

**1 · The causal claim is false, and my own data falsifies it.** On the **11 targets both arms
answered, the CHECKABLE/BLIND classification is identical 11/11.** No arm-1 row changes class when
handed arm 2's real site-sourced evidence. Blindness is a property of **the target's value shape**,
not of groundedness.

Arm 1's higher blind share was **composition**: it answered 9 targets arm 2 *declined*, 7 of them
non-numeric. **Arm 2 lowered its blind share by declining blind targets, not by being grounded.**
Fisher two-tailed **p = 0.71** by row count — not distinguishable. *(Audit A6.)*

**2 · The pre-registration was broken by the document that claimed to execute it.**
`PLAN_attribution.md` §1 fixed **M** as *"the share of arm 2's earned **score**"* — 9/23 = **0.39**,
which §3 maps to **RUBRIC-DOMINATED**. The withdrawn text redefined it as *"earned **row-points**"* —
9/14 = **0.64**, **MIXED** — under a heading reading *"The verdict, applied without adjustment."*
The threshold was not adjusted; **the denominator was**, after the numbers existed, across a
pre-registered boundary, in the flattering direction, disclosed nowhere. `attribute.py`'s dead
`total_earned` variable is the fossil of the discarded denominator. *(Audit A4, A7.)*

**3 · The decomposition that carried the conclusion did not close.** The text read *"+9 declines,
−11 on checkable rows, +1 fabrication"* against a claimed +4. That sums to **−1**. The −11 was the
**BLIND** delta printed under the **CHECKABLE** label, and the real +5 was dropped — so the prose
asserted the opposite of its own table. Arm 2 authored **more** well-evidenced numeric points, not
fewer. This is the defect gate 13 refuses, in the audit's own arithmetic. *(Audit A4.)*

**4 · M is not robust to its own definition.** Three correction methods give three answers for arm 1
— as-shipped **0.20**, message-granularity **0.40** *(A2)*, gate-name delta **0.00** *(A7)* — because
`_failed_set` keyed on `(gate, detail)` where `detail` is a **truncated join** of every row's message
(`validate_patch.py:218`, `[:200]`). Arm 1's details run 224–1159 characters, so a row's class was
decided partly by its ordinal position in the file, and one row scored CHECKABLE because destroying
its evidence made the battery report **fewer** defects. A metric whose value depends on which repair
you choose is not a measurement.

**5 · A category error underneath all of it.** CHECKABLE is decided against evidence **the completion
authored itself**; the rubric is decided against a hidden answer key. Disjoint inputs, no causal
path. *(Audit A6.)*

## What replaces it, and it is not mine

The audit's own finding is stronger than the one withdrawn, and belongs to A6:

> **The CHECKABLE class buys zero protection.** Take arm 1, add shadow-run denominators, rewrite two
> weasel phrases — and the battery returns **no FAILED gates at all**, the same terminal state as
> arm 2, with the score unchanged at 19/40. `divergence` goes GREEN on **all 20 rows**, including the
> **−1 FABRICATION** whose own grading reads *"the corpus contains nothing on this target."*

So it was never 80 % that survived. It was **100 %**, and the mechanism is not the blind class:
**the mechanical oracle compares a value to prose the same author wrote.** No evidence-mutation
coverage metric can see that — including the one this document was built on.

## What is NOT withdrawn

`RESULTS.md` — the mutation measurement — stands, corrected. The **3 of 9** count is verified exact
*(A3)*, and `op_evidence_unrelated`'s survivor set is sound and independent of every defect above
*(A7)*.

## The lesson, printed because it is the point

Four overclaims in four directions, in one document, written in about twenty minutes at the end of a
long session — and a seven-auditor panel found all four. **The pre-registration did not fail; it was
not honoured.** Writing a plan and then reporting against a different denominator is the failure the
plan exists to make visible, and it was visible: the fossil was sitting in the code.
