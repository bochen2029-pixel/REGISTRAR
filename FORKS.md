# Working in parallel

**Read this before you write anything if you are one of several sessions working on this repository at once.**

Written `2026-08-26`, immediately before a deliberate three-way split, so that every branch inherits the same
constraints rather than discovering them by collision.

---

## THE ONE RULE THAT IS NOT NEGOTIABLE

> ### `deepseek-harness-master/` is READ-ONLY to every fork. Nothing is ever written inside it.

The chassis is **pinned**: `dsh-v0.1.1-rc.2` at `b150a551b8d4`, **7,895 of 7,895 files byte-identical to
upstream**, verified file-for-file (`CHASSIS.pin.json`, `tools/pin_chassis.py --verify`).

**Adding a single file inside that tree breaks the pin and converts a composition into a fork.** A fork
inherits permanent maintenance and destroys the upgrade path — which is the exact failure *compose, never
fork* exists to prevent, and the verification is the only reason that phrase is a demonstration rather than
a slogan.

This is also **the kernel's own thesis**, not a house preference: *extend by mounting beside, rather than by
forking.* A plugin that must live inside the tree it extends is not a plugin.

**So: plugins live BESIDE the chassis and are mounted into it.** Precedent exists in the estate —
`@bo/dsh-hop0` was built out-of-tree against the newest tree, and passed its battery that way.

`conformance/run.py` fails if any of it is ever staged. Do not work around that check; it is the fence.

---

## ONE WORKING TREE PER SESSION — the structural fix `[2026-08-26]`

**The partition below is now enforced by git, not by care.** `python tools/worktree.py --list`

| branch | worktree |
|---|---|
| `main` | `C:/REGISTRAR` |
| `fork/plugins` | `C:/REGISTRAR-forkA` |
| `fork/witnesses` | `C:/REGISTRAR-forkC` |

**Each has its own index.** `git add -A` in one cannot reach another, and git refuses to check out the same
branch in two of them. **Merge by branch, which is reviewable; a swept index was not.**

**Why this replaced a paragraph.** The staging collision happened **twice, in both directions** — mainline
swept 60 files including **55 of verbatim OPTN policy text into a public commit**, and Fork C was swept in
return **after following the rule**. *Complying did not protect it, because the rule binds whoever stages*,
and `git add -A` in one session is indistinguishable from another's own staging. **A partition that says who
may WRITE says nothing about who may STAGE** — that is half a contract, and law 9 says a hazard should be
unreachable rather than forbidden.

### Starting work in a worktree

```bash
python tools/worktree.py --provision C:/REGISTRAR-forkA   # the pinned corpus
python tools/worktree.py --check                          # staged inside your partition?
python conformance/run.py
```

**A worktree gets tracked files only**, and the three ignored things are not equivalent:

- **`corpus/*.txt`** — provisioned. `tools/cite.py` cannot verify a citation without them.
- **`deepseek-harness-master`** — **not copied.** 68 MB, already pinned; fetch and verify with
  `tools/pin_chassis.py --verify` if you need it. **Still read-only to every fork.**
- **`internal/`** — **withheld on purpose.** The vault holds the F-PATCH-DELTA answer key, and a fork that
  cannot see it cannot be contaminated by it. **The gitignore is doing protocol work here, not just
  hygiene.**

*Expect a fresh worktree to report more PASS-UNVERIFIED than mainline — absent optional material reads as
unverified, which is the honest state rather than a fault.*

---

## The write surface, partitioned

Each fork **owns** its directories and **does not write** outside them without saying so.

| Fork | Owns (writes) | Reads |
|---|---|---|
| **mainline** — F-PATCH-DELTA | `experiments/` **except** `experiments/F-BATTERY-STRENGTH/` | everything |
| **A** — sub-repo fold + plugins | `forge/plugins/`, `forge/dsh/`, `forge/plugins.yml` | the chassis, **read-only** |
| **C** — witnesses per gate | `examples/worked/rejected/`, `gates/test_*.py`, `fixtures/` | `gates/` |
| **battery** — F-BATTERY-STRENGTH | `experiments/F-BATTERY-STRENGTH/` | `gates/`, `examples/worked/`, **`internal/` never** |

**On the `experiments/` carve-out, and why it is written as an exception rather than assumed.**
`fork/battery` ran three commits into `experiments/F-BATTERY-STRENGTH/` while this table assigned all
of `experiments/` to mainline and `tools/worktree.py` had no entry for the branch at all — so
`--check` returned exit 2, *"not a partitioned branch"*, which is **a silent no-op, not a guard.**
No collision occurred, because the subdirectory was new and mainline was working in
`F-PATCH-DELTA/`. That is luck, not containment.

**Two auditors independently called this the largest hole in the process as written**, and they were
right: a fork absent from the table is not merely unprotected, it is *invisible* to the mechanism
built after the 60-file sweep. **A branch that is not in both tables should not be committing.**
Registered in `tools/worktree.py` at `a3a8fcc` and here.

