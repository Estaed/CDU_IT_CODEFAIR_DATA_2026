"""Unit tests for pipeline.changes: diffing two capability-table snapshots."""

from __future__ import annotations

from pipeline import changes

BASE_ROW = {
    "bushtel_id": "1",
    "name": "Testville",
    "svc_health_centre": "Y",
    "svc_school": "Y",
    "svc_store": "N",
    "svc_police": "N",
    "svc_library": "N",
    "svc_council_centre": "N",
    "svc_employment": "N",
    "svc_wifi": "Y",
    "svc_stand": "N",
    "svc_aerodrome": "N",
    "wifi_comment": "Behind the store, 9am-5pm.",
    "road_access_comment": "Sealed road.",
    "lat": "-12.345",
    "lon": "130.987",
    "best_path": "satellite",
    "telehealth_video": "degraded",
    "school_video_meeting": "works",
    "mygov_text": "works",
    "voice_sms": "works",
    "mobile_says": "accc=1;ntg2022=1;rrl5=1;bushtel=1",
}


def _row(**overrides: str) -> dict:
    return {**BASE_ROW, **overrides}


def test_no_change_is_empty():
    older = [_row()]
    newer = [_row()]
    assert changes.diff_tables(older, newer) == []


def test_one_verdict_flip_is_one_row():
    older = [_row()]
    newer = [_row(telehealth_video="fails")]
    result = changes.diff_tables(older, newer)
    assert len(result) == 1
    row = result[0]
    assert row["column"] == "telehealth_video"
    assert row["before"] == "degraded"
    assert row["after"] == "fails"
    assert changes.sentence(row) == "Telehealth video: degraded -> fails"


def test_community_only_in_newer_table():
    older = [_row(bushtel_id="1")]
    newer = [_row(bushtel_id="1"), _row(bushtel_id="2", name="Newtown")]
    result = changes.diff_tables(older, newer)
    assert len(result) == 1
    assert result[0]["column"] == "bushtel_id"
    assert result[0]["bushtel_id"] == "2"
    assert result[0]["name"] == "Newtown"


def test_community_only_in_older_table():
    older = [_row(bushtel_id="1"), _row(bushtel_id="2", name="Oldtown")]
    newer = [_row(bushtel_id="1")]
    result = changes.diff_tables(older, newer)
    assert len(result) == 1
    assert result[0]["column"] == "bushtel_id"
    assert result[0]["bushtel_id"] == "2"
    assert result[0]["before"] == "present"
    assert result[0]["after"] == ""


def test_ignored_columns_never_produce_a_row():
    older = [_row()]
    newer = [
        _row(
            wifi_comment="Different opening hours entirely.",
            road_access_comment="Now unsealed.",
            lat="-12.999",
            lon="131.111",
        )
    ]
    assert changes.diff_tables(older, newer) == []


def test_says_covered_flag_flip():
    older = [_row(mobile_says="accc=1;ntg2022=1;rrl5=1;bushtel=1")]
    newer = [_row(mobile_says="accc=1;ntg2022=1;rrl5=1;bushtel=0")]
    result = changes.diff_tables(older, newer)
    assert len(result) == 1
    assert result[0]["column"] == "bushtel_says_covered"
    assert result[0]["before"] == "1"
    assert result[0]["after"] == "0"


def test_svc_flag_sentence_wording():
    older = [_row(svc_wifi="Y")]
    newer = [_row(svc_wifi="N")]
    row = changes.diff_tables(older, newer)[0]
    assert changes.sentence(row) == "Public Wi-Fi no longer listed"

    older = [_row(svc_wifi="N")]
    newer = [_row(svc_wifi="Y")]
    row = changes.diff_tables(older, newer)[0]
    assert changes.sentence(row) == "Public Wi-Fi now listed"


def test_newest_pair_orders_oldest_first(tmp_path):
    (tmp_path / "capability_table_2026-09-12.csv").write_text("x", encoding="utf-8")
    (tmp_path / "capability_table_2026-09-15.csv").write_text("x", encoding="utf-8")
    (tmp_path / "capability_table_2026-09-01.csv").write_text("x", encoding="utf-8")
    pair = changes.newest_pair(tmp_path)
    assert pair is not None
    older, newer = pair
    assert older.name == "capability_table_2026-09-12.csv"
    assert newer.name == "capability_table_2026-09-15.csv"


def test_newest_pair_none_when_fewer_than_two(tmp_path):
    (tmp_path / "capability_table_2026-09-12.csv").write_text("x", encoding="utf-8")
    assert changes.newest_pair(tmp_path) is None


def test_date_of():
    from pathlib import Path

    assert changes.date_of(Path("data/out/history/capability_table_2026-09-15.csv")) == "2026-09-15"
