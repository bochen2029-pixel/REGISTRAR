# AUDIT — seven independent auditors, and what they broke

**`2026-08-27` · seven opus-tier auditors run against `fork/battery` before merge, each with a
distinct adversarial mandate and each told that refuting a claim is worth more than confirming one.
Findings posted to the Intercom bus at `proj-registrar-qc-b60738d4` (messages #2006–#2029) and
reproduced here. Every finding below was re-verified by the author before acceptance; none was taken
on the auditor's word.**

**The panel found more than the work it audited.** That is recorded plainly because the alternative
— folding their findings into the original as though they had always been there — is the failure
mode this repository already has a name for.

---

## Verdicts

| | mandate | verdict |
|---|---|---|
| **A1** | reproduce the mutation numbers | **MAJOR** — score overstated; 2 new holes found |
| **A2** | attack the attribution instrument | **BLOCKER** — a second contamination, same class as the first |
| **A3** | is the "new hole class" new? | **MAJOR** — already known; mechanism mis-stated |
| **A4** | house-law compliance | **BLOCKER** — 6 blockers, incl. a broken pre-registration |
| **A5** | partition & vault hygiene | **MINOR** — nothing leaked; one governance gap |
| **A6** | red-team the headline | **REFUTED** |
| **A7** | hostile code review | **BLOCKER** — two published numbers wrong |

## What they killed

**The headline.** A6 — 11/11 identical classification on shared targets; the class tracks the
target's value shape, not groundedness. `p = 0.71`. See `ATTRIBUTION.md`, withdrawn.

**The `[D]` meta-finding, and this one was falsifiable in one command.** `RESULTS.md` claimed *"gate
13's hardening opened this hole — a gate was made more accurate and less powerful in the same
commit."* A4 checked git. Gate 13 has two commits: the **introducing** commit `3825787` **already
contains** `NOT_A_QUANTITY`, and the only later one, `2d1ed0f`, **tightened** the gate. There is no
commit in which it was weakened. Verified independently: `git show 3825787:gates/divergence.py |
grep -c NOT_A_QUANTITY` → **2**. Tagged `[D]` with no chain shown and no commit cited.

**The novelty.** A3 — the class is already named in `examples/worked/REJECTED.md:225-227` and pinned
by `gates/test_divergence.py::test_identifiers_are_not_assertions`. Fixture
`15-credentials-UNCAUGHT.json` states the contingency principle outright: *"Removing the digit
removes the refusal."* The contribution is the **count**, not the discovery.

**The stated mechanism.** A3 — it is not "the value carries a bare scalar quantity." It is a
**key-name regex** (`NOT_A_QUANTITY`), plus a `(?<![\w.])` lookbehind that rejects a digit after an
underscore, plus `attest._asserts_a_bound`. Proof: `numbers_of({'hospital': 1147})` with an **int**
value returns `set()`, while the same clock data under a different key returns `{0.0, 6.0}`.

**A false receipt.** A4 — both `ATTRIBUTION.md` and `LOG.md` asserted a retraction was *"left in the
tool with the note beside it."* `attribute.py` contained **zero** retraction text. Verified: `grep
-ci "retract|meaningless|not comparable"` → **0**. A claimed receipt that does not exist is worse
than a quiet edit. The note is now actually in the tool.

**A three-states violation, in the mount direction.** A4 — *"all sixteen gates still pass"* where the
battery returns 14 GREEN · **2 PASS-UNVERIFIED**, and *"defects this battery would mount"* where no
mutant is ever all-GREEN. Both corrected.

## What they found that the work missed

1. **There is no target-collision gate.** Two rows, same target, contradictory values, properly
   chained inverse → `PASS-UNVERIFIED`, nothing objects. *(A1, A7; verified.)* The old
   `duplicate-conflict` "kill" came from a null inverse, not the collision — a **false kill**.
2. **The L0/L1/L4 immutability gate has zero coverage, and no patch mutation can give it any.**
   `targets.json` declares 20 targets, **all L2/L3**, and gate 4 only inspects declared targets. The
   battery's most safety-critical gate is unmeasured, and 83.8 % implied otherwise. *(A1, A7.)*
3. **The battery does not catch an inflated shadow-run denominator.** The old operator's kills came
   from the counts not closing. Keep them closing so the lying denominator is the only defect and
   **all 9 survive** — the case the operator's own docstring called *"the quiet one."* *(A7.)*
4. **`how_scored()` reported silence as an honest decline** — `"hold" in w` matches `"no hold"`, so
   `score.py`'s only absent string was misclassified. Latent on these two arms; the expected failure
   mode at the real-site run. *(A7.)* Order corrected.
5. **The mechanical oracle compares a value to prose the same author wrote.** Structural, and no
   evidence-mutation coverage metric can see it. *(A6.)*
6. **`attest` catches supersession but not denial.** *"this rule was withdrawn in rev 5"* → FAILED;
   *"the source does not specify any owner"* → passes. *(A3.)*
7. **Only 10 of 16 gates were ever driven to FAILED** across the whole run. Coverage of the
   instrument was never reported. *(A1.)*

## What survived audit

- **Determinism** — `--json` byte-identical across three runs and four `PYTHONHASHSEED` values. *(A1.)*
- **The FAILED-only kill criterion** — honestly implemented, no PASS-UNVERIFIED leakage. *(A1, A4.)*
- **No no-op and no duplicate mutants**; error handling depresses rather than inflates. *(A7.)*
- **The 3-of-9 count** — exact. *(A3.)*
- **`op_evidence_unrelated`'s survivor set** — sound and independent of every defect above. *(A7.)*
- **Containment** — zero vault content in either commit; `S = 0.575` is arithmetic on the already
  public 23/40, and the quoted `"180 against 192 (6%)"` is from the **tracked** arm-1 result. Both
  commits touch only `experiments/F-BATTERY-STRENGTH/`. Scratch copy of the vault confirmed
  destroyed. Safe for a public repo. *(A5; verified.)*

## Where the auditors disagree, and why that is itself a finding

**A2 and A7 give different corrections for the same bug.** Both identify `_failed_set` keying on
`(gate, detail)` where `detail` is a truncated join. A2 recomputes at message granularity → **M(arm
1) = 0.40**. A7 recomputes on gate names → **M(arm 1) = 0.00**. As shipped it was **0.20**.

Three defensible methods, three answers, one of them the maximum and one the minimum of the range.
**That is not a discrepancy to adjudicate — it is the reason the metric is withdrawn.** A number
whose value depends on which repair you pick was never measuring what its label claimed.

## The governance gap

`fork/battery` was absent from `PARTITION` in `tools/worktree.py` and from `FORKS.md`, so
`worktree.py --check` had no rule to enforce for it, and `FORKS.md` assigns `experiments/` to
mainline. No collision occurred — `F-BATTERY-STRENGTH/` is a fresh subdirectory — but the guardrail
built specifically to stop the 60-file sweep was inert for this worktree. *(A5.)* Registered in this
commit.

---

*Auditors were given the repository, the branch, and a mandate; they were not given the author's
conclusions to confirm. The bus record is `proj-registrar-qc-b60738d4`.*