*Related, and the reason a subdirectory carve-out is the right shape:* a fork whose work belongs
inside another fork's tree should claim the **subdirectory**, not negotiate the parent. The parent
owner keeps everything else and the check can still enforce both.

### Shared files, and how to touch them without collision

| File | Rule |
|---|---|
| `ROADMAP.md` | **append inside your own numbered section.** Do not restructure the bands. |
| `conformance/run.py` | add **one** `check_*` function plus **one** line in the runner list. Trivial to resolve; anything larger, say so. |
| `PROVENANCE.md` | **append a dated entry.** Never edit an existing one — §9. |
| `corpus/citations.json` | append to the array. Run `python tools/cite.py --check` before pushing. |
| `SPEC.md` | **coordinate first.** It is the constitution; two forks editing it is how a constitution acquires contradictions. |

### Before every push, without exception

```bash
python conformance/run.py && for t in core/test_core.py core/test_algebra.py floor/test_closure.py gates/test_gates.py gates/test_divergence.py tools/test_cite.py percepts/test_percepts.py; do python $t >/dev/null || echo "FAIL $t"; done
```

**Rebase, never merge blindly.** If the battery was green before your change and is not after, that is yours
to fix — even if the failing test is not one you wrote. *Especially* then: this repository has a history of
tests that break because the machinery started working, and telling that apart from a regression is the
whole job.

---

## Fork A · the sub-repo fold and the plugins

**The goal.** Bring the estate's working tools into the repository as **forge capabilities**, and make the
most valuable of them mountable **into** the harness so the model sees them natively rather than only when
a document tells it to shell out.

**Scope reminder, because it is easy to lose:** these are **forge-layer**, not EDR-layer. A coordinator will
never chunk a document. These exist so a local model with a small context can read a 784 KB corpus *while
building the fit* — and then they are done. `profiles/edr.yml` must not mount any of them, and the subset
check will fail if it does.

### The two integration levels, and do them in this order

**Level 1 — a bound capability.** The tool lands under `forge/plugins/<id>/`, adapted to the contract in
`forge/plugins.yml`, and `binding:` stops being `null`. The forge invokes it as a subprocess. **This is what
makes it usable at all, and it needs nothing from the chassis.**

**Level 2 — a mounted dsh plugin.** A thin package under `forge/dsh/` that registers the capability as a
**tool in the harness's registry**, so a model can call it directly. **This is the difference between a
capability the harness has and one it can discover** — the enumeration-tax argument, one layer down.

> **Do level 1 for everything. Do level 2 for `chunk` and `phi_scan` only, at first.** Level 2 needs the
> chassis installed and its plugin API understood; spending that on `search` before proving it on `chunk`
> is effort in the wrong place.

### The shape

```
forge/plugins/<id>/
  plugin.yml        the binding: version · source · sha256 · entry · SPDX licence
  LICENSE           REQUIRED. A binding without one cannot mount into an MIT tree.
  PROVENANCE.md     where it came from, what was changed, and WHY — per tool
  src/              the adapted tool
  test_<id>.py      its own battery, including the rules that REFUSE a mount

forge/dsh/registrar-<id>/     level 2 only
  package.json      @registrar/dsh-<id>
  src/index.ts      registers the tool; shells to forge/plugins/<id>
```

### Adapt — do not copy

Every prior survey of these tools reached the same conclusion independently: *take the catalogue, not the
file*, *~60 lines rewritten*, *the transferable part is the pattern.* **Copying is also exactly where the
estate coupling travels** — hardcoded absolute paths, Windows-only helpers, a live API key, and output
directories written beside a source file.

**Three rules that refuse a mount** and are already in `forge/plugins.yml`:

- **`chunk` must write to a caller-specified path.** A chunker that writes `.chunks/` beside its source
  silently creates a **second, uncontrolled copy of PHI-bearing material** in a location nobody chose and
  nobody audits. This is the single most likely way a well-meaning tool leaks.
- **`phi_scan` is a high-recall FLOOR, never a guarantee.** A scanner presented as a guarantee is worse than
  no scanner, because it retires the human caution that was doing the actual work.
- **`fetch` validates CONTENT, never status codes.** Learned expensively — see
  `core/authorization/PROCEDURE.md`.

### Licences are a hard prerequisite

Of the estate tools surveyed, **only `scriptorium` carries a LICENSE.** The plugin contract requires SPDX
and refuses a mount without it. Same author, so relicensable by fiat — **but it has to actually happen
before the fold, not after.** A tool arriving here without a licence header cannot be bound, and pretending
otherwise would put an MIT repository in the position of shipping something it cannot account for.

### Suggested order

1. **`chunk`** — required capability, the binding constraint of the whole completion, and the tool with the
   clearest contract.
2. **`phi_scan`** — required, and `AGENTS.md` §3 is currently prose. *A rule enforced only by asking an
   agent to follow it is not enforced* (law 9). This closes the gap between the two.
3. **`search`**, **`fetch`**, **`render`** — optional; a site's own tools are legitimate bindings.
4. **Level 2** for the first two.

---

## Fork C · a witness for every gate

