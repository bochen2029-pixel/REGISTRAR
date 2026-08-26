#!/usr/bin/env python3
"""
REGISTRAR · tools · citation verification
─────────────────────────────────────────────────────────────────────────────
Turns provenance from a discipline into a gate.

THE PROBLEM THIS SOLVES

`PROVENANCE.md` §4 rules out "a model's uncited assertion — an AI harness
producing a confident regulatory value without a source is producing a
fabrication with good grammar." That rule is unenforceable by reading, because
a fabricated citation and a correct one look identical: both name a plausible
authority, a plausible section, and a plausible claim.

So do not read them. **Check them.**

    A citation is admissible only if its quoted passage byte-matches a
    sha256-pinned local copy of the source.

A model can invent a policy section number. It cannot invent a verbatim quote
that matches a hash-pinned file on this disk. Acceptance therefore becomes a
string comparison rather than an act of trust, and the entire class of
plausible-but-invented citation dies mechanically.

WHAT THIS DOES NOT DO

It verifies that the quote **exists in the source**. It does not verify that the
quote **establishes the claim** — that is a judgment, it belongs to a human or
to an adversarial reviewer, and this tool deliberately does not pretend to make
it. Passing here means "not fabricated." It does not mean "correct."

    python tools/cite.py --check                 verify every citation in the ledger
    python tools/cite.py --manifest              show the pinned corpus
    python tools/cite.py --add <src> <file>      pin a source

Zero dependencies. Corpus documents live in corpus/ and are NOT redistributed
from this repository — they belong to their publishers. Only the manifest,
which is hashes and URLs, is committed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "corpus")
MANIFEST = os.path.join(CORPUS, "MANIFEST.json")
CITATIONS = os.path.join(ROOT, "corpus", "citations.json")

OK, MISSING, MISMATCH, UNPINNED = "OK", "SOURCE-MISSING", "QUOTE-NOT-FOUND", "SOURCE-UNPINNED"
WARN = "CHECK-CURRENCY"

# Language meaning a passage may be real and no longer in force. Found the hard
# way: 42 CFR 486.318(a)-(c) describes an expired three-measure regime that is
# still in the codified text, and a search for "outcome measures" lands there
# first. The byte-match gate PASSES a citation to it — the passage exists, it is
# merely superseded. So the gate warns, because it genuinely cannot decide.
SUNSET = (
    r"effective until",
    r"expire[sd]?\s+(?:on|at)",
    r"no longer (?:in effect|applicable)",
    r"until\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d",
    r"superseded by",
)


# ── normalisation ───────────────────────────────────────────────────────────
def normalise(s: str) -> str:
    """
    Fold the differences that PDF extraction introduces and that nobody means:
    unicode form, curly quotes, dashes, soft hyphens, and runs of whitespace.

    Deliberately NOT case-folded and NOT punctuation-stripped. A quote that only
    matches after aggressive mangling is not a quote.
    """
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")                                  # soft hyphen
    s = re.sub(r"[‘’‛]", "'", s)
    s = re.sub(r"[“”‟]", '"', s)
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ── manifest ────────────────────────────────────────────────────────────────
def load_manifest() -> dict:
    if not os.path.exists(MANIFEST):
        return {"sources": {}}
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def save_manifest(m: dict) -> None:
    os.makedirs(CORPUS, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def add_source(source_id: str, path: str, url: str = "", accessed: str = "") -> None:
    m = load_manifest()
    m.setdefault("sources", {})[source_id] = {
        "file": os.path.relpath(os.path.abspath(path), CORPUS).replace("\\", "/"),
        "sha256": sha256(path),
        "bytes": os.path.getsize(path),
        "url": url,
        "accessed": accessed,
    }
    save_manifest(m)
    print(f"pinned {source_id}  sha256 {m['sources'][source_id]['sha256'][:16]}…  {m['sources'][source_id]['bytes']:,} B")


def source_text(source_id: str, m: dict) -> tuple[str | None, str]:
    """Return (normalised text, status). Verifies the file still matches its pin."""
    src = m.get("sources", {}).get(source_id)
    if not src:
        return None, UNPINNED
    path = os.path.join(CORPUS, src["file"])
    if not os.path.exists(path):
        return None, MISSING
    if sha256(path) != src["sha256"]:
        return None, "SOURCE-CHANGED"
    with open(path, encoding="utf-8", errors="replace") as fh:
        return normalise(fh.read()), OK


# ── the check ───────────────────────────────────────────────────────────────
def verify(citation: dict, cache: dict, m: dict) -> tuple[str, str]:
    """
    One citation. Returns (status, detail).

    A citation is a dict with at least: element, source, quote.
    """
    sid = citation.get("source")
    quote = citation.get("quote", "")

    if not sid or not quote.strip():
        return MISMATCH, "citation carries no source or no quote"

    if sid not in cache:
        cache[sid] = source_text(sid, m)
    text, status = cache[sid]
    if text is None:
        return status, f"source {sid!r} is not available to check against"

    needle = normalise(quote)
    if len(needle) < 24:
        return MISMATCH, f"quote is {len(needle)} chars — too short to be evidence of anything"

    if needle in text:
        # Is the quote sitting in a neighbourhood that sunsets itself?
        i = text.find(needle)
        window = text[max(0, i - 2500): i + len(needle) + 2500]
        for pat in SUNSET:
            m = re.search(pat, window, re.I)
            if not m:
                continue
            # A human may close the warning — by recording WHY, not by silencing it.
            conf = citation.get("currency_confirmed")
            if conf:
                return OK, f"verbatim; sunset nearby, confirmed in force — {conf}"
            return WARN, (f"verbatim in {sid}, but nearby text reads "
                          f"{m.group(0)!r} — CONFIRM IT IS STILL IN FORCE")
        return OK, f"verbatim in {sid} ({len(needle)} chars)"

    # Say something useful about how it failed, rather than just "no".
    head = needle[:40]
    if head in text:
        return MISMATCH, f"first 40 chars occur in {sid}, but the full quote does not — truncated or altered"
    return MISMATCH, f"not present in {sid} — the passage does not exist as quoted"


def check_all(path: str = CITATIONS) -> int:
    m = load_manifest()
    if not os.path.exists(path):
        print("no citations.json yet — nothing to check.")
        print("This is the honest state while the locators read TODO-VERIFY.")
        return 0

    with open(path, encoding="utf-8") as fh:
        cites = json.load(fh).get("citations", [])

    cache: dict = {}
    bad = warned = 0
    for c in cites:
        status, detail = verify(c, cache, m)
        mark = {OK: "ok    ", WARN: "WARN  "}.get(status, "REJECT")
        print(f"  {mark}  {c.get('element', '?'):<44} {detail}")
        if status not in (OK, WARN):
            bad += 1
        if status == WARN:
            warned += 1

    print(f"\n{len(cites) - bad}/{len(cites)} citations verify byte-exact against pinned sources")
    if warned:
        print(f"{warned} carry sunset language nearby. A passage can be REAL AND EXPIRED,")
        print("and this gate cannot tell the difference — so it says so rather than guessing.")
    if bad:
        print(f"{bad} REJECTED. A citation that does not appear in its source is a fabrication,")
        print("regardless of how plausible it reads. It does not enter the ledger.")
    else:
        print("\nNote what this does and does not mean: every quote EXISTS in its source.")
        print("Whether each quote ESTABLISHES its element is a separate judgment,")
        print("and it belongs to a human. This gate only kills fabrication.")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if "--manifest" in argv:
        m = load_manifest()
        srcs = m.get("sources", {})
        if not srcs:
            print("corpus is empty — nothing pinned yet")
            return 0
        for sid, s in sorted(srcs.items()):
            here = os.path.exists(os.path.join(CORPUS, s["file"]))
            print(f"  {sid:<28} {s['sha256'][:16]}…  {s['bytes']:>12,} B  "
                  f"{'present' if here else 'MISSING'}  {s.get('accessed', '')}")
        return 0

    if "--add" in argv:
        i = argv.index("--add")
        sid, path = argv[i + 1], argv[i + 2]
        url = argv[argv.index("--url") + 1] if "--url" in argv else ""
        acc = argv[argv.index("--accessed") + 1] if "--accessed" in argv else ""
        add_source(sid, path, url, acc)
        return 0

    if "--check" in argv or len(argv) == 1:
        return check_all()

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
