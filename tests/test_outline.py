"""Unit tests for pipeline.outline: the NT boundary path and the lat/lon projection."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline import outline

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "data/out/data_pack.json"

NUM = r"-?\d+(?:\.\d)?"
POINT = rf"{NUM} {NUM}"
SUBPATH = rf"M {POINT}(?: L {POINT})+ Z"
PATH_RE = re.compile(rf"^{SUBPATH}(?: {SUBPATH}){{2}}$")


def _load_pack() -> dict:
    with PACK.open(encoding="utf-8") as f:
        return json.load(f)


def _raw_boundary_file() -> Path | None:
    return next(ROOT.glob("data/raw/abs_ste_2021*"), None)


def test_project_origin():
    assert outline.project(-10.5, 128.5) == (0.0, 0.0)


def test_project_known_point():
    assert outline.project(-12.5, 131.0) == (75.0, 60.0)


def test_project_rounds_to_one_decimal():
    x, y = outline.project(-10.501, 128.501)
    assert x == round(x, 1)
    assert y == round(y, 1)


def test_all_96_points_inside_view_box_and_match_project():
    data_pack = _load_pack()
    communities = data_pack["communities"]
    assert len(communities) == 96
    for community in communities:
        x, y = community["x"], community["y"]
        assert 0.0 <= x <= 300.0
        assert 0.0 <= y <= 480.0
        expected_x, expected_y = outline.project(community["lat"], community["lon"])
        assert x == expected_x
        assert y == expected_y


def test_outline_path_under_byte_budget():
    data_pack = _load_pack()
    encoded = data_pack["outline"].encode("utf-8")
    assert len(encoded) < 8_000


def test_outline_path_starts_and_ends_correctly():
    path = _load_pack()["outline"]
    assert path.startswith("M")
    assert path.endswith("Z")


def test_outline_path_has_three_closed_subpaths():
    path = _load_pack()["outline"]
    assert path.count("Z") == 3


def test_outline_path_matches_grammar():
    path = _load_pack()["outline"]
    assert PATH_RE.match(path), path


def test_outline_path_coordinates_inside_view_box():
    path = _load_pack()["outline"]
    numbers = [float(n) for n in re.findall(NUM, path)]
    assert len(numbers) % 2 == 0
    xs = numbers[0::2]
    ys = numbers[1::2]
    assert all(0.0 <= x <= 300.0 for x in xs)
    assert all(0.0 <= y <= 480.0 for y in ys)


def test_outline_path_matches_committed_pack_at_pinned_tolerance():
    raw = _raw_boundary_file()
    if raw is None:
        pytest.skip("data/raw/abs_ste_2021* is absent")
    built = outline.outline_path(raw, outline.TOLERANCE_DEG)
    assert built == _load_pack()["outline"]


def test_coarser_tolerance_is_shorter():
    raw = _raw_boundary_file()
    if raw is None:
        pytest.skip("data/raw/abs_ste_2021* is absent")
    coarse = outline.outline_path(raw, 0.5)
    fine = outline.outline_path(raw, 0.005)
    assert len(coarse.encode("utf-8")) < len(fine.encode("utf-8"))


def test_outline_module_does_not_import_forbidden_layers():
    source = (ROOT / "pipeline/outline.py").read_text(encoding="utf-8")
    forbidden_import = re.compile(r"^(import|from) (requests|pipeline\.fetch|pipeline\.sources)")
    for line in source.splitlines():
        assert not forbidden_import.match(line), line
    assert "spike" not in source
    assert "design/ds" not in source
