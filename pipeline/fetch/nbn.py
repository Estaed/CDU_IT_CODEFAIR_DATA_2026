"""Re-fetch the NBN coverage footprint zips that ``pipeline.sources.nbn`` reads.

The only module in the repository that talks to data.gov.au for NBN coverage. Run by hand,
never by a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.nbn

Downloads the CC BY 4.0 NBN coverage footprint shapefiles published on data.gov.au (dataset
9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e, data date 2024-03-26) to ``data/raw/``. Idempotent: a
file already present at its expected size is skipped.
"""

from __future__ import annotations

from pathlib import Path

import requests

from pipeline.fetch._download import present_at, stream_to_file

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
HEADERS = {"User-Agent": "CDU-ITCodeFair-2026/0.1 (Crosscheck)"}
TIMEOUT_SECONDS = 300

SOURCES = {
    "fixedline": {
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/"
            "nbn_coverage_fixedline_2024-03-26.zip"
        ),
        "zip_name": "nbn_coverage_fixedline_2024-03-26.zip",
        "expected_bytes": 9_460_437,
    },
    "wireless": {
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/"
            "nbn_coverage_wireless_2024-03-26.zip"
        ),
        "zip_name": "nbn_coverage_wireless_2024-03-26.zip",
        "expected_bytes": 378_833_757,
    },
}


def download(name: str, spec: dict) -> Path:
    dest = RAW / spec["zip_name"]
    if present_at(dest, spec["expected_bytes"]):
        print(f"[{name}] already downloaded: {dest.name} ({dest.stat().st_size} bytes)")
        return dest

    RAW.mkdir(parents=True, exist_ok=True)
    print(f"[{name}] downloading {spec['url']} ...")
    with requests.get(spec["url"], headers=HEADERS, stream=True, timeout=TIMEOUT_SECONDS) as resp:
        resp.raise_for_status()
        size = stream_to_file(resp, dest)
    print(f"[{name}] downloaded {size} bytes -> {dest}")
    if size != spec["expected_bytes"]:
        print(f"[{name}] WARNING: size {size} does not match expected {spec['expected_bytes']}")
    return dest


def main() -> None:
    for name, spec in SOURCES.items():
        download(name, spec)


if __name__ == "__main__":
    main()
