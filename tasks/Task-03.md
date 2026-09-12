# Task-03: ACCC source — carrier predicted coverage polygons 2025

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* promotion of `spike/lane_accc.py`; regression against the spike's `accc.csv`. The KMLs are large (GB range), so the spike's streaming approach is kept, not redesigned.

**Lane**
- OWNS: `pipeline/sources/accc.py`, `pipeline/fetch/accc.py`, `tests/test_source_accc.py`, `tests/fixtures/accc_2026-09-12.csv`
- MUST NOT TOUCH: `pipeline/sources/bushtel.py` (Task-01), `pipeline/sources/nbn.py` (Task-02), `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py` (Task-04), `pipeline/rules.py`, `pipeline/pack.py`, `spike/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-01

## Objective

The *predicted* publisher line: for each carrier and technology in the ACCC Mobile
Infrastructure Report 2025 outdoor polygons (Telstra/Optus/TPG/MOCN 4G, 3G, 5G), whether the
community point is inside, the distance in km to the nearest 4G polygon per carrier, and the
`carriers_4g_count`. Every value labelled a carrier prediction downstream.

## Execution Guide

- `pipeline/sources/accc.py`: `load(kml_dir, communities) -> DataFrame` with the columns of
  `spike/out/accc.csv` (`telstra_4g_2025` … `tpg_5g_2025` as 1/0/−1 where −1 means the file
  was not available, `carriers_4g_count`, `dist_km_telstra_4g`, `dist_km_optus_4g`,
  `dist_km_tpg_4g`). Port the KML reading from `spike/lane_accc.py` (pyogrio or lxml streaming,
  whichever the spike used; keep it). Record the CKAN package id and the `Last-Modified:
  2025-11-10` fact in the docstring; the date flows into provenance in Task-05.
- `pipeline/fetch/accc.py`: lists the CKAN package `4b472a18-d0fa-409c-994a-ab17162bcb90`
  resources `Coverage map - <MNO> - <tech> - Outdoor - 2025`, downloads to
  `data/raw/accc_<mno>_<tech>_outdoor_2025.kml` (unzipping where the resource is a zip). Move the
  existing files from `spike/raw/` to `data/raw/`. The spike noted the page 403s automated fetches
  from some clients; the script must report that clearly and name the manual download path.
- Fixture: `spike/out/accc.csv` → `tests/fixtures/accc_2026-09-12.csv`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_source_accc.py`: 96 rows; the nine coverage flags and `carriers_4g_count` equal the fixture for all 96; Wadeye `telstra_4g_2025 == 1`, Baniyala `carriers_4g_count == 0` and `dist_km_telstra_4g == 16.367`.
- [ ] The test runs under 120 s on this machine against the raw KMLs, or reads a cached intermediate the module writes to `data/out/cache/` and invalidates by KML mtime; whichever, the DoD names the measured time.
- [ ] `grep -n "spike" pipeline/sources/accc.py` prints nothing.
