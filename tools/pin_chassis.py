#!/usr/bin/env python3
"""
REGISTRAR · tools · the chassis pin
─────────────────────────────────────────────────────────────────────────────
Verify that the vendored-in-place harness is byte-for-byte what upstream
published at the tag `CHASSIS.pin.json` names.

**Why this exists rather than a `.gitignore` line.** Sixty-eight megabytes of
third-party code sits in this repository's root. Before the pin, the only thing
keeping it out of the public tree was one ignore rule — and an ignore rule is a
preference, not a fence. **Unpinned third-party code must never become
load-bearing**, and a records system in a regulated domain is adopted on its
dependencies as much as on its properties.

    python tools/pin_chassis.py --check      verify against the recorded digests
    python tools/pin_chassis.py --verify     re-fetch upstream and compare, file by file
    python tools/pin_chassis.py --record     recompute the local digest after a deliberate change

`--check` is offline and fast: it recomputes the local tree digest and compares
it to the pin. `--verify` is the real one — it downloads the tagged tarball and
compares **every file**, which is what turns "we recorded a number" into "we
know these are the bytes DeepSeek published."

**COMPOSE, NEVER FORK.** The verification is what proves no upstream file has
been modified. A fork inherits permanent maintenance and destroys the upgrade
path; a pinned tree composed to a profile does not — and this tool is the
difference between claiming that and demonstrating it.

Zero dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tarfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIN = os.path.join(ROOT, "CHASSIS.pin.json")
TREE = os.path.join(ROOT, "deepseek-harness-master")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Build artifacts and VCS metadata are not the component. Excluding them is what
# makes the digest reproducible on a machine that has run `pnpm install`.
SKIP = {"node_modules", ".git", "dist", ".turbo", ".cache"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def tree_digests(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, path).replace("\\", "/")
            try:
                with open(p, "rb") as fh:
                    out[rel] = sha(fh.read())
            except OSError:
                pass
    return out


def merkle(d: dict[str, str]) -> str:
    """One reproducible identity for a tree. Path and content, in sorted order."""
    h = hashlib.sha256()
    for k in sorted(d):
        h.update(k.encode())
        h.update(d[k].encode())
    return h.hexdigest()


def load_pin() -> dict:
    with open(PIN, encoding="utf-8") as fh:
        return json.load(fh)


# ── offline ─────────────────────────────────────────────────────────────────
def check() -> int:
    pin = load_pin()
    if not os.path.isdir(TREE):
        print("chassis not on disk.")
        print(f"  fetch: {pin['upstream']['tarball']}")
        print("  then:  python tools/pin_chassis.py --verify")
        return 2

    local = tree_digests(TREE)
    got = merkle(local)
    want = pin["verification"]["tree_digest_local"]

    print(f"chassis · {pin['component']} {pin['version']} ({pin['licence']})")
    print(f"  tag     {pin['upstream']['tag']}")
    print(f"  commit  {pin['upstream']['commit'][:12]}")
    print(f"  files   {len(local):,}\n")

    if got == want:
        print(f"  ok    local tree digest matches the pin")
        print(f"        {got}")
        print(f"\n  {pin['verification']['identical']:,} of "
              f"{pin['verification']['upstream_files']:,} upstream files verified byte-identical "
              f"on {pin['verification']['verified']}.")
        print("  Run --verify to re-establish that against upstream rather than against this record.")
        return 0

    print("  FAILED  the local tree does not match the pin")
    print(f"    recorded {want}")
    print(f"    computed {got}")

    # say WHICH files, because "something changed" teaches nothing
    ref = pin.get("_file_digests")
    if ref:
        differ = sorted(k for k in ref.keys() & local.keys() if ref[k] != local[k])
        gone = sorted(ref.keys() - local.keys())
        added = sorted(local.keys() - ref.keys())
        for label, xs in (("modified", differ), ("removed", gone), ("added", added)):
            if xs:
                print(f"\n    {label} ({len(xs)}):")
                for x in xs[:10]:
                    print(f"      {x}")
    else:
        print("\n    (no per-file record in the pin — run --verify to find out which)")
    return 1


# ── the real one ────────────────────────────────────────────────────────────
def verify() -> int:
    pin = load_pin()
    up_url = pin["upstream"]["tarball"]
    tmp = os.path.join(ROOT, "corpus", "_chassis_verify.tar.gz")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)

    print(f"fetching {pin['upstream']['tag']} …")
    req = urllib.request.Request(up_url, headers={"User-Agent": "REGISTRAR/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as fh:
        fh.write(r.read())

    tar_sha = sha(open(tmp, "rb").read())
    want_sha = pin["upstream"]["tarball_sha256"]
    if tar_sha != want_sha:
        print(f"  FAILED  tarball sha256 does not match the pin")
        print(f"    recorded {want_sha}")
        print(f"    fetched  {tar_sha}")
        print("\n  Upstream re-tagged, or the download is not what was pinned. STOP.")
        os.remove(tmp)
        return 1
    print(f"  ok    tarball sha256 matches ({tar_sha[:16]}…)")

    up: dict[str, str] = {}
    with tarfile.open(tmp, "r:gz") as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            parts = m.name.split("/", 1)
            rel = (parts[1] if len(parts) > 1 else parts[0]).replace("\\", "/")
            if any(p in SKIP for p in rel.split("/")):
                continue
            f = t.extractfile(m)
            if f:
                up[rel] = sha(f.read())
    os.remove(tmp)

    local = tree_digests(TREE)
    same = {k for k in up.keys() & local.keys() if up[k] == local[k]}
    differ = sorted(k for k in up.keys() & local.keys() if up[k] != local[k])
    missing = sorted(up.keys() - local.keys())
    extra = sorted(local.keys() - up.keys())

    print(f"\n  upstream  {len(up):,} files")
    print(f"  identical {len(same):,}")
    print(f"  differing {len(differ):,}")
    print(f"  missing   {len(missing):,}")
    print(f"  extra     {len(extra):,}")

    allowed = set(pin.get("local_additions", {}).get("files", []))
    unexpected = sorted(set(extra) - allowed)

    if differ or missing:
        print("\n  FAILED — the local tree is NOT what upstream published.")
        for label, xs in (("modified", differ), ("missing", missing)):
            for x in xs[:10]:
                print(f"    {label}: {x}")
        print("\n  COMPOSE, NEVER FORK. A modified upstream file is a fork, and it")
        print("  inherits permanent maintenance and destroys the upgrade path.")
        return 1

    if unexpected:
        print(f"\n  FAILED — {len(unexpected)} local file(s) not accounted for in the pin:")
        for x in unexpected[:10]:
            print(f"    {x}")
        print("\n  Every local addition must be enumerated and justified in CHASSIS.pin.json.")
        return 1

    print(f"\n  GREEN — every upstream file byte-identical; "
          f"{len(extra)} local addition(s), all accounted for.")
    return 0


def record() -> int:
    """Recompute the local digest. Only after a change you INTEND."""
    pin = load_pin()
    local = tree_digests(TREE)
    pin["verification"]["tree_digest_local"] = merkle(local)
    with open(PIN, "w", encoding="utf-8") as fh:
        json.dump(pin, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"recorded local tree digest: {pin['verification']['tree_digest_local']}")
    print("Run --verify before trusting it: a recorded digest proves only that")
    print("the bytes have not changed since you recorded them.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--verify" in a:
        raise SystemExit(verify())
    if "--record" in a:
        raise SystemExit(record())
    if "--check" in a or not a:
        raise SystemExit(check())
    print(__doc__)
    raise SystemExit(2)
