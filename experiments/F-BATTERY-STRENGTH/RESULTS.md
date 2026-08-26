# F-BATTERY-STRENGTH — the gate battery, measured

**Run `2026-08-26` · `fork/battery` worktree, branched from `bd89dd0` · harness
`experiments/F-BATTERY-STRENGTH/mutate.py` · deterministic, zero dependencies, no PHI.**

Claim grammar per the house: `[M]` measured · `[D]` derived · `[BET]` kill named · `[NULL]` the
baseline it must beat. A number without its grain, denominator and source is not a number.

---

## The result

| | |
|---|---|
| **Mutation score** | **83.8 %** `[M]` |
| Grain | one **named** defect per mutant |
| Denominator | **136** mutants from 19 operators over `examples/worked/northlake.patch.json` |
| Killed | 114 — some gate returned `FAILED` |
| **Survived** | **22 — defects this battery would accept** |
| Baseline | the worked example, `PASS-UNVERIFIED` (unchanged; the three undecidable gates) |
| Reproduce | `python experiments/F-BATTERY-STRENGTH/mutate.py` |

**Kill criterion is `FAILED`, never `PASS-UNVERIFIED`.** Counting an undecidable gate as a catch is
the three-states-collapsed-into-two error this repository has a gate against. A mutant that only
trips an undecidable gate has not been caught.

## Why the battery had no number before this

`SPEC.md` §14 ranks the risk first — *the central risk is not a wrong patch, it is a weak battery* —
and the evidence for the battery's strength was seven `*-UNCAUGHT.json` fixtures. Those were
**found by hand, by the people who wrote the gates.** That finds the holes someone could imagine and
produces **no denominator**. Seven known holes out of an unknown total is not a measurement.

F-PATCH-DELTA inherits it: **`S = 0.57` was graded by this battery.** A grader of unmeasured strength
leaves the score's meaning unmeasured — a pass could mean the harness did well, or that the battery
is easy, and nothing on the plate distinguished those. It now has a second bound to print.

---

## What survived, and what is actually new

### Rediscovered — the instrument's validity check `[M]`

Mutation independently reproduced **two of the seven** hand-found holes, from operators written
without reading the fixtures:

| operator | mutants | already known as |
|---|---|---|
| `expiry-past` | 9 survived | **fixture 16** — *"the expiry gate parses the date and never compares it to a clock"* |
| `author-machine` | 9 survived | **fixture 17** — *"reports GREEN on the signature gate… it carries a non-empty string"* |

Confirmed at source: `validate_patch.py:190` calls `date.fromisoformat()` and never compares to
today; `:274` tests only `.strip()` for non-emptiness. **The method finds real holes.**

### New — not among the seven `[M]`

> **The evidence check is contingent on the value carrying a bare measurement.**

For **3 of 9 rows** in the worked example, every cited source can be replaced with *"the cafeteria
closes at eight on weekends"* and **all sixteen gates still pass.**

| row | value | why nothing fires |
|---|---|---|
| `nl-001` | `"house_coordinator"` | a role — no quantity to hunt for |
| `nl-004` | `hospital: "1147"`, `06:00–10:00` | an **identifier** and **clock times**, not measurements |
| `nl-007` | `"donor_age_under_18"` | the number is *inside an enum label*, not a standalone quantity |

`gates/attest.py:11` declares the scope plainly — *"gates/divergence — do the NUMBERS in value /
evidence agree? — arithmetic."* **The scope is documented. The consequence is not**: a row asserting
an owner, a routing choice, a window or a category has no mechanical check that its evidence
supports it, and those are exactly the L2 rows that encode how an organisation actually works.

### The meta-finding, and it is the one worth keeping `[D]`

**Gate 13's hardening is what opened this hole.** Its own recorded history says three of its first
four findings were *the gate being wrong* — identifiers read as claims (*a hospital number is not a
measurement*), conservative rounding read as divergence. Both fixes were correct and both were
necessary. Teaching it to ignore identifiers and tolerate rounding is **precisely what makes
`hospital: "1147"` and `06:00` invisible to it.**

> **A gate was made more accurate and less powerful in the same commit, and nothing measured which
> way the trade came out.** That is not an argument against the fix. It is an argument that a gate's
> *coverage* needs a number the way its *correctness* already has tests.

---

## What this does NOT show, stated as loudly

**A mutation score is bounded by its operator set, and mine is not exhaustive.** 83.8 % means *83.8 %
of the defects this harness could think to generate.* Mutation did **not** rediscover fixtures 14,
15, 19 or 20 — silent partial installs, the credentials repoint, the `__partial__` bypass, the
adverse replay — because no operator here generates those shapes. **Fork C's hand method found four
holes this search could not.** The two methods are complements; neither dominates.

Three further limits:

- **A survivor is a candidate hole, not a confirmed one.** Some may be equivalent mutants. All 22 are
  printed in full so a human judges rather than a counter.
- **One patch.** All mutants derive from `northlake.patch.json`. A different worked example would
  exercise different gate paths.
- **`author-machine` has a compensating control** the harness cannot see: the real signature is the
  output commit, not the field. The hole is that the *stated* contract (`AGENTS.md` §5 — *you do not
  sign*) is unenforced at the file, which is law 9's own criterion — *if a rule can only be enforced
  by asking, it is not enforced.*

## `[NULL]` — and it did not win

The null was the seven hand-written fixtures: *if mutation surfaces nothing they did not cover, the
hand method was sufficient and this experiment prints its own funeral.* It surfaced one new hole
class and put a denominator under all of them. **The null loses, narrowly and usefully** — and its
four exclusive findings are recorded above rather than quietly dropped.

## What follows

1. **Two one-line gate fixes** close 18 of 22 survivors: compare `expiry` to today; refuse an
   `author` that matches a machine pattern, or move the check to the commit and say so in the gate's
   own words. *Both are Fork C's partition (`gates/`).*
2. **The measurement-free row is a design question, not a one-liner.** Options: require a
   `derived_from` method for non-numeric values; require the evidence quote to contain the value's
   own token; or declare the class unenforceable from a file and move it to the undecidable three,
   where it would at least be *visible*. **Currently it is invisible, which is the worst of the
   three.**
3. **`experiments/F-PATCH-DELTA/RESULTS.md` gains a second bound.** `S = 0.57` was bounded from above
   by a corpus whose author knew the answers; it is also bounded by a grader now measured at 83.8 %
   against a non-exhaustive operator set. Both belong in one sentence.
4. **Re-run this after any change to `gates/`.** The score is a regression instrument: a gate fix
   that lowers it has traded coverage for accuracy without saying so.

---

*Nothing here has run inside an OPO. No patient data has touched any part of this. Every number above
is the output of a command in this repository and a hostile reader can falsify it in one minute.*
