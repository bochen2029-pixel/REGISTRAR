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

**Opened 2026-08-26**, in the same commit as the first `core/` file. Rows below cover
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
- **accessed** 2026-08-26
- **establishes** CMS grades OPOs on two outcome measures — a donation rate and a transplantation rate — whose denominators are derived from inpatient death records rather than from OPO self-report.
- **notes** The *denominator source* is verified. The precise numerator definition is **not** and remains TODO-VERIFY in the element file. The element therefore records where the denominator comes from and refuses to assert the numerator.

### core/lifecycle/measures/transplantation_rate
- **layer** L0
- **element** The graded transplantation rate.
- **kind** mandate
- **source** CMS — CMS-3409-P, fact sheet and proposed rule
- **locator** CMS fact sheet, 2026-01-28; FR doc 2026-01833, 2026-01-30
- **accessed** 2026-08-26
- **establishes** As above; the second of the two graded measures, same denominator construction.
- **notes** Same numerator caveat.

### core/lifecycle/tiering
- **layer** L0
- **element** The three-tier recertification regime and its consequences.
- **kind** mandate
- **source** CMS — CMS-3409-P; corroborated by Crowell & Moring and Holland & Knight client alerts
- **locator** FR doc 2026-01833, 2026-01-30; comment period closed 2026-03-31
- **accessed** 2026-08-26
- **establishes** **Tiers attach to donation service areas, not to organisations.** An OPO holding at least one Tier 1 DSA is recertified automatically; one holding Tier 2 areas is not out of compliance but must compete for areas that open; an OPO holding *only* Tier 3 areas is non-compliant and decertified.
- **notes** **This corrected a published error.** Project material previously stated "Tier 3 is decertified" at organisation grain, which materially overstated decertification exposure. Corrected 2026-08-26.

### core/lifecycle/timeline
- **layer** L0
- **element** When the regime takes effect.
- **kind** mandate
- **source** CMS — CMS-3409-P; supplementary CMS guidance issued 2026-03-11
- **locator** FR doc 2026-01833, 2026-01-30
- **accessed** 2026-08-26
- **establishes** Final rule expected late 2026, effective 60 days after publication; recertification and decertification proceedings for Tier 2 and Tier 3 commence January 2027. The March 2026 guidance is complementary and does not alter the tier architecture or the timeline.
- **notes** **Re-verify before any distribution.** A citation is a claim about a document at a date, and the final rule has not landed.

### core/lifecycle/authority
- **layer** L0
- **element** The regulatory home of the OPO Conditions for Coverage.
- **kind** mandate
- **source** eCFR — 42 CFR Part 486, Subpart G
- **locator** `ecfr.gov`, Title 42 → Chapter IV → Subchapter G → Part 486 → Subpart G
- **accessed** 2026-08-26
- **establishes** Subpart G is the location of the OPO certification, designation and Conditions for Coverage requirements.
- **notes** Existence and scope verified. **Individual section citations within Subpart G are not yet verified** and appear as TODO-VERIFY throughout the lifecycle file.

### core/lifecycle/states/referral_received
- **layer** L0
- **element** The referral relationship between an OPO and its donor hospitals.
- **kind** mandate
- **source** eCFR — 42 CFR Part 486, Subpart G, § 486.322(a) *Standard: Hospital agreements*
- **locator** 42 CFR 486.322(a) · issue date 2026-08-24 · pinned `ecfr-42-486-subpartG` sha256 `cc14fbe7cc703cdd…`
- **accessed** 2026-08-26
- **establishes** *"An OPO must have a written agreement with 95 percent of the Medicare and Medicaid participating hospitals and critical access hospitals in its service area that have both a ventilator and an operating room and have not been granted a waiver by CMS to work with another OPO."*
- **notes** Quote verified **byte-exact** against the pinned source by `tools/cite.py`. First locator filled; the element is now implemented rather than a TODO.

