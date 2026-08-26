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

---

### 2026-08-26T23:10Z · plan written before execution

`PLAN_attribution.md`. Question: how much of `S = 0.57` rests on rows the battery can mechanically
check. **Thresholds and all three interpretations fixed before any number existed**, plus one
additional check named in advance — *if the ungrounded arm draws more of its score from blind rows
than the grounded arm, the blind class is where a confident-but-baseless prior hides.*

Protocol decided explicitly: the answer key does **not** enter this worktree. The withholding rule
protects candidate *authorship*; this audit authors nothing. Arm 2's scores were read from the
vault's existing `RESULT_2-site-corpus.json` through a scratch copy outside every git tree, because
`score.py` writes a `RESULT_*.json` and running it in main's tree would drop a file in another
session's partition.

### 2026-08-26T23:06Z · first run — and the instrument was contaminated

Reported arm 1 at **M = 1.00**. Wrong, and wrong in the flattering direction.

Axis A asked *did any gate FAIL after destroying this row's evidence?* **Arm 1 fails four gates
before any mutation** — evidence binding, shadow run, divergence, schema conformance — so every
arm-1 mutant was trivially killed and the ungrounded prior appeared perfectly gate-covered.

Verified rather than assumed: `arm1 baseline worst=FAILED`, `arm2 baseline worst=PASS-UNVERIFIED,
FAILED gates: none`. **Arm 2's number was valid all along; arm 1's was an artifact.**

### 2026-08-26T23:12Z · corrected, and the pre-registered check fired

Axis A is now a **delta** — CHECKABLE only if destroying the evidence introduces a failure the
baseline did not already carry. Well-posed whether or not the patch passes.

**arm 1 M = 0.20 · arm 2 M = 0.64.** PLAN §3 verdict at 0.64: **MIXED — the claim is partial and
must say so.**

**And §3's additional check fired.** The arm that read no site material earned **80 %** of its points
on rows the gates cannot tie to evidence; the grounded arm, 36 %. **The blind class is where the
ungrounded prior lives.** Arm 1 was still refused — but on structural tells, denominators and weasel
words, not on its assertions being unsupported. *A completion that supplied denominators and dropped
the weasel phrasing keeps 80 % of that score with nothing behind it.*

### 2026-08-26T23:14Z · one metric retracted, not deleted

`attribute.py` prints a per-bucket delta of **−83 %**, which is meaningless: arm 1 has zero declines
and arm 2 has nine, so the arms are not comparable bucket-by-bucket and the denominator changes
sign. **Left in the tool with the retraction printed beside it** rather than quietly removed — a
number that cannot be computed should be visibly refused, not absent.

### 2026-08-26T23:15Z · banked

`ATTRIBUTION.md`. Also recorded: **the composition of arm 2's win is not what the plate implies** —
+9 from declines, −11 on checkable rows, +1 from the fabrication it did not commit. *Arm 2 beat the
prior primarily by knowing what it did not know*, which is a real property and a different claim
from *the corpus let it author better values.*
