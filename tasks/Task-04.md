# Task-04: ACMA RRL and NT Government sources — licensed sites and the coverage lists

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* promotion of `spike/lane_rrl_ntg.py` into two modules; regression against the spike's `rrl.csv` and `ntg.csv`.

**Lane**
- OWNS: `pipeline/sources/rrl.py`, `pipeline/sources/ntg.py`, `pipeline/fetch/rrl.py`, `pipeline/fetch/ntg.py`, `tests/test_source_rrl.py`, `tests/test_source_ntg.py`, `tests/fixtures/rrl_2026-09-12.csv`, `tests/fixtures/ntg_2026-09-12.csv`, `tests/fixtures/rrl_sites_nt_2026-09-12.csv` (added by the main loop 2026-09-13: the site table needs its own oracle)
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

## Contract (main loop, 2026-09-13)

Written before delegation; the bee works from this text. Where it is more specific than the
Execution Guide it wins. Oracle figures were counted from `spike/out/rrl.csv`, `spike/out/ntg.csv`
and `spike/out/rrl_sites_nt.csv` on 2026-09-13, not recalled.

**Raw files.** Already moved by the main loop to `data/raw/`: `spectra_rrl_2026-09-12.zip`
(67,363,362 bytes; the spike's `spectra_rrl.zip`, dated on the move), `ntg_2019.xlsx`,
`ntg_2021.xlsx`, `ntg_2022.xlsx`, `ntg_smallcell.xlsx`. One correction to the Execution Guide:
`data/raw/` is gitignored, so nothing there is committed; `ntgov_communities_mobile_coverage_2021.xlsx`
is byte-identical to `ntg_2021.xlsx` (md5 `43ca644c`) and is left alone for Task-05's provenance
registry to reconcile. The modules read the `ntg_*.xlsx` names. The bee never runs the fetch
scripts and never touches the network.

**Common to both modules**
- `communities` is the frame from `pipeline.sources.bushtel.load`, passed in; `rrl` uses
  `bushtel_id`, `lat`, `lon`; `ntg` also `name` and `aliases`. Neither module imports the other
  or anything from `pipeline.sources`, `pipeline.pack`, `pipeline.rules`, `spike`, `requests`.
- No `name` column in either output frame; identity lives in the BushTel frame. `bushtel_id`
  int, sorted, 96 rows. Every other column a **string exactly as the spike wrote it to CSV**
  (Task-01 convention): flags `"0"`/`"1"`, empty `""`, distances `str(round(km, 3))`
  (`"0.064"`, `"0.17"`, `"5.213"`), ints `str(int)`.
- `haversine_km` and `normalise_name` ported verbatim (each module carries its own copy; the
  two may not share a helper module without a new file outside OWNS).
- Missing raw file: `FileNotFoundError` naming the file and the fetch command
  (`PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.rrl` / `... -m pipeline.fetch.ntg`).
  Never skip.
- Build a list of dicts, construct each frame once (pandas 3, copy-on-write).

**`pipeline/sources/rrl.py`**
- `sites(rrl_zip: Path) -> pd.DataFrame`: the per-site table, columns `site_id`, `lat`, `lon`,
  `name`, `precision`, `carrier_group`, `bands`, `device_count`, ported from
  `build_rrl_sites_nt` without changing the filtering: `CARRIER_KEYWORDS`, `EXCLUDE_SUBSTRINGS`,
  `EXCLUDE_EXACT_NAMES`, `CELLULAR_BANDS_HZ`, `GRANTED_STATUS = "1"`, `DEVICE_TYPE == "T"`,
  `client.csv -> licence.csv -> device_details.csv -> site.csv` streamed from inside the zip with
  `io.TextIOWrapper(..., encoding="utf-8", errors="replace")`, NT sites only, sorted by
  `["carrier_group", "site_id"]` as strings. Oracle: 576 rows; `telstra` 333, `optus` 162,
  `tpg` 81, `jv` 0. `lat`/`lon` floats as read, `device_count` int; when written to CSV the
  file equals the fixture byte for byte.
- `write_sites(frame, path: Path) -> None`: writes that table with `csv.writer(lineterminator="\n")`,
  UTF-8. Task-05's entry point writes `data/out/rrl_sites_nt.csv` with it; no test writes there.
- `load(rrl_zip: Path, communities: pd.DataFrame) -> pd.DataFrame`: calls `sites`, then
  `build_rrl_csv` ported verbatim (haversine to every site of each group, thresholds 5/10/40,
  nearest across all groups, `CARRIER_LABEL` `Telstra` / `Optus` / `TPG/Vodafone` / `Mobile JV`).
  Columns, in this order: `bushtel_id`, then for each group in `telstra, optus, tpg, jv` the
  three `<group>_within_5km/10km/40km`, then `any_within_5km/10km/40km`, `nearest_site_km`,
  `nearest_site_carrier`, `nearest_site_name`, `nearest_site_precision`.
- Docstring: the ACMA licence terms and the attribution line `Based on Australian
  Communications and Media Authority information.` from the spike header; source URL and the
  301 to `cdn.acma.gov.au`; fetch date 2026-09-12.

**`pipeline/sources/ntg.py`**
- `load(xlsx_2019: Path, xlsx_2021: Path, xlsx_2022: Path, xlsx_smallcell: Path,
  communities: pd.DataFrame) -> pd.DataFrame`. `load_2019` / `load_2021` / `load_2022` /
  `load_smallcell` ported verbatim (sheet names `Sheet1`, `Communities with Mobile` +
  `Communities`, `Communities with Mobile`, `Sheet1`; header offsets 3 / 2 / 6 / 3;
  `data_only=True`).
- Matching: `names_norm = {normalise_name(name)} | {normalise_name(a) for a in aliases}` with
  `aliases` comma-split from the frame's `aliases` column; first list row whose normalised name
  is in the set. `MANUAL_ALIASES: dict[str, str] = {}` at module level with a comment saying
  that the 2026-09-12 run matched 60 / 57 / 46 / 2 rows with normalisation and BushTel aliases
  alone, so the dict is empty by measurement, not by omission; it is applied (spike form ->
  BushTel form) before normalisation so a future alias is a one-line addition.
- Columns, in this order: `bushtel_id`, `ntg2022_listed`, `ntg2022_matched_name`,
  `ntg2022_site_type`, `ntg2022_macro`, `ntg2022_small`, `ntg2022_proximity`, `ntg2022_provider`,
  `ntg2022_population`, `ntg2022_coord_dist_km`, `ntg2021_with_mobile_listed`,
  `ntg2021_mobile_phone`, `ntg2021_comment`, `ntg2019_listed`, `ntg2019_backhaul`,
  `ntg2019_provider`, `ntg2019_coord_dist_km`, `smallcell_listed`, `smallcell_provider`. The
  `ntg2022_macro/small/proximity` cells are `""` when not listed, `"0"`/`"1"` when listed;
  `ntg2021_comment` keeps the spreadsheet text as is (community 654 carries an embedded newline;
  `ntg2021_mobile_phone` `Not recorded` comes from the sheet itself).
- Docstring: the four data.nt.gov.au package names, CC BY, fetch date 2026-09-12.

**`pipeline/fetch/rrl.py`** and **`pipeline/fetch/ntg.py`**
- `rrl.main()` streams `https://web.acma.gov.au/rrl/spectra_rrl.zip` (follows the 301) to
  `data/raw/spectra_rrl_<today>.zip`, `.part` then rename, timeout, `raise_for_status`.
- `ntg.main()` calls `https://data.nt.gov.au/api/3/action/package_show` for the four package
  names in `NTG_PACKAGES`, takes the first `XLSX` resource, writes `data/raw/ntg_<key>.xlsx`.
- Each runnable as `python -m pipeline.fetch.<name>`; not run by any test or by the gate. The
  only modules importing `requests` for these sources.

**Fixtures** (byte-identical copies): `spike/out/rrl.csv` -> `tests/fixtures/rrl_2026-09-12.csv`;
`spike/out/ntg.csv` -> `tests/fixtures/ntg_2026-09-12.csv`; `spike/out/rrl_sites_nt.csv` ->
`tests/fixtures/rrl_sites_nt_2026-09-12.csv`.

**`tests/test_source_rrl.py`** (unit, no marker)
- `frame` fixture (module scope): `bushtel.load(...)` then `rrl.load(ROOT /
  "data/raw/spectra_rrl_2026-09-12.zip", communities)`. Missing zip fails with the fetch command;
  no skip.
- `test_shape`: 96 rows, unique ids, columns exactly the twenty above in order.
- `test_regression_against_fixture`: every fixture column except `name` and `bushtel_id`, all
  96 rows, `nearest_site_km` as float to 3 decimals, the rest as strings; first difference in
  the message.
- `test_oracle`: `any_within_5km` sums to 78, `any_within_10km` 83, `any_within_40km` 96;
  `nearest_site_carrier` counts `Telstra` 93, `Optus` 3. Wadeye 426: `nearest_site_km == "0.064"`,
  `nearest_site_name == "74 Perdjert Street WADEYE"`, `nearest_site_carrier == "Telstra"`,
  `nearest_site_precision == "Unknown"`. Baniyala 458: `nearest_site_km == "0.17"`,
  `nearest_site_name == "19 m Mast, Baniyala Community EAST ARNHEM"`.
- `test_sites_table`: `rrl.sites(zip)` has 576 rows; `write_sites` to `tmp_path / "s.csv"`
  produces bytes equal to `tests/fixtures/rrl_sites_nt_2026-09-12.csv`.
- `test_missing_zip_names_fetch_command`: `load(tmp_path / "nope.zip", communities)` raises
  `FileNotFoundError` matching `pipeline.fetch.rrl`.
- `test_layer_rules`: no line in `pipeline/sources/rrl.py` matches
  `^(import|from) (pipeline\.sources|spike|requests)`.
- Measure and report the wall time of `pytest tests/test_source_rrl.py` (`device_details.csv`
  is 385 MB inside the zip).

**`tests/test_source_ntg.py`** (unit, no marker)
- `frame` fixture: `ntg.load(RAW / "ntg_2019.xlsx", RAW / "ntg_2021.xlsx", RAW / "ntg_2022.xlsx",
  RAW / "ntg_smallcell.xlsx", communities)`.
- `test_shape`: 96 rows, unique ids, columns exactly the nineteen above in order.
- `test_regression_against_fixture`: every fixture column except `name` and `bushtel_id`, all
  96 rows, as strings (the fixture was read with `csv.DictReader`, `newline=""`, so the embedded
  newline in row 654 survives); first difference in the message.
- `test_oracle`: `ntg2022_listed` sums to 60, `ntg2022_macro == "1"` 46, `ntg2022_small == "1"`
  3, `ntg2022_proximity == "1"` 12, `ntg2021_with_mobile_listed` 57, `ntg2019_listed` 46,
  `smallcell_listed` 2; `ntg2019_backhaul` counts `Optic fibre` 30, `Microwave radio` 16, `""`
  50. Wadeye 426: `ntg2022_macro == "1"`, `ntg2022_provider == "TELSTRA"`,
  `ntg2019_backhaul == "Optic fibre"`, `ntg2019_provider == "Project 13"`. Baniyala 458:
  `ntg2022_listed == "0"`, `ntg2022_macro == ""`, `ntg2021_mobile_phone == "Not recorded"`.
- `test_missing_xlsx_names_fetch_command`: a `tmp_path / "nope.xlsx"` in place of the 2022 file
  raises `FileNotFoundError` matching `pipeline.fetch.ntg`.
- `test_layer_rules`: neither `pipeline/sources/rrl.py` nor `pipeline/sources/ntg.py` has a line
  matching `^(import|from) (pipeline\.sources|spike|requests)`.
