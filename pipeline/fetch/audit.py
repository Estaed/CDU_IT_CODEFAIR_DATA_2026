"""Re-fetch the National Audit of Mobile Coverage non-alignment CSV.

The only module in the repository that talks to infrastructure.gov.au. Run by hand, never by
a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.audit

Downloads the published non-alignment tiles (1,205,924 bytes on 2026-09-12, date published
27 May 2026) to ``data/raw/audit_non_alignment_<today>.csv``. The file is well under 10 MB
and is committed, so this runs once; a snapshot already on disk is left alone.

Source: https://www.infrastructure.gov.au/sites/default/files/documents/
national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv, linked from the
non-alignments page of the Better Connectivity Plan. The page states no licence
(PRD Open Question 2); the attribution line it carries is in ``pipeline.provenance``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import requests

from pipeline.fetch._download import stream_to_file

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
URL = (
    "https://www.infrastructure.gov.au/sites/default/files/documents/"
    "national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv"
)
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 300
PATTERN = "audit_non_alignment_*.csv"


def download() -> Path:
    existing = sorted(RAW.glob(PATTERN))
    if existing:
        dest = existing[-1]
        print(f"already downloaded: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest

    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / f"audit_non_alignment_{date.today().isoformat()}.csv"
    print(f"downloading {URL} ...")
    with requests.get(URL, headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS) as response:
        response.raise_for_status()
        size = stream_to_file(response, dest)
    print(f"wrote {dest} ({size:,} bytes)")
    return dest


def main() -> None:
    download()


if __name__ == "__main__":
    main()
