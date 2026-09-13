"""Re-fetch the ACMA RRL bulk extract that ``pipeline.sources.rrl`` reads.

The only module in the repository that talks to acma.gov.au. Run by hand, never by a test or
the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.rrl

Streams the daily extract (about 67 MB; the URL answers 301 to cdn.acma.gov.au) to
``data/raw/spectra_rrl_<today>.zip`` through a ``.part`` file, renamed only once complete.

Source: https://web.acma.gov.au/rrl/spectra_rrl.zip, landing page
https://www.acma.gov.au/radiocomms-licence-data. Attribution: "Based on Australian
Communications and Media Authority information."
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
RRL_URL = "https://web.acma.gov.au/rrl/spectra_rrl.zip"
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 300
CHUNK_BYTES = 1024 * 1024


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / f"spectra_rrl_{date.today().isoformat()}.zip"
    part = dest.with_suffix(dest.suffix + ".part")
    with requests.get(
        RRL_URL, headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS, allow_redirects=True
    ) as response:
        response.raise_for_status()
        with part.open("wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_BYTES):
                if chunk:
                    f.write(chunk)
    part.replace(dest)
    print(f"wrote {dest} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
