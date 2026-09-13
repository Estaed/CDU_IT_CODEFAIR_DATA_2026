# Tasks index — Crosscheck

Generated 2026-09-13 by `generate-tasks` from `docs/PRD.md`, `CLAUDE.md` Part 2 and the three
reference screens in `design/screens/`. Only `verify-task` ticks a box here. The task file wins
over this table when they disagree.

## Phases

| Phase | What it holds | Where it is owned |
|---|---|---|
| **v1 (this list)** | Pipeline from frozen snapshots to the 96-row capability table and data pack; the single-file offline app with three screens; report-ready figures; submission zip. Deadline 2026-09-30. | PRD §4, §5, §6 |
| v1.1, deferred not cancelled | D1 modelled coverage publisher; D2 "report signal here"; D3 wider universe; D4 LLM road-note extraction; D5 national scope. Seams already in Part 2: publisher line (`kind`), flag emitter, requirement row, pack header version. | PRD §10 |
| Optional flags, licence-gated | BoM cyclone count (OQ3), National Audit tiles (OQ2): new flag emitters, drop if unanswered by 2026-09-26. | PRD §9 |

Outside the software gate, owned by Emma, Thanh and Will: the 8-page report, the deck, the
pitch (PRD §4.3). Task-10 hands them their figures; Task-11 leaves a slot in the zip.

## Tasks, in execution order

- [x] Task-00: Walking skeleton — rules with tests, interim pack, app shell, build, gate green
- [x] Task-01: BushTel source — identity, services present, capability flags
- [x] Task-02: NBN source — fixed-line and fixed-wireless footprints
- [x] Task-03: ACCC source — carrier predicted coverage polygons 2025
- [x] Task-04: ACMA RRL and NT Government sources — licensed sites and the coverage lists
- [x] Task-05: Merge, provenance, and the pipeline entry point
- [x] Task-06: NT outline, projected points, filters and actions in the pack
- [ ] Task-07: Community screen in the app
- [ ] Task-08: Map screen in the app
- [ ] Task-09: Share screen, QR, save-as-file, and the host-only PWA files
- [ ] Task-10: Report-ready figures and tables
- [ ] Task-11: Reproduction README, submission packaging, spike retirement

## Execution routing

Summary of each task's Execution and Lane blocks. `claude-worker` means an Agent-tool subagent
spawned from the Claude main loop (Tarik, 2026-09-13: Claude workers, not Codex); rerouting a
task to `codex` is an edit to its Execution block, dated, not a runtime choice. The main loop
writes nothing here itself except the review after DONE.

| Task | Agent | Plan mode | Effort | Depends on | Parallel wave |
|---|---|---|---|---|---|
| Task-00 | claude-worker | no | high | none | 1 |
| Task-01 | claude-worker | no | medium | Task-00 | 2 |
| Task-02 | claude-worker | no | medium | Task-01 | 3 |
| Task-03 | claude-worker | no | medium | Task-01 | 3 |
| Task-04 | claude-worker | no | medium | Task-01 | 3 |
| Task-05 | claude-worker | no | high | Task-02, Task-03, Task-04 | 4 |
| Task-06 | claude-worker | no | high | Task-05 | 5 |
| Task-07 | claude-worker | no | high | Task-06 | 6 |
| Task-08 | claude-worker | no | high | Task-07 | 7 |
| Task-09 | claude-worker | no | high | Task-08 | 8 |
| Task-10 | claude-worker | no | medium | Task-06 | 6 (beside Task-07) |
| Task-11 | claude-worker | no | medium | Task-09, Task-10 | 9 |

Tasks 02, 03 and 04 own disjoint files and can run as one wave in separate worktrees; so can
Task-07 and Task-10. Every other step is serial because it edits `app/app.js` or `pipeline/pack.py`.

After each wave goes green: `/code-review` over the accumulated diff with the task files and
Part 2 attached; `review-visual` after Tasks 07, 08 and 09 against `design/screens/*.html`,
advisory only.
