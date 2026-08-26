# PROVENANCE.md — the source ledger for L0 and L1

**Every element of the seed traces to a public document, cited here, with the date it was consulted.**

This file is not documentation. It is an **audit instrument**, and it is written as the code is written —
never retrofitted, never reconstructed from memory, never filled in before a release to make a table look
complete.

> **An element with no row in this ledger is not implemented. It is a TODO.**

---

## §1 · Why this file exists

The author of this repository is a **former employee of an organ procurement organisation that built a system
of this exact kind.**

That fact is disclosed here rather than discovered later, because it determines a build constraint with legal
consequences, and because a repository asking fifty-five organisations to trust its spine should not make
them ask.

**Domain intuition is his to keep and use. Somebody else's schema is not.**

Knowing *that* an EDR must reconcile a serology result against an allocation deadline is domain knowledge,
carried in a head, and it belongs to the person who learned it. Knowing *how a particular employer's system
modelled that reconciliation* is that employer's design, and it is not available to this project at any
price — not as a reference, not as an influence, not as a thing to avoid copying too closely.

The discipline that keeps those two apart is mechanical rather than a matter of good intentions: **every
element in `core/` and `clinical/` must be derivable from a public document, and this ledger must show
which one.** If a design decision cannot be traced to a public source, it does not ship — regardless of how
confident anyone is that it is correct.

---

## §2 · The rule

For every element of **L0** (the mandated spine) and **L1** (the clinical invariants):

1. It must be **derivable from a publicly available document.**
2. That document must be **named here, with a stable locator and the date it was consulted.**
3. The row must record **what the source actually establishes** — not a restatement of the element.
4. If the element is a *design choice* rather than a mandate, it must be **marked as such**, because a
   design choice presented as a mandate is the most damaging error this ledger can contain.
5. **The row is written in the same commit as the code.** Not before, not after, not in a cleanup pass.

---

## §3 · Admissible sources

These are the classes of source this project may build from. **Every use requires verification at the point
of use, against the live text, with the accessed date recorded** — regulatory text moves, effective dates
slip, and policy is re-published.

| Authority | What it establishes | Locator |
|---|---|---|
| **OPTN Policies** | Organ allocation policy, required data submission, the definitions the network operates under. The authoritative source for L0 policy content. | `optn.transplant.hrsa.gov` |
| **OPTN data collection instruments** | The required-element sets and their field definitions, as published (e.g. the deceased-donor registration and histocompatibility instruments). | OPTN, as published |
| **42 CFR Part 121** | The OPTN Final Rule — the statutory frame the network operates under. | `ecfr.gov` |
| **42 CFR Part 486, Subpart G** | Conditions for Coverage for Organ Procurement Organizations — the certification and outcome-measure regime. | `ecfr.gov` |
| **The Federal Register** | Final and proposed rules, preambles, comment responses, effective dates. **The preamble often establishes intent that the codified text alone does not.** | `federalregister.gov` |
| **CMS published guidance** | Fact sheets, interpretive guidance, measure specifications and their denominators. | `cms.gov` |
| **SRTR published methodology** | Measure construction and cohort definitions, where relied upon. | `srtr.org` |
| **Peer-reviewed literature** | Clinical invariants: viability criteria, ischemia tolerances, standard panels. **Cite the paper, not the consensus.** | DOI |
| **Vendor public documentation** | Integration surfaces and formats, where publicly documented by the vendor. | vendor's own public docs |
| **Standards bodies** | HL7, LOINC, SNOMED CT, ICD, and the terminologies OPTN references. | the standard's own publisher |

**Anything on this list is admissible only in its published form, as published.** A summary of a rule is not
the rule.

---

## §4 · Inadmissible sources — explicitly

Named individually, because "use public sources" is too vague to enforce and the failure modes here are
specific:

- **Any internal document of any employer, past or present.** Specifications, schemas, data dictionaries,
  ERDs, tickets, wikis, runbooks, training material, screenshots.
- **Recollection of a former employer's design.** Including recollection expressed as "the obvious way to
  model this," where the obviousness comes from having seen one implementation.
- **Another vendor's product**, examined by screenshot, trial account, demo, or reverse engineering of a
  file format or interface.
- **A customer's or partner's configuration**, in any form.
- **Real case data**, identified or de-identified, from any source, for any purpose including fixtures.
  `fixtures/` are **synthetic**, forever, and that is not a privacy convenience — it is a provenance
  requirement.
- **A model's uncited assertion.** An AI harness producing a confident regulatory value without a source is
  producing a fabrication with good grammar. `AGENTS.md` §9.2 governs this; **no generated value enters
  `core/` without a human-verified citation in this ledger.**
- **This repository's own prose.** `SPEC.md` and `README.md` are arguments, not authorities. They may not be
  cited as the source for an element.

---

## §5 · Ledger format

One row per element. Element IDs are stable and match the path in the tree.

