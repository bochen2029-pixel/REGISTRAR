# demo/ — the replay board

**Watch the loop.** One real case from the synthetic site, played back through the percept stream, the floor
judging at every boundary:

```
python demo/replay.py
```

~45 seconds. `--fast` skips the pacing; `--selftest` replays twice and asserts the transcripts
byte-identical, because replay determinism is a proof obligation (SPEC §7); `--transcript out.txt` writes
the full board.

**What you will see, in order:** the case arrives and the board *holds* — 240 minutes of window margin,
on the record. The panel is drawn and the closure surfaces the derived chain: *under the site's own p90
budgets, tonight's OR window has 54 minutes of margin, and the result must be in by 16:06* — a deadline
nobody set, recovered with its full derivation. The lab overruns its contract (**breach, surfaced, with the
site's own p90 quoted against the binder's promise**) and the margin narrows to 22. Then the offer beats its
budget by two and a half hours and **the margin comes back** — *slack can return; an alarm cannot say so* —
which is the alert-fatigue thesis of SPEC §2b rendered in one line of a real case. The case closes 105
minutes inside the window, and the tape shows `surfaced 4 · held 4 · total 8, by addition`.

**Real vs staged, stated:** every duration and the clamp wall-clock are the tape's; the interleaving offsets
between events are composed for display and labeled `[D]`. The budgets in every derivation are folds over
the full tape (`n=` shown inline). The measures block at the end includes one ratio honestly reported
**NOT DERIVABLE** because the tape lacks its denominator column — three states, never two, at the measure
layer too.

This is the first case the percept stream has ever carried. Output lands in `demo/_out/` (gitignored, fresh
per run).
