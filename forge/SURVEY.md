# What was surveyed, and what was decided

**`2026-08-26` · Fork A.** Seven candidate tools examined by read-only scouts before any code moved. This is
the provenance record the plugin contract requires: *adapt-not-copy has to be shown, not asserted.*

**Headline: not one of the seven can be vendored today, and two of them should not be bound even if they
could.** Both facts are useful, and the second is the more interesting one.

---

## The licence wall

**Every tool surveyed is unlicensed.** Not "ambiguously licensed" — no `LICENSE` file, no SPDX header, no
copyright line:

| Tool | Licence | Note |
|---|---|---|
| `chunker` | **none** | no git history, no author metadata |
| `Everything` | **none** | and bundles `es.exe`, **third-party proprietary freeware** |
| `everywhen` | **none** | vendored deps *are* licensed; the tool's own code is not |
| `everywhere` | **none** | `_run_state/ROADMAP.md` says *"Package: MIT license"* — an intention, not a grant |
| `KEEL` | **declared, no file** | `Cargo.toml: license = "MIT"` and **no LICENSE file anywhere in history** |

**KEEL is the instructive case.** A Cargo manifest field is *metadata*, not a grant — there is no copyright
line and no permission text to carry forward. The contract in `plugins.yml` refuses a mount without SPDX, and
it is right to: an MIT repository must be able to account for every line it ships.

**Most of these are the operator's own work and relicensable by fiat.** That is a paperwork problem, not a
third-party one — **but it has to happen before a fold, not after.** `Everything` is the exception and stays
excluded regardless: a bundled proprietary binary cannot travel.

---

## `chunk` — clean-room, and the licence is not the main reason

`chunker.py` is 642 lines, single file, stdlib at import, network-free, argument-driven. On the merits it is
good work and roughly 80% would drop straight in.

**It also violates the refusing rule, by default.** With `--out` omitted it writes
`<source_dir>/<basename>.chunks/` — **the second uncontrolled copy beside the source, which is the exact
failure `caller_specified_output` exists to prevent.** `--out` defaults to `None`, so this is the *default
path*, not an edge case. And the manifest embeds `os.path.abspath(source)`, leaking the source location into
the output.

Two further findings: **no tests exist**, while the README claims *"verified: zero data loss"* — an
unsubstantiated claim of the kind this repository refuses everywhere else. And the `.docx` extractor drops
all tables, which matters for SOP binders.

**So the rewrite was required on behaviour, and the licence merely settles it.** What was taken is the
*design*, described by a scout rather than copied:

- **boundary hierarchy, highest-that-fits** — heading → page marker → paragraph → sentence → line → word,
  with PDF pages normalised to `## Page N` so page breaks fall out of the same machinery
- **reserve headroom before packing** — the non-obvious arithmetic that makes a *rendered* chunk actually
  fit its budget
- **recap overlap at block granularity**, with a degenerate-case tail when one block exceeds the overlap
- **the orientation triple** — a `section:` breadcrumb, a `next:` pointer, plus `INDEX.md` and a manifest

---

## `search` — **not bound, and that is the finding**

Three tools, three different reasons, and the third is the one worth recording.

**`Everything`** searches *filenames*, not contents. Its own README: *"Everything is the locator: it matches
names/paths, not file contents."* It cannot answer *which passage establishes this claim*.

**`everywhen`** indexes **Claude Code session transcripts** — `~/.claude/projects/**/*.jsonl`, hardcoded,
with the corpus root baked in and **no path arguments at all**. It is a session-log concordance. Pointing it
at a regulatory corpus is not possible without a rewrite.

**`everywhere`** is the interesting one: right modality, right interface shape (paths positional, hits as
`path + line + byte_offset + column`), right architecture (stateless — *no index, no daemon*, which for a
**pinned** corpus is correct, because an index adds a staleness failure mode to a regulatory locator).

**And it is the wrong choice anyway, on its own published numbers.** At ten patterns it runs at **0.07×
ripgrep** — fourteen times slower. Its own findings say so: *"The crossover is ~50–100k+ patterns on this
hardware… Below that, use ripgrep."* Filling a locator is one pattern, occasionally a handful. It would also
cost a CUDA toolkit, Visual Studio, an NVIDIA card, and a Windows-only lock.

> **Verdict: `search` stays unbound, and `grep` remains the legitimate binding the contract already names.**
> `path + offset + span` is about thirty lines of stdlib `re` over `pathlib`, with no build step and no
> platform lock.

