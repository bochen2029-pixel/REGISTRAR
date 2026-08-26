#!/usr/bin/env python3
"""
REGISTRAR · core · the algebra of the fit, executable
─────────────────────────────────────────────────────────────────────────────
`SPEC.md` §3 states six theorems about mounting and retiring patch rows. Until
now they lived in prose. This module implements the objects so the theorems can
be *run* — and, more importantly, so the local-invertibility gate can stop
reporting PASS-UNVERIFIED and start deciding.

    Σ = {σ₀}            the seed — a singleton, because L0 is law
    Λ                    the fit — the only mutable space
    ∂Λ = Λ × (Λ → Λ)     the fit context: (λ, ρ) — mounted fit + RETRACTION

    mount(p, p⁻) : (λ, ρ) ↦ ( p(λ), ρ ∘ p⁻ )
    retire       : (λ, ρ) ↦ ( ρ(λ), id )

ON `≃` RATHER THAN `=`

The source paper is explicit that strict state equality is an idealization —
freeing a block does not restore the heap's prior layout, and a discarded
generative name is not the one the next allocation draws. The equalities are to
be read up to **observational equivalence**: two states are related when no
observer can distinguish them.

For a configuration layer that is not a weakening, it is the correct notion.
`equivalent()` below is that relation, made concrete for this domain: two fits
agree when every declared target reads the same. Bookkeeping a fit carries
about itself — ordering, insertion history, absent-vs-null — is not observable
and does not count.

WHAT THIS BUYS, CONCRETELY

T3's hypothesis is `p⁻(p(λ)) ≃ λ` **pointwise** — the inverse need not invert
the whole configuration space, only the state where it is applied. That is a
computation, not a proof obligation, and `check_invertibility()` performs it.
The gate that was named after this theorem can now enforce it.

Zero dependencies. Python 3.9+.
"""

from __future__ import annotations

import copy
import sys

# Strangers run this on their own consoles, and a Windows default is cp1252 —
# which cannot encode the algebra's own notation. Learned from fetch_states.py.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from dataclasses import dataclass
from typing import Any, Callable, Iterable

# A fit is a mapping from declared target ids to values. Nothing more: the
# targets are enumerated by the seed (core/lifecycle/targets.json), so the
# space is bounded by construction rather than by convention.
Fit = dict[str, Any]

ABSENT = object()   # distinct from None, which is a legal value


# ── observational equivalence ───────────────────────────────────────────────
def equivalent(a: Fit, b: Fit) -> bool:
    """
    `a ≃ b` — no observer can distinguish them.

    An observer of a fit sees the value at each declared target. It does not
    see dict ordering, and it cannot distinguish "absent" from "present with
    the absent sentinel". Anything else is representation, not behaviour.
    """
    keys = set(a) | set(b)
    return all(a.get(k, ABSENT) == b.get(k, ABSENT) for k in keys)


def difference(a: Fit, b: Fit) -> dict[str, tuple]:
    """Where two fits are distinguishable. Empty iff a ≃ b."""
    out = {}
    for k in set(a) | set(b):
        av, bv = a.get(k, ABSENT), b.get(k, ABSENT)
        if av != bv:
            out[k] = ("<absent>" if av is ABSENT else av,
                      "<absent>" if bv is ABSENT else bv)
    return out


# ── the objects ─────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Row:
    """
    One patch row, as an element of the monoid: a (change, inverse) PAIR.

    Without `inverse` the pair is not an element and `mount` is undefined on
    it — which is why the schema makes the field mandatory. That is the algebra
    speaking, not a policy someone could relax under deadline.
    """
    target: str
    value: Any
    inverse: Any
    id: str = ""

    def forward(self, fit: Fit) -> Fit:
        out = dict(fit)
        out[self.target] = copy.deepcopy(self.value)
        return out

    def backward(self, fit: Fit) -> Fit:
        out = dict(fit)
        if self.inverse is None:
            # null inverse means "there was no prior value here" — so the
            # inverse of installing it is removing it, not writing null.
            out.pop(self.target, None)
        else:
            out[self.target] = copy.deepcopy(self.inverse)
        return out


@dataclass
class Context:
    """∂Λ — the mounted fit, and the retraction that returns it to the seed."""
    fit: Fit
    retraction: list[Row]      # inverses, in the order they must be applied

    @classmethod
    def seed(cls, base: Fit | None = None) -> "Context":
        """(λ₀, id) — the seed with an empty patch file. The unit."""
        return cls(fit=dict(base or {}), retraction=[])


