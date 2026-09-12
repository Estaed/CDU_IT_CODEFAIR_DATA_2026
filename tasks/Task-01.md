# Task-01: BushTel source — identity, services present, capability flags

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

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_source_bushtel.py`: `load()` returns exactly 96 rows, unique `bushtel_id`, and equals `tests/fixtures/bushtel_2026-09-12.csv` joined with `communities_2026-09-12.csv` on every shared column (string compare after ISO date conversion).
- [ ] Wadeye row: `svc_health_centre == "Y"`, `svc_wifi == "Y"`, `road_seasonal_cut == 1`, `profile_last_updated == "2026-07-03"`; Baniyala row: `svc_mobile_phone == ""`, `profile_last_updated == "2025-08-06"`.
- [ ] `grep -rl "import requests" pipeline | grep -v pipeline/fetch/` prints nothing.
- [ ] `pipeline/sources/bushtel.py` imports nothing from `pipeline.sources` or `spike`.
