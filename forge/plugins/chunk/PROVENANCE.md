# chunk · provenance

**`2026-08-26` · clean-room · MIT**

## Where this came from

**Nothing was copied.** No bytes from any surveyed tool entered this directory.

A read-only scout surveyed `C:\chunker` (642 lines, single file, stdlib at import) and reported its *design*
in prose. This implementation was written from that description. The author of this file never read the
original source — which is the strongest form of *take the catalogue, not the file* available, and the
distinction is worth stating precisely rather than asserting a general "adapted from."

## Why it is a rewrite and not a fold

**Two independent reasons, and the licence is the weaker one.**

**1 · It violated the refusing rule, by default.** The surveyed tool wrote
`<source_dir>/<basename>.chunks/` whenever `--out` was omitted — and `--out` defaulted to `None`, so that was
the *default path*, not an edge case. That is **a second, uncontrolled copy of PHI-bearing material in a
location nobody chose and nobody audits**, which `forge/plugins.yml` refuses a mount for. Its manifest also
recorded `os.path.abspath(source)`, leaking the source location into the output.

**2 · No licence.** No `LICENSE`, no SPDX header, no copyright line anywhere in the tree. Unvendorable into
an MIT repository regardless of merit.

**3 · No tests**, while its README claimed *"verified: zero data loss."* An unsubstantiated verification
claim is what this repository refuses everywhere else, and a chunker's entire contract is a claim about loss.

## What the design contributed

Genuinely good ideas, and they are the reason this took an afternoon rather than a week:

- **A boundary hierarchy, highest-that-fits** — heading → page marker → paragraph → sentence → line → word,
  with page markers folded into the *same* machinery as headings rather than a parallel path.
- **Reserve headroom before packing.** The non-obvious one. A rendered chunk is frame + recap + body, so
  sizing the *body* to the budget overflows the budget every time.
- **Recap overlap at block granularity**, with a degenerate case for a block larger than the whole overlap.
- **The orientation triple** — a section breadcrumb, a `next:` pointer, and an INDEX beside a manifest.

## What was changed, and why

| Change | Reason |
|---|---|
| **`--out` is mandatory**; no default, nothing derived from the source | the refusing rule. This is the whole reason for the rewrite. |
| **The manifest records a `label`, never a path** | knowing a document came from a PHI share is itself a disclosure |
| **The recap is budgeted as *rendered*, not raw** | see below — this was found by running it |
| An explicit `FRAME` allowance rather than a percentage | an underestimate overflows the context; that direction is not recoverable |
| `strip_recaps()` is **exported** | a consumer wanting the original bytes must not reimplement the rule, and the battery asserts reconstruction with it |
| The token estimate is **biased high**, by character class | an overestimate wastes context; an underestimate truncates a clinical document mid-sentence |
| **42 assertions**, including the reconstruction property | the original had none |
| PDF and `.docx` dropped | the surveyed `.docx` extractor silently dropped all tables, which matters for SOP binders. Better absent than quietly lossy. |

## What running it found

**The first run against the real 784 KB OPTN corpus put two chunks over budget** — and the tool reported it
and exited non-zero rather than shipping quietly, which is the behaviour that made the cause findable.

The cause: **a recap is rendered *quoted*, and every line gains a `> ` prefix.** Across a hundred-line recap
that is a couple of hundred tokens the raw estimate cannot see. `_tail()` now measures the quoted form.

That is also the lesson `cutter` teaches by counter-example — **a byte count is a meaningless proxy for a
token target on mixed content** — arriving one level down: *a raw token count is a meaningless proxy for a
rendered one.*

## What it does not do

- **No PDF, no `.docx`.** Text, markdown, JSON, JSONL and HTML only. A caller with a PDF extracts it first,
  with a tool it chose, and the extraction is then the input — which keeps the extraction step visible and
  auditable rather than buried.
- **No network.** Self-checked in the battery.
- **No absolute paths.** Self-checked in the battery.
- **It does not decide where output goes.** That is the caller's, always.
