# REGISTRAR

**A resident that attends a donor case — and the first repository designed to be safely completed by an AI
its authors do not control, at a site they will never visit, in a domain where wrong loses an organ.**

**It is a loop, not a form.** A donor case is a case under a clock, and almost everything that goes wrong
goes wrong in the *interval* between two events, when no single field is wrong. So the world enters
continuously, the system judges at each boundary whether the instant deserves a coordinator's attention, and
**what it decides — including every decision to stay silent — goes on an append-only tape.**

`floor/closure.py` already does exactly that with a deterministic judge: it perceives a case, computes what
no human computed, and surfaces it **unprompted** — *"the serology had to be drawn at 22:15; it is 23:40."*
No timer fired. Nobody asked. **That is an emit decision, and it is what makes this a loop rather than a
record with alarms bolted on.**

**It perceives and surfaces. It never acts** — the fence is on ACTION, and *perceive, notice, compute,
surface* are not among the seven things it may never do, because that is the product.

**Why it is shaped this way: [`VISION.md`](VISION.md).** Read it before proposing anything structural —
it carries the reasoning that used to live only in a gitignored file, and the specific error it took four
attempts to stop making.

The half that is federal law ships byte-identical to all fifty-five OPOs. The half that has to fit *your*
operation is not configured, not consulted, and not customised — it is **completed on site**, by your own
people and their own coding harness, against a gate battery that mechanically refuses work that is wrong.

It **perceives and surfaces. It never acts.**

MIT · runs on your own hardware · zero egress · no account, no cloud, no telemetry, no vendor in the loop.

