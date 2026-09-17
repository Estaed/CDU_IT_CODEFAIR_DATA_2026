"""Unit tests for pipeline.sources.mbsp: funded base stations near the 96 communities.

The one thing that can go silently wrong here is the de-duplication: every site is published
twice, once as a ``Point`` placemark and once as its coverage ``Polygon``
(``reports/2026-09-12-arena-failure.md`` section 1.4). A loader that counts both reports
double and no assertion downstream would notice, so the hand-built KML below carries the twin.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd
import pytest

from pipeline.sources import mbsp

ROOT = Path(__file__).resolve().parent.parent

# The arena report's own count, reproduced by this loader on the frozen snapshot.
NT_UNIQUE_SITES = 49

KML_HEAD = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
)
KML_TAIL = "</Document></kml>"


def _placemark(mbsp_id: str, location: str, lon: float, lat: float, geometry: str) -> str:
    return (
        f"<Placemark><name>{mbsp_id}</name><ExtendedData><SchemaData>"
        f'<SimpleData name="MBSP_ID">{mbsp_id}</SimpleData>'
        f'<SimpleData name="Location">{location}</SimpleData>'
        f'<SimpleData name="State">NT</SimpleData>'
        f"</SchemaData></ExtendedData>{geometry}</Placemark>"
    )


def _point(lon: float, lat: float) -> str:
    return f"<Point><coordinates>{lon},{lat},0.0</coordinates></Point>"


def _polygon(lon: float, lat: float) -> str:
    ring = " ".join(
        f"{lon + dx},{lat + dy},0.0"
        for dx, dy in ((0, 0), (0.01, 0), (0.01, 0.01), (0, 0.01), (0, 0))
    )
    return (
        "<Polygon><outerBoundaryIs><LinearRing>"
        f"<coordinates>{ring}</coordinates>"
        "</LinearRing></outerBoundaryIs></Polygon>"
    )


@pytest.fixture
def hand_built_zip(tmp_path) -> Path:
    """Two funded sites, each published twice: once as a Point, once as a Polygon."""
    near = (133.0, -14.0)  # the community's own coordinate
    far = (135.0, -14.0)  # about 215 km east
    body = "".join(
        [
            _placemark("MBSP-NT-900", "Nearby", *near, _point(*near)),
            _placemark("MBSP-NT-900", "Nearby", *near, _polygon(*near)),
            _placemark("MBSP-NT-901", "Far away", *far, _point(*far)),
            _placemark("MBSP-NT-901", "Far away", *far, _polygon(*far)),
        ]
    )
    path = tmp_path / "mbsp_funded_2026-09-17.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "MBSP - Round 1 Funded Base Stations.kml", KML_HEAD + body + KML_TAIL
        )
    return path


@pytest.fixture
def communities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"bushtel_id": "1", "name": "On the site", "lat": -14.0, "lon": 133.0},
            {"bushtel_id": "2", "name": "A hundred km off", "lat": -14.0, "lon": 134.0},
            {"bushtel_id": "3", "name": "Past the cut-off", "lat": -20.0, "lon": 133.0},
        ]
    )


def test_the_polygon_twin_is_not_counted_twice(hand_built_zip):
    frame = mbsp.sites(hand_built_zip)
    assert len(frame) == 2
    assert sorted(frame["mbsp_id"]) == ["MBSP-NT-900", "MBSP-NT-901"]
    assert list(frame.columns) == mbsp.SITE_COLUMNS
    assert set(frame["round"]) == {"Round 1"}


def test_within_5km_counts_only_the_site_that_is_near(hand_built_zip, communities):
    frame = mbsp.load(hand_built_zip, communities)
    assert list(frame.columns) == mbsp.COLUMNS
    by_id = frame.set_index("bushtel_id")
    assert by_id.loc[1, "mbsp_within_5km"] == "1"
    assert float(by_id.loc[1, "mbsp_nearest_km"]) < 0.1
    assert by_id.loc[2, "mbsp_within_5km"] == "0"
    assert 100 < float(by_id.loc[2, "mbsp_nearest_km"]) < 120
    # Past FAR_M the nearest site says nothing about this community, so the cell is empty.
    assert by_id.loc[3, "mbsp_within_5km"] == "0"
    assert by_id.loc[3, "mbsp_nearest_km"] == ""


def test_one_row_per_community_sorted_by_id(hand_built_zip, communities):
    frame = mbsp.load(hand_built_zip, communities)
    assert len(frame) == len(communities)
    assert list(frame["bushtel_id"]) == sorted(frame["bushtel_id"])


def test_missing_snapshot_names_the_fetch_command(tmp_path):
    with pytest.raises(FileNotFoundError) as caught:
        mbsp.sites(tmp_path / "absent.zip")
    assert mbsp.FETCH_COMMAND in str(caught.value)


def test_frozen_snapshot_reproduces_the_arena_report_count():
    """49 unique NT sites across the eight rounds, the figure the arena report recorded."""
    found = sorted((ROOT / "data/raw").glob("mbsp_funded_*.zip"))
    if not found:
        pytest.skip("no MBSP snapshot under data/raw/")
    frame = mbsp.sites(found[-1])
    nt = frame[frame["mbsp_id"].str.contains("-NT-")]
    assert len(nt) == NT_UNIQUE_SITES
    assert len(frame) == len(set(frame["mbsp_id"]))
