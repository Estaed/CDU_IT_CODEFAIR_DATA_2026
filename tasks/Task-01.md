# Task-01: BushTel source — identity, services present, capability flags

Status: DONE (verify-task, 2026-09-13; gate GREEN: ruff clean, 37 unit + 1 browser test; regression 96 rows x 34 columns, 0 differences)

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* promotion of `spike/lane_bushtel.py` into a module with a fixed output contract; the criterion is a row-for-row regression against the spike's output.

**Lane**
- OWNS: `pipeline/sources/__init__.py`, `pipeline/sources/bushtel.py`, `pipeline/fetch/__init__.py`, `pipeline/fetch/bushtel.py`, `tests/test_source_bushtel.py`, `tests/fixtures/bushtel_2026-09-12.csv`, `tests/fixtures/communities_2026-09-12.csv`
- MUST NOT TOUCH: `pipeline/rules.py`, `pipeline/pack.py` (Task-00), `pipeline/sources/nbn.py` (Task-02), `pipeline/sources/accc.py` (Task-03), `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py` (Task-04), `spike/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-00

## Objective

The base frame every other source joins onto: the 96 BushTel Major/Minor communities with id,
name, aliases, type, region, SA1, population, coordinates, and the services present as Y/N/U
flags. Also the fetch script that produced the frozen snapshot, so `PROVENANCE.md` (Task-05) can
name it and a later re-fetch is one command.

## Execution Guide

- `pipeline/sources/bushtel.py`: `load(detail_path, communities_path) -> pandas.DataFrame` with
  one row per community keyed on `bushtel_id`, columns exactly as `spike/out/bushtel.csv` plus the
  identity columns of `spike/communities.csv`. Port the `SERVICE_COLUMNS` map, the WiFi-hours and
  road-season regexes from `spike/lane_bushtel.py`; free-text columns (`wifi_comment`,
  `road_access_comment`, `stand_comment`, `mobile_phone_comment`, `internet_comment`) stay in the
  frame (the pipeline may hold them; the pack decides what ships, Task-00). Date column
  `profile_last_updated` converted to ISO here, once.
- `pipeline/fetch/bushtel.py`: the only module that talks to `bushtel.nt.gov.au`; writes
  `data/raw/bushtel_communities_<date>.json` and `data/raw/bushtel_community_detail_<date>.json`.
  Port from the spike's fetch (see `spike/lane_bushtel.py` header and `../AI Challenge 2026/`
  fetch script if the spike calls it). Not run by tests.
- Snapshot: `data/raw/bushtel_community_detail_2026-09-12.json` already exists (20.7 MB,
  gitignored). Tests read it; if it is absent the test fails with a message naming the fetch
  command, it does not skip.
- Fixtures: copy `spike/out/bushtel.csv` and `spike/communities.csv` to `tests/fixtures/` with
  the date suffix; the regression compares against the fixture, not against `spike/`.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/test_source_bushtel.py`: `load()` returns exactly 96 rows, unique `bushtel_id`, and equals `tests/fixtures/bushtel_2026-09-12.csv` joined with `communities_2026-09-12.csv` on every shared column (string compare after ISO date conversion).
- [x] Wadeye row: `svc_health_centre == "Y"`, `svc_wifi == "Y"`, `road_seasonal_cut == 1`, `profile_last_updated == "2026-07-03"`; Baniyala row: `svc_mobile_phone == ""`, `profile_last_updated == "2025-08-06"`.
- [x] `grep -rl "import requests" pipeline | grep -v pipeline/fetch/` prints nothing.
- [x] `pipeline/sources/bushtel.py` imports nothing from `pipeline.sources` or `spike`.

## Contract (main loop, 2026-09-13)

Written before delegation; the implementation bee and the test bee work from this text.
Where it is more specific than the Execution Guide it wins.

**One departure from the Execution Guide, decided by the main loop:** `load` takes the detail
snapshot only. `data/raw/bushtel_community_detail_2026-09-12.json` carries every identity field
(`DefaultName`, `AliasNamesString`, `CommunityTypeName`, `NTRegionName`, `Population`, `Sa1Code`,
`Point`, `LastUpdated.Profile`), so `spike/communities.csv` was itself derived from it; feeding a
hand-made CSV back into the pipeline would make it a second source of truth. The CSV survives only
as the regression fixture.

**`pipeline/sources/bushtel.py`**
- `load(detail_path: Path) -> pandas.DataFrame`. Reads the JSON list, keeps records whose
  `CommunityTypeName` is `Major` or `Minor` (59 + 37 = 96), sorted by `bushtel_id`.
