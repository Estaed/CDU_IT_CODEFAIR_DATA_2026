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

## Contract (main loop, 2026-09-13)

Written before delegation; the bee works from this text. Where it is more specific than the
Execution Guide it wins. Oracle figures below were counted from `spike/out/nbn.csv` on
2026-09-13, not recalled.

**Raw files.** Already moved by the main loop: `data/raw/nbn_coverage_fixedline_2024-03-26.zip`
(9,460,437 bytes) and `data/raw/nbn_coverage_wireless_2024-03-26.zip` (378,833,757 bytes). The
bee never runs the fetch script and never touches the network.

**`pipeline/sources/nbn.py`**
- `load(fixedline_zip: Path, wireless_zip: Path, communities: pd.DataFrame) -> pd.DataFrame`.
  `communities` is the frame from `pipeline.sources.bushtel.load`, passed in by the caller; the
  module reads only its `bushtel_id`, `lat`, `lon` columns. Never imported (layer rule 2).
- Columns, in this order: `bushtel_id` (int), `nbn_technology`, `in_fixed_line`,
  `in_fixed_wireless`, `dist_km_nearest_fixed_line`, `dist_km_nearest_fixed_wireless`,
  `fixed_line_attrs`, `fixed_wireless_attrs`. No `name` column: identity lives in the BushTel
  frame and `merge.py` (Task-05) joins on `bushtel_id`. One row per community, sorted by
  `bushtel_id`.
- Every non-key column is a **string exactly as the spike wrote it to CSV** (Task-01
  convention): flags `"0"`/`"1"`; distances `str(round(km, 3))` (`"0.0"` inside, `"4.694"`,
  `"245.26"`, `"1239.699"`); attrs `k=v;k=v` over every non-geometry column of the matched
  polygon, `""` when not inside (Yirrkala: `polygon_id=8NLN-20`).
- Geometry, ported from `spike/lane_nbn.py` without changing the maths: shapefile member found
  inside the zip and read with `geopandas.read_file(f"/vsizip/{zip}/{member}", engine="pyogrio",
  bbox=NT_BBOX)`, `NT_BBOX = (128.9, -26.1, 138.1, -10.8)`; reprojected to EPSG:4326 if needed;
  point-in-polygon with `sjoin(predicate="within")`, first match kept per community; distances
  in **EPSG:3577 (GDA94 / Australian Albers)** via `geometry.distance().min() / 1000`, `0.0`
  when inside. The CRS choice goes in the module docstring: 3577 because the fixture was
  computed in it, and one CRS for the whole NT beats a per-zone split for a 3-dp regression.
- Technology: `FIXED_LINE` if in fixed line, else `FIXED_WIRELESS` if in fixed wireless, else
  `SATELLITE_RESIDUAL`.
- Build a list of dicts and construct the frame once (pandas 3, copy-on-write).
- Missing zip: raise `FileNotFoundError` whose message names the file and the fetch command
  `PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.nbn`. Never skip, never fall back.
- Imports: `zipfile`, `pathlib`, `geopandas`, `pandas`, `shapely.geometry.Point`. Nothing from
  `pipeline.sources`, `pipeline.pack`, `pipeline.rules`, `spike`, `requests`, and no direct
  `pyogrio` import (geopandas calls it). `grep -n "spike" pipeline/sources/nbn.py` prints nothing.

**`pipeline/fetch/nbn.py`**
- The only module that talks to `data.gov.au` for NBN. `main()` streams the two zips named in the
  `spike/lane_nbn.py` docstring (dataset `9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e`, CC BY 4.0) to
  `data/raw/<zip_name>`, skipping a file already present at its expected size, writing to a
  `.part` file and renaming on completion. `requests` with a timeout and `raise_for_status`.
- Runnable as `python -m pipeline.fetch.nbn`; not run by any test or by the gate.

**Fixture** (byte-identical copy): `spike/out/nbn.csv` -> `tests/fixtures/nbn_2026-09-12.csv`.

**`tests/test_source_nbn.py`** (unit, no marker)
- `frame` fixture (module scope): `bushtel.load(ROOT / "data/raw/bushtel_community_detail_2026-09-12.json")`
  then `nbn.load(FIXEDLINE_ZIP, WIRELESS_ZIP, communities)`. A missing raw file fails the test
  with the fetch command in the message; it does not skip.
- `test_shape`: 96 rows, `bushtel_id` unique, columns exactly the eight above in order.
- `test_regression_against_fixture`: `csv.DictReader` over the fixture; for every fixture
  column except `name` and `bushtel_id`, compare all 96 rows: distance columns as floats to
  3 decimals (`abs(a - b) < 0.0005`), every other column as strings. Report the first
  differing `(id, column, expected, got)` in the assertion message.
- `test_distribution`: `nbn_technology` counts `SATELLITE_RESIDUAL` 95, `FIXED_LINE` 1,
  `FIXED_WIRELESS` 0; Yirrkala 576: `FIXED_LINE`, `in_fixed_line == "1"`,
  `dist_km_nearest_fixed_line == "0.0"`, `fixed_line_attrs == "polygon_id=8NLN-20"`; Wadeye
  426: `SATELLITE_RESIDUAL`.
- `test_missing_zip_names_fetch_command`: `load(tmp_path / "nope.zip", WIRELESS_ZIP, communities)`
  raises `FileNotFoundError` matching `pipeline.fetch.nbn`.
- `test_layer_rules`: the text of `pipeline/sources/nbn.py` has no line matching
  `^(import|from) (pipeline\.sources|spike|requests)`.
- Measure and report the wall time of `pytest tests/test_source_nbn.py` (the wireless
  shapefile is 653 MB inside its zip; the bbox read is the cost).
