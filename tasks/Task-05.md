# Task-05: Merge, provenance, and the pipeline entry point

Status: DONE (2026-09-13, verify-task; gate green, 75 unit + 1 browser tests, run_pipeline 39 s, five mutations caught)

> **Note (2026-09-13, PRD decision log):** the provenance registry also ships inside the pack as a `sources` table in the header keyed by short ids; every `{source, date}` pair on a population, publisher, service-source or flag line becomes a single `src` key. Measured on the Task-00 pack: 288,193 -> 225,841 bytes. `pack_version` stays 1.

> **Decisions (2026-09-13, main loop, before spawning; these bind the lane and the tests):**
> 1. **Pack `sources` table.** The header gains `"sources": {"s1": {...}, ...}`; ids are `s` + a 1-based index over the distinct `(source, date)` pairs sorted by `(source, date)`. Each entry is `{"source": <name>, "date": <date>}` plus `"url"` and `"licence"` where known: from the provenance registry (matched by the registry entry's `pack_source` name) or from `pipeline/thresholds.csv` (`source` -> `source_url`). Every line that carried `source` + `date` (population, publishers, service sources, flags) now carries `"src": "<id>"` instead; `path.rule`/`path.date` stay as they are. Rule-path labels (`"<path word>, spike rule"`) and `"none published"` have no url and are the only entries allowed without one.
> 2. **Provenance registry shape.** `provenance.SOURCES` is a tuple of dicts: `id` (bushtel, nbn_fixedline, nbn_wireless, accc_mir_2025, rrl, ntg_2019, ntg_2021, ntg_2022, ntg_smallcell), `name`, `pack_source` (the exact string the pack uses, or `""`), `url`, `licence`, `attribution`, `pattern` (a glob relative to `data/raw/`), `date` (publication date as the screen footers show it; `ntg_2019` is `"2019"`). `write(out_path, raw_dir)` globs each pattern, adds fetch date (file mtime, ISO date) and byte size per matched file, and fails with a message naming the `FETCH_COMMAND` of the source when a pattern matches nothing. Hand-written URLs come from `spike/README.md` and the fetch modules; BushTel licence text is `"NT Government; reuse terms under Open Question 1 (docs/PRD.md)"` until OQ1 closes.
> 3. **Regression exclusions.** `tests/test_merge.py` compares every column present in both the merged frame and the fixture except `spike20` (spike-only) and `telehealth_reason` (the pipeline writes the rules' reason sentence, the spike wrote a debug string); both named in one `EXCLUDED` tuple with that reason. Verdict mapping: GREEN->works, AMBER->degraded, RED->fails, n-a->nodata.
> 4. **Who writes what.** Implementation and the `test_pack.py`/`test_build.py` updates: one bee, in the main tree (it needs the gitignored `data/raw/` and `data/out/cache/`). `tests/test_merge.py` and `tests/test_provenance.py`: a second bee, from this file only; it never reads the first bee's code. The main loop integrates and runs `verify-task`.
> 5. `data/raw/` was cleaned first: the duplicate `ntgov_communities_mobile_coverage_2021.xlsx` (same MD5 as `ntg_2021.xlsx`) and its data-quality PDF moved to `spike/raw/`. The two ACCC `.zip` archives stay and match the `accc_*_outdoor_2025.*` pattern.

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

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py` from the root, with networking irrelevant (no `requests` import reachable from it), writes the four outputs and exits 0.
- [x] `tests/test_merge.py`: the merged table equals `tests/fixtures/capability_table_2026-09-12.csv` on every shared column for all 96 rows (after verdict-word mapping); telehealth counts are works 1, degraded 58, fails 11, nodata 26; `mobile_sources_disagree` sums to 31; `best_path == "satellite"` for 29 rows.
- [x] `tests/test_provenance.py`: every source id referenced by any pack `source` field exists in `SOURCES`; every `SOURCES` entry has a non-empty url, licence and attribution line; `PROVENANCE.md` lists every file under `data/raw/` and no file that is absent.
- [x] `grep -rnE "^\s*(import|from) .*spike|['\"]spike/" pipeline scripts app tests --include=*.py --include=*.js` prints nothing: no code imports from or opens a path under `spike/`. (Reworded 2026-09-13, Tarik: the literal `grep -rn "spike"` form is unreachable because of the `spike20` column name in the fixture and the "ported from" docstrings in Task-01/04 modules.)
- [x] `data/out/data_pack.json` regenerated from the pipeline table is identical in verdicts and reasons to the Task-00 pack (assert in `test_pack.py`, which now reads the pipeline table).
