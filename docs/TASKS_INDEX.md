# Tasks index — Crosscheck

Generated 2026-09-13 by `generate-tasks` from `docs/PRD.md`, `CLAUDE.md` Blueprint and the three
reference screens in `design/screens/`. Only `verify-task` ticks a box here. The task file wins
over this table when they disagree.

## Phases

| Phase | What it holds | Where it is owned |
|---|---|---|
| **v1 (this list)** | Pipeline from frozen snapshots to the 96-row capability table and data pack; the single-file offline app with three screens; report-ready figures; submission zip. Deadline 2026-09-30. | PRD §4, §5, §6 |
| v1.1, deferred not cancelled | D1 modelled coverage publisher; D2 "report signal here"; D3 wider universe; D4 LLM road-note extraction; D5 national scope. Seams already in Blueprint: publisher line (`kind`), flag emitter, requirement row, pack header version. | PRD §10 |
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
- [x] Task-07: Community screen in the app
- [x] Task-08: Map screen in the app
- [x] Task-09: Share screen, QR, save-as-file, and the host-only PWA files
- [x] Task-10: Report-ready figures and tables
- [x] Task-11: Reproduction README, submission packaging, spike retirement
- [x] Task-12: Freshness, history and changes in the pack (added 2026-09-15)
- [x] Task-13: Send as SMS, copy statement and the freshness line (added 2026-09-15)
- [x] Task-14: Changes since the previous snapshot on the Share screen (added 2026-09-15)
- [x] Task-15: Compare two communities (added 2026-09-15)
- [ ] Task-16: Sunlight mode (added 2026-09-15; blocked until the sunlight tokens are exported from the design project)
- [x] Task-17: QR encoder in the app (second batch, added 2026-09-15)
- [x] Task-22: Mesh-size statement, 200 bytes (second batch, added 2026-09-15)
- [x] Task-20: Map layers in the pipeline: towns, highways, regions, coverage (second batch, added 2026-09-15; reads reports/2026-09-15-map-bytes.md)
- [x] Task-18: Transfer by camera, QR frames (second batch, added 2026-09-15)
- [x] Task-19: Nearby chat over the phone's own Wi-Fi (second batch, added 2026-09-15)
- [x] Task-21: Map second pass in the app: layers, zoom, pan, labels; pack version 2 (second batch, added 2026-09-15)
- [x] Task-24: Received pack updates the app in place (added 2026-09-15, Tarik: "update atsin")
- [x] Task-25: QR reading on every browser, jsQR fallback for iPhone (added 2026-09-15, OQ15)
- [x] Task-26: Small fixes before outside testers, and the page that never updates (added 2026-09-15)
- [x] Task-27: Transfer by camera, visible progress and missed-frame repair (added 2026-09-15)
- [x] Task-28: Install as a real home-screen app, tactics from the Calisthenics app (added 2026-09-15)
- [x] Task-29: Map points cluster by zoom, tactic from the AI Challenge app (added 2026-09-15)
- [x] Task-30: A first-time user understands the app, clarity batch from Tarik's phone test (added 2026-09-16)
- [x] Task-31: Transfer v3 experiment: A, B, C and B+C measured on two phones (third batch, added 2026-09-16)
- [x] Task-32: Remove nearby chat and the Wi-Fi join QR (third batch, added 2026-09-16)
- [x] Task-34: Community screen, third pass: one screen before scrolling (third batch, added 2026-09-16)
- [x] Task-33: Map, third pass: one shape in four fill states, layers off, service selector, worst-first list (third batch, added 2026-09-16)
- [x] Task-35: Report here: the community's own evidence, on the phone, shared by choice (third batch, added 2026-09-16)
- [x] Task-36: Transfer v3 in the app from the Task-31 winner (third batch, added 2026-09-16; spec completed after Task-31)
- [x] Task-37: Transfer v4: the pack travels by light, not the app; lite copy withdrawn (added 2026-09-16 evening)
- [x] Task-38: Measured publisher: the National Audit non-alignment tiles as the fifth line (fourth batch, added 2026-09-17)
- [x] Task-42: Cuts: changes since the previous snapshot, the mesh text, compare (fourth batch, added 2026-09-17)
- [x] Task-39: Map-claim reliability: one model trained in the pipeline on the Audit, AUC 0.65 kill criterion (fourth batch, added 2026-09-17; ⛔ cleared 2026-09-17)
- [x] Task-40: Priority score, intervention and addressee; the LEO sentence; MBSP sites (fourth batch, added 2026-09-17)
- [x] Task-41: Priority tab, the reliability line, the analyst's sixty seconds; pack version 3 (fourth batch, added 2026-09-17)
- [x] Task-43: Findings pack: figures, tables and docs/FINDINGS.md for the report (added 2026-09-17 evening)
- [x] Task-44: The pack's `headline` block: three counts for the home screen (fifth batch, added 2026-09-21)
- [x] Task-45: Home screen, rows as questions, the summary sentence, inside words folded (fifth batch, added 2026-09-21)
- [x] Task-46: Tests for the fifth batch, written from the contract, not from the code (fifth batch, added 2026-09-21)
- [ ] Task-47: `headline()` reads the health-centre label from a named constant (sixth batch, added 2026-09-21)
- [ ] Task-48: Map v3: three lenses, no clusters, regions that zoom, one screen; the degraded clause (sixth batch, added 2026-09-21)
- [ ] Task-49: Tests for map v3 and the degraded clause, written from the contract (sixth batch, added 2026-09-21)

