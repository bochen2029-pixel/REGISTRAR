# REGISTRAR — SPECIFICATION · v0.1

**2026-08-25 · STATUS: SPECIFICATION, PRE-BUILD.** Nothing described here has run inside an OPO. No patient
data has touched any part of it.

**Claim grammar.** Every assertion in this document carries its status, and the tags are load-bearing:

| Tag | Meaning |
|---|---|
| `[M]` | measured, with a dated receipt |
| `[V]` | externally verified, source named |
| `[D]` | derived, chain shown |
| `[SPEC]` | designed, unbuilt |
| `[BET]` | unproven, kill condition named |
| `[NULL]` | the cheap baseline this must beat |
| `[BUDGET]` | a target, not a measurement |

**A number without its grain, denominator and source is not a number. Funerals print.** Where this document
and a dated receipt ever disagree, the receipt wins.

Companion: **[opnaorta.ai/edr](https://opnaorta.ai/edr)**.

---

## §0 · What is being built

**A resident that attends a donor case — and, at a second radius, one that attends its own fit.**

An electronic donor record is a case under a clock. The world enters it continuously: referrals, labs,
transitions, timers, the passage of time itself. **Almost everything that goes wrong in this domain goes
wrong in the interval between two events, and no field is wrong when it does.**

So the object here is a **loop**, not a form. The world enters; at each boundary the system judges whether
this instant deserves a coordinator's attention; and what it decides — including every decision to stay
silent — goes on an append-only tape. **§2b states the loop, its three planes, and its three radii.**

**The system ships in two halves.**

**The seed (L0/L1)** is federal law and clinical invariant. It ships byte-identical to every OPO, because
there is exactly one legal answer to what it contains.

**The fit (L2/L3)** is everything that differs between organisations. It is authored **on site, by the site**,
using the site's own material — against a gate battery that mechanically refuses work that is wrong, and
mounted only under a human signature.

The organising insight is that generality and specificity are both *static* properties of an artifact, and
they are the wrong axis. The property that matters is **completability** — how much correct work a competent
outside intelligence can add, per unit of effort, without breaking anything. That is not a property of the
artifact alone; it is a property of the artifact **plus the intelligence receiving it** — and that second term
went from nothing to uniformly installed at every site. `[D]`

**The seed does not need to be complete. It needs to be completable, and completability is engineerable.**

---

## §1 · The layer stack

| Layer | Contents | Owner | Mutability |
|---|---|---|---|
| **L0 · mandated spine** | OPTN policy and required data elements, allocation submission structure, CMS measure definitions and their denominators, and the case lifecycle: referral → triage and eligibility → authorisation → donor management → allocation → recovery → packaging and transport → disposition and reporting | federal law | **immutable** |
| **L1 · clinical invariants** | ABO and subtyping, HLA, the serology panel, organ-specific viability criteria, standard donor-management targets, OPTN-defined vocabularies and code sets | medicine | **immutable** |
| **L2 · operational shape** | staffing model, in-house versus contracted coordinators, call rotation and the escalation ladder as practised rather than as written, hospital-development territory, on-site versus remote workup, internal QA thresholds, who signs what, what runs in parallel | the site | **completed on site** |
| **L3 · local integrations** | which donor hospitals run which EHR and at what version, reference-lab interfaces and result formats, imaging and PACS, e-signature, transport and perfusion, allocation credentials, identity provider | the site | **completed on site** |
| **L4 · the case** | one donor, one record, append-only, hash-chained, exportable in full at any moment without asking permission | clinicians and coordinators | **append-only** |

Two consequences worth stating plainly:

- **L0 has never been open-sourced.** Fifty-five organisations pay separately — in money or in multi-year
  internal builds — to re-encode something identical by law. That is deadweight loss that only an open
  artifact removes. Building the seed is worth doing **even if everything else in this document fails.**
- **The seed must be useful with an empty patch file.** A real state machine, real validators, and the site's
  own CMS-shaped numbers computed from its own tape on day one. That property is what makes everything above
  it optional rather than load-bearing. `[SPEC]`

---

## §2 · The patch contract

All site adaptation lives in one typed file, `<site>.patch.yml`, in the **site's own** version control. Every
row must carry all of the following, or it does not validate:

| Field | Rule |
|---|---|
| `target` | a row id in L2 or L3. **A target in L0, L1 or L4 fails the blast-radius gate.** |
| `value` | the change |
| `inverse` | the row's inverse. **Mandatory** — see §3; without it the row is not a well-formed element and cannot be mounted at all. |
| `evidence` | a pointer into the site's own material: which SOP, which ticket, which interface config, which span of tape |
| `shadow_run` | a replay against the site's historical cases, with counts at both grains |
| `expiry` | a date. Rows re-earn their place; **nothing is permanent by default.** |
| `author` | a named human. The signature is on the tape, forever. |

**Drift demotes. Retirement unwinds through the inverse, in reverse dependency order** — and §3 shows why that
order is forced rather than chosen.

---

## §2b · The loop — three planes, three radii, and the dial that cannot be set

This is the architecture. The layer stack says what the parts are; this says what the system *does*.

### The three planes

**COMMITTED** — `core/tape.py`. Append-only, hash-chained, owned. Every judgment, every hold, every
surfacing, every margin. **Every view in this system is a deterministic fold over it.** Built.

**FORMING** — candidate surfacings and candidate rows, speculative and abortable, **never persisted**. A
surfacing killed mid-formation when a lab result contradicts it dies here, and the fact that it was
considered and killed goes on the tape. `[SPEC]`

**FELT** — the disposition: how readily this instance speaks, as a property of its weights rather than a
config value. Coefficients on the tape; **never a percept.** `[SPEC]`

**Only commits kill.** Forming evidence may pause a judgment; only a commit ends one.

### Two laws the plane structure implies, and one that had to be learned

**Silence is world, not absence.** Elapsed time enters as a percept — a scalar tick — rather than as a
question waiting to be answered. **In this domain that is not a refinement, it is the main case**: the
failure is almost always the interval, and an interval produces no event to react to. A system that only
perceives events is structurally blind to the thing that most often goes wrong.

**Ingest is unconditional; only judgment cadence is modulated.** Pacing may delay the system's next
utterance. **It must never delay a percept.** And where a queue can overflow, the loss is *counted loudly* —
a silently dropped percept is the turn reborn inside the loop, and it is worse than a turn because nobody
can see it. `[D — from the reference implementation's own doctrine, 2026-08-12]`

**Events and suppressions are added, never conflated.** A surfacing that was considered and withheld is
recorded as such, and a total is `surfaced + suppressed` **by addition**. The reference implementation
carries this note against a bug it already found: the two were once double-logged, and the count lied in the
flattering direction until somebody added them separately.

### The loop

The world enters token by token, unconditionally. **Nothing is re-read, because nothing is ever put down** —
a donor case runs twelve to thirty-six hours, and a turn-based system re-assembles that entire history on
every interaction. At each boundary the system judges: **surface, or stay silent.**

**And silence is written down.** A hold goes on the tape with its margin. Today an EDR that surfaced nothing
is indistinguishable from an EDR that considered a case and declined — and OPTN Policy 2.3(4) already
demands the opposite at the record layer: *document what is unavailable and why.* This applies the same rule
to judgment.

### Three radii, one shape

| Radius | What enters | The judgment | The seam |
|---|---|---|---|
| **the case** | labs, transitions, timers, elapsed time | does this instant deserve attention? | the board — **nothing acts** |
| **the fit** | SOPs, tickets, gate refusals, drift | is there enough here to propose a row? | the gates, and a signature |
| **the seed** | findings across sites | is this a variation point the seed should declare? | upstream, human-authored |

**The same loop three times.** The algebra of §3 is the seam at radius 2; the gates of §4 are its
enforcement; the closure of §6 is the deterministic judge at radius 1.

### The dial cannot be set — and this is the argument

**Alert fatigue is the most documented failure in clinical software.** Every records system has it.
Coordinators mute alarms because there are too many and the one that mattered is in the pile. It is
universally treated as a tuning problem.

**It is not a tuning problem, and there is a measurement.** `[M inherited — measured on another domain's
streams; the transfer to this one is a bet]`

> The best fixed threshold caught **36 of 39** planted moments and was **deaf exactly where it mattered**.
> The same system at zero bias fired **921 times per stream hour**. There is no setting between them.

The reason is structural. Maximising expected value over a sequence of surface-or-hold actions under a rate
constraint makes a runtime threshold **exactly the Lagrange multiplier** on that constraint — and a scalar
multiplier can only express a utility that is *constant in state*. **The utility of speaking is violently
state-dependent.** The same unfilled field deserves nothing at hour two of a workup and a page at hour nine
when the OR window is closing.

**So no threshold is right in both cases, and no configuration project ever finishes.**

One decomposition kills the obvious patch: at zero bias the deduplication ratio was **1.07** — the flood is
not one condition repeating, it is **breadth**, roughly 59 distinct individually-defensible conditions per
hour. **You cannot dedupe out of that, cool it with a refractory period, or rank it away with a filter
outside the loop.** What must be decided is whether *this instant, given everything currently held*, deserves
a word. **That is a judgment, and judgments live in weights.**

Absorbed into weights rather than wrapped around: **63.4% → 6.7% per decision boundary, ≈9.5×, catches
kept.** `[M inherited]` `[BET — kill condition: if the deterministic floor of §6 catches nearly everything a
trained disposition would, the disposition is theatre and the funeral prints.]`

### The fence is on action, never on perception

**The resident perceives the case and surfaces. It never acts on it.**

That is §8 unchanged, with its mechanism named. And note which direction it cuts: **a resident satisfies the
decision-support carve-out better than a threshold alarm does.** The carve-out turns on presenting the basis
so a professional can independently review it. An alarm presents a number. **The closure presents the argmin
path — the chain of constraints that produced the deadline, recovered from the same computation that
produced it** — and the hold record adds what was considered and declined.

### The floor is the null

`floor/` and `gates/` must pass their full battery **with every learned component disabled**, or the release
does not ship. **The resident must beat the floor or it does not ship either.** No organ outlives its null.

### The switch

`registrar.state` — **`off` | `shadow` | `live`** — a file only the operator writes.

**`off` is the default and it is exactly today's repository**: the seed, the gates, the floor, turn-based
completion. **`shadow`** renders what the resident would have surfaced beside what actually happened, with
nothing reaching anyone. **`live`** means it surfaces — never that it acts.

**No surface may exist that only makes sense at `live`.** Every interval surface degrades to a useful
turn-based surface, or it does not belong here. `[SPEC]`

---

## §3 · The algebra of the fit

The claims in §1 and §2 — that the seed can ship identical, that independent completions land compatible, that
a wrong fit unwinds rather than scarring, that no machine reaches L0 — are one short algebra. It is written
down here because a claim you can compute is a claim somebody else can check.

### Objects

```
Σ  = { σ₀ }            the seed: L0 ⊕ L1, a SINGLETON — L0 is law, so there is exactly one legal seed
Λ                       the fit: L2 ⊕ L3 — the only mutable space in the system
K  = E*                 the record: the free monoid on entries. append is the only arrow.
∂Λ = Λ × (Λ → Λ)        the fit context: (λ, ρ) — the mounted fit, and the RETRACTION
```

The retraction `ρ` is the composite of the inverses of every row mounted so far. The initial context is
`(λ₀, id)`, where `λ₀` is the seed with an empty patch file — **the unit of the algebra is the shipping
artifact.**

Because Σ is a point, an instance `Σ × Λ × K ≅ Λ × K`. **The seed contributes no degrees of freedom.**

`K` is not a state space. There is no `delete` and no `update` — **not forbidden, absent from the signature.**
A correction is a new entry.

### Operations

```
mount(p, p⁻) : (λ, ρ) ↦ ( p(λ), ρ ∘ p⁻ )
retire       : (λ, ρ) ↦ ( ρ(λ), id )
```

A patch row is a **pair** — a change and its inverse. Without `p⁻` the pair is not an element of the monoid
and `mount` is undefined. **The inverse is required by the algebra, not by a policy somebody could relax
under deadline.**

### A note on `=`

Throughout this section, an equality between contexts is **observational equivalence**, written `≃`: two
states are related when no observer can distinguish them.

This is not a hedge, and it is not a weakening. The strict form is unattainable in any real runtime — freeing
a block does not restore the heap's prior layout, and a discarded generative name is not the one the next
allocation draws. Observational equivalence is the established notion of program equivalence, and for a
configuration layer it is also the *correct* notion: what matters is that nothing downstream can tell the
difference, not that the bytes match.

### Theorems

**T1 · the lift projects.**
```
pr₁ ∘ mount(p, p⁻) = p ∘ pr₁
```
The fit you inspect is the fit that is mounted; the bookkeeping cannot drift from the artifact.

**T2 · mounting is a monoid homomorphism.**
```
mount( (p₁,p₁⁻) · (p₂,p₂⁻) ) = mount(p₁,p₁⁻) ∘ mount(p₂,p₂⁻)

where   (p₁,p₁⁻) · (p₂,p₂⁻) = ( p₁ ∘ p₂ ,  p₂⁻ ∘ p₁⁻ )        ← the twisted product
```
*Proof.* Apply the right-hand side to `(λ, ρ)`. The inner mount gives `(p₂(λ), ρ ∘ p₂⁻)`; the outer then gives
`(p₁(p₂(λ)), ρ ∘ p₂⁻ ∘ p₁⁻)`, which is the left-hand side by definition. ∎

**This is the theorem that carries the white-label argument.** A *sequence* of patch rows is itself a single
patch row, and composition is associative — so the order in which independent rows are authored does not
change the mounted fit. Fifty-five teams completing the seed separately, in any order, land in compatible
places. And the *twist* — inverses composing in reverse — is the formal reason retirement must unwind in
reverse dependency order. The algebra forces it; no implementation gets a vote.

**The preconditions, stated rather than assumed.** T2 is associativity, and it gives order-independence for a
*given set* of rows. Lifting that to the full runtime claim — two completions of the same row set settling
into equivalent states — carries four hypotheses, and they are load-bearing:

1. **Quiescence.** Both settle; the claim is about settled states, not states mid-flight.
2. **Acyclic dependencies** among rows.
3. **The same set of operations.** Different row sets are not claimed to converge, and never were.
4. **Every row total on its provision** — a row whose application completes must have installed *every* key
   it declares.

The fourth is the one a machine-authored row can violate: a row that half-installs and returns breaks the
guarantee **silently**, with no error and no symptom until something downstream reads a key that was never
written. It is therefore not left to authorial care. **It is gate 11.**

**T3 · retirement is invariant under mounting.**
```
retire( mount(p,p⁻)(λ,ρ) ) ≃ retire(λ,ρ)        whenever   p⁻(p(λ)) ≃ λ
```
*Proof.* The left side is `((ρ ∘ p⁻)(p(λ)), id) = (ρ(p⁻(p(λ))), id)`, and the hypothesis collapses the inner
term to `λ`. ∎

Mounting never moves where retirement lands, so by induction the seed is recoverable after **any** sequence of
mounts. And the hypothesis is **pointwise**: an inverse need not invert the whole configuration space, only
the state where it was applied. That is the difference between a property you assert and a property a gate can
test in milliseconds — and it is exactly what the local-invertibility gate in §4 mechanises.

**T4 · containment.** Let `A : Ω → M_Λ` be a completion agent over the site's own material — untrusted,
arbitrary, possibly adversarial. Let the gate be three-valued,
```
G : M_Λ × ∂Λ → { GREEN, PASS-UNVERIFIED, FAILED }
```
and let gated mounting be the identity unless the verdict is `GREEN` **and** a signature is present. Then
```
∀A,   Reach_G(λ₀, id)  ⊆  { (λ,ρ) : retire(λ,ρ) ≃ (λ₀, id) }
```
*Proof.* Induction on the number of gated mounts. Base: `retire(λ₀, id) = (λ₀, id)`. Each step is either the
identity, or a mount whose local-inverse hypothesis the gate has verified — and T3 preserves the retirement
image in that case. ∎

Every state reachable by any agent retires to the seed. The bound is on the image of the gated operator and is
**independent of `A`** — which is precisely why this repository can be handed to a stranger's harness, and why
nothing in the design depends on the model being good. **The safety property is a property of the fence, not
of the model.**

**T5 · the denominator theorem.** A graded ratio `R = N/D` is admissible only if the denominator is a fold
over the tape: `∃ φ_D` with `φ_D(k) = D(k)` for every `k ∈ K`. **A ratio whose denominator cannot be
reconstructed from the record is not a measure.**

**T6 · scope, as a typing statement.** `mount : M_Λ → (∂Λ → ∂Λ)`. There is no homomorphism from the patch
monoid into `Σ → Σ`, because Σ is a point whose only endomorphism is the identity; and none into `K → K`,
because the record admits no arrow but append. The immutability of L0, L1 and L4 is therefore not a permission
that could be misconfigured, revoked, or argued with at three in the morning. **The arrow does not exist.**

### What the mathematics does not buy

T1–T3 and T6 are theorems: two-line calculations, true of the algebra unconditionally. **T4 is a theorem about
the model.** Whether the code faithfully implements this algebra is a separate, testable claim — and closing
that gap is the entire job of the conformance battery. **A proof about the design is not a receipt about the
build.** Nothing here is exempt from §12.

*This construction follows a published effect-context algebra; the transposition to the fit, the singleton
seed, the three-valued gate and the containment result are this project's own. It is not new mathematics and
does not claim to be — it is old mathematics pointed at a record system.*

---

## §4 · The gate battery

A gate is mechanical wherever a machine can check it. A gate that cannot pass inside a bounded retry writes a
hard stop **naming the exact defect in words** and escalates to a human, rather than degrading silently.

| Gate | Refuses |
|---|---|
| OPTN required-element completeness | submission or allocation-readiness with a mandated element missing |
| Timer integrity | a case whose response, offer or ischemia clock is unaccounted for |
| Chain-of-custody continuity | a gap in the conserved chain from recovery to disposition |
| Authorisation record validity | any downstream step where the authorisation artifact is absent or malformed |
| Measure-denominator integrity | a computed ratio whose denominator is not a fold over the tape (T5) |
| Patch blast radius | any row touching L0, L1 or L4, or any row outside its declared scope |
| Evidence binding | a row asserting local practice with no cited source and no shadow run |
| **Local invertibility** | a row where `p⁻(p(λ)) ≠ λ` at the current `λ` — the T3 hypothesis, mechanised |
| Floor-with-learned-zeroed | a release where the deterministic floor fails with every model component disabled |
| **Totality on provision** | a row whose application completes without having installed every key it declares — the silent breaker of confluence |
| Three-state honesty | reporting `GREEN` where the truth is `PASS-UNVERIFIED` |

That last row is the one everybody collapses. **`GREEN`, `PASS-UNVERIFIED` and `FAILED` are three different
states.** Folding the middle into the first is how a system reports success past a step that never ran — and a
foreign harness will produce confident, plausible, wrong work all day long if a weak battery blesses it.

**The battery is what makes AI completion safe. If it is weak, this project is actively dangerous rather than
merely unhelpful.** Build it adversarially.

---

## §5 · The differentiation kit

Not documentation. The machinery that lets a site's own harness do in a week what an interview programme does
in years — and, more importantly, **prove** that it did.

| Component | What it is |
|---|---|
| `AGENTS.md` | The boot contract for a foreign harness: read order, what may be touched, what is structurally immutable, which gate proves the work landed. **The repository tells the intelligence how to read it.** This is the self-unpacking — not autonomy, but a manual for the general-purpose unpacker already installed at every site. |
| `elicit/` | The elicitation protocol as an executable question set, ordered by decision-impact, each question naming which source *in the site's own building* answers it: SOPs, org chart, QA exception log, ticket history, interface configs, escalation threads. **The harness interviews the material, not the coordinators.** |
| `schema/patch.schema.json` | The contract of §2, and its validator. |
| `examples/worked/` | One complete, annotated patch layer for a fictional OPO — **including the wrong first drafts and the gate output that rejected them.** This is what a model actually pattern-matches against; after `AGENTS.md` it is the highest-value file here. |
| `adapters/` | Typed L3 interface shells with conformance tests, so completing one is filling a shape rather than inventing one. |
| `fixtures/` | Synthetic donor cases. Adversarial, and zero PHI, forever. |

### The bet, stated exactly

The old question was *"can an AI learn an organisation by watching it for months?"* — unproven, slow, and
entangled with PHI at every step. The question this design actually asks is:

> **Can an AI fill a well-specified schema, when driven by a local team with local access, against a battery
> that catches it when it is wrong?**

That is a far easier bet, and it is the one this project takes. `[BET]` Its falsifier is R5 in §11.

### The compliance shape

Two models, two data classes, one clean line:

- **The frontier harness reads the seed** — public, MIT, zero PHI. Nothing to protect, so nothing to negotiate.
- **A local open-weight model reads the site** — SOPs, tickets, configs, tape. PHI-bearing, and it never
  egresses. Unplug the network cable and it behaves identically.

---

## §6 · The floor, and the closure

The deterministic, model-free layer. It must pass its full battery with **every learned component disabled**,
or the release does not ship.

Its sharpest piece is the temporal closure. A case is a **Simple Temporal Network**: time points joined by
constraints `a ≤ x_j − x_i ≤ b`. Three classical facts do all the work — the network is consistent **iff** its
distance graph has no negative cycle; the tightest implied bounds are all-pairs shortest paths in the
**(min, +) tropical semiring**; and the feasible window of any event falls out as `[ −D[j][0], D[0][j] ]`.

**What that buys, which a flat list of timers cannot:** *implied* deadlines. No individual field is wrong at
the moment a case becomes infeasible; the failure lives in the transitive closure of constraints that are each
individually satisfied. A coordinator knows every pairwise rule; nobody computes the consequence.

**And the argmin path is the explanation.** The chain that binds a deadline is recovered from the same
computation that produced it, so the output is a derivation a physician can check in seconds — which is what
"advisory by construction" has to mean if it means anything.

Note the layer attribution: the federal constraints are real but generous, and **the rows that actually decide
whether a case converts are the L2/L3 ones** — your OR window, your lab's turnaround, your team's mobilisation
time. **The closure is only ever as good as the fit**, which is why the fit is the product and the record is
what it leaves behind.

### Correctness discipline

Times are whole minutes; arithmetic is integer `(min, +)`, which is **exactly associative**. The sentinel is
`0x3f3f3f3f`, sized so it can be added to itself without overflowing a 32-bit integer. Therefore any
accelerated path and the deterministic floor **must be bit-identical, asserted by equality and never by
tolerance.** A floating-point implementation would be faster to write and would silently fail both replay
determinism and floor-with-learned-zeroed.

### On hardware, honestly

A GPU is **not** required for one case: a lifecycle is nearly series-parallel, so its induced width is small
and the floor runs in effectively linear time on a CPU. The general algorithm is cubic; the domain's structure
is what makes it cheap. Acceleration earns its place only on the portfolio counterfactual sweep — N live cases
× K candidate interventions is tens of thousands of small networks, arithmetic that is GEMM-shaped with
`(+, ×)` replaced by `(min, +)`. `[BUDGET]`

**`[NULL]` — a flat list of timers with alarms.** What every EDR already has, and not weak. The experiment is
cheap and needs only an existing tape: replay historical cases, count the breaches a flat list would have
missed, print the number. **If the flat list catches nearly all of them, the closure becomes a funeral and
this document will say so.**

### The floor is also the resident's null

The closure is the **deterministic judge at radius 1** (§2b): it perceives a case, computes what no human
computed, and surfaces it **unprompted** — no timer fired, nobody asked. That is already an emit decision,
made by a fixed rule rather than a trained one. **The system has always been a resident; the floor is its
simplest possible mind.**

Which makes it the null for everything above it. The floor must pass its full battery **with every learned
component disabled**, and **any resident must beat the floor, or neither ships.** `[NULL]` **No organ
outlives its null** — and this is a strong one: exact, explicable, and it needs no card.

---

## §7 · The record and the measures

`K` is append-only and hash-chained. Every view — the board, a workup screen, a CMS numerator — is a
**deterministic fold** over it, which turns replay determinism into a proof obligation rather than a wish: two
independent replays of one tape must be byte-identical.

The graded ratios are first-class computed objects derived from the tape, not assembled quarterly by an
analyst. An OPO deploying the seed sees its own CMS-shaped numbers the day it turns on — **which is a product
on its own, before anything else in this document is built.** Admissibility is T5.

---

## §8 · What it never does

Written as prohibitions because they should be unreachable rather than discouraged:

1. It does not **run or alter allocation.** Allocation belongs to OPTN, executed through their systems.
2. It does not **determine eligibility or brain death.** It may surface that a required element is missing.
3. It does not **participate in the family approach.** Not as a script, not as a prompt, not as an observer.
4. It does not **write to L4.** The case record is written by humans.
5. It does not **transmit anything outside the building** absent an explicit, revocable, logged authorisation.
6. It does not **rank donors, recipients or families.** It ranks its own candidate utterances, which is a
   different object entirely.
7. It does not **make or override a clinical determination.** It surfaces and cites; the human decides.

### Why this list is a boundary rather than a policy

Every operation that reaches outside a system proceeds in two stages, and they fall on opposite sides of the
line that decides what can be undone.

- **Acquisition** — opening a descriptor, reserving a block, starting a process. It installs a record *inside*
  the boundary, and that record is revertible.
- **Emission** — the write, the send, the submission. It pushes data through the channel that acquisition
  opened, leaves it where other parties may read it, and **has no inverse.** Nothing in any runtime can
  retract it.

There are exactly two recoveries available for an emission. **Withhold** it until the state that produced it
is certain to persist. Or **compensate** — an action restoring things up to some coarser equivalence the
application supplies: delete the file that was created, refund the charge that was made. Compensations compose
in the same order inverses do, but the guarantees do not travel with them; each one has to be argued again on
its own terms.

**REGISTRAR acquires and never emits.** It reads, connects, computes and holds. It does not submit, send,
sign, allocate or act. The list above is therefore not caution and not a product decision — **it is the system
boundary drawn where the theory says it has to be. An emission never made needs no compensation.**

And the other recovery has a name here too. *Withholding an emission until the state that produced it is
certain to persist* is precisely what a human signature does in this design. **The signature is the output
commit.**

### The fence is on action, never on perception

Read the seven prohibitions again and note what is **not** among them: *perceive*, *notice*, *compute*,
*surface*. **They are a list of acts.** The system may attend a case as closely as it is able — that is the
product — and it may never act on one.

> **The resident perceives and surfaces. It never acts.**

Not throttled, not permissioned. There is no arrow from a judgment to an act: `core/case.py` takes no input
a model produced, and allocation, authorization, transmission and the record itself are structurally
unreachable (§3, T6 — *the arrow does not exist*).

**And the direction this cuts is the opposite of the intuitive one.** A resident is *more* compliant with
the decision-support carve-out than a threshold alarm is, because the carve-out turns on presenting the
basis for independent review. **An alarm presents a number. The closure presents the derivation** — the
argmin path, recovered from the same computation that produced the deadline — and a hold record adds what
was considered and declined. §2b.

**Advisory by construction.** The clinical-decision-support carve-out turns on whether software presents the
basis of its recommendation so a professional can independently review it and does not rely primarily on the
software. That clause is not merely compatible with this design — **it is this design, arrived at from the
other direction.** Confirm with your own counsel, on your own facts, before deployment. This document asserts
no regulatory status it has not had reviewed.

---

## §9 · The distribution

REGISTRAR is not a framework and does not ship its own plugin system. **It is a distribution**: a pinned
runtime, a set of out-of-tree packages, and a profile that mounts only what an electronic donor record needs.

**The runtime is [Cordis](https://github.com/deepseek-ai/deepseek-harness)** (MIT), the effect and coeffect
kernel formalised in *A Programming Paradigm for Spatiotemporal Composability* (Shi, Zhang & Cui; Peking
University and DeepSeek-AI), together with the harness built on it.

**Stated precisely, because the tense here has been wrong.** The chassis is **vendored in place** — it sits
in this repository's root — and it is **unpinned and unwired**: no `.git`, so no assertable SHA, and nothing
imports it. It is gitignored and a conformance gate fails if it is ever staged, because **unpinned
third-party code must not ship from an MIT tree.** The algebra of §3 is implemented **directly**, in
`core/algebra.py`, in stdlib Python with no runtime dependency. **Cordis is the reference implementation of
those semantics and the intended substrate for the composed instance; that composition has not been built.**
The pin is `internal` §14 item 1 and it blocks the wiring, not the design. The algebra in §3 is not an abstraction
over nothing — `mount`, `retire`, the twisted product and confluence are that kernel's semantics with the
objects of this domain substituted in. **The alternative to depending on it was re-deriving a published,
tested effect system ourselves, which would be novel, unaudited and unmaintained, and would make §3's
theorems claims about code nobody has reviewed.**

Two maturity facts, kept separate because they carry different risk:

- **The kernel is `cordis` v4.0.1**, authored by Shigma, with roughly four years and several thousand
  community plugins behind it in the Koishi ecosystem before DeepSeek adopted it. This is where §3 lives.
- **The harness around it is a release candidate** and says so. That is the layer a distribution composes
  down, and it is pinned and vendored rather than tracked.

**Compose, never fork.** A fork inherits permanent maintenance burden and destroys the upgrade path. The
distribution is a pinned tree plus `@registrar/*` packages beside it plus a profile — so the mounted surface
is a configuration, and **the audit surface is what you mount, not what is in the tree.**

**Provider-agnostic by construction.** The runtime's LLM seam resolves providers as configuration rather than
code: an OpenAI-compatible gateway, a self-hosted endpoint, or a provider newer than the shipped catalog is a
config route. Credentials are *references* resolved per request, so no secret enters a config file. **This is
what makes §5's two-model split one runtime with two routes rather than two stacks** — a public route for the
seed, a local route for the site, and no way for the second to reach the first.

**Self-modification is permitted inward and gated outward.** The runtime can compose new components from
within a running session — in process memory, discarded on restart, unable to promote themselves, and
requiring a person to start them. That is a real capability and this project does not disable it. But nothing
it authors reaches the standing instance except as a **candidate patch row**, through the gates of §4, under a
signature. The runtime's own design already draws that line; REGISTRAR only insists on it.

### The same body, twice — what a clone delivers

**A clone is not a specification. It is a working harness**, composed to a profile, with the default plugins
mounted and **FUSOR at its core** — runnable against a local open-weight model on one card, or against any
API, because provider routing is configuration rather than code. **That harness is what completes the fit.**

**And the same stack, re-profiled, is what the finished record runs on**, with its own resident attending
cases. **One substrate, instantiated twice** — the forge that grows the seed into this organisation's shape,
and the record that then attends its cases. Not two products sharing a repository: **the same loop at two
radii** (§2b), which is why the recursion is mechanical rather than metaphorical.

**FUSOR is toggleable at both levels.** Everything is a plugin, so it unmounts — from the source, or from
inside a running session, because a registration carries its own disposer. Off, you have a conventional
turn-based harness and a conventional record, and both still work. **The maximum-ambition version ships by
default; using it that way is the operator's choice.**

**Why it must be in the delivery rather than bolted on:** the body is excellent and heartless. Its own
documentation names the hole — *"injected context waits in the inbox until another message wakes it"* — and
the chain of who-wakes-it terminates at a clock, a tool completion, or a person. **Without something home to
notice, a completion stalls at every boundary waiting for a person to type *continue*, and a three-person IT
function with a day job does not finish that.**

**Bootstrapping runs at every level, during and after.** Because the harness is a plugin host with reversible
effects, a wall is never a dead end at either radius: it authors the plugin, shadow-runs it against the
site's own material, and **proposes** it — one yes mounts it hash-pinned, drift demotes, retirement unwinds
through the disposer. **The same contract as a patch row, applied to capability rather than configuration.**

**The gap, stated precisely.** `[SPEC]` **The harness itself is here** — the full dsh tree, in the
repository root. What is missing is narrower than its absence: **it has never been installed** (no
`node_modules`, nothing built), **it is unpinned** (no `.git`, no assertable SHA), **it is stock rather than
composed** (the default tree on `127.0.0.1:3080`, not a profile carrying only what a record needs), **every
plugin binding is `null`**, and **FUSOR is not mounted in it.**

So a clone today delivers the seed, the gates, the floor, the contract, the percept stream, the switch **and
the harness** — but you would install and compose it yourself. Closing that is four pieces: **pin · compose a
boot profile · bind the default plugins · mount FUSOR.** A packaged desktop chassis — an executable with an
embedded runtime, so nobody meets a console — is separate and further out.

### Repository layout `[SPEC — to be created]`

```
core/            L0 — lifecycle · elements + validators · submission · measures · timers
clinical/        L1 — panels, typing, viability criteria, vocabularies
adapters/        L3 interface shells: epic · cerner · meditech · lab · pacs · esig · transport
floor/           the deterministic, model-free layer (§6)
gates/           the gate battery (§4)
conformance/     the battery a completed instance must pass before it load-bears
fixtures/        synthetic donor cases; zero PHI, forever
elicit/          the question set (§5)
schema/          patch.schema.json — the contract of §2
examples/worked/ one complete annotated patch layer, with its rejected drafts
AGENTS.md        the boot contract for a foreign harness            [EXISTS]
PROVENANCE.md    per-L0-element public-source citation (§10)         [EXISTS — ledger empty]

<site>.patch.yml   AUTHORED ON SITE. Lives in the site's own version control. Never here.
<site>.tape/       The site's record. Never here.
```

---

## §10 · The clean-room constraint

The author is a former employee of an OPO that built a system of this exact kind. This is a build constraint
with legal consequences, not a footnote.

**Everything in the seed must be derivable from public sources only:** published OPTN policy and data-element
definitions, the CFR, CMS rules and fact sheets, vendor public documentation, published literature, and
synthetic fixtures. Not from anything proprietary seen, written, or remembered as an internal design.

**`PROVENANCE.md` carries a public-source citation per L0 element, written as the code is written and not
retrofitted.** Any provenance question about any design decision must be answerable by pointing at a public
document.

**Domain intuition is his to keep and use. Somebody else's schema is not.**

---

## §11 · The build ladder

Each rung is shippable, names its null, and is earned by the rung below it.

| Rung | Deliverable | Gate | `[NULL]` |
|---|---|---|---|
| **R1** | `core/` L0: lifecycle state machine, OPTN element set, validators, over `fixtures/` | a competent OPO quality director reads the L0 objects and **recognises their own operation**. If not, the spine is wrong and nothing above it matters. | a spreadsheet and the incumbent's own reporting |
| **R2** | `core/measures/`: the graded ratios as folds (T5), computed from a tape | denominator reconstructible for every fixture | the quarterly manual audit |
| **R3** | `floor/`: the temporal closure, reference then accelerated, with the bit-identity assertion | equality holds across the full fixture set; the floor passes with learned components disabled | a flat list of timers |
| **R4** | `gates/` + `schema/` + `conformance/`: the fence | a deliberately adversarial patch corpus is refused, with the defect named in words every time | human review |
| **R5** | `elicit/` + `AGENTS.md` + `examples/worked/`: the kit — **and the falsifier** | a harness, given only *public* material for a second OPO, authors a candidate patch; grade it against the known delta, **pre-registered before the run** | a human implementation guide |
| **R6** | First site completion, under signature | time from clone to first signed patch; rows accepted versus rejected | — |

**R5 is the cheapest decisive experiment in the entire plan.** It costs one weekend, touches no PHI, and needs
nobody's permission. It has three publishable outcomes: the patch covers the material delta and the thesis has
its first receipt; the patch is shallow but correctly shaped, which is the *expected* result and tells you
exactly how much observation the fitting requires; or the patch is confidently wrong, **the funeral prints,
and the honest product is an excellent open-source spine with a human implementation guide.** Run it before
building anything above R4.

---

## §12 · What is NOT claimed

- **Nothing here has run inside an OPO. No patient data has touched any part of it.**
- The completion claim is a `[BET]` with its falsifier printed in §11 and its kill condition named.
- Any performance figure carried into this project from other work was measured on other streams, in another
  room. **Its transfer to this domain is a bet in every case**, and is listed as one.
- **There are no clinical performance numbers, because there are none.** When that changes, the plate changes
  first and the prose follows.
- The central risk is not a wrong patch. It is a **weak battery** — because a foreign harness will produce
  confident, plausible, wrong work, and the gates are the only thing standing between that and an organisation
  where wrong loses an organ.
- A second risk is real and structural: fifty-five completions could become fifty-five private forks, which is
  how comparable open-source healthcare projects have ended. Confluence and the patch layer only work if **the
  patch path is so much easier than the fork path that forking is irrational.** If the repository merely
  *discourages* editing L0, someone will edit L0.
- Regulatory statements must be verified against the current rule text at the time of reading and reviewed
  with the deploying organisation's own counsel.

---

*v0.1, banked 2026-08-25. Nothing in this document has been built. The ladder in §11, not this document,
decides what happens next.*
