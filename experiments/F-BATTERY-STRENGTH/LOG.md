# F-BATTERY-STRENGTH — the running log

**Append-only. Every entry carries a UTC timestamp. Corrections are new entries with the reason,
never quiet edits — house law 14.**

Session: `fork/battery` worktree at `C:\REGISTRAR-forkB`, branched from `bd89dd0`.
Operator instruction: *proceed at your own best recommendation, log everything with datetimestamps,
durably, as a file in the repo.*

---

### 2026-08-26T22:54:00Z · why this experiment exists

`SPEC.md` §14 and the counterweights both rank the same risk first:

> **the central risk is not a wrong patch — it is a weak battery.**

**It has never been measured.** The battery's strength is currently attested by seven
`*-UNCAUGHT.json` fixtures, and `conformance/run.py` reports them honestly:

```
PASS-UNVERIFIED gates · known exposures ... 7 hole(s) no SEMANTIC gate catches, retained
deliberately (7 also trip a floor gate for being minimal — that is not closure)
```

Those seven were **found by hand, by the people who wrote the gates.** That method finds the holes
someone could imagine. It cannot estimate the ones nobody thought of, and it produces no denominator.

**F-PATCH-DELTA inherits the problem.** `S = 0.57` was graded *by this battery*. A grader of unmeasured
strength makes the score's meaning unmeasured too: a pass could mean the harness did well, or that the
battery is easy, and nothing on the plate distinguishes them.

**The claim under test:** mutation testing gives the battery a survival rate — a number with a
denominator — and every survivor is a hole found by search rather than by imagination.

**[NULL]** — the seven hand-found fixtures. If mutation finds nothing the hand-written set did not,
the hand method was sufficient, that is a real result, and this experiment prints its own funeral.

---

### 2026-08-26T22:53:43Z · worktree claimed

`git worktree add C:/REGISTRAR-forkB -b fork/battery` from `bd89dd0`. Provisioned via
`tools/worktree.py --provision`: 5 pinned corpus sources copied; chassis absent by design;
`internal/` **withheld on purpose** — and correct here for a second reason the tool does not
mention: this experiment measures the *battery*, so the F-PATCH-DELTA answer key is irrelevant to it
and its absence costs nothing.

Claimed path: `experiments/F-BATTERY-STRENGTH/` only. Nothing else written, in any tree.

### 2026-08-26T22:55:48Z · first run

19 operators → **136 mutants → 114 killed, 22 survived. Score 83.8 %.** Baseline unchanged at
`PASS-UNVERIFIED`. Survivors clustered in four operators: `expiry-past` (9), `author-machine` (9),
`evidence-unrelated` (3), `value-contradicts` (1).

### 2026-08-26T22:58Z · a hypothesis formed, then killed by checking

**First reading was wrong and is recorded rather than overwritten.** I proposed that the battery
"checks numbers and not prose", i.e. that survival tracked the value's *type* — string survives,
dict dies. `nl-004` and `nl-007` are dicts and survived, so the hypothesis was false.

Checking the actual values gave the real mechanism: survival tracks whether the value carries a
**bare measurement** the divergence gate can hunt for in evidence prose. A role (`"house_coordinator"`),
an identifier (`hospital: "1147"`), clock times (`06:00`), and a number embedded in an enum label
(`"donor_age_under_18"`) all fail to present one. **3 of 9 rows.**

*Found by running it, not by reading it — the same way the tuple-reversed diagnostic in Addendum A
was found.*

### 2026-08-26T23:00Z · attribution checked before claiming anything

Read all seven `*-UNCAUGHT.json` comments **after** the operators were written, never before.

- `expiry-past` → **fixture 16**, same mechanism, independently reproduced.
- `author-machine` → **fixture 17**, same mechanism, independently reproduced.
- `value-contradicts` → *related* to fixture 18, not identical: 18 is two rows contradicting each
  other; this is one row contradicting its own cited evidence.
- `evidence-unrelated` on measurement-free rows → **not among the seven.** The one new class.

**And the reverse, which matters more:** mutation did **not** find fixtures 14, 15, 19 or 20. No
operator here generates a silent partial install, a credentials repoint, a `__partial__` bypass, or
an adverse replay. **The hand method found four holes this search cannot.** Recorded because an
instrument that only reports its wins is an advertisement.

### 2026-08-26T23:02Z · results written

`RESULTS.md` banked with the score, the new hole class, the meta-finding (gate 13's hardening opened
the blind spot), the four stated limits, and the `[NULL]` verdict — the hand-written fixture set
loses narrowly, and its four exclusive findings are printed beside the loss.

**Owed, and not done here:** the two one-line gate fixes live in `gates/`, which is **Fork C's
partition**. They are described in `RESULTS.md` §What follows and deliberately left unwritten.
