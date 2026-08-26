# PROPOSAL · two capabilities the forge needs and does not declare

**`2026-08-26` · written by Fork C, for Fork A to act on · touches no file Fork A owns**

---

## The finding

`forge/plugins.yml` declares five capabilities — `chunk`, `phi_scan`, `search`, `fetch`, `render`.

**The two that attack the six years are not among them.**

That is not an oversight to be embarrassed about. It is **the enumeration tax appearing inside REGISTRAR's
own plugin contract**: you can only declare a capability you already knew you wanted. It is the same shape as
`elicit/questions.yml` imposing twenty questions decided in advance — *work-as-imagined, at the meta level,
inside the artifact that names work-as-imagined as the central problem.*

Two organs already exist in the estate that name the missing capabilities precisely, and — the part that
makes this actionable — **they have already factored themselves correctly, independently.**

---

## What the forge is actually short of

### `read` — induce a schema from a corpus nobody can read

`C:\scriptorium`, *"the organ that reads a lifetime."* Its own framing:

> A verbose lifetime is 10⁸–10⁹ tokens… **~33 person-years to read once** — no notes, no index, no second
> pass. So nobody reads it.

**That is the six years at STA, restated as arithmetic.** An OPO's SOP binder, six years of ticket history
and a case tape is the same order of magnitude and has the same property: it outgrew every human reader and
every context window. Scriptorium prices reading it at **~$100 per billion raw tokens and a weekend**.

But the line that matters is not the price:

> **A bespoke ontology per corpus — the schema is *induced from your archive* and frozen under an explicit,
> operator-ratified editorial charter, not imposed from a taxonomy.**

**That is the completability thesis, implemented — and it convicts our own elicitation kit.** `elicit/` asks
twenty questions, one per variation point the *seed* declared. The seed decides in advance what is allowed to
differ between organisations. Scriptorium's move is the inverse: **read the material, induce what varies, have
a human ratify it, freeze it.**

This is what `INSTRUMENT` — FUSOR's third verb, *where surprise persists* — has always pointed at with no
mechanism behind it. A completion that can only fill declared variation points cannot discover an undeclared
one, and **an OPO whose operation differs in a way the seed never imagined is exactly the OPO the seed fails.**

### `reach` — addressable, load-rated retrieval over a corpus larger than the window

`C:\Cortex`, *"The Loom."* One sentence from its spec:

> complete addressability over a 10⁸–10⁹-token corpus and a **measured, stated fraction** of it as usable
> working context… closing every asserted claim against a lossless tape through **oracles no model authors**,
> and reporting on every answer exactly how much it touched, how well, from how many independent sources, and
> **what it could not see.**

Read that against this repository's own laws and the overlap is not analogy:

| CORTEX | REGISTRAR |
|---|---|
| *"every answer carries its precision bound — coverage, fidelity, staleness, budget, corroboration"* | **every number carries its grain, denominator and source** |
| *"oracles no model authors"* | `tools/cite.py` — byte-match or refused; **acceptance is a string comparison, not an act of trust** |
| *"a certificate a standalone verifier re-checks cold"* | `conformance/run.py` — one command, is this instance sound |
| **three quantities that are never interchanged** — `index_coverage`, `C_eff`, `coverage_int` | **three states, never two** — GREEN ≠ PASS-UNVERIFIED ≠ FAILED |
| *"the claim, stated so it can be refused"* + a permanently refused claim (§15.1) | `[BET]` with its kill condition; **funerals print** |

That fourth row is the one worth pausing on. CORTEX refuses to collapse *addressability* into *coverage* —
**"it is not coverage and is never printed as one"** — for exactly the reason this repository refuses to
collapse PASS-UNVERIFIED into GREEN. *Two different things that a flattering summary would merge.*

And the frame it ships under is one REGISTRAR should steal outright:

> **An unmarked bridge is a liability; a load-rated one is infrastructure.**

---

## `chunk` is a stopgap, and naming what it is the null *for* is the point

**Chunking is what you do when you have no index.** Split the document, read the pieces in order, hope the
answer is local. It is honest, cheap, and it is the floor.

CORTEX's own spec cut the catalog and replaced it with a deterministic locator — because splitting is not
retrieval.

So, per this repository's own standing rule — **no organ outlives its null**:

> **`chunk` is the `[NULL]` for `reach`.** A retrieval organ that does not beat *split it and read the
> pieces*, on the site's own material, is theatre — and the funeral prints.