## Later

Not written as task files yet (no id until the file exists; generate-tasks, one wave at a time):

- The ten-second hand-over test with three people, recorded under `reports/` (Tarik; PRD §4.2 fifth batch's pass mark).
- The report's "robust top list": which communities stay in the top ten under every row of the sensitivity table.
- NT Government 2019 against 2022 lists as a real before/after finding for the report.
- Per-service Report here (`CR2`): future work in the report, not built in v1.

## Execution routing

Summary of each task's Execution and Lane blocks. `claude-worker` means an Agent-tool subagent
spawned from the Claude main loop (Tarik, 2026-09-13: Claude workers, not Codex); rerouting a
task to `codex` is an edit to its Execution block, dated, not a runtime choice. The main loop
writes nothing here itself except the review after DONE.

| Task | Agent | Effort | Depends on | Parallel wave |
|---|---|---|---|---|
| Task-00 | claude-worker | high | none | 1 |
| Task-01 | claude-worker | medium | Task-00 | 2 |
| Task-02 | claude-worker | medium | Task-01 | 3 |
| Task-03 | claude-worker | medium | Task-01 | 3 |
| Task-04 | claude-worker | medium | Task-01 | 3 |
| Task-05 | claude-worker | high | Task-02, Task-03, Task-04 | 4 |
| Task-06 | claude-worker | high | Task-05 | 5 |
| Task-07 | claude-worker | high | Task-06 | 6 |
| Task-08 | claude-worker | high | Task-07 | 7 |
| Task-09 | claude-worker | high | Task-08 | 8 |
| Task-10 | claude-worker | medium | Task-06 | 6 (beside Task-07) |
| Task-11 | claude-worker | medium | Task-09, Task-10 | 9 |
| Task-12 | claude-worker | medium | Task-10 | 9 (beside Task-11) |
| Task-13 | claude-worker | high | Task-12 | 10 |
| Task-14 | claude-worker | medium | Task-12, Task-13 | 11 |
| Task-15 | claude-worker | high | Task-14 | 12 |
| Task-16 | claude-worker | medium | Task-15 | 13, after the stop marker is cleared |

Tasks 02, 03 and 04 own disjoint files and can run as one wave in separate worktrees; so can
Task-07 and Task-10. Every other step is serial because it edits `app/app.js` or `pipeline/pack.py`.

After each wave goes green: `/code-review` over the accumulated diff with the task files and
Blueprint attached; `review-visual` after Tasks 07, 08 and 09 against `design/screens/*.html`,
advisory only.
| Task-17 | claude-worker | no | high | none | 14 |
| Task-22 | claude-worker | no | medium | none | 14 (beside Task-17) |
| Task-20 | claude-worker | no | high | none (reads the map-bytes report) | 14 (beside Task-17) |
| Task-18 | claude-worker | no | high | Task-17 | 15 |
| Task-19 | claude-worker | no | high | Task-18 | 16 |
| Task-21 | claude-worker | no | high | Task-19, Task-20 | 17 |
| Task-26 | claude-worker | no | medium | Task-21 | 18 |
| Task-24 | claude-worker | no | high | Task-26 | 19 |
| Task-25 | claude-worker | no | high | Task-24 | 20 |
| Task-27 | claude-worker | no | high | Task-25 | 21 |
| Task-28 | claude-worker | no | medium | Task-26 | 19 (beside Task-24; disjoint files) |
| Task-29 | claude-worker | no | high | Task-21 | 20 (beside the Task-25 fix; map files only) |

| Task-31 | claude-worker (opus) | no | high | none | 22 |
| Task-32 | claude-worker | no | medium | none | 22 (beside Task-31; disjoint files) |
| Task-34 | claude-worker | no | high | Task-32 | 23 |
| Task-33 | claude-worker | no | high | Task-34 | 24 |
| Task-35 | claude-worker (opus) | no | high | Task-34 | 24 (beside Task-33: report.js, community sections; Task-33 owns the map sections) |
| Task-36 | claude-worker (opus) | no | high | Task-31 (measured), Task-32 | 25 |
| Task-37 | claude-worker (opus) | no | high | Task-36 | 26 |

| Task-38 | claude-worker (opus) | no | high | none | 27 |
| Task-42 | claude-worker | no | medium | none | 27 (beside Task-38; disjoint files except `pack.py`, different hunks) |
| Task-39 | claude-worker (opus) | no (⛔ cleared 2026-09-17 by Tarik: fetch and train before the OQ18 answer) | high | Task-38 | 28 |
| Task-40 | claude-worker (opus) | no | high | Task-38, Task-39 | 29 |
| Task-41 | claude-worker (opus) | no | high | Task-40, Task-42 | 30 |
| Task-43 | claude-worker | no | medium | Task-41 | 31 |
| Task-44 | codex (luna) | no | medium | none | 32 |
| Task-46 | codex (luna) | no | high | none (contract only; runs nothing) | 32 (beside Task-44) |
| Task-45 | codex (luna) | no | high | Task-44 | 33 |
| Task-47 | codex (small tier) | no | low | Task-44 | 34 |
| Task-48 | codex (top bee tier) | no | high | Task-45 | 34 (the only lane that builds) |
| Task-49 | codex (small tier) | no | high | none (contract only; runs nothing) | 34 |

Fifth batch (2026-09-21) execution note: PRD 4.2 fifth batch, the ten-second hand-over test. Codex
pool clear (11 % / 33 %), so every lane is a Codex bee; the main loop (Fable) wrote the specs, runs
the gate once all three land, does the eye review and writes `docs/demo-script.md`. Task-46 writes
the tests for 44 and 45 from their contracts and never opens the new code.

Fourth batch (2026-09-17) execution note: Tarik's decision after Eko's function-by-function
review, PRD §4.2 fourth batch and §2 "the analyst's sixty seconds". Codex is at 100 % until
2026-09-19, so every lane is a Claude worker; the main loop (Fable) writes the specs, runs
`verify-task` and the gate. Wave 27 is two disjoint lanes; 28 to 30 are serial on
`pipeline/pack.py` and then `app/app.js`. The camera transfer is untouched by this batch and is
revisited after Task-41. Tarik owns the OQ2/OQ18 licence email, the BoM download (OQ3), the ADII
export (OQ5) and the weights in `pipeline/priority_weights.csv` once Task-40 writes them.

Third batch (2026-09-16) execution note: Codex is at 100 % on both windows until 2026-09-19, so
every lane is a Claude worker; the main loop (Fable) writes the specs, runs `verify-task` and the
gate, and Tarik runs the phone measurements Task-31 needs. Waves 23 and 24 are serial on
`app/app.js` except where the lanes own disjoint render functions, named in each Lane block.

Second batch (2026-09-15) execution note: Codex quota is exhausted until 2026-09-19, so every
lane is a Claude worker. Wave 14 is three disjoint lanes; 15 to 17 are serial because each
touches `app/app.js`. Task-16 keeps its place and its stop marker; it is not in this batch's
waves.
