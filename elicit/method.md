# How to run an elicitation

**Read this before pointing anything at anything.**

The goal is one file: `<your-slug>.patch.yml`, describing how your organisation differs from the mandated
spine, with every row cited to something in your own building. Twenty questions, in
[`questions.yml`](questions.yml), keyed to the nineteen variation points the seed declares.

**You can do this entirely by hand.** The questions are the artifact; the software only makes it faster and
checkable. If you read nothing else here, read the `trap` field on each question — that is where the answers
actually go wrong.

---


## The one rule that matters most

**Interview the material, not the coordinators.**

Not because people are unhelpful — because the person who knows the most about how a case runs is, right now,
running one. That is the structural reason this took six years by the conventional method, and it is the
reason it does not have to any more: **the answers are already on your disk.**

Your SOPs. Your ticket history. Your interface configurations. Your QA exception log. Your escalation threads.
Your OR scheduling correspondence. Your case tape. All of it readable in an afternoon by something that reads
quickly, none of it requiring anyone to stop what they are doing.

Take questions to people **after** you have a draft — not to gather the answers, but to be told which of your
answers are wrong. That is a twenty-minute conversation instead of a six-month programme, and it is a far
better use of a coordinator than an interview.

---

## PHI: the two-model split, and why it is not optional

There are two reading jobs here and they must not be done by the same thing.

| Reads | Which model | Data class |
|---|---|---|
| **The seed** — this repository, its schema, its gates, its fixtures | any frontier coding harness | public, MIT, **zero PHI**. Nothing to protect, nothing to negotiate, **no BAA required.** |
| **The site** — your SOPs, tickets, configs, tape, screens | an open-weight model on **hardware you own** | **PHI-bearing. Never egresses.** |

**Never place PHI in a prompt, a tool call, a commit message, a log line, a patch row, or an evidence field** —
regardless of what agreement you believe covers the endpoint. That determination is not the operator's to make
in the moment.

**PHI is more than names.** Dates and times bound to a specific case, medical record numbers, donor
identifiers, a hospital name bound to an event, free-text clinical notes, and any combination that
re-identifies. **A single unusual case can be re-identified from timing alone.**

Three things make this tractable rather than paralysing:

1. **Most of what you need is not PHI, by design.** SOPs, org charts, call rotations, interface configs, QA
   thresholds, lab contracts and escalation ladders are operational documents. Work from those.
2. **What you need is timing and completeness, not clinical content.** If you find yourself reading a
   patient's clinical narrative to write a patch row, you have taken a wrong turn.
3. **Aggregate, then cite.** An evidence field should read *"p75 elapsed was 6h04m over 402 cases, 2025"* —
   never a case. The count is the evidence. The case is not.

**If you cannot tell whether something is PHI, it is.** Stop and ask your privacy officer.

---

## Work-as-done, not work-as-imagined

**The binder describes work as imagined. The organisation runs on work as done. The gap between them is the
entire value of what you are writing.**

When the documented process and the observed practice disagree, **encode the observed practice and cite both.**
A row that says *"the SOP says the supervisor owns conflicts; the ticket history shows the house coordinator
owns them in 128 of 134 cases"* is worth more than the rest of the file, because it is the thing no policy
document anywhere contains.

Nobody reports a workaround, because from the inside it is not a workaround — it is the job. So look for the
**shapes** that indicate one:

- a spreadsheet that shadows a screen
- a field that is always empty
- a phone call that substitutes for a system
- a step consistently done in a different order than documented
- a recurring ticket describing the same manual fix
- a rule everyone follows that appears in no document

That last one is the richest. See `authorization.second_person_rule` in the worked example.

---

## What a good row looks like

Seven fields, all required, and none of them decorative:

```yaml
- target:  evaluation.reference_lab          # a target the seed declares. nothing else exists.
  value:   { turnaround_minutes: 360 }       # what is true here
  inverse: null                              # how to get back. null only if there was no prior value.
  evidence:
    - source: contracts/reference-lab-2024.pdf p.7
      says:   "contracted turnaround is 4 hours"
    - source: case tape, drawn -> resulted, 2025, n=402
      says:   "observed p75 was 6h04m; the contracted figure was met in 38% of cases"
  shadow_run: { cases: 402, would_have_matched: 402 }
  expiry:  2026-12-01                        # nothing is permanent by default
  author:  ""                                # a machine leaves this EMPTY. a human signs.
```

