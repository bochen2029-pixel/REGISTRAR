# SESSION LOG

**Append-only. Newest entries at the bottom. Never edit an entry — corrections are new entries with the
reason, per `PROVENANCE.md` §9 and house law 14.**

## What this file is for

`PROVENANCE.md` records where an *element* came from. `logs/` records what a *session* did — every timestamped
act, what it verified before acting, what it found, what it declined to touch, and what it got wrong.

It exists because of a failure this project has already had four times in one day: **doctrine drifts back
under maintenance, and nothing was ever reverted deliberately.** A claim was true when written and stopped
being true while nobody was looking. `conformance/claims.py` now gates the *numbers*. Nothing gates a demoted
paragraph, a skipped docstring, or a check nobody pointed at a surface. **A dated log of what was actually
done is the cheapest instrument that makes those visible after the fact.**

It is tracked, not gitignored, for the same reason `VISION.md` was moved out of `internal/`: **a record that
does not survive a clone is not a record.**

## The entry format

Every entry carries: a **UTC-offset timestamp**, the **HEAD it started from**, the **worktree and branch**,
what was **verified before acting** (never recalled — run the command), what **changed**, what was
**deliberately not touched and why**, and **what it got wrong**. An entry with no *"got wrong"* line has
either had a very short session or is not being honest; say which.

---

## 2026-08-26 17:54:37 CDT · session `opus5-intake` · worktree `main` @ `bd89dd0`

**Operator instruction:** re-read `REGISTRAR_ONE-PAGER_THE-TOTALITY` and
`internal/FUSOR_AT_THE_CENTER_v1.0_REFOUNDING.md`, read the project memory, confirm alignment, then proceed
at my own recommendation and log everything durably with timestamps.

### Read before acting

`internal/FUSOR_AT_THE_CENTER_v1.0_REFOUNDING.md` (v1.0 + the late audit) · `VISION.md` · the four memory
files and their index · `ROADMAP.md` · `FORKS.md` · `AGENTS.md` · `README.md` · `conformance/run.py --verbose`
· `tools/worktree.py --list`.

### Alignment, stated so a later session can check whether I held it

**REGISTRAR is a resident that attends a donor case.** Not an EDR with a resident attached. `floor/closure.py`
already perceives a case, computes what no human computed, and surfaces it unprompted — that is an emit
decision with a deterministic judge. **The fence is on ACTION; `perceive, notice, compute, surface` are not
among the seven never-dos, and cannot be, because that is the product.** Three radii, one loop: the case, the
fit, the seed. The floor is the resident's `[NULL]` and must be beaten, not replaced.

### Verified before acting — run, not recalled

| Check | Result |
|---|---|
| `git rev-list --all --objects -- corpus/` | **0 corpus text objects in any reachable commit.** See finding 1. |
| `conformance/run.py` | 50 GREEN · 9 PASS-UNVERIFIED · 0 FAILED, exit 2 |
| `claims.py --surface` × 7 surfaces | 5 GREEN · 1 PASS-UNVERIFIED · **1 FAILED** — see finding 2 |
| `tools/worktree.py --list` | in `main`, which owns `core/`, `clinical/`, `floor/`, `experiments/` |

### Finding 1 — the corpus sweep never reached a commit `[VERIFIED]`

`registrar-orientation` records that `git add -A` swept 60 files across forks, *"55 of them verbatim OPTN
policy text into a public commit."* **That last clause is stronger than what the history shows.**

`git rev-list --all --objects -- corpus/` returns **zero** `.txt`/`.pdf`/`.html` objects reachable from any
ref, local or remote. Only `MANIFEST.json`, `README.md` and `citations.json` are tracked, which is the
intended state. **The sweep was caught at the index and never published.**

This matters because it is a redistribution question, not a tidiness one — OPTN policy text belongs to its
publisher and this repository's stated position is that it is never redistributed. **The public history is
clean, and nobody had checked.** Recorded here so the memory's phrasing does not harden into a belief that
there is a leak to remediate.

### Finding 2 — `ROADMAP.md` fails the claims gate, and had never been pointed at it `[FIXED, below]`

`conformance/claims.py` landed at `57a3c51` and reports `claims · public surface` as PASS-UNVERIFIED because
`REGISTRAR_SURFACE` is unset — so **the gate that exists to catch stale public claims was not checking any
surface.** Pointed at all seven, it found:

| Surface | Verdict |
|---|---|
| `README.md` · `AGENTS.md` · `edr.html` · the one-pager | GREEN |
| `VISION.md` · `SPEC.md` | PASS-UNVERIFIED — makes no claim in a readable form |
| **`ROADMAP.md`** | **FAILED — 3 stale** |

Genuine drift, each confirmed by reading the line rather than trusting the matcher:

- L23 `40 GREEN · 7 PASS-UNVERIFIED · 0 FAILED · 197 assertions` → **50 · 9 · 0 · 396**
- L27 `41 citations byte-exact` → **44**
- L32 `gates | **thirteen**` → **sixteen**

