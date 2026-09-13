"""Re-fetch the ACCC 2025 outdoor coverage KMLs that ``pipeline.sources.accc`` reads.

The only module in the repository that talks to data.gov.au for the ACCC Mobile Infrastructure
Report data release. Run by hand, never by a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.accc

Lists the resources of CKAN package ``4b472a18-d0fa-409c-994a-ab17162bcb90`` with
``package_show``, finds ``Coverage map - <MNO> - <tech> - Outdoor - 2025`` for each job and
streams it to ``data/raw/accc_<key>_outdoor_2025.<kml|zip>``, extracting the ``.kml`` member of a
zip next to it. A file already present at the resource's declared size is skipped.

The dataset page has refused automated fetches (HTTP 403) from some clients; the script then
prints the page, the resource name and the target filename so the file can be downloaded by
hand, and continues with the next job.

Licence: CC BY 2.5 AU. Release used on 2026-09-12: newest resource Last-Modified 2025-11-10.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
PACKAGE_ID = "4b472a18-d0fa-409c-994a-ab17162bcb90"
PACKAGE_SHOW_URL = f"https://data.gov.au/data/api/3/action/package_show?id={PACKAGE_ID}"
DATASET_PAGE = f"https://data.gov.au/data/dataset/{PACKAGE_ID}"
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 120
CHUNK_BYTES = 1 << 20

# (job key, MNO name as it appears in the resource name, technology)
JOBS = (
    ("telstra_4g", "Telstra", "4G"),
    ("optus_4g", "Optus", "4G"),
    ("tpg_4g", "TPG", "4G"),
    ("mocn_4g", "Optus-TPG MOCN", "4G"),
    ("telstra_3g", "Telstra", "3G"),
    ("optus_3g", "Optus", "3G"),
    ("telstra_5g", "Telstra", "5G"),
    ("optus_5g", "Optus", "5G"),
    ("tpg_5g", "TPG", "5G"),
)


class Forbidden(Exception):
    """The server answered HTTP 403."""


def resource_name(mno: str, tech: str) -> str:
    return f"Coverage map - {mno} - {tech} - Outdoor - 2025"


def target(key: str, ext: str) -> Path:
    return RAW / f"accc_{key}_outdoor_2025.{ext}"


def get(url: str, stream: bool = False) -> requests.Response:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, stream=stream)
    if response.status_code == 403:
        response.close()
        raise Forbidden(url)
    response.raise_for_status()
    return response


def download(url: str, dest: Path, expected_size: int | None) -> str:
    if dest.is_file() and (not expected_size or dest.stat().st_size == expected_size):
        return f"skipped, present at {dest.stat().st_size} bytes"
    partial = dest.with_name(dest.name + ".part")
    with get(url, stream=True) as response, partial.open("wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_BYTES):
            if chunk:
                f.write(chunk)
    partial.replace(dest)
    return f"downloaded {dest.stat().st_size} bytes"


def extract_kml(zip_path: Path, dest: Path) -> None:
    if dest.is_file():
        return
    with zipfile.ZipFile(zip_path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith(".kml")]
        if not members:
            raise RuntimeError(f"no .kml member inside {zip_path}")
        partial = dest.with_name(dest.name + ".part")
        with archive.open(members[0]) as src, partial.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        partial.replace(dest)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    try:
        with get(PACKAGE_SHOW_URL) as response:
            resources = response.json()["result"]["resources"]
    except Forbidden:
        print(f"HTTP 403 on package_show. Download the files by hand from {DATASET_PAGE}")
        for key, mno, tech in JOBS:
            print(f"  '{resource_name(mno, tech)}' -> {target(key, 'kml')}")
        return
    by_name = {r.get("name"): r for r in resources}

    for key, mno, tech in JOBS:
        name = resource_name(mno, tech)
        resource = by_name.get(name)
        if resource is None:
            print(f"[{key}] not on the dataset: '{name}'")
            continue
        is_zip = (resource.get("format") or "").upper() == "ZIP"
        dest = target(key, "zip" if is_zip else "kml")
        try:
            status = download(resource["url"], dest, resource.get("size"))
        except Forbidden:
            print(
                f"[{key}] HTTP 403. Download '{name}' by hand from {DATASET_PAGE} "
                f"and save it as {dest}"
            )
            continue
        if is_zip:
            extract_kml(dest, target(key, "kml"))
            status += f", extracted {target(key, 'kml').name}"
        print(f"[{key}] {status}")


if __name__ == "__main__":
    main()