- Columns, in this order: `bushtel_id` (int), `name`, `aliases`, `community_type`, `nt_region`,
  `population_abs2021`, `sa1_code`, `lat`, `lon`, then every column of `spike/out/bushtel.csv`
  after `name` in the same order (`cap_mobile` … `profile_last_updated`).
- Identity mapping: `name` = `DefaultName`; `aliases` = `AliasNamesString` normalised to the
  fixture's form (compare against `spike/communities.csv`; if the fixture's alias text cannot be
  reproduced from any field of the record, say so in the report instead of hand-patching);
  `community_type` = `CommunityTypeName`; `nt_region` = `NTRegionName`; `population_abs2021` =
  `Population` (int); `sa1_code` = `Sa1Code`; `lat` = `Point.Latitude`, `lon` = `Point.Longitude`.
- Service, capability, comment, `road_seasonal_cut` and `service_types_listed` columns: port
  `SERVICE_COLUMNS`, `COMMENT_COLUMNS`, `SEASONAL` and `strip_html` from `spike/lane_bushtel.py`
  unchanged. `profile_last_updated` = `LastUpdated.Profile` converted from
  `dd/mm/yyyy, hh:mm:ss AM` to `yyyy-mm-dd` here, once; empty stays empty.
- All non-identity columns are strings exactly as the spike wrote them to CSV (`Y`/`N`/`U`/``,
  `0`/`1` for the `cap_*` and `road_seasonal_cut` ints, the comment text); build a list of dicts
  and construct the frame once (pandas 3, copy-on-write: no chained assignment).
- Missing snapshot: raise `FileNotFoundError` whose message names the fetch command
  `PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel`. Never skip, never fall back.
- Imports: `json`, `re`, `pathlib`, `pandas`. Nothing from `pipeline.sources`, `pipeline.pack`,
  `pipeline.rules`, `spike`, `requests`.

**`pipeline/fetch/bushtel.py`**
- The only module that talks to `bushtel.nt.gov.au`. `main()` fetches the community list and one
  detail record per Major/Minor community, writes `data/raw/bushtel_communities_<date>.json` and
  `data/raw/bushtel_community_detail_<date>.json` (`<date>` = today, ISO) in the same shape as the
  2026-09-12 snapshots (a JSON list each). Endpoints and the polite delay: read
  `../AI Challenge 2026/scripts/fetch_raw_sources.py` and the header of `spike/lane_bushtel.py`.
  `requests` with a timeout, `raise_for_status`, one `time.sleep` between detail calls.
- Runnable as `python -m pipeline.fetch.bushtel`; not run by any test or by the gate.

**Fixtures** (test bee copies, byte-identical): `spike/out/bushtel.csv` ->
`tests/fixtures/bushtel_2026-09-12.csv`; `spike/communities.csv` ->
`tests/fixtures/communities_2026-09-12.csv`.

**`tests/test_source_bushtel.py`** (unit, no marker)
- `frame` fixture: `bushtel.load(ROOT / "data/raw/bushtel_community_detail_2026-09-12.json")`;
  if the file is missing the test fails (it does not skip).
- `test_shape`: 96 rows, `bushtel_id` unique, columns start with the nine identity columns in
  order.
- `test_regression_against_fixtures`: read both fixtures with `csv.DictReader`, join on
  `bushtel_id`, and for every column present in both the fixture join and the frame (all but
  `spike20`) compare as strings for all 96 rows; the fixture's `profile_last_updated` is converted
  to ISO by the test with its own tiny parser before comparing. Report the first differing
  (id, column, expected, got) in the assertion message.
- `test_wadeye_and_baniyala`: Wadeye 426 `svc_health_centre == "Y"`, `svc_wifi == "Y"`,
  `road_seasonal_cut == "1"`, `profile_last_updated == "2026-07-03"`, `nt_region == "TOP END"`,
  `population_abs2021 == 2259`; Baniyala 458 `svc_mobile_phone == ""`, `profile_last_updated ==
  "2025-08-06"`.
- `test_missing_snapshot_names_fetch_command`: `load(tmp_path / "nope.json")` raises
  `FileNotFoundError` whose message contains `pipeline.fetch.bushtel`.
- `test_layer_rules`: the text of `pipeline/sources/bushtel.py` has no line matching
  `^(import|from) (pipeline\.sources|spike|requests)`; `grep`-equivalent over `pipeline/` finds
  `import requests` only under `pipeline/fetch/`.
