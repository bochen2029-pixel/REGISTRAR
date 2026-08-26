# ROADMAP

**A Poincaré disk, not a Gantt chart.** The centre is exact because it is next; the edge compresses because it
is far. Everything beyond the horizon is still *in* the disk — bounded, named, not pretended into precision.

**Read it with the claim grammar of everything else here:** `[M]` measured with a receipt · `[V]` verified,
source named · `[D]` derived · `[SPEC]` designed, unbuilt · `[BET]` kill condition named · `[NULL]` the
baseline it must beat. **Where this and a dated receipt disagree, the receipt wins.**

**Standing rule, and it governs the whole document: no rung ships without its null.** If the cheap baseline
wins, the funeral prints and that rung dies. A roadmap that cannot lose is a brochure.

> ### Working in parallel? Read [`FORKS.md`](FORKS.md) first.
>
> As of `2026-08-26` this work is deliberately split across concurrent sessions. `FORKS.md` carries the
> write-surface partition, the shared-file rules, and **the one constraint that is not negotiable:**
> **`deepseek-harness-master/` is read-only to every fork.** It is pinned byte-for-byte against upstream,
> and writing inside it converts a composition into a fork — the exact failure *compose, never fork* exists
> to prevent. **Plugins are mounted beside it, never added to it.**

---

## Where it stands · `2026-08-26` · 50 GREEN · 9 PASS-UNVERIFIED · 0 FAILED · 396 assertions

| Built | State |
|---|---|
| L0 spine, cited | 13/15 states established · 44 citations byte-exact · 5 pinned sources |
| L4 tape | append-only, hash-chained, no delete/update **by type** |
| replay | refuses illegal transitions; guards enforced where provenance allows |
| the algebra | `mount`/`retire`/T3 computed — the invertibility gate **decides** |
| the floor | the temporal closure; the argmin path *is* the citation |
| gates | **sixteen**, three states, defects named in words |
| the kit | `elicit/` 20 questions · a worked patch · **four refused drafts** |
| profiles | `edr` ⊂ `forge`, checked not trusted |
| percepts + switch | six ported laws · `off` is inert · fails toward inert |
| provenance | byte-match or refused · sunset detection · `[M]` |

| Not built | Why it matters |
|---|---|
| ~~`adapters/`~~ | **the SHAPE now exists** — contract, `lab/` worked, battery. Bindings `null`. |
| `clinical/` gaps | the 2.9 panel remainder, 2.11 per-organ, 2.5 hemodilution |
| `t_cold_ischemia` | clinical literature, not policy |
| ~50 jurisdiction rows | **theirs, not ours** — contributed upstream |
| the resident | gated on F-PATCH-DELTA |
| the harness, composed | present, uninstalled, unpinned, unwired |
| adapter **bindings** | `null` — a real integration needs specs an OPO holds |

---

# I · THE CENTRE — exact, because it is next

## 1 · `adapters/` — the shape for the layer that eats the years `[DONE 2026-08-26]`

**The thesis says L2/L3 is the six years. L3 is most of it** — *which donor hospitals run which EHR and at
what version, reference-lab interfaces and result formats, imaging, e-signature, transport.* An OPO with
forty donor hospitals has forty integration surfaces. **That is where an in-house build dies**, not in the
lifecycle, which is law and identical everywhere.

Four things are waiting on this directory:

- **`elicit/` asks four tier-4 questions and nothing catches the answers.** `SPEC.md` §5 promises *"typed
  shells with conformance tests, so completing one is filling a shape rather than inventing one."* **There is
  no shape.**
- **Cordis has no reason to exist yet.** Seven long-lived connectors that must load, fail, reload and unload
  **without restarting a records system mid-case** is the paper's own motivating scenario — and a donor case
  is exactly the in-flight task it names. Until adapters exist, the runtime argument is theoretical.
- **F-PATCH-DELTA tests the easy half without it.** Most of a real delta is L3.
- **`clinical/`'s gaps have no consumer** — lab result formats are where L1 and L3 meet.

**Deliverable — the shape and one worked instance, not seven integrations:**

| | |
|---|---|
| `adapters/CONTRACT.md` | what any L3 adapter declares: ingests · lifecycle events it may produce · failure modes · **its own null** |
| `adapters/contract.json` | the machine form, so a gate can check a binding |
| `adapters/lab/` | **the worked one.** Serology gates the match run; the reference-lab turnaround is already the sharpest row in the worked example — *"the contract says four hours, the laboratory takes six."* |
| `adapters/conformance.py` | an adapter that cannot demonstrate it handles a **malformed** result, a **late** result, and a result arriving **after disposition** does not mount |
| `fixtures/adapters/` | synthetic, adversarial, **zero PHI** |

