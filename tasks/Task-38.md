# Task-38: Measured publisher — the National Audit non-alignment tiles as the fifth line

**Status: DONE** — verified 2026-09-17 (main loop: gate green, 154 unit + 85 browser; mutation: worst-seed budget 2.5 → 2.0 × K turns `test_seeded_drop_completes_within_budget[loss10]` red, restored; `NEAR_M` 5 km → 500 m turns `test_oracle` red, restored. `data/raw/audit_non_alignment_2026-09-17.csv` stays gitignored like every raw file; the fetcher re-creates it.)

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

Status: IMPLEMENTED (2026-09-17, claude-worker opus) — awaiting verify-task

**Gate green.** Two browser transfer-budget assertions first failed because the pack grew past
a 750-byte block boundary (K 24 -> 25); Tarik decided that question the same day and the
decision is applied. See "Gate" below.

### What landed

- `pipeline/fetch/audit.py` (new): `download()` / `main()`, streams the CSV through
  `_download.stream_to_file` to `data/raw/audit_non_alignment_2026-09-17.csv`, skipping a
  snapshot already on disk. Run once by hand: 1,205,924 bytes, exactly the size
  `reports/2026-09-12-arena-measured.md` S3.1.5 records.
- `pipeline/sources/audit.py` (new): `FETCH_COMMAND`, `_require`, `tiles()` (NT filter before
  any geometry, which also drops the repeated header row), `load()` (96 rows keyed on
  `bushtel_id`, columns `audit5`, `audit_nearest_km`, `audit_carriers`, `audit_year`),
  `write_table()`. Distances are metres in GDA2020 MGA zone 52 (EPSG:7852) west of 132 deg E
  and zone 53 (EPSG:7853) east of it; cross-checked against EPSG:3577 Albers, agreeing within
  10 m on all three hits. `"0"` is documented in the module docstring and asserted never to be
  written (Task-39 fills it).
- `pipeline/merge.py`: `merge()` takes `audit` after `ntg`; the frame joins between `rrl` and
  `ntg` so its columns sit after the RRL block in `_ordered`. `mobile_says`, `PUBLISHER_KEYS`
  and `mobile_publishers_available` (still `4`) are untouched.
- `pipeline/pack.py`: `publisher_lines` appends the fifth line, `kind: "measured"`,
  `source: "National Audit non-alignment 2026-05"`; every figure goes through `rules.fig`
  (the 5 km radius through `rules.LICENSED_RADIUS_KM`, as the ACMA line does).
- `pipeline/provenance.py`: one registry entry `audit_non_alignment_2026_05`, URL, date
  published 2026-05-27, `licence: "unstated; request on file (OQ2)"`, attribution
  "National Audit of Mobile Coverage, Department of Infrastructure, Transport, Regional
  Development, Communications, Sport and the Arts". PROVENANCE.md picks up the fetch date and
  size from the file itself.
- `scripts/run_pipeline.py`: loads the audit frame, passes it to `merge`, writes
  `data/out/tables/audit_within_5km.csv`.
- Tests: `tests/test_source_audit.py` (new, 11), `tests/test_merge.py` (+2),
  `tests/test_pack.py` (+3).

### The numbers

- **3 of 96** communities have a non-alignment tile within 5 km, all Telstra:
  **Nauiyu** (id 397) 4.7 km, 2025; **Barunga** (id 580) 1.0 km, 2024; **Jilkminggan**
  (id 593) 3.2 km, 2025. 25 of 96 have a tile within 40 km; the other 71 cells are empty.
  Wadeye's nearest tile is 142 km away.
- **Agreement changed for exactly those 3**, all in the same direction: `available` 4 -> 5,
  `covered` unchanged at 4, so the note flips from "Sources agree" to "Sources disagree".
  Every claim says covered and the government's own drive test found no signal. The other 93
  lines are `not-recorded` and change nothing (`rules.agreement` ignores them).
