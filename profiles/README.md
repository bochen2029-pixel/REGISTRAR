# profiles/

**One clone. Two artifacts. The profile decides what mounts.**

REGISTRAR is a single repository containing the seed, the map, the blueprint and the unpacking process. That
is deliberate — `git clone` is the entire adoption story, and splitting the forge into a second repository
would mean an OPO has to find and trust two things instead of one.

But **an OPO running a donor record should not be running a document chunker in production.** So the
repository ships two profiles, and they are not equal:

| Profile | What it is | Who runs it | For how long |
|---|---|---|---|
| **`edr`** | the deployed record. The seed, the floor, the gates, the tape. | coordinators, at 3 a.m. | decades |
| **`forge`** | the machinery that completes the seed into one site's shape | that site's IT team | the completion, then idle |

**`edr` is the default**, and it is a strict subset. A site that never touches the forge still gets a
complete, useful record system — that property is `SPEC.md` §1, and the profile mechanism enforces it rather
than asking anyone to remember it.

---

## The two axes, and they are orthogonal

Confusing these is easy and the distinction matters:

- **The profile says WHAT MOUNTS.** `edr` or `forge`. A property of the deployment.
- **`registrar.state` says WHETHER ANYONE IS HOME.** `off` | `shadow` | `live`. A property of the moment,
  and a file only the operator writes.

Every combination is legal and means something:

| | `off` | `shadow` | `live` |
|---|---|---|---|
| **`edr`** | the record, computed on demand. **Today's repository.** | the closure renders what it *would* have surfaced | it surfaces to the board |
| **`forge`** | turn-based completion — a harness, prompted by a person | the resident drafts rows and renders them beside what a human did | the resident proposes into the queue |

**`edr` + `off` is the default and it is a real product.** Everything above it is optional.

---

## Why the forge's tools are mounted, not vendored

The completion tooling — chunking a 784 KB policy corpus, scanning for PHI, checking a citation byte-exact —
is real machinery that exists elsewhere in working form. **REGISTRAR does not vendor it.**

Three reasons, and the third is the important one:

1. **A vendored copy is a fork.** It drifts, it inherits the source's environment coupling, and it makes this
   repository responsible for maintaining a document splitter forever.
2. **Licence.** A plugin mounted at completion time is not redistributed by this repository. Only the
   interface ships.
3. **Your tools are as good as ours.** A site with its own document pipeline should mount that instead. The
   forge declares *what it needs done*; it does not dictate what does it. **That is the completability
   argument applied to the tooling itself** — the same reason the seed does not dictate the fit.

See [`../forge/plugins.yml`](../forge/plugins.yml) for the declared capabilities and
[`../forge/PLUGINS.md`](../forge/PLUGINS.md) for how to mount your own.

---

## Reading a profile

```bash
python core/profile.py                  # which profile is active, and what it mounts
python core/profile.py --profile forge  # what the forge would mount
python core/profile.py --check          # is the edr profile still a strict subset?
```

**That last check is the load-bearing one.** If forge-only machinery ever appears in the `edr` profile, a
site deploying a record system inherits completion tooling it did not ask for and cannot audit. Conformance
runs it.
