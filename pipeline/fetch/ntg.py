"""Re-fetch the NT Government coverage spreadsheets that ``pipeline.sources.ntg`` reads.

The only module in the repository that talks to data.nt.gov.au. Run by hand, never by a test
or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.ntg

Resolves each package through the CKAN ``package_show`` API (resource URLs are not hardcoded),
takes its first XLSX resource and writes ``data/raw/ntg_<key>.xlsx``.

Source: https://data.nt.gov.au (Northern Territory Government open data, CC BY); packages and
layouts in reports/2026-09-12-arena-reconcile.md S4.1.
"""

from __future__ import annotations

from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
CKAN_PACKAGE_SHOW = "https://data.nt.gov.au/api/3/action/package_show"
NTG_PACKAGES = {
    "2019": "list-of-remote-communities-with-mobile-coverage",
    "2021": "remote-communities-with-mobile-coverage",
    "2022": "mobile-phone-coverage-in-remote-areas-of-the-nt",
    "smallcell": "remote-sites-with-mobile-phone-small-cell-coverage",
}
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 60


def xlsx_url(package_name: str) -> str:
    response = requests.get(
        CKAN_PACKAGE_SHOW,
        params={"id": package_name},
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    resources = response.json()["result"]["resources"]
    xlsx = [r for r in resources if (r.get("format") or "").upper() == "XLSX"]
    if not xlsx:
        raise RuntimeError(f"no XLSX resource in data.nt.gov.au package {package_name}")
    return xlsx[0]["url"]


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for key, package_name in NTG_PACKAGES.items():
        url = xlsx_url(package_name)
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        dest = RAW / f"ntg_{key}.xlsx"
        dest.write_bytes(response.content)
        print(f"wrote {dest} ({len(response.content):,} bytes) from {url}")


if __name__ == "__main__":
    main()
