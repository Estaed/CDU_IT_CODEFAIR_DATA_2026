# Otopilot wave plan — 2026-09-13

Written by the main loop (Claude Fable 5.1) for the run Tarik requested: Task-02, Task-03,
Task-04 with Claude bees. Preflight `onkontrol.py --tasks 02,03,04 --orchestrator claude
--delegate claude` was green at `112b193` before the preparation commit and is re-run on the
commit that carries this plan; that commit is `BASE_SHA` and the report records it.

## Direction

| Field | Value |
|---|---|
| Orchestrator | Claude (this session, Fable 5.1, main loop only) |
| Bees | `claude -p`, one per lane, in its own detached worktree |
| Quota at preflight | Claude 5-hour window 1%, weekly 62% (GO); Codex untouched |
| Baseline gate at `112b193` | GREEN: ruff clean, 37 unit + 1 browser test |
| Stop markers | none in the three task files |
| BACKLOG.md | no entry for Task-02, 03 or 04; nothing to carry into a brief |

## Preparation done by the main loop before the wave (this commit)

- Raw snapshots moved from `spike/raw/` to `data/raw/` so no bee touches the network: the two
  NBN zips, six ACCC KMLs plus the two zip originals, `spectra_rrl.zip` renamed
  `spectra_rrl_2026-09-12.zip`, the four `ntg_*.xlsx`. `spike/raw/` is now empty; the spike
  scripts are frozen and are not run again.
- `data/out/cache/` created and gitignored: the ACCC KML parse cache Task-03's contract defines.
- `## Contract (main loop, 2026-09-13)` appended to each of the three task files, in the
  Task-00 / Task-01 pattern: signatures, column order, string convention, fixture regression,
  oracle figures counted from the spike outputs, departures from the Execution Guide.
- Task-04 `OWNS` gains `tests/fixtures/rrl_sites_nt_2026-09-12.csv` (dated in the Lane block).

## Wave 1 — three lanes, one wave

All three depend only on Task-01 (DONE) and own disjoint paths (preflight: no collisions).

| Task | Wave | Agent | Model / tier | Effort | OWNS | GATE | Timebox | Attempts |
|---|---:|---|---|---|---|---|---:|---:|
| Task-02 | 1 | `claude -p` | `sonnet` | medium | `pipeline/sources/nbn.py`, `pipeline/fetch/nbn.py`, `tests/test_source_nbn.py`, `tests/fixtures/nbn_2026-09-12.csv` | `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` | 60 min | 1–2 |
| Task-03 | 1 | `claude -p` | `opus` | high | `pipeline/sources/accc.py`, `pipeline/fetch/accc.py`, `tests/test_source_accc.py`, `tests/fixtures/accc_2026-09-12.csv` | same | 180 min | 1–2 |
| Task-04 | 1 | `claude -p` | `opus` | medium | `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py`, `pipeline/fetch/rrl.py`, `pipeline/fetch/ntg.py`, `tests/test_source_rrl.py`, `tests/test_source_ntg.py`, three fixtures | same | 90 min | 1–2 |

Tier reasoning, one line each: Task-02 is a straight port of one 200-line lane with one
fixture, so the bee default. Task-03 carries the parse cache design and a 50-minute cold
parse that must not be run twice, and a 14-column regression. Task-04 is two modules, two
fixtures plus a byte-exact site table, and the string convention over 39 columns, which is
where a cheaper bee drifts. `fable` is not a bee under any condition.

Timebox note for Task-03: the spike's parse of the six KMLs took about 50 minutes; the bee's
first test run builds the cache, so 180 minutes is 50 minutes of parse plus the work.

## Worktree setup per lane (main loop, before launch)

`git worktree add --detach <lane> BASE_SHA` under `../.lanes/task-0X` beside the project;
then Windows junctions inside the lane for what git does not carry: `.venv` -> the root
`.venv`, `data/raw` -> the root `data/raw`, and for Task-03 also `data/out/cache` -> the root
`data/out/cache`, so the parse cache is built once and survives the worktree.

## Gate and integration

The bee's report is a claim. The main loop runs the lane's `GATE` in the worktree, checks
the single bee commit stays inside `OWNS`, cherry-picks it onto `main`, runs `GATE` again on
`main`, then a mutation check on each source module (break one transform, the regression must
go red, restore), then `verify-task`. Only `verify-task` marks DONE. A red lane gets one
second attempt with the first gate output and the failure trajectory appended to its brief;
red twice goes to `BACKLOG.md` with the reason.

## Excluded

None of the selected tasks is excluded. Task-05 onward are not in this run: Task-05 depends on
all three lanes and is serial.
