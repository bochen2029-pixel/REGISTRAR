# QC BRIEF · full-system quality check of REGISTRAR

**You are a fresh session with zero prior context, tasked with a comprehensive, adversarial, evidence-bound
quality check of everything in `C:\REGISTRAR` — the spec against itself, the work against the spec, the work
against the work, and the claims against the receipts.**

Written `2026-08-26` by the mainline session at the end of the build stretch this brief audits. **Start your
session in `C:\REGISTRAR`** so the project memory at `~/.claude/projects/C--REGISTRAR/memory/` loads — it
carries orientation, house laws, and the drift history.

---

## 0 · Ground rules — read these before touching anything

1. **QC is read-only.** You may create files ONLY under `C:\REGISTRAR\qc\` (make the directory) and your
   scratchpad. **Do not edit, fix, reformat, or "improve" anything else during the QC pass** — remediation is
   a report you write, not an action you take. The one exception: tiny repro scripts in your scratchpad.
2. **`deepseek-harness-master/` is READ-ONLY, absolutely.** It is a pinned third-party tree
   (`CHASSIS.pin.json`, 7,895/7,895 files byte-identical to upstream). Writing one byte inside it converts a
   composition into a fork. Verify the pin (`python tools/pin_chassis.py --check`); never touch the tree.
3. **Do not push, deploy, or publish anything.** No `git push`, no `wrangler`, no artifact publishing. Local
   report only; the operator decides what happens to it.
4. **Contamination notice:** `internal/f-patch-delta/DELTA.json` is the answer key to the completion
   falsifier. **Reading it is fine for QC and disqualifies this session from ever authoring an arm-② candidate
   patch.** Accept that trade; QC of the experiment requires seeing the whole instrument.
5. **Three sessions may exist as git worktrees** (`C:\REGISTRAR-forkA`, `-forkC`, branches `fork/plugins`,
   `fork/witnesses`). Work in the main worktree. If `git status` shows uncommitted work, **note it in the
   report and do not stage, stash, or clean it.**
6. **Match the house evidence discipline in your own report.** Every claim you make carries one of:
   `CONFIRMED` (you reproduced it — include the command and output) or `PLAUSIBLE` (you reasoned it — say
   what would confirm it). A QC report that asserts without receipts, about a repository whose entire thesis
   is receipts, refutes itself.

---

## 1 · The gist, so your reading has a frame

**REGISTRAR is an open-source electronic donor record (EDR) for the 55 U.S. organ procurement organisations
(OPOs) — built as a RESIDENT, not a form.** A donor case is a case under a clock; most failures live in the
*interval between events* when no single field is wrong. So the object is a loop: the world enters
continuously, a judge decides at each boundary whether the instant deserves a coordinator's attention, and
every decision — **including every decision to stay silent** — goes on an append-only tape.
`floor/closure.py` is that loop with the dumbest possible mind (a deterministic constraint closure), and it
is the `[NULL]` any trained resident must beat.

**The central bet is "completability":** the half that is federal law (L0) plus clinical invariants (L1)
ships identical everywhere; the half that fits one site (L2 operational shape + L3 integrations) is
**completed on site by an AI harness the authors never meet**, held safe by a mechanical gate battery, a
patch algebra with computable inverses, and a human signature at the seam. L4 is the case record itself —
humans only. **The fence is on ACTION, never on perception** (`SPEC.md` §8: the seven prohibitions are acts;
*perceive, notice, compute, surface* are the product).

**Claim grammar used everywhere, including on the public page:** `[M]` measured with receipt · `[V]`
verified, source named · `[D]` derived · `[SPEC]` designed, unbuilt · `[BET]` kill condition named ·
`[NULL]` the baseline to beat · `[OA]` operator-attested. **Three states, never two:** `GREEN ≠
PASS-UNVERIFIED ≠ FAILED`, and the middle one is *treated as failure*, not as a pass.

**State at time of writing:** 16 gates · conformance `50 GREEN · 9 PASS-UNVERIFIED · 0 FAILED` · 8 test
suites, ~280 assertions · 44 byte-exact citations against 5 sha256-pinned sources · 23 adversarial fixtures
(22 refused; the `-UNCAUGHT` ones are **deliberately retained open exposures, not bugs to fix**) · the
completion falsifier F-PATCH-DELTA has run against a **synthetic** site: arm ① floor `S=0.47` (1
fabrication), arm ② `S=0.57` (0 fabrications), both SHAPED — **a pass bounds the kit from above and says
nothing about a real OPO.**

---

## 2 · Read order (budget your context; the corpus texts are large — spot-check, never read whole)

**Phase A — the frame (read fully, in this order):**
1. `VISION.md` — why it is shaped this way; the perception/action fence
2. `README.md`
3. `SPEC.md` — the constitution: layers, algebra T1–T6, floor, fence, battery, §2b the loop
4. `ROADMAP.md` — the Poincaré-disk plan; what is DONE vs `[BET]` vs `[SPEC]`
5. `internal/FUSOR_AT_THE_CENTER_v1.0_REFOUNDING.md` — the re-founding **and the audit appended to it**
6. `internal/SPEC.internal.md` — the unsanitised strategy (gitignored; on this machine only)

**Phase B — the contracts:** `AGENTS.md` (esp. §3, §7b, §7c, §8) · `schema/patch.schema.json` ·
`PROVENANCE.md` (the correction log IS the culture) · `FORKS.md` · `plans/*.md` (the fork briefs and
`PROPOSAL_read-and-reach.md` with its OUTCOME).

**Phase C — the machinery (read code, not just docstrings):** `core/` (tape, case, algebra, lifecycle) ·
`floor/` · `gates/` (validate_patch + the five standalone gates + witness.py) · `percepts/` ·
`conformance/` (run.py, claims.py) · `tools/` (cite, pin_chassis, worktree) · `forge/plugins.yml` ·
`adapters/` · `profiles/`.

**Phase D — the experiment:** `experiments/F-PATCH-DELTA/` (README → PREREGISTRATION → RESULTS →
`site/` corpus → `fairbank.patch.yml` if present) and `internal/f-patch-delta/` (builder, extractor, key).

**Phase E — the surfaces:** `C:\NEW\REGISTRAR_ONE-PAGER_THE-TOTALITY_2026-08-26.md` ·
`C:\Websites\aorta-site\_upload\edr.html` (the live page's source) ·
`C:\NEW\REGISTRAR_SNAPSHOT_THE-WHOLE-MOMENT_2026-08-26_1304_v2_MAINLINE.md` (addenda A–F = the session log).

---

## 3 · Run order — establish ground truth before judging (expect ~2 min for the full battery)

```bash
cd /c/REGISTRAR
python conformance/run.py                                    # the battery (slow; be patient)
for t in core/test_core.py core/test_algebra.py floor/test_closure.py gates/test_gates.py \
         gates/test_divergence.py gates/test_witness.py tools/test_cite.py percepts/test_percepts.py; \
    do python $t | tail -1; done
python tools/cite.py --check
python tools/pin_chassis.py --check
python schema/validate.py --self
python conformance/claims.py --check
python conformance/claims.py --surface /c/Websites/aorta-site/_upload/edr.html
python conformance/claims.py --surface "/c/NEW/REGISTRAR_ONE-PAGER_THE-TOTALITY_2026-08-26.md"
python gates/validate_patch.py examples/worked/northlake.patch.json
python gates/validate_patch.py experiments/F-PATCH-DELTA/fairbank.patch.yml
python experiments/F-PATCH-DELTA/score.py experiments/F-PATCH-DELTA/candidate_arm1.json
python core/profile.py --check
python adapters/conformance.py ; python forge/conformance.py
git log --oneline -40 ; git worktree list ; git status
```

Record every deviation from the §1 state block. **A number that moved is either progress or drift — decide
which, with evidence.**

---

## 4 · The QC dimensions — all of them, ranked most- to least-load-bearing

1. **The spec against itself.** Is the algebra section internally coherent (T3's "pointwise ≃" vs what the
   gate actually computes; T4's bound and its dependence on the fixed target list; T5/T6 as types vs
   claims)? Do §2b (the loop), §8 (the fence), and the gate battery describe the same system? Does any
   later addition (holds, §7b/§7c, gates 14–16) contradict an earlier section that nobody re-read?
2. **The work against the spec.** For each SPEC/ROADMAP commitment: built, honest, and named where the spec
   says? (The re-founding audit at the bottom of the internal doc did this once; **re-verify it and extend
   it** — it found 4/12 drifted the first time.)
3. **The work against itself.** Duplicate/near-duplicate machinery (three YAML-null-trap handlers, three
   conformance-style checkers, two hold-key spellings, JSON vs YAML loaders); dead code; things asserted in
   one file and contradicted in another; encoding/CRLF/platform hacks vs the "runs cold on clone" claim —
   **would any of this actually run on Linux?**
4. **Gate quality.** The gates are the product. For each of the 16: can it fire (witness exists)? can it be
   fooled (author an evasion in your scratchpad and try)? does it cry wolf (false-positive surface —
   lexical lists in `attest.py`, exclude-regexes in `claims.py`)? The seven retained `-UNCAUGHT` exposures:
   still uncaught? still honestly labelled?
5. **The experiment's validity.** The pre-registration vs what actually happened (deviations are *recorded*
   — were any not?); the scorer's mechanics (`TOL=0.15`, key-matching crudeness, the admitted "scorer
   artifacts"); the rubric's incentive structure; corpus realism and its two recorded defects; whether
   "deterministic seed" survives Python-version changes to `random`.
6. **Claims vs receipts, everywhere.** Every `[M]` traceable? Every number on the page/one-pager either in
   `CLAIMS.json`'s reach or flagged as unreachable? Substrate numbers properly quarantined as
   `[M inherited]`? Anything stated as fact that is actually `[BET]`?
7. **Process and structure.** FORKS partition vs the actual commit history (forks committed to `main` all
   day; the branches were created at the very end — is the story coherent?); the worktree provisioning; the
   vault protocol's honest limits (the key IS in git history — verify the disclosure matches reality).
8. **Efficiency and simplification.** The battery's runtime (it now spawns many subprocesses — measure it);
   opportunities to consolidate checkers behind one shared library without weakening anything; anything
   over-engineered relative to its risk, or under-engineered relative to its load.

---

## 5 · Starting hypotheses — unverified suspicions from the author; confirm or refute BEFORE general sweep

Seeded deliberately, both to accelerate you and to calibrate the depth expected. **Each is a suspicion, not
a finding.**

- **H1 · The all-holds exploit (rubric).** A patch of zero rows and twenty holds appears to score +1 × 20 =
  `S = 0.50` with zero fabrications → verdict **SHAPED**, beating the 0.47 floor — while doing no work. It
  may also pass the gates (accountability GREEN by construction; most row-gates vacuous over zero rows).
  **If confirmed, the falsifier's SHAPED band is gameable by total abstention** and the rubric or thresholds
  need a documented fix (e.g., holds cap, or S computed over answered targets with a coverage floor).
- **H2 · `attest.py` lexical brittleness.** "formerly" fires on innocent renames ("formerly Northlake
  Regional"); negations ("not withdrawn") likely misread; `MANDATORY`/`PERMISSIVE` word lists are
  English-fragile. Estimate the false-positive surface on realistic prose.
- **H3 · The battery is slow enough to time out tooling** (>100 s observed). Profile where the time goes
  (nested subprocesses re-running suites?) and propose the cheapest 10× improvement that changes no verdict.
- **H4 · `claims.py` coverage gap.** The page's most important number (`S = 0.57`) is NOT in `CLAIMS.json`
  (the key lives in the gitignored vault) — so the claims gate cannot catch drift on the one number that
  matters most. Verify, and propose how to gate it without shipping the key.
- **H5 · Cross-platform truth of "zero dependencies, runs cold."** `pyyaml` is assumed in several checkers;
  `PYTHONIOENCODING` hacks; Windows path handling. Try the mental (or actual) Linux run.
- **H6 · Schema/holds drift.** `$holds` vs `holds`, `reason` vs `why`, `class` enum vs the arm-② candidate's
  actual fields, `patternProperties` interplay with `additionalProperties:false` — is there a combination
  that validates in `schema/validate.py` but violates the documented contract, or vice versa?

---

## 6 · What is ALREADY self-reported — re-reporting it scores zero

This repository records its own failures aggressively. The following are **known and documented**; your job
on these is only to verify the fix holds: the three greedy-matcher false positives and the deleted
target-drift check (funeral in `gates/attest.py`) · the claims-gate recursion/timeout and the "+1 fudge"
(`conformance/run.py`, commit log) · the staging collisions and worktree fix (`FORKS.md`) · the corpus
`_smoke/` leak and its gate · the hardware-claim correction (README, PROVENANCE) · the plate drift
(PROVENANCE `2026-08-26` entry) · the README loop demotion (re-founding audit) · the two synthetic-corpus
defects (RESULTS.md) · the `null:` YAML reserved-key trap (three sites) · T3 catching fixture authors twice.

**Novelty is the currency: a finding nobody has written down yet, with a receipt.**

---

## 7 · Deliverable

Write **`C:\REGISTRAR\qc\QC_REPORT_<date>.md`** (create `qc/`), structured exactly:

1. **Verdict page** — one screen: overall assessment in the repo's own three-state grammar, the five
   findings that matter most, and the single sentence you would put in front of the operator.
2. **Ground truth** — what you ran, what it returned, deltas from §1's state block.
3. **Findings** — ranked CRITICAL / HIGH / MEDIUM / LOW; each with: one-line claim · `CONFIRMED`/`PLAUSIBLE`
   · evidence (file:line, command, output) · why it matters in THIS domain (an organ, a false refusal, a
   silent pass) · smallest honest fix. **Separate section per QC dimension of §4, plus H1–H6 dispositions.**
4. **What is right** — brief, specific credit: the strongest three design decisions and the strongest three
   pieces of evidence discipline you found. (Calibration, not flattery — a QC that finds only faults in a
   repo this self-critical has mis-sampled.)
5. **Remediation plan** — ordered by leverage: for each accepted finding, the fix, the risk of the fix, the
   test that proves it, and a size estimate (S/M/L). Group into: *do before any real-site contact* / *do
   before the next fork wave* / *opportunistic*.
6. **Meta** — what you could not verify and why; what this QC's own blind spots are; whether the brief
   itself (this file) misled you anywhere — **QC the QC brief too.**

**Voice:** the house style names defects in words and never hedges a confirmed finding. Write like
`REJECTED.md`, not like an audit firm.

---

*One last framing, from the operator's own laws: the central risk is not a wrong patch — it is a weak
battery. You are the battery's battery. Act accordingly.*
