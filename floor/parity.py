#!/usr/bin/env python3
"""
REGISTRAR · floor · CPU/GPU parity
─────────────────────────────────────────────────────────────────────────────
Asserts the one property that makes an accelerated closure admissible:

    closure_gpu(D) == closure_cpu(D)      for every fixture, EXACTLY

Not "within tolerance". Not "reproducible in practice". **Bit-identical**,
because the conformance battery contains replay determinism, and a fast path
that produces almost-the-same answer fails it.

That equality is available only because the semiring is integer (min, +),
which is exactly associative. This harness exists to prove the implementation
honours what the arithmetic permits — the two are different claims.

WITHOUT A GPU

    This reports **PASS-UNVERIFIED**, and that is the correct answer rather
    than a degraded one. `floor/tropical.cu` has never been compiled or run in
    this project's reference environment. Reporting GREEN because the CPU side
    agrees with itself would be exactly the failure the three-state gate exists
    to prevent.

WHAT IT STILL CHECKS WITHOUT A GPU

    The claims that do not need a card, and that a wrong kernel would break:

      · the sentinel survives being added to itself in int32
      · repeated squaring and Floyd–Warshall agree — the GPU uses the first,
        the reference the second — on every FEASIBLE network entry-for-entry,
        and on the verdict for every network. They legitimately differ on the
        distances inside an infeasible one, because those are not defined; see
        check_algorithms_agree().
      · the closure is idempotent where idempotence is defined
      · every distance is an int; no float has crept in

    Those are real, and they are the ones that would silently differ.

    python floor/parity.py
"""

from __future__ import annotations

import ctypes
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from closure import INF, STN, load_case  # noqa: E402

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"
LIB = os.path.join(HERE, "libtropical.so")

RESULTS: list[tuple[str, str, str]] = []


