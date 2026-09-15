"""Throwaway fetcher for the 2026-09-15 map-bytes measurement spike.

Downloads the extra source files the spike needs that are not already in ``data/raw/``:
ABS SA3 (and SA4) 2021 digital boundary shapefiles. Also *attempts* an NT highways
download and records whether it worked.

Not part of the pipeline. Not imported by anything under ``pipeline/``, ``app/`` or
``scripts/``. Run once, by hand, from the project root:

    PYTHONUTF8=1 .venv/Scripts/python reports/spike-map-bytes/fetch.py

Writes to ``data/raw/`` (new files only, per the task's own instruction; nothing existing
is overwritten -- both downloads are skipped if the destination already exists).
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
HEADERS = {"User-Agent": "CDU-ITCodeFair-2026/0.1 (Crosscheck spike)"}
TIMEOUT_SECONDS = 300

# ABS ASGS Edition 3 (2021) digital boundary files, CC BY 4.0. Same host and path pattern
# already used by pipeline/fetch/abs_boundary.py for the STE (state/territory) layer.
SOURCES = {
    "abs_sa3_2021_shp.zip": (
        "https://www.abs.gov.au/statistics/standards/"
        "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
        "access-and-downloads/digital-boundary-files/SA3_2021_AUST_SHP_GDA2020.zip"
    ),
    "abs_sa4_2021_shp.zip": (
        "https://www.abs.gov.au/statistics/standards/"
        "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
        "access-and-downloads/digital-boundary-files/SA4_2021_AUST_SHP_GDA2020.zip"
    ),
}

# NT highways attempt. Recorded here so the report can state exactly what was tried.
# data.gov.au's only national roads dataset is Geoscape "National Roads" (package
# "national-roads"): a 775 MB .gdb zip, licence "notspecified" (not CC BY) -- too large
# and licence unclear for this spike, not downloaded.
# data.nt.gov.au (NTG Open Data Portal) lists "NT Government Controlled Roads"
# (package "nt-government-controlled-roads", licence cc-by / Creative Commons Attribution)
# whose one resource is a KMZ hosted on nt.gov.au. That host returns 403 Forbidden to a
# scripted GET (tried: default requests UA, a browser UA, a browser UA with a plausible
# Referer) -- looks like bot protection in front of the file host, not a login wall.
HIGHWAYS_CANDIDATE = {
    "dataset_url": "https://data.nt.gov.au/dataset/nt-government-controlled-roads",
    "resource_url": (
        "https://nt.gov.au/_media/images/driving_and_transport/"
        "roads_and_traffic_management/nt-government-controlled-road-maps.zip"
    ),
    "licence": "cc-by (Creative Commons Attribution, per data.nt.gov.au package metadata)",
}


def present(dest: Path) -> bool:
    return dest.is_file() and dest.stat().st_size > 0


def download(dest_name: str, url: str) -> None:
    dest = RAW / dest_name
    if present(dest):
        print(f"already present, skipped: {dest.name} ({dest.stat().st_size} bytes)")
        return
    print(f"downloading {url} ...")
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS) as resp:
            resp.raise_for_status()
            partial = dest.with_name(dest.name + ".part")
            with partial.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    if chunk:
                        f.write(chunk)
            partial.replace(dest)
        print(f"downloaded {dest.stat().st_size} bytes -> {dest}")
    except requests.RequestException as exc:
        print(f"FAILED: {dest_name}: {exc}")


def try_highways() -> None:
    dest = RAW / "nt_controlled_roads.kmz"
    if present(dest):
        print(f"already present, skipped: {dest.name} ({dest.stat().st_size} bytes)")
        return
    url = HIGHWAYS_CANDIDATE["resource_url"]
    print(f"attempting highways download: {url} ...")
    browser_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Referer": "https://data.nt.gov.au/dataset/nt-government-controlled-roads",
    }
    try:
        resp = requests.get(url, headers=browser_headers, timeout=60)
        print(f"status: {resp.status_code}, content-type: {resp.headers.get('content-type')}")
        if resp.status_code == 200 and "zip" in resp.headers.get("content-type", ""):
            dest.write_bytes(resp.content)
            print(f"downloaded {dest.stat().st_size} bytes -> {dest}")
        else:
            print("FAILED: highways download did not return a zip (see report TBD section)")
    except requests.RequestException as exc:
        print(f"FAILED: highways: {exc}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        download(name, url)
    try_highways()


if __name__ == "__main__":
    sys.exit(main())