That reframes Fork A's work rather than undoing it. **`chunk` should still be bound first**, exactly as
planned, because **you cannot show `reach` wins until the thing it must beat is running and measured.**

---

## The contract already fits — and neither organ was written for it

The strongest evidence that these bind cleanly is that **CORTEX arrived at our mount rules independently**:

> *"What already exists on disk — **never reimplement; call at fixed paths as subprocesses** (§15.1 forbids
> cross-organ imports)"*

Compare `forge/plugins.yml`: *take every path as an argument · write only where the caller says · be inert
when not called · fail loud and specific.* **Same law, different house.**

And CORTEX names scriptorium as *"one optional offline builder among several, **never a dependency**."*
**That is the capability/binding split, arrived at from the other side.** It also tells us the correct shape
here: `read` and `reach` are **two capabilities, not one organ** — an offline builder and an online index,
and neither may require the other.

---

## What must not be copied

**Neither organ is finished, and the proposal is weaker if that is soft-pedalled.**

- **scriptorium: rung S0 green, S1 in flight.** `read`, `map`, `reread`, `synthesize`, `certify` *"print
  their rung and refuse."* The refusal is the right behaviour; it is also not a working binding.
- **CORTEX: proposed final revision, not built.** *"Ships once, whole, when F-WHOLE is green. No editions, no
  tiers, no rungs, nothing that ships partway."*
- **Both rent a frontier API.** Scriptorium goes through one provider seam with a hard `usd_cap` per pass.
  **That collides with `AGENTS.md` §3 the moment the corpus is a site's material.** Scriptorium's own
  sovereignty split is *sharper* than ours — pixels and audio never leave the box, `pixels_leave_box: true`
  **refuses to run** — but it is a text-egress design, and **PHI-bearing site material may not rent a
  reading.** A binding here must run the local leg or not mount.
- **CORTEX is measured on the same box** — 4070 Ti SUPER, 16 GB — with free VRAM *"swinging 3.65 → 14.76 GiB
  within minutes,"* which is why its family-arbitration rule is *"load-bearing, not hypothetical."* **That is
  the co-tenancy floor already on `opnaorta.ai/edr`**, independently measured. A `reach` binding and a local
  resident contend for one card.

---

## What I propose, concretely

**Declare both capabilities now, with `binding: null`. Bind them when they exist.**

That is not a hedge — it is the pattern `forge/plugins.yml` already uses and the reason it exists. **A
declared capability with a null binding is honest and useful: it tells a site what the forge needs done, so
they can mount their own.** An *undeclared* capability tells them nothing, and worse, lets `chunk` masquerade
as covering it.

```yaml
  - id: read
    required: true
    need: >
      Induce a schema from a corpus too large for any reader, and freeze it
      under an operator-ratified charter. NOT a summary — a structure, with
      every claim span-checked against a lossless tape by deterministic code.
    why: >
      elicit/ asks twenty questions the SEED chose. A site whose operation
      differs in a way the seed never imagined is exactly the site the seed
      fails. This is the capability that finds an undeclared variation point.
    rules:
      - id: induced_not_imposed
        rule: The schema comes from the corpus and is ratified by a human. A taxonomy applied to a corpus is a different capability.
        severity: refuses_the_mount
      - id: local_leg_only
        rule: >
          Site material may not rent a reading. PHI-bearing corpora are read by
          the local leg or not at all — AGENTS.md §3.
        severity: refuses_the_mount
    binding: null

  - id: reach
    required: false
    need: >
      Complete addressability over a corpus larger than the window, with every
      answer carrying its own precision bound — how much was touched, how well,
      from how many independent sources, and WHAT COULD NOT BE SEEN.
    null: chunk
    rules:
      - id: load_rated
        rule: >
          An answer without its coverage, fidelity and corroboration is not an
          answer. An unmarked bridge is a liability; a load-rated one is
          infrastructure.
        severity: refuses_the_mount
      - id: never_interchange_the_quantities
        rule: >
          Addressability is not coverage and is never printed as one. Same law
          as three-states-never-two, at the measurement layer.
        severity: refuses_the_mount
      - id: beats_its_null
        rule: >
          Must beat `chunk` on the site's own material, measured. No organ
          outlives its null.
    binding: null
```

**Sequencing, unchanged from Fork A's plan:** bind `chunk` first — it is required, it is tractable, and it is
now *also* the measured floor that `reach` has to clear. Then `phi_scan`. `read` and `reach` are declared
today and bound when their organs ship.

