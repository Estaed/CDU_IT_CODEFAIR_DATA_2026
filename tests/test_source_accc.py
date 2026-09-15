"""Unit tests for pipeline.sources.accc: carrier predicted coverage 2025 per community."""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

from pipeline.sources import accc, bushtel

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "data/raw/bushtel_community_detail_2026-09-15.json"
KML_DIR = ROOT / "data/raw"
CACHE_DIR = ROOT / "data/out/cache"
FIXTURE = ROOT / "tests/fixtures/accc_2026-09-15.csv"

FLAG_COLUMNS = [
    "telstra_4g_2025",
    "optus_4g_2025",
    "tpg_4g_2025",
    "mocn_4g_2025",
    "telstra_3g_2025",
    "optus_3g_2025",
    "telstra_5g_2025",
    "optus_5g_2025",
    "tpg_5g_2025",
]
DISTANCE_COLUMNS = ["dist_km_telstra_4g", "dist_km_optus_4g", "dist_km_tpg_4g"]
COLUMNS = ["bushtel_id", *FLAG_COLUMNS, "carriers_4g_count", *DISTANCE_COLUMNS]


@pytest.fixture(scope="module")
def communities():
    return bushtel.load(SNAPSHOT)


@pytest.fixture(scope="module")
def frame(communities):
    return accc.load(KML_DIR, communities, CACHE_DIR)


def test_shape(frame):
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    assert list(frame.columns) == COLUMNS
    assert list(frame["bushtel_id"]) == sorted(frame["bushtel_id"])


def test_regression_against_fixture(frame):
    with FIXTURE.open(encoding="utf-8", newline="") as f:
        expected_rows = {int(row["bushtel_id"]): row for row in csv.DictReader(f)}
    assert len(expected_rows) == 96
    frame_by_id = frame.set_index("bushtel_id")

    differences = []
    for bushtel_id, expected_row in expected_rows.items():
        if bushtel_id not in frame_by_id.index:
            differences.append((bushtel_id, "bushtel_id", "present", "missing"))
            continue
        got_row = frame_by_id.loc[bushtel_id]
        for column, expected in expected_row.items():
            if column in ("name", "bushtel_id"):
                continue
            got = got_row[column]
            if column in DISTANCE_COLUMNS:
                same = round(float(expected), 3) == round(float(got), 3)
            else:
                same = expected == str(got)
            if not same:
                differences.append((bushtel_id, column, expected, got))

    first = differences[0] if differences else None
    assert differences == [], f"{len(differences)} differences, first: {first}"


def test_oracle(frame):
    assert Counter(frame["carriers_4g_count"]) == {"0": 22, "1": 68, "3": 6}
    assert (frame["telstra_4g_2025"] == "1").sum() == 74
    assert (frame["optus_4g_2025"] == "1").sum() == 6
    assert (frame["mocn_4g_2025"] == "1").sum() == 6
    assert (frame["tpg_4g_2025"] == "0").all()
    assert (frame["telstra_3g_2025"] == "-1").all()
    # Optus 5G and TPG 5G layers fetched 2026-09-15 (outside the 2026-09-12 budget)
    assert (frame["optus_5g_2025"] == "1").sum() == 2
    assert (frame["tpg_5g_2025"] == "0").all()
    assert (frame["telstra_5g_2025"] == "1").sum() == 10

    by_id = frame.set_index("bushtel_id")
    wadeye = by_id.loc[426]
    assert wadeye["telstra_4g_2025"] == "1"
    assert wadeye["carriers_4g_count"] == "1"
    assert wadeye["dist_km_telstra_4g"] == "0.0"

    baniyala = by_id.loc[458]
    assert baniyala["carriers_4g_count"] == "0"
    assert baniyala["dist_km_telstra_4g"] == "16.367"


def _write_square_kml(path: Path) -> None:
    # Square lon 129.5..130.001, lat -13.5..-12.5: covers (130.0, -13.0), and (131.0, -13.0)
    # lies 0.999 degrees east of its edge.
    ring = "129.5,-13.5,0 130.001,-13.5,0 130.001,-12.5,0 129.5,-12.5,0 129.5,-13.5,0"
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><Polygon>'
        f"<outerBoundaryIs><LinearRing><coordinates>{ring}</coordinates></LinearRing>"
        "</outerBoundaryIs></Polygon></Placemark></Document></kml>\n",
        encoding="utf-8",
    )


def test_cache_roundtrip(tmp_path, monkeypatch):
    kml = tmp_path / "accc_test_outdoor_2025.kml"
    cache = tmp_path / "cache"
    _write_square_kml(kml)

    original = accc.parse_nt_polygons
    first = accc.nt_polygons(kml, cache)
    assert len(first) == 1
    assert (cache / "accc_test_outdoor_2025.nt.pkl").is_file()

    def must_not_parse(_path):
        raise AssertionError("parsed although the cache is current")

    monkeypatch.setattr(accc, "parse_nt_polygons", must_not_parse)
    second = accc.nt_polygons(kml, cache)
    assert len(second) == len(first)
    assert all(a.equals(b) for a, b in zip(first, second, strict=True))

    calls = []

    def counting(path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(accc, "parse_nt_polygons", counting)
    stat = kml.stat()
    os.utime(kml, ns=(stat.st_atime_ns, stat.st_mtime_ns + 2_000_000_000))
    third = accc.nt_polygons(kml, cache)
    assert len(calls) == 1
    assert all(a.equals(b) for a, b in zip(first, third, strict=True))

    two = pd.DataFrame({"bushtel_id": [1, 2], "lat": [-13.0, -13.0], "lon": [130.0, 131.0]})
    inside, dist_km = accc.point_results(third, two)
    assert inside == {1: 1, 2: 0}
    assert dist_km[1] == 0.0
    assert dist_km[2] == pytest.approx(111.0, abs=0.2)


def test_missing_required_names_fetch_command(tmp_path, communities):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.accc"):
        accc.load(tmp_path, communities, tmp_path / "cache")


def test_layer_rules():
    source_text = (ROOT / "pipeline/sources/accc.py").read_text(encoding="utf-8")
    forbidden = re.compile(r"^(import|from) (pipeline\.sources|spike|requests)", re.MULTILINE)
    assert not forbidden.search(source_text)
    assert "spike" not in source_text
