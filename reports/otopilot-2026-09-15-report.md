# Otopilot run report — 2026-09-15

Main loop: Claude Fable 5.1 (this session, Tarik's choice at approval). Bees: `claude -p`, one
per lane, detached worktrees under `../.lanes/`. Plan: `reports/otopilot-2026-09-15-plan.md`,
approved 12:35. `BASE_SHA` `5826840` (the plan commit). Run started 12:43 local.

## Outcome

| Task | Result | Bee tier | Attempts | Bee wall | Bee cost | Trajectory | Main commit |
|---|---|---|---:|---:|---:|---|---|
| Task-08 map screen | **green, review-visual pending** | opus | 1 (+ main-loop finish) | 8 min, 49 turns | $2.14 | lane gate 1 fail -> 0 after the PRD alignment below | `c90c3bf` + `6305792` (status) |
| Task-10 figures | **green, DONE** | sonnet | 1 (+ main-loop commit) | 19 min, 100 turns | $2.73 | lane gate GREEN first run (no commands ran in the bee, 20 refusals) | `48c8ab0` + `d186138` (status) |
| Task-09 share screen | **green, review-visual pending** | opus | 1 | 6 min, 25 turns | $1.74 | lane gate GREEN, main gate GREEN, 0 refusals with `--allowedTools` | `b7c3234` + `e62ff08` (status) |
| Task-11 packaging | in flight (wave 3 opened 13:20, base `e62ff08`) | sonnet | | | | | |

## Checkpoint after wave 1 (Task-08 integrated 13:08)

- Claude 5-hour window 18% -> 30% (delta 12, estimate was 12); weekly 42% -> 43%. Codex unused.
- **Bees could not run commands.** `--permission-mode acceptEdits` auto-accepts file edits
  only; every Bash and PowerShell call of the Task-08 bee (build, ruff, gate, `git add`) was
  refused and it reported BLOCKED with the code written and uncommitted. Launcher fixed for
  every later bee: `--allowedTools "Bash,PowerShell,Read,Edit,Write,MultiEdit,Glob,Grep"`.
  The 2026-09-13 run did not hit this; the difference is not yet explained (lesson for the
  skill's Claude recipe, brain side).
- Task-08 lane gate, run by the main loop: 11 of 12 browser tests green; the one red asserted
  Baniyala "1 of 4" as the DoD said. The PRD decision log (2026-09-13) rules 1 of 3 — a
  `not-recorded` line is not a source — and the community screen already renders 3. The main
  loop changed that one expected value, dated it in the test and the DoD, and did not respawn.
  Second gate: lint E501 on the main loop's own comment; shortened; third gate GREEN. Main gate
  GREEN at `c90c3bf` (93 unit + 12 browser).
- `pack.filters[*].definition` is absent, so the map prints only "Showing n of 96" (allowed by
  the task file).
- Wave 2 opened before Task-10 finished: Task-09 depends only on Task-08 and its OWNS is
  disjoint from Task-10's, so both plan invariants hold.

## Checkpoint after wave 2 (Task-10 integrated 13:15, Task-09 integrated 13:19)

- Claude 5-hour window reset during the wave (30% -> 0% at 13:11, new window); weekly
  43% -> 44%. Codex unused. Wave 2 cost cannot be read as a 5-hour delta across the reset;
  weekly delta 1 point.
- Task-10 bee wrote `figures.py`, the test and the `run_pipeline.py` line with no command
  run (20 refusals, same cause as Task-08); the main loop ran the lane gate: GREEN first time,
  7 new unit tests, PNGs 2000x3200, tables 11/8+2/21 rows, greps clean. The main loop
  committed the lane (bee had not) and integrated. Advisory for the team's eye, not in the
  DoD: both maps draw hollow circles instead of the verdict glyph shapes, and the legend
  overlaps the south-west corner of the outline.
- Task-09 bee (first with `--allowedTools`) ran ruff, its tests and the full gate itself,
  committed once, 0 refusals. Departures it recorded: APP_URL read from the pack, QR and
  sizes meta inserted by text at `</head>` and the pack marker (`app/index.html` is outside
  the lane), manifest link added by script over `https:` only, `crosscheck-v1` cache name,
  nothing exercised over `https:`. `dist/` now holds `index.html` (305,315 bytes), `sw.js`,
  `manifest.webmanifest`.
- Wave 3: Task-11 on `sonnet`, base `e62ff08`, launched 13:20 with a 60-minute timebox.

## Incident after wave 2 (13:25) and recovery (13:25-15:45)

- `git worktree remove --force` on the three integrated lanes followed the junctions inside
  them and emptied their targets: `.venv` (404 MB), `data/raw` (3.7 GB, gitignored) and
  `data/out/cache` (277 MB). Commits and `data/out/` were untouched. Main-loop error: the
  junctions had to be unlinked (`(Get-Item $j).Delete()`) before the worktree was removed;
  the wave-3 cleanup now does that and verified the targets afterwards.
- Recovery: `uv sync` rebuilt `.venv`; the fetch scripts re-downloaded every raw file; ABS,
  NBN, NTG and ACCC came back byte-identical to `PROVENANCE.md`. BushTel and RRL cannot be
  re-fetched as of 12 September: Tarik chose the honest path, `_2026-09-15` files, dates
  updated in the provenance registry and the tests. The ACCC fetch also brought the Optus 5G
  and TPG 5G layers that the 12 September budget had skipped. The parse cache was rebuilt
  (13:41-15:00).
- Data delta 12 -> 15 September: no verdict, path or publisher claim changed in any of the
  96 rows. Milingimbi `svc_wifi` Y -> N; Angurugu Wi-Fi comment; both profile stamps; RRL site
  table 576 -> 575 rows (nearest-site distances unchanged); the two 5G columns -1 -> real.
- Fixtures frozen on 2026-09-15 as a second set beside the 2026-09-12 files (Tarik's choice);
  tests repointed; `_to_iso` accepts ISO dates; ACCC oracle updated for the 5G layers; RRL
  row count 575. Gate GREEN at `d1dac2c` (104 unit + 15 browser, 305,594 / 255,883 bytes).
- The Task-11 bee that had started on the empty `.venv` was stopped at 13:30 with no changes
  in its worktree; its worktree was removed junction-first.
- Tarik added Task-12..16 (PRD §4.2 additions, `2b51e10`); Task-16 carries a stop marker.

## Wave 9 (15:50): Task-11 + Task-12, both `sonnet`, base `d1dac2c`

Task-12 depends on Task-10 only and owns `pipeline/changes.py`, `pipeline/pack.py`,
`scripts/run_pipeline.py`, `data/out/history/`, two tests; Task-11 owns `README.md`,
`scripts/package_submission.py`, `tests/test_package.py`, `spike/`, `.gitignore`. Disjoint.
Quota before the wave: Claude 5-hour 0% -> measured below at the checkpoint, weekly 44%.

## Checkpoint after wave 9 (Task-12 integrated 16:00, Task-11 integrated 16:10)

- Claude 5-hour 0% -> 28% before the wave (includes the recovery work) -> measured at the
  next checkpoint; weekly 44% -> 46%.
- Task-12 (`sonnet`, 12 min, 28 turns, $1.15, 0 refusals): lane gate GREEN first run, 13 new
  tests; main GREEN at `552a1a0`; status `af0d579`. `changes.items` = Milingimbi only.
- Task-11 (`sonnet`, 16 min, 45 turns, $1.48, 0 refusals): lane gate GREEN, 5 packager tests,
  zip 940,723 bytes / 76 entries; one DoD grep needed three docstrings inside `pipeline/`
  reworded by the main loop; main GREEN at `0780fe8` (122 unit + 15 browser); status
  `38f8880`. Leftover gitignored `spike/raw/` held a duplicate NTG 2021 xlsx (byte-equal to
  `data/raw/ntg_2021.xlsx`, deleted) and the NTG 2021 data-quality statement PDF, moved to
  `docs/ntg_2021_data-quality-statement.pdf`.
- Wave 10 (16:12): Task-13 on `opus`, base `af0d579` (Task-11 owns no app file), 75 minutes.