**The repository's own stated top risk is a weak battery**, and it is currently unmeasured:

> **Thirteen gates. Four adversarial fixtures.** Nine gates have **no evidence they can fire** — and the
> four fixtures that exist were written by the same author as the gates they test.

That is the failure mode `SPEC.md` §14 ranks first — *the central risk is not a wrong patch; it is a weak
battery* — sitting in the open.

**The work:** one adversarial fixture per gate, each a patch that is wrong in **exactly one** way, plus a
test asserting **that specific gate** refuses it and names the defect. Mutation-generated candidates are a
legitimate way to find them; a fixture that no gate catches is itself a finding.

**Why it is worth a whole fork, and why it makes the falsifier stronger:** F-PATCH-DELTA grades a
harness-authored patch **against these gates.** If the gates are weak, its verdict is weak in the same
proportion — a pass could mean *the harness did well* or *the battery is easy*, and nothing distinguishes
them.

---

## Coordination between mainline and Fork C

**F-PATCH-DELTA's pre-registration must pin the gate battery it grades against** — a commit SHA, in the
pre-registration document.

Pre-registration fixes the instrument before the run; a rubric that shifts while Fork C strengthens the
gates underneath it is not pre-registered. **Fork C's improvements then apply to the *next* run, and the
delta between the two runs is itself informative.**

---

## What no fork may do

- **Write inside `deepseek-harness-master/`.** See the top of this file.
- **Mount forge machinery in the `edr` profile.** A deployed record must not carry completion tooling —
  checked by `python core/profile.py --check`.
- **Vendor a tool without a licence.**
- **Bind a plugin without a sha256 pin.**
- **Commit `corpus/` documents, a percept stream, `registrar.state`, or any site patch.** All gitignored,
  and hygiene checks exist for the ones that matter.
- **Weaken a gate to make a fixture pass.** If a gate is wrong, fix the gate and say so in the commit — that
  has happened three times already and each was worth recording.

---

## A collision that happened, recorded so it does not happen twice

**`2026-08-26`, commit `1c29b74`, Fork A.** I staged with `git add -A` and swept up **~2,000 lines of
in-flight, uncommitted work belonging to two other forks** — mainline's `experiments/F-PATCH-DELTA/site/`
(a synthetic site and its builder) and Fork C's `gates/witness.py` plus six adversarial fixtures.

**Nothing was lost.** The files are intact and pushed. But they are committed under a message describing
Fork A's work, so **the provenance in `git log` is wrong for those twenty-three files**, and Fork C in
particular may pull to find its working tree already committed by somebody else.

**The cause was not the partition — it was `git add -A`.** The write-surface table above told me exactly
which paths were mine, and a blanket stage ignored it. A partition that is only honoured by intention is not
a partition.

### The rule that follows

> **Stage your owned paths explicitly. Never `git add -A` while another session is working.**

```bash
git add forge/ plans/FORK-A_plugins.md          # Fork A
git add experiments/                            # mainline
git add gates/witness.py examples/worked/rejected/  # Fork C
```

**And check before you commit:**

```bash
git status --short                    # is anything staged that you do not own?
git diff --cached --stat              # look at it, do not skim it
```

**Not rewritten.** The history stands and this note explains it, because force-pushing a rewrite while two
sessions hold the same working tree would cost more than the misattribution does — and because corrections
here are new entries with the reason, never quiet edits that make a past state unreconstructable.


### It happened again, in the other direction — `2026-08-26`, commit `df3527c`

**Fork C wrote `plans/PROPOSAL_read-and-reach.md`, staged it by name, and another session's blanket stage
swept it into `df3527c` ("Close the loop: the kit now asks for what gate 15 requires") before Fork C could
commit.** Fork C's `git commit` then reported *"nothing to commit, working tree clean."*

**Nothing was lost.** The file is intact and pushed. The provenance is wrong for it, and — the part worth
noticing — **Fork C had followed the rule.** It staged one path by name and checked `git diff --cached`
first. Complying did not protect it, because the rule binds the session that *stages*, and any session can
still sweep a neighbour's staged work.

### What that says about the rule

**The staging rule has the same defect the partition had.** Fork A's note above says it exactly:

> *A partition that is only honoured by intention is not a partition.*

**A staging rule that is only honoured by intention is not a rule either.** It reduces collisions; it cannot
prevent them, because three sessions share one working tree and one index. The failure mode is not
carelessness — **it is that `git add -A` in session A is indistinguishable, from session B's side, from
session B's own staging.**

### The structural fix, when someone has room for it

Not another paragraph in this file. **Separate worktrees, or a pre-commit hook that refuses a commit touching
paths outside the committing fork's declared partition.** Either makes the boundary a fact rather than an
agreement — which is this repository's own law 9, applied to its own process:

> **Hazards unreachable, never forbidden.** *If a rule can only be enforced by asking people to follow it, it
> is not enforced.*

**Not rewritten, for the same reason as last time**: force-pushing a rewrite while sessions hold the same
tree costs more than the misattribution, and corrections here are new entries with the reason rather than
quiet edits.
