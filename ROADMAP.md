# ROADMAP

**A Poincaré disk, not a Gantt chart.** The centre is exact because it is next; the edge compresses because it
is far. Everything beyond the horizon is still *in* the disk — bounded, named, not pretended into precision.

**Read it with the claim grammar of everything else here:** `[M]` measured with a receipt · `[V]` verified,
source named · `[D]` derived · `[SPEC]` designed, unbuilt · `[BET]` kill condition named · `[NULL]` the
baseline it must beat. **Where this and a dated receipt disagree, the receipt wins.**

**Standing rule, and it governs the whole document: no rung ships without its null.** If the cheap baseline
wins, the funeral prints and that rung dies. A roadmap that cannot lose is a brochure.

---

## Where it stands · `2026-08-26` · 40 GREEN · 6 PASS-UNVERIFIED · 0 FAILED

| Built | State |
|---|---|
| L0 spine, cited | 13/15 states established · 41 citations byte-exact · 5 pinned sources |
| L4 tape | append-only, hash-chained, no delete/update **by type** |
| replay | refuses illegal transitions; guards enforced where provenance allows |
| the algebra | `mount`/`retire`/T3 computed — the invertibility gate **decides** |
| the floor | the temporal closure; the argmin path *is* the citation |
| gates | twelve, three states, defects named in words |
| the kit | `elicit/` 20 questions · a worked patch · **four refused drafts** |
| profiles | `edr` ⊂ `forge`, checked not trusted |
| percepts + switch | six ported laws · `off` is inert · fails toward inert |
| provenance | byte-match or refused · sunset detection · `[M]` |

| Not built | Why it matters |
|---|---|
| **`adapters/`** | **empty — and it is the largest share of the six years** |
| `clinical/` gaps | the 2.9 panel remainder, 2.11 per-organ, 2.5 hemodilution |
| `t_cold_ischemia` | clinical literature, not policy |
| ~50 jurisdiction rows | **theirs, not ours** — contributed upstream |
| the resident | gated on F-PATCH-DELTA |
| the harness, composed | present, uninstalled, unpinned, unwired |

---

# I · THE CENTRE — exact, because it is next

## 1 · `adapters/` — the shape for the layer that eats the years `[NEXT]`

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

## 2 · Two afternoons, in parallel, neither blocking the other

**Pre-register F-PATCH-DELTA.** Write what counts as success *before* anything runs. Three arms:
**① template-prior** (generic OPO defaults, no site material — **the floor; without it a passing arm 2 might
just mean the schema is fillable by anyone**) · **② prompted harness** on public material for a second OPO ·
**③ resident** — later, and arm 2 is its null.

**Expect the pre-registration to surface a problem**, which is why it is cheap: how much public material for a
second OPO actually exists? A website, an annual report, CMS data. If that is too thin, **the test is unfair
and a negative result is uninformative — and finding that out costs an afternoon rather than a weekend.**

**Pin the chassis.** Blocking, and it now blocks *wiring* rather than acquisition — the bytes are already
here. `internal` §14 item 1. **Unpinned third-party code must not become load-bearing.**

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

**The `holds` block.** What a completing harness considered and declined, per target, with the reason.
**Today a harness that smooths over a contradiction and one that never saw it produce identical output.** And
`sources contradict, unresolved` is the single highest-value line a completion can emit: it is a finding
*about the organisation*.

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
loses an organ. **Twelve gates ship with four adversarial fixtures — the eight without witnesses are the
exposure**, and they were written by the same author as the gates.

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