### core/lifecycle/timers/t_referral_response — **A CORRECTION**
- **layer** **L3** — *was drafted L0*
- **element** The bound on OPO response to a referral.
- **kind** mandate (that a definition must exist) + **site-authored** (what it is)
- **source** eCFR — 42 CFR Part 486, Subpart G, § 486.322(a)
- **locator** 42 CFR 486.322(a) · issue date 2026-08-24 · pinned, sha256 as above
- **accessed** 2026-08-26
- **establishes** *"The agreement must specify the meaning of the terms “timely referral” and “imminent death.”"*
- **notes**
  **This timer was mislayered, and verification is what found it.** It was drafted `layer: L0` on the
  assumption that a federally mandated response bound exists. The live text says the opposite: the CFR
  requires that *"timely referral"* be **defined in the agreement**, and does not define it federally.
  The bound is therefore **per donor hospital**, authored on site, and a validator that enforced one national
  figure would be enforcing something the rule does not say.

  Consequences, all applied 2026-08-26: the timer moved to L3; a new variation point
  `intake.timely_referral_definition` was added; the elicit coverage test immediately failed for having no
  question about it, and one was written.

  **This is the case for filling locators rather than deferring them.** An unverified element is not merely
  uncited — it can be *wrong in a way that moves a layer boundary*, and every hour it stays unverified is an
  hour the architecture rests on an assumption nobody checked.

### core/lifecycle/measures — **the whole graded regime, from the regulation**
- **layer** L0 · **kind** mandate
- **source** eCFR — 42 CFR 486.318(d) and (e)
- **locator** 486.318(d) regime · (d)(1)(i)-(ii) numerators · (d)(1)(iv) denominator · (e)(6) Tier 3
- **accessed** 2026-08-26 · quotes verified byte-exact
- **establishes** *"An OPO is evaluated by measuring the donation rate and the organ transplantation rate in their DSA."* Numerators, denominator and the tier thresholds are all codified, with one-sided 95% confidence intervals against top-quartile and median thresholds.
- **notes**
  Three things this changed. **(1)** The two-measure claim was previously sourced to a CMS fact sheet; it is now citable to the regulation. **(2)** The denominator is far more specific than "inpatient death records" — *patients 75 or younger, primary cause of death consistent with organ donation, most recent 12 months of state death certificate data.* **(3)** Tier 3 triggers on donation **or** transplantation — either measure, not both. Stricter than a summary conveys.

  **And a finding that changes a gate.** T5 requires a denominator be reconstructible as a fold over the tape. **This one is not**: donor potential comes from state death certificates, which are outside the OPO's record entirely. That is exactly what makes the measure hard to game — and it means the measure-denominator gate must verify reconstruction against an **external** source, not the tape alone. The gate as specified would have checked the wrong thing.

### SUPERSEDED · 42 CFR 486.318(a)–(c) — the three-measure regime — **A NEAR-MISS, RECORDED**
- **date** 2026-08-26 · **class** expired, still in the codified text
- **establishes** *"The outcome measures described in § 486.318(a)(1) through (3) are effective until July 31, 2022."*
- **notes**
  § 486.318(a)–(c) describes an expired three-measure regime and **is still present in the current codified text.** A search for "outcome measures" lands there *first*. Reading only the search hit would have produced a citation to law that has not been in force since 2022 — and **the byte-match gate would have passed it**, because the passage is real. It is merely dead.

  This is the documented limit of `tools/cite.py`, demonstrated rather than asserted: *passing means "not fabricated"; it does not mean "correct."*

  **Mechanical response, applied the same day:** the gate now scans the neighbourhood of every quote for sunset language and returns `CHECK-CURRENCY`. A human may close the warning only by recording *why* in a `currency_confirmed` field — never by silencing it. Five citations tripped it; each carries its reasoning. **The expired passage is retained in `citations.json` on purpose, so the failure mode stays visible instead of becoming a story.**

