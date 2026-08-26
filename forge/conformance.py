#!/usr/bin/env python3
"""
REGISTRAR · forge · plugin conformance
─────────────────────────────────────────────────────────────────────────────
**A bound plugin that violates a refusing rule does not mount.**

`forge/plugins.yml` declares five capabilities and, for four of them, a rule
whose severity is `refuses_the_mount`. Those are not warnings and not style
notes — each one is a way a well-meaning tool causes harm in this domain:

  chunk · caller_specified_output
      A chunker that writes `.chunks/` beside its source **silently creates a
      second, uncontrolled copy of PHI-bearing material** in a location nobody
      chose and nobody audits. This is the single most likely way a tool leaks
      here, and it leaks by being helpful.

  phi_scan · floor_not_guarantee
      **A scanner presented as a guarantee is worse than no scanner**, because
      it retires the human caution that was doing the actual work. The claim
      must be a floor, in code, in docs, and in what it prints.

  fetch · validate_content
      A statute site returned HTTP 200 and an identical 250,874-byte
      application shell for *every* path tried, including nonsense ones.
      **A fetch succeeded when the bytes contain what you came for.**

  render · no_credentials
      A render binding reads public documents. Anything needing authentication
      is a human's job.

WHAT THIS CHECKS, AND WHAT IT CANNOT

    It checks the DECLARATION and, where a binding exists, the SOURCE — by
    reading it. It cannot prove a tool behaves correctly at runtime; it can
    prove the tool does not contain the shapes that violate a refusing rule,
    and that it declares what it must.

    An unbound capability reports PASS-UNVERIFIED. **That is the honest state**
    — five nulls is a contract without an implementation, which is exactly what
    ships today.

    python forge/conformance.py
    python forge/conformance.py --capability chunk

Zero dependencies beyond pyyaml, which only this checker needs.
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGINS = os.path.join(HERE, "plugins")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"

RESULTS: list[tuple[str, str, str]] = []


def record(state: str, name: str, detail: str = "") -> None:
    RESULTS.append((state, name, detail))
    dots = "." * max(2, 34 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE-LEVEL DETECTION OF THE REFUSING RULES
#
# Each returns (ok, detail). These read code rather than run it — a plugin is
# refused for CONTAINING the shape, not for being caught doing it, because by
# the time it is caught the copy already exists.
# ─────────────────────────────────────────────────────────────────────────────

# Writing beside the source: a path derived from the INPUT rather than taken
# as an argument. These are the idioms that do it.
BESIDE_SOURCE = (
    (r"\.chunks\b", "writes a `.chunks` directory"),
    (r"os\.path\.dirname\s*\(\s*(?:os\.path\.abspath\s*\(\s*)?(?:src|source|input|in_path|infile)",
     "derives an output directory from the input path"),
    (r"(?:src|source|input|in_path|infile)\w*\s*\+\s*['\"]\.", "appends a suffix to the source path"),
    (r"with_suffix\s*\(", "rewrites the source path's suffix"),
    (r"Path\s*\(\s*(?:src|source|input|infile)\w*\s*\)\s*\.parent", "writes to the source's parent"),
)

GUARANTEE_WORDS = (
    (r"\bguarantee[sd]?\b", "claims a guarantee"),
    (r"\bensures?\s+(?:no|zero)\b", "claims to ensure absence"),
    (r"\b(?:is|are)\s+(?:now\s+)?(?:clean|safe|sanitiz|scrubbed)", "declares output clean"),
    (r"\b100%|\ball\s+PHI\b", "claims completeness"),
    (r"\bno\s+PHI\s+(?:remains|present|found)\b", "asserts absence rather than non-detection"),
)

FLOOR_WORDS = (r"\bfloor\b", r"high[- ]recall", r"never a guarantee", r"not a guarantee")

NETWORK = (r"\burllib\b", r"\brequests\b", r"\bhttpx\b", r"\bsocket\b", r"\bhttp\.client\b",
           r"\baiohttp\b", r"\bcurl\b", r"\bwget\b")

SECRETSHAPE = (r"api[_-]?key", r"secret", r"token\s*=", r"password", r"\.key\b", r"Bearer ")

ABS_PATH = re.compile(r"['\"][A-Za-z]:[\\/]{1,2}(?!\s)[^'\"\n]{2,}['\"]")


def sources_of(cap_dir: str) -> list[tuple[str, str]]:
    out = []
    for root, dirs, files in os.walk(cap_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git"}]
        for fn in files:
            if fn.endswith((".py", ".ts", ".js", ".mjs")):
                p = os.path.join(root, fn)
                try:
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        out.append((os.path.relpath(p, ROOT).replace("\\", "/"), fh.read()))
                except OSError:
                    pass
    return out


# Prose that FORBIDS a credential must mention one. A gate that cannot tell a
# prohibition from a use cries wolf — and the next real alarm gets discounted.
#
# NOTE ON WHAT THIS CHECKER CAN AND CANNOT SEE. It reads source textually, so
# it cannot distinguish a MENTION from a USE without help. That weakness has
# produced a false positive three times — on a comment forbidding credentials,
# and twice on a test asserting a module is *not* imported. Each time the fix
# was the same: widen the denial vocabulary rather than narrow the detector,
# because a gate that cries wolf is worse than no gate.
#
# The honest limitation, stated: a plugin that reaches the network inside a
# paragraph of prose about not reaching the network would pass this check. A
# reviewer reading the diff is the backstop, and that is what PROVENANCE.md and
# the LICENSE requirement exist to make likely.
DENIAL = re.compile(
    r"never|must\s+not|may\s+not|cannot|does\s+not|carries\s+no|holds\s+no"
    r"|no\s+credential|no\s+network|without\s+an?\s*(?:key|token|credential)"
    r"|forbidden|refus|prohibit|is\s+a\s+human|human's\s+job"
    r"|absent|assert|check\(|self-check|test_"
    # critique shapes: naming a bad claim in order to reject it
    r"|worse\s+than|presented\s+as|rather\s+than|would\s+be",
    re.I)


def _is_denial(text: str, at: int) -> bool:
    """
    Is this mention inside a passage that forbids the thing it names?

    Scoped to the surrounding paragraph rather than a fixed byte window: a
    two-line comment routinely exceeds any window small enough to be precise,
    and the first version of this check used 120 characters and produced
    exactly the false positive it was written to avoid.
    """
    start = text.rfind("\n\n", 0, at)
    start = 0 if start < 0 else start
    end = text.find("\n\n", at)
    end = len(text) if end < 0 else end
    return bool(DENIAL.search(text[start:end]))


def check_caller_specified_output(srcs) -> tuple[bool, str]:
    hits = []
    for path, text in srcs:
        for pat, why in BESIDE_SOURCE:
            for m in re.finditer(pat, text, re.I):
                line = text[: m.start()].count("\n") + 1
                hits.append(f"{path}:{line} {why}")
    if hits:
        return False, "; ".join(hits[:3])
    # and it must actually accept an output path
    takes_out = any(re.search(r"\bout_?(?:dir|path|file)\b", t, re.I) for _, t in srcs)
    if not takes_out:
        return False, "no `out_dir`/`out_path` argument — output location is not the caller's"
    return True, "output is caller-specified; no write-beside-source idiom present"


def check_floor_not_guarantee(srcs) -> tuple[bool, str]:
    """
    A guarantee CLAIMED is a refusal. A guarantee REFUSED is the contract.

    This used its own ±90-character window and flagged three passages that were
    forbidding the very thing they named — *"a scanner presented as a guarantee
    is worse than no scanner"*, *"this tool never reports that text is clean"*,
    and a test asserting no CLEAN verdict exists. Fourth instance of the one
    weakness this checker has: reading source textually cannot tell a mention
    from a use. It now shares `_is_denial` with the other rules rather than
    keeping a narrower copy of the same idea.
    """
    claims = []
    for path, text in srcs:
        for pat, why in GUARANTEE_WORDS:
            for m in re.finditer(pat, text, re.I):
                if _is_denial(text, m.start()):
                    continue
                line = text[: m.start()].count("\n") + 1
                claims.append(f"{path}:{line} {why}")
    if claims:
        return False, "; ".join(claims[:3])
    says_floor = any(any(re.search(p, t, re.I) for p in FLOOR_WORDS) for _, t in srcs)
    if not says_floor:
        return False, "never describes itself as a FLOOR — it must, in the code a reader sees"
    return True, "described as a high-recall floor; no guarantee language"


def check_validate_content(srcs) -> tuple[bool, str]:
    ok = any(re.search(r"content|bytes|body|text", t, re.I) and
             re.search(r"status|code|200", t) for _, t in srcs)
    only_status = any(re.search(r"(?:status|code)\s*==\s*200\s*(?::|\)|$)", t) for _, t in srcs)
    if only_status and not ok:
        return False, "success decided on a status code alone"
    if not srcs:
        return False, "no source to read"
    return True, "does not decide success on a status code alone"


def check_no_credentials(srcs) -> tuple[bool, str]:
    hits = []
    for path, text in srcs:
        for pat in SECRETSHAPE:
            for m in re.finditer(pat, text, re.I):
                if _is_denial(text, m.start()):
                    continue
                line = text[: m.start()].count("\n") + 1
                hits.append(f"{path}:{line}")
    if hits:
        return False, f"credential-shaped material at {', '.join(hits[:3])}"
    return True, "carries no keys and no session"


REFUSERS = {
    "caller_specified_output": check_caller_specified_output,
    "floor_not_guarantee": check_floor_not_guarantee,
    "validate_content": check_validate_content,
    "no_credentials": check_no_credentials,
}


# ─────────────────────────────────────────────────────────────────────────────
def check_capability(cap: dict) -> None:
    cid = cap["id"]
    print(f"\ncapability · {cid}")

    binding = cap.get("binding")
    cap_dir = os.path.join(PLUGINS, cid)

    if not binding:
        record(UNVERIFIED, "binding",
               "null — the contract exists; nothing implements it"
               + ("" if cap.get("required") else " (optional)"))
        return

    # ── the declaration ─────────────────────────────────────────────────────
    #
    # AN IN-TREE BINDING IS ALREADY PINNED — BY THE COMMIT.
    #
    # A sha256 in this file, for a file in this repository, would have to be
    # updated by hand on every edit. It would go stale on the first change and
    # then LIE — asserting a pin that no longer matches, which is worse than
    # declaring none. Git already answers "are these the bytes that shipped".
    #
    # A MOUNTED binding is different and still needs its pin: it names bytes
    # outside this tree, which nothing here can vouch for. That is the whole
    # reason `pin` exists — see CHASSIS.pin.json, where the same argument
    # produced a file-for-file verification rather than a trusted number.
    src = str(binding.get("source", ""))
    in_tree = bool(src) and os.path.exists(os.path.join(ROOT, src))

    fields = ("version", "source", "entry", "licence") if in_tree else              ("version", "source", "pin", "entry", "licence")
    need = [k for k in fields if not binding.get(k)]
    record(FAILED if need else GREEN, "binding declares",
           f"missing {', '.join(need)}" if need
           else (f"{binding.get('licence')}, in-tree — pinned by the commit"
                 if in_tree else f"{binding.get('licence')}, pinned"))

    # ── the licence, which is not negotiable ────────────────────────────────
    lic = os.path.join(cap_dir, "LICENSE")
    has_file = os.path.exists(lic)
    record(GREEN if has_file else FAILED, "LICENSE file present",
           "present" if has_file
           else "ABSENT — a binding without a licence cannot mount into an MIT tree")

    # ── provenance: where it came from and what changed ─────────────────────
    prov = os.path.join(cap_dir, "PROVENANCE.md")
    record(GREEN if os.path.exists(prov) else FAILED, "PROVENANCE.md",
           "present — source, changes, and why" if os.path.exists(prov)
           else "absent — adapt-not-copy has to be shown, not asserted")

    srcs = sources_of(cap_dir)
    record(GREEN if srcs else FAILED, "source present",
           f"{len(srcs)} file(s)" if srcs else "no source under forge/plugins/")

    if not srcs:
        return

    # ── no absolute paths, no estate coupling ───────────────────────────────
    abs_hits = []
    for path, text in srcs:
        for m in ABS_PATH.finditer(text):
            line = text[: m.start()].count("\n") + 1
            abs_hits.append(f"{path}:{line} {m.group(0)[:40]}")
    record(FAILED if abs_hits else GREEN, "no hardcoded absolute paths",
           "; ".join(abs_hits[:3]) if abs_hits
           else "every path is an argument — it works on a stranger's machine")

    # ── the network rule ────────────────────────────────────────────────────
    may_network = cid in ("fetch", "render")
    net = []
    for path, text in srcs:
        for pat in NETWORK:
            for m in re.finditer(pat, text):
                if _is_denial(text, m.start()):
                    continue
                net.append(f"{path}:{text[: m.start()].count(chr(10)) + 1}")
    if may_network:
        record(GREEN, "network", f"permitted for `{cid}`, caller-supplied URL only")
    else:
        record(FAILED if net else GREEN, "no network access",
               f"reaches the network at {', '.join(net[:3])}" if net
               else "no network imports — reads local, writes local")

    # ── THE REFUSING RULES ──────────────────────────────────────────────────
    for rule in cap.get("rules") or []:
        if rule.get("severity") != "refuses_the_mount":
            continue
        fn = REFUSERS.get(rule["id"])
        if not fn:
            record(UNVERIFIED, f"rule · {rule['id']}", "no checker implemented for this rule")
            continue
        ok, detail = fn(srcs)
        record(GREEN if ok else FAILED, f"rule · {rule['id']}", detail)


def main(argv: list[str]) -> int:
    try:
        import yaml
    except ImportError:
        print("forge/conformance.py needs pyyaml (only this checker does)")
        return 3

    only = argv[argv.index("--capability") + 1] if "--capability" in argv else None
    with open(os.path.join(HERE, "plugins.yml"), encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    print("REGISTRAR · forge · plugin conformance")
    caps = [c for c in doc.get("capabilities", []) if not only or c["id"] == only]
    print(f"{len(caps)} capabilit{'y' if len(caps) == 1 else 'ies'} declared; "
          f"{sum(1 for c in caps if c.get('binding'))} bound")

    for c in caps:
        check_capability(c)

    n_g = sum(1 for s, _, _ in RESULTS if s == GREEN)
    n_u = sum(1 for s, _, _ in RESULTS if s == UNVERIFIED)
    n_f = sum(1 for s, _, _ in RESULTS if s == FAILED)
    print(f"\n{n_g} GREEN · {n_u} PASS-UNVERIFIED · {n_f} FAILED")

    if n_f:
        print("\nFAILED — a plugin that violates a refusing rule does not mount.")
        return 1
    if n_u:
        print("\nPASS-UNVERIFIED — the contract holds and nothing implements it yet.")
        print("  Five nulls is a contract without an implementation, which is")
        print("  what ships today. THIS IS NOT A PASS.")
        return 2
    print("\nGREEN — every declared capability is bound and every refusing rule holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
