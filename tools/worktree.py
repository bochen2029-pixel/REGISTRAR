#!/usr/bin/env python3
"""
REGISTRAR · tools · fork worktrees

**One working tree per session, so `git add -A` in one cannot reach another.**

WHY THIS EXISTS

Three sessions shared one working tree and one index on 2026-08-26. The
staging collision happened **twice, in both directions**:

  · mainline ran `git add -A` and swept 60 files belonging to Fork A and Fork C
    into its own commit — **55 of them verbatim OPTN policy text**, which
    reached a public MIT repository before anyone noticed.
  · Fork C, which **had followed the rule** — staged one path by name, checked
    `git diff --cached` — was swept anyway, in the opposite direction.

**Complying did not protect it, because the rule binds whoever stages.** A
partition that says who may WRITE which directories says nothing about who may
STAGE them, and `git add -A` in one session is indistinguishable from another
session's own staging.

`FORKS.md` answered that with a paragraph. **This repository's own law 9 says a
hazard should be unreachable rather than forbidden**, and a shared index is the
hazard. Separate worktrees make the collision impossible: each has **its own
index**, and git refuses to check out the same branch in two of them.

    python tools/worktree.py --list             what exists now
    python tools/worktree.py --provision <dir>  give a worktree what it needs
    python tools/worktree.py --check            am I in one, and is it sane?

WHAT A NEW WORKTREE DOES NOT GET, AND WHY THAT IS MOSTLY CORRECT

A worktree receives **tracked files only.** Three ignored things matter:

  `corpus/*.txt`             the pinned sources. NEEDED — `tools/cite.py` cannot
                             verify a citation without them. Provisioned.
  `deepseek-harness-master`  68 MB, pinned, read-only to every fork. NOT copied:
                             fetch and verify it, or work without it. Copying
                             68 MB per worktree to hold bytes that are already
                             pinned is waste.
  `internal/`                the vault — including the F-PATCH-DELTA answer key.
                             **DELIBERATELY NOT PROVISIONED.** A fork that
                             cannot see the answer key cannot be contaminated by
                             it, and the arm-2 protocol asked for exactly that
                             separation. **The gitignore is doing protocol work
                             here, not just hygiene.**

Zero dependencies.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# fork -> the directories it owns, from FORKS.md
PARTITION = {
    "main": ["experiments/", "core/", "clinical/", "floor/", "conformance/",
             "schema/", "corpus/", "tools/", "percepts/", "profiles/", "adapters/"],
    "fork/plugins": ["forge/"],
    "fork/witnesses": ["examples/worked/rejected/", "gates/"],
    "fork/battery": ["experiments/F-BATTERY-STRENGTH/"],
}


def _git(*a: str, cwd: str = ROOT) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          cwd=cwd).stdout.strip()


def worktrees() -> list[tuple[str, str]]:
    out, cur = [], {}
    for ln in _git("worktree", "list", "--porcelain").splitlines():
        if ln.startswith("worktree "):
            cur = {"path": ln.split(" ", 1)[1]}
        elif ln.startswith("branch "):
            cur["branch"] = ln.split(" ", 1)[1].replace("refs/heads/", "")
            out.append((cur["path"], cur["branch"]))
        elif ln.startswith("detached"):
            cur["branch"] = "(detached)"
            out.append((cur["path"], cur["branch"]))
    return out


def listing() -> int:
    print("worktrees\n")
    for path, branch in worktrees():
        owns = PARTITION.get(branch)
        print(f"  {branch:<18} {path}")
        if owns:
            print(f"  {'':<18} owns: {', '.join(owns[:4])}"
                  + (" …" if len(owns) > 4 else ""))
    print()
    print("  Each has its OWN INDEX. `git add -A` in one cannot reach another,")
    print("  and git refuses to check out the same branch in two of them.")
    return 0


def provision(dest: str) -> int:
    """Give a worktree the ignored material it legitimately needs."""
    if not os.path.isdir(dest):
        print(f"no worktree at {dest}")
        return 1

    print(f"provisioning {dest}\n")

    # the pinned corpus — cite.py cannot verify without it
    src_c = os.path.join(ROOT, "corpus")
    dst_c = os.path.join(dest, "corpus")
    n = 0
    for f in sorted(os.listdir(src_c)):
        if not f.endswith(".txt"):
            continue
        d = os.path.join(dst_c, f)
        if not os.path.exists(d):
            shutil.copy2(os.path.join(src_c, f), d)
            n += 1
    print(f"  corpus            {n} pinned source(s) copied"
          if n else "  corpus            already present")

    # the chassis — pinned, and NOT copied
    if os.path.isdir(os.path.join(dest, "deepseek-harness-master")):
        print("  chassis           present")
    else:
        print("  chassis           ABSENT — by design. It is 68 MB and already")
        print("                    pinned. Fetch and verify if you need it:")
        print("                      python tools/pin_chassis.py --verify")

    # the vault — deliberately withheld
    print("  internal/         WITHHELD ON PURPOSE — the vault holds the")
    print("                    F-PATCH-DELTA answer key, and a fork that cannot")
    print("                    see it cannot be contaminated by it.")

    print("\n  verify:  python conformance/run.py")
    return 0


def check() -> int:
    """Am I in a worktree, on the right branch, staging inside my partition?"""
    here = os.getcwd()
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=here)
    print(f"branch   {branch}")
    print(f"path     {here}\n")

    owns = PARTITION.get(branch)
    if owns is None:
        print(f"  {branch!r} is not a partitioned branch. If this is a fork,")
        print("  add it to PARTITION in this file so the check can protect it.")
        return 2

    staged = [f for f in _git("diff", "--cached", "--name-only", cwd=here).splitlines() if f]
    if not staged:
        print(f"  nothing staged. This branch owns: {', '.join(owns)}")
        return 0

    outside = [f for f in staged if not any(f.startswith(p) for p in owns)]
    print(f"  {len(staged)} staged, {len(outside)} outside this branch's partition")
    for f in outside[:12]:
        print(f"    {f}")
    if outside:
        print()
        print("  These belong to another fork. On a shared tree that was a real")
        print("  collision — 55 files of verbatim policy text reached a public")
        print("  commit that way. On a worktree it is only a warning, because a")
        print("  branch merge is reviewable and a swept index was not.")
        return 1
    print("  every staged path is inside this branch's partition")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--provision" in a:
        raise SystemExit(provision(a[a.index("--provision") + 1]))
    if "--check" in a:
        raise SystemExit(check())
    raise SystemExit(listing())