### core/lifecycle/states/death_determination
- **layer** L0 · **kind** mandate · **locator** 42 CFR 486.344(b)(1) · **accessed** 2026-08-26
- **establishes** *"Verify that death has been pronounced according to applicable local, State, and Federal laws."*
- **notes** The drafted claim said "separation of death determination from donation activity." The text is narrower and better: the duty is **verification of a pronouncement made elsewhere.** The system's constitutional prohibition on asserting death was already correct; it now rests on the regulation rather than on inference.

### core/lifecycle/states/reporting_closed · core/lifecycle/timers/t_data_reporting
- **layer** L0 · **kind** mandate · **locator** 42 CFR 486.328(d) · **accessed** 2026-08-26
- **establishes** *"Data reported by the OPO to the OPTN must be reported within 30 days after the end of the month in which a death occurred."* And: *"If an OPO determines … that the data it reported to the OPTN was incorrect, it must report the corrected data … within 30 days of the end of the month in which the error is identified."*
- **notes**
  **A real federal deadline with a number** — the contrast case to `t_referral_response`, which turned out to be per-agreement. One verification pass moved one timer out of L0 and put another firmly into it.

  And the correction clause is worth noting for its own sake: **the regulation is itself append-with-correction.** An error is *reported*, not erased. The tape's design was arrived at independently and then found already written into the rule.

### Batch 3 — **what was drafted as "OPTN Policy" was mostly in the CFR**

Four elements were drafted pointing at OPTN Policy, whose own site returns 403 to automated retrieval. **Three
of them are established by the CFR instead** — which is fetchable, and which nobody had checked.

### core/lifecycle/states/evaluation
- **locator** 42 CFR 486.344(c)(3)-(4) · **accessed** 2026-08-26 · verified byte-exact
- **establishes** *"Ensure that the potential donor's blood is typed using two separate blood samples."* and *"Document potential donor's record with all test results, including blood type, before organ recovery."*
- **notes** Typing requires **two separate samples** — a duplication requirement, not a single test. And results must be in the record **before recovery**, which makes completeness a **transition guard** rather than a reporting obligation. The lifecycle now enforces it as one.

### core/lifecycle/states/allocation
- **locator** 42 CFR 121.7(a)(1) and 121.7(b)(3) · **accessed** 2026-08-26 · verified byte-exact
- **establishes** *"An OPTN member procuring an organ shall operate the OPTN computer match program … to identify and rank potential recipients."* and *"An organ offer is made when all information necessary to determine whether to transplant the organ into the potential recipient has been given to the transplant hospital."*
- **notes** Ranking is performed by the **OPTN match program**; the OPO *operates* it and does not rank. This system's prohibition 6 — *it does not rank donors, recipients or families* — now rests on the rule rather than on our own restraint. And an offer is defined by **completeness of information transferred**, not by a message being sent: exactly the class of condition the gates check.

### core/lifecycle/states/packaging_transport
- **locator** 42 CFR 121.7(c) · **accessed** 2026-08-26 · verified byte-exact
- **establishes** *"…accompanied by written documentation of activities conducted to determine the suitability of the organ donor and shall maintain this document for one year."*
- **notes** Documentation travels **with the organ** and is retained a year. The record is a conserved artifact rather than a database row — which is why chain-of-custody continuity is a gate.

### core/lifecycle/L4 — the statutory basis for the tape
- **locator** 42 CFR 121.11(a)(2)(i) · **accessed** 2026-08-26 · verified byte-exact
- **establishes** *"All OPOs and transplant programs shall maintain such records pertaining to **each potential donor identified**, each organ retrieved, each recipient transplanted…"*
- **notes** Note the scope: **each potential donor *identified*** — not only converted cases. The non-conversion terminals (`ruled_out_medical`, `authorization_declined`, `no_organs_recovered`, `referral_lapsed`) are therefore **mandated record-keeping**, not a design choice this project made for tidiness. `referral_lapsed` remains marked a design choice because the *state* is ours; the *obligation to keep the record* is not.

