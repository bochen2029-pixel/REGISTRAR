# MAINLINE · F-PATCH-DELTA, the falsifier

**Created `2026-08-26` · branch point `9a1a5f7` · read [`../FORKS.md`](../FORKS.md) first, it is binding**

---

## In one breath

**Pre-register the experiment that can kill the project**, then run it. Give a harness only *public* material
for a second OPO, have it author a candidate patch under the gates, grade against a known delta — **with the
rubric written before anything runs.**

---

## Why this is mainline

Everything else in this repository is downstream of one unproven claim: **that a competent outside
intelligence can add correct work to this artifact, per unit of effort, without breaking it.** That is
completability, and it is `[BET]`.

The seed is worth having regardless — `SPEC.md` §1 says so, and fifty-five organisations re-encoding
identical law is deadweight loss an open artifact removes on its own. **But the completion claim is the
thesis, and it has never been tested.**

It has been "next" for a long time. It is cheap: **one weekend, no PHI, nobody's permission.**

---

## The three arms, and why the order is forced

| Arm | What it gets | What it establishes |
|---|---|---|
| **① template-prior** | the seed, **no site material at all** — fill the schema with generic OPO defaults | **the floor.** Without it, a passing arm ② might only mean *the schema is fillable by anyone* |
| **② prompted harness** | the seed **+ public material** for a second OPO | the claim under test |
| **③ resident** | continuous access, later | needs the resident — **and ② is its null** |

**Run ① and ② now. ③ is gated on this returning.**

**And the ordering is not a preference.** If the resident is built first and then measured, its contribution
cannot be separated from the schema's — *was the fit good because something was home to notice, or because
the schema was easy to fill?* **Skip arm ② and that question is unanswerable forever.**

---

## Run it with a GENERIC harness. That is a feature.

`AGENTS.md` deliberately names no harness. **If the seed is only completable by our stack, we built a
product rather than a seed** — and the completability thesis is false in the way that matters most.

So a run with Claude Code, or any capable harness, is a **stronger** test than one with a REGISTRAR-composed
harness, not a weaker one.

**Corollary:** this experiment needs no chassis, no plugins, no resident. It is unblocked today.

---

## THE FIRST TASK IS TO FIND OUT WHETHER THE EXPERIMENT IS WELL-POSED

The design says *"public material for a second OPO."* **Before writing a rubric, establish how much of that
exists.**

An OPO's genuinely public surface is thin: a website, an annual report if they publish one, CMS
certification data, SRTR/OPTN aggregate figures, maybe a news mention. **Almost none of it describes
operational shape** — call rotation, escalation practice, OR windows, lab turnaround. Those are the L2/L3
facts a patch is made of, and they may be **structurally unavailable in public.**

**If that is the case, the test as specified is unfair, and a negative result would be uninformative** —
it would measure the material, not the harness.

**Three honest responses, and picking one is part of the pre-registration:**

1. **Narrow the claim.** Grade only on what public material *could* support, and say plainly that L3 is
   untestable this way.
2. **Use a synthetic site with a known delta.** Fully fair, fully gradeable — but it tests the *schema and
   the gates*, not the world. **Say which.**
3. **Grade against STA**, where ground truth exists — **but that is clean-room contaminated** and
   `PROVENANCE.md` §4 makes recollection of a former employer's design inadmissible. **Probably refuse
   this**, and record why.

**Finding this out costs an afternoon. Finding it out mid-run costs the weekend.**

---

## What the pre-registration must fix, before anything runs

- **The question**, in one sentence, falsifiable.
- **The arms**, and exactly what material each receives.
- **The gate battery, pinned by commit SHA.** Fork C is strengthening the gates concurrently; a rubric that
  shifts underneath the run is not pre-registered.
- **The rubric** — how a candidate patch is scored against the known delta, written in advance.
- **The thresholds** for each of the three outcomes, in advance.
- **What invalidates the run** — conditions under which the result is discarded rather than reported.

---

## The three outcomes, and all three are publishable

- **Covers the delta** → the first receipt. Everything downstream is justified.
- **Shallow but correctly shaped** → **the expected result, and the most useful.** It tells you *how much
  observation the fit actually requires*, which is the number nobody has.
- **Confidently wrong** → **the funeral prints.** The honest product becomes an excellent open-source spine
  plus a human implementation guide — **still more than exists today.**

**Pre-commit to publishing whichever lands.** A falsifier you only publish when it passes is not a falsifier.

---

## Definition of done

**For the pre-registration** (this session): a document in `experiments/F-PATCH-DELTA/` that a hostile
reviewer could use to run the experiment without asking a question, with the gate SHA pinned and the
material question answered.

**For the run** (after): the candidate patches, the grades, the verdict, and the write-up — including
everything the harness got wrong.

---

## What not to do

- **Do not run before pre-registering.** The whole value is that the rubric predates the result.
- **Do not adjust the rubric after seeing output.** If it was wrong, say so, discard the run, and re-register.
- **Do not use PHI, or any material from a real OPO that is not public.**
- **Do not use recollection of STA's design as ground truth** — `PROVENANCE.md` §4.
- **Do not touch `deepseek-harness-master/`** or any other fork's write surface. See `FORKS.md`.