```
### <element-id>
- **layer**      L0 | L1
- **element**    what it is, in one line
- **kind**       mandate | definition | clinical-invariant | design-choice
- **source**     the publishing authority and document title
- **locator**    section, policy number, CFR cite, or DOI — precise enough to check in under a minute
- **accessed**   YYYY-MM-DD
- **establishes** what the source actually says. Not a restatement of the element.
- **notes**      any gap between what the source establishes and what the element does
```

**Worked example of the format** — illustrative only; this is *not* a claim about any real element, and the
placeholders are deliberately unfilled:

```
### core/elements/<example>
- layer        L0
- element      <the required element>
- kind         mandate
- source       <publishing authority> — <document title>
- locator      <policy §, CFR cite, or DOI>
- accessed     <YYYY-MM-DD>
- establishes  <what the text actually says>
- notes        <where the element is narrower or broader than the source, and why>
```

### On `kind: design-choice`

Not everything in the seed is mandated. Data representation, internal identifiers, module boundaries and file
formats are choices. **Mark them.** A design choice mislabelled as a mandate is worse than an uncited element,
because it launders an opinion into apparent law and every downstream reader inherits it.

---

## §6 · The ledger

**Opened 2026-08-25**, in the same commit as the first `core/` file. Rows below cover
`core/lifecycle/lifecycle.yml` and `floor/`.

**Read the coverage honestly.** The lifecycle file's *structure* is drafted, but most of its elements carry
`locator: TODO-VERIFY` — the authority is named, the exact citation is not yet checked against live text.
**Per §2 those elements are not implemented; they are TODOs**, and no validator may enforce one until its
locator is filled. What follows is what has actually been verified.

---

### core/lifecycle/measures/donation_rate
- **layer** L0
- **element** The graded donation rate, and the origin of its denominator.
- **kind** mandate
- **source** CMS — *Organ Procurement Organizations (OPOs) Conditions for Coverage: Revisions* (CMS-3409-P), fact sheet and proposed rule
- **locator** CMS fact sheet, 2026-01-28; Federal Register document 2026-01833, published 2026-01-30
- **accessed** 2026-08-25
- **establishes** CMS grades OPOs on two outcome measures — a donation rate and a transplantation rate — whose denominators are derived from inpatient death records rather than from OPO self-report.
- **notes** The *denominator source* is verified. The precise numerator definition is **not** and remains TODO-VERIFY in the element file. The element therefore records where the denominator comes from and refuses to assert the numerator.

### core/lifecycle/measures/transplantation_rate
- **layer** L0
- **element** The graded transplantation rate.
- **kind** mandate
- **source** CMS — CMS-3409-P, fact sheet and proposed rule
- **locator** CMS fact sheet, 2026-01-28; FR doc 2026-01833, 2026-01-30
- **accessed** 2026-08-25
- **establishes** As above; the second of the two graded measures, same denominator construction.
- **notes** Same numerator caveat.

### core/lifecycle/tiering
- **layer** L0
- **element** The three-tier recertification regime and its consequences.
- **kind** mandate
- **source** CMS — CMS-3409-P; corroborated by Crowell & Moring and Holland & Knight client alerts
- **locator** FR doc 2026-01833, 2026-01-30; comment period closed 2026-03-31
- **accessed** 2026-08-25
- **establishes** **Tiers attach to donation service areas, not to organisations.** An OPO holding at least one Tier 1 DSA is recertified automatically; one holding Tier 2 areas is not out of compliance but must compete for areas that open; an OPO holding *only* Tier 3 areas is non-compliant and decertified.
- **notes** **This corrected a published error.** Project material previously stated "Tier 3 is decertified" at organisation grain, which materially overstated decertification exposure. Corrected 2026-08-25.

### core/lifecycle/timeline
- **layer** L0
- **element** When the regime takes effect.
- **kind** mandate
- **source** CMS — CMS-3409-P; supplementary CMS guidance issued 2026-03-11
- **locator** FR doc 2026-01833, 2026-01-30
- **accessed** 2026-08-25
- **establishes** Final rule expected late 2026, effective 60 days after publication; recertification and decertification proceedings for Tier 2 and Tier 3 commence January 2027. The March 2026 guidance is complementary and does not alter the tier architecture or the timeline.
- **notes** **Re-verify before any distribution.** A citation is a claim about a document at a date, and the final rule has not landed.

### core/lifecycle/authority
- **layer** L0
- **element** The regulatory home of the OPO Conditions for Coverage.
- **kind** mandate
- **source** eCFR — 42 CFR Part 486, Subpart G
- **locator** `ecfr.gov`, Title 42 → Chapter IV → Subchapter G → Part 486 → Subpart G
- **accessed** 2026-08-25
- **establishes** Subpart G is the location of the OPO certification, designation and Conditions for Coverage requirements.
- **notes** Existence and scope verified. **Individual section citations within Subpart G are not yet verified** and appear as TODO-VERIFY throughout the lifecycle file.

---

### Design choices, marked as such

Per §5, a design choice mislabelled as a mandate is the most damaging error this ledger can contain. These
are choices. Nothing above compels them.