- 237 NT tiles parsed (Telstra 210, Optus 25, TPG 2), matching the arena report.
- `ruff check --no-cache .`: `All checks passed!`
- Unit tests: 138 -> **154 passing** (+16). Browser tests: 85 before and after (none added),
  all 85 passing.
- `data/out/data_pack.json` 445,601 -> **464,416** bytes (limit 512,000).
  `dist/index.html` 892,413 -> **911,228** bytes (limit 1,048,576).
  `capability_table.csv` 105 -> 109 columns.

### Gate

`PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` first exited **1** at the browser step, on
two assertions that had nothing to do with the audit line and everything to do with the pack
being 19 KB bigger:

- `test_seeded_drop_completes_within_budget[loss10]` (budget 1.6 x K)
- `test_sources_0_to_19_never_delivered_still_completes` (budget 1.75 x K)

The transfer payload's gzip went 17,891 -> 18,373 bytes, i.e. 373 bytes past 24 x 750, so
**K went 24 -> 25**. Measured on the built page, frames actually needed (fixed seed 20260915):

| scenario | budget | K=24 (before) | K=25 (after) |
|---|---|---|---|
| 10 % loss | 1.6 x K | 1.29 x | **2.20 x** |
| 50 % loss | 2.8 x K | 1.67 x | 1.92 x |
| 70 % loss | 4.5 x K | 1.25 x | 1.40 x |
| sources 0..19 dropped | 1.75 x K | 1.33 x | **1.80 x** |

Across 20 seeds at K=24 and 10 % loss the ratio ranges **1.00 - 1.83** (median 1.31): 3 of 20
(1.71, 1.75, 1.83) would already have failed the 1.6 x K budget before this task. The budget is a
single-seed observation, not a property of the decoder, and it is brittle in K — which the
rest of this batch (Task-39's `claim_reliability`, Task-40's score) will push further.

**Decided by Tarik, 2026-09-17, and applied:** a loss budget is a distribution, not one seed.
Over the twenty fixed seeds `20260915 + s * 7919`, s = 0..19, the median frames-needed ratio
must stay within Part 2's 1.6 / 2.8 / 4.5 x K and the worst seed within 2.5 / 3.5 / 4.5 x K,
every seed completing; the deterministic sources-0..19 scenario moves from 1.75 to 2.0 x K.
Tarik amended Part 2 himself; this lane applied it in `tests/browser/test_transfer.py` and
nowhere else. Observed at K 25: 10 % median 1.44 worst 2.32, 50 % median 1.56 worst 3.24,
70 % median 1.40 worst 2.28, omission 1.80. The three loss tests now run their twenty seeds
inside one page evaluation, so the transfer file still takes about 5 s.

**The gate is green: `scripts/gate.py` exits 0** (154 unit, 85 browser, browser step 36.8 s).

### Deviations from the Contract

1. **`tests/test_provenance.py` (outside OWNS, one line).** `EXPECTED_IDS` is an exact set;
   the contracted registry entry fails `test_sources_shape` without it. Added the new id only.
2. **`tests/browser/test_community.py` (outside OWNS, one line).**
   `.publisher-row` count 4 -> 5, the direct consequence of the fifth line.
3. **`tests/test_pack.py` and `tests/test_merge.py` are not append-only.**
   `test_publisher_order_and_kinds` (kinds list), `test_wadeye_426` (its loop asserted every
   publisher says covered) and `test_columns` / the `merge()` call sites had to change with
   the signature and the fifth line. Nothing was weakened: Wadeye still asserts 4 covered plus
   an explicit `not-recorded` fifth.
4. **No audit fixture file under `tests/fixtures/`.** The hand-built CSV is four rows and is
   written into `tmp_path` by the test, where the tile geometry reads next to the distance it
   is asserted to produce. Nothing else needs it.
5. **The audit frame joins between `rrl` and `ntg`** although its parameter comes after
   `ntg`, so that its columns land after the RRL block as the Contract asks.
