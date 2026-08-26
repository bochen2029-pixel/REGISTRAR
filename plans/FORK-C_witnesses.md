# FORK C · a witness for every gate

**Created `2026-08-26` · branch point `9a1a5f7` · read [`../FORKS.md`](../FORKS.md) first, it is binding**

---

## In one breath

**Thirteen gates. Four adversarial fixtures.** Nine gates have no evidence they can fire. Give each one a
witness — a patch that is wrong in exactly one way, and a test asserting *that* gate refuses it and names
the defect.

---

## Why this is worth a whole session

`SPEC.md` §14 ranks the risks, and this is **first**:

> **The central risk is not a wrong patch. It is a weak battery.** A foreign harness produces confident,
> plausible, wrong work all day, and the gates are the only thing between that and an organisation where
> wrong loses an organ.

That risk is currently **unmeasured**, and worse than unmeasured: the four fixtures that do exist were
written by **the same author as the gates they test.** A battery validated only against adversaries its own
author imagined is a battery whose blind spots are exactly its author's.

**And it is what makes the falsifier worth running.** F-PATCH-DELTA grades a harness-authored patch *against
these gates*. If the battery is weak, its verdict is weak in the same proportion — **a pass could mean the
harness did well, or it could mean the battery is easy, and nothing distinguishes them.**

---

## The thirteen, and which have witnesses

Run `python gates/validate_patch.py examples/worked/northlake.patch.json` to see them live.

| Gate | Witness today |
|---|---|
| schema shape | `03-no-inverse` |
| **blast radius** | `01-off-surface` |
| target syntax | **none** |
| L0/L1/L4 immutability | **none** |
| inverse declared | `03-no-inverse` |
| **local invertibility** (T3) | in `test_divergence`-adjacent unit tests, **no fixture** |
| **evidence binding** | `02-ungrounded` |
| shadow run | `02-ungrounded` |
| shadow-run fidelity | undecidable — PASS-UNVERIFIED by design |
| expiry | **none** |
| **totality on provision** | `04-partial` |
| **divergence** (gate 13) | unit tests, **no fixture** |
| signature | **none** |

**Confirm this table before trusting it** — it was assembled by reading, and reading is what this fork
exists to replace.

---

## The work

For each gate without a witness:

1. **A fixture in `examples/worked/rejected/`** — a patch wrong in **exactly one** way. One defect per
   fixture, or a passing test proves nothing about which gate caught it.
2. **A test** asserting *that specific gate* returns `FAILED`, **and that its detail names the defect in
   words.** `SPEC.md` requires every refusal to teach; a gate that says "invalid" is a gate nobody learns
   from.
3. **A `$note`** in the fixture explaining what a real harness would have been thinking when it produced
   this. The existing four do this and it is why they are the highest-signal file in the repository.

**Mutation is a legitimate way to find candidates** — take the worked example, perturb one field, see which
gate fires. **A perturbation that no gate catches is itself a finding**, and the most valuable output this
fork can produce.

---

## The class of defect worth hunting hardest

`examples/worked/REJECTED.md` already names it, and it is the one a fixture is most likely to miss:

> **The silent one** — a row that installs *half* of what it declares and stops convergence **with no error
> and no symptom.**

A fixture that fails loudly is easy. **A fixture that fails silently is what the battery actually needs to
prove it catches**, because that is the shape of the failure that reaches production.

---

## What would make this fork a failure

**Writing fixtures that pass.** The temptation is to produce thirteen tidy files and a green battery. **A
fixture that no gate catches is the finding** — record it, do not delete it, and do not weaken the fixture
until something catches it.

**And do not weaken a gate to make a fixture pass.** If a gate is wrong, fix the gate and say so in the
commit. That has happened three times already in this repository and each was worth recording — most
recently gate 13, where **three of its first four findings were the gate being wrong, not the rows.**

---

## Definition of done

- every gate that *can* be witnessed has a fixture and a test naming its defect
- gates that genuinely cannot be decided from a file **stay PASS-UNVERIFIED and are documented as such** —
  `shadow-run fidelity` needs the site's tape; that is honest, not a gap
- **any perturbation no gate caught is written up** in `REJECTED.md` as an open exposure
- `conformance/run.py` reports the count: *N gates, M witnessed*
- the full battery green before every push

---

## Coordination with mainline

**Mainline's F-PATCH-DELTA pre-registration pins the gate battery by commit SHA.**

Your improvements apply to the **next** run, not the one being pre-registered — pre-registration fixes the
instrument, and a rubric that shifts while you strengthen the gates underneath it is not pre-registered.

**The delta between the two runs is itself informative:** the same harness graded by a weak battery and then
a strong one tells you how much of the first verdict was the battery.

---

## What not to do

- **Do not touch `deepseek-harness-master/`.** See `FORKS.md`.
- **Do not edit the four existing fixtures.** They are cited in `REJECTED.md` and on the public page.
- **Do not add a fixture containing anything resembling real data.** Synthetic, and the hygiene check
  requires every fixture to say so.
- **Do not weaken a gate to make a fixture pass.**
