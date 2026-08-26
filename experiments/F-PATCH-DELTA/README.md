# F-PATCH-DELTA

**The falsifier.** Can a competent outside harness author a candidate fit that passes the gates and
materially matches what a site actually does — without being told the answers?

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — the question, the arms, the rubric, the thresholds, and what
  invalidates a run. **Fixed before anything ran.**
- [`RESULTS.md`](RESULTS.md) — what has been run, and what it showed.
- [`site/`](site/) — **the corpus.** Fairbank Donor Network, fictional, zero PHI.

---

## IF YOU ARE HERE TO RUN ARM ② — STOP AND READ THIS

**The answer key is not in this directory, deliberately.**

`DELTA.json`, the extractor that computes it, and the builder that seeded the corpus all live in
`internal/f-patch-delta/`, which is **gitignored**. A fresh clone does not receive them.

That was not the original arrangement. **They were committed here, beside the corpus, for one commit** —
which made the pre-registration's own rule unenforceable:

> §6 · *the harness is given the delta, in any form*

A protocol that says *"do not look at the answer key"* while the answer key sits in the same directory is
**an instruction where a mechanism was needed** — and a diligent harness would have read it precisely
because it is adjacent and looks relevant.

### What you must not read

| | Why |
|---|---|
| `internal/f-patch-delta/DELTA.json` | the answer key |
| `internal/f-patch-delta/extract_delta.py` | names every trap in its comments |
| `internal/f-patch-delta/build_site.py` | the seeded distributions |
| [`RESULTS.md`](RESULTS.md) | states the contradictions and the unanswerable target outright |
| [`PREREGISTRATION.md`](PREREGISTRATION.md) **§3** | describes the trap design |

`PREREGISTRATION.md` §1, §2, §4–§8 are safe and worth reading — the question, the arms, the rubric and the
thresholds are all public on purpose. **That is what pre-registration is for.**

### Honest limit of this arrangement

**The spoilers are in git history.** They were pushed before this was noticed, so `git log` still reaches
them. Moving them stops *accidental* contamination — a file you trip over — and does not stop deliberate
digging.

**That asymmetry is the whole mitigation, and it is stated rather than papered over.** A runner who goes
looking in history has chosen to invalidate the run, and §6 already covers that.

---

## The protocol

Give a session that **did not build this corpus**:

- the repository — `AGENTS.md`, `elicit/`, `schema/`, `examples/worked/`, the gates
- [`site/`](site/)
- **and nothing from the list above**

Ask it to author `fairbank.patch.yml` against the seed's declared variation points. Then:

```bash
python gates/validate_patch.py <candidate>
python experiments/F-PATCH-DELTA/score.py <candidate>
```

Scoring regenerates the answer key from the vault. If it is missing:

```bash
python internal/f-patch-delta/extract_delta.py
```

**Report the gate result and the score separately.** A patch that scores well and fails the gates is a
different finding from one that passes the gates and scores badly, and collapsing them hides which.

---

## Read the floor before you read any arm-② number

**Arm ① — a patch generated from generic OPO defaults, having read nothing about the site — scored
`S = 0.47` and cleared the SHAPED threshold.**

So an arm ② result near 0.47 means **the schema did the work and the harness did not.** §5 is explicit that
this is a FAILS regardless of the absolute score.

**And the gates refused arm ① on their own, without the answer key** — *"asserts generality, not this site"*,
and 20 of 20 shadow runs with no denominator.
