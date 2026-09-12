# Task-05: Merge, provenance, and the pipeline entry point

> **Execution:** agent `claude-worker` · effort `high` · plan mode **no**
> *Why:* the join and the provenance registry are fully specified by the spike's `merge.py` and Part 2; the criterion is the 96-row regression against the frozen spike table plus a provenance completeness check.

**Lane**
- OWNS: `pipeline/merge.py`, `pipeline/provenance.py`, `scripts/run_pipeline.py`, `tests/test_merge.py`, `tests/test_provenance.py`, `tests/fixtures/capability_table_2026-09-12.csv`, `pipeline/pack.py` (one edit: `INTERIM_TABLE` → `data/out/capability_table.csv`, `SOURCE_DATES` → provenance registry)
- MUST NOT TOUCH: `pipeline/sources/*` (Tasks 01–04), `pipeline/rules.py` (Task-00), `app/`, `scripts/build_app.py`, `spike/` (read `spike/out/capability_table.csv` once, to copy it into `tests/fixtures/`)
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-02, Task-03, Task-04

## Objective

One command from frozen snapshots to the capability table (CSV and XLSX), with a provenance file
that lists every raw source with URL, fetch date, size, licence and attribution line. After this
task the pack no longer reads the spike's table and `spike/` is imported by nothing, read by
nothing.

## Execution Guide

- `pipeline/merge.py`: `merge(bushtel, nbn, accc, rrl, ntg, thresholds) -> DataFrame` joining
  on `bushtel_id` (left join on the BushTel frame, 96 rows always; a missing source row yields
  the "not recorded" value, never a dropped row) and applying `pipeline.rules` per row for
  `mobile_says`, `mobile_sources_covered`, `mobile_sources_disagree`, `best_path`, the four
  verdict columns, `services_failing`, `services_degraded`, `fixed_latency_ms`. Column names as
  `spike/out/capability_table.csv`, plus `best_path`. Verdict words are `works|degraded|fails|
  nodata` (the spike's GREEN/AMBER/RED/n-a are mapped in the regression test, not kept).
- `pipeline/provenance.py`: a `SOURCES` registry (list of dicts: id, name, url, licence,
  attribution line, raw path pattern, `date` field) and `write(out_path, raw_dir)` that fills fetch
  date and byte size from the files on disk and writes `data/out/PROVENANCE.md`. Dates and
  attribution lines are those on `design/screens/*.html` footers. `pack.py` reads source names and
  dates from this registry (delete `SOURCE_DATES`).
- `scripts/run_pipeline.py`: loads the five sources from `data/raw/`, merges, writes
  `data/out/capability_table.csv`, `.xlsx` (openpyxl), `PROVENANCE.md`, then calls
  `pipeline.pack.main()`. No network. Exits non-zero if any raw file is missing, naming the
  fetch script.
- Fixture: copy `spike/out/capability_table.csv` to `tests/fixtures/capability_table_2026-09-12.csv`.
  The regression compares every column the pipeline keeps, all 96 rows, mapping verdict words.
- Update `pipeline/pack.py`: `INTERIM_TABLE` becomes `data/out/capability_table.csv`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root, with networking irrelevant (no `requests` import reachable from it), writes the four outputs and exits 0.
- [ ] `tests/test_merge.py`: the merged table equals `tests/fixtures/capability_table_2026-09-12.csv` on every shared column for all 96 rows (after verdict-word mapping); telehealth counts are works 1, degraded 58, fails 11, nodata 26; `mobile_sources_disagree` sums to 31; `best_path == "satellite"` for 29 rows.
- [ ] `tests/test_provenance.py`: every source id referenced by any pack `source` field exists in `SOURCES`; every `SOURCES` entry has a non-empty url, licence and attribution line; `PROVENANCE.md` lists every file under `data/raw/` and no file that is absent.
- [ ] `grep -rn "spike" pipeline scripts app tests --include=*.py --include=*.js` prints only the fixture-copy comment in `tests/test_merge.py`.
- [ ] `data/out/data_pack.json` regenerated from the pipeline table is identical in verdicts and reasons to the Task-00 pack (assert in `test_pack.py`, which now reads the pipeline table).
