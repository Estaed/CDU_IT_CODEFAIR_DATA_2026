"""Unit tests for pipeline.prioritise: the score, the rank and the intervention (Task-40).

Every test here builds its rows by hand. The module is standard library only and takes plain
dicts, so none of this needs the pipeline to have run.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

from pipeline import prioritise

ROOT = Path(__file__).resolve().parent.parent

PRESENT_NO = dict.fromkeys(prioritise.PRESENCE_COLUMNS, "N")


def make_row(**overrides: str) -> dict[str, str]:
    """One capability-table row with nothing remarkable about it."""
    row = {
        **PRESENT_NO,
        "bushtel_id": "1",
        "name": "Testville",
        "population_abs2021": "100",
        "telehealth_video": "degraded",
        "voice_sms": "works",
        "claim_reliability_word": "medium",
        "audit5": "",
        "mbsp_within_5km": "0",
        "best_path": "terrestrial_mobile",
        "any_within_5km": "1",
        "carriers_4g_count": "1",
        "mobile_says": "accc=1;ntg2022=1;rrl5=1;bushtel=1",
        "backhaul_2019": "Optic fibre",
    }
    row.update(overrides)
    return row


def _rewrite_weight(source: Path, destination: Path, component: str, factor: float) -> Path:
    """A copy of the weights CSV with one component's weight multiplied."""
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        if row["component"] == component:
            row["weight"] = str(float(row["weight"]) * factor)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return destination


@pytest.fixture(scope="module")
def weights():
    return prioritise.load_weights()


def test_weights_come_from_csv(tmp_path, weights):
    """Doubling one weight in the CSV doubles that contribution and moves no other."""
    doubled = prioritise.load_weights(
        _rewrite_weight(prioritise.WEIGHTS_CSV, tmp_path / "w.csv", "population", 2.0)
    )
    values = {spec["component"]: 0.5 for spec in weights}
    before = {c["name"]: c["contribution"] for c in prioritise.score(values, weights)["components"]}
    after = {c["name"]: c["contribution"] for c in prioritise.score(values, doubled)["components"]}

    assert after["population"] == pytest.approx(before["population"] * 2)
    for name, contribution in before.items():
        if name != "population":
            assert after[name] == pytest.approx(contribution)


def test_every_weight_is_read_from_the_csv(tmp_path, weights):
    """Halving any one weight in the CSV halves exactly that contribution and no other.

    The weights live in the CSV and nowhere else (Blueprint, Never hardcode); a weight baked
    into the module would leave its contribution unmoved when the file changed.
    """
    values = {spec["component"]: 0.5 for spec in weights}
    base = {c["name"]: c["contribution"] for c in prioritise.score(values, weights)["components"]}
    for spec in weights:
        name = spec["component"]
        halved = prioritise.load_weights(
            _rewrite_weight(prioritise.WEIGHTS_CSV, tmp_path / f"{name}.csv", name, 0.5)
        )
        after = {
            c["name"]: c["contribution"] for c in prioritise.score(values, halved)["components"]
        }
        assert after[name] == pytest.approx(base[name] * 0.5)
        for other, contribution in base.items():
            if other != name:
                assert after[other] == pytest.approx(contribution)


def test_zero_weight_contributes_zero(weights):
    zero = [spec["component"] for spec in weights if spec["weight"] == 0]
    assert zero, "the components waiting on a licence must still be listed"

    values = {spec["component"]: 1.0 for spec in weights}
    contributions = {
        c["name"]: c["contribution"] for c in prioritise.score(values, weights)["components"]
    }
    for name in zero:
        assert contributions[name] == 0.0

    # And they move no rank: dropping them entirely gives the same order.
    rows = [
        make_row(bushtel_id=str(index), population_abs2021=str(index * 40))
        for index in range(1, 11)
    ]
    kept = [spec for spec in weights if spec["weight"] != 0]
    assert [e["id"] for e in prioritise.ranked(rows, kept)] == [
        e["id"] for e in prioritise.ranked(rows, weights)
    ]