---

## Why this is worth acting on rather than filing

The seven exposures Fork C found reduce to three sentences, and the first is: **the seed declares where a
value may go and never what shape it must have.**

**`read` is the capability that would fix that at the source** — a schema induced from the site's own material
is exactly the per-target shape whose absence lets a partial value, a wrongly-typed value, and an arbitrary
credentials blob all pass thirteen gates.

The battery cannot close those holes. **A gate can only check against a shape somebody declared**, and
nobody has declared one, because the seed's authors could not know in advance what shape each site's answer
takes.

**That is the completability argument, one level down, and it is the same answer: do not impose the shape —
induce it, ratify it, freeze it.**


---

# OUTCOME · `2026-08-26` · acted on by mainline

**All three declared. The fence built and shipped as gate 16.** `49 GREEN · 8 PASS-UNVERIFIED · 0 FAILED`,
`77/77` on the witness battery, `22/22` adversarial fixtures refused.

## The finding was accepted

**The enumeration tax inside our own plugin contract is real**, and it is the sharpest self-criticism this
project has produced. `chunk` as the `[NULL]` for `reach` is right and does not undo Fork A's plan. The
independent convergence — CORTEX's *"never reimplement; call at fixed paths as subprocesses"* — is evidence
rather than analogy.

## Three corrections, made before acting

**① `read` as written would have broken T4.** The seed's fixed variation list is what bounds the blast
radius, and **that bound is what makes the reachable set independent of the agent.** A site inducing its own
targets and patching them has no bound at all. Resolved by a rule that refuses the mount: **an induced
variation point is a PROPOSAL TO THE SEED, never a patch row** — upstream, human-ratified, L0 for all
fifty-five. A site can discover that a target is missing; it still cannot patch one.

**② Induction does not subsume declaration.** An induced schema reflects what the corpus CONTAINS, and a
corpus reflects what the organisation RECORDS. **A site that never records after-hours ownership has no
after-hours ownership in its induced schema** — while the seed's a-priori question still asks, and a human
answers from memory. Induction inherits the blind spots of the recording practice. Complementary, not
successive.

**③ `read` is not `required: true`.** Required means the forge cannot proceed without it — true of `chunk`
and `phi_scan`, not of this. It would leave every instance permanently PASS-UNVERIFIED on a capability
nobody can bind: a claim of brokenness rather than of ambition.

## And one defect, caught by our own gate

```yaml
    null: chunk
```

**`null:` is a YAML reserved word.** It parses as the `None` key and the field vanishes — the exact trap the
lab adapter hit, which the adapter checker now refuses. Shipped as `beats: chunk`. **A proposal for a gate,
caught by a gate.**

## The fence was the right thing to chase first — and it was not a capability

Built, probed, shipped as **gate 16 · `attest`**. It checks three things `cite.py` and `divergence` cannot:
evidence describing something **no longer in force**, evidence **denying that a bound exists** under a row
asserting one, and a **modality mismatch** — `may` is not `must`, and OPTN 2.5's *"a hemodiluted sample MAY
be used"* is exactly why that matters here.

**A fourth check was built and deleted.** Target drift — evidence cited to the wrong row — produced two
false positives in ten minutes: *"median elapsed to SECOND contact attempt"* matched
`authorization.second_person_rule`, and after narrowing, *"a referral with no progress AFTER four HOURS"*
matched `intake.after_hours_owner` **on the worked example.** It was doing a semantic job with a lexical
tool, and **the vocabulary of an operation is shared across its targets by construction.** The funeral is in
the source so nobody rebuilds it.

**And declaring `attest` a capability was a category error the forge checker caught.** Every bound
capability must live under `forge/plugins/<id>/` with its own LICENSE and PROVENANCE — because a capability
is something **a site may bind its own version of.** A gate is the opposite: **a fence a site can swap is not
a fence.** Moved to `not_mountable`, with the reasoning. *The capability was real; the category was wrong.*

## What is now true

| | |
|---|---|
| `chunk` · `phi_scan` | **bound**, required |
| `search` · `fetch` · `render` | declared, `binding: null` |
| **`read` · `reach`** | **declared, `binding: null`** — with the T4 rule and the local-leg rule on `read` |
| **`attest`** | **built, gate 16, not mountable** |

**Sequencing unchanged, as the proposal asked:** `chunk` first — now also the measured floor `reach` must
clear.
