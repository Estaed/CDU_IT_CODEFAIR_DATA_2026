"""The source registry: where every raw file came from, and the lines that must be shown.

This module is the one place a source URL, a publication date, a licence or an attribution
line is written down (CLAUDE.md Part 2, Key Constraints). ``write`` turns it into
``data/out/PROVENANCE.md`` by measuring the files actually on disk; ``citations`` hands the
same registry to ``pipeline.pack`` so the app's sources table quotes the registry rather than
a second copy of it.

Standard library only: it is imported by the pack build, which must not pull in a reader.
"""

from __future__ import annotations

import importlib
from datetime import date
from pathlib import Path

# Sources with a frozen snapshot under data/raw/. ``pack_source`` is the exact string the
# pack cites the source by, empty when the pack never names it; ``module`` is the
# pipeline.sources module whose FETCH_COMMAND re-fetches the file; ``date`` is the
# publication date the screen footers show, not the fetch date (that is read off the file).
SOURCES = (
    {
        "id": "bushtel",
        "name": "BushTel community profiles",
        "pack_source": "BushTel profile",
        "url": "https://bushtel.nt.gov.au/api/Community",
        "licence": "NT Government; reuse terms under Open Question 1 (docs/PRD.md)",
        "attribution": "BushTel community profiles, Northern Territory Government",
        "pattern": "bushtel_*.json",
        # The snapshot date; the pack cites each community's own profile stamp instead,
        # because the portal publishes no single date for the set (pack.PER_COMMUNITY_SOURCES).
        "date": "2026-09-15",
        "module": "bushtel",
    },
    {
        "id": "nbn_fixedline",
        "name": "nbn fixed-line coverage footprint",
        "pack_source": "",
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/"
            "nbn_coverage_fixedline_2024-03-26.zip"
        ),
        "licence": "CC BY 4.0",
        "attribution": "nbn co fixed-line coverage footprint",
        "pattern": "nbn_coverage_fixedline_*.zip",
        "date": "2024-03-26",
        "module": "nbn",
    },
    {
        "id": "nbn_wireless",
        "name": "nbn fixed-wireless coverage footprint",
        "pack_source": "",
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/"
            "nbn_coverage_wireless_2024-03-26.zip"
        ),
        "licence": "CC BY 4.0",
        "attribution": "nbn co fixed-wireless coverage footprint",
        "pattern": "nbn_coverage_wireless_*.zip",
        "date": "2024-03-26",
        "module": "nbn",
    },
    {
        "id": "accc_mir_2025",
        "name": "ACCC Mobile Infrastructure Report 2025 outdoor coverage maps",
        "pack_source": "ACCC MIR 2025",
        "url": "https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90",
        "licence": "CC BY 2.5 AU",
        "attribution": "ACCC Mobile Infrastructure Report 2025",
        "pattern": "accc_*_outdoor_2025.*",
        "date": "2025-11-10",
        "module": "accc",
    },
    {
        "id": "rrl",
        "name": "ACMA Register of Radiocommunications Licences",
        "pack_source": "ACMA RRL",
        "url": "https://www.acma.gov.au/radiocomms-licence-data",
        "licence": "ACMA licence: derivatives and their redistribution permitted",
        "attribution": (
            "Based on Australian Communications and Media Authority information"
        ),
        "pattern": "spectra_rrl_*.zip",
        "date": "2026-09-15",
        "module": "rrl",
    },
    {
        "id": "ntg_2019",
        "name": "Remote Communities with Mobile Coverage and Backhaul Transmission 2019",
        "pack_source": "NT Government 2019 coverage list",
        "url": "https://data.nt.gov.au/dataset/list-of-remote-communities-with-mobile-coverage",
        "licence": "CC BY",
        "attribution": "NT Government mobile coverage list 2019",
        "pattern": "ntg_2019.xlsx",
        "date": "2019",
        "module": "ntg",
    },
    {
        "id": "ntg_2021",
        "name": "Remote Communities with 3G/4G Mobile Coverage 2021",
        "pack_source": "",
        "url": "https://data.nt.gov.au/dataset/remote-communities-with-mobile-coverage",
        "licence": "CC BY",
        "attribution": "NT Government mobile coverage list 2021",
        "pattern": "ntg_2021.xlsx",
        "date": "2021",
        "module": "ntg",
    },
    {
        "id": "ntg_2022",
        "name": "Mobile Phone Coverage in Remote Areas of the NT 2022",
        "pack_source": "NT Government 2022 list",
        "url": "https://data.nt.gov.au/dataset/mobile-phone-coverage-in-remote-areas-of-the-nt",
        "licence": "CC BY",
        "attribution": "NT Government mobile coverage list 2022",
        "pattern": "ntg_2022.xlsx",
        "date": "2022-07-04",
        "module": "ntg",
    },
    {
        "id": "abs_ste_2021",
        "name": "ABS ASGS Edition 3 State and Territory boundary 2021",
        "pack_source": "",
        "url": (
            "https://www.abs.gov.au/statistics/standards/"
            "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
            "access-and-downloads/digital-boundary-files/STE_2021_AUST_SHP_GDA2020.zip"
        ),
        "licence": "CC BY 4.0",
        "attribution": (
            "Australian Bureau of Statistics, ASGS Edition 3 State and Territory boundaries 2021"
        ),
        "pattern": "abs_ste_20*",
        "date": "2021-07-20",
        "fetch_command": "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_boundary",
    },
    {
        "id": "abs_sa3_2021",
        "name": "ABS ASGS Edition 3 SA3 boundary 2021",
        "pack_source": "ABS ASGS SA3 2021",
        "url": (
            "https://www.abs.gov.au/statistics/standards/"
            "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
            "access-and-downloads/digital-boundary-files/SA3_2021_AUST_SHP_GDA2020.zip"
        ),
        "licence": "CC BY 4.0",
        "attribution": (
            "Australian Bureau of Statistics, ASGS Edition 3 SA3 boundaries 2021"
        ),
        "pattern": "abs_sa3_20*",
        "date": "2021-07-20",
        "fetch_command": "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_sa3",
    },
    {
        "id": "abs_ucl_2021",
        "name": "ABS ASGS Edition 3 UCL boundary 2021",
        "pack_source": "ABS ASGS UCL 2021",
        "url": (
            "https://www.abs.gov.au/statistics/standards/"
            "australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/"
            "access-and-downloads/digital-boundary-files/UCL_2021_AUST_GDA2020_SHP.zip"
        ),
        "licence": "CC BY 4.0",
        "attribution": (
            "Australian Bureau of Statistics, ASGS Edition 3 Urban Centres and "
            "Localities boundaries 2021"
        ),
        "pattern": "abs_ucl_20*",
        "date": "2021-07-20",
        "fetch_command": "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_ucl",
    },
    {
        "id": "ntg_smallcell",
        "name": "Remote Sites with Mobile Phone Small Cell Coverage",
        "pack_source": "",
        "url": (
            "https://data.nt.gov.au/dataset/"
            "remote-sites-with-mobile-phone-small-cell-coverage"
        ),
        "licence": "CC BY",
        "attribution": "NT Government remote small cell sites",
        "pattern": "ntg_smallcell.xlsx",
        "date": "2021-06-22",
        "module": "ntg",
    },
)

