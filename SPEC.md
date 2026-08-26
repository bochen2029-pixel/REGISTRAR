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

An open-source electronic donor record, in two halves.

**The seed (L0/L1)** is federal law and clinical invariant. It ships byte-identical to every OPO, because
there is exactly one legal answer to what it contains.

**The fit (L2/L3)** is everything that differs between organisations. It is authored **on site, by the site**,
using the site's own coding harness and the site's own material — against a gate battery that mechanically
refuses work that is wrong, and mounted only under a human signature.

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

**T3 · retirement is invariant under mounting.**
```
retire( mount(p,p⁻)(λ,ρ) ) = retire(λ,ρ)        whenever   p⁻(p(λ)) = λ
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
∀A,   Reach_G(λ₀, id)  ⊆  { (λ,ρ) : retire(λ,ρ) = (λ₀, id) }
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

**Advisory by construction.** The clinical-decision-support carve-out turns on whether software presents the
basis of its recommendation so a professional can independently review it and does not rely primarily on the
software. That clause is not merely compatible with this design — **it is this design, arrived at from the
other direction.** Confirm with your own counsel, on your own facts, before deployment. This document asserts
no regulatory status it has not had reviewed.

---

## §9 · Repository layout `[SPEC — to be created]`

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
AGENTS.md        the boot contract for a foreign harness
PROVENANCE.md    per-L0-element public-source citation (§10)

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
