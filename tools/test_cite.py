#!/usr/bin/env python3
"""
REGISTRAR · tools · citation gate tests

    python tools/test_cite.py

The gate's only job is to make fabrication mechanically detectable. These tests
feed it the exact shapes a confident model produces and assert that each one is
refused without any judgment being exercised.
"""
from __future__ import annotations
import os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cite  # noqa: E402

PASS, FAIL = [], []
def check(name, got, want):
    if got == want: PASS.append(name); print(f"  ok    {name}")
    else: FAIL.append(name); print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")

SOURCE = (
    "42 CFR 486.301 Condition for Coverage: Definitions and terms.\n"
    "An organ procurement organization must meet the requirements of this subpart.\n"
    "The OPO must have a plan for the timely referral of potential donors.\n"
    "Curly “quotes” and an em—dash appear here too.\n"
)

def with_source(fn):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "src.txt")
        open(p, "w", encoding="utf-8").write(SOURCE)
        m = {"sources": {"s1": {"file": "src.txt", "sha256": cite.sha256(p),
                                "bytes": os.path.getsize(p), "url": "", "accessed": "2026-08-25"}}}
        old = cite.CORPUS
        cite.CORPUS = d
        try:
            fn(m)
        finally:
            cite.CORPUS = old

def test_gate():
    def body(m):
        cache = {}
        def v(quote, source="s1"):
            return cite.verify({"element": "t", "source": source, "quote": quote}, cache, m)[0]

        print("\nthe gate")
        check("verbatim quote is accepted",
              v("The OPO must have a plan for the timely referral of potential donors."), cite.OK)

        # the exact shape a model produces when it is confident and wrong
        check("plausible fabricated regulation is REJECTED",
              v("The OPO must respond to each referral within one hour of notification."), cite.MISMATCH)

        check("one altered word is REJECTED",
              v("The OPO must have a plan for the immediate referral of potential donors."), cite.MISMATCH)

        check("unpinned source is REJECTED", v("anything at all here", "nope"), cite.UNPINNED)

        check("a too-short quote is REJECTED", v("must meet"), cite.MISMATCH)

        print("\nnormalisation folds noise, not meaning")
        check("curly quotes match straight ones",
              v('Curly "quotes" and an em-dash appear here too.'), cite.OK)
        check("collapsed whitespace still matches",
              v("An organ procurement organization    must meet\nthe requirements of this subpart."), cite.OK)
        # but it must NOT be so permissive that meaning survives mangling
        check("case change is NOT folded away",
              v("THE OPO MUST HAVE A PLAN FOR THE TIMELY REFERRAL OF POTENTIAL DONORS."), cite.MISMATCH)

        print("\nthe pin is enforced on the corpus itself")
        # A source is hashed once per run and cached — correct, since a check
        # reads each source once. So a FRESH cache is the honest way to test
        # that the pin is enforced at load rather than assumed.
        path = os.path.join(cite.CORPUS, "src.txt")
        open(path, "a", encoding="utf-8").write("An extra sentence nobody pinned.\n")
        real_quote = "The OPO must have a plan for the timely referral of potential donors."
        fresh: dict = {}
        status = cite.verify({"element": "t", "source": "s1", "quote": real_quote}, fresh, m)[0]

        check("a source that no longer matches its pin is refused", status, "SOURCE-CHANGED")
        # and note this is refused even though the quote genuinely IS in the file —
        # once provenance is in doubt, the content no longer matters
        check("refused even though the quote is still present",
              real_quote in open(path, encoding="utf-8").read(), True)
    with_source(body)

if __name__ == "__main__":
    print("REGISTRAR · tools · cite")
    test_gate()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:"); [print(f"  - {f}") for f in FAIL]
    raise SystemExit(1 if FAIL else 0)
