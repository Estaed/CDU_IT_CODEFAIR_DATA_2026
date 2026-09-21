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

### Checkpoint 4, 01:43 ACST: chain 4 green and committed; audit launched; push still held

Gate exit 0 (orchestrator): 212 unit + 100 browser, HTML 978,941, pack 506,433, no mojibake
left in `docs/FINDINGS.md`. Task-50's line reads 17 of 96, 1,140 people, 8 with a health
centre, 79 others. Eye review at 360 × 780: region view labels now sit beside their points;
Sources lens reads at a glance (3 / 30 / 63).

Emulator (`terra_nt`, Chrome, 412 px wide; `reports/shots/2026-09-22-map-v3-emulator.png`):
works, legend visible, but at this width two label problems the 360 px tests do not see:
"Maningrida" is placed left of marker 6 and reads as marker 7's name; "Numbulwar" overlaps
the town label "Katherine". Rule to add in the fix wave: a label may not overlap ANY other
label (towns included) and may not sit nearer to another tier-1 marker than to its own; else
it is hidden (the list under the map carries every name). The push waits for that.

Read-only audit bee launched (small tier, high, `--sandbox read-only`): wording, consistency,
accessibility, empty and error states, 360 px overflow, map misreadings, judging criteria;
at most 20 ranked defects, features excluded.

### Checkpoint 5, 01:55 ACST: audit triaged, fix wave launched

Audit (`reports/2026-09-22-audit.md`): 20 findings. Accepted as defects, 17 plus the label
rule from the emulator review: F1 to F5, F19, F20 (silent or raw failure states), F7 to F10
(accessibility), F11 (label collisions), F12 to F14, F18 and the app part of F15 (wording).
Declined: F6 (tab semantics are right but every browser test keys on `[role=tab]`; too wide
for an unattended night, logged under Later), the intervention words and `DCDD` in F15
(pipeline and report vocabulary; the judges are DCDD), F16 and F17 (analyst-facing evidence
text; transfer diagnostics kept on purpose).

Chain 5: Task-51 (fixes, small tier, high), then Task-52 (tests from the contract, may run
the browser suite because it runs after), then the gate by the orchestrator. A first
attempt at writing the task files failed on a shell quoting error; nothing was written, the
files were then written with the Write tool.

### Checkpoint 6 and closeout, 02:29 ACST

| Task | Attempts | Result | Commit |
|---|---|---|---|
| Task-47 named constant | 1 | green | 730c480 |
| Task-48 map v3 | 4 rounds (1 top tier, 3 small tier) | green; eye review at 360 and 412 wide and in the emulator | 730c480 |
| Task-49 map tests | 1 + two correction rounds | green | 730c480 |
| Task-50 mobile-reach finding | 2 (mojibake in the first) | green | 730c480 |
| Task-51 audit fixes | 2 (row F14 skipped in the first, caught by Task-52) | green | 730c480 |
| Task-52 audit tests | 1 | green | 730c480 |

Final gate by the orchestrator: exit 0, 212 unit + 117 browser, `dist/index.html` 982,131
bytes, pack 506,433 bytes. Pushed to `main` (611a4f0..730c480); Pages workflow queued at push.
Nothing went to `BACKLOG.md`: no task was red twice.

Stopped here on the third stop rule: what the last eye review still finds is taste
("Maningrida" sits left of its marker 6, between 6 and 7; the rule holds, the reading is
merely less comfortable than a right-hand label).

**Awaiting the operator's eye:** the live map on a real phone; the ten-second hand-over test
with three people (the fifth batch's actual pass mark, still not run).

What the night showed about the process, for the next run: (1) three of the four map rounds
were spec gaps the orchestrator could have seen by sketching the screen budget first (height
cap, label rule); (2) the separately written tests caught two real omissions (F14, region
label drift) and one class of defect only an eye caught (a label far from its point), which
then became a DOM-measured test; (3) the top bee tier cost 37 points of the Codex 5-hour
window for round 1 and its result needed the same rework a small-tier bee's would have.

### Correction, 05:11 ACST

The wake lock was held for the whole run: its process printed `held`, slept its six hours and
printed `released` at 05:11, exit 0. At closeout (02:29) the orchestrator looked for that
process with a command-line filter, found nothing, and wrongly concluded it had died at the
background tool's ten-minute limit. The filter did not match; the process was alive. "Not
found" was reported as "gone". Next run: record the process id when the lock is taken and
stop it by id.

