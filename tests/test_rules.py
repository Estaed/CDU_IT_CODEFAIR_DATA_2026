"""Unit tests for pipeline.rules: pure functions over plain dicts (Contract, Task-00)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pipeline import rules

ROOT = Path(__file__).resolve().parent.parent

ROW_KEYS = [
    "nbn_technology",
    "in_fixed_line",
    "in_fixed_wireless",
    "carriers_4g_count",
    "telstra_4g_2025",
    "optus_4g_2025",
    "tpg_4g_2025",
    "dist_km_telstra_4g",
    "dist_km_optus_4g",
    "dist_km_tpg_4g",
    "ntg2022_listed",
    "ntg2022_macro",
    "ntg2022_small",
    "ntg2022_proximity",
    "ntg2022_provider",
    "ntg2019_backhaul",
    "any_within_5km",
    "nearest_site_km",
    "nearest_site_carrier",
    "nearest_site_name",
    "svc_mobile_phone",
    "svc_health_centre",
    "svc_school",
    "svc_store",
    "svc_police",
    "svc_library",
    "svc_council_centre",
    "svc_employment",
    "svc_wifi",
    "svc_stand",
    "svc_aerodrome",
    "road_seasonal_cut",
    "profile_last_updated",
    "bushtel_id",
    "name",
    "aliases",
    "community_type",
    "nt_region",
    "population_abs2021",
    "lat",
    "lon",
]


def make_row(**overrides: str) -> dict[str, str]:
    row = dict.fromkeys(ROW_KEYS, "")
    row.update(
        nbn_technology="SATELLITE_RESIDUAL",
        svc_health_centre="Y",
        svc_school="Y",
        in_fixed_line="0",
        in_fixed_wireless="0",
        carriers_4g_count="0",
        ntg2022_listed="0",
        any_within_5km="0",
    )
    row.update(overrides)
    return row


@pytest.fixture(scope="module")
def thresholds():
    return rules.load_thresholds(ROOT / "pipeline/thresholds.csv")


def test_fig():
    assert rules.fig(5000, "kbps") == "`5,000 kbps`"
    assert rules.fig(664.9, "ms") == "`664.9 ms`"
    assert rules.fig(100, "ms") == "`100 ms`"


def test_join_names():
    assert rules.join_names([]) == "A carrier"
    assert rules.join_names(["Telstra"]) == "Telstra"
    assert rules.join_names(["Telstra", "Optus"]) == "Telstra and Optus"
    assert rules.join_names(["Telstra", "Optus", "TPG"]) == "Telstra, Optus and TPG"


def test_agreement():
    assert rules.agreement(
        [
            {"says_covered": "covered"},
            {"says_covered": "covered"},
            {"says_covered": "covered"},
            {"says_covered": "covered"},
        ]
    ) == (4, 4)
    assert rules.agreement(
        [
            {"says_covered": "covered"},
            {"says_covered": "not-covered"},
            {"says_covered": "not-covered"},
            {"says_covered": "not-recorded"},
        ]
    ) == (1, 3)
    assert rules.agreement(
        [
            {"says_covered": "covered"},
            {"says_covered": "covered"},
            {"says_covered": "not-covered"},
            {"says_covered": "not-covered"},
        ]
    ) == (2, 4)


def test_load_thresholds(thresholds):
    entry = thresholds["requirement.telehealth_video.latency"]
    assert entry["value"] == 100.0
    assert "healthdirect" in entry["source"]
    assert thresholds["requirement.mygov_banking.bandwidth_down"]["value"] is None


def test_rules_is_stdlib_only():
    text = (ROOT / "pipeline/rules.py").read_text(encoding="utf-8")
    forbidden = re.compile(r"^(import|from) (pandas|geopandas|shapely|numpy)", re.MULTILINE)
    assert forbidden.search(text) is None


# --- Eight hand-built test rows (Contract, "Eight hand-built test rows") ---


def test_wadeye_shape_1111(thresholds):
    row = make_row(
        carriers_4g_count="1",
        telstra_4g_2025="1",
        ntg2022_listed="1",
        any_within_5km="1",
        svc_mobile_phone="Y",
    )
    telehealth = rules.telehealth_video(row, thresholds)
    assert telehealth["verdict"] == "degraded"
    assert telehealth["reason"] == "Latency `664.9 ms` on satellite vs `100 ms` required"
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "works"
    assert voice["reason"] == (
        "Telstra 4G is predicted here and the community is on the 2022 list"
    )
    assert rules.best_path(row) == "terrestrial_mobile"


def test_all_zero_0000(thresholds):
    row = make_row()
    telehealth = rules.telehealth_video(row, thresholds)
    assert telehealth["verdict"] == "fails"
    assert telehealth["reason"] == (
        "Latency `664.9 ms` on satellite vs `100 ms` required; no carrier 4G polygon"
    )
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "fails"
    assert voice["reason"] == (
        "No carrier 4G polygon and not on the 2022 list; no public WiFi recorded"
    )
    assert rules.best_path(row) == "satellite"


def test_1011(thresholds):
    row = make_row(
        carriers_4g_count="1",
        telstra_4g_2025="1",
        ntg2022_listed="0",
        any_within_5km="1",
        svc_mobile_phone="Y",
    )
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "works"
    assert voice["reason"] == "Telstra 4G is predicted here; the community is not on the 2022 list"


def test_baniyala_shape_0010(thresholds):
    row = make_row(
        carriers_4g_count="0",
        ntg2022_listed="0",
        any_within_5km="1",
        svc_mobile_phone="",
    )
    telehealth = rules.telehealth_video(row, thresholds)
    assert telehealth["verdict"] == "fails"
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "fails"
    assert voice["reason"] == (
        "No carrier 4G polygon and not on the 2022 list; no public WiFi recorded"
    )
    publishers = [
        {"says_covered": "not-covered"},
        {"says_covered": "not-covered"},
        {"says_covered": "covered"},
        {"says_covered": "not-recorded"},
    ]
    assert rules.agreement(publishers) == (1, 3)


def test_1101(thresholds):
    row = make_row(
        carriers_4g_count="1",
        telstra_4g_2025="1",
        ntg2022_listed="1",
        any_within_5km="0",
        svc_mobile_phone="Y",
    )
    assert rules.best_path(row) == "satellite"
    telehealth = rules.telehealth_video(row, thresholds)
    assert telehealth["verdict"] == "degraded"


def test_0011(thresholds):
    row = make_row(
        carriers_4g_count="0",
        ntg2022_listed="0",
        any_within_5km="1",
        svc_mobile_phone="Y",
    )
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "fails"
    publishers = [
        {"says_covered": "not-covered"},
        {"says_covered": "not-covered"},
        {"says_covered": "covered"},
        {"says_covered": "covered"},
    ]
    assert rules.agreement(publishers) == (2, 4)


def test_yirrkala_fixed_line(thresholds):
    row = make_row(
        nbn_technology="FIXED_LINE",
        in_fixed_line="1",
        carriers_4g_count="1",
        telstra_4g_2025="1",
        ntg2022_listed="1",
        any_within_5km="1",
        svc_mobile_phone="Y",
    )
    assert rules.best_path(row) == "fixed_line"
    telehealth = rules.telehealth_video(row, thresholds)
    assert telehealth["verdict"] == "works"
    assert telehealth["reason"] == (
        "Fixed line footprint contains the community; latency is under the `100 ms` "
        "requirement on fixed access"
    )
    assert telehealth["assumption"] == (
        "No fixed-access latency figure is sourced yet; fixed access is treated as under "
        "`100 ms` until the ACCC figure is added."
    )
    school = rules.school_video_meeting(row, thresholds)
    assert school["verdict"] == "works"
    assert school["reason"] == (
        "Fixed line footprint contains the community; the `150 kbps` upload requirement "
        "is cleared on fixed access"
    )
    assert "assumption" not in school


def test_wifi_only_voice_0000(thresholds):
    row = make_row(svc_wifi="Y")
    voice = rules.voice_sms(row)
    assert voice["verdict"] == "degraded"
    assert voice["reason"] == "No carrier 4G polygon and not on the 2022 list; public WiFi only"


# --- The satellite-path assumption, and the LEO sentence inside it (Task-40) ---


def test_telehealth_fails_carries_only_the_leo_assumption(thresholds):
    """Task-40: the fails branch gained an assumption; before it there was none."""
    row = make_row()
    result = rules.telehealth_video(row, thresholds)
    assert result["verdict"] == "fails"
    assert result["assumption"] == rules.leo_assumption(thresholds)


def test_telehealth_degraded_has_assumption_with_telstra(thresholds):
    row = make_row(carriers_4g_count="1", telstra_4g_2025="1")
    result = rules.telehealth_video(row, thresholds)
    assert result["verdict"] == "degraded"
    assert result["assumption"] == (
        "Could work over Telstra 4G if latency is under `100 ms`. No measurement exists here. "
        + rules.leo_assumption(thresholds)
    )


def test_leo_threshold_row(thresholds):
    entry = thresholds["capability.leo_satellite.latency"]
    assert entry["value"] == 29.8
    assert entry["unit"] == "ms"
    assert entry["source"] == "ACCC Measuring Broadband Australia release 147/24"
    assert entry["source_url"].startswith("https://www.accc.gov.au/")


def test_leo_sentence_quotes_the_figure_from_the_table(thresholds):
    """The figure is rendered through ``fig``, never typed into the sentence."""
    sentence = rules.leo_assumption(thresholds)
    assert "low-earth-orbit service" in sentence
    assert "`29.8 ms`" in sentence
    assert "29.8" not in rules.LEO_ASSUMPTION


def test_both_satellite_paths_carry_the_leo_sentence_and_no_verdict_moves(thresholds):
    figure = rules.fig(thresholds["capability.leo_satellite.latency"]["value"], "ms")
    degraded = rules.telehealth_video(
        make_row(carriers_4g_count="1", telstra_4g_2025="1"), thresholds
    )
    fails = rules.telehealth_video(make_row(), thresholds)

    assert degraded["verdict"] == "degraded"
    assert fails["verdict"] == "fails"
    for result in (degraded, fails):
        assert figure in result["assumption"]
        # The sentence is an assumption, never part of the reason the verdict rests on.
        assert "low-earth-orbit" not in result["reason"]
    # The release is already cited for the 664.9 ms figure, so no source line is added.
    assert len(fails["sources"]) == 3
    assert len(degraded["sources"]) == 3


def test_fixed_path_telehealth_has_no_leo_sentence(thresholds):
    """Only a satellite path carries it: fixed access is not waiting on a dish."""
    row = make_row(nbn_technology="FIXED_LINE", in_fixed_line="1")
    result = rules.telehealth_video(row, thresholds)
    assert result["verdict"] == "works"
    assert "low-earth-orbit" not in result["assumption"]