**What is deliberately NOT built:** a real Epic, Cerner or Meditech integration. Those need interface specs an
OPO holds, and **inventing them is exactly the fabrication the citation gate exists to prevent.** Vendor
bindings ship `null`, the same pattern and the same reason as `forge/plugins.yml`: **the seed declares what
must be true of an adapter; the site binds the one it actually has.**

`[NULL]` — a coordinator retyping from a screen. **Every adapter must name what it replaces and beat it.**

**SHIPPED.** `CONTRACT.md` (five refusable declarations) · `lab/adapter.yml` (the worked one) ·
`conformance.py` (10 GREEN · 3 PASS-UNVERIFIED · 0 FAILED, and PASS-UNVERIFIED is the honest state for an
unbound shell). **And the battery caught a trap on its first run, on the first adapter:** a bare `null:` key
is a YAML reserved word that parses as the **None key**, so the field vanished and the adapter read as having
declared no null at all. Renamed to `beats:`, and **the checker now refuses the trap** rather than tolerating
it, so no future adapter can lose a field the same way.

**What is next here, and it is not more shells:** an adapter that has a real binding. That waits on a site.

## 2 · Two afternoons, in parallel, neither blocking the other

**Pre-register F-PATCH-DELTA.** Write what counts as success *before* anything runs. Three arms:
**① template-prior** (generic OPO defaults, no site material — **the floor; without it a passing arm 2 might
just mean the schema is fillable by anyone**) · **② prompted harness** on public material for a second OPO ·
**③ resident** — later, and arm 2 is its null.

**It surfaced one, and it was worse than "thin" — `2026-08-26`.** `experiments/F-PATCH-DELTA/PREREGISTRATION.md`
§0, reproducible via `audit_public_material.py`:

> **0 of 13 evidence items in the worked example are public. 0 of 20 elicit questions name a public source.**

They name the case tape (×11), SOPs, the call rotation, service-desk history, written hospital agreements,
and lab and transport contracts. **None publishable — and that is the thesis rather than an oversight.** An
OPO's public surface describes *what it is*, not *how it runs*.

**So the experiment as specified would have measured the material, not the harness**, and a negative result
would have been uninformative. **Arm ② is now a synthetic site with a known delta**, with its cost stated up
front: *it tests whether the KIT is completable, not whether a REAL OPO is legible.* **A pass is necessary
and not sufficient; a failure is decisive.** Grading against STA was considered and **refused** — the ground
truth would be recollection of a former employer's design, which `PROVENANCE.md` §4 makes inadmissible.

**PRE-REGISTERED.** Gate battery pinned at `87c463d`. Rubric, thresholds, and invalidation conditions all
fixed before any corpus was written.

**CORPUS BUILT · ARM ① RUN · ARM ② BLOCKED — `2026-08-26`.** See
[`experiments/F-PATCH-DELTA/RESULTS.md`](experiments/F-PATCH-DELTA/RESULTS.md).

- **`site/`** — Fairbank Donor Network, fictional. 1,186 raw case events, four SOPs, two contracts, an
  integration inventory. **Three binder/tape contradictions in both directions**, and **one target nothing
  supports.**
- **Arm ① — the template prior: `19/40 · S = 0.47 · 1 fabrication · SHAPED`.** **The floor is already at
  SHAPED**, so arm ② clearing 0.40 would mean nothing — it must beat 0.47 by a real margin. §5 anticipated
  this: *if ① scores near ②, the schema is doing the work and the harness is not.* **Thresholds not adjusted;
  §6 forbids it.**
- **The gates refused arm ① independently, without the answer key** — evidence binding caught *"asserts
  generality, not this site"*, and 20/20 shadow runs had no denominator. **A harness could produce arm ① at
  any site and the battery would refuse it at every one.**
- **ARM ② RUN — `S = 0.57`, ZERO fabrications, SHAPED.** A session that did not build the corpus. It
  **declined to score itself** (reading per-target output would be the delta *"in any form"*), skipped
  §3 rather than reading around it, and disclosed an `internal/` grep hit it did not open.
- **Floor 0.47 → candidate 0.57, and the gap is exactly where the site departs from the industry.** All
  three planted contradictions resolved to the tape rather than the binder; the unanswerable target was
  **declined rather than filled** — arm ① fabricated there. Those four targets are the whole difference.