### Finding 3 — one of the four flags was the GATE being wrong `[FIXED]`

`claims.py` flagged `states_verified: surface says [2], repository says 13`. **The surface is correct and the
gate is wrong.** ROADMAP L265 reads *"the 2/15 states, which are open for non-equivalent reasons"* — a claim
that **2 of 15 are OPEN**, i.e. 13 verified. The matcher read `2/15` as a verified-count claim.

House law: *a gate that cries wolf is worse than no gate, because the next real alarm gets discounted*, and
*three of gate 13's first four findings were the gate being wrong, not the rows — each is now a test.*
**This is the fourth instance of that lesson, and the file itself already documents three.**

**Fixed rather than reported, and the reasoning is worth recording because I changed my mind mid-session.**
My first position was to report and not patch, on the grounds that `conformance/claims.py` belongs to another
session. Then I checked instead of assuming: `git status --short conformance/` was **clean** — that session's
work was committed at `57a3c51` and it is no longer in flight. The fix is **one `exclude` entry, in the
convention the file already established for exactly this failure**, which is the scale `FORKS.md` calls
trivial to resolve. Leaving a public surface permanently red so as to respect a boundary that was no longer
occupied would have traded a real defect for an imagined courtesy.

**Owed regardless: a test.** The exclude is currently protected by nothing but itself. Each of gate 13's
three matcher errors *became a test*; this one has not yet, and it should — `conformance/` has no test module
of its own, which is why it did not.

### Changed

| File | Change | Authority |
|---|---|---|
| `logs/SESSION-LOG.md` | new — this file | operator instruction |
| `ROADMAP.md` | three stale numbers corrected; two historical passages restated without their dead counts; a dated update appended to the top-ranked risk | it was FAILING a gate on a public surface |
| `core/tape.py` | docstring names it **the committed plane**, and names the two consequences that are easy to lose | re-founding §5, listed and never done |
| `floor/closure.py` | docstring names it **the null the resident must beat** — and *the first resident, with the dumbest possible mind* | re-founding §5, listed and never done |
| `conformance/claims.py` | one `exclude` entry + the reason as a comment | finding 3 — verified not in flight first |
| `conformance/CLAIMS.json` | regenerated via `--emit`; diff is the three lines of that exclude and nothing else | it is generated, never hand-edited |

The two docstrings are the audit's *"three that were never done"*, minus the third (`AGENTS.md` §7c) which
another session has since landed. The audit's reason for them stands: **an architecture nobody can find from
inside the file is an architecture that lives only in a spec.**

### Deliberately not touched

- **`SPEC.md`** — `FORKS.md`: *coordinate first. It is the constitution and two forks editing it is how a
  constitution acquires contradictions.* It also reports PASS-UNVERIFIED to the claims gate, meaning it
  phrases its numbers in a form the scanner cannot read. **Not a pass. Owed, by whoever owns the constitution.**
- **`forge/`, `examples/worked/rejected/`, `gates/`** — Forks A and C, separate worktrees and separate indexes.
- **The seven `UNCAUGHT` exposures** — Fork C's, and the next move on them is named in the ROADMAP update
  rather than taken here: *a well-formed variant of each. If one passes clean, that is the highest-priority
  gate in the project, identified by measurement rather than intuition.*
- **`corpus/citations.json`'s cp1252 read bug** — real (a bare `json.load()` fails on Windows in a file
  strangers will open) but not urgent. Carried forward, third session running.

### Result

All five surfaces that make machine-readable claims are **GREEN**. Battery **50 GREEN · 9 PASS-UNVERIFIED ·
0 FAILED**, unchanged. All 11 test modules pass. `floor/closure.py` still derives 22:15 and `core.tape`
imports clean.

### What I got wrong

**Three things, and two of them happened during the fix itself, which is the more useful half.**

**1 · My own correction block introduced a fresh stale claim.** Appending the dated update to *What would
kill it*, I quoted the superseded state — *"eight gates with no evidence they can fire"* — and the claims gate
immediately flagged `gates: surface says [8]`. **A drift-fix that introduces drift, caught within ten minutes
by the gate it was written to satisfy.** Rewritten to describe the change without restating the dead number.

The general lesson is sharper than the incident: **this project's correction law and its claims gate are in
direct tension.** *Corrections are new entries with the reason, never a quiet edit* — but a preserved
superseded number is, to a numeric scanner, indistinguishable from a live wrong one. **The resolution is that
a correction may preserve the reasoning without restating the count**; git holds the exact prior text, so
nothing becomes unreconstructable.

**2 · My first exclude regex required a literal space and shipped fixing nothing.** The phrasing it targeted
wrapped across a line break — `the 2/15\nstates, which are open` — so ` states` never matched, the exclude
did nothing, and the surface stayed red. **I found it by re-running, not by reading.** Corrected to `\s+`, and
the reason is now a comment in the file so the next person does not re-derive it. *When code reads correctly
and behaves impossibly, look at the bytes* — the house law already covers this and I did not apply it until
after the fact.

