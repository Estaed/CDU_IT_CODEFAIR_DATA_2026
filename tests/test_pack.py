"""Unit tests for pipeline.pack: the data pack built from the pipeline capability table."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from pipeline import pack, prioritise, rules

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data/out/capability_table.csv"
TASK00_PACK = ROOT / "tests/fixtures/data_pack_task00.json"
DATE_RE = re.compile(r"^\d{4}(-\d{2}-\d{2})?$")


def _load_rows() -> list[dict[str, str]]:
    if not TABLE.exists():
        raise AssertionError(
            f"missing {TABLE}; run "
            "PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py"
        )
    with TABLE.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def thresholds():
    return rules.load_thresholds(ROOT / "pipeline/thresholds.csv")


@pytest.fixture(scope="module")
def data_pack(thresholds):
    rows = _load_rows()
    return pack.build_pack(rows, thresholds, "https://example.invalid/", "DIC005", "2026-09-13")


def _cited(data_pack, line: dict) -> dict:
    """The header entry a dated line points at; every line carries an id, never a name."""
    assert "source" not in line and "date" not in line
    return data_pack["sources"][line["src"]]


def _by_id(data_pack, bushtel_id: int) -> dict:
    for community in data_pack["communities"]:
        if community["id"] == bushtel_id:
            return community
    raise AssertionError(f"community {bushtel_id} not found")


def test_pack_header(data_pack):
    assert data_pack["pack_version"] == 2
    assert data_pack["count"] == 96
    assert len(data_pack["communities"]) == 96


def test_source_table_ids_and_fields(data_pack):
    sources = data_pack["sources"]
    assert list(sources) == [f"s{index}" for index in range(1, len(sources) + 1)]
    pairs = [(entry["source"], entry["date"]) for entry in sources.values()]
    assert pairs == sorted(pairs)
    assert len(set(pairs)) == len(pairs)
    # Only the rule-path labels and the unpublished requirement may go without a URL.
    without_url = {entry["source"] for entry in sources.values() if "url" not in entry}
    assert all(
        name.endswith(f", {rules.RULE_NAME}") or name == "none published"
        for name in without_url
    ), without_url


def test_communities_sorted_by_id(data_pack):
    ids = [c["id"] for c in data_pack["communities"]]
    assert ids == sorted(ids)


def test_every_dated_field_has_source_and_date(data_pack):
    for community in data_pack["communities"]:
        for line in pack.dated_lines(community):
            entry = _cited(data_pack, line)
            assert entry["source"]
            assert DATE_RE.match(entry["date"])
    assert DATE_RE.match(data_pack["communities"][0]["path"]["date"])


def test_publisher_order_and_kinds(data_pack):
    for community in data_pack["communities"]:
        kinds = [p["kind"] for p in community["publishers"]]
        assert kinds == ["predicted", "listed", "licensed", "portal", "measured"]


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
    for publisher in wadeye["publishers"][:4]:
        assert publisher["says_covered"] == "covered"
    # The Audit's nearest non-alignment tile is 142 km away: it records nothing here.
    assert wadeye["publishers"][4]["says_covered"] == "not-recorded"
    assert wadeye["agreement"]["covered"] == 4
    assert wadeye["agreement"]["available"] == 4
    assert wadeye["agreement"]["note"] == "Sources agree"
    assert wadeye["population"]["value"] == 2259
    assert _cited(data_pack, wadeye["population"])["date"] == "2026-07-03"
    assert "Health centre" in [p["name"] for p in wadeye["present"]]


def test_baniyala_458(data_pack):
    baniyala = _by_id(data_pack, 458)
    telehealth = next(s for s in baniyala["services"] if s["service"] == "telehealth_video")
    assert telehealth["verdict"] == "fails"
    assert baniyala["agreement"]["covered"] == 1
    assert baniyala["agreement"]["available"] == 3
    assert baniyala["agreement"]["note"] == "Sources disagree"
    assert baniyala["publishers"][3]["says_covered"] == "not-recorded"
    assert _cited(data_pack, baniyala["population"])["date"] == "2025-08-06"


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


def test_verdicts_and_reasons_match_task00_pack(data_pack):
    """Moving off the frozen interim table must not change a verdict or a sentence."""
    with TASK00_PACK.open(encoding="utf-8") as f:
        task00 = json.load(f)

    def services(entry: dict) -> dict:
        return {
            community["id"]: [
                (service["service"], service["verdict"], service["reason"])
                for service in community["services"]
            ]
            for community in entry["communities"]
        }

    assert services(data_pack) == services(task00)


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
    assert committed["pack_version"] == 2
    assert committed["count"] == 96
    assert path.stat().st_size <= 512_000


def test_filters_order_labels_and_counts(data_pack):
    filters = data_pack["filters"]
    ids_and_labels = [(entry["id"], entry["label"]) for entry in filters]
    assert ids_and_labels == [
        ("all", "All"),
        ("clinic-no-terrestrial", "Clinic, no terrestrial path"),
        ("carrier-yes-list-no", "Carrier says covered, list does not"),
        ("licensed-no-map", "Licensed mast, no coverage map"),
    ]
    counts = {entry["id"]: len(entry["ids"]) for entry in filters}
    assert counts == {
        "all": 96,
        "clinic-no-terrestrial": 12,
        "carrier-yes-list-no": 14,
        "licensed-no-map": 11,
    }


def test_filter_ids_are_community_ids(data_pack):
    all_ids = {community["id"] for community in data_pack["communities"]}
    filters_by_id = {entry["id"]: entry["ids"] for entry in data_pack["filters"]}
    for ids in filters_by_id.values():
        assert set(ids) <= all_ids
    assert filters_by_id["all"] == sorted(all_ids)


def test_legend_matches_telehealth_video_counts(data_pack):
    counts = {"works": 0, "degraded": 0, "fails": 0, "nodata": 0}
    for community in data_pack["communities"]:
        service = next(s for s in community["services"] if s["service"] == "telehealth_video")
        counts[service["verdict"]] += 1
    assert counts == {"works": 1, "degraded": 58, "fails": 11, "nodata": 26}
    assert data_pack["legend"] == counts


def test_every_community_has_at_least_one_action(data_pack):
    allowed_who = {"Carrier", "DCDD", "Community"}
    for community in data_pack["communities"]:
        assert len(community["actions"]) >= 1
        for action in community["actions"]:
            assert action["who"] in allowed_who
            assert action["text"]
            assert action["text"].endswith(".")


def test_wadeye_426_actions(data_pack):
    # Sentences copied verbatim from design/screens/community.html lines 164-165.
    wadeye = _by_id(data_pack, 426)
    assert wadeye["actions"] == [
        {"who": "Carrier", "text": "publish measured latency for this site."},
        {"who": "DCDD", "text": "confirm the clinic's enterprise link technology."},
    ]


def test_pack_header_has_outline(data_pack):
    assert isinstance(data_pack["outline"], str)
    assert data_pack["outline"]


def test_header_team_and_attributions(data_pack):
    assert data_pack["team"] == pack.read_constant("TEAM_NUMBER")
    items = data_pack["attributions"]
    assert items
    for item in items:
        assert set(item) == {"text", "licence", "date"}
        assert item["text"]
    texts = [item["text"] for item in items]
    assert "ACCC Mobile Infrastructure Report 2025" in texts


def test_every_community_has_freshness(data_pack):
    sources = data_pack["sources"]
    for community in data_pack["communities"]:
        freshness = community["freshness"]
        assert freshness["source"] in sources
        assert DATE_RE.match(freshness["date"])


def test_layers_key_present_and_src_resolves(data_pack):
    # Task-20: the pack's map layers, each src a key of the pack's own sources table.
    layers = data_pack["layers"]
    assert layers, "pack layers list must not be empty"
    for layer in layers:
        assert layer["kind"] in {"point", "line", "area"}
        assert layer["paths"]
        assert layer["src"] in data_pack["sources"]


def test_layers_ids_and_order(data_pack):
    ids = [layer["id"] for layer in data_pack["layers"]]
    assert ids == ["cov-telstra", "cov-optus", "cov-tpg", "regions-sa3", "towns"]


def test_pack_version_and_count_unaffected_by_layers(data_pack):
    assert data_pack["pack_version"] == 2
    assert data_pack["count"] == 96
    assert len(data_pack["communities"]) == 96


def test_pack_build_imports_no_fetch_module():
    # Layer rule 3: requests lives under pipeline/fetch/ only, so the pack build (and with it
    # scripts/run_pipeline.py) must not import a fetch module even for a constant.
    for name in ("pipeline/pack.py", "pipeline/outline.py", "pipeline/provenance.py"):
        with (ROOT / name).open(encoding="utf-8") as handle:
            text = handle.read()
        assert not re.search(r"^(import|from) pipeline\.fetch", text, re.MULTILINE), name


def test_measured_publisher_line(data_pack):
    """Task-38: the fifth line is the National Audit, and it never says covered."""
    not_covered = []
    for community in data_pack["communities"]:
        assert len(community["publishers"]) == 5
        measured = community["publishers"][4]
        assert measured["publisher"] == "National Audit of Mobile Coverage"
        assert measured["kind"] == "measured"
        assert measured["says_covered"] in {"not-covered", "not-recorded"}
        entry = _cited(data_pack, measured)
        assert entry["source"] == "National Audit non-alignment 2026-05"
        assert entry["date"] == "2026-05-27"
        assert entry["licence"] == "unstated; request on file (OQ2)"
        if measured["says_covered"] == "not-covered":
            not_covered.append(community["id"])
            assert "Drive test found no" in measured["detail"]
        else:
            # Task-39 fills audit5 "0": an audited road within 5 km carrying no
            # non-alignment. Still not a claim of coverage, so still not-recorded.
            assert measured["detail"].startswith(
                ("No audited road within", "Audited road within")
            )

    assert not_covered == [397, 580, 593]


def test_agreement_counts_every_line_that_makes_a_claim(data_pack):
    for community in data_pack["communities"]:
        publishers = community["publishers"]
        available = sum(1 for p in publishers if p["says_covered"] != "not-recorded")
        covered = sum(1 for p in publishers if p["says_covered"] == "covered")
        assert community["agreement"]["available"] == available
        assert community["agreement"]["covered"] == covered


def test_measured_line_turns_three_unanimous_communities_into_disagreements(data_pack):
    for bushtel_id in (397, 580, 593):
        community = _by_id(data_pack, bushtel_id)
        assert community["agreement"] == {
            "covered": 4,
            "available": 5,
            "note": "Sources disagree",
        }


def test_every_community_carries_a_reliability_line(data_pack):
    """Task-39: the word, its probability and the two features that drove it."""
    sources = data_pack["sources"]
    for community in data_pack["communities"]:
        line = community["claim_reliability"]
        assert set(line) == {"word", "p_wrong", "drivers", "src"}
        assert line["word"] in pack.RELIABILITY_WORDS
        # A probability exactly when there is a word to justify: no word, no number.
        assert (line["p_wrong"] is None) == (line["word"] == "none")
        if line["p_wrong"] is not None:
            assert 0.0 <= line["p_wrong"] <= 1.0
        assert len(line["drivers"]) == (0 if line["word"] == "none" else 2)
        assert line["src"] in sources


def test_reliability_line_cites_the_model_and_says_what_it_is_not(data_pack):
    line = data_pack["communities"][0]["claim_reliability"]
    entry = data_pack["sources"][line["src"]]
    assert entry["source"] == pack.RELIABILITY_SOURCE
    assert DATE_RE.match(entry["date"])  # the date the model was fit
    assert "Main_Audit_Roads" in entry["url"]
    assert entry["licence"]
    # What the word is worth is said once, on the source every community points at.
    assert "not a measurement here" in entry["note"]
    assert "AUC" in entry["note"] and "{auc}" not in entry["note"]
    assert {c["claim_reliability"]["src"] for c in data_pack["communities"]} == {line["src"]}


def test_reliability_words_match_the_model_output(data_pack):
    """The pack repeats pipeline/reliability.py's words; it never recomputes one."""
    lines = pack.reliability_lines()
    if not lines:
        pytest.skip("data/out/reliability.csv has not been written")
    for community in data_pack["communities"]:
        assert community["claim_reliability"]["word"] == lines[community["id"]]["word"]