### Batch 4 — OPTN Policies, and **the spine is established**

Operator downloaded the OPTN corpus live 2026-08-26. `optn-policies.txt` pinned, 374 pages, 752k chars,
**"OPTN Policies Effective as of August 1, 2025"** per the PDF's own title. Extracted text carries
`[[PAGE n]]` markers so every citation names its page.

**13 of 15 states established. 27 citations, all byte-exact, across three pinned sources.**

Highlights, each verified:

- **`referral_triaged` — OPTN 2.3(4):** *"Document in the deceased donor medical record if any of this information is not available and the reason it is not available."* **Missing information is itself a required entry, with its reason.** The ledger-of-silence property this project argued for on design grounds turns out to be *required by rule*.
- **`donor_management` — OPTN 2.13:** five enumerated duties, and the standard is **"reasonable efforts"**, not an outcome. A validator may check that effort was documented; it may never check that a physiologic target was met.
- **`authorization` — OPTN 2.14.E:** *"The host OPO may only recover organs that it has received authorization to recover."* A hard precondition, per organ.
- **`no_organs_recovered` — OPTN 2.14.E:** *"If an authorized organ is not recovered, the host OPO must document the specific reason for non-recovery."* The non-conversion terminal is a mandated record with a required reason code.
- **`recovery` — OPTN 2.14.B:** a written pre-recovery verification protocol per organ, and *"At least one of the individuals performing a verification must be an OPO staff member."* **Four eyes**, one of them the OPO's — and "qualified" is delegated to the OPO's own protocol, which makes it a local variation point.
- **`disposition` — OPTN 2.12:** *"…follow up and reporting of deceased donor test results received after procurement."* **Disposition does not close the case.** The record stays open to late-arriving truth — which is why L4 is append-only and a correction is an append.

### death_determination — **the original claim was right; the attribution was wrong**
- **locator** OPTN Policy 2.15.G (p.38) · verified byte-exact
- **establishes** *"The donor hospital healthcare team member who declares the death of the potential deceased donor cannot be involved in any aspect of the organ recovery procedure or transplantation of that donor's organs."*
- **notes** This element was drafted claiming "separation of death determination from donation activity," **corrected away** in batch 2 when it could not be found in the CFR, and now **recovered from its actual source.** Both are true: the CFR gives the OPO a duty to *verify*; OPTN Policy forbids the *declarer* from participating. The correction was right and the original instinct was right — only the attribution was wrong. Both citations are retained.

### authorization — **known-incomplete, and deliberately not resolved**
- **locator** PER-JURISDICTION — REQUIRES A STATE TABLE · **status** known-incomplete
- **notes** Every other locator in this file resolves to one document. The state-anatomical-gift-act leg resolves to **fifty-odd state statutes**, and no single citation can establish it. `authorization` therefore stays `verified: false` until a jurisdiction table exists with a citation per state. The variation is statutory rather than operational, so that table belongs in the seed — **a site does not get to author who may authorize donation.**

### A STATUS FLAG THAT COULD BE CLEARED BY REWORDING — **caught, and fixed**

Marking the UAGA locator `PER-JURISDICTION` instead of `TODO-VERIFY` **silently flipped `authorization` to
`verified: true`.** The generator's rule was *"the locator is not the literal string TODO-VERIFY"* — so
renaming it was enough. Nothing checked evidence.

That is the exact failure this ledger exists to prevent, committed by its own tooling, and it would have
reported a fully-established spine while one element rested on nothing.

**Fixed the same hour.** `verified` now requires **`quote_verified: true` on every provenance entry** — the
quote having been byte-checked against a pinned source. **A status flag that can be cleared by rewording is
not a status flag.** And because the reasons are not equivalent, the machine form now carries
`unverified_because`: `design-choice` (no source exists — the element is ours), `known-incomplete` (no single
citation can establish it), or `unverified` (nobody has checked). Conformance reports them separately.

