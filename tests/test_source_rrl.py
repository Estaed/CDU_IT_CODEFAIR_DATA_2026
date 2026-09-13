"""Unit tests for pipeline.sources.rrl: ACMA licensed cellular sites near each community."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import pytest

from pipeline.sources import bushtel, rrl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
RRL_ZIP = RAW / "spectra_rrl_2026-09-12.zip"
BUSHTEL_SNAPSHOT = RAW / "bushtel_community_detail_2026-09-12.json"
RRL_FIXTURE = ROOT / "tests/fixtures/rrl_2026-09-12.csv"
SITES_FIXTURE = ROOT / "tests/fixtures/rrl_sites_nt_2026-09-12.csv"
FORBIDDEN_IMPORT = re.compile(r"^(import|from) (pipeline\.sources|spike|requests)", re.MULTILINE)

GROUPS = ["telstra", "optus", "tpg", "jv"]
COLUMNS = (
    ["bushtel_id"]
    + [f"{group}_within_{t}km" for group in GROUPS for t in (5, 10, 40)]
    + [f"any_within_{t}km" for t in (5, 10, 40)]
    + ["nearest_site_km", "nearest_site_carrier", "nearest_site_name", "nearest_site_precision"]
)


@pytest.fixture(scope="module")
def communities():
    return bushtel.load(BUSHTEL_SNAPSHOT)


@pytest.fixture(scope="module")
def frame(communities):
    if not RRL_ZIP.exists():
        raise AssertionError(
            f"missing snapshot {RRL_ZIP}; run "
            "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.rrl"
        )
    return rrl.load(RRL_ZIP, communities)


def test_shape(frame):
    assert len(COLUMNS) == 20
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    assert list(frame.columns) == COLUMNS


def test_regression_against_fixture(frame):
    with RRL_FIXTURE.open(encoding="utf-8", newline="") as f:
        expected_rows = {int(row["bushtel_id"]): row for row in csv.DictReader(f)}
    got_rows = {row["bushtel_id"]: row for row in frame.to_dict("records")}
    assert sorted(got_rows) == sorted(expected_rows)

    differences = []
    for bushtel_id, expected_row in sorted(expected_rows.items()):
        got_row = got_rows[bushtel_id]
        for column, expected in expected_row.items():
            if column in ("name", "bushtel_id"):
                continue
            got = got_row[column]
            if column == "nearest_site_km":
                same = round(float(got), 3) == round(float(expected), 3)
            else:
                same = got == expected
            if not same:
                differences.append((bushtel_id, column, expected, got))

    first = differences[0] if differences else None
    assert differences == [], f"{len(differences)} differences, first: {first}"


def test_oracle(frame):
    assert (frame["any_within_5km"] == "1").sum() == 78
    assert (frame["any_within_10km"] == "1").sum() == 83
    assert (frame["any_within_40km"] == "1").sum() == 96
    carriers = Counter(frame["nearest_site_carrier"])
    assert carriers["Telstra"] == 93
    assert carriers["Optus"] == 3

    by_id = frame.set_index("bushtel_id")
    wadeye = by_id.loc[426]
    assert wadeye["nearest_site_km"] == "0.064"
    assert wadeye["nearest_site_name"] == "74 Perdjert Street WADEYE"
    assert wadeye["nearest_site_carrier"] == "Telstra"
    assert wadeye["nearest_site_precision"] == "Unknown"

    baniyala = by_id.loc[458]
    assert baniyala["nearest_site_km"] == "0.17"
    assert baniyala["nearest_site_name"] == "19 m Mast, Baniyala Community EAST ARNHEM"


def test_sites_table(tmp_path):
    table = rrl.sites(RRL_ZIP)
    assert len(table) == 576
    written = tmp_path / "s.csv"
    rrl.write_sites(table, written)
    assert written.read_bytes() == SITES_FIXTURE.read_bytes()


def test_missing_zip_names_fetch_command(tmp_path, communities):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.rrl"):
        rrl.load(tmp_path / "nope.zip", communities)


def test_layer_rules():
    source_text = (ROOT / "pipeline/sources/rrl.py").read_text(encoding="utf-8")
    assert not FORBIDDEN_IMPORT.search(source_text)