# Sources the pack cites that have no snapshot of their own: the ABS population figure
# travels inside the BushTel profile, and the satellite latency figure is a published
# measurement quoted from pipeline/thresholds.csv. They carry the same fields minus the
# file-shaped ones, so citations() reads both registries the same way.
PACK_SOURCES = (
    {
        "id": "abs_census_2021",
        "name": "ABS Census 2021 SA1 population, via BushTel",
        "pack_source": "ABS 2021 SA1 via BushTel",
        "url": "https://www.abs.gov.au/census",
        "licence": "CC BY 4.0",
        "attribution": "ABS Census 2021 SA1 population via BushTel",
        "date": "",
    },
    {
        "id": "accc_mba_147_24",
        "name": "ACCC Measuring Broadband Australia release 147/24",
        "pack_source": "ACCC Measuring Broadband Australia release 147/24",
        "url": (
            "https://www.accc.gov.au/media-release/"
            "broadband-performance-of-satellite-services-measured-for-the-first-time"
        ),
        "licence": "CC BY 2.5 AU",
        "attribution": "ACCC Measuring Broadband Australia, satellite latency",
        "date": "2024-12-05",
    },
)

HEADER = (
    "| Source | File | Fetched | Bytes | URL | Licence | Attribution |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
)


def citations() -> dict[str, dict[str, str]]:
    """``{pack source name: {date, url, licence}}`` for every source the pack names.

    ``date`` is the publication date; an empty one means the citing line keeps its own date
    (a BushTel profile stamp differs per community).
    """
    table: dict[str, dict[str, str]] = {}
    for entry in SOURCES + PACK_SOURCES:
        if entry["pack_source"]:
            table[entry["pack_source"]] = {
                "date": entry["date"],
                "url": entry["url"],
                "licence": entry["licence"],
            }
    return table


def fetch_command(entry: dict) -> str:
    """The command that re-fetches this source: a literal string, or its source module's."""
    if "fetch_command" in entry:
        return entry["fetch_command"]
    module = importlib.import_module(f"pipeline.sources.{entry['module']}")
    return module.FETCH_COMMAND


def matches(entry: dict, raw_dir: Path) -> list[Path]:
    """Files under ``raw_dir`` this source accounts for, or a failure naming the fetch step."""
    found = sorted(Path(raw_dir).glob(entry["pattern"]))
    if not found:
        raise FileNotFoundError(
            f"no file matches {entry['pattern']} under {raw_dir} for source "
            f"'{entry['id']}'. Re-fetch it with: {fetch_command(entry)}"
        )
    return found


def rows(raw_dir: Path) -> list[dict[str, str]]:
    """One record per raw file: the registry fields plus the file's fetch date and size."""
    raw_dir = Path(raw_dir)
    records = []
    for entry in SOURCES:
        for path in matches(entry, raw_dir):
            stat = path.stat()
            records.append(
                {
                    "source": entry["name"],
                    "file": path.name,
                    "fetched": date.fromtimestamp(stat.st_mtime).isoformat(),
                    "bytes": f"{stat.st_size:,}",
                    "url": entry["url"],
                    "licence": entry["licence"],
                    "attribution": entry["attribution"],
                }
            )
    return records


def write(out_path: Path, raw_dir: Path) -> Path:
    """Write ``PROVENANCE.md``: every raw file with its URL, fetch date, size and licence."""
    out_path = Path(out_path)
    records = rows(raw_dir)
    lines = [
        "# Provenance",
        "",
        "Every file under `data/raw/` the pipeline reads, with the URL it came from, the date",
        "it was fetched, its size on disk, its licence and the attribution line the app and",
        "the report carry. Generated by `pipeline/provenance.py`; do not edit by hand.",
        "",
        "",
    ]
    row = "| {source} | `{file}` | {fetched} | {bytes} | {url} | {licence} | {attribution} |\n"
    table = HEADER + "".join(row.format(**record) for record in records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + table, encoding="utf-8", newline="\n")
    return out_path
