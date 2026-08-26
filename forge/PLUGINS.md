# Mounting a capability

**The forge declares what it needs done. It does not dictate what does it.**

`plugins.yml` lists capabilities — chunk, phi_scan, search, fetch, render. Every one of them is currently
**unbound**, and that is the honest state: this repository vendors no tools, and the contract ships before
any binding does.

**If you have a document pipeline, a PHI scanner, or a search index already — mount those.** That is the
point. A site's own tools are usually better fitted to a site's own material, and the same argument that
says the seed should not dictate the fit says the forge should not dictate its instruments.

---

## Why nothing is vendored

Three reasons, and the third is the one that matters:

1. **A vendored copy is a fork.** It drifts from its source, inherits that source's environment coupling —
   hardcoded paths, one operating system, a key file — and makes this repository responsible for maintaining
   a document splitter forever.
2. **Licence.** A plugin mounted at completion time is not redistributed by an MIT repository. Only the
   interface ships. **A binding with no licence cannot be mounted into this tree** — that check is in the
   contract, not in anyone's memory.
3. **Yours may be better.** The forge runs once, in your building, on your material.

---

## What a binding looks like

```yaml
- id: chunk
  binding:
    version: "1.0"
    source:  /opt/ourteam/docsplit
    pin:     sha256:a1b2c3…            # a binding without a pin is not mounted
    entry:   "python /opt/ourteam/docsplit/split.py"
    licence: MIT
```

Then the contract's rules apply, and some of them **refuse the mount** rather than warn:

- **`chunk` must write where the caller says.** A chunker that writes a `.chunks/` directory beside its
  source creates a second, uncontrolled copy of PHI-bearing material in a location nobody chose. This is
  the single most likely way a well-meaning tool leaks.
- **`phi_scan` must be described as a floor**, never a guarantee. A scanner presented as a guarantee is
  worse than no scanner, because it retires the human caution that was doing the actual work.
- **`fetch` must validate content, never status codes.** Learned expensively — see
  [`../core/authorization/PROCEDURE.md`](../core/authorization/PROCEDURE.md).

---

## What no binding may do

From [`../profiles/forge.yml`](../profiles/forge.yml), and these are rules rather than judgment calls so
that they do not have to be re-litigated per plugin:

- **No live audio or video lane at a deployed site.** A room at an OPO is a room where family authorization
  conversations happen — the most protected exchange in this domain, and the one thing `SPEC.md` §8
  prohibition 3 forbids this system from participating in, scripting, or observing.
- **No egress of site material.** The local leg of the two-model split is the entire compliance posture.
- **No writes outside the fit.** The forge authors one file — the site's patch — and proposes everything
  else. A binding inherits that bound; it does not widen it.

---

## The part that is the point

**The forge is a plugin host, so a wall it hits is not a dead end.**

When the completion meets something it cannot read — a lab format nothing parses, an SOP structure that
defeats the chunker — it can author the binding, shadow-run it against your own material, and **propose**
it. One yes mounts it hash-pinned, with an expiry. Drift demotes it. Retirement unwinds it through the same
disposer that made mounting safe.

**That is the same contract as a patch row, applied to capability instead of configuration** — and it is
affordable here in a way it is not one layer down. A forge plugin that is wrong wastes an afternoon. An EDR
plugin that is wrong touches a case.

Proposals land in `plugins.yml` under `proposed:`, and **a human signs**. Nothing mounts unsigned, here or
anywhere else in this repository.