### core/lifecycle/states/referral_lapsed
- **layer** L0 (structural)
- **kind** **design-choice**
- **source** none — introduced by this project
- **accessed** 2026-08-25
- **establishes** Nothing. It is not a mandated state.
- **notes** Added so that non-progression is representable. A referral that quietly stops moving is a real and measurable failure with **no event, only an absence** — and a state machine with no terminal for it cannot express the thing the missed-referral audit is about. Marked a design choice so no reader mistakes it for policy.

### floor/closure.py — integer (min,+) arithmetic
- **layer** floor
- **kind** **design-choice**
- **source** classical result: an STN is consistent iff its distance graph has no negative cycle; minimal network = all-pairs shortest paths
- **accessed** 2026-08-25
- **establishes** The algorithm is standard and not this project's invention.
- **notes** The *choice* is whole minutes and integer arithmetic with `INF = 0x3f3f3f3f`. Exactly associative, no floating point, no drift — which is what lets an accelerated implementation be compared to this one **by equality rather than tolerance**, and is therefore a precondition of replay determinism rather than a style preference.

### fixtures/ — JSON rather than YAML
- **layer** fixtures
- **kind** **design-choice**
- **accessed** 2026-08-25
- **notes** So the floor runs on a bare Python with nothing installed. A reference artifact that requires a dependency install before it does anything is a worse reference artifact.

### fixtures/cases/* — all values illustrative
- **kind** **design-choice**
- **accessed** 2026-08-25
- **notes** Every duration in every fixture is **synthetic and illustrative**, including the cold-ischemia budget in `infeasible-transport.json`. Organ-specific ischemia tolerances are clinical figures requiring citation to published literature before any validator enforces one; `t_cold_ischemia` in the lifecycle file is deliberately TODO-VERIFY. **No fixture value should be read as a clinical or regulatory claim.**

---

## §7 · Contested, superseded, and excluded

Where a source was consulted and **not** relied upon, it is recorded here with the reason. Sources are subject
to the same funeral discipline as everything else in this project: **what was rejected, and why, is part of
the record.**

### Excluded — CMS and Federal Register primary sources, retrieved indirectly
- **date** 2026-08-25
- **class** access, not admissibility
- **notes** `cms.gov` returned HTTP 403 and `federalregister.gov` redirected to a bot-check on automated retrieval. The figures above were corroborated through published law-firm client alerts (Crowell & Moring, Holland & Knight) and search summaries of the CMS fact sheet. **The sources are admissible; this retrieval was indirect, and that is recorded rather than hidden.** Every row above should be re-checked against the primary text by a human before it load-bears.

Expected entry classes, so the discipline is unambiguous when the first one arrives:

- **Superseded** — a rule replaced by a later one; the element follows the current text, and the prior
  citation is retained so a reader can see the change.
- **Ambiguous** — the source does not clearly establish the element; the element is narrowed until it does,
  and the narrowing is recorded.
- **Out of scope** — the source establishes something real that this seed deliberately does not implement.
- **Excluded on provenance** — the source is not admissible under §4. **Recorded without describing its
  contents.**

---

## §8 · How to audit this repository

Written for a hostile reviewer, which is the only kind worth designing for. This should take an afternoon.

1. **Enumerate the elements.** Every file under `core/` and `clinical/` declares its element IDs.
2. **Diff against this ledger.** Any element without a row is a finding. Any row without an element is a
   finding.
3. **Spot-check ten citations against the live text.** The locator should get you to the passage in under a
   minute. If it does not, the locator is inadequate — which is itself a finding.
4. **Check `kind`.** Anything marked `mandate` must be traceable to policy or regulation, not to a paper and
   not to practice. Anything that *should* be `design-choice` and is not is the highest-severity finding
   available here.
5. **Check the dates against `git log`.** A ledger row committed substantially later than the code it
   describes was retrofitted, which defeats the instrument. **Provenance written after the fact is not
   provenance; it is a rationalisation with a date field.**
6. **Check the fixtures.** They must be synthetic. Real data disguised as fixtures would be visible in
   distributional structure — internally consistent identifiers, plausible clinical correlations, realistic
   timing.

**If any of the above fails, say so in public.** That is the only thing this project asks of anyone.

---

## §9 · Maintenance

- **Regulatory text moves.** A citation is a claim about a document *at a date*. When a rule changes, the
  affected rows are revisited and the change recorded — the old row is not deleted.
- **Re-verification is scheduled, not reactive.** L0 rows are re-checked against live text on a stated
  cadence, and the cadence is published once the first rows exist.
- **This file is append-mostly.** Corrections are new entries with the reason. The one thing that must never
  happen is a quiet edit that makes a past state unreconstructable — which is the same law the case record
  runs on, applied to the repository's own conscience.

---

*v0.1 · 2026-08-25 · Rev 0, specification. The ledger is empty because the seed is unbuilt, and it will be
written one row at a time, in the commits that build it.*
