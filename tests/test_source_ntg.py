"""Unit tests for pipeline.sources.ntg: NT Government mobile coverage lists."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import pytest

from pipeline.sources import bushtel, ntg

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
BUSHTEL_SNAPSHOT = RAW / "bushtel_community_detail_2026-09-15.json"
NTG_FIXTURE = ROOT / "tests/fixtures/ntg_2026-09-15.csv"
FORBIDDEN_IMPORT = re.compile(r"^(import|from) (pipeline\.sources|spike|requests)", re.MULTILINE)

COLUMNS = [
    "bushtel_id",
    "ntg2022_listed",
    "ntg2022_matched_name",
    "ntg2022_site_type",
    "ntg2022_macro",
    "ntg2022_small",
    "ntg2022_proximity",
    "ntg2022_provider",
    "ntg2022_population",
    "ntg2022_coord_dist_km",
    "ntg2021_with_mobile_listed",
    "ntg2021_mobile_phone",
    "ntg2021_comment",
    "ntg2019_listed",
    "ntg2019_backhaul",
    "ntg2019_provider",
    "ntg2019_coord_dist_km",
    "smallcell_listed",
    "smallcell_provider",
]


@pytest.fixture(scope="module")
def communities():
    return bushtel.load(BUSHTEL_SNAPSHOT)


@pytest.fixture(scope="module")
def frame(communities):
    return ntg.load(
        RAW / "ntg_2019.xlsx",
        RAW / "ntg_2021.xlsx",
        RAW / "ntg_2022.xlsx",
        RAW / "ntg_smallcell.xlsx",
        communities,
    )


def test_shape(frame):
    assert len(COLUMNS) == 19
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    assert list(frame.columns) == COLUMNS


def test_regression_against_fixture(frame):
    with NTG_FIXTURE.open(encoding="utf-8", newline="") as f:
        expected_rows = {int(row["bushtel_id"]): row for row in csv.DictReader(f)}
    got_rows = {row["bushtel_id"]: row for row in frame.to_dict("records")}
    assert sorted(got_rows) == sorted(expected_rows)

    differences = []
    for bushtel_id, expected_row in sorted(expected_rows.items()):
        got_row = got_rows[bushtel_id]
        for column, expected in expected_row.items():
            if column in ("name", "bushtel_id"):
                continue
            if got_row[column] != expected:
                differences.append((bushtel_id, column, expected, got_row[column]))

    first = differences[0] if differences else None
    assert differences == [], f"{len(differences)} differences, first: {first}"


def test_oracle(frame):
    assert (frame["ntg2022_listed"] == "1").sum() == 60
    assert (frame["ntg2022_macro"] == "1").sum() == 46
    assert (frame["ntg2022_small"] == "1").sum() == 3
    assert (frame["ntg2022_proximity"] == "1").sum() == 12
    assert (frame["ntg2021_with_mobile_listed"] == "1").sum() == 57
    assert (frame["ntg2019_listed"] == "1").sum() == 46
    assert (frame["smallcell_listed"] == "1").sum() == 2
    backhaul = Counter(frame["ntg2019_backhaul"])
    assert backhaul["Optic fibre"] == 30
    assert backhaul["Microwave radio"] == 16
    assert backhaul[""] == 50

    by_id = frame.set_index("bushtel_id")
    wadeye = by_id.loc[426]
    assert wadeye["ntg2022_macro"] == "1"
    assert wadeye["ntg2022_provider"] == "TELSTRA"
    assert wadeye["ntg2019_backhaul"] == "Optic fibre"
    assert wadeye["ntg2019_provider"] == "Project 13"

    baniyala = by_id.loc[458]
    assert baniyala["ntg2022_listed"] == "0"
    assert baniyala["ntg2022_macro"] == ""
    assert baniyala["ntg2021_mobile_phone"] == "Not recorded"


def test_missing_xlsx_names_fetch_command(tmp_path, communities):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.ntg"):
        ntg.load(
            RAW / "ntg_2019.xlsx",
            RAW / "ntg_2021.xlsx",
            tmp_path / "nope.xlsx",
            RAW / "ntg_smallcell.xlsx",
            communities,
        )


def test_layer_rules():
    for module in ("rrl", "ntg"):
        source_text = (ROOT / f"pipeline/sources/{module}.py").read_text(encoding="utf-8")
        assert not FORBIDDEN_IMPORT.search(source_text), module
