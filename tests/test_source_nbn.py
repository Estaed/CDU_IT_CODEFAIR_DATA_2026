"""Unit tests for pipeline.sources.nbn: NBN fixed-line / fixed-wireless footprint membership."""

from __future__ import annotations

import csv
import re
import time
from pathlib import Path

import pytest

from pipeline.sources import bushtel, nbn

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "data/raw/bushtel_community_detail_2026-09-12.json"
FIXEDLINE_ZIP = ROOT / "data/raw/nbn_coverage_fixedline_2024-03-26.zip"
WIRELESS_ZIP = ROOT / "data/raw/nbn_coverage_wireless_2024-03-26.zip"
FIXTURE = ROOT / "tests/fixtures/nbn_2026-09-12.csv"

COLUMNS = [
    "bushtel_id",
    "nbn_technology",
    "in_fixed_line",
    "in_fixed_wireless",
    "dist_km_nearest_fixed_line",
    "dist_km_nearest_fixed_wireless",
    "fixed_line_attrs",
    "fixed_wireless_attrs",
]
DISTANCE_COLUMNS = {"dist_km_nearest_fixed_line", "dist_km_nearest_fixed_wireless"}


@pytest.fixture(scope="module")
def communities():
    if not SNAPSHOT.exists():
        raise AssertionError(
            f"missing snapshot {SNAPSHOT}; run "
            "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel"
        )
    return bushtel.load(SNAPSHOT)


@pytest.fixture(scope="module")
def frame(communities):
    if not FIXEDLINE_ZIP.exists() or not WIRELESS_ZIP.exists():
        raise AssertionError(
            f"missing raw zip(s) {FIXEDLINE_ZIP} / {WIRELESS_ZIP}; run "
            "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.nbn"
        )
    t0 = time.monotonic()
    result = nbn.load(FIXEDLINE_ZIP, WIRELESS_ZIP, communities)
    print(f"\npipeline.sources.nbn.load wall time: {time.monotonic() - t0:.1f}s")
    return result


def _load_fixture() -> dict[int, dict[str, str]]:
    with FIXTURE.open(encoding="utf-8", newline="") as f:
        return {int(row["bushtel_id"]): row for row in csv.DictReader(f)}


def test_shape(frame):
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    assert list(frame.columns) == COLUMNS


def test_regression_against_fixture(frame):
    fixture = _load_fixture()
    frame_by_id = frame.set_index("bushtel_id")

    differences = []
    for bushtel_id, expected_row in fixture.items():
        got_row = frame_by_id.loc[bushtel_id]
        for column in COLUMNS:
            if column in ("name", "bushtel_id"):
                continue
            expected = expected_row[column]
            got = got_row[column]
            if column in DISTANCE_COLUMNS:
                if abs(float(expected) - float(got)) >= 0.0005:
                    differences.append((bushtel_id, column, expected, got))
            elif str(got) != expected:
                differences.append((bushtel_id, column, expected, got))

    if differences:
        pytest.fail(f"first difference: {differences[0]}")


def test_distribution(frame):
    counts = frame["nbn_technology"].value_counts()
    assert counts.get("SATELLITE_RESIDUAL", 0) == 95
    assert counts.get("FIXED_LINE", 0) == 1
    assert counts.get("FIXED_WIRELESS", 0) == 0

    yirrkala = frame.set_index("bushtel_id").loc[576]
    assert yirrkala["nbn_technology"] == "FIXED_LINE"
    assert yirrkala["in_fixed_line"] == "1"
    assert yirrkala["dist_km_nearest_fixed_line"] == "0.0"
    assert yirrkala["fixed_line_attrs"] == "polygon_id=8NLN-20"

    wadeye = frame.set_index("bushtel_id").loc[426]
    assert wadeye["nbn_technology"] == "SATELLITE_RESIDUAL"


def test_missing_zip_names_fetch_command(communities, tmp_path):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.nbn"):
        nbn.load(tmp_path / "nope.zip", WIRELESS_ZIP, communities)


def test_layer_rules():
    text = Path(nbn.__file__).read_text(encoding="utf-8")
    for line in text.splitlines():
        assert not re.match(r"^(import|from) (pipeline\.sources|spike|requests)", line)