**On percentiles.** Use p75 or higher, and p90 where the number feeds a latest-safe-start calculation. A
threshold set at the median is breached half the time by construction.

**On the inverse.** It must genuinely restore the prior state. If you cannot determine the prior value, that
is a stop — not a field to fill with something reasonable.

**On the signature.** A machine's output is a **candidate**. A named human reads it and signs, and that
signature is what makes the mount legitimate. It is also, formally, the moment the system commits to an
effect it cannot take back.

---

## When the material does not answer the question

**Record a hold. Do not guess, and do not skip.**

Every one of the twenty declared targets must end up as a row or a hold — the `accountability` gate refuses
a patch that is silent on any of them, and `AGENTS.md` §7b gives the shape.

**The three situations that look identical from outside, and why that matters:**

| What happened | What a reader sees without a hold |
|---|---|
| you searched and the material is genuinely silent | *nothing* |
| you never got to that target | *nothing* |
| the site has no local variation there | *nothing* |

**A hold makes them three different things.** It names what you searched, so the next person does not repeat
it, and so a site that wants the gap closed knows exactly which document to go and find.

### The classes, and which one carries the most

- **`sources_contradict`** — **the most valuable output of a completion.** The binder says one thing and the
  behaviour shows another, and nobody has reconciled them. *This is a finding about the organisation, not a
  gap in your work.* Resist the pull to pick a side: if the tape has a clean majority you may encode it and
  cite both (see the worked example's `intake.after_hours_owner`); if it does not, hold it.
- **`no_evidence`** — you looked in the places the question names and it is not there. Say **where you
  looked**, not just that you looked.
- **`requires_tier_1_5_change`** — the answer would need a change at federal, CMS, OPTN or state level. **Not
  yours to answer**, and saying so is the correct output.
- **`phi_adjacent_declined`** — answering would mean enumerating something a completion should not be
  handling.
- **`ambiguous_needs_human`** — the material supports two readings and choosing needs someone who works
  those shifts.

### A hold is not a failure and it is not a STOP

**A hold is finished work.** You record it and continue. A STOP is different — it means you cannot proceed
at all without a human decision. **Nine holds and a finished draft is a good outcome**; nine stops is not.

**And a plausible row is worse than a hold.** A gap is visible. A confident wrong answer is not — which is
why the completion falsifier scores a fabrication *below* a blank.


## Sequence

1. **Draft from the material.** Work the questions in tier order — the tier-1 constraints bind schedules, so
   getting them wrong invalidates everything downstream.
2. **Run the gate.** `python gates/validate_patch.py <your>.patch.json`. It names each defect in words.
   Iterate until nothing is `FAILED`.
3. **Take the draft to people.** Twenty minutes, asking which rows are wrong. Expect several to be.
4. **Shadow-run every row** against your own historical cases before anyone signs. A row nobody replayed is a
   guess with formatting.
5. **A human signs.** Then, and only then, it mounts.

Read [`../examples/worked/REJECTED.md`](../examples/worked/REJECTED.md) before step 1. The refused drafts
teach more than the accepted one.

---

## ~~What to do when you cannot answer a question~~ — CORRECTED `2026-08-26`

This section used to say **"leave it out."** That is now wrong, and the correction is worth keeping visible
rather than quietly editing away, because **the sentence that followed it was right and is the reason the
instruction had to change.**

It said: *the questions you cannot answer are themselves a finding — they are the parts of your own operation
nobody currently has visibility into, and that list is worth having even if you never write a patch file at
all.*

**Exactly so. And "leave it out" throws that list away.** An omitted target produces no list at all: it looks
identical to a target nobody reached, and identical again to one where the site genuinely has no local
variation. The finding this paragraph correctly identified as valuable was being discarded by the instruction
sitting directly above it.

**So: record a hold instead.** Same honesty, same refusal to guess — and the list survives. See *When the
material does not answer the question* above, and `AGENTS.md` §7b for the shape. The `accountability` gate
enforces it.

**The rest stands unchanged, and harder than before:** a guessed row is a wrong number wearing the formatting
of a right one, and it propagates into every deadline computed from it. **A fabrication scores below a
blank** — that is not rhetoric, it is how the completion falsifier's rubric is written.
