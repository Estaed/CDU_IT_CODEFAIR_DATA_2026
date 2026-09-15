# Otopilot range plan — 2026-09-15

Written by the main loop (Claude Fable 5.1) for the run Tarik requested at 12:20: "otopilot
başlat, tüm taskları bitirelim" — Task-08 to Task-11, the whole remaining v1 backlog. Preflight
`onkontrol.py --tasks 08,09,10,11 --orchestrator claude --delegate claude` was green at
`562bfbb` and is re-run on the commit that carries this plan; that commit is `BASE_SHA` for
wave 1. Later waves cut their lanes from the integrated main HEAD.

## Direction

| Field | Value |
|---|---|
| Planner | Claude Fable 5.1, this foreground session |
| Orchestrator | Claude, this session (Fable 5.1). Skill default is an `opus` session; Tarik is at the desk and asked to start now, so the run drives from here unless he says `opus` |
| Bees | `claude -p`, one per lane, detached worktree under `../.lanes/task-XX` |
| Fallback delegate | **none**: Codex 5-hour 100% (resets 13:20) and weekly 100% (resets in 4 days). A Codex handover is not legal in this plan; at a Claude wall the run waits (5-hour) or closes (weekly) |
| Quota at preflight (12:20) | Claude 5-hour 18% (resets 13:11), weekly 42% (GO). Codex 100%/100% (STOP, unused) |
| Baseline gate at `562bfbb` | GREEN: ruff clean, 93 unit + 6 browser tests, 286,977 / 255,604 bytes |
| Stop markers | none in the four task files |
| BACKLOG.md | no entry for Task-08..11; nothing to carry into a brief |

## Range classes

All four tasks are plain lanes: agent `claude-worker` (not the orchestrating CLI), plan mode
`no`, complete Lane blocks, disjoint OWNS across the selection (preflight). No contract-first
lane, no hard stop. Task-08 and Task-09 change what is looked at, so both are reported
**green, review-visual pending** — never plain green (TASKS_INDEX: `review-visual` after 07, 08, 09).

## Waves

| Task | Wave | Agent | Model / tier | Effort | OWNS | GATE | Timebox | Attempts |
|---|---:|---|---|---|---|---|---:|---:|
| Task-08 map screen | 1 | `claude -p` | `opus` | high | `app/app.js` (map renderer), `tests/browser/test_map.py` | `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` | 75 min | 1–2 |
| Task-10 figures + tables | 1 | `claude -p` | `sonnet` | medium | `pipeline/figures.py`, `scripts/run_pipeline.py` (additive), `tests/test_figures.py`, `data/out/figures/`, `data/out/tables/` (outputs) | same | 60 min | 1–2 |
| Task-09 share screen, QR, PWA files | 2 | `claude -p` | `opus` | high | `app/app.js` (share renderer), `app/sw.js`, `app/manifest.webmanifest`, `scripts/build_app.py` (additive), `tests/browser/test_share.py`, `tests/test_build.py` (additive) | same | 75 min | 1–2 |
| Task-11 README, packaging, spike retirement | 3 | `claude -p` | `sonnet` | medium | `README.md` (Reproduce section), `scripts/package_submission.py`, `tests/test_package.py`, deletion of `spike/`, `.gitignore` (one line, derived at plan time) | same | 60 min | 1–2 |

Wave invariants: Task-08 and Task-10 share no path (`app/` vs `pipeline/`+`scripts/run_pipeline.py`)
and neither depends on the other (08 → 07, 10 → 06, both DONE). Task-09 depends on 08 and
edits `app/app.js`; Task-11 depends on 09 and 10. Three serial waves, two lanes in the first.

Tier reasoning: Task-08 is SVG DOM built by hand against `build.mjs` markup with four filter
routes and a selected panel reusing Task-07 functions — the file is already 1,000+ lines and
drift is expensive, so `opus`. Task-09 touches the build script, the QR module-for-module test
and a download assertion under Playwright, so `opus`. Task-10 is matplotlib plus three CSVs
with fixed oracle counts, `sonnet`. Task-11 is a README, a zip script and a deletion, `sonnet`.
`fable` is not a bee under any condition.

Quota estimate per wave (Claude 5-hour window points, from the 2026-09-13 run: bees 5–9 min,
27–34 turns each, orchestrator ~2× the bees): wave 1 ≈ 12, wave 2 ≈ 8, wave 3 ≈ 6. Measured
deltas go into the checkpoint after each wave.

## Derived metadata (written back at plan time)

- Task-11 Lane `OWNS` gains `.gitignore`: the Execution Guide already says to remove the
  `spike/raw/` line, the Lane block omitted the file. Dated in the task file.

## Facts the bees are told (checked by the main loop, 12:25)

- `pack.filters[*].definition` does not exist in `data/out/data_pack.json` (keys: id, label,
  ids). Task-08 renders "Showing n of 96" without the definition and says so in NOTES; the
  bee must not touch `pipeline/`.
- `design/ds/design/tokens.json` exists; Pillow 12.3.0 is in `.venv` (matplotlib dependency).
- `app/sw.js` and `app/manifest.webmanifest` do not exist yet; `scripts/build_app.py` copies
  nothing to `dist/` beyond `index.html`. Task-09 creates both.
- `spike/` is 16 tracked files, 624 KB; nothing under `pipeline/ scripts/ tests/ app/` imports
  it (grep: docstrings only). `tests/test_merge.py` reads `tests/fixtures/` only.
  `spike/raw/` is gitignored and empty since 2026-09-13; the untracked folder on main is
  removed by the main loop after integration, not by the bee.
- The ACCC test needs `data/out/cache/` (277 MB, gitignored) or it re-parses for ~59 min:
  every lane gets a junction to it.

## Worktree setup per lane (main loop, before launch)

`git worktree add --detach ../.lanes/task-XX <base>`; then junctions inside the lane for what
git does not carry: `.venv`, `data/raw`, `data/out/cache` -> the root copies. The lane's gate
builds its own `dist/`.

## Gate and integration

The bee's report is a claim. The main loop runs the lane's `GATE` in the worktree, checks the
single bee commit stays inside `OWNS`, cherry-picks it onto `main`, runs `GATE` again on
`main`, then ticks the task file and `docs/TASKS_INDEX.md` in a status commit. A red lane gets
one second attempt with the first gate output and the failure trajectory in its brief; red
twice goes to `BACKLOG.md` with the reason and every dependent task is skipped with that reason.

Quota is re-measured before every wave (`onkontrol.py --quota-only`): GO spawns the wave,
NARROW spawns one bee at a time, a 5-hour wall waits for the reset by `ScheduleWakeup`, a
weekly wall closes the run.

## Excluded

None. After Task-11 the v1 tracker is complete; what remains outside the gate is the manual
checklist (PRD §6), the report, the deck, the Pages deployment and `review-visual` on 08/09.
