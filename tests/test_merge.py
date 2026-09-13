"""Unit tests for pipeline.merge: the five-source join and the verdict columns it fills.

# The fixture tests/fixtures/capability_table_2026-09-12.csv is a byte-for-byte copy of the
# spike's frozen 2026-09-12 table (Task-05, main-loop decision 3).
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
import pytest

from pipeline import rules
from pipeline.merge import merge

ROOT = Path(__file__).resolve().parent.parent

BUSHTEL_FIXTURE = ROOT / "tests/fixtures/bushtel_2026-09-12.csv"
NBN_FIXTURE = ROOT / "tests/fixtures/nbn_2026-09-12.csv"
ACCC_FIXTURE = ROOT / "tests/fixtures/accc_2026-09-12.csv"
RRL_FIXTURE = ROOT / "tests/fixtures/rrl_2026-09-12.csv"
NTG_FIXTURE = ROOT / "tests/fixtures/ntg_2026-09-12.csv"
COMMUNITIES_FIXTURE = ROOT / "tests/fixtures/communities_2026-09-12.csv"
THRESHOLDS = ROOT / "pipeline/thresholds.csv"
CAPABILITY_FIXTURE = ROOT / "tests/fixtures/capability_table_2026-09-12.csv"

# spike20: only present in the spike's fixture, not produced by the pipeline.
# telehealth_reason: the pipeline writes the rules' reason sentence; the frozen table has a
# debug string ("fixed=SATELLITE_RESIDUAL latency=..."). Neither is comparable.
EXCLUDED = ("spike20", "telehealth_reason")

VERDICT_MAP = {"GREEN": "works", "AMBER": "degraded", "RED": "fails", "n/a": "nodata"}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _bushtel_frame() -> pd.DataFrame:
    # The frozen BushTel lane wrote identity (aliases, type, region, population, sa1,
    # lat, lon) to communities_*.csv and the rest to bushtel_*.csv; the source module
    # emits both in one frame, so the fixture is rebuilt the same way here.
    identity = _read(COMMUNITIES_FIXTURE).drop(columns=["name", "spike20"])
    return identity.merge(_read(BUSHTEL_FIXTURE), on="bushtel_id", how="left")


@pytest.fixture(scope="module")
def sources():
    return {
        "bushtel": _bushtel_frame(),
        "nbn": _read(NBN_FIXTURE),
        "accc": _read(ACCC_FIXTURE),
        "rrl": _read(RRL_FIXTURE),
        "ntg": _read(NTG_FIXTURE),
    }


@pytest.fixture(scope="module")
def thresholds():
    return rules.load_thresholds(THRESHOLDS)


@pytest.fixture(scope="module")
def frame(sources, thresholds):
    return merge(
        sources["bushtel"],
        sources["nbn"],
        sources["accc"],
        sources["rrl"],
        sources["ntg"],
        thresholds,
    )


def _load_fixture_rows() -> list[dict[str, str]]:
    with CAPABILITY_FIXTURE.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _fixture_columns() -> list[str]:
    with CAPABILITY_FIXTURE.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


def _frame_by_id(frame: pd.DataFrame) -> pd.DataFrame:
    # Normalise the join key to string regardless of merge()'s internal dtype.
    return frame.set_index(frame["bushtel_id"].astype(str))


def test_shape(frame):
    assert len(frame) == 96
    ids = frame["bushtel_id"].astype(str)
    assert ids.is_unique
    assert list(ids) == sorted(ids, key=int)


def test_columns(frame):
    expected = (set(_fixture_columns()) - {"spike20"}) | {"best_path"}
    assert set(frame.columns) == expected


def test_regression_against_fixture(frame):
    fixture_rows = _load_fixture_rows()
    frame_by_id = _frame_by_id(frame)
    shared_columns = [c for c in _fixture_columns() if c not in EXCLUDED and c != "spike20"]

    differences = []
    for expected_row in fixture_rows:
        bushtel_id = expected_row["bushtel_id"]
        got_row = frame_by_id.loc[bushtel_id]
        for column in shared_columns:
            expected = expected_row[column]
            if column in ("telehealth_video", "school_video_meeting", "mygov_text", "voice_sms"):
                expected = VERDICT_MAP.get(expected, expected)
            got = got_row[column]
            if str(got) != str(expected):
                differences.append((bushtel_id, column, expected, got))
                break
        if differences:
            break

    if differences:
        pytest.fail(f"first difference: {differences[0]}")


def test_telehealth_video_distribution(frame):
    counts = frame["telehealth_video"].value_counts()
    assert counts.get("works", 0) == 1
    assert counts.get("degraded", 0) == 58
    assert counts.get("fails", 0) == 11
    assert counts.get("nodata", 0) == 26


def test_mobile_sources_disagree_sum(frame):
    assert frame["mobile_sources_disagree"].astype(int).sum() == 31


def test_best_path_satellite_count(frame):
    assert (frame["best_path"] == "satellite").sum() == 29


def test_missing_source_row_still_yields_96_rows(sources, thresholds):
    nbn = sources["nbn"]
    nbn_missing = nbn[nbn["bushtel_id"] != nbn["bushtel_id"].iloc[0]]
    result = merge(
        sources["bushtel"],
        nbn_missing,
        sources["accc"],
        sources["rrl"],
        sources["ntg"],
        thresholds,
    )
    assert len(result) == 96


def test_layer_rules():
    text = Path(ROOT / "pipeline/merge.py").read_text(encoding="utf-8")
    for line in text.splitlines():
        assert not re.match(r"^(import|from) (requests|pipeline\.fetch)", line)
    assert "spike" not in text
