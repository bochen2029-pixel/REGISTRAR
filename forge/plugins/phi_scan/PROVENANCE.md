# phi_scan · provenance

**`2026-08-26` · clean-room · MIT**

## Where this came from

**No code was copied.** A read-only scout surveyed `C:\KEEL` and reported both its detection logic and its
framing. The detection logic turned out to be **five regexes and a Luhn check** — email, SSN, `sk-` keys,
`AKIA` keys, payment cards. Against this domain's PHI list it finds **almost nothing**: no medical record
number, no date bound to a case, no donor identifier, no institution-plus-event, no combination reasoning.
There was nothing worth taking, and the licence — declared in `Cargo.toml`, with **no LICENSE file anywhere
in its history** — settled it regardless.

**The framing was the find, and it is better than the usual formulation because it is structural rather than
asserted.**

## What the vocabulary contributed

| Term | What it buys, and where it lives here |
|---|---|
| **rung** | an ordinal naming *epistemic type*, not strength. `Span.rung`. |
| **the oracle** | *a non-model assertion that PHI is present* — rungs 1 and 2 together |
| **"a verification pass, not an oracle"** | the exact phrase for anything probabilistic. The rung-3 socket carries it. |
| **additive-only — "the union only grows"** | **`merge()`, and a test asserts it contains no removal.** This is what makes the floor a property of the code rather than a promise. |
| **"never sole"** | rung 3 may add; it may never be the whole answer |
| **gate vs mask** | this is a *mask* — it finds spans. Refusing a frontier route is a *gate*. Merging them is how a redaction becomes an authorisation. |
| **labels, never values** | `Span.label()`. A test asserts the PHI itself never reaches the output. |
| **agent-frozen** | rung 1 is operator-authored. The tool supplies mechanism, never policy. |

## The defect this exists to avoid

**KEEL conflates "clean" with "not detected."** Empty findings is its only representation of nothing-found,
and when its rung-3 classifier fails to load it **silently returns zero spans** — so *a degraded scanner and
a genuinely clean text produce byte-identical output*, with a line on stderr as the only difference. Its own
test names the empty case `clean_text_is_unchanged`.

That is the same shape as a stalled resident being indistinguishable from a quiet one, and this repository
has a three-state discipline precisely because collapsing the middle state is how a system reports success
past a step that never ran.

**So there is no `CLEAN` verdict here, and there cannot be:**

| verdict | means |
|---|---|
| `FINDINGS` | PHI-shaped material was found. Act on it. |
| `NONE_DETECTED` | the rungs that **ran** found nothing. **Not a claim that the text is clean.** |
| `DEGRADED` | a rung did not run. **The scan is incomplete and its silence carries no information.** |

Every result records `rungs_run` and `rungs_degraded`. A supplied rung that raises produces `DEGRADED` — and
`DEGRADED` exits **2**, worse than `FINDINGS`'s **1**, because findings are actionable and an incomplete scan
is not.

**And a rung that was never supplied is not degradation** — it was never claimed, and reporting it would cry
wolf.

## What was added that KEEL does not have

**The combination rule**, which is the domain rule that matters most here. *A single unusual case is
re-identifiable from timing alone.* A date is usually nothing. A date bound to a time bound to an institution
identifies a person to anyone who was in the building, and **no individual pattern scores that high because
individually none of them should.**

`combinations()` raises the finding when three or more distinct quasi-identifier classes fall within a
window. A scanner built only on *find the names* misses the disclosure that actually happens in an
operational document.

Also added: MRN, donor/UNOS identifiers, accession numbers, several date notations, times, the HIPAA
age-over-89 rule, and an NPI validator that checks the Luhn digit over the `80840` prefix — so a random
ten-digit number is not reported as a provider identifier.

## What it does not do

- **It is not a guarantee, and it must never be described as one** — in code, in docs, or in a commit message.
  `forge/conformance.py` refuses a mount for guarantee language, and this file's own battery asserts the floor
  claim is present.
- **It does not redact.** It reports spans with offsets; what a caller does with them is a separate decision
  with separate consequences.
- **It does not decide egress.** That is a gate, and it lives elsewhere.
- **No rung 3 ships.** The socket is documented rather than stubbed, because a stub that returns nothing is
  indistinguishable from a rung that failed — which is the defect above, reintroduced.
