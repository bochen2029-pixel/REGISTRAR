# fixtures/

**Synthetic donor cases. Zero PHI, forever.**

Not de-identified real cases. Not sampled, not perturbed, not anonymised. **Synthetic** — and that is a
provenance requirement rather than a privacy convenience. See [`PROVENANCE.md` §4](../PROVENANCE.md): real
case data is inadmissible in this repository for any purpose, including fixtures.

An auditor should be able to confirm this from the data itself. Real data disguised as fixtures shows up in
distributional structure — internally consistent identifiers, plausible clinical correlations, realistic
timing. These have none, because there is nothing underneath them.

## Every value here is illustrative

No duration in any fixture is a clinical or regulatory claim. That explicitly includes the cold-ischemia
budget in `cases/infeasible-transport.json`: organ-specific ischemia tolerances are clinical figures that
require citation to published literature before any validator enforces one, and `t_cold_ischemia` in
[`core/lifecycle/lifecycle.yml`](../core/lifecycle/lifecycle.yml) is deliberately `TODO-VERIFY`.

**If you find yourself quoting a number from this directory, stop.**

## Format

JSON rather than YAML, so [`floor/closure.py`](../floor/closure.py) runs on a bare Python with nothing
installed. A reference artifact that requires a dependency install before it does anything is a worse
reference artifact.

```json
{ "kind": "at_least", "later": "cross_clamp", "earlier": "incision",
  "minutes": 45, "label": "incision to cross-clamp", "layer": "L1" }
```

| kind | meaning |
|---|---|
| `at_least` | `later - earlier >= minutes` |
| `at_most`  | `later - earlier <= minutes` |
| `window`   | `event` falls within `[opens, closes]` from the reference |
| `at`       | a completed event, pinned to a known time |

`layer` records **which layer owns the constraint** — and that field is the point. Run
`floor/closure.py` on a case and read which layers appear in the binding path: the federal constraints are
real but generous, and **the rows that actually decide whether a case converts are the L2 and L3 ones** —
your OR window, your lab's turnaround, your team's mobilisation. That is the whole argument for why the fit
is the product, visible in one output.

## The cases

**`morning-or-window.json`** — every field green, no timer expired, and the morning OR window already gone.
The closure derives that the serology had to be drawn at 22:15 the previous evening; it is 23:40. This is the
failure class a flat list of timers cannot see, because at the moment the case became infeasible **no single
field was wrong.**

**`infeasible-transport.json`** — a case that cannot be met, where no individual constraint is unreasonable.
The closure reports the four constraints that cannot all hold, and that the case is short by thirty minutes.

## Run them

```bash
python floor/closure.py fixtures/cases/morning-or-window.json
python floor/closure.py fixtures/cases/infeasible-transport.json
python floor/test_closure.py
```

## Adding a case

Make it adversarial. **The fixture set is what makes a passing completion mean something**, and a battery
that only contains cases which pass proves nothing at all. Good additions: a case that is feasible but with
zero slack; one where two organs' ischemia budgets conflict; one where the binding path runs entirely through
L3 constraints; one that is infeasible for a reason no single timer would surface.
