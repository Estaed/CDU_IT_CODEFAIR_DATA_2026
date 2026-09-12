# 20-community spike — 2026-09-12

Kill-criterion test for the D + A combination in `reports/2026-09-12-arena-verdict.md`:
build the per-community capability table for 96 BushTel Major/Minor communities (20 flagged
`spike20=1` in `communities.csv` are the ones reported in detail) and see whether it varies.
If every community is satellite, "covered" by every publisher and fails the same service, the
map is one colour and the concept is dead.

Not the pipeline. Throwaway code, written to be promoted only if Part 2 says so.

## Layout

| Path | What | Written by |
|---|---|---|
| `communities.csv` | 96 Major/Minor communities from BushTel detail snapshot (`data/raw/`): id, name, aliases, type, region, ABS 2021 SA1 population, SA1, lat/lon, `spike20` flag. **Shared read-only input for every lane.** | main loop |
| `raw/` | Downloads (gitignored). Re-fetch from the URLs below. | lanes |
| `lane_nbn.py` → `out/nbn.csv` | NBN technology per community by CC-BY footprint | lane NBN |
| `lane_accc.py` → `out/accc.csv` | Carrier predicted coverage per community, ACCC 2025 KML | lane ACCC |
| `lane_rrl_ntg.py` → `out/rrl.csv`, `out/ntg.csv` | ACMA licensed cellular sites near each community; NT Government 2019/2021/2022 lists matched by name | lane RRL |
| `lane_bushtel.py` → `out/bushtel.csv` | Services present per community (BushTel), mobile/internet capability flags | main loop |
| `thresholds.csv` | Service requirements with source URL and date | main loop |
| `merge.py` → `out/capability_table.csv` | The joined table, one row per community, plus service verdicts | main loop |

Every `out/*.csv` keys on `bushtel_id` and carries all 96 rows, even when the value is "not
found" — an absent row and a negative result must not look the same.

## Sources

| Source | URL | Licence |
|---|---|---|
| NBN fixed-line footprint (2024-03-26) | `https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/nbn_coverage_fixedline_2024-03-26.zip` | CC BY 4.0 |
| NBN fixed-wireless footprint (2024-03-26) | `https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/nbn_coverage_wireless_2024-03-26.zip` | CC BY 4.0 |
| ACCC Mobile Infrastructure Report data release | CKAN package `4b472a18-d0fa-409c-994a-ab17162bcb90` on data.gov.au; resources `Coverage map - <MNO> - <tech> - Outdoor - 2025` | CC BY 2.5 AU |
| ACMA Register of Radiocommunications Licences | `https://web.acma.gov.au/rrl/spectra_rrl.zip` (301 → cdn.acma.gov.au) | ACMA licence: derivatives and their redistribution permitted |
| NT Government mobile coverage lists 2019 / 2021 / 2022 / small cell | data.nt.gov.au CKAN, names in `reports/2026-09-12-arena-reconcile.md` §4.1 | CC BY |
| BushTel community profiles | `data/raw/bushtel_community_detail_2026-09-12.json` (snapshot) | TBD, © NTG |

Python: `.venv/Scripts/python.exe` (uv, Python 3.13; geopandas 1.1.4, shapely 2.1.2, pyogrio
0.13.0, pandas 3.0.5, lxml, openpyxl, requests). Run every script from this folder's parent
(the project root) with `PYTHONUTF8=1`.
