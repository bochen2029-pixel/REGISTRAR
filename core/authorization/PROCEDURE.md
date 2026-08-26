# Filling your state's authorization row

**Addressed to the AI harness doing this, and to the human who will sign it.**

You are adding one row to [`jurisdiction.yml`](jurisdiction.yml): who may authorize donation in your state,
cited to your state's statute. It takes about an hour. **It is the one thing this repository actively wants
pushed back**, because your row is worth little to you alone and a great deal to the other fifty-four.

Read [the Texas row](jurisdiction.yml) first. It is the shape you are copying — **not the content.**

---

## Before anything else: the failure that looks exactly like success

**Do not trust an HTTP 200.**

Texas was retrieved on the second attempt because the first one *appeared to work*. `curl` returned **200
OK** and **250,874 bytes** for the statute URL. It also returned 200 and the identical 250,874 bytes for
every other path tried — a PDF path, a ZIP path, a nonsense path. `statutes.capitol.texas.gov` is a
JavaScript single-page application with catch-all routing: **every URL serves the same application shell,
and the statute text is never in it.**

A fetch loop over fifty states would have reported **50/50 success** and downloaded fifty copies of Angular
boilerplate.

So the first rule of this procedure:

> **Validate content, not status codes.** A download is successful when the bytes contain the statutory
> text you came for. Nothing else counts — not the code, not the size, not the content-type.

`fetch_states.py` in this directory enforces that. If you are working by hand, enforce it yourself:

```bash
grep -ci 'anatomical gift' downloaded.html    # 0 means you have an app shell, not a statute
```

**If a state's site is a SPA**, use a headless browser instead. This repository was built with
`kernel.sh` (`python kernel.py new --local --url <URL>` then `text <session>`), but any renderer works.

---

## The steps

### 1 · Find your statute

Most states adopted the **Revised Uniform Anatomical Gift Act (2006)**. Some are still on the **1987** or
**1968** UAGA, and a few have non-uniform acts. **Do not assume.** Search your state code for
*"anatomical gift"* and find the chapter.

Two sections matter:

| You need | Typically titled | In Texas |
|---|---|---|
| **Who may authorize** — the ordered class list | *"Who may make an anatomical gift of a decedent's body or part"* | § 692A.009(a) |
| **Whether first-person authorization binds** | *"Preclusive effect of anatomical gift…"* | § 692A.008(a) |

**Section numbers do not transfer between states.** Texas puts the preclusive-effect rule at `.008` and the
priority list at `.009`; base RUAGA numbers them differently, and your state may too. Find them by *title*,
never by number.

### 2 · Pin the source

```bash
python tools/cite.py --add <state>-<code>-<chapter> corpus/<file>.txt \
  --url "<the URL you actually used>" --accessed YYYY-MM-DD
```

Pin the **extracted text you searched**, not just a PDF or HTML original — the quote is checked against the
bytes it was taken from.

**Capture the currency statement.** Texas's site says *"current through the 89th 2nd Called Legislative
Session, 2025."* Yours will say something equivalent. A statute citation is a claim about a document **at a
date**, and without that line the claim has no date.

### 3 · Write the row

Copy the Texas row's structure. Fill:

- `state`, `name`, `act` (which UAGA vintage), `adopted` (the session law that enacted it), `code`
- `source_id` — matching what you pinned
- `currency` — the statement from step 2
- `acquisition` — **how you got it**, especially if curl failed. The next contributor benefits.
- `first_person` — `binding: true/false`, with locator and verbatim quote
- `surrogate_priority` — locator, and the classes **in statutory order**
- `within_class_rule` — what happens when a class disagrees. Texas: majority of reasonably available members.
- `counsel_reviewed: false`

### 4 · Verify

```bash
python tools/cite.py --check
python conformance/run.py
```

Every quote must byte-match. **A quote that does not match its pinned source is a fabrication regardless of
how plausible it reads**, and the gate will refuse it. That is the gate doing its job, not an obstacle.

### 5 · Have a lawyer read it

`counsel_reviewed: false` is **legal and expected** on a new row. A cited, unreviewed row is far better than
an empty cell. But this is the one part of the seed where a byte-exact citation is **necessary and not
sufficient** — a correctly quoted statute can still be misread, and the consequence here is not a bad metric.

**No automated check can set this field.** It is a human act and the gate deliberately cannot perform it.

---

## Rules that are not negotiable

**Never infer a state from its neighbour.** Adjacent states diverge in exactly the ways that matter. Texas
lists *hospital administrator* and *any other person having authority to dispose of the body* as classes
(10) and (11); many states do not. Copying that list one state over would authorise people who are not
authorised.

**Never fill a field you could not cite.** If the statute is ambiguous, say so in `note` and leave the field
out. An absent field is honest; a guessed one is a wrong answer wearing the formatting of a right one.

**Never cite a summary.** Not a law-firm client alert, not a state health department FAQ, not a
secondary table, not another OPO's row. The statute itself or nothing.

**Watch for superseded text.** Codified law can contain expired provisions that are still printed —
this project has already been bitten by one (see `PROVENANCE.md`). `tools/cite.py` warns when it sees sunset
language near your quote; a human closes that warning by recording *why*, never by silencing it.

---

## What you are not being asked for

You are **not** being asked to decide who may authorize donation. That is your legislature's work, already
done. You are being asked to **cite** it.

And this row is **not** part of your site patch. It does not go in `<site>.patch.yml`, it is not private to
you, and it does not describe your operation. It goes upstream, into the shared seed, because the law is the
same for everyone operating in your state — including the OPO next door whose service area crosses into it.
