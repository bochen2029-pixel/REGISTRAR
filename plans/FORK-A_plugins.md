# FORK A · the sub-repo fold and the plugins

**Created `2026-08-26` · branch point `9a1a5f7` · read [`../FORKS.md`](../FORKS.md) first, it is binding**

---

## In one breath

Bring the estate's working tools into this repository as **forge capabilities**, and mount the two that
matter most **into the harness** so a model discovers them rather than being told about them.

---

## THE CONSTRAINT THAT WILL BITE YOU FIRST

> **`deepseek-harness-master/` is read-only. Never write inside it.**

You have been asked to make things into "dsh plugins," and the obvious move is
`deepseek-harness-master/packages/<yours>`. **Do not.** That tree is pinned — `dsh-v0.1.1-rc.2`,
**7,895/7,895 files byte-identical to upstream**, verified file-for-file. One added file breaks the pin and
converts a composition into a fork, inheriting permanent maintenance and destroying the upgrade path.

It is also the kernel's own thesis: *extend by mounting beside, never by forking.* Precedent in the estate —
`@bo/dsh-hop0` was built out-of-tree against the newest tree and passed its battery that way.

`python tools/pin_chassis.py --verify` must stay GREEN. `conformance/run.py` fails if any of it is staged.

---

## Why this fork exists

These are **forge-layer**, not EDR-layer, and losing that distinction is the main way this work goes wrong.

**A coordinator will never chunk a document.** `chunk` exists so a local open-weight model with a small
context can read a 784 KB policy corpus **while building the fit** — once, for a week, and then never again.
`profiles/edr.yml` must not mount any of it, and `python core/profile.py --check` fails if it does.

What makes them worth folding in at all: **`elicit/method.md` requires PHI-bearing site material to be read
only by a local model.** That is the binding constraint of the entire completion, and a small context facing
a 400-page SOP binder is the shape of it.

---

## What already exists to build on

| | |
|---|---|
| [`../forge/plugins.yml`](../forge/plugins.yml) | five capabilities declared — `chunk` · `phi_scan` · `search` · `fetch` · `render`. **Every `binding:` is `null`.** That is your work. |
| [`../forge/PLUGINS.md`](../forge/PLUGINS.md) | how a binding is declared and what refuses a mount |
| [`../profiles/forge.yml`](../profiles/forge.yml) | the three **refused** capabilities — rules, not judgment calls |
| [`../CHASSIS.pin.json`](../CHASSIS.pin.json) | what the harness is, and the two maturity facts kept apart |

---

## Two levels. Do them in this order.

### Level 1 · a bound capability

The tool lands under `forge/plugins/<id>/`, adapted to the contract, and `binding:` stops being `null`. The
forge invokes it as a subprocess. **Needs nothing from the chassis** — no install, no TypeScript, no plugin
API. This is what makes the capability usable at all.

```
forge/plugins/<id>/
  plugin.yml        version · source · sha256 · entry · SPDX licence
  LICENSE           REQUIRED — a binding without one cannot mount into an MIT tree
  PROVENANCE.md     where it came from, what changed, and WHY
  src/              the adapted tool
  test_<id>.py      its battery, INCLUDING the rules that refuse a mount
```

### Level 2 · a mounted dsh plugin

A thin package under `forge/dsh/registrar-<id>/` that registers the capability as a **tool in the harness's
registry.**

**This is the difference between a capability the harness *has* and one it can *discover*** — a loose file
is invisible unless a document tells the model to run it; a registered tool is native. That is the
enumeration-tax argument, one layer down.

> **Level 1 for all five. Level 2 for `chunk` and `phi_scan` only, at first.** Level 2 requires the chassis
> installed and its plugin API understood; spending that on `search` before proving it on `chunk` is effort
> in the wrong place.

---

## Order of work

1. **`chunk`** — required, the binding constraint of the whole completion, clearest contract.
2. **`phi_scan`** — required, and `AGENTS.md` §3 is currently **prose**. *A rule enforced only by asking an
   agent to follow it is not enforced* (law 9). This closes that gap.
3. **`search` · `fetch` · `render`** — optional. A site's own tools are legitimate bindings.
4. **Level 2** for the first two.

---

## Adapt. Do not copy.

Every independent survey of these tools reached the same conclusion: *take the catalogue, not the file* ·
*~60 lines rewritten* · *the transferable part is the pattern.*

**Copying is also exactly where the estate coupling travels** — hardcoded absolute paths, Windows-only
helpers, a live API key, and output directories written beside a source file.

### Three rules that refuse a mount, already in the contract

- **`chunk` writes only to a caller-specified path.** A chunker that writes `.chunks/` beside its source
  **silently creates a second, uncontrolled copy of PHI-bearing material** in a location nobody chose and
  nobody audits. This is the single most likely way a well-meaning tool leaks.
- **`phi_scan` is a high-recall FLOOR, never a guarantee.** A scanner presented as a guarantee is worse than
  no scanner, because it retires the human caution that was doing the actual work. It must be *specified,
  tested and described* as a floor.
- **`fetch` validates CONTENT, never status codes.** A statute site returned HTTP 200 and an identical
  250,874-byte application shell for **every** path tried, including nonsense ones. See
  [`../core/authorization/PROCEDURE.md`](../core/authorization/PROCEDURE.md).

---

## Licences are a hard prerequisite

**Of the estate tools surveyed, only `scriptorium` carries a LICENSE.** The contract requires SPDX and
refuses a mount without it.

Same author, so relicensable by fiat — **but it must happen before the fold, not after.** A tool arriving
here without a licence header cannot be bound, and pretending otherwise would put an MIT repository in the
position of shipping something it cannot account for.

**If you cannot resolve a licence, stop and say so.** Do not bind it anyway.

---

## Definition of done

- `chunk` and `phi_scan` bound at level 1, each with a LICENSE, a pin, a `PROVENANCE.md` and a passing battery
- `python adapters/conformance.py`-style checking extended to `forge/plugins/` — **a bound plugin that
  violates a refusing rule must FAIL, and there must be a test proving it does**
- `python core/profile.py --check` still GREEN — **no forge machinery in the `edr` profile**
- `python tools/pin_chassis.py --verify` still GREEN — **the chassis untouched**
- the full battery green before every push

---

## What not to do

- **Do not write inside the chassis.**
- **Do not vendor a tool without a licence.**
- **Do not bind without a sha256 pin.**
- **Do not let a plugin reach the network** unless its capability is `fetch` or `render`, and then only to a
  caller-supplied URL.
- **Do not add a live audio or video capability.** Refused by rule in `profiles/forge.yml` — *a room at an
  OPO is a room where family authorization conversations happen*, and that is prohibition 3.
- **Do not make `phi_scan` sound like a guarantee**, in code, in docs, or in a commit message.
