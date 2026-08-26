# F-BATTERY-STRENGTH — the gate battery, measured

**Corrected `2026-08-27` after a seven-auditor review. The first version of this file reported
83.8 %, claimed a new hole class, and carried a `[D]` meta-finding that git falsifies. See
[`AUDIT.md`](AUDIT.md) for what broke and who broke it; the prior text is at commit `0ea1b5d` and is
not rewritten.**

Run on `fork/battery`, branched from `bd89dd0` · harness
[`mutate.py`](mutate.py) · deterministic, zero dependencies, no PHI, reads only.

Claim grammar: `[M]` measured · `[D]` derived, chain shown · `[NULL]` the baseline it must beat.
A number without its grain, denominator and source is not a number.

---

## The result

| | |
|---|---|
| **Mutation score** | **74.8 %** `[M]` |
| Grain | one **named** defect per mutant |
| Denominator | **127** mutants from 18 operators over `examples/worked/northlake.patch.json` (9 rows) |
| Killed | 95 — some gate returned `FAILED` |
| **Survived** | **32 — defects this battery does not FAIL**, in **6 classes** |
| Baseline | the worked example: 14 GREEN · **2 PASS-UNVERIFIED** · 0 FAILED |
| Reproduce | `python experiments/F-BATTERY-STRENGTH/mutate.py` |

**Kill criterion is `FAILED`, never `PASS-UNVERIFIED`** — counting an undecidable gate as a catch is
the three-states-collapsed-into-two failure this repository gates against. *Note the constraint never
fired: no mutant tripped only an undecidable gate, so it is a discipline that had no occasion to
work.*

**"Survived" means the battery does not FAIL it — not that it would mount.** Two gates are ambient
`PASS-UNVERIFIED` on every mutant, so **no mutant among the 127 is ever all-GREEN** and none would
mount. The earlier wording collapsed those.

### What changed from 83.8 %

| correction | effect |
|---|---|
| `op_target_reaches_l0` **removed** — its stated defect was false; it died on blast radius, byte-identical to `op_target_undeclared` | −9 mutants |
| `op_shadow_inflate` **fixed** — kills came from counts not closing, not the lying denominator | 9 kills → 9 survivors |
| `op_duplicate_conflict` **fixed** — the kill came from a null inverse, not the collision | 1 kill → 1 survivor |

## The six survivor classes

| class | mutants | status |
|---|---|---|
| `expiry-past` | 9/9 survive | **known** — fixture 16. `validate_patch.py:191` parses the date, never compares it to today. |
| `author-machine` | 9/9 survive | **known** — fixture 17. `:274` tests `.strip()` for non-emptiness; any string signs. |
| `evidence-unrelated` | 3/9 survive | **quantified here** — see below |
| `shadow-inflate` | 9/9 survive | **new** *(A7)* — the battery does not catch an inflated denominator |
| `duplicate-conflict` | 1/1 survives | **new** *(A1, A7)* — **there is no target-collision gate** |
| `value-contradicts` | 1/1 survives | related to fixture 18; that is two rows contradicting each other, this is one row contradicting its own evidence. Denominator 1 — the operator only fires on string values. |

## The evidence-substitution finding — quantified, not discovered

> For **3 of 9 rows**, every cited source can be replaced with *"the cafeteria closes at eight on
> weekends"* and the battery returns **no FAILED gate**.

`nl-001` (a role), `nl-004` (an identifier and clock times), `nl-007` (a number inside an enum
label). The count is exact and nobody had counted it.

**The class itself was already known**, and this file previously claimed otherwise. It is named in
`examples/worked/REJECTED.md:225-227`, pinned by
`gates/test_divergence.py::test_identifiers_are_not_assertions`, and stated outright in fixture
`15-credentials-UNCAUGHT.json`: *"Removing the digit removes the refusal."* *(A3.)*

**The mechanism, corrected `[D]`:** not "the value carries a bare scalar quantity." It is the
**key-name regex** `NOT_A_QUANTITY` (`gates/divergence.py:117`), plus a `(?<![\w.])` lookbehind that
rejects a digit following an underscore, plus `attest._asserts_a_bound` — two gates, not one. Chain:
`numbers_of({'hospital': 1147})` with an **int** value → `set()`; the same clock data under a
different key → `{0.0, 6.0}`. *(A3.)*