**One thing was taken:** `everywhere`'s **output contract** — `{path, line_number, byte_offset, column,
text}` with rg-compatible exit codes `0` hit / `1` none / `2` error. A well-designed machine-readable hit
record costs nothing to imitate.

*If a real need ever appears for sweeping 50,000+ literals at once — a term-list sweep, not a claim locator —
`everywhere` is genuinely the right tool for that and this note should be revisited.*

---

## `phi_scan` — KEEL supplies the vocabulary, not the code

KEEL's detection is **five regexes and a Luhn check**: email, SSN, `sk-` keys, `AKIA` keys, credit cards.
**No MRN, no dates bound to a case, no donor identifier, no institution-plus-event, no combination logic.**
Against the PHI list this domain needs, it detects almost nothing. Its rung-3 path is a Rust ONNX harness for
a **1.62 GB model** — irrelevant to a zero-dependency Python tree.

**The framing, though, is better than the usual formulation, because it is structural rather than asserted:**

| Term | What it buys |
|---|---|
| **rung** | an ordinal naming *epistemic type*, not strength |
| **the oracle** | *"a non-model assertion that PII is present"* — the deterministic floor |
| **"a verification pass, not an oracle"** | the exact phrase for anything probabilistic |
| **additive-only — "the union only grows"** | **makes the floor a property of the type, not a promise**: a higher rung can never unmask a lower one |
| **"never sole"** | a one-line refusal of the guarantee framing |
| **leak-uncertain ⇒ treat as sovereign** | the fail direction, stated as a rule |
| **gate vs mask** | two jobs with different consequences. `phi_scan` is a *mask*; refusing the frontier route is a *gate*. **Do not merge them.** |
| **labels, never values** | an audit record carries the class, never the PHI |
| **agent-frozen** | the marker list is operator-authored; the tool supplies mechanism, never policy |
| **pre-registered thresholds** | recall uplift, FP ceiling and latency written *before* measuring |

### And one thing to fix rather than import

**KEEL conflates "clean" with "not detected."** Empty findings is the only representation of *nothing found* —
and when its rung-3 classifier fails to load, it **silently returns zero spans**. *A degraded scanner and a
genuinely clean text produce byte-identical output*, with only a line on stderr to tell them apart. Its own
test names the empty case `clean_text_is_unchanged`.

> **That is precisely the failure this repository's three-state discipline exists to prevent**, and it is the
> same shape as a stalled resident being indistinguishable from a quiet one (`percepts/switch.py`).
>
> **`phi_scan` must therefore never return `CLEAN`. It returns `NONE_DETECTED`, and it records which rungs
> actually ran and whether any degraded.** A scan whose scanner did not run is not a scan.

---

## Decisions

| Capability | Decision |
|---|---|
| **`chunk`** | **build clean-room.** Design adapted from a description; mandatory `--out`; no source path in the manifest; tests, which the original lacked. |
| **`phi_scan`** | **build clean-room**, using KEEL's vocabulary and fixing its one defect — three-state verdict, rungs recorded, additive-only union. |
| **`search`** | **UNBOUND, deliberately.** grep is the honest binding. `everywhere` is 14× slower at this pattern count and costs a CUDA toolchain. |
| **`fetch` · `render`** | not yet surveyed; optional; lower priority than the two required capabilities. |
| `Everything` · `everywhen` | **excluded.** Wrong modality and wrong corpus respectively; one bundles a proprietary binary. |
| `cutter` | **not relevant** — see below. |
| `Intercom` | **not relevant** — see below. |

---

## `cutter` — a category error, and the distinction is worth keeping

Proposed as a possible `chunk` binding. **It is the opposite of one.**

| | `chunk` | `cutter` |
|---|---|---|
| output | 1 document → N pieces | 1 file → 1 **shorter** file |
| information | lossless in aggregate | **lossy by design — the evicted span is destroyed** |
| boundary | semantic | protocol-structural (never orphan a `tool_use`/`tool_result` pair) |
| input | any document | **Claude Code session transcripts only** |

It is a lossy oldest-first evictor of an append-only conversation log — a context-window trimmer, hardwired
to `parentUuid` / `tool_use` / `usage` record shapes. **Binding it to `chunk` would mean a chunker that
deletes forty per cent of a medical record**, and its own README draws the same line: *"the fast dumb
cutter."*

Unlicensed, Win32-only (`wmain`, `MoveFileExW`, mmap, BCrypt), **in-place with no backup by design**, and
`_backups/` currently holds three real transcripts.

**Two things it teaches, both worth keeping:**

**A byte percentage is a meaningless proxy for a token target** when the corpus mixes byte-huge/token-cheap
with byte-cheap/token-dense content — *"tiktoken counts a base64 image as millions of tokens."* That applies
directly to sizing `chunk` over records that mix scanned attachments with dense coded text.

**And a cautionary one.** `cutter.cpp:486` prints `" - VERIFIED replace, chain re-linked"` **unconditionally**
— no read-back, no hash comparison, no re-parse. The word appears exactly once in the source, inside that
`fprintf`. **A tool that prints VERIFIED without verifying is the precise failure this repository's
three-state discipline exists to prevent**, and it is a useful thing to have seen in the wild.

*If the capability were ever wanted it is not `chunk` — it would be `evict`, and a records system does not
evict. Records are retained.*

---

## `Intercom` — well built, and the answer to a question this domain does not ask

A stdlib-only SQLite message bus with cursors, barrier-synchronised rounds, CAS leases, handoff capsules and
lane identity. Genuinely good, and it has run at scale. It also carries an explicit *"License TBD"* and
hardcodes `C:\Intercom` — **and its schema seeds four other estate tools by absolute path into every database
it creates.**

**But the licence is not the reason.** Intercom's premise is *many concurrent autonomous agents that must
coordinate without a human relaying messages.* **One OPO's IT team filling twenty variation points once has
no concurrency, no barrier problem, no contention a git merge does not already solve, and no liveness
problem** — humans do not die mid-turn and need a takeover capsule.

Two further reasons, and the second matters more than the first:

- **It fits none of the five capabilities.** Declaring a `bus` capability to accommodate it would be *adding
  a capability to justify a tool*, which is backwards.
- **It would introduce a new PHI sink.** `messages.body` is free text in an unencrypted SQLite file with WAL
  sidecars. **That is a HIPAA surface added to solve a problem this deployment does not have** — and it would
  then need scanning, retention, audit and destruction under policy.

**One pattern worth borrowing later:** its wake-adapter contract fails **open** — *"may never block, deny, or
error-loop a session."* Good discipline, independent of the rest.

---

**Nothing was copied. No tool's bytes entered this repository.** What travelled is design described in prose
and vocabulary named in a canon — which is what *take the catalogue, not the file* means, and it is also the
only lawful route while the licence wall stands.
