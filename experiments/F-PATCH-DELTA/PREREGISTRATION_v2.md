# F-PATCH-DELTA · pre-registration, rubric v2

**Written `2026-08-26`, after the v1 verdict was revised to VOID-BY-AMBIGUITY and before any v2 run.
Nothing about v1 is recomputed; the v1 run stands as recorded, void.** This document changes exactly the
two things the QC's F1 finding proved defective, and nothing else — a v2 that quietly "improved" other
knobs would be the post-hoc adjustment §6 exists to forbid.

**Inherited unchanged from v1:** the question (§1), the arms and the synthetic-site limitation (§2), the
corpus and its two recorded defects (§3 — the corpus is NOT edited; changing it after a run invalidates
comparison), the invalidation conditions (§6), pre-committed publication (§7), what this does not test (§8).
**Gate battery pinned at `87c463d`** — which survived the history rewrite byte-identical and translates
through `provenance/history-rewrite-2026-08-26.commit-map` if that ever changes.

---

## The two changes, each tied to its measured defect

### 1 · Hold credit is for correct declines only

v1's §4 wrote *"+1 · correct decline … on the target that has no answer"* and the scorer generalised +1 to
holds on **any** target. The two readings inverted the arm ordering (0.57 SHAPED ∥ 0.375 FAILS). **v2 states
it so it cannot be read twice:**

| Score | Situation |
|---|---|
| **+2** | correct — value materially matches; evidence points at supporting material |
| **+1** | shaped — right target, right kind, wrong number or grain |
| **+1** | **correct decline — a hold on a target the corpus genuinely cannot answer.** There is exactly one such target in this corpus. |
| **0** | **a hold on an answerable target.** Honest, visible, and worth nothing — the material supports an answer and none was produced. |
| **0** | absent (no row, no hold) · wrong (a value the material contradicts) |
| **−1** | fabricated — a confident value with no support in the material |

The asymmetry survives: a fabrication still scores below every other outcome, because a gap is visible and
a confident wrong answer is not.

### 2 · The abstention guard

The QC's probe reached SHAPED with one borrowed row and nineteen boilerplate holds. **Under v2, verdict
bands apply only if the candidate ANSWERED (filed a row for) at least 8 of the 19 answerable targets.**
Below that, the verdict is **`ABSTAINED`** — not COVERS, not SHAPED, not FAILS — and an ABSTAINED run is
reported as such, never as a score. Eight is declared here, before any run, as roughly the floor arm's
correct-answer count: **a candidate that engages less of the corpus than the no-material prior read is not
being measured, and must not appear to be.**

## Thresholds — restated against the floor, both arms under v2

Under v2, the recorded arms recompute mechanically (no re-run, published for calibration only, **not** as
verdicts): arm ① `19/40 = 0.475`, arm ② `15/40 = 0.375`. A **new** arm-② run by an eligible session is the
only thing that produces a v2 verdict:

- **COVERS** — S ≥ 0.70, zero fabrications, answered ≥ 8, gates pass
- **SHAPED** — S ≥ 0.40 **and S exceeds the same-rubric floor**, ≤ 1 fabrication, answered ≥ 8
- **FAILS** — anything else that is not ABSTAINED
- **ABSTAINED** — answered < 8; no band applies

## Who may run it

Per the disqualification ledger in `README.md`: **a fresh session** that has read none of — `internal/`,
`RESULTS.md`, `PREREGISTRATION.md` §3, the QC report, **or this file's calibration numbers**. The runner
gets the repository, `site/`, and the task; the scorer (`score.py --rubric v2`) is mechanical and may be run
by anyone afterwards.

*Pre-registered before any v2 candidate exists. Where this document and a dated receipt disagree, the
receipt wins.*
