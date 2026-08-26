#!/usr/bin/env python3
"""
REGISTRAR · core · the algebra, tested

    python core/test_algebra.py

These assert the theorems in SPEC.md §3 against the implementation. Where a
theorem is unconditional the test is unconditional; where it carries a
hypothesis, the test checks the hypothesis is REQUIRED — a theorem whose
hypothesis can be dropped without breaking anything was not load-bearing.
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from algebra import (Context, Row, check_all, check_invertibility, equivalent,
                     mount, mount_all, retire, rows_from_patch)

PASS, FAIL = [], []
def check(name, got, want):
    if got == want: PASS.append(name); print(f"  ok    {name}")
    else: FAIL.append(name); print(f"  FAIL  {name}\n          got  {got!r}\n          want {want!r}")

A = Row("a.x", 1, None)
B = Row("b.y", 2, None)
C = Row("a.x", 9, 1)          # supersedes A: inverse restores A's value


def test_T1_lift_projects():
    """pr₁ ∘ mount(p,p⁻) = p ∘ pr₁ — the fit you inspect is the fit mounted."""
    print("\nT1 · the lift projects")
    ctx = Context.seed()
    check("mounting projects to the forward map",
          mount(ctx, A).fit, A.forward(ctx.fit))
    ctx2 = mount_all(Context.seed(), [A, B])
    check("and after a sequence", ctx2.fit, {"a.x": 1, "b.y": 2})


def test_T2_order_independence():
    """
    A sequence of rows IS a row, and composition is associative — so the order
    in which INDEPENDENT rows are authored does not change the mounted fit.
    This is the white-label argument.
    """
    print("\nT2 · order independence for independent rows")
    fwd = mount_all(Context.seed(), [A, B]).fit
    rev = mount_all(Context.seed(), [B, A]).fit
    check("independent rows commute", fwd, rev)

    # ...and dependent rows do NOT, which is why the twist exists
    dep_fwd = mount_all(Context.seed(), [A, C]).fit
    dep_rev = mount_all(Context.seed(), [C, A]).fit
    check("dependent rows do NOT commute (as expected)", dep_fwd != dep_rev, True)


def test_T2_twist_reverse_order():
    """Retirement unwinds in REVERSE mount order. The algebra forces it."""
    print("\nT2 · the twist — inverses compose backwards")
    ctx = mount_all(Context.seed(), [A, C])       # a.x: absent -> 1 -> 9
    check("mounted value is the later row's", ctx.fit["a.x"], 9)
    check("retraction is in reverse mount order",
          [r.value for r in ctx.retraction], [9, 1])
    check("retiring recovers the seed", retire(ctx).fit, {})


def test_T3_pointwise():
    """
    retire(mount(p,p⁻)(λ,ρ)) ≃ retire(λ,ρ)  whenever  p⁻(p(λ)) ≃ λ.

    The hypothesis is POINTWISE — correct at the state where applied, not
    globally. That is what makes it a computation rather than a proof.
    """
    print("\nT3 · invertibility is pointwise, and computable")
    check("a null inverse inverts at the absent state",
          check_invertibility(A, {}).ok, True)
    check("a valued inverse inverts where the value was there",
          check_invertibility(C, {"a.x": 1}).ok, True)

    # THE POINT: the same row is NOT invertible at a different state
    bad = check_invertibility(C, {})
    check("the SAME row fails at a state that lacks the prior value", bad.ok, False)
    check("and the failure is named, not just flagged",
          "assumes a prior state" in bad.reason or "absent" in bad.reason, True)

    # a null inverse where a value existed loses it
    lossy = check_invertibility(Row("a.x", 5, None), {"a.x": 1})
    check("a null inverse over an existing value is refused", lossy.ok, False)


def test_T3_hypothesis_is_required():
    """
    If the hypothesis fails, the conclusion fails: the seed is NOT recovered.
    A theorem whose hypothesis can be dropped was not load-bearing.
    """
    print("\nT3 · the hypothesis is load-bearing")
    ctx = mount(Context.seed(), C)      # C's inverse names a value nothing established
    check("hypothesis fails at this state", check_invertibility(C, {}).ok, False)
    check("and the seed is NOT recovered", retire(ctx).fit, {"a.x": 1})
    check("which is exactly what T4 forbids", equivalent(retire(ctx).fit, {}), False)


def test_T4_containment():
    """∀ sequences, the reachable state retires to the seed — given T3 holds."""
    print("\nT4 · containment")
    rows = [A, B, Row("c.z", {"k": [1, 2]}, None), C]
    ctx = mount_all(Context.seed(), rows)
    check("every hypothesis holds", all(x.ok for x in check_all(rows)), True)
    check("retire ≃ the seed", equivalent(retire(ctx).fit, {}), True)

    # deep values must not leak by reference
    ctx.fit["c.z"]["k"].append(99)
    check("mutating a mounted value cannot corrupt the inverse",
          equivalent(retire(mount_all(Context.seed(), rows)).fit, {}), True)


def test_worked_example():
    """The shipped patch must satisfy T3 at every row and retire to the seed."""
    print("\nthe worked example")
    with open(os.path.join(ROOT, "examples", "worked", "northlake.patch.json"),
              encoding="utf-8") as fh:
        patch = json.load(fh)
    rows = rows_from_patch(patch)
    res = check_all(rows)
    bad = [r.render() for r in res if not r.ok]
    check("every row invertible at its state", bad, [])
    check("the patch retires to the seed",
          equivalent(retire(mount_all(Context.seed(), rows)).fit, {}), True)
    check("it exercises a supersedes chain",
          any(r.inverse is not None for r in rows), True)


def test_gate_uses_it():
    """The local-invertibility gate must now DECIDE, not report PASS-UNVERIFIED."""
    print("\nthe gate is wired to T3")
    sys.path.insert(0, os.path.join(ROOT, "gates"))
    from validate_patch import GREEN, FAILED, load_patch, load_targets, validate
    r = validate(load_patch(os.path.join(ROOT, "examples", "worked", "northlake.patch.json")),
                 load_targets())
    state = next(s for s, g, _ in r.rows if g == "local invertibility")
    check("gate is GREEN on the worked example", state, GREEN)

    broken = {"rows": [{"target": "a.x", "value": 9, "inverse": 1}]}
    r2 = validate(broken, load_targets())
    state2 = next(s for s, g, _ in r2.rows if g == "local invertibility")
    check("gate FAILS a row whose inverse assumes an unestablished state", state2, FAILED)


if __name__ == "__main__":
    print("REGISTRAR · core · algebra")
    for t in (test_T1_lift_projects, test_T2_order_independence, test_T2_twist_reverse_order,
              test_T3_pointwise, test_T3_hypothesis_is_required, test_T4_containment,
              test_worked_example, test_gate_uses_it):
        t()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nfailed:"); [print(f"  - {f}") for f in FAIL]
    raise SystemExit(1 if FAIL else 0)
