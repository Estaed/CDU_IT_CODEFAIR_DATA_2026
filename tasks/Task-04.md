# Task-04: ACMA RRL and NT Government sources — licensed sites and the coverage lists

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* promotion of `spike/lane_rrl_ntg.py` into two modules; regression against the spike's `rrl.csv` and `ntg.csv`.

**Lane**
- OWNS: `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py`, `pipeline/fetch/rrl.py`, `pipeline/fetch/ntg.py`, `tests/test_source_rrl.py`, `tests/test_source_ntg.py`, `tests/fixtures/rrl_2026-09-12.csv`, `tests/fixtures/ntg_2026-09-12.csv`
- MUST NOT TOUCH: `pipeline/sources/bushtel.py` (Task-01), `pipeline/sources/nbn.py` (Task-02), `pipeline/sources/accc.py` (Task-03), `pipeline/rules.py`, `pipeline/pack.py`, `spike/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-01

## Objective

Two publisher lines. *Licensed*: from the ACMA Register of Radiocommunications Licences, the
carrier cellular-band transmit sites within 5, 10 and 40 km of each community, the nearest
site's distance, carrier, name and precision (the 5 km radius is the decision in PRD §11;
40 km is true for 96/96 and is kept only as a column). *Listed*: the NT Government 2019, 2021
and 2022 coverage lists and the small-cell list matched by community name, with macro / small
cell / proximity basis, provider, 2019 backhaul type.

## Execution Guide

- `pipeline/sources/rrl.py`: `load(rrl_zip, communities) -> DataFrame` with the columns of
  `spike/out/rrl.csv` (`*_within_5km/10km/40km`, `any_within_*`, `nearest_site_km`,
  `nearest_site_carrier`, `nearest_site_name`, `nearest_site_precision`). Port the licence
  filtering (NT, carrier client names, cellular bands) from `spike/lane_rrl_ntg.py`; also emit
  the per-site table the spike wrote as `rrl_sites_nt.csv` to `data/out/rrl_sites_nt.csv`, the
  report's "verify on the ground" evidence.
- `pipeline/sources/ntg.py`: `load(xlsx_2019, xlsx_2021, xlsx_2022, xlsx_smallcell, communities)
  -> DataFrame` with the columns of `spike/out/ntg.csv` (`ntg2022_*`, `ntg2021_*`, `ntg2019_*`,
  `smallcell_*`). Name matching rules ported verbatim; record every manual alias the spike
  needed in a module-level dict with a comment naming the two spellings.
- `pipeline/fetch/rrl.py` downloads `spectra_rrl.zip` (301 → cdn.acma.gov.au) to
  `data/raw/spectra_rrl_<date>.zip`; `pipeline/fetch/ntg.py` downloads the four data.nt.gov.au
  resources named in `reports/2026-09-12-arena-reconcile.md` §4.1 to `data/raw/ntg_*.xlsx`. Move
  existing files from `spike/raw/`; `data/raw/ntgov_communities_mobile_coverage_2021.xlsx` is
  already there and committed.
- Fixtures from `spike/out/rrl.csv` and `spike/out/ntg.csv`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_source_rrl.py`: 96 rows equal to the fixture; `any_within_5km` sums to the fixture's count; Wadeye `nearest_site_km == 0.064` and `nearest_site_name == "74 Perdjert Street WADEYE"`; Baniyala `nearest_site_km == 0.17`.
- [ ] `tests/test_source_ntg.py`: 96 rows equal to the fixture; `ntg2022_listed` sums to the fixture's count; Wadeye `ntg2022_macro == 1`, `ntg2019_backhaul == "Optic fibre"`; Baniyala `ntg2022_listed == 0`.
- [ ] Neither module imports the other or anything under `spike/`.