def mount(ctx: Context, row: Row) -> Context:
    """mount(p, p⁻) : (λ, ρ) ↦ ( p(λ), ρ ∘ p⁻ )"""
    return Context(fit=row.forward(ctx.fit), retraction=[row] + ctx.retraction)


def mount_all(ctx: Context, rows: Iterable[Row]) -> Context:
    for r in rows:
        ctx = mount(ctx, r)
    return ctx


def retire(ctx: Context) -> Context:
    """
    retire : (λ, ρ) ↦ ( ρ(λ), id )

    Note the order: `retraction` is built by prepending, so iterating it
    forwards applies inverses in REVERSE mount order. That is the twist in
    T2's product `(p₁∘p₂, p₂⁻∘p₁⁻)`, and it is why retirement unwinds in
    reverse dependency order. The algebra forces it; this code does not get a
    vote.
    """
    fit = ctx.fit
    for row in ctx.retraction:
        fit = row.backward(fit)
    return Context(fit=fit, retraction=[])


# ── T3, as a computation ────────────────────────────────────────────────────
@dataclass(frozen=True)
class Invertibility:
    ok: bool
    target: str
    reason: str
    difference: dict[str, tuple]

    def render(self) -> str:
        if self.ok:
            return f"{self.target}: p⁻(p(λ)) ≃ λ at this λ"
        d = "; ".join(f"{k}: {v[0]!r} → {v[1]!r}" for k, v in self.difference.items())
        return f"{self.target}: {self.reason}" + (f" — {d}" if d else "")


def check_invertibility(row: Row, fit: Fit) -> Invertibility:
    """
    T3's hypothesis, computed at the state where the row would be applied.

    This is the whole point of the pointwise formulation. A global inverse is a
    strong and usually unprovable claim; correctness *at this λ* is a
    two-line calculation, and it is exactly what the gate needs to decide
    whether mounting this row keeps the seed recoverable.
    """
    restored = row.backward(row.forward(fit))
    diff = difference(restored, fit)
    if not diff:
        return Invertibility(True, row.target, "verified at this state", {})

    # Name the failure precisely — a gate that says "invalid" teaches nothing.
    # `difference(restored, fit)` yields (what the inverse produced, what was
    # actually there). Getting these the right way round matters: the first
    # version of this diagnostic had them reversed and reported the exact
    # opposite of the truth. Found by running it.
    if row.target in diff:
        produced, actual = diff[row.target]
        if produced == "<absent>":
            reason = ("the inverse removed the target, but it held a prior value "
                      "— the inverse must restore that value, not delete the key")
        elif actual == "<absent>":
            reason = ("the inverse installed a value where the target was absent "
                      "— this row assumes a prior state the patch does not establish; "
                      "either the superseded row is missing, or the inverse should be null")
        else:
            reason = "the inverse does not restore the prior value at this state"
    else:
        reason = "applying and inverting this row disturbed an unrelated target"
    return Invertibility(False, row.target, reason, diff)


def check_all(rows: Iterable[Row], base: Fit | None = None) -> list[Invertibility]:
    """
    Check every row **at the state it would actually be applied in** — i.e.
    with all prior rows already mounted. Checking each row against the bare
    seed would be a different and weaker claim.
    """
    ctx = Context.seed(base)
    out = []
    for row in rows:
        out.append(check_invertibility(row, ctx.fit))
        ctx = mount(ctx, row)
    return out


# ── loading rows from a real patch file ─────────────────────────────────────
def rows_from_patch(patch: dict) -> list[Row]:
    return [
        Row(target=r["target"], value=r.get("value"),
            inverse=r.get("inverse"), id=r.get("id", ""))
        for r in patch.get("rows", [])
        if "target" in r
    ]


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print(__doc__)
        print("usage: python core/algebra.py <patch.json>")
        raise SystemExit(2)

    with open(sys.argv[1], encoding="utf-8") as fh:
        patch = json.load(fh)
    rows = rows_from_patch(patch)

    print(f"patch: {sys.argv[1]}   rows: {len(rows)}\n")
    results = check_all(rows)
    for r in results:
        print(f"  {'ok  ' if r.ok else 'FAIL'}  {r.render()}")

    ctx = mount_all(Context.seed(), rows)
    back = retire(ctx)
    recovered = equivalent(back.fit, {})
    print(f"\n  {'ok  ' if recovered else 'FAIL'}  retire(mount*(λ₀)) ≃ λ₀ — the seed is recoverable")
    bad = [r for r in results if not r.ok]
    raise SystemExit(1 if bad or not recovered else 0)