- **Gates: 10/13 GREEN, identical at HEAD and at the pin.** The §6 deviation is **neutralised** — Fork C's
  gate-13 fix did not change the verdict, and that null delta is itself the measurement Fork C predicted.
- **THE CORPUS HAD TWO DEFECTS I DID NOT PLANT, AND THE CANDIDATE FOUND BOTH TO THE EXACT COUNT** —
  `after_hours` is an independent coin flip contradicting the stated business hours in 197 of 420 rows, and
  `H-1490` is called low-volume at four referrals while the tape carries 71. **It surfaced both rather than
  smoothing either**, and declined to adjudicate the second because the tape is undated. Recorded as an
  instrument defect; **the corpus is NOT being corrected, because changing it after a run would invalidate
  the comparison.**

**Pin the chassis.** Blocking, and it now blocks *wiring* rather than acquisition — the bytes are already
here. `internal` §14 item 1. **Unpinned third-party code must not become load-bearing.**

## 2b · The three-way split `[2026-08-26]`

Concurrent, partitioned by write surface, contract in [`FORKS.md`](FORKS.md).

| Fork | Plan | Doing | Owns |
|---|---|---|---|
| **mainline** | [`plans/MAINLINE_f-patch-delta.md`](plans/MAINLINE_f-patch-delta.md) | pre-register the falsifier, then run arms ① and ② | `experiments/` |
| **A** | [`plans/FORK-A_plugins.md`](plans/FORK-A_plugins.md) | fold the estate tools in as forge capabilities; mount the first two as dsh plugins | `forge/plugins/`, `forge/dsh/` |
| **C** ✅ | [`plans/FORK-C_witnesses.md`](plans/FORK-C_witnesses.md) | **a witness for every gate** — DONE: 9 witnessed, 3 entangled, 1 undecidable; **7 exposures found and retained** | `examples/worked/rejected/`, `gates/test_*.py` |

All three dated `2026-08-26`, branch point `9a1a5f7`. **Each plan is self-contained** — a session with no
prior context can pick one up and work from it. The shared constraints live in [`FORKS.md`](FORKS.md) and
are binding on all three.

**Fork A, in one line:** level 1 is *a bound capability* — the tool lands under `forge/plugins/<id>/`, adapted
rather than copied, and `binding:` stops being `null`. Level 2 is *a mounted dsh plugin* — a thin package
that registers the capability as a **tool in the harness's registry**, so a model discovers it instead of
being told about it. **Level 1 for all of them; level 2 for `chunk` and `phi_scan` only, at first.**
**Licences are a hard prerequisite** — only one estate tool currently carries one, and the contract refuses a
mount without SPDX.

**Fork C, and why it earned a whole session:** at the branch point the battery shipped with **four**
adversarial fixtures and most of its gates had no evidence they could fire — and the four that existed were
written by the same author as the gates they tested. That is `SPEC.md` §14's *first-ranked* risk, unmeasured.
**Counts as of the branch point are deliberately not restated here; the current ones are in the table above
and the update under *What would kill it*.** **And it makes the falsifier stronger:** F-PATCH-DELTA
grades against these gates, so a weak battery makes its verdict weak in the same proportion — a pass could
mean *the harness did well* or *the battery is easy*, with nothing to tell them apart.

**One coordination point:** F-PATCH-DELTA's pre-registration **pins the gate battery it grades against**, by
commit SHA. Pre-registration fixes the instrument; a rubric that shifts while Fork C strengthens the gates
underneath it is not pre-registered. Fork C's work applies to the *next* run, **and the delta between the two
runs is itself informative.**

## 2c · The capabilities the forge did not know it needed `[2026-08-26]`

Fork C, reading two estate organs, found **the enumeration tax inside `forge/plugins.yml` itself** — five
capabilities chosen in advance, in the artifact that names work-as-imagined as the central problem. See
[`plans/PROPOSAL_read-and-reach.md`](plans/PROPOSAL_read-and-reach.md), acted on the same day.

- **`read`** — induce a schema from a corpus nobody can read. Declared, `binding: null`. **Carries the rule
  that keeps it from breaking T4:** an induced variation point is a *proposal to the seed*, never a patch
  row. And **induction does not subsume the twenty questions** — a corpus reflects what an organisation
  records, so induction inherits the blind spots of the recording practice.
- **`reach`** — addressable retrieval, every answer carrying its precision bound. Declared, `binding: null`,
  **`beats: chunk`.** *Chunking is what you do when you have no index.*
- **`attest` — BUILT, gate 16.** The fence: evidence *no longer in force*, evidence *denying its own bound*,
  and *modality mismatch* — `may` is not `must`. **Not mountable** — a fence a site can swap is not a fence,
  and declaring it a capability was a category error the forge checker caught.

