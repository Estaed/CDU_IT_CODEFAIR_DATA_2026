"""Re-fetch the Mobile Black Spot Program bulk extract that ``pipeline.sources.mbsp`` reads.

The only module in the repository that talks to data.gov.au for MBSP. Run by hand, never by a
test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.mbsp

Downloads the CC BY 4.0 ``MBSP - All Funded Base Stations.zip`` (297,168 bytes on 2026-09-12,
``reports/2026-09-12-arena-failure.md`` section 1.4) to ``data/raw/mbsp_funded_<today>.zip``.
The file is small and ``data/raw/`` is gitignored, so this runs once; a snapshot already on
disk is left alone.

Source: https://data.gov.au/data/dataset/mobile-black-spot-program-mbsp, licence CC BY 4.0.
The attribution line is in ``pipeline.provenance``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import requests

from pipeline.fetch._download import stream_to_file

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
URL = (
    "https://data.gov.au/data/dataset/2d988915-1192-4f50-92d5-891efc0ba612/resource/"
    "28c8b5c8-9b46-4b61-ad19-84c6dc6483d0/download/mbsp-all-funded-base-stations.zip"
)
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 300
PATTERN = "mbsp_funded_*.zip"
EXPECTED_BYTES = 297_168


def download() -> Path:
    existing = sorted(RAW.glob(PATTERN))
    if existing:
        dest = existing[-1]
        print(f"already downloaded: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest

    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / f"mbsp_funded_{date.today().isoformat()}.zip"
    print(f"downloading {URL} ...")
    with requests.get(URL, headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS) as response:
        response.raise_for_status()
        size = stream_to_file(response, dest)
    print(f"wrote {dest} ({size:,} bytes)")
    if size != EXPECTED_BYTES:
        print(f"note: {size:,} bytes, not the {EXPECTED_BYTES:,} recorded on 2026-09-12")
    return dest


def main() -> None:
    download()


if __name__ == "__main__":
    main()
