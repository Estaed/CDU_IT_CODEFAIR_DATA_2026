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

### Checkpoint 2, 00:12 ACST (2026-09-22): map v3 green and committed, push held

Attempt 2 chain (refinement bee, test-fix bee, gate by the orchestrator): **gate exit 0**, 211
unit + 99 browser, HTML 973,211 bytes, pack 506,433. Committed locally. Eye review of
`reports/shots/2026-09-21-map-v3-fix.png`: the map now fills the screen, ranks are legible, the
legend sits above the fold, the selection card works. One factual defect no test caught: the
label "Wurrumiyanga" is drawn about 150 px from its own point, over another label, and
tier-1 markers 2 and 6 sit under labels. A name beside the wrong point is an error of fact, so
the push is held until it is fixed.

Chain 3, launched 00:12, one wake-up: label-adjacency fix (app bee), a DOM-measured label test
written from the contract (test bee), Task-50 (the unreachable-communities finding; it reruns
the pipeline, so it runs serially here), then the gate by the orchestrator.

### Checkpoint 3, 00:57 ACST (2026-09-22): chain 3 back, gate RED on one test, two real defects

| Item | Result |
|---|---|
| Label adjacency (app bee, attempt 1) | rest view fixed (labels 15 to 17 units from their markers; Wurrumiyanga and Milingimbi hidden for lack of room). Region view RED: offsets are in view-box units, so at `region=top-end` label 397 is 72.5 px and 362 is 99.6 px from its marker (limit 40 px + half width) |
| Label test (test bee) | written from the contract, caught the defect above; not bent |
| Task-50 (finding) | numbers right (17 of 96, 1,140 people, 8 with a health centre, 79 others); the generated line carries mojibake for the em dash, typed into `figures.py` |
| Gate (orchestrator) | exit 1: 212 unit green, browser 99 of 100 |

Quota after the 5-hour resets: Claude 0 % / weekly 31 %; Codex 0 % / weekly 42 %. Verdict GO.
Chain 4 launched: the mojibake fix at its source (one separator helper, a test assertion on
U+2014), the on-screen label offset fix, then the gate. One attempt each; a red here goes to
`BACKLOG.md` and the run moves on to the audit.