**3 · I attributed a documented regression to myself and was corrected.** The re-founding audit names commit
`69dbcd3` (mine, earlier today) for demoting the loop from the README's opening. I read that and reported it
as my regression. The operator corrected it: **the EDR-first framing predates that commit** — the prior README
opened *"The open-source electronic donor record — built as a resident, not a form"*. What `69dbcd3` actually
did was **preserve an existing drift and move the loop paragraph further down**, which is a smaller and
different error than introducing it.

**The useful part is not the attribution, it is the mechanism**: I had `FUSOR_AT_THE_CENTER` in context when I
rewrote that file and still did not restore the loop to the opening, because I was optimising the first screen
for a GitHub visitor and the re-founding was not what I was checking against. *That is exactly how doctrine
drifts back under maintenance* — not by disagreement, but by optimising for something else while the
constitution sits unconsulted. `registrar-doctrine-drifts` says to re-read the re-founding after any commit
whose message contains *reconcile*. Mine did. **That rule would have caught this and I would not have needed
the operator to.**

---

## 2026-08-26 18:0x CDT · session `opus5-intake` · worktree `main` @ `bd89dd0`

### CORRECTION — Finding 1 above is WRONG, and the error was mine `[house law 14: new entry, with the reason]`

**Finding 1 concluded "the public history is clean." It is not.** I scoped the check to `corpus/` and
reported the absence of a leak there as the absence of a leak. **The corpus text reached the public history
by a different path, and I would have found it by checking for the content rather than the directory.**

*The check I ran was `git rev-list --all --objects -- corpus/`. The check I should have run does not name a
path at all.* This is the same class as the leak detector whose regex matched `js` inside `.json`, and the
same class as the `curl 200` reported as "it fetches" — **a narrow probe reported as a general result.** It
is recorded here rather than edited above because the wrong conclusion is the evidence.

### Finding 4 — ~787 KB of verbatim OPTN Policy text is in the PUBLISHED history `[VERIFIED · UNRESOLVED · OPERATOR DECISION]`

| | |
|---|---|
| What | The pinned OPTN Policies document, chunked, as `chunk` plugin smoke-test output |
| Where | `forge/plugins/chunk/_smoke/` (38 files) and `_smoke2/` (17 more) — **55 deleted paths** |
| Size | **786,565 bytes** across the `_smoke/` set alone; `_smoke2/` is additional |
| Introduced | `41c8ff1` — **confirmed an ancestor of `origin/main`** |
| Deleted | `019f71a` *"Remove redistributed OPTN text; make the rule a gate"*, 16:03:53 -0500 |
| Still reachable | **YES.** `git show 019f71a~1:forge/plugins/chunk/_smoke/chunk-020.md` returns verbatim policy text from any clone. |

**Deleting a file in a later commit does not remove it from history.** A stranger who clones the public
repository can retrieve the whole document today. Retrieval was performed to confirm it, not inferred.

**And the hygiene gate reports GREEN over it:** `hygiene · corpus not redistributed .... only the manifest
and the citations are committed`. **That is true of the working tree and false of the artifact.** A gate
GREEN on a property the published thing does not have is precisely *reporting success past a step that never
ran* — this project's own first law — occurring inside its own battery.

**Not acted on, deliberately.** The fix is a history rewrite plus a force-push: destructive, outward-facing,
with three worktrees holding branches, and **GitHub retains unreachable objects after a force-push** so it
additionally requires a support request or a delete-and-recreate. `FORKS.md` twice declined to rewrite
history for *misattribution*; **this is redistribution of a third party's document, which is a different
severity**, and the decision is the operator's alone. Options and tradeoffs delivered in chat.

**Owed regardless of what is decided:** the hygiene gate should check **history, not just the working tree**,
or it will keep reporting GREEN over this. That is a real check, it is cheap, and it belongs to whoever owns
`conformance/`.

### Finding 5 — Fork A: what it finished, and where it actually is `[VERIFIED]`

**Nothing is stranded.** `fork/plugins` is **0 commits ahead, 3 behind** `main` — Fork A's work is fully
absorbed. Its two commits (`94b8ed5` chunk, `5042bd6` phi_scan) are ancestors of both branches.

**Done — level 1, both required capabilities**, each with `LICENSE`, `PROVENANCE.md`, `src/`, and a battery:
chunk (42 assertions) and phi_scan (48). `forge/test_conformance.py` proves the refusing rules fire
(26 passed). Its definition-of-done is met **except level 2**.

**Not done:** `forge/dsh/` **does not exist** — level 2 is at zero, and it was the plan's headline claim
(*the difference between a capability the harness has and one it can discover*). Five bindings remain `null`:
`search`, `fetch`, `render` (optional in the plan) plus `read` and `reach` (declared later at `71a10f2`,
after Fork A's plan was written, so they were never in its scope).

### Changed this entry

`logs/SESSION-LOG.md` only. No code, no history, no push.

---
