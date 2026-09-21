# Unattended run, 2026-09-21 night: plan and checkpoints

Operator away from about 23:10 ACST ("otopilot gibi düşün"). Orchestrator: Claude main loop
(`fable`, the operator's own foreground session; no `opus` hand-off was arranged). Bees: Codex
(`codex-swarm`), small tier by default, top bee tier for the map lane. Departure from the
`otopilot` skill, stated up front: the two in-flight bees share the working tree with disjoint
`OWNS` (they were launched before the operator left), so there is no worktree or cherry-pick
step for them; the gate's exit code still decides, run by the orchestrator, never by a bee.

## Scope the operator approved, and its edges

1. Land Task-48 (map v3) and Task-49 (its tests, written from the contract); gate; eye review
   at 360 × 780 and in the `terra_nt` emulator.
2. One read-only audit of the built app: the judging criteria under `docs/`, wording that
   still speaks the pre-fifth-batch language, accessibility (contrast, tap targets, focus,
   labels), empty and error states, overflow at 360 px.
3. One defects-only fix wave from that audit.

Not in scope, whatever the audit says: a new feature, screen or pack field; anything under
`pipeline/` that changes a verdict or a rank; the polish-by-Fable experiment (the
operator declined it). Such findings go to `docs/TASKS_INDEX.md` → Later.

Amended 23:13 ACST by the operator ("cok commit sonrasi pushlamayi unutma ki canliya alalim"):
`git push origin main` after each group of commits whose gate is green; never a red or
half-landed tree. First push: the fifth batch, HEAD at that moment.

## Stop rules

A pool within 5 points of its wall (5-hour ≥ 90 %, weekly ≥ 92 %): finish what is in flight,
write the checkpoint, stop. A task red twice: one dated line in `BACKLOG.md` with the failing
command and the reason, move on. Findings that are taste rather than defects: stop.

## Quota at the start of the run (22:47 ACST)

Claude 5-hour 63 %, weekly 29 %. Codex 5-hour 23 %, weekly 35 %.

## Checkpoints

### Checkpoint 1, 23:33 ACST: wave 34 landed, not yet green

| Task | Attempt | Result |
|---|---|---|
| Task-47 (named constant) | 1 | code as specified, ruff clean; unit tests run by the orchestrator in the gate below |
| Task-49 (map tests from the contract) | 1 | 27 map tests written; two read `publisher_lines`, the pack key is `publishers` (test defect) |
| Task-48 (map v3, top bee tier) | 1 | contract met by its own measurements (96 points, 0 label collisions, legend inside 780); gate RED: 4 browser tests. Three are test defects; one is real: the longer Wadeye sentence pushes the community screen's actions row 6 px past 780 |

Eye review by the orchestrator (the bee's own 360 × 780 shots): structure right, look weak.
Map capped too small (legend ends at 543 of 780), rank numbers unreadable, left-edge labels
clipped, `Reset view` covers Alice Springs, stray stems under dim points in a region view.
These are gaps in the spec, not bee errors. Attempt 2 is one chain: a refinement bee (small
tier, high) with eight numbered fixes, then a test-fix bee, then the gate by the orchestrator.

Quota, measured 23:30: Claude 5-hour 80 % (resets in 1 h 07), weekly 31 %. Codex 5-hour 60 %
(resets in 1 h 14; the top-tier map bee alone cost 37 points), weekly 40 %. Verdict GO; the
orchestrator narrows its own turns (one wake-up per chain) because its own window is the
tighter one.