# --- The priority row (Task-40) ---


def test_priority_list_is_96_rows_in_rank_order(data_pack):
    priority = data_pack["priority"]
    assert len(priority) == 96
    assert [entry["rank"] for entry in priority] == list(range(1, 97))
    assert {entry["id"] for entry in priority} == {c["id"] for c in data_pack["communities"]}


def test_priority_components_header_matches_the_weights_csv(data_pack):
    weights = prioritise.load_weights()
    assert data_pack["priority_components"] == [
        {"name": spec["component"], "weight": spec["weight"]} for spec in weights
    ]
    for entry in data_pack["priority"]:
        assert len(entry["c"]) == len(weights)


def test_priority_intervention_is_one_of_the_eight_words(data_pack):
    words = [entry["word"] for entry in data_pack["priority_interventions"]]
    assert words == [word for word, _, _ in prioritise.INTERVENTIONS]
    assert len(words) == 8
    for entry in data_pack["priority_interventions"]:
        assert entry["addressee"]
    for entry in data_pack["priority"]:
        # The word is an index into the header, not a string repeated 96 times.
        assert 0 <= entry["i"] < len(words)
        assert entry["why"].endswith(".")


def test_every_community_carries_its_rank_and_intervention_index(data_pack):
    by_id = {entry["id"]: entry for entry in data_pack["priority"]}
    for community in data_pack["communities"]:
        pointer = community["priority"]
        assert set(pointer) == {"rank", "i"}
        assert pointer["rank"] == by_id[community["id"]]["rank"]
        assert pointer["i"] == by_id[community["id"]]["i"]


def test_priority_score_is_the_sum_of_its_contributions(data_pack):
    for entry in data_pack["priority"]:
        assert entry["score"] == pytest.approx(sum(entry["c"]), abs=0.002)


def test_pack_carries_no_weight_the_app_could_recompute_a_verdict_from(data_pack):
    """The pack ships the score, not the thresholds it was measured against (layer rule 4)."""
    assert "thresholds" not in data_pack
    names = {entry["name"] for entry in data_pack["priority_components"]}
    assert "telehealth_verdict" in names
