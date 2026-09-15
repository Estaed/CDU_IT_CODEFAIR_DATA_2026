# Otopilot run report — 2026-09-15

Main loop: Claude Fable 5.1 (this session, Tarik's choice at approval). Bees: `claude -p`, one
per lane, detached worktrees under `../.lanes/`. Plan: `reports/otopilot-2026-09-15-plan.md`,
approved 12:35. `BASE_SHA` `5826840` (the plan commit). Run started 12:43 local.

## Outcome

| Task | Result | Bee tier | Attempts | Bee wall | Bee cost | Trajectory | Main commit |
|---|---|---|---:|---:|---:|---|---|
| Task-08 map screen | **green, review-visual pending** | opus | 1 (+ main-loop finish) | 8 min, 49 turns | $2.14 | lane gate 1 fail -> 0 after the PRD alignment below | `c90c3bf` + `6305792` (status) |
| Task-10 figures | in flight | sonnet | | | | | |
| Task-09 share screen | in flight (wave 2 opened 13:12, base `6305792`) | opus | | | | | |
| Task-11 packaging | not started (wave 3) | sonnet | | | | | |

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