## 3 · Two cheap gates with real teeth

**The divergence gate — DONE `2026-08-26`, gate 13.** Every row exists three times — what it **says**
(`value`), what it **cites** (`evidence`), what **happened** (`shadow_run`) — and the twelve existing gates
checked each separately while nothing checked that they agree. **The catches live in the disagreements, and
formatting is what hides them.**

It refuses: a value its evidence contradicts · **a value rounded DOWN from its evidence** (optimism computes
deadlines wrong in the direction that loses organs) · a shadow run whose arithmetic does not close · a
numerator above its denominator · a replay over zero cases · a `derived_from` that names no method. It flags:
an evidence `n` that disagrees with the replay's.

**And it accepts conservative rounding**, because this repository's own rule is to round up — *p75 or higher,
p90 where the figure feeds a latest safe start.* A gate that punished the rule being followed would be worse
than no gate.

**Three of its first four findings were the GATE being wrong, not the rows** — identifiers read as claims, a
value rounded up read as divergence, and *"four hours"* unread because the scanner only saw digits. Each is
now a test. `[NULL]` — human review, which reads three fields as one story because they are formatted as one.

**The `holds` block — DONE `2026-08-26`, and it became gate 15.** What a completing harness considered and
declined, per target, with the reason. **Found by measurement, not inspection:** F-PATCH-DELTA's arm-②
candidate accounted for 20 of 20 targets unprompted, and checking the **worked example** against the same
standard showed **8 rows and 12 silences.** *The file everyone is told to copy was demonstrating the defect.*

`accountability` now refuses a patch silent on any declared target — **a target with no row and no hold is
indistinguishable from one nobody looked at.** Twelve holds added to the worked example, two of them
`sources_contradict`, which is *a finding about the organisation rather than a gap in the work.*

**And the field shape was adopted from the run rather than invented here** — the candidate had independently
produced `target/tier/reason/searched/detail`, separating the verdict from the explanation and adding the
authority tier. Better than what this repository first proposed.

**The kit was corrected to match.** `AGENTS.md` §7b and `elicit/method.md` now ask for what the gate
requires — and a section of `method.md` that said **"leave it out"** was in direct contradiction. Its
correction is kept visible rather than edited away, because *the sentence beneath it was right*: **the
questions you cannot answer are themselves a finding — and "leave it out" threw that finding away.**

---

# II · THE MIDDLE BAND — shape known, detail earned by doing

## 4 · Run F-PATCH-DELTA `[BET · the falsifier]`

One weekend. No PHI. Nobody's permission. **Run it with a GENERIC harness, and that is a feature:** if the
seed is only completable by our stack, **we built a product rather than a seed, and the completability thesis
is false in the way that matters most.**

Three publishable outcomes, and **all three are worth publishing:**

- **covers the delta** → the first receipt, and everything downstream is justified
- **shallow but correctly shaped** → **the expected result**, and the most useful: it says *how much
  observation the fit actually requires*
- **confidently wrong** → **the funeral prints**, and the honest product is an excellent open-source spine
  with a human implementation guide — **still more than exists today**

## 5 · F-BOOT — make a clone deliver a *composed* harness

The full dsh tree is already in the root. What is missing is narrower than absence: **never installed, unpinned, stock rather than composed, every plugin binding `null`, FUSOR not mounted.** Four pieces: **pin ·
compose a boot profile · bind `chunk` and `phi_scan` · mount FUSOR toggleable.**

**Independent of F-PATCH-DELTA in both directions** — that conflation is corrected and must stay corrected.

## 6 · Close the seed's remaining provenance

The `clinical/` transcription gaps · `t_cold_ischemia` (**cite the paper, not the consensus**) · the 2/15
states, which are open for **non-equivalent reasons** and must not be collapsed: `authorization` is
`known-incomplete` (fifty statutes, no single citation can establish it), `referral_lapsed` is
`design-choice` (**no source exists; the state is ours**).

## 7 · The jurisdiction table — **contributed, not built**

~50 rows, and **not a backlog anyone here intends to work through.** They belong to the OPOs operating under
them, whose counsel has already read the statute. **The asymmetry is what makes it work:** an L2/L3 fit is
*deliberately worthless to anyone else*, so the repository is take-only by construction — a jurisdiction row
inverts that, being worth little to its author and a great deal to the other fifty-four. **And because
service areas span state lines, you will need rows you did not write.**

`PROCEDURE.md` + `fetch_states.py` + `state_sources.json` make one row about an hour. **`counsel_reviewed`
stays a human act no automated check can set.**

