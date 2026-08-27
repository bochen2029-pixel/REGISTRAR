#!/usr/bin/env python3
"""QC probes — reproduce the QC report's H1/H2 receipts.

Runs the four candidates in this directory through the REAL scorer
(experiments/F-PATCH-DELTA/score.py, answer key from the vault) and the REAL
gate battery (gates/validate_patch.py). Writes RESULT_*.json into THIS
directory only; the rest of the repository is untouched.

    python qc/probes/run_probes.py

Candidates:
  A  pure abstention          rows: []  + 20 holds   -> scorer S=0.50 SHAPED; gates FAIL (rows minItems)
  B  one borrowed row + 19 holds                     -> scorer S=0.53 SHAPED; gates ZERO FAILED (exit 2)
  C  number-stuffed rows                             -> scorer S=0.62 SHAPED; gate 13 catches the stuffing
  D  innocent-prose attest bait (formerly / not withdrawn / no limit)
                                                     -> gate 16 FAILED on innocent evidence text
"""
import contextlib, importlib.util, io, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

spec = importlib.util.spec_from_file_location(
    "score", os.path.join(ROOT, "experiments", "F-PATCH-DELTA", "score.py"))
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
score.HERE = HERE          # RESULT_*.json lands beside this script, never in experiments/

env = dict(os.environ, PYTHONIOENCODING="utf-8")
for name in "ABCD":
    p = os.path.join(HERE, f"qc_cand_{name}.json")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        score.main([p])
    tail = [l.strip() for l in buf.getvalue().splitlines()
            if l.strip().startswith(("score", "fabrications", "verdict"))]
    print(f"SCORER {name}: " + " | ".join(tail))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "gates", "validate_patch.py"), p],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    failed = [l.strip() for l in (r.stdout + r.stderr).splitlines()
              if "FAILED" in l and "defects above" not in l]
    print(f"GATES  {name}: exit={r.returncode} FAILED={len(failed)}")
    for l in failed:
        print(f"       {l[:150]}")
