"""Unit tests for pipeline.sources.audit: National Audit non-alignment tiles per community."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
import pytest

from pipeline.sources import audit, bushtel

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
AUDIT_CSV = RAW / "audit_non_alignment_2026-09-17.csv"
BUSHTEL_SNAPSHOT = RAW / "bushtel_community_detail_2026-09-15.json"
FORBIDDEN_IMPORT = re.compile(r"^(import|from) (pipeline\.sources|spike|requests)", re.MULTILINE)

HEADER = [
    "WKT",
    "fid",
    "Tile Id",
    "MNO",
    "State",
    "LGA",
    "Audit Data",
    "MNO Predicted Coverage",
    "MNO Feedback on non-alignment",
    "Further Details",
    "Year",
    "Day",
    "Month",
    "Batch Item",
]

# The hand-built fixture: community 1 sits at (-14.0, 133.0); a degree of longitude there is
# 111.320 * cos(14 deg) = 108.02 km, so 0.018515 deg east of it is 2.0 km away.
NEAR_LON = 133.0 + 0.018515
FAR_LON = 133.0 + 0.185150  # 20 km east
TILE_DEG = 0.009  # the published tile is a ~1 km square


def _tile_wkt(lon: float, lat: float) -> str:
    """A tile whose west edge is at ``lon`` and whose latitude span contains ``lat``."""
    south, north = lat - TILE_DEG / 2, lat + TILE_DEG / 2
    ring = [
        (lon, north),
        (lon + TILE_DEG, north),
        (lon + TILE_DEG, south),
        (lon, south),
        (lon, north),
    ]
    points = ",".join(f"{x} {y}" for x, y in ring)
    return f"MULTIPOLYGON ((({points})))"


def _fixture_row(wkt: str, carrier: str, state: str, year: str) -> list[str]:
    return [
        wkt,
        "1",
        "tile",
        carrier,
        state,
        "Roper Gulf",
        "No audit roads coverage",
        "With MNO claimed coverage",
        "No feedback from MNO",
        "",
        year,
        "1",
        "5",
        "202505-b1",
    ]


@pytest.fixture(scope="module")
def fixture_csv(tmp_path_factory) -> Path:
    """Three tiles: 2 km from community 1, 20 km from it, and one in another state."""
    path = tmp_path_factory.mktemp("audit") / "audit_non_alignment_fixture.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerow(HEADER)  # the published file repeats its header as the first data row
        writer.writerow(_fixture_row(_tile_wkt(NEAR_LON, -14.0), "Telstra", "NT", "2025"))
        writer.writerow(_fixture_row(_tile_wkt(FAR_LON, -14.0), "Optus", "NT", "2024"))
        # Another state, 0.5 km away: must be ignored however close it is.
        writer.writerow(_fixture_row(_tile_wkt(133.004, -14.0), "Telstra", "SA", "2025"))
    return path


@pytest.fixture(scope="module")
def fixture_communities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"bushtel_id": 1, "name": "Near", "lat": -14.0, "lon": 133.0},
            {"bushtel_id": 2, "name": "Far", "lat": -23.0, "lon": 134.0},
        ]
    )


@pytest.fixture(scope="module")
def fixture_frame(fixture_csv, fixture_communities) -> pd.DataFrame:
    return audit.load(fixture_csv, fixture_communities)


def test_fixture_shape(fixture_frame):
    assert list(fixture_frame.columns) == audit.COLUMNS
    assert list(fixture_frame["bushtel_id"]) == [1, 2]


def test_tile_within_5km_is_counted_and_measured(fixture_frame):
    near = fixture_frame.set_index("bushtel_id").loc[1]
    assert near["audit5"] == "1"
    assert near["audit_nearest_km"] == "2.0"
    assert near["audit_carriers"] == "Telstra"  # the SA tile 0.5 km away is not in the NT set
    assert near["audit_year"] == "2025"


def test_no_tile_within_40km_leaves_every_cell_empty(fixture_frame):
    far = fixture_frame.set_index("bushtel_id").loc[2]
    assert far["audit5"] == ""
    assert far["audit_nearest_km"] == ""
    assert far["audit_carriers"] == ""
    assert far["audit_year"] == ""


def test_other_states_are_dropped_before_any_geometry(fixture_csv):
    assert len(audit.tiles(fixture_csv)) == 2


def test_write_table_lists_only_the_communities_within_5km(
    fixture_frame, fixture_communities, tmp_path
):
    written = audit.write_table(fixture_frame, fixture_communities, tmp_path / "t.csv")
    text = written.read_text(encoding="utf-8")
    assert text == (
        "bushtel_id,name,audit_carriers,audit_nearest_km,audit_year\n1,Near,Telstra,2.0,2025\n"
    )


@pytest.fixture(scope="module")
def communities():
    return bushtel.load(BUSHTEL_SNAPSHOT)


@pytest.fixture(scope="module")
def frame(communities):
    if not AUDIT_CSV.exists():
        raise AssertionError(f"missing snapshot {AUDIT_CSV}; run {audit.FETCH_COMMAND}")
    return audit.load(AUDIT_CSV, communities)


def test_shape(frame):
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    assert list(frame.columns) == audit.COLUMNS


def test_nt_tile_count(frame):
    tiles = audit.tiles(AUDIT_CSV)
    assert len(tiles) == 237  # reports/2026-09-12-arena-measured.md S3.1.6
    assert sorted(set(tiles["carrier"])) == ["Optus", "TPG", "Telstra"]


def test_zero_is_never_written_by_this_module(frame):
    # "0" means "a road was audited within 5 km and carried no non-alignment". This CSV lists
    # non-alignments only and cannot say that, so Task-39 fills it; Task-38 never does.
    assert set(frame["audit5"]) == {"1", ""}


def test_oracle(frame):
    within = frame[frame["audit5"] == "1"]
    assert sorted(within["bushtel_id"]) == [397, 580, 593]
    by_id = frame.set_index("bushtel_id")
    assert by_id.loc[397, "audit_nearest_km"] == "4.7"
    assert by_id.loc[580, "audit_nearest_km"] == "1.0"
    assert by_id.loc[593, "audit_nearest_km"] == "3.2"
    assert set(within["audit_carriers"]) == {"Telstra"}
    assert (frame["audit_nearest_km"] != "").sum() == 25  # a tile within 40 km
    assert by_id.loc[426, "audit_nearest_km"] == ""  # Wadeye: nearest tile is 142 km away


def test_missing_csv_names_fetch_command(tmp_path, communities):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.audit"):
        audit.load(tmp_path / "nope.csv", communities)


def test_layer_rules():
    source_text = (ROOT / "pipeline/sources/audit.py").read_text(encoding="utf-8")
    assert not FORBIDDEN_IMPORT.search(source_text)