---

# III · THE OUTER BAND — direction certain, timing not

## 8 · The resident `[BET]`

Gated on F-PATCH-DELTA. `percepts/` already carries the six ported laws; **what is missing is the trained
judge.** Then: **escalation** — *the resident may escalate the **shape** of a problem, never the **material***,
with every payload constructible from the public seed plus its own prose, **checkable** · **the on-site
disposition tune** — the site's own tape is retro-labelable because *the future is on the tape*, so **every
site's tune differs because every site's tape differs: the stem cell at the weights layer, and it never
egresses.**

`[NULL]` — **a weekly cron.** Re-run the harness every Monday. The only reason to think it loses is that
**the clock is state-blind and the flood is breadth.** *If a resident does not beat a weekly cron on the
site's own ledger, the resident is theatre.*

## 9 · Self-extension — level 3, where Cordis becomes load-bearing

The instance **authors a plugin, shadow-runs it, proposes it**; one yes mounts it hash-pinned, drift demotes,
**retirement unwinds through the disposer.** The patch contract applied to *capability* instead of
*configuration*. **A one-way door on any substrate without reversible effects** — which is the whole reason
the runtime is not interchangeable.

**Affordable at the forge radius in a way it is not at the case radius: a forge plugin that is wrong wastes an
afternoon; an EDR plugin that is wrong touches a case.**

## 10 · R6 — first site completion, under signature

Time from clone to first signed patch. Rows accepted versus rejected. **The first real `[M]` this project
will own**, and the first time the fence is tested by someone who did not build it.

## 11 · The packaged chassis

An executable with an embedded runtime, so nobody meets a console. **The room, not the engine** — and it must
be **whole at every rung**: at `off` a complete client that beats its own null, at `shadow` the ledger, at
`live` the seat. *No surface may exist that only makes sense at `live`.*

---

# IV · THE HORIZON — bounded, named, not pretended into precision

**Fifty-five completions**, and the structural risk that they become **fifty-five private forks** — how
comparable open-source healthcare projects have ended. **Confluence only works if the patch path is so much
easier than the fork path that forking is irrational.** *If the repository merely discourages editing L0,
someone will edit L0.*

**The measures computed from a site's own tape**, so an OPO sees its CMS-shaped numbers the day it turns on —
**a product on its own, before anything else here is built.**

**The regulatory cycle turning under all of it.** The final rule lands late 2026; Tier 2/3 proceedings begin
January 2027. **Tier 4 (OPTN Policy) moves in months and is what goes stale first.** Re-verification follows
the clocks, not the calendar.

**Whether any of this is adopted at all** — which is not an engineering question and will not be answered by
building more.

---

## What would kill it, in order of likelihood

**1 · A weak battery.** *The central risk is not a wrong patch.* A foreign harness produces confident,
plausible, wrong work all day, and the gates are the only thing between that and an organisation where wrong
loses an organ. **At the three-way branch point the battery shipped with four adversarial fixtures and most
gates had no witness — that was the exposure**, and the fixtures that existed were written by the same author
as the gates they tested.

> **Updated `2026-08-26`, after Fork C.** The sentence above described the state at the three-way branch point
> and is kept because it is the reason the fork was launched. **Now: sixteen gates, nine witnessed, three
> entangled with a structural floor, one undecidable from a file — and seven exposures found and RETAINED**
> as fixtures that pass (`examples/worked/rejected/*UNCAUGHT*`). The risk did not go away; **it got measured,
> and it changed shape — from most of the battery having no evidence it could fire, to seven NAMED holes
> that no semantic gate catches.** All seven currently trip a floor gate for being minimal — *and conformance says in words that
> this is not closure.* **The next move on this risk is a well-formed variant of each of the seven: if one
> passes clean, that is the highest-priority gate in the project, identified by measurement rather than
> intuition.**

**2 · The completability bet fails.** F-PATCH-DELTA returns *confidently wrong*. **Then the honest product is
the spine plus a human implementation guide, and the page says so.**

**3 · Forks, not patches.** See the horizon.

**4 · The transfer bet.** Every FUSOR receipt was measured on **dev streams, not donor cases.** The transfer
is a bet in every case and is listed as one.

**5 · Nobody stands up a local model.** The reference deployment answers it by demonstration `[OA]`; a
*different* OPO's security officer is an R6 question.

---

*Nothing here has run inside an OPO. No patient data has touched any part of it. There are no clinical
performance numbers because there are none — when that changes, the plate changes first and the prose
follows.*
