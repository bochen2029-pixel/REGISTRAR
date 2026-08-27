#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Bo Chen
"""
REGISTRAR · forge · chunk
─────────────────────────────────────────────────────────────────────────────
Split a document too large to read in one pass into context-sized pieces at
clean semantic boundaries, with enough orientation that a reader never loses
its place.

**Why this exists.** `elicit/method.md` requires PHI-bearing site material to be
read only by a *local* open-weight model — a small context facing a 400-page SOP
binder. And the seed's own pinned OPTN corpus is 784 KB: the single file a
harness cannot read in one pass while filling a locator. This is the binding
constraint of the entire completion.

THE RULE THAT REFUSES A MOUNT

    `--out` is MANDATORY. There is no default, and no path is ever derived from
    the source.

    A chunker that writes a directory beside its source silently creates a
    **second, uncontrolled copy of PHI-bearing material** in a location nobody
    chose and nobody audits. That is the single most likely way a well-meaning
    tool leaks here, and it leaks by being helpful. The surveyed prior art
    defaulted to exactly that behaviour, which is a large part of why this is a
    rewrite rather than a fold.

    For the same reason the manifest records a LABEL, never a path. Knowing a
    document came from `\\\\phi-share\\donors\\2026\\case-1147\\workup.pdf` is itself
    a disclosure.

ON THE TOKEN ESTIMATE, AND WHICH DIRECTION IT ERRS

    A byte count is a meaningless proxy for a token budget once content is
    mixed: a base64 image is byte-huge and token-cheap, dense coded text is the
    reverse. So the budget is in tokens and the estimate is by character class.

    **It is biased to OVER-estimate, deliberately.** An overestimate wastes a
    little context; an underestimate overflows it and truncates a clinical
    document mid-sentence. Only one of those is recoverable.

READING THE OUTPUT

    Chunks in order reconstruct the source. Each carries a recap of the tail of
    its predecessor for continuity — **fenced by markers, so it is removable**:
    `strip_recaps()` is exported for exactly that, and the battery uses it to
    assert reconstruction rather than reimplementing the rule.

    python chunk.py SOURCE --out DIR [--budget N] [--overlap N] [--label NAME]

Stdlib only. No network. Every path is an argument.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RECAP_OPEN = "<!-- recap-start -->"
RECAP_CLOSE = "<!-- recap-end -->"

DEFAULT_BUDGET = 8000
DEFAULT_OVERLAP = 400


# ─────────────────────────────────────────────────────────────────────────────
# TOKENS — estimated by character class, biased high
# ─────────────────────────────────────────────────────────────────────────────
_WORD = re.compile(r"[A-Za-z]+")
_NUM = re.compile(r"\d+")
_CJK = re.compile(r"[　-鿿가-힯]")
_PUNCT = re.compile(r"[^\w\s]")


def estimate_tokens(text: str) -> int:
    """
    Approximate tokens, **erring high**.

    An overestimate wastes context. An underestimate overflows it and truncates
    a document mid-sentence. Only one of those is recoverable, so every ratio
    here rounds up.
    """
    if not text:
        return 0
    # ~4 chars per token for prose, but long words split into several pieces
    tok = sum((len(w) + 3) // 4 for w in _WORD.findall(text))
    # digits tokenise densely — roughly one token per two or three characters
    tok += sum((len(n) + 1) // 2 for n in _NUM.findall(text))
    # CJK is close to one token per character
    tok += len(_CJK.findall(text))
    # punctuation and symbols are usually their own token
    tok += len(_PUNCT.findall(text))
    # newlines carry structure and are not free
    tok += text.count("\n")
    return max(1, tok)


# ─────────────────────────────────────────────────────────────────────────────
# BLOCKS — the unit of packing
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Block:
    text: str
    section: tuple[str, ...] = ()   # the heading breadcrumb, outermost first
    kind: str = "para"              # para | heading | page | record
    tokens: int = 0

    def __post_init__(self) -> None:
        if not self.tokens:
            self.tokens = estimate_tokens(self.text)


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_PAGE = re.compile(r"^\s*\[\[PAGE\s+(\d+)\]\]\s*$", re.I)


def split_blocks(text: str) -> list[Block]:
    """
    Paragraphs, with a heading breadcrumb carried down.

    Headings push and pop a stack, so every block knows its full path — that
    breadcrumb is what stops a reader losing its place mid-document, and it is
    the single most useful piece of orientation metadata.

    `[[PAGE n]]` markers are treated as headings at a reserved depth, so a
    paginated extraction gets page numbers through the same machinery rather
    than a parallel one.
    """
    blocks: list[Block] = []
    stack: list[tuple[int, str]] = []
    buf: list[str] = []

    def flush(kind: str = "para") -> None:
        if not buf:
            return
        body = "\n".join(buf).strip()
        buf.clear()
        if body:
            blocks.append(Block(body, tuple(t for _, t in stack), kind))

    for line in text.splitlines():
        pg = _PAGE.match(line)
        if pg:
            flush()
            # page markers sit at depth 7 — below any real heading, so they
            # refine a section rather than replacing it
            stack[:] = [f for f in stack if f[0] < 7]
            stack.append((7, f"page {pg.group(1)}"))
            blocks.append(Block(line.strip(), tuple(t for _, t in stack), "page"))
            continue

        h = _HEADING.match(line)
        if h:
            flush()
            level = len(h.group(1))
            stack[:] = [f for f in stack if f[0] < level]
            stack.append((level, h.group(2)))
            blocks.append(Block(line.rstrip(), tuple(t for _, t in stack), "heading"))
            continue

        if not line.strip():
            flush()
        else:
            buf.append(line)

    flush()
    return blocks


# ─────────────────────────────────────────────────────────────────────────────
# OVERSIZED — the cascade, and it must terminate
# ─────────────────────────────────────────────────────────────────────────────
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def split_oversized(block: Block, budget: int) -> list[Block]:
    """
    A block larger than the budget, broken at the highest boundary that helps.

    paragraph → sentence → line → word → characters. The last is the only place
    a word is ever cut, and only when a single atom has no break point at all.
    **Every level strictly advances**, so this terminates on any input.
    """
    if block.tokens <= budget:
        return [block]

    for splitter in (
        lambda s: s.split("\n\n"),
        lambda s: _SENTENCE.split(s),
        lambda s: s.split("\n"),
        lambda s: s.split(" "),
    ):
        parts = [p for p in splitter(block.text) if p.strip()]
        if len(parts) > 1:
            out: list[Block] = []
            for p in parts:
                out.extend(split_oversized(Block(p, block.section, block.kind), budget))
            return _rejoin(out, budget, block)

    # one atom, no break point: cut by characters, proportionally
    text = block.text
    per = max(1, int(len(text) * budget / max(1, block.tokens)))
    return [Block(text[i:i + per], block.section, block.kind)
            for i in range(0, len(text), per)]


def _rejoin(parts: list[Block], budget: int, parent: Block) -> list[Block]:
    """Greedily recombine fragments so the split is no finer than it must be."""
    out: list[Block] = []
    cur: list[str] = []
    tok = 0
    for p in parts:
        if cur and tok + p.tokens > budget:
            out.append(Block("\n".join(cur), parent.section, parent.kind))
            cur, tok = [], 0
        cur.append(p.text)
        tok += p.tokens
    if cur:
        out.append(Block("\n".join(cur), parent.section, parent.kind))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# PACKING — with headroom reserved BEFORE anything is placed
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Chunk:
    blocks: list[Block] = field(default_factory=list)
    recap: str = ""

    @property
    def section(self) -> tuple[str, ...]:
        for b in self.blocks:
            if b.section:
                return b.section
        return ()

    @property
    def body(self) -> str:
        return "\n\n".join(b.text for b in self.blocks)


def _quoted_tokens(text: str) -> int:
    """
    What a recap costs AS RENDERED, not as raw text.

    Every line gains a `> ` prefix when quoted, and across a hundred-line recap
    that is a couple of hundred tokens the raw estimate cannot see. Budgeting
    the raw form is precisely why two chunks came out over budget on the first
    real run against the 784 KB corpus.
    """
    return estimate_tokens("\n".join("> " + ln for ln in text.splitlines()))


def _tail(blocks: list[Block], want: int) -> str:
    """
    The last `want` tokens' worth of prior content, measured **as it will be
    rendered** — quoted — rather than raw.
    """
    out: list[str] = []
    for b in reversed(blocks):
        cand = [b.text] + out
        if out and _quoted_tokens("\n\n".join(cand)) > want:
            break
        out = cand
    if not out and blocks:
        # one block larger than the whole overlap budget: take a proportional
        # tail, then trim until the QUOTED form fits
        text = blocks[-1].text
        keep = max(1, int(len(text) * want / max(1, blocks[-1].tokens)))
        cut = "…" + text[-keep:]
        while keep > 1 and _quoted_tokens(cut) > want:
            keep = keep * 3 // 4
            cut = "…" + text[-keep:]
        out = [cut]
    return "\n\n".join(out)


def pack(blocks: list[Block], budget: int, overlap: int) -> list[Chunk]:
    """
    Greedy fill, with the recap and the frame subtracted **first**.

    This is the non-obvious part. A rendered chunk is header + recap + body +
    footer, so sizing the *body* to the budget overflows the budget every time.
    The reserve comes off the top.
    """
    # The frame is four comment lines, the recap fence and a footer. Allowed for
    # explicitly rather than folded into a percentage — an underestimate here
    # overflows the context, which is the one direction that is not recoverable.
    FRAME = 120
    reserve = overlap + FRAME + max(200, budget // 20)
    content_budget = max(1, budget - reserve)

    sized: list[Block] = []
    for b in blocks:
        sized.extend(split_oversized(b, content_budget))

    chunks: list[Chunk] = []
    cur = Chunk()
    tok = 0
    for b in sized:
        if cur.blocks and tok + b.tokens > content_budget:
            chunks.append(cur)
            cur = Chunk(recap=_tail(cur.blocks, overlap) if overlap else "")
            tok = 0
        cur.blocks.append(b)
        tok += b.tokens
    if cur.blocks:
        chunks.append(cur)
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# RENDER — orientation is the product
# ─────────────────────────────────────────────────────────────────────────────
def render(chunk: Chunk, idx: int, total: int, label: str) -> str:
    crumb = " > ".join(chunk.section) if chunk.section else "(no section)"
    head = [
        f"<!-- ============ CHUNK {idx}/{total} ============ -->",
        f"<!-- source: {label} -->",
        f"<!-- section: {crumb} -->",
    ]
    if chunk.recap:
        head.append(f"<!-- recap of chunk {idx - 1}, for continuity — not new content -->")
        head.append(RECAP_OPEN)
        head.extend("> " + ln for ln in chunk.recap.splitlines())
        head.append(RECAP_CLOSE)
    nxt = f"chunk-{idx + 1:03d}.md" if idx < total else "(none — this is the last)"
    foot = f"<!-- end chunk {idx}/{total} | next: {nxt} -->"
    return "\n".join(head) + "\n\n" + chunk.body + "\n\n" + foot + "\n"


def strip_recaps(text: str) -> str:
    """
    Remove recap regions and the comment frame.

    Exported because a consumer that wants the original bytes back must not
    have to reimplement the rule — and because the battery asserts
    reconstruction with it rather than with a private copy.
    """
    text = re.sub(re.escape(RECAP_OPEN) + r".*?" + re.escape(RECAP_CLOSE),
                  "", text, flags=re.S)
    text = re.sub(r"^<!--.*?-->\s*$", "", text, flags=re.M)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# EXTRACT — text formats only; anything else is the caller's problem
# ─────────────────────────────────────────────────────────────────────────────
class _Strip(__import__("html.parser", fromlist=["HTMLParser"]).HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.out: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def extract(path: str) -> tuple[str, str]:
    ext = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()

    if ext in (".html", ".htm"):
        p = _Strip()
        p.feed(raw)
        return re.sub(r"\n{3,}", "\n\n", "".join(p.out)), "html"
    if ext == ".json":
        try:
            return json.dumps(json.loads(raw), indent=2, ensure_ascii=False), "json"
        except ValueError:
            return raw, "json"
    if ext == ".jsonl":
        # a record is an atom — NEVER split a line, because half a JSON object
        # is not a smaller JSON object, it is corrupt
        return "\n\n".join(ln for ln in raw.splitlines() if ln.strip()), "jsonl"
    return raw, "text"


# ─────────────────────────────────────────────────────────────────────────────
def chunk_document(source_path: str, out_dir: str, budget: int = DEFAULT_BUDGET,
                   overlap: int = DEFAULT_OVERLAP, label: str | None = None) -> dict:
    """
    `out_dir` is required and is used verbatim. Nothing is derived from
    `source_path`, and `source_path` never appears in the output.
    """
    if not out_dir:
        raise ValueError("out_dir is required — this tool never chooses where to write")

    text, fmt = extract(source_path)
    # the label is what the manifest records. A path is a disclosure.
    label = label or os.path.basename(source_path)

    blocks = split_blocks(text)
    chunks = pack(blocks, budget, overlap)
    os.makedirs(out_dir, exist_ok=True)

    entries = []
    over = []
    for i, ch in enumerate(chunks, 1):
        body = render(ch, i, len(chunks), label)
        name = f"chunk-{i:03d}.md"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(body)
        actual = estimate_tokens(body)
        if actual > budget:
            over.append(name)
        entries.append({"idx": i, "file": name, "tokens": actual,
                        "section": " > ".join(ch.section)})

    manifest = {
        "label": label,                      # NOT a path — see the module docstring
        "format": fmt,
        "source_tokens": estimate_tokens(text),
        "chunks": len(chunks),
        "budget": budget,
        "overlap": overlap,
        "over_budget": over,
        "entries": entries,
        "note": ("Read chunk-001 … chunk-NNN in order. Each after the first opens with a "
                 "recap of its predecessor, fenced by recap-start/recap-end; strip those "
                 "to reconstruct the source."),
    }
    with open(os.path.join(out_dir, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    with open(os.path.join(out_dir, "INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# {label} — {len(chunks)} chunks\n\n")
        fh.write("Read in order. Each chunk after the first opens with a recap of the\n")
        fh.write("previous one, fenced by `recap-start`/`recap-end` — that text is a\n")
        fh.write("repeat, not new content.\n\n| # | file | tokens | section |\n|---|---|---|---|\n")
        for e in entries:
            fh.write(f"| {e['idx']} | {e['file']} | {e['tokens']} | {e['section'] or '—'} |\n")

    return manifest


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Split a document into context-sized pieces at semantic boundaries.")
    ap.add_argument("source", help="the document to split")
    ap.add_argument("--out", required=True,
                    help="output directory. REQUIRED — this tool never chooses where to "
                         "write, because a path derived from the source is a second "
                         "uncontrolled copy in a place nobody audits.")
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="tokens per chunk")
    ap.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP, help="recap tokens")
    ap.add_argument("--label", default=None,
                    help="what the manifest records instead of a path (default: basename)")
    a = ap.parse_args(argv)

    m = chunk_document(a.source, a.out, a.budget, a.overlap, a.label)
    print(f"{m['chunks']} chunks · {m['source_tokens']} source tokens · budget {m['budget']}")
    print(f"wrote {a.out}")
    if m["over_budget"]:
        print(f"WARNING: {len(m['over_budget'])} chunk(s) over budget: "
              f"{', '.join(m['over_budget'][:5])}")
        return 1
    return 0


if __name__ == "__main__":
    # The forge fence, wired — QC F5 found require_forge() with zero callers,
    # and a fence nobody invokes is law 9 verbatim. A deployed record must
    # not carry completion machinery that RUNS; the guard names the escape.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "core"))
    from profile import require_forge
    require_forge("forge/plugins/chunk/src/chunk.py")
    raise SystemExit(main(sys.argv[1:]))