def test_ranks_unique_and_reproducible(weights):
    """96 rows that all score the same still rank 1..96, and twice the same way."""
    rows = [
        make_row(bushtel_id=str(index), name=f"C{index}", population_abs2021="100")
        for index in range(1, 97)
    ]
    first = prioritise.ranked(rows, weights)
    assert [entry["rank"] for entry in first] == list(range(1, 97))
    assert len({entry["id"] for entry in first}) == 96
    assert len({entry["score"] for entry in first}) == 1, "the rows were built to tie"

    # Feeding the same rows in the opposite order gives the identical ranking: the order is
    # decided by the tiebreakers, never by the order the rows arrived in.
    again = prioritise.ranked(list(reversed(rows)), weights)
    assert [(e["id"], e["rank"]) for e in again] == [(e["id"], e["rank"]) for e in first]
    # Every tiebreaker before the last one is equal here, so the last one decided.
    assert [entry["id"] for entry in first] == sorted(entry["id"] for entry in first)


def test_score_is_the_sum_of_its_contributions(weights):
    values = {spec["component"]: 0.25 for spec in weights}
    scored = prioritise.score(values, weights)
    assert scored["score"] == pytest.approx(
        sum(component["contribution"] for component in scored["components"])
    )
    for component in scored["components"]:
        assert component["contribution"] == pytest.approx(
            component["value"] * component["weight"]
        )


def test_normalise_puts_every_component_in_0_1(weights):
    rows = [
        make_row(
            bushtel_id=str(index),
            population_abs2021=str(index * 31),
            telehealth_video=("fails" if index % 2 else "works"),
            voice_sms=("fails" if index % 3 else "works"),
            claim_reliability_word=("low" if index % 4 else "high"),
            audit5=("1" if index % 5 else ""),
            mbsp_within_5km=("1" if index % 6 else "0"),
        )
        for index in range(1, 21)
    ]
    scaled = prioritise.normalise([prioritise.raw_components(row) for row in rows], weights)
    for values in scaled:
        for spec in weights:
            assert 0.0 <= values[spec["component"]] <= 1.0


def test_health_centre_counts_twice(weights):
    """The clinic is the one presence flag worth two (contract item 1)."""
    clinic = prioritise.raw_components(make_row(svc_health_centre="Y"))
    school = prioritise.raw_components(make_row(svc_school="Y"))
    assert clinic["services_present"] == 2.0
    assert school["services_present"] == 1.0


def _intervention_rows() -> dict[str, dict[str, str]]:
    """One hand-built row per rule, each built so that no earlier rule fires."""
    return {
        "low-latency backhaul": make_row(svc_health_centre="Y", best_path="satellite"),
        "mobile site (MBSP nomination)": make_row(
            voice_sms="fails",
            any_within_5km="0",
            carriers_4g_count="0",
            mobile_says="accc=0;ntg2022=0;rrl5=0;bushtel=0",
        ),
        "verify and publish the licensed site": make_row(
            mobile_says="accc=0;ntg2022=0;rrl5=1;bushtel=0"
        ),
        "refresh the coverage list": make_row(mobile_says="accc=1;ntg2022=0;rrl5=1;bushtel=1"),
        "backup power": make_row(backhaul_2019="Microwave radio"),
        # A drive-test non-alignment within 5 km, with no earlier rule firing.
        "verify on the ground": make_row(audit5="1"),
        # A clinic off satellite whose telehealth is still only Degraded.
        "measure the link here": make_row(
            svc_health_centre="Y",
            telehealth_video="degraded",
            best_path="terrestrial_mobile",
        ),
        "monitor": make_row(),
    }


