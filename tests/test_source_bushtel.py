"""Unit tests for pipeline.sources.bushtel: identity, services, capability flags."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

from pipeline.sources import bushtel

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "data/raw/bushtel_community_detail_2026-09-15.json"
BUSHTEL_FIXTURE = ROOT / "tests/fixtures/bushtel_2026-09-15.csv"
COMMUNITIES_FIXTURE = ROOT / "tests/fixtures/communities_2026-09-15.csv"

IDENTITY_COLUMNS = [
    "bushtel_id",
    "name",
    "aliases",
    "community_type",
    "nt_region",
    "population_abs2021",
    "sa1_code",
    "lat",
    "lon",
]


def _to_iso(value: str) -> str:
    """Convert 'dd/mm/yyyy, hh:mm:ss AM' to 'yyyy-mm-dd'; empty stays empty."""
    if not value or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value  # the 2026-09-15 fixture already holds ISO dates
    date_part = value.split(",", 1)[0].strip()
    day, month, year = date_part.split("/")
    return f"{year}-{month}-{day}"


def _load_fixture_join() -> dict[int, dict[str, str]]:
    with BUSHTEL_FIXTURE.open(encoding="utf-8", newline="") as f:
        bushtel_rows = {int(row["bushtel_id"]): row for row in csv.DictReader(f)}
    with COMMUNITIES_FIXTURE.open(encoding="utf-8", newline="") as f:
        community_rows = {int(row["bushtel_id"]): row for row in csv.DictReader(f)}

    joined: dict[int, dict[str, str]] = {}
    for bushtel_id, row in bushtel_rows.items():
        merged = dict(row)
        merged.update(community_rows.get(bushtel_id, {}))
        joined[bushtel_id] = merged
    return joined


@pytest.fixture(scope="module")
def frame():
    if not SNAPSHOT.exists():
        raise AssertionError(
            f"missing snapshot {SNAPSHOT}; run "
            "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel"
        )
    return bushtel.load(SNAPSHOT)


def test_shape(frame):
    assert len(frame) == 96
    assert frame["bushtel_id"].is_unique
    columns = list(frame.columns)
    assert columns[: len(IDENTITY_COLUMNS)] == IDENTITY_COLUMNS


def test_regression_against_fixtures(frame):
    joined = _load_fixture_join()
    frame_by_id = frame.set_index("bushtel_id")

    differences = []
    for bushtel_id, expected_row in joined.items():
        if bushtel_id not in frame_by_id.index:
            differences.append((bushtel_id, "bushtel_id", "present", "missing"))
            continue
        got_row = frame_by_id.loc[bushtel_id]
        for column, expected in expected_row.items():
            if column in ("spike20", "bushtel_id") or column not in frame_by_id.columns:
                continue
            expected_value = _to_iso(expected) if column == "profile_last_updated" else expected
            got_value = str(got_row[column])
            if expected_value != got_value:
                differences.append((bushtel_id, column, expected_value, got_value))

    message = f"{len(differences)} differences, first ten: {differences[:10]}"
    assert differences == [], message


def test_wadeye_and_baniyala(frame):
    by_id = frame.set_index("bushtel_id")

    wadeye = by_id.loc[426]
    assert wadeye["svc_health_centre"] == "Y"
    assert wadeye["svc_wifi"] == "Y"
    assert wadeye["road_seasonal_cut"] == "1"
    assert wadeye["profile_last_updated"] == "2026-07-03"
    assert wadeye["nt_region"] == "TOP END"
    assert wadeye["population_abs2021"] == 2259

    baniyala = by_id.loc[458]
    assert baniyala["svc_mobile_phone"] == ""
    assert baniyala["profile_last_updated"] == "2025-08-06"


def test_missing_snapshot_names_fetch_command(tmp_path):
    with pytest.raises(FileNotFoundError, match="pipeline.fetch.bushtel"):
        bushtel.load(tmp_path / "nope.json")


def test_layer_rules():
    source_text = (ROOT / "pipeline/sources/bushtel.py").read_text(encoding="utf-8")
    forbidden = re.compile(r"^(import|from) (pipeline\.sources|spike|requests)", re.MULTILINE)
    assert not forbidden.search(source_text)

    for path in (ROOT / "pipeline").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "import requests" in text:
            relative = path.relative_to(ROOT).as_posix()
            assert relative.startswith("pipeline/fetch/"), (
                f"{relative} imports requests outside pipeline/fetch/"
            )