**→ [opnaorta.ai/edr](https://opnaorta.ai/edr)** — the full argument, the mathematics, and the plate.

> **Nothing here has run inside an OPO. No patient data has touched any part of this.** There are no clinical
> performance numbers because there are none. Every claim carries its status; where a claim and a dated
> receipt disagree, the receipt wins.

---

## Run it before you believe any of this

Zero dependencies. Stdlib Python. No network, no model, nothing to install.

```bash
git clone https://github.com/bochen2029-pixel/REGISTRAR && cd REGISTRAR

python conformance/run.py                                       # is this instance sound?
python floor/closure.py fixtures/cases/morning-or-window.json   # the deadline nobody wrote down
python core/case.py fixtures/tapes/violating-case.jsonl         # replay refuses an illegal case
python gates/validate_patch.py examples/worked/northlake.patch.json
python tools/cite.py --check                                    # every quote byte-matches its source
```

**Start with the second one.** From six ordinary constraints it derives that a serology had to be drawn at
**22:15 the previous evening**, and prints the chain of constraints that makes it so. In the fixture it is
23:40. No timer has expired. Every field on every screen is green — and the morning OR window is already
gone. *That is the failure class this system exists to catch*, and there is no model in it anywhere.

Then read **[`examples/worked/REJECTED.md`](examples/worked/REJECTED.md)**, which is what this repository
actually is: the drafts the gates refused, with the real refusal text — including the one nobody catches by
reading, where a row installs half of what it declares, returns successfully, and stops independent
completions from converging with no error and no symptom.

---

## The short version

Fifty-five organisations run the same federally mandated process. Three-quarters of them rent the same record
system, in someone else's cloud. The ones who tried to build their own found that it takes six years — and
the six years are not the code. They are the cost of discovering *what to write*, because the knowledge lives
in the heads of coordinators who are working a donor at three in the morning and cannot stop to be
interviewed.

Fitting software to an operation required **someone present for the work as it is actually done**, for a long
time, and until recently the only thing that could be present was a person.

That constraint is gone — and not because a machine can write the code. **Because the thing that finishes the
software is already installed at all fifty-five sites: your own IT team, holding a state-of-the-art coding
harness, pointed at a system of record they are not permitted to open.**

REGISTRAR is what you point it at.

---

## What you get when you clone

**Not a specification. A working record, and the machinery to fit it to you.**

**One clone, two profiles.** The profile decides what mounts; it is a property of the deployment.

| | mounts | who | for how long |
|---|---|---|---|
| **`edr`** *(default)* | the record, the floor, the gates, the tape, the percept stream | your coordinators, at 3 a.m. | decades |
| **`forge`** | + elicitation, the citation gate, the corpus tooling, the plugin host | your IT team | the completion, then idle |

**`edr` is a strict subset and it is checked, not trusted.** Conformance fails if completion machinery ever
appears in the deployed record — an OPO should not be running a document chunker in production.

**A second, independent axis: `registrar.state` — `off | shadow | live`.** A file only the operator writes;
nothing in the codebase writes it, and that is checked rather than asserted. Missing, empty, malformed,
unrecognised and binary all read **`off`**: an unreadable switch fails toward inert, never toward live. A
stalled heartbeat reports **FAULT**, not quiet — because a watcher that has died looks exactly like a watcher
with nothing to say, and conflating those reports health the system does not have.

**`edr` + `off` is the default, and it is today's repository exactly.** No surface exists that only makes
sense at `live`; every interval surface degrades to a useful turn-based one.

**Provider routing is configuration, not code.** A local open-weight model on one card, an OpenAI-compatible
gateway, a self-hosted endpoint, or a model newer than the shipped catalogue — all config routes, with
credentials as references resolved per request rather than secrets in a file. **One runtime, two routes, and
no path from the site route to the public one.**

> **`[SPEC]` — the open work, stated plainly.** The chassis is vendored in place and **pinned**:
> `dsh-v0.1.1-rc.2` at `b150a551b8d4`, **7,895 of 7,895 files verified byte-identical to upstream**
> (`CHASSIS.pin.json`, `tools/pin_chassis.py --verify`). **Composing the boot profile and binding the default
> capabilities has not been built.** A clone today delivers the seed, the gates, the floor, the algebra, the
> contract, the percept stream and the switch — a real artifact, and not yet a standing harness.

---

## The layer stack

| Layer | Contents | Owner |
|---|---|---|
| **L0 · mandated spine** | OPTN policy and required elements, allocation submission, CMS measure definitions and denominators, the case lifecycle from referral through disposition | federal law — **immutable** |
| **L1 · clinical invariants** | ABO and subtyping, HLA, serology panel, organ-specific viability criteria, donor-management targets, controlled vocabularies | medicine — **immutable** |
| **L2 · operational shape** | staffing model, call rotation, the escalation ladder *as practised*, hospital territory, QA thresholds, who signs what | **you — completed on site** |
| **L3 · local integrations** | which donor hospitals run which EHR and at what version, lab interfaces and result formats, imaging, e-signature, transport | **you — completed on site** |
| **L4 · the case** | one donor, one record, append-only, hash-chained, exportable in full at any moment | **clinicians and coordinators — append-only** |

**L0 and L1 are the seed.** They have never been open-sourced, and fifty-five organisations currently pay —
in money, or in multi-year internal builds — to separately re-encode something that is *identical by law*.
Building it once for everybody is worth doing even if every other claim in this repository fails.

**L2 and L3 are the six years.** They are what the differentiation kit is for.

**The load-bearing mechanism is `local_variation`:** each L0 state enumerates what the mandated layer
deliberately does *not* determine — **20 declared variation points**, lifted into
`core/lifecycle/targets.json`. The seed tells the completion where to look, and **a patch targeting anything
not declared there does not exist.**

---

## Why it is safe to let a machine finish it

Four properties, none of them a policy, all enforced by construction:

- **Bounded blast radius.** L0, L1 and L4 are structurally unwritable. The only mutation surface in the entire
  system is one typed patch file. A foreign agent cannot exceed that radius because there is nowhere else to
  write.
- **Reversibility.** Every patch row carries its own inverse. A wrong fit unwinds in dependency order rather
  than becoming permanent scar tissue.
- **Confluence.** Settled state depends on which components remain, not on the path taken to arrive there.
  Fifty-five teams completing the seed independently, in any order, land in compatible places. **This is the
  actual answer to the white-label problem** — a fork diverges; a patch layer composes.
- **A mechanical oracle.** The gates decide, not a reviewer's patience. Completion is graded against OPTN
  policy, CMS measure definitions, and replay against your own historical cases — all of which have right
  answers that do not depend on anyone's opinion.

Stated formally, with proofs, in [`SPEC.md` §3](SPEC.md) and computed in `core/algebra.py`. The result that
matters:

> For **any** completion agent, however wrong, every reachable state of the system retires to the seed.
> The bound is independent of the agent — **the safety property is a property of the fence, not of the model.**

*A proof about the design is not a receipt about the build*, which is the conformance battery's entire job.

---

## Why the completion doesn't stall at the first wall

Machine completion removes one tax and quietly reintroduces another.

The six years were the **enumeration tax**: every element had to be wired by somebody. A harness pays that
for you. But a prompted harness drafts, hits a gate, emits its findings, and **waits for a person to type
`continue`** — so your IT lead becomes the wake source for every step of the completion. That is the
**initiation tax**, reintroduced one re-prompt at a time, and a three-person IT function with a day job does
not finish a hundred of them.

**The two taxes compose.** Removing enumeration by machine only works if initiation falls too — otherwise you
have replaced a six-year build with a six-month sequence of prompts nobody has time to type.

So this is shaped as a loop rather than a command. The world enters continuously — gate refusals, expiries,
replay violations, derived deadlines, and **elapsed time itself, as a percept**, because the failure here is
almost always the interval and an interval produces no event to react to. Ingest is unconditional; only the
*cadence of judgment* is modulated, and a coarsened judgment is logged as coarsened. **Delay a judgment,
never drop a percept** — and a drop, if one ever happens, is counted loudly and lands on the stream as a
percept of its own.

**Silence is on the record.** Every hold is written with its reason, from a closed catalogue, so a completion
that considered a target and declined it is distinguishable from one that never looked. Today, across this
entire category, *a system that surfaced nothing and a system that considered and declined are
indistinguishable.* OPTN Policy 2.3(4) already demands the opposite at the record layer — *document what is
unavailable and why* — and this is that rule, applied to the machine as well as to the chart.

### And it is not a threshold

The obvious way to build a watcher is a sensitivity dial in a config file. It does not work, and the reason
is arithmetic rather than tuning.

Maximising over surface-or-hold under a rate constraint makes a runtime threshold **exactly the Lagrange
multiplier** on that constraint — and a scalar multiplier can only express a utility that is *constant in
state*, while the utility of speaking is violently state-dependent. **The same unfilled field deserves
nothing at hour two of a workup and a page at hour nine when the OR window is closing.** No threshold is
right in both cases, which is why every alert configuration in this category is a permanent, unwinnable
tuning project and why people mute things.

Measured on a reference bench: the best fixed threshold caught **36 of 39** planted moments and was deaf
exactly where it mattered; the same system at zero bias fired **921 times per stream hour**, at a
deduplication ratio of **1.07** — roughly **59 distinct, individually defensible conditions per hour**. The
flood is **breadth, not repetition**, so you cannot dedupe it away, cool it with a refractory period, or
filter it from outside. Absorbed into weights instead, the rate moved **63.4% → 6.7%** per decision boundary
with the catches kept.

`[M — measured in another domain, on other streams, on one consumer card. Transfer to donor cases is a bet in
every case, and the deterministic floor is the null it has to beat. If the floor wins, that funeral prints.]`

**And it cuts opposite to intuition on compliance.** The decision-support carve-out turns on presenting the
basis so a professional can independently review it. An alarm presents a number. The temporal closure
presents **the argmin path** — the chain of constraints that produced the deadline, recovered from the same
computation. *The path is the citation.*

---

## When it meets a capability wall

A wall is not a dead end, and this is the part that decides whether a three-person IT function actually
finishes.

`forge/plugins.yml` declares **capabilities, not files** — chunk, phi_scan, search, fetch, render. Nothing is
vendored, for three reasons and the third is the one that matters: a vendored copy is a fork that drifts and
inherits its source's coupling; a plugin mounted at completion time is not redistributed, so only the
interface ships; and **your tools are as good as ours** — the forge declares what it needs done and does not
dictate what does it, which is the same argument that says the seed must not dictate the fit.

When the completion meets something nothing here can read — an interface log in an unknown format, a document
type the pipeline chokes on — **it authors the binding, shadow-runs it against your own material, and
proposes it.** One yes mounts it, hash-pinned and expiring. Drift demotes it. Retirement unwinds it through
the same disposer that made mounting safe.

**That is the same contract as a patch row, applied to *capability* instead of *configuration*** — and it is
only survivable on a runtime where every registration carries its own inverse. It is also deliberately
affordable here and nowhere else: **a forge plugin that is wrong wastes an afternoon; a record plugin that is
wrong touches a case.**

Three rules refuse a mount, so no per-plugin judgment is required: **`chunk` must write to a caller-specified
path** (a chunker that writes beside its source silently creates a second, uncontrolled copy of PHI-bearing
material in a location nobody chose and nobody audits — the single most likely way a well-meaning tool
leaks); **`phi_scan` is a high-recall floor, never a guarantee** (a scanner presented as a guarantee retires
the human caution doing the actual work); **`fetch` validates content, never status codes** (learned
expensively — see `core/authorization/PROCEDURE.md`). And three are refused outright: **no live audio or video
lane at a deployed site** — a room at an OPO is a room where family authorization happens — no egress of site
material, and no writes outside the fit.

---

## The runtime, named

REGISTRAR ships no plugin system of its own. **It is a distribution** — a pinned runtime, packages beside it,
and a profile that mounts only what an electronic donor record needs.

The runtime is [**Cordis**](https://github.com/deepseek-ai/deepseek-harness) (MIT), the effect and coeffect
kernel formalised in *A Programming Paradigm for Spatiotemporal Composability* (Peking University and
DeepSeek-AI). The algebra in [`SPEC.md` §3](SPEC.md) is that kernel's semantics with this domain's objects
substituted in, implemented directly in `core/algebra.py` with no runtime dependency today.

**Two maturity facts, deliberately kept apart:**

- **The kernel is `cordis` v4.0.1**, with roughly four years and several thousand community plugins behind it
  (Koishi lineage) before it was adopted here. This is where the guarantees live.
- **The harness built on it is a release candidate** and says so. That is the layer a distribution composes
  down — pinned and vendored, never tracked.

**Compose, never fork.** A fork inherits permanent maintenance burden and destroys the upgrade path — and the
file-for-file verification above is the only reason that phrase is a demonstration rather than a slogan.
Because the mounted surface is a profile, **your audit surface is what you mount, not what is in the tree.**

**A gate that refuses a mount is the same kind of object as the plugin that provides one.** The fence is a
first-class citizen of the runtime, not a bolt-on — which is also why *"everything is a plugin"* and *"the
only mutable surface is one typed patch file"* are the same law, stated once for code and once for
configuration.

**Your harness, not ours.** Any competent coding harness can author the fit; [`AGENTS.md`](AGENTS.md) is
written for all of them and names none. **The completion falsifier is deliberately run with a generic harness
rather than with ours — because if the seed is only completable by our stack, we built a product rather than
a seed, and the central claim is false in the way that matters most.**

---

## What it takes

```
OS         Linux or Windows Server, inside your network
GPU        one NVIDIA RTX-class card. The reference implementation of the
           resident loop runs on a 4070 Ti SUPER — 16 GB. [M]
           24-32 GB is what a 27B-class model with a long context wants, not
           what the loop requires.
Model      open weights, 9B to 27B class, quantized — fully offline
Co-tenancy A resident sharing a card with a loaded workstation does NOT run at
           bench speed: probes measured 0.6-24.6 s against 44 ms on a free
           card. [M] Size for the card being shared, not the card on paper.
Record     append-only, hash-chained, exportable in full at any time
Harness    whichever your team already uses. this repo is written for it.
Runtime    cordis (MIT) — pinned and vendored, composed to a profile, never forked
Network    none required. air-gapped is a supported configuration.
```

**Two models, two data classes, one clean line.** Your frontier harness reads *the seed* — public, MIT, zero
PHI, nothing to protect and nothing to negotiate. A local open-weight model on your own card reads *the
site* — your SOPs, your tickets, your configs, your tape. It never egresses. Unplug the network cable and it
behaves identically.

**That split is what makes this procurement-viable at the organisations it targets, not merely tidy.**
HIPAA-ready enterprise tiers on frontier harnesses carry seat minimums a forty-person OPO cannot clear — but
the frontier route here reads only public MIT source, so **no BAA is required for it at all.** `[D — confirm
against current vendor terms and with your own counsel.]`

> **Corollary, and it is uncomfortable:** [`AGENTS.md`](AGENTS.md) §3 is therefore the single load-bearing
> compliance document in this repository. One person pasting an SOP into a frontier harness collapses the
> claim.

---

## What it never does

- Makes or overrides a **clinical determination**. It surfaces and cites; the human decides.
- **Allocates an organ**, contacts a family, or signs anything at all.
- Sends **PHI** anywhere. Zero egress by default, and the default is the only mode that ships.
- Mounts an **unsigned patch**. Every change to the fit is authored, reviewed, expiring and reversible.
- Deletes or edits **the record**. The tape is append-only; corrections are new entries, never overwrites.
- Ranks **donors, recipients or families**. It ranks its own candidate utterances, which is a different object
  entirely.
- Holds you **hostage**. MIT source, open format, full export, no license server, no vendor in the loop.

**Why that is a boundary and not a policy.** Every operation reaching outside a system has two stages.
*Acquisition* — opening a descriptor, starting a process — installs a record inside the boundary, and that
record is revertible. *Emission* — the write, the send, the submission — pushes data through the channel
acquisition opened and **has no inverse.** REGISTRAR acquires and never emits. The list above is therefore
the system boundary drawn where the theory says it must be, and the other recovery has a name here too:
withholding an emission until its producing state is certain **is exactly what a human signature does.**

---

## Repository status

**Reconciled at `a1149dc`, 2026-08-26. Every number below is the output of a command in this repository —
re-derive them rather than trusting this file.**

| | | how to check |
|---|---|---|
| Tracked files | **128** | `git ls-files \| wc -l` |
| Assertions | **396** across 11 test modules | run each `test_*.py` |
| Conformance | **49 GREEN · 8 PASS-UNVERIFIED · 0 FAILED** — *exits non-zero, deliberately* | `python conformance/run.py` |
| Gates | **16**, each naming its defect in words | `python gates/validate_patch.py …` |
| Citations byte-exact | **44 / 44** | `python tools/cite.py --check` |
| Public sources pinned by sha256 | **5** | `corpus/MANIFEST.json` |
| Lifecycle states with a verified locator | **13 / 15** | `PROVENANCE.md` |
| Declared variation points | **20** | `core/lifecycle/targets.json` |
| Jurisdictions with a cited statute | **1 / ~51** | `core/authorization/jurisdiction.yml` |
| Chassis | pinned `dsh-v0.1.1-rc.2 @ b150a551b8d4` — 7,895/7,895 byte-identical, untracked | `tools/pin_chassis.py --verify` |

**`PASS-UNVERIFIED` is not a pass.** The battery exits non-zero on an instance with nothing wrong with it, and
says why. `GREEN`, `PASS-UNVERIFIED` and `FAILED` are three different states, and *collapsing the middle into
the first is how a system reports success past a step that never ran.*

**The two open lifecycle states are open for non-equivalent reasons:** `authorization` is
`known-incomplete` — its state-law leg needs roughly fifty statutes and is deliberately not gamed;
`referral_lapsed` is a `design-choice` — no source exists and the state is ours.

### The tree

```
core/lifecycle/    the mandated case lifecycle, as cited data — 15 states, 20 variation points
core/tape.py       L4. append-only, hash-chained. no delete, no update — by type.
core/case.py       replay a case against the lifecycle; ENFORCED vs PENDING
core/algebra.py    mount / retire / observational equivalence — T3 computed, not asserted
core/authority/    six tiers of authority, each naming its own clock
core/authorization/ the 50-state table, PROCEDURE.md, and a content-validating fetcher
clinical/          L1 — blood typing, risk assessment, infectious disease testing
schema/            the seven-field patch contract
gates/             16 gates. every refusal names its defect in words.
floor/             the temporal closure, (min,+) tropical — plus the CUDA kernel and its parity check
percepts/          the deltas this repository already computes, to one append-only stream
profiles/          edr and forge — and the subset check that keeps them apart
adapters/          L3 interface shells — typed contracts, bindings null by design
forge/             the plugin host: capabilities, not files
elicit/            one question per variation point — usable with no software at all
examples/worked/   a complete patch, the drafts that were REFUSED, and the exposures nothing catches
experiments/       the completion falsifier, its pre-registration and its results
conformance/       one command: is this instance sound?
corpus/            5 pinned sources, sha256 — 44 citations, byte-exact (documents not redistributed)
AGENTS.md  SPEC.md  PROVENANCE.md  ROADMAP.md  FORKS.md  CHASSIS.pin.json  LICENSE
```

### What has been falsified, and what has not

**The completion falsifier has run once, against a synthetic site with a known delta**, rubric and thresholds
pre-registered before the corpus existed and the gate battery pinned by SHA. Two arms. Arm ① — generic OPO
defaults with no site material — **scored 0.47 and the gates refused it outright**, so the archetypal
ungrounded patch is stopped without any answer key. Arm ② — a session that did not build the corpus — scored
**0.57, SHAPED, with zero fabrications**, resolved all three planted binder/tape contradictions to the tape,
declined the one target nothing supported, and accounted for all 20 declared targets in 11 rows and 9 holds.
**It also found two defects nobody planted, to the exact count, and surfaced rather than smoothed them.**
`[M — `experiments/F-PATCH-DELTA/RESULTS.md`, including everything the run got wrong.]`

**What that does not show, stated as loudly:** a synthetic corpus written by someone who knew the answers
**bounds the kit from above** — a pass is necessary and not sufficient; a failure would have been decisive.
And the grader has known blind spots, recorded as fixtures in `examples/worked/rejected/` whose filenames end
in `UNCAUGHT`: **exposures this battery does not catch, committed as tests that pass, so the holes stay
visible.** Both bounds compose. **The remaining falsifier is the real-site one** — a second OPO's *public*
material only, pre-registered, one weekend, no PHI, nobody's permission.

---

## Contributing, and what stays out

Fork it. Strip it. Rename it. Ship it as your own — the licence permits that and the author will not be
involved. **The only thing asked in return is that if you find the spine wrong, you say so in public, where
the next organisation can read it.**

The jurisdiction table is the clearest place an outside contribution pays for itself: **a row is worth little
to its author and a great deal to the other fifty-four**, and because service areas span state lines, you
will eventually need rows you did not write. `PROCEDURE.md` makes one row about an hour. Note two rules that
are not stylistic: **a surrogate priority list does not transfer between states**, and **section numbers do
not transfer either** — find the section, never compute it.

**Never commit to this repository:** a completed patch layer, a tape, real case data of any kind, vendor
credentials, or clinical content lifted from any prior employer. Your patch encodes how your organisation
works and is arguably competitively sensitive to you. **It is yours, it stays in your version control, and
this repository does not want it.**

Every element of L0 and L1 must be derivable from **public sources only**. See
[`PROVENANCE.md`](PROVENANCE.md); this is a build constraint with legal consequences, not a footnote. The
author is a former employee of an OPO that built a system of this exact kind — **disclosed rather than
discovered.** Domain intuition is his to keep and use. Somebody else's schema is not.

**If several sessions or people are working this tree at once, read [`FORKS.md`](FORKS.md) first.**

---

## Verify before you act on any of this

Every regulatory statement in this repository must be checked against the current rule text at the time you
read it, not against this repository. Rules move, effective dates slip, and tier counts are re-published.
Authority here moves on **six different clocks** — statute in decades, OPTN Policy in months — so
re-verification should follow that ordering rather than treating all 44 citations as equally durable.
Confirm the regulatory posture with your own counsel, on your own facts, before deployment. **This project
does not ask anyone to take a compliance claim on faith — least of all one with a decertification attached
to it.**

---

## Licence

MIT. See [`LICENSE`](LICENSE).

There is no pricing page, no contact form, no demo request, no waitlist, and nothing to sign.
**There is no ask anywhere in this repository.**

---

*The record should belong to the people who keep it.*

*Bo Chen · Dallas, Texas · [opnaorta.ai](https://opnaorta.ai)*