def test_each_intervention_reachable():
    cases = _intervention_rows()
    assert sorted(cases) == sorted(word for word, _, _ in prioritise.INTERVENTIONS)
    for expected, row in cases.items():
        word, addressee = prioritise.intervention(row)
        assert word == expected
        assert addressee


def test_first_matching_rule_wins():
    """A row that satisfies two rules gets the earlier one."""
    row = make_row(
        svc_health_centre="Y",
        best_path="satellite",
        backhaul_2019="Microwave radio",
        mobile_says="accc=0;ntg2022=0;rrl5=1;bushtel=0",
    )
    assert prioritise.intervention(row)[0] == "low-latency backhaul"


def test_why_names_the_two_largest_contributions_and_the_rule(weights):
    row = make_row(svc_health_centre="Y", best_path="satellite", telehealth_video="fails")
    entries = prioritise.ranked([row, make_row(bushtel_id="2")], weights)
    entry = next(e for e in entries if e["id"] == 1)
    largest = sorted(entry["components"], key=lambda c: -c["contribution"])[:2]
    for component in largest:
        if component["contribution"] > 0:
            assert prioritise.COMPONENT_LABEL[component["name"]].lower() in entry["why"].lower()
    assert prioritise.RULE_BECAUSE[entry["intervention"]] in entry["why"]
    assert entry["why"].endswith(".")


def _varied_rows(count: int = 96) -> list[dict[str, str]]:
    verdicts = ("fails", "degraded", "nodata", "works")
    voices = ("fails", "degraded", "works")
    words = ("low", "medium", "high", "none")
    return [
        make_row(
            bushtel_id=str(index),
            name=f"C{index}",
            population_abs2021=str((index * 37) % 900 + 20),
            telehealth_video=verdicts[index % len(verdicts)],
            voice_sms=voices[index % len(voices)],
            claim_reliability_word=words[index % len(words)],
            audit5=("1" if index % 11 == 0 else ""),
            mbsp_within_5km=("1" if index % 13 == 0 else "0"),
            svc_health_centre=("Y" if index % 3 else "N"),
            svc_school=("Y" if index % 2 else "N"),
        )
        for index in range(1, count + 1)
    ]


def test_sensitivity_one_row_per_weight_and_factor(weights):
    table = prioritise.sensitivity(_varied_rows(), weights)
    assert len(table) == len(weights) * len(prioritise.SENSITIVITY_FACTORS)
    assert {(row["component"], row["factor"]) for row in table} == {
        (spec["component"], factor)
        for spec in weights
        for factor in prioritise.SENSITIVITY_FACTORS
    }
    for row in table:
        assert 0 <= row["top10_overlap"] <= prioritise.TOP_N
        assert -1.0 <= row["spearman_rho"] <= 1.0
        assert row["perturbed_weight"] == pytest.approx(row["weight"] * row["factor"], abs=1e-4)


def test_sensitivity_of_a_zero_weight_moves_nothing(weights):
    table = prioritise.sensitivity(_varied_rows(), weights)
    zero = [row for row in table if row["weight"] == 0]
    assert zero, "the components waiting on a licence must still be reported"
    for row in zero:
        assert row["top10_overlap"] == prioritise.TOP_N
        assert row["spearman_rho"] == 1.0


def test_spearman_of_a_ranking_against_itself_is_one():
    ranking = {index: index for index in range(1, 97)}
    assert prioritise.spearman(ranking, ranking) == 1.0
    reversed_ranking = {index: 97 - index for index in range(1, 97)}
    assert prioritise.spearman(ranking, reversed_ranking) == pytest.approx(-1.0)


def test_stdlib_only():
    """Layer rule 9: the score is computed with the standard library, like pipeline.rules."""
    text = (ROOT / "pipeline/prioritise.py").read_text(encoding="utf-8")
    forbidden = re.compile(
        r"^(import|from) (pandas|geopandas|shapely|numpy|sklearn|matplotlib|requests)",
        re.MULTILINE,
    )
    assert forbidden.search(text) is None