### Correction · accessed dates
Twenty-nine accessed dates recorded as **2026-08-25** were corrected to **2026-08-26**, the true retrieval
date. Recorded here rather than quietly amended, per §9. Nothing material turns on the day, but a ledger
whose dates are approximate is not a ledger.

### Batch 5 — the clinical layer (L1), and the jurisdiction table left empty

**35 citations, all byte-exact.** `clinical/donor_testing.yml` created: blood type determination, subtyping,
the general risk assessment and infectious disease testing, every provenance block quote-verified against the
pinned OPTN corpus.

Three findings worth carrying forward:

- **L1 carries time, not only data.** *"…at least two donor blood samples **prior to the match run**"* (2.6.A)
  and *"Urinalysis, **within 24 hours before cross clamp**"* (2.8) are temporal constraints, not fields. They
  are marked `feeds_closure: true` and belong in `floor/closure.py` alongside the L2/L3 bounds. **The clinical
  layer meets the schedule**, which nothing in the design anticipated.
- **A conflict is withheld, not resolved.** *"If there are conflicting or indeterminate subtype results, the
  subtype results must not be reported to the OPTN and the deceased donor must be allocated based on the
  primary blood type."* (2.6.B) Not a tiebreak, not the more recent result — **withheld**, with a fallback to
  the safer type. The same shape this system uses everywhere: when the evidence does not settle, decline.
- **Two requirements that look like one.** CLIA-certified *laboratory* (2.9) and FDA licensed/approved/cleared
  *assay* (2.9(2)) are distinct properties. A certified lab running an unapproved test fails one; an approved
  test in an uncertified lab fails the other. **A validator checking only one is checking half a rule.**

`clinical/donor_testing.yml` declares four gaps in its own `incomplete` section — the remainder of the 2.9
panel, per-organ required information (2.11.A–E), hemodilution (2.5), and viability criteria. A
complete-looking L1 would be a claim; conformance now checks that the file names its gaps.

### core/authorization/jurisdiction.yml — **empty, and that is the point**

- **keyed_on** `donor_state_of_residence` · 42 CFR 486.342(b) · verified byte-exact
- **establishes** *"…in a manner that satisfied applicable State law requirements in the potential donor's **State of residence**"*
- **and** OPTN 2.14.E: *"…whether that be the donor or a surrogate donation decision-maker **consistent with applicable state law**"*

**The key is residence — not the state of death, not the hospital's state, not the OPO's.** Those differ
routinely: service areas span state lines and patients are transferred across them. A table keyed on the
hospital's state would be wrong in exactly the cases where it matters, and wrong silently. That was worth
finding before building the table rather than after.

Both the federal rule and OPTN policy **defer** on who may act as surrogate. Neither supplies the answer,
which is precisely why the table must exist.

**The fifty rows are empty.** They are not an oversight and not waiting on effort — they are waiting on
evidence of a kind nothing here has gathered: a pinned statute per state, each an adoption of some UAGA
vintage, each locally amended. The file carries the row contract, the procedure, and this:

> This is the one part of the seed where a byte-exact citation is **necessary and not sufficient** — a
> correctly quoted statute can still be misread, and the consequence of misreading it is not a bad metric.
> **An empty table is honest. A plausible one would be the single most dangerous artifact this project could
> ship.**

`authorization` therefore remains `verified: false`, reported as `known-incomplete`, and conformance reports
the table as PASS-UNVERIFIED with its reason rather than passing over it.

### Batch 6 — Texas filled, and the acquisition trap that nearly got past me

**38 citations byte-exact.** `core/authorization/jurisdiction.yml` has its first row: **Texas**, Health &
Safety Code Ch. 692A, RUAGA (2006) as adopted by Acts 2009, 81st Leg., R.S., Ch. 186, current through the
89th 2nd Called Legislative Session, 2025.

