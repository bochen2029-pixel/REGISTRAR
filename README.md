# REGISTRAR

**The open-source electronic donor record.**

The half that is federal law ships byte-identical to all fifty-five OPOs. The half that has to fit *your*
operation is not configured, not consulted, and not customised — it is **completed on site**, by your own
people and their own AI, against a gate battery that refuses to pass work that is wrong.

MIT · runs on your own hardware · zero egress · no account, no cloud, no telemetry, no vendor in the loop.

**→ [opnaorta.ai/edr](https://opnaorta.ai/edr)** — the full argument, the mathematics, and the plate.

> **STATUS: REV 0 — specification, pre-build.** Nothing here has run inside an OPO. No patient data has
> touched any part of this. There are no clinical performance numbers because there are none. When that
> changes, the plate changes first and the prose follows.

---

## The short version

Fifty-five organisations run the same federally mandated process. Three-quarters of them rent the same record
system, in someone else's cloud. The ones who tried to build their own found that it takes six years — and the
six years are not the code. They are the cost of discovering *what to write*, because the knowledge lives in
the heads of coordinators who are working a donor at three in the morning and cannot stop to be interviewed.

Fitting software to an operation required **someone present for the work as it is actually done**, for a long
time, and until recently the only thing that could be present was a person.

That constraint is gone — and not because a machine can write the code. **Because the thing that finishes the
software is already installed at all fifty-five sites: your own IT team, holding a state-of-the-art coding
harness, pointed at a system of record they are not permitted to open.**

REGISTRAR is what you point it at.

---

## What this actually is

Not a product. Not a framework. **The first repository designed to be safely completed by an AI its authors do
not control, at a site they will never visit, in a domain where wrong loses an organ.**

The seed is given away. The fit is given away. What is kept is the fence.

### The layer stack

| Layer | Contents | Owner |
|---|---|---|
| **L0 · mandated spine** | OPTN policy and required elements, allocation submission, CMS measure definitions and denominators, the case lifecycle from referral through disposition | federal law — **immutable** |
| **L1 · clinical invariants** | ABO and subtyping, HLA, serology panel, organ-specific viability criteria, donor-management targets, controlled vocabularies | medicine — **immutable** |
| **L2 · operational shape** | staffing model, call rotation, the escalation ladder as practised, hospital territory, QA thresholds, who signs what | **you — completed on site** |
| **L3 · local integrations** | which donor hospitals run which EHR and at what version, lab interfaces and result formats, imaging, e-signature, transport | **you — completed on site** |
| **L4 · the case** | one donor, one record, append-only, hash-chained, exportable in full at any moment | **clinicians and coordinators — append-only** |

**L0 and L1 are the seed.** They have never been open-sourced, and fifty-five organisations currently pay — in
money, or in multi-year internal builds — to separately re-encode something that is *identical by law*.
Building it once for everybody is worth doing even if every other claim in this repository fails.

**L2 and L3 are the six years.** They are what the differentiation kit is for.

The seed is **useful at L0 with an empty patch file**: a real state machine, real validators, and your own
CMS-shaped numbers computed from your own tape on the day you turn it on.

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

These are stated formally, with proofs, in [`SPEC.md` §3](SPEC.md). The result that matters:

> For **any** completion agent, however wrong, every reachable state of the system retires to the seed.
> The bound is independent of the agent — **the safety property is a property of the fence, not of the model.**

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

---

## What it takes

```
OS         Linux or Windows Server, inside your network
GPU        one NVIDIA RTX-class card, 24–32 GB VRAM
Model      open weights, 9B to 27B class, quantized — fully offline
Record     append-only, hash-chained, exportable in full at any time
Harness    whichever your team already uses. this repo is written for it.
Network    none required. air-gapped is a supported configuration.
```

**Two models, two data classes, one clean line.** Your frontier harness reads *the seed* — public, MIT, zero
PHI, nothing to protect and nothing to negotiate. A local open-weight model on your own card reads *the site* —
your SOPs, your tickets, your configs, your tape. It never egresses. Unplug the network cable and it behaves
identically.

---

## Repository status

This repository currently contains the **specification**. The build ladder, its gates, and the falsifier that
decides whether the central claim survives are in [`SPEC.md` §11](SPEC.md).

The cheapest decisive experiment in the whole plan costs one weekend, touches no PHI, and needs nobody's
permission — and it either produces the first receipt or prints the funeral. It is **R5** in the ladder, and
it is deliberately scheduled *before* anything above it gets built.

---

## Contributing, and what stays out

Fork it. Strip it. Rename it. Ship it as your own — the licence permits that and the author will not be
involved. **The only thing asked in return is that if you find the spine wrong, you say so in public, where
the next organisation can read it.**

**Never commit to this repository:** a completed patch layer, a tape, real case data of any kind, vendor
credentials, or clinical content lifted from any prior employer. Your patch encodes how your organisation
works and is arguably competitively sensitive to you. **It is yours, it stays in your version control, and
this repository does not want it.**

Every element of L0 must be derivable from **public sources only** — published OPTN policy and data-element
definitions, the CFR, CMS rules and fact sheets, vendor public documentation, published literature, and
synthetic fixtures. See [`SPEC.md` §10](SPEC.md); this is a build constraint with legal consequences, not a
footnote.

---

## Verify before you act on any of this

Every regulatory statement in this repository must be checked against the current rule text at the time you
read it, not against this repository. Rules move, effective dates slip, and tier counts are re-published.
Confirm the regulatory posture with your own counsel, on your own facts, before deployment. **This project
does not ask anyone to take a compliance claim on faith — least of all one with a decertification attached
to it.**

---

## Licence

MIT. See [`LICENSE`](LICENSE).

There is no pricing page, no contact form, no demo request, no waitlist, and nothing to sign.
**There is no ask anywhere in this repository.**

---

*Bo Chen · Dallas, Texas · [opnaorta.ai](https://opnaorta.ai)*
