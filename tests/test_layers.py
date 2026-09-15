"""Unit tests for pipeline.layers: the pack's map layers (towns, regions, coverage)."""

from __future__ import annotations

from pathlib import Path

import pytest
from shapely.geometry import Polygon

from pipeline import layers, outline, provenance

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data/raw"
BOUNDARY_RAW = RAW_DIR / outline.RAW_NAME

# The figure chosen from reports/2026-09-15-map-bytes.md (OQ13) for exactly the five layers
# this task ships, at the pinned tolerance 0.02: 81,012 + 53,546 + 35,165 + 13,663 + 208.
REPORT_BYTE_BUDGET = 183_594

EXPECTED_LAYER_IDS = ["cov-telstra", "cov-optus", "cov-tpg", "regions-sa3", "towns"]


def test_simplify_to_paths_projects_and_rounds_a_hand_built_square():
    # 1x1 degree square; corners chosen so outline.project gives whole numbers.
    square = Polygon([(130.0, -13.0), (131.0, -13.0), (131.0, -12.0), (130.0, -12.0)])
    paths = layers.simplify_to_paths([square], tolerance_deg=0.0)
    assert paths == ["M 45.0 75.0 L 75.0 75.0 L 75.0 45.0 L 45.0 45.0 L 45.0 75.0 Z"]


def test_simplify_to_paths_drops_a_ring_under_4_square_units():
    # 0.05 x 0.05 degree square: degree area 0.0025 < 4 / (K**2) == 0.004444...
    tiny = Polygon([(130.0, -13.0), (130.05, -13.0), (130.05, -12.95), (130.0, -12.95)])
    assert layers.simplify_to_paths([tiny], tolerance_deg=0.0) == []


def test_simplify_to_paths_keeps_a_ring_just_above_the_floor():
    # 0.08 x 0.08 degree square: degree area 0.0064 > 4 / (K**2) == 0.004444...
    above_floor = Polygon([(130.0, -13.0), (130.08, -13.0), (130.08, -12.92), (130.0, -12.92)])
    assert above_floor.area > layers.MIN_DEGREE_AREA
    assert layers.simplify_to_paths([above_floor], tolerance_deg=0.0) != []


@pytest.fixture(scope="module")
def built_layers():
    return layers.build_layers(RAW_DIR, BOUNDARY_RAW)


def test_build_layers_ids_and_order(built_layers):
    assert [layer["id"] for layer in built_layers] == EXPECTED_LAYER_IDS


def test_build_layers_kind_and_paths(built_layers):
    for layer in built_layers:
        assert layer["kind"] in {"point", "line", "area"}
        assert layer["paths"], f"{layer['id']} has no paths"


def test_build_layers_src_present_in_provenance_with_url_date_licence(built_layers):
    cited = provenance.citations()
    for layer in built_layers:
        assert layer["src"] in cited, f"{layer['id']}: src {layer['src']!r} not in provenance"
        entry = cited[layer["src"]]
        assert entry["url"]
        assert entry["date"]
        assert entry["licence"]


def test_build_layers_point_layer_shape(built_layers):
    towns = next(layer for layer in built_layers if layer["id"] == "towns")
    assert towns["kind"] == "point"
    names = {point["label"] for point in towns["paths"]}
    assert names == {"Darwin", "Katherine", "Tennant Creek", "Alice Springs", "Nhulunbuy"}
    for point in towns["paths"]:
        assert 0.0 <= point["x"] <= 300.0
        assert 0.0 <= point["y"] <= 480.0


def test_build_layers_total_bytes_under_report_budget(built_layers):
    import json

    total = 0
    for layer in built_layers:
        if layer["kind"] == "point":
            total += len(json.dumps(layer["paths"], separators=(",", ":")).encode("utf-8"))
        else:
            total += sum(len(path.encode("utf-8")) for path in layer["paths"])
    assert total <= REPORT_BYTE_BUDGET, total


def test_layers_module_does_not_import_forbidden_layers():
    import re

    source = (ROOT / "pipeline/layers.py").read_text(encoding="utf-8")
    forbidden_import = re.compile(r"^(import|from) (requests|pipeline\.fetch)")
    for line in source.splitlines():
        assert not forbidden_import.match(line), line
    assert "spike" not in source
    assert "design/ds" not in source