- **§ 692A.008(a)** — first-person authorization **binds**: *"a person other than the donor is barred from making, amending, or revoking an anatomical gift…"* Family cannot override a registered donor.
- **§ 692A.009(a)** — eleven classes in priority order. **Classes (10) and (11) — hospital administrator, and any person with authority to dispose of the body — are not in every state's list.** Copying this list one state over would authorise people who are not authorised.
- **§ 692A.009(b)–(c)** — a known objection inside a class escalates to a **majority of reasonably available members**, not unanimity and not first-to-answer.

`counsel_reviewed: false`, and the gate cannot set it. **This is the one part of the seed where a byte-exact
citation is necessary and not sufficient.**

### THE PROBE THAT LIED — recorded, because I acted on it

Before starting, I probed whether Texas statutes were fetchable and reported **"it fetches"** on the strength
of an **HTTP 200 and 250,874 bytes.** That was wrong, and I stated it in a brainstorm as though it were a
finding.

`statutes.capitol.texas.gov` is an Angular single-page application with catch-all routing. **Every path
returns the identical 250,874-byte shell with HTTP 200** — the statute URL, a PDF path, a ZIP path, a
nonsense path. The statute text is never in it. Texas was eventually retrieved with a headless browser.

**A fetch loop over fifty states would have reported 50/50 success and written fifty copies of Angular
boilerplate.** `tools/cite.py` would have caught it downstream — no quote would byte-match — but only after
somebody spent a day writing rows against nothing.

I checked a status code and called it evidence. That is the exact failure this repository is built to refuse,
committed by its author, in a brainstorm, one turn before building the thing that refuses it.

**What came of it, and it is worth more than the row:**
- `fetch_states.py` validates **content, never status codes**. A download succeeds only when the bytes
  contain statutory language; anything else is a MISS that names its reason. Running it against Texas
  correctly reports MISS — **the script's own demo case is the failure it exists to catch.**
- `PROCEDURE.md` opens with it, before any instruction: *"Do not trust an HTTP 200."*
- The Texas row carries an `acquisition` field recording that curl cannot reach it.

### The reframe — fifty one-state problems, not one fifty-state problem

This table was written up as *"large and left undone."* Wrong frame, and wrong in a way this project should
have known better than: it is **fifty one-state problems, each with a natural owner better placed than this
repository's author** — the OPO operating under that statute, whose counsel has already read it.

So a **third category** now exists alongside seed and site-patch: **contributed**. A jurisdiction row is not
configured, it is contributed upstream. A site does not get to *decide* who may authorize donation; a site is
exactly the right party to *cite* its own state's statute.

And there is an asymmetry that makes it work. A site's L2/L3 fit is **deliberately worthless to anyone
else** — which means the repository is take-only by construction, and no site has any reason to push. A
jurisdiction row inverts that: worth little to its author alone, valuable to the other fifty-four, and
**because service areas span state lines you will need rows you did not write.** It is the first artifact
here with a real reason to contribute back.

### Batch 7 — NOTA, and the authority chain made explicit

**41 citations byte-exact, five pinned sources.** The National Organ Transplant Act pinned from the official
GPO text (`USCODE-2024-title42-chap6A-subchapII-partH`, 42 U.S.C. §§ 273–274g). The 2024 edition was taken
after checking that 2023 and 2024 carry the same substance — an edition choice recorded rather than defaulted.

- **42 U.S.C. 274(a)** — the statutory basis for the OPTN. The top of the chain.
- **42 U.S.C. 274e(a)–(b)** — the organ-sale prohibition is **statutory and criminal**, not a policy
  restatement. OPTN Policy mirrors it; the offence lives here, with penalties of up to $50,000 or five years.

That last one bears on design and is worth stating: it is **the one place where a record system's contents
could become evidence in a prosecution.** That is an argument for the tape being tamper-evident and
exportable rather than merely durable — a property arrived at for other reasons and now with a second one.

### core/authority/chain.yml — on whose authority does this system refuse things?

Six tiers, statute to site fit, each naming **how it changes and on what clock**:

