# Task-02: NBN source — fixed-line and fixed-wireless footprints

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* promotion of `spike/lane_nbn.py`; the criterion is a regression against the spike's `nbn.csv` for all 96 rows.

**Lane**
- OWNS: `pipeline/sources/nbn.py`, `pipeline/fetch/nbn.py`, `tests/test_source_nbn.py`, `tests/fixtures/nbn_2026-09-12.csv`
- MUST NOT TOUCH: `pipeline/sources/bushtel.py` (Task-01), `pipeline/sources/accc.py` (Task-03), `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py` (Task-04), `pipeline/rules.py`, `pipeline/pack.py`, `spike/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-01

## Objective

Per community: which NBN footprint contains the point (fixed line, fixed wireless, or neither →
satellite residual) and the distance in km to the nearest fixed-line and fixed-wireless polygon.
This is the D-half of the capability row (PRD §5 "Fixed access").

## Execution Guide

- `pipeline/sources/nbn.py`: `load(fixedline_zip, wireless_zip, communities) -> DataFrame` with
  the columns of `spike/out/nbn.csv` (`nbn_technology`, `in_fixed_line`, `in_fixed_wireless`,
  `dist_km_nearest_fixed_line`, `dist_km_nearest_fixed_wireless`, `fixed_line_attrs`,
  `fixed_wireless_attrs`), keyed on `bushtel_id`. Read the zips with `geopandas.read_file`
  (pyogrio engine), project to a metre CRS (GDA2020 MGA zone 52/53 by longitude, or EPSG:3577
  Australian Albers for a single CRS; pick one and record it in the module docstring) before
  distances. `communities` is the frame from `pipeline.sources.bushtel.load` passed in, not
  imported (layer rule 2).
- `pipeline/fetch/nbn.py`: downloads the two CC BY 4.0 zips named in `spike/README.md` to
  `data/raw/nbn_coverage_fixedline_2024-03-26.zip` and `..._wireless_2024-03-26.zip`. Move the
  existing files from `spike/raw/` to `data/raw/` (both gitignored; sizes over 10 MB).
- Fixture: `spike/out/nbn.csv` → `tests/fixtures/nbn_2026-09-12.csv`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_source_nbn.py`: 96 rows; `nbn_technology` equals the fixture for all 96 (95 `SATELLITE_RESIDUAL`, Yirrkala `FIXED_LINE`); distances equal the fixture to 3 decimals.
- [ ] The module reads only the two raw zips and the communities frame; `grep -n "spike" pipeline/sources/nbn.py` prints nothing.
- [ ] Missing raw files fail the test with the fetch command in the message; no skip.