def record(state: str, name: str, detail: str = "") -> None:
    RESULTS.append((state, name, detail))
    dots = "." * max(2, 40 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


# ── the reference, and the algorithm the kernel uses ────────────────────────
def closure_floyd(D: list[list[int]]) -> list[list[int]]:
    """Floyd–Warshall in (min,+). What floor/closure.py does."""
    n = len(D)
    out = [row[:] for row in D]
    for k in range(n):
        for i in range(n):
            if out[i][k] >= INF:
                continue
            for j in range(n):
                if out[k][j] >= INF:
                    continue
                s = out[i][k] + out[k][j]
                if s < out[i][j]:
                    out[i][j] = s
    return out


def tropical_mm(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """A ⊗ B — the exact operation floor/tropical.cu implements per block."""
    n = len(A)
    C = [[INF] * n for _ in range(n)]
    for i in range(n):
        Ai, Ci = A[i], C[i]
        for k in range(n):
            a = Ai[k]
            if a >= INF:
                continue
            Bk = B[k]
            for j in range(n):
                b = Bk[j]
                if b >= INF:
                    continue
                s = a + b
                if s < Ci[j]:
                    Ci[j] = s
    return C


def closure_squaring(D: list[list[int]]) -> list[list[int]]:
    """
    Repeated squaring — what the kernel does, because it keeps the batch
    dimension parallel where Floyd–Warshall's k-loop would serialise it.
    """
    n = len(D)
    out = [row[:] for row in D]
    for i in range(n):
        out[i][i] = min(out[i][i], 0)
    steps = max(1, (n - 1).bit_length())
    for _ in range(steps):
        out = tropical_mm(out, out)
        for i in range(n):
            out[i][i] = min(out[i][i], 0)
    return out


def fixture_matrices() -> list[tuple[str, list[list[int]]]]:
    d = os.path.join(ROOT, "fixtures", "cases")
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        stn, _ = load_case(os.path.join(d, fn))
        n = len(stn.names)
        idx = {nm: i for i, nm in enumerate(stn.names)}
        D = [[INF] * n for _ in range(n)]
        for i in range(n):
            D[i][i] = 0
        for c in stn.constraints:
            i, j = idx[c.earlier], idx[c.later]
            if c.weight < D[i][j]:
                D[i][j] = c.weight
        out.append((fn, D))
    return out


# ── checks that need no card ────────────────────────────────────────────────
def check_sentinel() -> None:
    ok = INF + INF < 2**31 - 1
    record(GREEN if ok else FAILED, "sentinel · INF+INF fits int32",
           f"INF={INF:#x}, doubled={INF*2:,} < 2^31-1"
           if ok else "SENTINEL IS WRONG — the kernel would overflow")


def has_negative_cycle(C: list[list[int]]) -> bool:
    return any(C[i][i] < 0 for i in range(len(C)))


def check_algorithms_agree() -> None:
    """
    The kernel uses repeated squaring; the reference uses Floyd–Warshall. If
    those disagree on a FEASIBLE network the GPU would be wrong before hardware
    is ever involved — checkable today, with no card.

    ON NETWORKS THAT ARE INFEASIBLE, THEY LEGITIMATELY DIFFER, and the first
    version of this check was wrong to demand otherwise. When a negative cycle
    exists, "the shortest path" is not a defined quantity — you can traverse
    the cycle arbitrarily many times and drive the distance down without bound.
    Floyd–Warshall relaxes each intermediate once and stops; squaring relaxes
    ⌈log₂ n⌉ times and therefore descends further. Both are correct; neither is
    computing something well-defined.

    What must agree, and does:
      · every feasible network, entry for entry
      · the VERDICT on every network — both detect the negative cycle

    That second property is the one the system actually consumes. `closure.py`
    checks the diagonal and refuses; it never reports a distance from an
    infeasible network. So the kernel and the reference agree everywhere the
    answer is used.
    """
    mismatched_feasible, verdict_disagree = [], []
    fixtures = fixture_matrices()
    for name, D in fixtures:
        f, sq = closure_floyd(D), closure_squaring(D)
        if has_negative_cycle(f) != has_negative_cycle(sq):
            verdict_disagree.append(name)
        elif not has_negative_cycle(f) and f != sq:
            mismatched_feasible.append(name)

    bad = mismatched_feasible + verdict_disagree
    infeasible = sum(1 for _, D in fixtures if has_negative_cycle(closure_floyd(D)))
    record(FAILED if bad else GREEN, "algorithm · squaring ≡ Floyd–Warshall",
           ", ".join(bad) if bad else
           f"{len(fixtures) - infeasible} feasible fixture(s) identical entry-for-entry; "
           f"{infeasible} infeasible, verdict agrees (distances undefined under a negative cycle)")


def check_idempotent() -> None:
    """
    Idempotence holds for feasible networks. Under a negative cycle it does not,
    and must not: re-closing descends the cycle again. Same reason as above.
    """
    fixtures = fixture_matrices()
    feasible = [(n, D) for n, D in fixtures if not has_negative_cycle(closure_floyd(D))]
    bad = [n for n, D in feasible if closure_floyd(closure_floyd(D)) != closure_floyd(D)]
    record(FAILED if bad else GREEN, "closure · idempotent where defined",
           ", ".join(bad) if bad else
           f"{len(feasible)} feasible fixture(s): closing a closed network changes nothing")


def check_integral() -> None:
    bad = []
    for name, D in fixture_matrices():
        C = closure_floyd(D)
        if any(not isinstance(v, int) for row in C for v in row):
            bad.append(name)
    record(FAILED if bad else GREEN, "arithmetic · integral throughout",
           ", ".join(bad) if bad else "no float anywhere; equality is meaningful")


# ── the check that needs one ────────────────────────────────────────────────
def check_gpu_parity() -> None:
    if not os.path.exists(LIB):
        record(UNVERIFIED, "parity · GPU ≡ CPU, bit-identical",
               "libtropical.so not built — see the header of floor/tropical.cu")
        return
    try:
        lib = ctypes.CDLL(LIB)
    except OSError as e:
        record(UNVERIFIED, "parity · GPU ≡ CPU, bit-identical", f"could not load: {e}")
        return

    # A real run would marshal each fixture, call the kernel, and compare
    # element-wise. The comparison is `==`, never `abs(a-b) < eps`.
    record(UNVERIFIED, "parity · GPU ≡ CPU, bit-identical",
           "library present but the host harness is unwritten — "
           "this is the receipt this kernel does not yet have")
    _ = lib


def main() -> int:
    print("REGISTRAR · floor · CPU/GPU parity\n")
    check_sentinel()
    check_algorithms_agree()
    check_idempotent()
    check_integral()
    check_gpu_parity()

    states = {s for s, _, _ in RESULTS}
    print()
    if FAILED in states:
        print("FAILED — the accelerated path is not admissible.")
        return 1
    if UNVERIFIED in states:
        print("PASS-UNVERIFIED — the CPU-side invariants hold, and the GPU parity")
        print("  check has NOT run. That is not a pass. floor/tropical.cu carries")
        print("  no measured claim until somebody executes this on real hardware.")
        return 2
    print("GREEN — bit-identical on every fixture.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
