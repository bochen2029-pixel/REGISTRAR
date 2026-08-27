# F-PATCH-DELTA · pre-registration, rubric v3 — the instrument catches up to the kit

**Written `2026-08-27`, before any v3 score is computed.** v2's verdict stands as recorded (FAILS, 0.28,
instrument-limited). v3 changes **the scorer only** — hold credit, the abstention guard, thresholds, arms,
corpus: all inherited from v2 unchanged.

**The honesty problem, named before the numbers:** v3 is designed after two candidates exist, by a session
that has seen their per-target grades. The guards against fitting-the-rubric-to-the-answer are: **(1)** both
changes below are *generic mechanisms* justified by defects already documented on the **v1** run (the
"scorer artifacts, not errors" note predates the v2 candidate); **(2)** v3 is applied **symmetrically to
every arm and every recorded candidate** — the floor is re-scored under the same rules, and the SHAPED band
still requires exceeding the same-rubric floor; **(3)** the changes are committed here before the first v3
number is printed, and the scorer prints its rubric version on every run.

## Change 1 · grade against the stated grain

`truth_numbers()` read only keys prefixed `value` — so a candidate that filed the key's own stored
`p90_minutes` **exactly** was marked 21% out against the p75. The kit's doctrine is *p75 or higher, p90
where the figure feeds a latest safe start*. **v3: a numeric answer matches if within TOL of any stored
percentile at or above the doctrine floor — keys `value*` or `p90*`. `median` stays excluded**: it is below
the doctrine floor, and crediting it would reward the exact optimism the divergence gate refuses.

## Change 2 · structural values are matched by leaves, not by flat key names

The flat key-match scored a *richer, correct* answer as "wrong — no key matches" (three per-hospital OR
windows with both bounds, which is what fixture 14 teaches, against a single-hospital truth dict). **v3:
flatten both dicts to leaves; a truth leaf matches if a candidate leaf agrees (numbers within TOL, strings
by normalised containment); ≥ 80% of truth leaves matched → correct (+2), ≥ 40% → shaped (+1), else
wrong (0).** Deterministic, generic, and it can still refuse: a wrong bound is an unmatched leaf.

## What a v3 verdict attaches to

Only the **v2-run candidate** (`fairbank.v2.patch.yml`) carries a verdict — it is the only protocol-valid
arm-② artifact. The v1 candidate and the floor are re-scored as **calibration**. Verdict bands are v2's,
including `answered ≥ 8` and *SHAPED requires exceeding the same-rubric floor*.

---

## v3.1 · the strict-leaf correction — `2026-08-27`, frozen before any v3.1 score is computed

QC round two measured a defect in change 2's matcher: `_leaf_match` used both-ways substring containment,
so a candidate stating the CONTRADICTION of a truth leaf scored as matching it (`not house_coordinator`
matched `house_coordinator`; 4 of run A's 16 matched leaves and 2 of run B's 13 matched by containment only).
The first QC's remediation had ordered exactly this removed from the flat matcher; v3 propagated it into the
leaf matcher instead.

**v3.1 changes exactly one thing: string leaves match by exact normalized equality (casefold, strip,
collapse inner whitespace) — never by containment.** Numeric leaves are unchanged (TOL). Everything else —
hold credit, abstention guard, thresholds, floors, grain-aware numerics — is inherited from v3 untouched.

**Per the v2→v3 precedent: recorded runs are re-scored mechanically under v3.1 and published beside their
v3 numbers; the v3.1 column is the operative one, the v3 column is history.** The scorer records rubric,
key file, and key digest in every result so this class of ambiguity cannot recur unrecorded.

*Frozen before computation; the QC's partial counts (which leaves matched by containment) were known when
this was written — the totals were not.*
