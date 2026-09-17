"""Unit tests for pipeline.figures: the report PNGs and CSV tables."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest
from PIL import Image

from pipeline import figures, prioritise

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
    for name in ("disagreement_patterns.csv", "verify_on_the_ground.csv", "verdict_counts.csv",
                 "priority.csv"):
        text = (built["tables_dir"] / name).read_text(encoding="utf-8")
        assert not banned.search(text)


# --- The priority map and tables (Task-40) ---


def test_map_priority_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "map_priority.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 1000


def test_priority_table_has_96_rows_in_rank_order(built):
    path = built["tables_dir"] / "priority.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 96
    assert list(rows[0]) == list(figures.PRIORITY_COLUMNS)
    assert [int(row["rank"]) for row in rows] == list(range(1, 97))
    assert all(row["intervention"] for row in rows)


def test_priority_sensitivity_table_has_one_row_per_weight_and_factor():
    path = prioritise.OUT_SENSITIVITY
    assert path.is_file(), f"missing {path}; run pipeline.prioritise"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    weights = prioritise.load_weights()
    assert len(rows) == len(weights) * len(prioritise.SENSITIVITY_FACTORS)
    assert {row["component"] for row in rows} == {spec["component"] for spec in weights}
    for row in rows:
        assert 0 <= int(row["top10_overlap"]) <= prioritise.TOP_N
        assert -1.0 <= float(row["spearman_rho"]) <= 1.0


def test_terciles_split_96_into_three_thirds():
    bands = [figures._tercile(rank, 96) for rank in range(1, 97)]
    assert bands.count(0) == 32
    assert bands.count(1) == 32
    assert bands.count(2) == 32


# --- Task-43: findings pack (reliability map, publisher map, sensitivity chart, tables,
# docs/FINDINGS.md) ---


def test_map_reliability_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "map_reliability.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 1000


def test_map_publishers_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "map_publishers.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 1000


def test_chart_sensitivity_png_dimensions_and_not_flat(built):
    path = built["figures_dir"] / "chart_sensitivity.png"
    assert path.is_file()
    image = Image.open(path)
    assert image.size == (2000, 3200)
    assert _distinct_colors(path) > 10


def test_top10_has_10_rows_in_rank_order_matching_priority(built):
    path = built["tables_dir"] / "top10.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert list(rows[0]) == list(figures.TOP10_COLUMNS)
    assert [int(row["rank"]) for row in rows] == list(range(1, 11))
    priority_rows = figures.load_priority()[:10]
    for top_row, priority_row in zip(rows, priority_rows, strict=True):
        assert top_row["name"] == priority_row["name"]
        assert top_row["score"] == priority_row["score"]
        assert top_row["intervention"] == priority_row["intervention"]
    pack_agreement = figures.load_pack_agreement()[int(priority_rows[0]["id"])]
    assert rows[0]["agreement"] == f"{pack_agreement['covered']}/{pack_agreement['available']}"


def test_intervention_counts_sums_to_96(built):
    path = built["tables_dir"] / "intervention_counts.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert sum(int(row["count"]) for row in rows) == 96


def test_publisher_lines_summary_has_five_rows_summing_to_96(built):
    path = built["tables_dir"] / "publisher_lines_summary.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 5
    for row in rows:
        total = (
            int(row["says_covered"]) + int(row["says_not_covered"]) + int(row["not_recorded"])
        )
        assert total == 96


def test_reliability_words_sums_to_96(built):
    path = built["tables_dir"] / "reliability_words.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert sum(int(row["count"]) for row in rows) == 96


def test_findings_md_carries_top10_row1_numbers_and_pooled_auc(built):
    text = figures.FINDINGS_MD.read_text(encoding="utf-8")
    with (built["tables_dir"] / "top10.csv").open(encoding="utf-8", newline="") as handle:
        row1 = next(csv.DictReader(handle))
    assert row1["population"] in text
    assert row1["score"] in text
    with (built["tables_dir"] / "reliability_validation.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        pooled = next(row for row in csv.DictReader(handle) if row["fold"] == "pooled")
    assert pooled["auc"] in text


def test_findings_md_sections_present(built):
    text = figures.FINDINGS_MD.read_text(encoding="utf-8")
    for heading in ("## Methodology", "## Findings", "## Discussion", "## Recommendations"):
        assert heading in text
