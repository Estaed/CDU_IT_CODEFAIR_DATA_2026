"""Unit tests for pipeline.pack: the interim data pack built from the spike table."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from pipeline import pack, rules

ROOT = Path(__file__).resolve().parent.parent
DATE_RE = re.compile(r"^\d{4}(-\d{2}-\d{2})?$")


def _load_rows() -> list[dict[str, str]]:
    with (ROOT / "spike/out/capability_table.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def thresholds():
    return rules.load_thresholds(ROOT / "pipeline/thresholds.csv")


@pytest.fixture(scope="module")
def data_pack(thresholds):
    rows = _load_rows()
    return pack.build_pack(rows, thresholds, "https://example.invalid/", "2026-09-13")


def _by_id(data_pack, bushtel_id: int) -> dict:
    for community in data_pack["communities"]:
        if community["id"] == bushtel_id:
            return community
    raise AssertionError(f"community {bushtel_id} not found")


def test_pack_header(data_pack):
    assert data_pack["pack_version"] == 1
    assert data_pack["count"] == 96
    assert len(data_pack["communities"]) == 96


def test_communities_sorted_by_id(data_pack):
    ids = [c["id"] for c in data_pack["communities"]]
    assert ids == sorted(ids)


def test_every_dated_field_has_source_and_date(data_pack):
    for community in data_pack["communities"]:
        population = community["population"]
        assert population["source"]
        assert DATE_RE.match(population["date"])
        for publisher in community["publishers"]:
            assert publisher["source"]
            assert DATE_RE.match(publisher["date"])
        for service in community["services"]:
            for source in service["sources"]:
                assert source["source"]
                assert DATE_RE.match(source["date"])
        for flag in community["flags"]:
            assert flag["source"]
            assert DATE_RE.match(flag["date"])


def test_publisher_order_and_kinds(data_pack):
    for community in data_pack["communities"]:
        kinds = [p["kind"] for p in community["publishers"]]
        assert kinds == ["predicted", "listed", "licensed", "portal"]


def test_says_covered_values(data_pack):
    allowed = {"covered", "not-covered", "not-recorded"}
    for community in data_pack["communities"]:
        for publisher in community["publishers"]:
            assert publisher["says_covered"] in allowed


def test_verdict_distributions(data_pack):
    counts = {
        "telehealth_video": {"works": 0, "degraded": 0, "fails": 0, "nodata": 0},
        "school_video_meeting": {"works": 0, "degraded": 0, "fails": 0, "nodata": 0},
        "mygov_text": {"works": 0, "degraded": 0, "fails": 0, "nodata": 0},
        "voice_sms": {"works": 0, "degraded": 0, "fails": 0, "nodata": 0},
    }
    for community in data_pack["communities"]:
        for service in community["services"]:
            counts[service["service"]][service["verdict"]] += 1

    assert counts["telehealth_video"] == {"works": 1, "degraded": 58, "fails": 11, "nodata": 26}
    assert counts["school_video_meeting"] == {"works": 1, "degraded": 69, "fails": 0, "nodata": 26}
    assert counts["mygov_text"] == {"works": 96, "degraded": 0, "fails": 0, "nodata": 0}
    assert counts["voice_sms"] == {"works": 74, "degraded": 5, "fails": 17, "nodata": 0}


def test_wadeye_426(data_pack):
    wadeye = _by_id(data_pack, 426)
    verdicts = [s["verdict"] for s in wadeye["services"]]
    assert verdicts == ["degraded", "degraded", "works", "works"]
    assert wadeye["path"]["value"] == "terrestrial_mobile"
    for publisher in wadeye["publishers"]:
        assert publisher["says_covered"] == "covered"
    assert wadeye["agreement"]["covered"] == 4
    assert wadeye["agreement"]["available"] == 4
    assert wadeye["agreement"]["note"] == "Sources agree"
    assert wadeye["population"]["value"] == 2259
    assert wadeye["population"]["date"] == "2026-07-03"
    assert "Health centre" in [p["name"] for p in wadeye["present"]]


def test_baniyala_458(data_pack):
    baniyala = _by_id(data_pack, 458)
    telehealth = next(s for s in baniyala["services"] if s["service"] == "telehealth_video")
    assert telehealth["verdict"] == "fails"
    assert baniyala["agreement"]["covered"] == 1
    assert baniyala["agreement"]["available"] == 3
    assert baniyala["agreement"]["note"] == "Sources disagree"
    assert baniyala["publishers"][3]["says_covered"] == "not-recorded"
    assert baniyala["population"]["date"] == "2025-08-06"


def test_yirrkala_576(data_pack):
    yirrkala = _by_id(data_pack, 576)
    verdicts = [s["verdict"] for s in yirrkala["services"]]
    assert verdicts == ["works", "works", "works", "works"]
    assert yirrkala["path"]["value"] == "fixed_line"


def test_no_bushtel_free_text(data_pack):
    serialised = json.dumps(data_pack, ensure_ascii=False)
    assert "Mon - Sat" not in serialised
    assert "Daly River Road" not in serialised
    assert "Catholic College" not in serialised
    assert '"wifi_comment"' not in serialised
    assert '"road_access_comment"' not in serialised
    assert '"stand_comment"' not in serialised


def test_actions_empty(data_pack):
    for community in data_pack["communities"]:
        assert community["actions"] == []


def test_bushtel_text_allowed_is_false():
    assert pack.BUSHTEL_TEXT_ALLOWED is False


def test_read_constant_team_number():
    text = (ROOT / "constants.md").read_text(encoding="utf-8")
    match = None
    for line in text.splitlines():
        if line.strip().startswith("| `TEAM_NUMBER`"):
            match = line
            break
    assert match is not None
    cells = [cell.strip() for cell in match.strip().strip("|").split("|")]
    expected = cells[1]
    assert pack.read_constant("TEAM_NUMBER") == expected


def test_committed_data_pack_file():
    path = ROOT / "data/out/data_pack.json"
    assert path.exists()
    with path.open(encoding="utf-8") as f:
        committed = json.load(f)
    assert committed["pack_version"] == 1
    assert committed["count"] == 96
    assert path.stat().st_size <= 307_200
