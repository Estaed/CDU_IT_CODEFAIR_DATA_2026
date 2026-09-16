# Task-03: ACCC source — carrier predicted coverage polygons 2025

Status: DONE (verify-task, 2026-09-13; gate GREEN on main at integration: ruff clean, 59 unit + 1 browser test; regression 96 rows x 13 columns against the fixture, 0 differences, on the real KMLs; cold parse 3,531 s once, warm run 6.8 s; mutations: km-per-degree red, contains->touches red, REQUIRED emptied red, MOCN-as-fourth-carrier unobservable because TPG 4G is 0 for all 96)

> **Execution:** agent `claude-worker` · effort `medium`
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

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/test_source_accc.py`: 96 rows; the nine coverage flags and `carriers_4g_count` equal the fixture for all 96; Wadeye `telstra_4g_2025 == 1`, Baniyala `carriers_4g_count == 0` and `dist_km_telstra_4g == 16.367`.
- [x] The test runs under 120 s on this machine against the raw KMLs, or reads a cached intermediate the module writes to `data/out/cache/` and invalidates by KML mtime; whichever, the DoD names the measured time. Measured 2026-09-13: cold cache 3,531 s for the six KMLs (once), warm cache 6.8 s for the whole module.
- [x] `grep -n "spike" pipeline/sources/accc.py` prints nothing.

## Contract (main loop, 2026-09-13)

Written before delegation; the bee works from this text. Where it is more specific than the
Execution Guide it wins. Oracle figures were counted from `spike/out/accc.csv` and
`spike/out/accc_run.log` on 2026-09-13, not recalled.

**Raw files.** Already moved by the main loop to `data/raw/`: `accc_telstra_4g_outdoor_2025.kml`
(252,569,107 bytes), `accc_optus_4g_outdoor_2025.kml` (1,422,233,412), `accc_tpg_4g_outdoor_2025.kml`
(91,430,470), `accc_mocn_4g_outdoor_2025.kml` (982,143,797), `accc_optus_3g_outdoor_2025.kml`
(20,262,143), `accc_telstra_5g_outdoor_2025.kml` (356,138,494), plus the two `.zip` originals
for Optus 4G and MOCN. The bee never runs the fetch script and never touches the network.

**The parse cost is the design constraint.** The spike's streaming parse took 2,377 s for
Optus 4G and 492 s for Telstra 4G (`spike/out/accc_run.log`), about 50 minutes for the six
files. The DoD's 120 s test is therefore met with the cache the DoD allows: the NT-subset
polygons of each KML are parsed **once** and cached under `data/out/cache/` (gitignored by
the main loop), keyed on the KML's size and mtime. The bee builds the cache once by running the
test; it does not parse twice, and it does not redesign the parser.

**`pipeline/sources/accc.py`**
- `load(kml_dir: Path, communities: pd.DataFrame, cache_dir: Path) -> pd.DataFrame`. Reads
  `kml_dir / f"accc_{key}_outdoor_2025.kml"` for each job key; `communities` from
  `pipeline.sources.bushtel.load`, columns used `bushtel_id`, `lat`, `lon`. All three paths
  explicit; no module-level `ROOT`.
- `JOBS`, in this order and with these output columns: `telstra_4g` -> `telstra_4g_2025`,
  `optus_4g`, `tpg_4g`, `mocn_4g`, `telstra_3g`, `optus_3g`, `telstra_5g`, `optus_5g`, `tpg_5g`
  (same `_2025` suffix). `REQUIRED = ("telstra_4g", "optus_4g", "tpg_4g", "mocn_4g", "optus_3g",
  "telstra_5g")`: the six files present in the 2026-09-12 snapshot. A required file missing ->
  `FileNotFoundError` naming the file and `PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.accc`.
  A non-required file missing -> `-1` in its column (Telstra 3G Outdoor 2025 does not exist on
  the dataset; Optus 5G and TPG 5G exceeded the spike's download budget); present -> parsed.
  The docstring records this, the CKAN package id `4b472a18-d0fa-409c-994a-ab17162bcb90`, the
  licence CC BY 2.5 AU and `Last-Modified: 2025-11-10`.
- Columns, in this order: `bushtel_id` (int), the nine flag columns, `carriers_4g_count`,
  `dist_km_telstra_4g`, `dist_km_optus_4g`, `dist_km_tpg_4g`. No `name` column. Sorted by
  `bushtel_id`, 96 rows. Every non-key column a **string as the spike wrote it**: flags
  `"1"`/`"0"`/`"-1"`; count `str(int)`; distances `str(round(km, 3))` (`"0.0"` inside,
  `"-1.0"` when the file is absent, `"16.367"`).
- `carriers_4g_count = max(t4, 0) + max(o4, 0) + max(max(tp4, 0), max(m4, 0))` (MOCN counts as
  TPG's network, not a fourth carrier).
- Three functions, so the parse and the point tests are testable apart:
  - `parse_nt_polygons(kml_path: Path) -> list[BaseGeometry]`: port of the spike's
    `parse_kml_for_communities` up to and including polygon construction, unchanged:
    `lxml.etree.iterparse(path, tag=Placemark, huge_tree=True)`, every `<Polygon>` under the
    Placemark, outer ring + holes via `parse_coords`, ring bbox test against
    `NT_BBOX = (128.9, 138.1, -26.1, -10.8)` (lon_min, lon_max, lat_min, lat_max), `Polygon(outer,
    holes)`, `buffer(0)` when invalid, empty dropped, `clear_element` after each Placemark.
  - `nt_polygons(kml_path: Path, cache_dir: Path) -> list[BaseGeometry]`: returns the cached
    list when `cache_dir / f"{kml_path.stem}.nt.pkl"` exists and its recorded `size` and
    `mtime_ns` equal `kml_path.stat()`; otherwise calls `parse_nt_polygons`, writes the cache,
    returns. Cache file: `pickle` of `{"kml": kml_path.name, "size": int, "mtime_ns": int,
    "polygons": list[bytes]}` with `shapely.to_wkb` / `shapely.from_wkb`. `cache_dir` created
    if missing.
  - `point_results(polygons, communities) -> tuple[dict[int, int], dict[int, float]]`:
    `inside[bushtel_id]` 1 when any polygon whose bounds contain the point `contains` it;
    `dist_km[bushtel_id]` `0.0` when inside, else `STRtree(polygons).nearest(pt)` distance in
    degrees `* 111.0` (the spike's flat-earth approximation, kept because the fixture holds it;
    say so in the docstring), `-1.0` when the file had no NT polygon at all.
- Imports: `pickle`, `pathlib`, `lxml.etree`, `shapely`, `shapely.geometry`, `shapely.strtree`,
  `pandas`. Nothing from `pipeline.sources`, `pipeline.pack`, `pipeline.rules`, `spike`,
  `requests`. `grep -n "spike" pipeline/sources/accc.py` prints nothing.

**`pipeline/fetch/accc.py`**
- The only module that talks to `data.gov.au` for the ACCC release. `main()` calls
  `package_show` for the package id, finds each `Coverage map - <MNO> - <tech> - Outdoor - 2025`
  resource for the nine jobs (MNO names `Telstra`, `Optus`, `TPG`, `Optus-TPG MOCN`), streams
  it to `data/raw/accc_<key>_outdoor_2025.<kml|zip>` (skip when present at the declared size,
  `.part` then rename), extracts the `.kml` member of a zip next to it, and prints one line per
  job: downloaded, skipped, or `not on the dataset`. On HTTP 403 it prints the dataset page
  `https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90`, the resource name and
  the target filename, and continues with the next job, so a manual download is one click.
  No download budget: the pipeline fetch is run by hand.
- Runnable as `python -m pipeline.fetch.accc`; not run by any test or by the gate.

**Fixture** (byte-identical copy): `spike/out/accc.csv` -> `tests/fixtures/accc_2026-09-12.csv`.

**`tests/test_source_accc.py`** (unit, no marker)
- `frame` fixture (module scope): `bushtel.load(...)` then `accc.load(ROOT / "data/raw",
  communities, ROOT / "data/out/cache")`. A missing required KML fails with the fetch command in
  the message; no skip.
- `test_shape`: 96 rows, unique `bushtel_id`, columns exactly the fourteen above in order.
- `test_regression_against_fixture`: for every fixture column except `name` and `bushtel_id`,
  all 96 rows: the three distance columns as floats to 3 decimals, everything else as strings;
  first difference in the message.
- `test_oracle`: `carriers_4g_count` counts `"0"` 22, `"1"` 68, `"3"` 6; `telstra_4g_2025`
  `"1"` 74; `optus_4g_2025` `"1"` 6; `mocn_4g_2025` `"1"` 6; `tpg_4g_2025` all `"0"`;
  `telstra_3g_2025`, `optus_5g_2025`, `tpg_5g_2025` all `"-1"`; `telstra_5g_2025` `"1"` 10.
  Wadeye 426: `telstra_4g_2025 == "1"`, `carriers_4g_count == "1"`, `dist_km_telstra_4g == "0.0"`.
  Baniyala 458: `carriers_4g_count == "0"`, `dist_km_telstra_4g == "16.367"`.
- `test_cache_roundtrip` (tmp_path, no raw file): write a small KML by hand with one Placemark
  whose square polygon covers `(130.0, -13.0)`; `nt_polygons(kml, cache)` parses and writes the
  `.nt.pkl`; a second call returns an equal list without parsing (assert by monkeypatching
  `parse_nt_polygons` to raise); `os.utime` the KML and the third call parses again. Then
  `point_results` on a two-row communities frame (one inside, one at `(131.0, -13.0)`) gives
  inside `1`/`0` and distances `0.0` / about `111.0`.
- `test_missing_required_names_fetch_command`: `load(tmp_path, communities, tmp_path /
  "cache")` raises `FileNotFoundError` matching `pipeline.fetch.accc`.
- `test_layer_rules`: no line in `pipeline/sources/accc.py` matches
  `^(import|from) (pipeline\.sources|spike|requests)`.
- Measure and report two wall times for `pytest tests/test_source_accc.py`: cold cache and warm
  cache. The DoD's 120 s applies to the warm run; write both numbers into the DoD line.
