#!/usr/bin/env python3
"""
REGISTRAR · forge · does the plugin gate actually refuse?

    python forge/test_conformance.py

**A gate nobody has watched refuse is a gate nobody knows works.** `forge/plugins.yml`
declares four rules whose severity is `refuses_the_mount`; these feed each one a
plugin that violates it, and assert it is caught — and feed each one a plugin
that honours it, and assert it is not.

The second half matters as much as the first. **A gate that cries wolf is worse
than no gate**, because the next real alarm gets discounted.
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import conformance as cf  # noqa: E402

PASS, FAIL = [], []


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print(f"  ok    {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")


def srcs(code: str, name: str = "plugin.py"):
    """One in-memory source file, shaped the way the checkers read them."""
    return [(f"forge/plugins/x/{name}", code)]


# ── chunk · caller_specified_output ─────────────────────────────────────────
def test_chunk_output_path():
    """
    A chunker that writes beside its source silently creates a second,
    uncontrolled copy of PHI-bearing material. This is the single most likely
    way a well-meaning tool leaks here.
    """
    print("\nchunk · output must be caller-specified")

    for code, label in [
        ('out = os.path.join(os.path.dirname(src), ".chunks")\n', "a .chunks dir beside the source"),
        ('d = os.path.dirname(os.path.abspath(source))\nwrite(d, parts)\n', "derived from the input path"),
        ('p = Path(input_path).parent / "out"\n', "the source's parent"),
        ('dest = src_path + ".part1"\n', "a suffix on the source path"),
    ]:
        ok, detail = cf.check_caller_specified_output(srcs(code))
        check(f"REFUSES {label}", ok, False)

    ok, detail = cf.check_caller_specified_output(
        srcs('def chunk(source_path, out_dir, budget):\n    write(out_dir, parts)\n'))
    check("ACCEPTS an explicit out_dir", ok, True)

    ok, _ = cf.check_caller_specified_output(
        srcs('def chunk(source_path, budget):\n    write(somewhere, parts)\n'))
    check("REFUSES a plugin with no output argument at all", ok, False)


# ── phi_scan · floor_not_guarantee ──────────────────────────────────────────
def test_phi_floor():
    """
    A scanner presented as a guarantee is WORSE than no scanner, because it
    retires the human caution that was doing the actual work.
    """
    print("\nphi_scan · a floor, never a guarantee")

    for code, label in [
        ('"""Guarantees no PHI reaches the model."""\n', "the word guarantee"),
        ('"""Ensures no protected information remains."""\n', "ensures-no"),
        ('# after this the text is clean\n', "declares output clean"),
        ('"""Detects 100% of identifiers."""\n', "claims completeness"),
        ('"""Confirms no PHI remains in the span."""\n', "asserts absence"),
    ]:
        ok, _ = cf.check_floor_not_guarantee(srcs(code))
        check(f"REFUSES {label}", ok, False)

    ok, _ = cf.check_floor_not_guarantee(srcs(
        '"""A HIGH-RECALL FLOOR, never a guarantee. Absence of a finding is not\n'
        'evidence of absence, and this must never be described as one."""\n'))
    check("ACCEPTS an explicit floor claim", ok, True)

    # the subtle one: a doc that says "never a guarantee" must not trip the
    # guarantee detector on the word itself
    ok, _ = cf.check_floor_not_guarantee(srcs(
        '"""This is a floor. It is never a guarantee and must not be called one."""\n'))
    check("does NOT trip on the phrase 'never a guarantee'", ok, True)

    ok, _ = cf.check_floor_not_guarantee(srcs('def scan(text):\n    return findings\n'))
    check("REFUSES silence — it must SAY it is a floor", ok, False)


# ── fetch · validate_content ────────────────────────────────────────────────
def test_fetch_validates_content():
    """
    A statute site returned HTTP 200 and an identical 250,874-byte application
    shell for every path tried, including nonsense ones.
    """
    print("\nfetch · content, never status codes")

    ok, _ = cf.check_validate_content(srcs(
        'r = get(url)\nif r.status == 200:\n    return r\n'))
    check("REFUSES success decided on a status code alone", ok, False)

    ok, _ = cf.check_validate_content(srcs(
        'r = get(url)\nif r.status == 200 and expected in r.content:\n    return r.text\n'))
    check("ACCEPTS a content check beside the status", ok, True)


# ── render · no_credentials ─────────────────────────────────────────────────
def test_render_no_credentials():
    print("\nrender · carries no keys")

    for code, label in [
        ('api_key = os.environ["KEY"]\n', "an api key"),
        ('headers = {"Authorization": "Bearer " + tok}\n', "a bearer token"),
        ('password = cfg["pw"]\n', "a password"),
    ]:
        ok, _ = cf.check_no_credentials(srcs(code))
        check(f"REFUSES {label}", ok, False)

    ok, _ = cf.check_no_credentials(srcs(
        '# A render binding carries no api_key and no session: anything needing\n'
        '# authentication is a human\'s job and must not be automated here.\n'))
    check("does NOT trip on a comment forbidding credentials", ok, True)


# ── the declaration-level checks ────────────────────────────────────────────
def test_unbound_is_unverified_not_pass():
    """
    Five nulls is a contract without an implementation. Reporting that as a
    pass would be the exact failure the three-state gate exists to prevent.
    """
    print("\nan unbound capability is PASS-UNVERIFIED, never GREEN")
    cf.RESULTS.clear()
    cf.check_capability({"id": "chunk", "required": True, "binding": None, "rules": []})
    states = {s for s, _, _ in cf.RESULTS}
    check("unbound reports PASS-UNVERIFIED", states, {cf.UNVERIFIED})
    check("and never GREEN", cf.GREEN in states, False)


def test_missing_licence_fails():
    """A binding without a licence cannot mount into an MIT tree."""
    print("\na binding without a LICENSE fails")
    cf.RESULTS.clear()
    real = cf.PLUGINS
    try:
        cf.PLUGINS = tempfile.mkdtemp()
        os.makedirs(os.path.join(cf.PLUGINS, "chunk"), exist_ok=True)
        cf.check_capability({
            "id": "chunk", "required": True, "rules": [],
            "binding": {"version": "1", "source": "s", "pin": "sha256:x",
                        "entry": "e", "licence": "MIT"}})
        rows = {g: s for s, g, _ in cf.RESULTS}
        check("LICENSE absent is FAILED", rows.get("LICENSE file present"), cf.FAILED)
        check("PROVENANCE absent is FAILED", rows.get("PROVENANCE.md"), cf.FAILED)
    finally:
        cf.PLUGINS = real


def test_absolute_paths_fail():
    """A binding that knows where things live on one machine works on one machine."""
    print("\nhardcoded absolute paths fail")
    import re
    hits = list(cf.ABS_PATH.finditer('p = "C:\\\\chunker\\\\chunker.py"'))
    check("a Windows absolute path is detected", len(hits) > 0, True)
    hits2 = list(cf.ABS_PATH.finditer('p = os.path.join(root, "src")'))
    check("a relative join is not", len(hits2), 0)


if __name__ == "__main__":
    print("REGISTRAR · forge · plugin gate")
    for t in (test_chunk_output_path, test_phi_floor, test_fetch_validates_content,
              test_render_no_credentials, test_unbound_is_unverified_not_pass,
              test_missing_licence_fails, test_absolute_paths_fail):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:")
        for f in FAIL:
            print(f"  - {f}")
    raise SystemExit(1 if FAIL else 0)
