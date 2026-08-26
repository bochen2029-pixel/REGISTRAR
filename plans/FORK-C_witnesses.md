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


---

# OUTCOME · `2026-08-26`

**Done against the definition above.** `13 gates · 9 witnessed · 3 entangled · 1 undecidable`, and
`battery · isolation` reports GREEN: every witnessed gate fires alone.

## The starting position was worse than this plan estimated

The table above said *nine gates unwitnessed*. Measured, it was **one gate cleanly witnessed out of
thirteen** — because every existing fixture fired two to four gates at once, and a fixture that trips three
gates proves *something* refused the patch, **not which**.

Three rows of that table were also simply wrong — `local invertibility`, `expiry` and `divergence` were
each already tripped by an existing fixture, incidentally. **The plan said to confirm the table before
trusting it, and confirming it was the first finding.**

## What was built

**Nine isolating fixtures** (`05`–`12`, `21`, `22`), each firing exactly one gate, each with a test asserting
that gate refuses it **and names the defect in words**. Plus `gates/witness.py` — the coverage matrix, run by
conformance so the number is printed rather than assumed — and 74 assertions in `gates/test_witness.py`.

## Three gates cannot be isolated, and that is structural

Recorded in `witness.py:ENTANGLED` with the reason, so no future author chases an impossible fixture:

- **`target syntax`** — a malformed target is by definition not a declared target, so blast radius always
  fires first. **Its value is teaching, not catching.**
- **`inverse declared`** — fires only when the key is *absent*, and an absent required field trips schema
  shape first.
- **`L0/L1/L4 immutability`** — **unreachable from any patch.** It is a seed invariant living in a patch
  validator; it would fire only if `lifecycle.yml` itself declared an L0 variation point. Witnessed with a
  synthetic target table.

And **`signature` never returns FAILED, correctly** — a machine leaves `author` empty, so unsigned is *not
yet*, never *wrong*. Its witness asserts the middle state.

## Seven exposures, retained as fixtures that pass

An adversarial sweep produced **44 silent passes out of 49 candidates**; each headline was re-verified by
hand before being written down. Seven are kept as `*-UNCAUGHT.json`, counted by conformance as known
exposures, with tests that fail in **both** directions — *if one starts being caught the exposure closed and
it must be promoted; if a file disappears, someone deleted an exposure instead of fixing it.*

The largest blast radius is `15`: **`allocation.credentials` is a declared target**, so a row can repoint the
national allocation system at an arbitrary host, ship a live-looking key, and set `verify_tls: False`, with
all thirteen gates content.

## One gate was fixed rather than recorded

Divergence's `conservative` branch accepted any value within +25% of **any** number in the evidence prose —
so a study's `n` and a **year** could license an arbitrary duration. It was the gate purpose-built for that
defect class, failing on its own mission, **silently in the affirmative.** Now a duration may only be
licensed by a duration; the house rule still passes and mainline's pinned worked example is unchanged.

## What this fork could not close

**Three sentences cover nearly every exposure, and all three are seed work:**

1. **The seed declares where a value may go, never what shape it must have.** No types, no ranges, no
   required keys, no direction of safety.
2. **Every gate reads a row; no gate reads the patch.**
3. **Several gates check that a field is present rather than what it says.**

The sharpest illustration came from the last fixture: omitting each required field in turn, **exactly one
omission isolates `schema shape` — `value`.** Every other field has a gate of its own. **The one field with
nothing behind it is the field the row exists to state.**

**Closing these means a schema per target.** That is a change to the seed, outside this partition, and it is
written up in `examples/worked/REJECTED.md` as the next thing anyone hunting this should read.
