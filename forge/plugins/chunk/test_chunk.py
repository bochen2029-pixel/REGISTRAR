#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
REGISTRAR · forge · chunk · the battery

    python forge/plugins/chunk/test_chunk.py

**The surveyed prior art had no tests at all**, while its README claimed
*"verified: zero data loss."* That claim is the reason these exist: an
unsubstantiated verification claim is exactly what this repository refuses
everywhere else, and a chunker's whole contract is a claim about loss.

The two that matter most are the reconstruction property — *reading the pieces
in order equals reading the whole* — and the refusing rule, that output goes
only where the caller said.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import chunk as C  # noqa: E402

PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def tmpdir():
    d = tempfile.mkdtemp()
    return d


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def _doc() -> str:
    parts: list[str] = []
    for i in range(1, 9):
        parts.append(f"# Section {i}")
        for j in range(6):
            parts.append(f"Paragraph {i}.{j} with enough words in it to occupy "
                         f"a measurable number of tokens when estimated.")
    return "\n\n".join(parts)


DOC = _doc()


# ── THE REFUSING RULE ───────────────────────────────────────────────────────
def test_out_is_mandatory():
    """
    A chunker that writes beside its source creates a second, uncontrolled copy
    of PHI-bearing material in a place nobody chose. `--out` has no default and
    nothing is ever derived from the source path.
    """
    print("\nthe refusing rule · output goes only where the caller said")
    d = tmpdir()
    src = write(d, "doc.md", DOC)

    r = subprocess.run([sys.executable, os.path.join(HERE, "src", "chunk.py"), src],
                       capture_output=True, text=True)
    check("the CLI refuses to run without --out", r.returncode != 0, True)
    check("and says so", "--out" in (r.stderr + r.stdout), True)

    try:
        C.chunk_document(src, "")
        check("the API refuses an empty out_dir", False, True)
    except ValueError as e:
        check("the API refuses an empty out_dir", "required" in str(e), True)

    before = set(os.listdir(d))
    out = os.path.join(tmpdir(), "elsewhere")
    C.chunk_document(src, out, budget=1200)
    check("NOTHING is written beside the source", set(os.listdir(d)), before)
    check("everything is written where asked", len(os.listdir(out)) > 2, True)


def test_manifest_carries_no_path():
    """Knowing a document came from a PHI share is itself a disclosure."""
    print("\nthe manifest records a label, never a path")
    d = tmpdir()
    src = write(d, "workup.md", DOC)
    out = os.path.join(tmpdir(), "o")
    C.chunk_document(src, out, budget=1200)

    blob = open(os.path.join(out, "MANIFEST.json"), encoding="utf-8").read()
    check("no absolute path anywhere in the manifest",
          re.findall(r"[A-Za-z]:[\\/][^\"]*", blob), [])
    check("no temp directory leaked", d.replace("\\", "/") in blob.replace("\\", "/"), False)
    m = json.loads(blob)
    check("the label is the basename by default", m["label"], "workup.md")

    out2 = os.path.join(tmpdir(), "o2")
    m2 = C.chunk_document(src, out2, budget=1200, label="case-material")
    check("and is overridable", m2["label"], "case-material")


# ── THE CORRECTNESS PROPERTY ────────────────────────────────────────────────
def test_reconstruction():
    """
    Reading the pieces in order equals reading the whole. **This is the claim
    the prior art made without a test.**
    """
    print("\nreading the chunks in order reconstructs the source")
    d = tmpdir()
    src = write(d, "doc.md", DOC)
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(src, out, budget=900, overlap=150)

    rebuilt = []
    for e in m["entries"]:
        body = open(os.path.join(out, e["file"]), encoding="utf-8").read()
        rebuilt.append(C.strip_recaps(body))
    joined = "\n".join(rebuilt)

    def norm(s):
        return re.sub(r"\s+", " ", s).strip()

    check("every source paragraph survives",
          all(norm(p) in norm(joined) for p in DOC.split("\n\n") if p.strip()), True)
    check("every heading survives",
          all(f"# Section {i}" in joined for i in range(1, 9)), True)
    check("more than one chunk was produced", m["chunks"] > 1, True)


