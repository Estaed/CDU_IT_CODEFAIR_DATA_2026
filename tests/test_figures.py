"""Unit tests for pipeline.figures: the report PNGs and CSV tables."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest
from PIL import Image

from pipeline import figures

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_TELEHEALTH_COUNTS = {"works": 1, "degraded": 58, "fails": 11, "nodata": 26}


@pytest.fixture(scope="module")
def built():
    """Run figures.main() once for the module, writing into the real data/out/ output dirs."""
    if not figures.BOUNDARY_RAW.is_file():
        pytest.skip(f"{figures.BOUNDARY_RAW} is absent")
    figures.main()
    return {
        "figures_dir": figures.FIGURES_DIR,
        "tables_dir": figures.TABLES_DIR,
    }


def _distinct_colors(path: Path) -> int:
    image = Image.open(path).convert("RGB")
    colors = image.getcolors(maxcolors=image.width * image.height)
    return len(colors)


def test_map_verdict_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "map_verdict.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 1000


def test_map_agreement_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "map_agreement.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 1000


def test_disagreement_patterns_sums_to_96_and_31(built):
    path = built["tables_dir"] / "disagreement_patterns.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert sum(int(row["n"]) for row in rows) == 96
    disagree_total = sum(
        int(row["n"])
        for row in rows
        if row["pattern"] not in (figures.UNANIMOUS_COVERED, figures.UNANIMOUS_NOT_COVERED)
    )
    assert disagree_total == 31


def test_verify_on_the_ground_has_11_rows_including_baniyala(built):
    path = built["tables_dir"] / "verify_on_the_ground.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 11
    assert any(row["name"] == "Baniyala" for row in rows)


def test_verdict_counts_telehealth_matches_spike(built):
    path = built["tables_dir"] / "verdict_counts.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    telehealth = {
        row["verdict"]: int(row["communities"])
        for row in rows
        if row["service"] == figures.SERVICE_LABELS["telehealth_video"]
        and row["verdict"] in EXPECTED_TELEHEALTH_COUNTS
    }
    assert telehealth == EXPECTED_TELEHEALTH_COUNTS


def test_no_hex_literal_in_figures_module():
    source = (ROOT / "pipeline/figures.py").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,6}", source)


def test_no_suppressed_population_language_in_tables(built):
    banned = re.compile(r"vulnerable|disadvantaged|at-risk|underserved", re.IGNORECASE)
    for name in ("disagreement_patterns.csv", "verify_on_the_ground.csv", "verdict_counts.csv"):
        text = (built["tables_dir"] / name).read_text(encoding="utf-8")
        assert not banned.search(text)
