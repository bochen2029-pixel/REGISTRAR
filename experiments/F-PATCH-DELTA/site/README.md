# Fairbank Donor Network — site material

**FICTIONAL. Fairbank Donor Network does not exist.** Every hospital identifier, contract, SOP, ticket and
case event here is invented. **Zero PHI, and no material from any real organ procurement organisation.**

This is the arm-② corpus for `F-PATCH-DELTA`. It exists so a harness can be asked to author a candidate fit
from site material, and be graded against a delta extracted from that material.

---

## What is here

```
ops/            standard operating procedures — what is WRITTEN
contracts/      the reference lab and transport agreements — what was PROMISED
rota/           the call schedule as actually staffed
interfaces/     the integration inventory
tape/           raw case events — what HAPPENED
servicedesk/    ticket history
```

**The tape is raw events, not summary statistics.** No file here says *"the p75 was nine minutes."* It says
what happened, one row per case, and the figure a fit needs must be **computed**. That is the whole point:
a corpus that states its answers has handed over the answer key.

---

## For a harness reading this

You have been asked to author `fairbank.patch.yml` against the seed's declared variation points. Read
[`../../../elicit/questions.yml`](../../../elicit/questions.yml) for what to look for, and
[`../../../elicit/method.md`](../../../elicit/method.md) for how.

**Three things worth knowing before you start, because they are true of real sites too:**

1. **The binder and the behaviour do not always agree.** Where they disagree, `elicit/method.md` is explicit
   about which one a fit encodes. That is a judgment you have to make and defend in your evidence.
2. **Some questions have no answer here.** The material is what a site actually has, not a complete set. **A
   target you cannot ground is a target you decline**, with a hold naming what you searched and why you
   declined. Inventing a plausible value is the worst available outcome.
3. **Numbers are computed, not quoted.** If you write a figure, your evidence must point at the rows it
   came from and name the method.
