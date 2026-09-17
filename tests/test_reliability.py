"""Unit tests for pipeline.reliability: the one model, its split, and its kill criterion.

Nothing here fits the real model: the training set is 3,919 road samples behind 80 seconds of
geometry, and a test that waited for it would be run once and then skipped. What is tested is
what can be got wrong silently -- the feature arithmetic, the region split, the cut points,
and that a pooled AUC under the floor still completes with every word ``none``.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pipeline import reliability

ROOT = Path(__file__).resolve().parent.parent
SKLEARN_IMPORT = re.compile(r"^\s*(import|from)\s+sklearn\b", re.MULTILINE)


def test_features_from_hand_built_row():
    # A point 2 km inside the claiming polygon, one licensed site of the claiming carrier at
    # 3 km, three more masts at 8, 14 and 31 km, and two carriers claiming the point.
    row = {
        "carrier_site_km": 3.0,
        "boundary_km": 2.0,
        "inside": True,
        "site_distances_km": [3.0, 8.0, 14.0, 31.0],
        "carriers_claiming": 2,
    }
    assert reliability.features(row) == {
        "site_km": 3.0,
        "depth_km": 2.0,
        "sites_10km": 2,
        "sites_20km": 3,
        "carriers_claiming": 2,
    }
    # Outside the polygon the same distance is negative depth: the sign is the whole point.
    outside = reliability.features({**row, "inside": False})
    assert outside["depth_km"] == -2.0
    assert list(reliability.features(row)) == list(reliability.FEATURE_NAMES)


def test_split_by_region_is_disjoint():
    regions = [f"Region {index}" for index in range(13)]
    samples = [region for region in regions for _ in range(4)]
    assignment = reliability.fold_of_region(samples)

    assert set(assignment) == set(regions)
    assert set(assignment.values()) == set(range(reliability.FOLDS))
    # Every sample of a region lands in one fold, so no region is on both sides of a split.
    for index in range(reliability.FOLDS):
        test = {region for region, fold in assignment.items() if fold == index}
        train = {region for region, fold in assignment.items() if fold != index}
        assert not (test & train)
        assert test
    # Seeded: the same regions deal the same way every run.
    assert reliability.fold_of_region(samples) == assignment


def test_words_from_cut_points():
    assert reliability.word_for(0.1) == "high"
    assert reliability.word_for(0.3) == "medium"
    assert reliability.word_for(0.7) == "low"
    assert reliability.word_for(None) == "none"
    # The cut points themselves, fixed before the first fit.
    assert reliability.word_for(reliability.CUT_MEDIUM) == "medium"
    assert reliability.word_for(reliability.CUT_LOW) == "low"


class _StubGeography:
    """One claimed point, so the kill path is proved by the model being absent, not the data."""

    def rows(self, points):
        return [
            {
                "point_index": 0,
                "x": 0.0,
                "y": 0.0,
                "carrier": "Telstra",
                "carrier_site_km": 3.0,
                "boundary_km": 2.0,
                "inside": True,
                "site_distances_km": [3.0],
                "carriers_claiming": 1,
            }
        ]


@pytest.fixture
def kill_path(tmp_path, monkeypatch):
    """``main`` with a stub ``evaluate`` that returns an AUC under the floor."""
    table = tmp_path / "capability_table.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["bushtel_id", "name", "lat", "lon", "audit5"])
        writer.writerow(["426", "Wadeye", "-14.2", "129.5", ""])
        writer.writerow(["580", "Barunga", "-14.5", "132.9", "1"])

    frame = pd.DataFrame(
        {
            "x": [0.0, 1.0],
            "y": [0.0, 1.0],
            "carrier": ["Telstra", "Optus"],
            "label": [1, 0],
            "site_km": [3.0, 9.0],
            "depth_km": [2.0, 0.5],
            "sites_10km": [1, 0],
            "sites_20km": [2, 1],
            "carriers_claiming": [1, 1],
            "region": ["Katherine", "Barkly"],
        }
    )
    stub_validation = [
        {
            "fold": "pooled",
            "regions": "2 SA3 regions, seed 0",
            "samples": 2,
            "positives": 1,
            "base_rate": 0.5,
            "auc": 0.5,
            "precision_at_0.5": "",
            "recall_at_0.5": "",
        }
    ]

    monkeypatch.setattr(
        reliability, "samples", lambda: (frame, _StubGeography(), np.array([], dtype=object))
    )
    monkeypatch.setattr(reliability, "evaluate", lambda _frame: (stub_validation, 0.5))
    monkeypatch.setattr(reliability, "TABLE_CSV", table)
    monkeypatch.setattr(reliability, "TABLE_XLSX", tmp_path / "capability_table.xlsx")
    monkeypatch.setattr(reliability, "RELIABILITY_CSV", tmp_path / "reliability.csv")
    monkeypatch.setattr(reliability, "VALIDATION_CSV", tmp_path / "validation.csv")
    monkeypatch.setattr(reliability, "COEFFICIENTS_CSV", tmp_path / "coefficients.csv")
    reliability.main()
    return tmp_path


def test_kill_path_completes(kill_path):
    # An AUC of 0.5 is under the floor, so nothing is fitted and no word ships.
    assert 0.5 < reliability.AUC_FLOOR
    with (kill_path / "reliability.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["id"] for row in rows] == ["426", "580"]
    assert {row["word"] for row in rows} == {"none"}
    assert {row["p_wrong"] for row in rows} == {""}
    assert {row["driver1"] for row in rows} == {""}


def test_kill_path_still_writes_the_validation_table(kill_path):
    with (kill_path / "validation.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["fold"] for row in rows] == ["pooled"]
    assert rows[0]["auc"] == "0.5"
    # The coefficients table is written too, and it is empty: there were none to write.
    with (kill_path / "coefficients.csv").open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []


def test_kill_path_leaves_the_table_readable(kill_path):
    table = pd.read_csv(
        kill_path / "capability_table.csv", dtype=str, keep_default_na=False
    )
    # No road samples were passed in, so no audit5 cell may be filled with "0".
    assert list(table["audit5"]) == ["", "1"]


def test_fill_audit_zero_only_fills_empty_cells():
    table = pd.DataFrame(
        {"bushtel_id": ["1", "2", "3"], "audit5": ["", "1", ""]}, dtype=str
    )
    changed = reliability.fill_audit_zero(table, {1, 2})
    assert changed == 1
    # "1" outranks "0": a non-alignment tile within 5 km is not erased by a quiet road.
    assert list(table["audit5"]) == ["0", "1", ""]


def test_thin_keeps_one_of_each_label_per_kilometre():
    import shapely

    points = shapely.points(
        [0.0, 200.0, 2_000.0, 300.0], [0.0, 0.0, 0.0, 0.0]
    )
    labels = np.array([0, 0, 0, 1])
    kept = reliability.thin(points, labels)
    # The 200 m neighbour of the same label goes; the 2 km one stays; the other label stays.
    assert list(kept) == [0, 2, 3]


def test_no_sklearn_elsewhere():
    """Layer rule 9: the one model lives in one file."""
    offenders = []
    for folder in ("pipeline", "scripts", "tests", "app"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            if path == ROOT / "pipeline" / "reliability.py":
                continue
            if SKLEARN_IMPORT.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
    for path in sorted((ROOT / "app").glob("*.js")):
        assert "sklearn" not in path.read_text(encoding="utf-8")
