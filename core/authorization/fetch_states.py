#!/usr/bin/env python3
"""
REGISTRAR · fan out and fetch every state's anatomical gift act
─────────────────────────────────────────────────────────────────────────────
Ten concurrent workers, staggered waves, and — the part that matters —
**every download validated by CONTENT, never by status code.**

WHY THAT IS THE WHOLE POINT

Texas taught this the expensive way. `curl` returned HTTP 200 and 250,874
bytes for the statute URL. It returned 200 and the identical 250,874 bytes for
a PDF path, a ZIP path, and a nonsense path: the site is a JavaScript app with
catch-all routing, and the statute text is never in the shell it serves.

A naive fetch loop would have reported **50/50 success** and written fifty
copies of Angular boilerplate to disk. Downstream, `tools/cite.py` would have
caught it — no quote would byte-match — but only after somebody spent a day
writing rows against nothing.

So a fetch here is successful only when the bytes contain statutory language.
Anything else is a MISS, and a MISS names the reason.

    python core/authorization/fetch_states.py --dry-run     # show the plan
    python core/authorization/fetch_states.py --states TX,CA,NY
    python core/authorization/fetch_states.py --all --wave 10

Nothing here writes a citation, a row, or a provenance entry. It downloads and
it validates. **A human and a lawyer do the rest** — see PROCEDURE.md.

Zero dependencies beyond the standard library.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# Other people run this on other people's consoles. Never assume UTF-8 stdout.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "corpus", "states")
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state_sources.json")

UA = "REGISTRAR/0.1 (open-source EDR; contact via the repository)"

# Language that must be present for the bytes to be a statute rather than a
# navigation shell. Deliberately domain-specific: "anatomical gift" is the
# term of art every UAGA-derived act uses in its title and body.
MUST_CONTAIN = ("anatomical gift",)
CORROBORATING = ("decedent", "donor", "priority", "spouse")

# Shapes that mean "you got an application, not a document".
SPA_MARKERS = ("data-beasties", "<app-root", "ng-version", "__NEXT_DATA__",
               "window.__INITIAL_STATE__", "Loading…", "Please enable JavaScript")

MIN_BYTES = 4000


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(script|style|nav|header|footer).*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    import html as _h
    s = _h.unescape(s)
    return re.sub(r"[ \t]+", " ", s)


def classify(raw: bytes, url: str) -> tuple[str, str, str]:
    """
    Return (verdict, reason, text). Verdict is OK | MISS.

    This is the function the whole script exists for. It answers "did we
    actually get the law?" and nothing about it is inferable from the HTTP
    layer.
    """
    if len(raw) < MIN_BYTES:
        return "MISS", f"only {len(raw)} bytes — too small to be a chapter", ""

    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    s = raw.decode(enc, errors="replace")

    if raw[:5] == b"%PDF-":
        return "MISS", "PDF — extract text first, then re-run validation on the text", ""

    text = strip_html(s) if "<" in s[:2000] else s
    low = text.lower()

    if not any(k in low for k in MUST_CONTAIN):
        for m in SPA_MARKERS:
            if m.lower() in s.lower():
                return ("MISS",
                        f"application shell, not a statute (saw {m!r}) — "
                        f"needs a headless browser; see PROCEDURE.md", "")
        return "MISS", "no 'anatomical gift' language — wrong page or JS-rendered", ""

    hits = sum(1 for k in CORROBORATING if k in low)
    if hits < 2:
        return "MISS", f"matched 'anatomical gift' but only {hits}/4 corroborating terms — verify by hand", text

    return "OK", f"{len(text):,} chars, {hits}/4 corroborating terms", text


def fetch_one(entry: dict, timeout: int = 45) -> dict:
    state, url = entry["state"], entry.get("url") or ""
    started = time.time()
    if not url:
        return {"state": state, "verdict": "SKIP", "reason": "no URL in the index — find it and add it", "secs": 0}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw, code = r.read(), r.getcode()
    except urllib.error.HTTPError as e:
        return {"state": state, "verdict": "MISS", "reason": f"HTTP {e.code}", "secs": round(time.time() - started, 1)}
    except Exception as e:
        return {"state": state, "verdict": "MISS", "reason": f"{type(e).__name__}: {e}",
                "secs": round(time.time() - started, 1)}

    verdict, reason, text = classify(raw, url)
    saved = ""
    if verdict == "OK":
        os.makedirs(OUT, exist_ok=True)
        saved = os.path.join(OUT, f"{state.lower()}-{entry.get('slug', 'uaga')}.txt")
        with open(saved, "w", encoding="utf-8") as fh:
            fh.write(text)
    return {"state": state, "verdict": verdict, "reason": f"HTTP {code} | {reason}",
            "saved": os.path.relpath(saved, ROOT) if saved else "",
            "secs": round(time.time() - started, 1)}


def load_index() -> list[dict]:
    if not os.path.exists(INDEX):
        print(f"no index at {INDEX}", file=sys.stderr)
        print("Create it: a list of {state, url, slug}. See state_sources.json.", file=sys.stderr)
        raise SystemExit(2)
    with open(INDEX, encoding="utf-8") as fh:
        return json.load(fh)["states"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--states", help="comma-separated postal codes")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--wave", type=int, default=10, help="concurrent workers per wave (default 10)")
    ap.add_argument("--pause", type=float, default=3.0, help="seconds between waves (default 3)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    entries = load_index()
    if a.states:
        want = {s.strip().upper() for s in a.states.split(",")}
        entries = [e for e in entries if e["state"].upper() in want]
    elif not a.all:
        ap.error("pass --states TX,CA or --all")

    have_url = [e for e in entries if e.get("url")]
    print(f"{len(entries)} jurisdictions · {len(have_url)} with a URL · "
          f"waves of {a.wave}, {a.pause}s between\n")

    if a.dry_run:
        for e in entries:
            print(f"  {e['state']:<4} {e.get('url') or '(no URL - needs finding)'}")
        return 0

    results: list[dict] = []
    waves = [entries[i:i + a.wave] for i in range(0, len(entries), a.wave)]
    for n, wave in enumerate(waves, 1):
        print(f"-- wave {n}/{len(waves)} --")
        with cf.ThreadPoolExecutor(max_workers=a.wave) as pool:
            for r in pool.map(fetch_one, wave):
                results.append(r)
                mark = {"OK": "ok  ", "MISS": "MISS", "SKIP": "skip"}[r["verdict"]]
                print(f"  {mark}  {r['state']:<4} {r['secs']:>5}s  {r['reason']}")
        if n < len(waves):
            time.sleep(a.pause)   # be a good citizen; these are public servers

    ok = [r for r in results if r["verdict"] == "OK"]
    miss = [r for r in results if r["verdict"] == "MISS"]
    skip = [r for r in results if r["verdict"] == "SKIP"]

    print(f"\n{len(ok)} retrieved · {len(miss)} missed · {len(skip)} skipped")
    if miss:
        print("\nMISSES — each needs a human or a headless browser:")
        for r in miss:
            print(f"  {r['state']:<4} {r['reason']}")

    report = os.path.join(OUT, "_fetch_report.json")
    os.makedirs(OUT, exist_ok=True)
    with open(report, "w", encoding="utf-8") as fh:
        json.dump({"results": results}, fh, indent=2)
    print(f"\nreport: {os.path.relpath(report, ROOT)}")

    print("\nWHAT THIS DID NOT DO: it did not write a citation, a row, or a")
    print("provenance entry, and a retrieved file is not a verified one.")
    print("Read PROCEDURE.md. Then a lawyer reads the row.")
    return 0 if not miss else 1


if __name__ == "__main__":
    raise SystemExit(main())
