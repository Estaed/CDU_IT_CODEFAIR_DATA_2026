# Task-38: Measured publisher — the National Audit non-alignment tiles as the fifth line

> **Execution:** agent `claude-worker` (opus) · effort `high`
> *Why:* 2026-09-17. A new source module with a spatial join and a new table column that every
> later task of this batch reads; a wrong `not-recorded` / `not-covered` split would poison
> Task-39's labels and Task-40's score, so Opus. Codex is at 100 % until 2026-09-19.

> **Lane:** OWNS `pipeline/sources/audit.py` (new), `pipeline/fetch/audit.py` (new),
> `pipeline/merge.py` (the two new columns only), `pipeline/pack.py` (the fifth publisher line
> in `publisher_lines` and its source key only), `pipeline/provenance.py` (append one registry
> entry), `scripts/run_pipeline.py` (load the audit frame and pass it to `merge`),
> `tests/test_source_audit.py` (new), `tests/test_pack.py` and `tests/test_merge.py` (append
> only), `tests/fixtures/` (a hand-built audit fixture), `data/out/` (regenerated), this file ·
> MUST NOT TOUCH `app/`, `pipeline/rules.py`, `pipeline/changes.py` (Task-42 deletes it),
> `mobile_says` or anything that matches on it (`ACTIONS_BY_PATTERN`, `FILTER_DEFS`,
> `figures.DISAGREEMENT_READINGS`), `design/`, `CLAUDE.md` · GATE `PYTHONUTF8=1
> .venv/Scripts/python scripts/gate.py` · DEPENDS ON none (wave 27, beside Task-42; disjoint
> files except `pipeline/pack.py`, where Task-42 removes the `changes` block and this task
> edits `publisher_lines` only)

## Why

PRD §4.2 fourth batch, first bullet. Every publisher line today is a claim; none is a
measurement. The National Audit of Mobile Coverage drove NT roads and published the tiles
where it found no signal inside a carrier's claimed coverage: 237 NT tiles, all
`Audit Data = "No audit roads coverage"` against `MNO Predicted Coverage = <carrier>`
(`reports/2026-09-12-arena-measured.md` §3.1.5–3.1.7). That is the one sourced "the map is
wrong here" the brief's datasets list can give us, and the fifth line beside the four claims.

## Contract

1. **Fetch.** `pipeline/fetch/audit.py` downloads
   `https://www.infrastructure.gov.au/sites/default/files/documents/national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv`
   (1,205,924 bytes on 2026-09-12) to `data/raw/audit_non_alignment_<date>.csv` through
   `_download.py`, like the other fetchers. Run once by hand; the file is under 10 MB and is
   committed. `FETCH_COMMAND` names the module.
2. **Source module.** `pipeline/sources/audit.py::load(csv_path, communities) -> DataFrame`,
   96 rows keyed on `bushtel_id`, columns `audit5` (`1` when at least one NT non-alignment
   tile polygon lies within 5 km of the community point, `0` when an audited tile lies within
   5 km but none is a non-alignment, empty string otherwise), `audit_nearest_km` (distance to
   the nearest non-alignment tile, one decimal, empty when none within 40 km),
   `audit_carriers` (carriers named on the tiles within 5 km, `/`-joined, empty otherwise),
   `audit_year`. Distances in metres through GDA2020 MGA like `rrl.py`. The `WKT` column is
   the tile polygon; parse with shapely, filter `State == "NT"` before any geometry.
   **`0` is only emitted when the CSV can say a road was audited nearby with no non-alignment**;
   the CSV lists non-alignments only, so in this task `audit5` is `1` or empty. The `0` value
   is defined here so Task-39, which samples the audited roads, can fill it without a schema
   change; this task never writes `0`. Say so in a comment and in the test.
3. **Merge.** `merge.merge` gains the audit frame as a parameter after `ntg_frame`; the two
   columns join on `bushtel_id` and sit after the RRL columns in `_ordered`. `mobile_says`
   and `PUBLISHER_KEYS` are **unchanged**.
4. **Pack.** `pack.publisher_lines` appends a fifth line:
   `{publisher: "National Audit of Mobile Coverage", kind: "measured", says_covered:
   "not-covered" | "not-recorded", detail, source: "National Audit non-alignment 2026-05", date}`.
   `not-covered` detail: `Drive test found no <carriers> signal <km> away inside claimed
   coverage`; `not-recorded` detail: `No audited road within 5 km; the Audit drove roads, not
   communities`. The source key goes through the provenance registry like the others; the
   registry entry carries the URL, the fetch date, the size, `licence: "unstated; request on
   file (OQ2)"` and the attribution line the page shows. The agreement count changes only
   where a `not-covered` line lands (`rules.agreement` already ignores `not-recorded`).
5. **Report table.** `data/out/tables/audit_within_5km.csv`: one row per community with a
   non-alignment tile within 5 km (id, name, carriers, km, year). Written by the source module's
   `write_table` and called from `run_pipeline.py`.

## Tests

`tests/test_source_audit.py`: a hand-built CSV fixture with three tiles (one 2 km from a
fixture community, one 20 km, one in another state) gives `audit5 == "1"`, `audit_nearest_km`
`2.0`, the other-state tile ignored; a community with no tile within 40 km gets empty strings
and `not-recorded`; `0` is never produced by this module (assert the column's value set is
`{"1", ""}` over the real table). `tests/test_pack.py`: every community has exactly five
publisher lines, the fifth has `kind == "measured"`, its `says_covered` is never `covered`,
and `agreement.available` equals the count of lines that are not `not-recorded`.
`tests/test_merge.py`: the two columns exist and `mobile_says` still has four keys.

## Out of the gate

The licence answer (OQ2, Tarik's email); whether the count of communities within 5 km of a
tile is more than a handful (the report says the number either way).

## Status

Status: TODO
