# corpus/

**Pinned copies of the public sources every L0 and L1 element must trace to.**

## What is committed, and what is not

**Committed:** `MANIFEST.json` — source ids, URLs, sha256 digests, byte counts, accessed dates.
And `citations.json` — the claims, each with the verbatim passage it rests on.

**Not committed:** the documents themselves. OPTN policy, the CFR text and CMS material belong to their
publishers, and this repository does not redistribute them. The manifest is enough to fetch your own copies
and confirm they are byte-identical to the ones every citation was checked against.

## Why the hash is the point

A citation is a claim about **a document at a date**. Regulatory text moves; a section number that was right
in August is not necessarily right in March. Pinning the sha256 makes every citation in
[`../PROVENANCE.md`](../PROVENANCE.md) reproducible rather than merely plausible — you can prove you are
reading the same bytes the claim was made against, or discover that you are not.

## The gate

```bash
python tools/cite.py --manifest     # what is pinned
python tools/cite.py --check        # do the citations verify, byte-exact?
```

A citation is admissible only if its quoted passage **byte-matches** the pinned source. A model can invent a
policy section number; it cannot invent a verbatim quote that matches a hash-pinned file. **Acceptance is a
string comparison, not an act of trust.**

**What this gate does not do:** it verifies the quote *exists in the source*. It does not verify the quote
*establishes the claim*. That is a judgment and it belongs to a human. Passing here means "not fabricated" —
it does not mean "correct."

## Adding a source

```bash
python tools/cite.py --add optn-policy corpus/optn-policies.txt \
  --url "https://optn.transplant.hrsa.gov/..." --accessed 2026-08-25
```

Pin the **extracted text** you actually search, not only the PDF — the citation is checked against the bytes
the quote was taken from. If extraction is redone with a different tool, the hash changes and every citation
resting on it is re-checked. That is correct behaviour, not an inconvenience.
