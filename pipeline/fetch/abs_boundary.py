"""Re-fetch the ABS state and territory boundary that ``pipeline.outline`` reads.

The only module in the repository that talks to abs.gov.au for the NT outline. Run by hand,
never by a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_boundary

Downloads the CC BY 4.0 ABS ASGS Edition 3 (2021) State and Territory digital boundary
shapefile, zipped, to ``data/raw/abs_ste_2021_shp.zip``. Idempotent: a file already present
is skipped. No GeoPackage was found at the same digital-boundary-files path on 2026-09-13
(one probe, 404), so the shapefile zip is what the pipeline reads.
"""

from __future__ import annotations

from pathlib import Path

import requests

from pipeline.fetch._download import present_at, stream_to_file

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
HEADERS = {"User-Agent": "CDU-ITCodeFair-2026/0.1 (Crosscheck)"}
TIMEOUT_SECONDS = 300

URL = (
    "https://www.abs.gov.au/statistics/standards/"
    "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
    "access-and-downloads/digital-boundary-files/STE_2021_AUST_SHP_GDA2020.zip"
)
DEST_NAME = "abs_ste_2021_shp.zip"

# Duplicated in pipeline.outline so the pack build never imports this module.
FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_boundary"


def download() -> Path:
    dest = RAW / DEST_NAME
    if present_at(dest, None):
        print(f"already downloaded: {dest.name} ({dest.stat().st_size} bytes)")
        return dest

    RAW.mkdir(parents=True, exist_ok=True)
    print(f"downloading {URL} ...")
    with requests.get(URL, headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS) as resp:
        resp.raise_for_status()
        size = stream_to_file(resp, dest)
    print(f"downloaded {size} bytes -> {dest}")
    return dest


def main() -> None:
    download()


if __name__ == "__main__":
    main()
