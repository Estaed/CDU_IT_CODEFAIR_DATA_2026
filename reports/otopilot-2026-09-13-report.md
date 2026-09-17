# Otopilot run report — 2026-09-13

Main loop: Claude Fable 5.1 (this session). Bees: `claude -p`, one per lane, detached
worktrees under `../.lanes/`. Plan: `reports/otopilot-2026-09-13-plan.md`. `BASE_SHA`
`9426f43` (the plan commit). Run 14:56–16:20 local.

## Outcome

| Task | Result | Bee tier | Attempts | Bee wall | Bee cost | Lane gate | Main commit |
|---|---|---|---:|---:|---:|---|---|
| Task-02 NBN | **green, DONE** | sonnet | 1 | 5 min, 27 turns | $0.88 | GREEN after the lint fix below | `1ca8b1b` + `f0f847f` (status) |
| Task-03 ACCC | **green, DONE** | opus | 1 (+ main-loop finish) | 6 min, 28 turns | $2.12 | GREEN after the lint fix below | `f130065` + `6b405c5` (status) |
| Task-04 RRL + NTG | **green, DONE** | opus | 1 | 9 min, 34 turns | $2.51 | GREEN after the lint fix below | `e9bb506` + `e03fcab` (status) |

Final main-branch gate at `6b405c5`: ruff clean (no cache), 59 unit + 1 browser test, sizes
307,624 / 288,194 bytes, GATE GREEN. Tracker ticked for all three. No task went to
`BACKLOG.md`; no worktree remains (`git worktree list` shows main only); wake lock released.

Every regression matched its spike fixture with 0 differences across all 96 rows: NBN 7
columns, ACCC 13 columns on the real KMLs, RRL 19 columns plus the 576-row site table
byte-equal, NTG 18 columns including the embedded newline in row 654.

## What did not go to plan

1. **The baseline was red, not green.** `ruff check .` at `112b193` printed `All checks
   passed!` from a stale `.ruff_cache`; `--no-cache` finds `I001` in `tests/test_rules.py`
   (missing blank line before `from pipeline import rules`, there since Task-00). Every bee hit
   it, every bee diagnosed it correctly and left the file alone because it was outside OWNS. The
   main loop fixed it on main (`bd89b1d`) and cherry-picked the fix into each worktree before
   running the lane gates. **Decision for Tarik:** make `scripts/gate.py` run ruff with
   `--no-cache` (a Blueprint change: the gate is owned by Blueprint). The lint step costs under a second
   either way.
2. **The Task-03 bee ended its turn on a background wait.** It wrote the module, fetch script,
   test and fixture, started the 50-minute cold parse in the background, said "a background wait
   will signal when it exits", and returned. In `-p` mode nothing signals; the child process died
   with the bee, the cache stayed empty, nothing was committed. The main loop ran the cold parse
   itself in the bee's worktree (`pytest tests/test_source_accc.py`: 6 passed, 3,531 s setup),
   timed the warm run (6.8 s), reviewed the four files against the contract, committed them as
   the lane commit, and gated as usual. No second bee was needed. Lesson for the otopilot skill
   (brain, not this repo): a lane whose gate contains one long single-threaded step needs either
   "no background jobs, wait in the foreground" in the brief or the main loop pre-warming the
   step before launch.
3. **Bee reports were claims, checked:** Task-04 reported `BLOCKED` solely because of the lint
   error above; its own work was complete and green. Task-02 reported `COMPLETE` with the same
   caveat. Both were correct.

## Mutation checks (main loop, on main, after integration)

| Module | Break | Regression |
|---|---|---|
| nbn | fixed line reported as fixed wireless | red |
| nbn | distance divisor 1000 -> 1001 | red |
| nbn | attrs separator `;` -> `,` | green, unobservable: the only in-footprint row (Yirrkala) has one attribute |
| rrl | 5 km threshold -> 6 km | red |
| rrl | 700 MHz band dropped | red (sites 441 vs 576) |
| rrl | Hutchison exclusion emptied | green, unobservable: those clients hold no NT cellular site |
| ntg | BushTel aliases ignored | red |
| ntg | 2022 header offset 6 -> 7 or 8 | green, unobservable: rows 6–7 are Adelaide River (Village) and Aileron Station (Highway), not among the 96 |
| accc | km per degree 111 -> 110 | red |
| accc | `contains` -> `touches` | red |
| accc | `REQUIRED` emptied | red (missing-file test) |
| accc | MOCN counted as a fourth carrier | green, unobservable: `tpg_4g_2025` is 0 for all 96 |

The four green mutations are limits of the frozen data, not of the tests; each is noted in the
task's Status line.

## Measured times

| Test module | Wall |
|---|---:|
| `tests/test_source_nbn.py` | 3.3 s (`nbn.load` 2.6 s; the wireless zip's bbox read) |
| `tests/test_source_accc.py` cold cache | 3,531 s, once; six `.nt.pkl` files, 290 MB, gitignored |
| `tests/test_source_accc.py` warm cache | 6.8 s |
| `tests/test_source_rrl.py` | 22.8 s (`device_details.csv` streamed twice: `load` and `test_sites_table`) |
| `tests/test_source_ntg.py` | 1.4 s |
| full gate on main, warm | about 60 s |

## Decisions for Tarik

- `gate.py`: ruff `--no-cache` (see 1 above).
- `data/out/cache/` is 290 MB and gitignored; a fresh clone pays one 59-minute cold parse before
  the ACCC test is green. Task-11's reproduction README must say so, or the cache gets committed
  somewhere outside git (not recommended at that size).
- Three fetch scripts (`nbn`, `accc`, `rrl`) each carry a ~10-line streaming download helper
  because no lane could add a shared file. Accept, or fold into one `pipeline/fetch/_download.py`
  in a later `simplify` pass.
- `spike/raw/` is now empty (its files moved to `data/raw/`); the spike scripts cannot run again.
  They are frozen and Task-11 deletes `spike/`, so nothing is lost, but it is a fact.
- Bee logs and briefs are kept outside the repo at `../.lanes/briefs/` (1.1 MB) as evidence; delete
  when no longer wanted.

## Awaiting eye check

None: no task in this wave produced anything a person looks at.
