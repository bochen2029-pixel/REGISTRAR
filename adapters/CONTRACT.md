# The L3 adapter contract

**An adapter is a shape to fill, not a shape to invent.**

L3 is *which donor hospitals run which EHR and at what version, reference-lab interfaces and result formats,
imaging, e-signature, transport.* An OPO with forty donor hospitals has forty integration surfaces, and
**this is where an in-house build actually dies** — not in the lifecycle, which is law and identical
everywhere.

So the seed ships the **shell and its conformance battery**. What plugs into it is yours.

---

## What ships here, and what does not

**Ships:** the contract, a machine-readable form a gate can check, one worked adapter (`lab/`), a conformance
battery, and adversarial fixtures.

**Does not ship: a working Epic, Cerner or Meditech integration.** Those need interface specifications an OPO
holds under agreement. **Inventing them would be exactly the fabrication `tools/cite.py` exists to prevent** —
a plausible-looking HL7 segment map that nobody verified is worse than an empty directory, because it
survives casual review and fails in production.

Vendor bindings therefore ship `null`, the same pattern and the same reason as `forge/plugins.yml`: **the
seed declares what must be true of an adapter; the site binds the one it actually has.**

---

## The five declarations

Every adapter declares these, or it does not mount.

### 1 · What it ingests

The source, the transport, and the shape. **Be specific about the version** — *"Epic"* is not an answer;
*which interface, at what version, from which hospital* is. Two donor hospitals running the same vendor at
different versions are **two adapters**, and pretending otherwise is how a fit silently stops fitting.

### 2 · Which lifecycle events it may produce

**A closed list, drawn from `core/lifecycle/lifecycle.yml`.** An adapter that could produce any event is not
an adapter, it is a write path — and the only write path in this system is one typed patch file.

**An adapter never produces a transition.** It produces *elements* — a result arrived, a document was signed,
an organ was collected — and the lifecycle decides whether that satisfies a guard. **The adapter observes;
the spine decides.** That separation is what keeps L3 from quietly authoring L0.

### 3 · Its failure modes, named individually

Not *"handles errors."* **Which failures, and what it does about each.** The battery tests three that every
adapter meets whether or not it expects them:

| | Failure | Why it is universal |
|---|---|---|
| **malformed** | a message that does not parse | every interface emits garbage eventually |
| **late** | a result that arrives after the deadline it was supposed to inform | **the normal case in this domain**, not the edge |
| **post-disposition** | a result arriving after the case closed | OPTN 2.12 *requires* these be obtained and reported — **disposition does not close the case** |

**An adapter that has not demonstrated all three does not mount.**

### 4 · Its own null

**What a coordinator does today, without it.** Usually: reads a screen and retypes. Sometimes: a phone call.

**An adapter that cannot beat its null is a liability, not an integration** — it adds a failure mode and a
maintenance burden to a process that already works. *No organ outlives its null.* State it, measure against
it, and if the null wins, **print the funeral and delete the adapter.**

### 5 · Its provenance

Where its format knowledge came from. **Vendor public documentation, a published standard, or an interface
specification the site holds** — and if the last, it stays at the site and never enters this repository.
`PROVENANCE.md` §4: another vendor's product examined by screenshot, trial account, or reverse engineering is
inadmissible, and that applies here exactly as it applies to L0.

---

## What an adapter may never do

Inherited from the layer stack, and each is structural rather than a preference:

- **Never write to L0, L1 or L4.** It produces observations. The lifecycle decides; humans write the record.
- **Never produce a transition.** See declaration 2.
- **Never egress.** An adapter reads a local interface and writes to a local record.
- **Never invent a value it did not receive.** A missing field is **absent**, and absence is itself a required
  entry — OPTN 2.3(4): *document what is unavailable and the reason it is not available.* **An adapter that
  defaults a missing result to a plausible value has fabricated a clinical fact.**
- **Never decide clinical meaning.** *"This result is abnormal"* is a determination. *"This result arrived,
  with this value, at this time"* is an observation. **Adapters do the second.**

---

## Time is the point

Most adapter work in this domain looks like a data problem and is a **timing** problem.

The worked example already carries the sharpest instance: **the contract says four hours, the laboratory
takes six.** A fit built on the contracted number computes every deadline two hours optimistic — **wrong in
the direction that loses organs.**

So an adapter declares the **observed** distribution of its own latency, not the promised one, and the
closure consumes that. An adapter that reports only *what* arrived and not *when* has answered half the
question. See `floor/closure.py`: the L2/L3 constraints are the ones that actually bind.

---

## Mounting

```bash
python adapters/conformance.py                    # every declared adapter
python adapters/conformance.py --adapter lab      # one
```

A binding declares: `version` · `source` · `sha256` pin · `entry` · SPDX `licence`. **A binding without a
licence cannot mount into an MIT tree**, and that is checked rather than remembered.

Read [`lab/`](lab/) first. It is the shape you are copying — **not the content.**
