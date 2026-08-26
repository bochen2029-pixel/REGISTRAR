# PLAN · the attribution audit — what did `S = 0.57` actually measure?

**Written `2026-08-26T23:10Z`, BEFORE running anything. Thresholds and interpretations are fixed
here so the reading cannot drift once the numbers exist — the same reason `PREREGISTRATION.md`
exists for the run this audits.**

---

## §1 · The question

F-PATCH-DELTA returned **`S = 0.57`** against a floor of `0.47`, graded by the gate battery. Today
that battery acquired its first coverage number — **83.8 %**, with one named blind class:

> A row whose value carries **no bare measurement** — a role, an owner, an identifier, a clock
> window, an enum label — has **no mechanical check that its evidence supports it.**

And L2, the layer this product exists to author, is described by the repository itself as *staffing
model, call rotation, the escalation ladder as practised, territory, who signs what.* **Almost none
of that is a number.**

So: **the mechanical oracle is one of the four properties that make it safe to let a machine finish
this, and it is the only one that is not a theorem.** The other three — bounded blast radius,
reversibility, confluence — hold unconditionally. This one is empirical, and it has never been
attributed.

> **How much of the arm-2 result rests on rows the battery can mechanically check, and how much
> rests on a human reading a rubric?**

## §2 · Method

Two independent classifications per target, then their cross-product.

**Axis A — gate-checkability `[D]`.** For each row in each candidate, does its `value` present a
**bare scalar quantity** that the divergence gate can hunt for in evidence prose? Classified by the
same rule the battery itself applies, and validated against the harness: a row is `CHECKABLE` if the
`evidence-unrelated` mutation of it is KILLED, and `BLIND` if that mutation SURVIVES. **This is not a
judgement call — it is a re-run of the instrument built this morning, per row.**

**Axis B — how the score was earned.** From `per_target[].why` in the scorer's own output:
`numeric` (a tolerance comparison, e.g. *"180 against 192 (6%)"*), `keys` (*"2/2 keys match"*),
or `absent/wrong/fabricated`.

**The cross.** Score contributed by `CHECKABLE` rows vs by `BLIND` rows, for both arms, and for the
delta between them.

## §3 · Pre-registered interpretation — fixed now, before any number exists

Let **M** = the share of arm 2's *earned* score contributed by rows the battery can mechanically
check.

| M | what it means | what follows |
|---|---|---|
| **≥ 0.70** | The oracle earned the result. | The claim *"a gate battery, not a vendor, decides"* is supported with a denominator for the first time. Print M on the plate and proceed to the real-site run. |
| **0.40 – 0.70** | Mixed. | The claim is **partial and must say so.** The pre-registration for the real-site run names M and the blind class. |
| **< 0.40** | The score was mostly graded by rubric, not by gates. | **The mechanical-oracle property is materially weaker than advertised for the layer that matters**, and that belongs in the counterweights and on the page before any real-site run. Not a funeral for the project — a correction to one of its four safety legs. |

**Additional pre-registered check.** If arm 1 (the floor, which read *no site material*) draws a
*higher* share of its score from `BLIND` rows than arm 2 does, that is evidence the blind class is
where an ungrounded prior most easily hides — the most actionable possible finding, and the reason
this audit is worth doing before the real-site run rather than after.

**What would make this audit worthless:** if `CHECKABLE` and `BLIND` turn out not to partition the
rows meaningfully — e.g. every row is one or the other. Then the cross has one cell and there is
nothing to attribute. **That outcome gets printed too.**

## §4 · Protocol — the answer key, handled explicitly

`internal/` is withheld from this worktree on purpose: *a fork that cannot see the answer key cannot
be contaminated by it.* That rule protects **candidate authorship.** This audit authors no candidate
— both candidates and the key already exist and the run is closed — so seeing the key cannot bias
anything that has not already happened.

**Even so, the key does not enter this worktree.** Arm 2's per-target scores are produced by running
the existing `score.py` in a **scratch copy outside every git tree**, and only its *output* is read
back. `score.py` writes a `RESULT_*.json`; running it in main's tree would leave a file in another
session's partition, which is precisely the collision the worktrees exist to prevent.

**Nothing in `C:\REGISTRAR` or any other worktree is written by this audit.**

## §5 · Deliverable

`ATTRIBUTION.md` beside this file: the cross-table, M with its grain and denominator, the
pre-registered verdict from §3 applied without adjustment, and whatever the audit got wrong.
Appended to `LOG.md` with timestamps as it runs.