| | Tier | Changes by | Clock |
|---|---|---|---|
| 1 | NOTA (42 U.S.C. 273–274g) | Act of Congress | years to decades |
| 2 | OPTN Final Rule (42 CFR 121) | HHS rulemaking | years |
| 3 | Conditions for Coverage (42 CFR 486 G) | CMS rulemaking | **years — a revision is in flight now** |
| 4 | OPTN Policy | board action, Secretarial review | **months — the fastest above the site** |
| 5 | State law | fifty-odd legislatures, independently | unpredictable, unsynchronised |
| 6 | The site's fit | the site, under signature | as often as the operation changes |

Three things this buys that the layer stack alone did not:

- **Any refusal should be traceable to a tier.** If it is not, it is this project's opinion wearing a gate's
  clothing, and it should be removed or marked a design choice.
- **It tells you what goes stale first.** Tiers 4 and 5 move fastest, so a re-verification schedule should
  follow that ordering rather than treating every citation as equally durable.
- **It bounds a completion.** A harness authoring a site fit works at tier 6 only. A proposed row that would
  require changing tiers 1–5 is not a fit — it is a request to change the law, and the correct response is to
  say so.

Tier 5 is the only one federal authority does not determine, and the only one keyed on a fact about the
**donor** rather than the OPO. Conformance checks that every tier names its clock: **a tier that cannot say
how it changes is not an authority, it is an assertion.**

---

### Design choices, marked as such

Per §5, a design choice mislabelled as a mandate is the most damaging error this ledger can contain. These
are choices. Nothing above compels them.

### core/lifecycle/states/referral_lapsed
- **layer** L0 (structural)
- **kind** **design-choice**
- **source** none — introduced by this project
- **accessed** 2026-08-26
- **establishes** Nothing. It is not a mandated state.
- **notes** Added so that non-progression is representable. A referral that quietly stops moving is a real and measurable failure with **no event, only an absence** — and a state machine with no terminal for it cannot express the thing the missed-referral audit is about. Marked a design choice so no reader mistakes it for policy.

### floor/closure.py — integer (min,+) arithmetic
- **layer** floor
- **kind** **design-choice**
- **source** classical result: an STN is consistent iff its distance graph has no negative cycle; minimal network = all-pairs shortest paths
- **accessed** 2026-08-26
- **establishes** The algorithm is standard and not this project's invention.
- **notes** The *choice* is whole minutes and integer arithmetic with `INF = 0x3f3f3f3f`. Exactly associative, no floating point, no drift — which is what lets an accelerated implementation be compared to this one **by equality rather than tolerance**, and is therefore a precondition of replay determinism rather than a style preference.

### fixtures/ — JSON rather than YAML
- **layer** fixtures
- **kind** **design-choice**
- **accessed** 2026-08-26
- **notes** So the floor runs on a bare Python with nothing installed. A reference artifact that requires a dependency install before it does anything is a worse reference artifact.

### fixtures/cases/* — all values illustrative
- **kind** **design-choice**
- **accessed** 2026-08-26
- **notes** Every duration in every fixture is **synthetic and illustrative**, including the cold-ischemia budget in `infeasible-transport.json`. Organ-specific ischemia tolerances are clinical figures requiring citation to published literature before any validator enforces one; `t_cold_ischemia` in the lifecycle file is deliberately TODO-VERIFY. **No fixture value should be read as a clinical or regulatory claim.**

---

## §7 · Contested, superseded, and excluded

Where a source was consulted and **not** relied upon, it is recorded here with the reason. Sources are subject
to the same funeral discipline as everything else in this project: **what was rejected, and why, is part of
the record.**

### Excluded — CMS and Federal Register primary sources, retrieved indirectly
- **date** 2026-08-26
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

*v0.1 · 2026-08-26 · Rev 0, specification. The ledger is empty because the seed is unbuilt, and it will be
written one row at a time, in the commits that build it.*
