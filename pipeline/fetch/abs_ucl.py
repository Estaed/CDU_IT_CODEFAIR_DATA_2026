"""Fetch the ABS UCL boundary that ``pipeline.layers`` reads for the five town centroids.

The only module in the repository that talks to abs.gov.au for the towns layer. Run by hand,
never by a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_ucl

Downloads the CC BY 4.0 ABS ASGS Edition 3 (2021) Urban Centres and Localities (UCL) digital
boundary shapefile, zipped, to ``data/raw/abs_ucl_2021_shp.zip`` -- same page and licence as
``pipeline.fetch.abs_sa3`` and ``pipeline.fetch.abs_boundary``. Idempotent: a file already
present is skipped.
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
    "access-and-downloads/digital-boundary-files/UCL_2021_AUST_GDA2020_SHP.zip"
)
DEST_NAME = "abs_ucl_2021_shp.zip"

# Duplicated in pipeline.layers so the pack build never imports this module (layer rule 3).
FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_ucl"


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
