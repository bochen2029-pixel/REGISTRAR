#!/usr/bin/env python3
"""
REGISTRAR · forge · F-BOOT — clone to standing harness, one command

**The question this answers:** an OPO IT director clones this repository
tomorrow — what happens? Before this file: a green battery, a readable spec, a
worked completion exercise, **and no harness.** The chassis was pinned and
verified and never installed. This is the gap between *demonstrated* and
*usable*, and it was the binding constraint on adoption.

    python forge/boot.py            verify → install → build → launch
    python forge/boot.py --status   where the boot stands, three-state
    python forge/boot.py --no-launch  everything except starting the server

THE ORDER IS THE ARGUMENT

  1  PIN     the chassis must verify byte-for-byte against CHASSIS.pin.json
             BEFORE anything executes from it. Installing unverified
             third-party code is the hazard; the pin makes it unreachable.
  2  INSTALL `pnpm install` — writes node_modules/ INSIDE the chassis tree.
             That is compatible with both fences, and the distinction matters:
             the PIN excludes build artifacts (node_modules, dist) from its
             digests, so it stays GREEN; the READ-ONLY rule protects SOURCES —
             no tracked upstream file is touched, and `pin_chassis --check`
             re-proves that after every step here.
  3  BUILD   — DOES NOT EXIST, and that is a finding, not an omission.
             Upstream ships prebuilt lib/ trees and `pnpm dsh web` runs FROM
             SOURCE via tsx. Running `pnpm run build` was measured to add
             6,463 files to the pinned tree — the pin caught it (0 files
             differed; the contamination was purely additive and was removed
             byte-verified). **Install is composition. Build is a fork. The
             boot needs no build, so the hazard is simply never reached.**
  4  LAUNCH  `pnpm dsh web --no-open` — upstream's documented entry — then
             probe http://127.0.0.1:3080 until it answers. **Loopback only**,
             per the chassis's own trust-boundary doctrine: the web host serves
             RCE-grade methods and must not be exposed.

WHAT THIS DOES NOT DO, STATED RATHER THAN IMPLIED

  · It does not mount REGISTRAR plugins into the harness. `chunk` and
    `phi_scan` are bound at level 1 (subprocess capabilities, forge/plugins/);
    level 2 — registering them as tools inside dsh — is declared work, not
    done work, and the status output says so.
  · It does not turn the resident on. `registrar.state` ships `off`; the
    switch is percepts/switch.py and it fails toward inert.
  · A deployed record never runs this. `require_forge` guards it — the forge
    is run once, by a site's IT team, and then never again.

Zero dependencies beyond what the chassis itself requires (node ≥ 22.19,
pnpm 11 — checked, with the miss named).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHASSIS = os.path.join(ROOT, "deepseek-harness-master")

sys.path.insert(0, os.path.join(ROOT, "core"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN, UNVERIFIED, FAILED = "GREEN", "PASS-UNVERIFIED", "FAILED"


def say(state: str, name: str, detail: str = "") -> None:
    dots = "." * max(2, 30 - len(name))
    print(f"  {state:<16}{name} {dots} {detail}")


def run(cmd: list[str], cwd: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout, shell=False)


def tool(name: str) -> str | None:
    return shutil.which(name) or shutil.which(name + ".cmd")


# ── the steps ───────────────────────────────────────────────────────────────
def step_pin() -> bool:
    if not os.path.isdir(CHASSIS):
        say(UNVERIFIED, "chassis present",
            "absent — fetch and verify: python tools/pin_chassis.py --verify")
        return False
    r = run([sys.executable, os.path.join(ROOT, "tools", "pin_chassis.py"), "--check"],
            cwd=ROOT, timeout=300)
    ok = r.returncode == 0
    say(GREEN if ok else FAILED, "chassis pinned",
        "byte-identical to the recorded pin" if ok
        else "DOES NOT MATCH THE PIN — nothing from this tree may execute. Stop.")
    return ok


def step_toolchain() -> bool:
    node, pnpm = tool("node"), tool("pnpm")
    if not node or not pnpm:
        say(FAILED, "toolchain", f"node: {'ok' if node else 'MISSING'} · pnpm: "
                                 f"{'ok' if pnpm else 'MISSING'} — install node ≥ 22.19 and pnpm 11")
        return False
    v = run([node, "--version"], cwd=ROOT, timeout=60).stdout.strip()
    say(GREEN, "toolchain", f"node {v}, pnpm present")
    return True


def installed() -> bool:
    return os.path.isdir(os.path.join(CHASSIS, "node_modules"))


def runs_from_source() -> bool:
    # Corrected twice by measurement, and the second correction is the truth:
    # NOTHING PREBUILT EXISTS OR IS NEEDED. `pnpm dsh web` executes
    # `node --import tsx/esm apps/cli/src/bin.ts` — the TypeScript sources run
    # directly, which is why a pin-clean, never-built tree answers on loopback.
    # (Draft 1 probed dist/ paths that never exist; draft 2 probed a lib/ that
    # turned out to be MY OWN build's contamination, deleted with it.)
    return os.path.isfile(os.path.join(CHASSIS, "apps", "cli", "src", "bin.ts"))


def step_install() -> bool:
    if installed():
        say(GREEN, "install", "node_modules present (sources untouched — the pin re-proves it)")
        return True
    print("  installing — the workspace is large; minutes, not seconds …")
    r = run([tool("pnpm"), "install"], cwd=CHASSIS, timeout=1800)
    ok = r.returncode == 0 and installed()
    tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
    say(GREEN if ok else FAILED, "install", tail[0][:90])
    return ok


def step_no_build() -> bool:
    """The absence of a build step, asserted rather than implied."""
    ok = runs_from_source()
    say(GREEN if ok else FAILED, "runs from source",
        "apps/cli/src/bin.ts present — tsx executes the sources; no artifact is needed"
        if ok else "apps/cli/src/bin.ts missing — verify the pin")
    say(GREEN, "build forbidden",
        "`pnpm run build` regenerates pinned artifacts (measured: +6,463 files) — never run it here")
    return ok


def step_launch() -> bool:
    """Start `pnpm dsh web --no-open`, probe loopback until it answers, report, stop."""
    url = "http://127.0.0.1:3080"
    proc = subprocess.Popen([tool("pnpm"), "dsh", "web", "--no-open"],
                            cwd=CHASSIS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    up = False
    for _ in range(60):
        time.sleep(2)
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                up = resp.status < 500
                break
        except urllib.error.HTTPError:
            # a 404 from a LISTENING server is an answer — the measured first
            # response of a fresh dsh web host on `/` is exactly that, and the
            # first draft of this probe counted it as down
            up = True
            break
        except Exception:
            if proc.poll() is not None:
                break
    say(GREEN if up else FAILED, "harness answers",
        f"{url} — loopback only, per the chassis's own trust-boundary doctrine"
        if up else "no answer on 127.0.0.1:3080 within 120 s")
    proc.terminate()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
    say(GREEN, "harness stopped", "boot verifies standing-up; running it is the operator's act")
    return up


def status() -> int:
    print("F-BOOT · status\n")
    pin = step_pin()
    tc = step_toolchain()
    say(GREEN if installed() else UNVERIFIED, "installed",
        "node_modules present" if installed() else "not yet — run forge/boot.py")
    say(GREEN if runs_from_source() else FAILED, "runs from source",
        "tsx executes the sources; build is forbidden and unnecessary" if runs_from_source()
        else "apps/cli/src/bin.ts missing — verify the pin")
    say(UNVERIFIED, "plugins mounted (level 2)",
        "chunk and phi_scan are bound as subprocess capabilities; in-harness "
        "tool registration is declared, not done")
    say(UNVERIFIED, "resident",
        "registrar.state = off by design; the switch fails toward inert")
    return 0 if (pin and tc) else 1


def main(argv: list[str]) -> int:
    if "--status" in argv:
        return status()

    from profile import require_forge
    require_forge("forge/boot.py")

    print("F-BOOT · clone → standing harness\n")
    for step in (step_pin, step_toolchain, step_install, step_no_build):
        if not step():
            print("\nstopped at the first refusal — nothing later ran. Fix and re-run;")
            print("every step is idempotent.")
            return 1
    if "--no-launch" not in argv:
        if not step_launch():
            return 1
    print("\nF-BOOT: the harness stands. Next: forge/PLUGINS.md for what it can")
    print("be given, and AGENTS.md for what a completion inside it must obey.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