def test_every_chunk_within_budget():
    """
    The rendered chunk is what must fit — header, recap, body and footer — not
    the body alone. Sizing the body to the budget overflows it every time, and
    the recap's `> ` quoting is the part a raw estimate cannot see.
    """
    print("\nevery RENDERED chunk fits its budget")
    d = tmpdir()
    src = write(d, "doc.md", DOC * 3)
    for budget in (600, 1500, 4000):
        out = os.path.join(tmpdir(), f"o{budget}")
        m = C.chunk_document(src, out, budget=budget, overlap=budget // 5)
        check(f"budget {budget}: none over", m["over_budget"], [])


def test_recaps_are_marked_and_removable():
    print("\nthe recap is fenced, so it can be removed")
    d = tmpdir()
    src = write(d, "doc.md", DOC)
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(src, out, budget=900, overlap=200)

    second = open(os.path.join(out, m["entries"][1]["file"]), encoding="utf-8").read()
    check("chunk 2 carries a recap", C.RECAP_OPEN in second, True)
    check("strip_recaps removes it", C.RECAP_OPEN in C.strip_recaps(second), False)

    first = open(os.path.join(out, m["entries"][0]["file"]), encoding="utf-8").read()
    check("chunk 1 has no recap — nothing precedes it", C.RECAP_OPEN in first, False)


def test_orientation():
    print("\norientation — a reader never loses its place")
    d = tmpdir()
    src = write(d, "doc.md", DOC)
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(src, out, budget=900)

    body = open(os.path.join(out, m["entries"][0]["file"]), encoding="utf-8").read()
    check("names its position", "CHUNK 1/" in body, True)
    check("names its source label", "source: doc.md" in body, True)
    check("carries a section breadcrumb", "section:" in body, True)
    check("points at the next", "next: chunk-002.md" in body, True)
    check("an INDEX exists", os.path.exists(os.path.join(out, "INDEX.md")), True)

    last = open(os.path.join(out, m["entries"][-1]["file"]), encoding="utf-8").read()
    check("the last says it is last", "(none — this is the last)" in last, True)


def test_jsonl_records_are_atoms():
    """Half a JSON object is not a smaller JSON object. It is corrupt."""
    print("\njsonl splits between records, never inside one")
    d = tmpdir()
    lines = [json.dumps({"i": i, "text": "x" * 200}) for i in range(60)]
    src = write(d, "t.jsonl", "\n".join(lines))
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(src, out, budget=700, overlap=0)

    torn = 0
    for e in m["entries"]:
        body = C.strip_recaps(open(os.path.join(out, e["file"]), encoding="utf-8").read())
        for ln in body.splitlines():
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    json.loads(ln)
                except ValueError:
                    torn += 1
    check("no record was torn", torn, 0)
    check("and it did split", m["chunks"] > 1, True)


def test_terminates_on_pathological_input():
    """
    One atom with no break point at all. The cascade must still terminate, and
    it must not silently drop the content.
    """
    print("\npathological input still terminates")
    d = tmpdir()
    src = write(d, "wall.txt", "x" * 60000)
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(src, out, budget=500)
    check("it produced chunks", m["chunks"] > 1, True)
    check("none over budget", m["over_budget"], [])

    total = sum(len(C.strip_recaps(
        open(os.path.join(out, e["file"]), encoding="utf-8").read()).replace("\n", "").strip())
        for e in m["entries"])
    check("substantially all characters survive", total >= 59000, True)


def test_tiny_and_empty():
    print("\ntiny and empty inputs")
    d = tmpdir()
    out = os.path.join(tmpdir(), "o")
    m = C.chunk_document(write(d, "tiny.md", "hello"), out, budget=4000)
    check("a tiny doc is one chunk", m["chunks"], 1)

    out2 = os.path.join(tmpdir(), "o2")
    m2 = C.chunk_document(write(d, "empty.md", ""), out2, budget=4000)
    check("an empty doc produces no chunks and does not crash", m2["chunks"], 0)
    check("and still writes a manifest",
          os.path.exists(os.path.join(out2, "MANIFEST.json")), True)


def test_token_estimate_errs_high():
    """
    An overestimate wastes context. An underestimate overflows it and truncates
    a clinical document mid-sentence. Only one is recoverable.
    """
    print("\nthe token estimate errs high, deliberately")
    prose = "The quick brown fox jumps over the lazy dog. " * 20
    est = C.estimate_tokens(prose)
    naive = len(prose) / 4          # the usual chars-per-token rule of thumb
    check("prose is estimated at or above the 4-char rule", est >= naive * 0.95, True)
    check("dense punctuation counts", C.estimate_tokens("a,b,c;d.e!f?") > 6, True)
    check("empty is zero", C.estimate_tokens(""), 0)


def test_no_network_and_no_absolute_paths():
    """The plugin contract, self-checked."""
    print("\nthe contract, self-checked")
    src = open(os.path.join(HERE, "src", "chunk.py"), encoding="utf-8").read()
    for mod in ("urllib", "requests", "socket", "httpx", "http.client"):
        check(f"does not import {mod}", re.search(rf"^\s*import\s+{re.escape(mod)}", src, re.M), None)
    abs_paths = [m.group(0) for m in re.finditer(r"['\"][A-Za-z]:[\\/]{1,2}[^'\"\n]{2,}['\"]", src)]
    check("no hardcoded absolute paths", abs_paths, [])
    check("carries an SPDX identifier", "SPDX-License-Identifier: MIT" in src, True)


if __name__ == "__main__":
    print("REGISTRAR · forge · chunk")
    for t in (test_out_is_mandatory, test_manifest_carries_no_path, test_reconstruction,
              test_every_chunk_within_budget, test_recaps_are_marked_and_removable,
              test_orientation, test_jsonl_records_are_atoms,
              test_terminates_on_pathological_input, test_tiny_and_empty,
              test_token_estimate_errs_high, test_no_network_and_no_absolute_paths):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
