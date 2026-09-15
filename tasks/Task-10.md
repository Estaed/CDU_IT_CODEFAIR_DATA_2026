# Task-10: Report-ready figures and tables

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* PRD §4.1 item 3 names the outputs; criteria are file existence, image dimensions and row counts fixed by the spike. The pictures are judged by the team, not by the gate.

**Lane**
- OWNS: `pipeline/figures.py`, `scripts/run_pipeline.py` (additive: call `figures.main()`), `tests/test_figures.py`
- MUST NOT TOUCH: `pipeline/sources/*`, `pipeline/merge.py`, `pipeline/pack.py`, `pipeline/rules.py`, `app/`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-06

## Objective

What Emma, Thanh and Will build the Findings section from: two static NT maps as PNG (one
coloured by telehealth verdict, one by agreement count), the disagreement pattern table with
counts, the "verify on the ground" list with the licensed-site evidence per community, and
verdict counts per service with population affected. Written to `data/out/figures/` and
`data/out/tables/` by the pipeline run.

## Execution Guide

- `pipeline/figures.py` with matplotlib (Agg backend, no display): `map_verdict(table, outline,
  out_png)` and `map_agreement(table, outline, out_png)` at 2000×3200 px (300×480 view box ×
  the same projection as the pack, so the PNG and the app agree), verdict colours and glyph
  shapes taken from `design/ds/design/tokens.json` (read the file; do not retype hex), system
  sans font, legend with glyph + word + count, title in sentence case, source line at the
  bottom naming the sources and dates.
- Tables as CSV in `data/out/tables/`: `disagreement_patterns.csv` (pattern, n, reading, the
  community names), `verify_on_the_ground.csv` (the 11 communities: name, region, population,
  nearest site km, site name, precision, ACCC 4G flag, NTG 2022 flag), `verdict_counts.csv`
  (service, verdict, communities, population sum; population omitted for communities under 100
  per PRD §7, counted as "under 100" rows instead).
- `scripts/run_pipeline.py` calls `figures.main()` after the pack.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/test_figures.py`: both PNGs exist after `figures.main()`, open with Pillow at 2000×3200, and are not a single colour (more than 1,000 distinct pixel values); `disagreement_patterns.csv` sums `n` to 96 and has a row with `n == 31` for "disagree" or the six patterns summing to 31; `verify_on_the_ground.csv` has exactly 11 rows including Baniyala; `verdict_counts.csv` telehealth rows read works 1, degraded 58, fails 11, nodata 26.
- [x] No hex literal in `pipeline/figures.py`: `grep -nE "#[0-9a-fA-F]{3,6}" pipeline/figures.py` prints nothing (colours are read from `tokens.json`).
- [x] `grep -n "vulnerable\|disadvantaged\|at-risk\|underserved" data/out/tables/*.csv pipeline/figures.py` prints nothing.

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `48c8ab0`; 7 new unit tests). Advisory, for the team's eye: both PNGs draw every community as a hollow circle rather than the verdict glyph shapes, and the legend sits over the south-west corner of the outline. Neither is in the DoD.