**And "no mechanical check" was too absolute.** `attest`'s phrase list runs regardless of value
shape: *"this rule was withdrawn in rev 5"* → **FAILED**. But *"the source does not specify any
owner"* — a direct denial of the row's claim — passes. The correct statement: **the numeric and
bound-modality checks are contingent; a value-independent phrase list survives, and it catches
supersession but not denial.** *(A3.)*

**WITHDRAWN:** the `[D]` meta-finding that gate 13's hardening opened this hole. Git falsifies it —
the introducing commit `3825787` already contains the exclusion, and the only later commit
`2d1ed0f` **tightened** the gate. There is no commit in which it was weakened.

## What this does NOT show

1. **The score is bounded by the operator set, and 18 operators is not exhaustive.** Mutation did not
   reproduce fixtures 14, 15, 19 or 20. **The hand method found four holes this search cannot.**
2. **The score is a function of patch shape.** 18 operators × 9 rows ≈ 127. Change the row count and
   the number moves with no change to any gate. It is defensible as a **regression instrument on a
   fixed patch** and *not* as a battery property — so it does **not** belong on F-PATCH-DELTA's plate
   as a bound on `S`, as the earlier version proposed.
3. **32 survivors are 6 classes, not 32 holes.** `expiry-past` is one hole counted nine times. The
   declared grain is per-mutant; every conclusion here is about classes, and mixing the two is what
   the number fence forbids.
4. **No mutant was checked for being killed by the *right* gate.** `killed_by` is collected and never
   reported. A mutant probing evidence-binding but killed by schema-conformance is a false kill. This
   is the largest unexamined threat to 74.8 %. *(A4.)*
5. **BLIND means "blind to substitution," not "blind to evidence."** Every row is killed by
   `evidence-strip` (9/9). The finding rests on one operator.
6. **Only 10 of 16 gates were ever driven to FAILED**, and the L0/L1/L4 immutability gate has **zero
   coverage** — no mutation of a patch file can reach it, because every declared target is L2/L3.

## `[NULL]` — the hand-written fixtures, and the honest scoreboard

The null was the seven `*-UNCAUGHT.json` fixtures. On hole-finding it **wins 4–1**: it found four
classes this search cannot generate; mutation contributed one quantification plus two new classes
found by the auditors improving the harness. What mutation added that the null could not is a
**denominator**. The earlier claim that *"the null loses, narrowly and usefully"* is withdrawn as
one-sided — **the two methods are complements and neither dominates**, which this file said twenty
lines later while claiming the opposite here.

## What follows

1. **Two one-line gate fixes close 18 of 32 survivors** — compare `expiry` to today; refuse a
   machine-shaped `author`, or move the check to the commit and say so in the gate's own words.
   *(`gates/` is Fork C's partition.)*
2. **`ROADMAP.md:357` already pre-declared the priority, by measurement**: *"a well-formed variant of
   each of the seven: if one passes clean, that is the highest-priority gate in the project."*
   `expiry-past` and `author-machine` **are** well-formed variants of 16 and 17 and they pass clean.
   The earlier version of this file re-ranked that silently in favour of its own finding. **The
   pre-declared ranking stands.**
3. **Two new gates are implied by the new classes**: a target-collision check, and a shadow-run
   denominator that must be reconcilable with the cited evidence.
4. **The L0 immutability gate needs a different instrument.** Its coverage cannot be raised by
   mutating patch files.
5. **Re-run after any `gates/` change** — the score is a regression instrument on this patch. It is
   **not** in `CLAIMS.json` and must not reach a public surface until it is, since it changes
   whenever `gates/` changes. *(A4.)*

---

*Nothing here has run inside an OPO. No patient data has touched any part of it. Every number above
is the output of a command in this repository. The one number that is **not** reproducible in a
clone — `M`, from the withdrawn attribution — is withdrawn partly for that reason.*
