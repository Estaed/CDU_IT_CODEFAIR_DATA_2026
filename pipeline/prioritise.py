"""The priority score, rank, intervention and addressee for one community.

Standard library only (CLAUDE.md Blueprint, layer rule 9), like ``pipeline.rules``: every
function takes plain dicts, so the whole thing is unit-tested with hand-built rows and never
touches a data frame. Run from the project root:
``PYTHONUTF8=1 .venv/Scripts/python -m pipeline.prioritise``.

**Every weight lives in ``pipeline/priority_weights.csv`` and nowhere else** (Blueprint, Never
hardcode). This module reads that file through ``load_weights`` and multiplies; it never
names a number. A component whose source has not arrived carries weight 0 and a ``note``
saying which open question it waits on: it is scored, reported and printed in the sensitivity
table like every other component, and contributes exactly nothing to the score.

Two outputs:

* ``data/out/priority.csv``  the 96 in rank order with their score, contributions,
  intervention, addressee and the one sentence that says why; read by ``pipeline.pack``.
* ``data/out/tables/priority_sensitivity.csv``  every weight taken to half and to one and a
  half of itself, with how much of the top ten survives and Spearman's rho over all 96.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS_CSV = ROOT / "pipeline/priority_weights.csv"
TABLE = ROOT / "data/out/capability_table.csv"
RELIABILITY_CSV = ROOT / "data/out/reliability.csv"
OUT_PRIORITY = ROOT / "data/out/priority.csv"
OUT_SENSITIVITY = ROOT / "data/out/tables/priority_sensitivity.csv"

SCORE_DECIMALS = 3
SENSITIVITY_FACTORS = (0.5, 1.5)
TOP_N = 10

# The ten BushTel presence flags, in the order the pack shows them. Repeated here rather than
# imported from ``pipeline.pack``: that module reads shapefiles, and this one is standard
# library only.
PRESENCE_COLUMNS = (
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
)
DOUBLE_WEIGHTED = "svc_health_centre"

# The verdict-to-value maps the weights CSV's ``note`` column names. A word not listed scores
# 0: it cannot be evidence of a gap if the rules never produce it.
TELEHEALTH_VALUE = {"fails": 1.0, "degraded": 0.5, "nodata": 0.25, "works": 0.0}
VOICE_VALUE = {"fails": 1.0, "degraded": 0.5, "works": 0.0}
# ``none`` sits between ``medium`` and ``high``: not knowing whether the claim holds is worse
# than knowing it does and better than knowing it does not (Task-39's word, not a verdict).
RELIABILITY_VALUE = {"low": 1.0, "medium": 0.5, "none": 0.25, "high": 0.0}

# One intervention and one addressee per community, first match wins, in this order.
INTERVENTIONS: tuple[tuple[str, str, object], ...] = (
    # A clinic whose only path is satellite: the 664.9 ms figure is the entire verdict and
    # nothing but backhaul moves it.
    (
        "low-latency backhaul",
        "DCDD, nbn",
        lambda row: row.get("svc_health_centre") == "Y" and row.get("best_path") == "satellite",
    ),
    # Voice and SMS fail with nothing predicted and nothing licensed within 5 km: there is no
    # site to fix, so the ask is a new one.
    (
        "mobile site (MBSP nomination)",
        "DCDD, carrier",
        lambda row: row.get("voice_sms") == "fails"
        and row.get("any_within_5km") == "0"
        and _count(row.get("carriers_4g_count")) == 0,
    ),
    # A licensed mast within 5 km that no carrier coverage map shows.
    (
        "verify and publish the licensed site",
        "carrier, ACMA",
        lambda row: row.get("mobile_says", "").startswith("accc=0;")
        and ";rrl5=1;" in row.get("mobile_says", ""),
    ),
    # A carrier prediction the 2022 NT Government list has never caught up with.
    (
        "refresh the coverage list",
        "DCDD",
        lambda row: row.get("mobile_says", "").startswith("accc=1;")
        and ";ntg2022=0;" in row.get("mobile_says", ""),
    ),
    # Microwave backhaul, or a cyclone exposure flag once OQ3 lands: the link goes when the
    # power does, and a battery is cheaper than a tower.
    (
        "backup power",
        "carrier",
        lambda row: "microwave" in row.get("backhaul_2019", "").lower() or _cyclone_flag(row),
    ),
    # 2026-09-17 evening, Tarik: the Audit's own drive test found no signal inside a carrier's
    # claimed coverage within 5 km. Every claim here says covered and the government's own
    # measurement disagrees, which is a visit, not a watch.
    ("verify on the ground", "DCDD, carrier", lambda row: row.get("audit5") == "1"),
    # A health centre off satellite whose telehealth still only rates Degraded: the path exists,
    # nobody has measured what it actually delivers at the clinic door.
    (
        "measure the link here",
        "DCDD",
        lambda row: row.get("svc_health_centre") == "Y"
        and row.get("telehealth_video") == "degraded"
        and row.get("best_path") != "satellite",
    ),
    # Nothing above fired.
    ("monitor", "DCDD", lambda row: True),
)

# The short strings the ``why`` sentence is assembled from: one per component, one per rule.
# Authored once here, never per community (Task-40 contract item 3).
COMPONENT_LABEL = {
    "population": "population",
    "services_present": "services present",
    "telehealth_verdict": "telehealth verdict",
    "voice_sms_verdict": "voice verdict",
    "claim_reliability": "claim reliability",
    "audit_non_alignment_5km": "drive-test non-alignment",
    "mbsp_funded_5km": "MBSP site within 5 km",
    "cyclone_exposure": "cyclone exposure",
    "adii_lga": "ADII score",
}
RULE_BECAUSE = {
    "low-latency backhaul": "health centre on a satellite path",
    "mobile site (MBSP nomination)": "no prediction and no licensed site within 5 km",
    "verify and publish the licensed site": "licensed site within 5 km, no coverage map",
    "refresh the coverage list": "predicted coverage, not on the 2022 list",
    "backup power": "microwave backhaul",
    "verify on the ground": "a drive test found no signal inside claimed coverage",
    "measure the link here": "a health centre whose link nobody has measured",
    "monitor": "no rule above it fired",
}


def _count(value: object) -> int:
    """A counted cell as an integer; empty, missing or unparseable reads as 0."""
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return 0


def _cyclone_flag(row: dict[str, str]) -> bool:
    """Whether the row carries a cyclone exposure flag. No source publishes one yet (OQ3)."""
    return _count(row.get("cyclone_exposure")) > 0


def load_weights(path: Path = WEIGHTS_CSV) -> list[dict]:
    """The score components in file order: name, weight, source column, transform, note."""
    weights = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            weights.append(
                {
                    "component": row["component"],
                    "weight": float(row["weight"]),
                    "source_column": row["source_column"],
                    "transform": row["transform"],
                    "note": row["note"],
                }
            )
    return weights


def raw_components(row: dict[str, str]) -> dict[str, float]:
    """The raw, unnormalised value of every component for one capability-table row."""
    present = sum(1 for column in PRESENCE_COLUMNS if row.get(column) == "Y")
    if row.get(DOUBLE_WEIGHTED) == "Y":
        present += 1
    return {
        "population": float(_count(row.get("population_abs2021"))),
        "services_present": float(present),
        "telehealth_verdict": TELEHEALTH_VALUE.get(row.get("telehealth_video", ""), 0.0),
        "voice_sms_verdict": VOICE_VALUE.get(row.get("voice_sms", ""), 0.0),
        "claim_reliability": RELIABILITY_VALUE.get(
            row.get("claim_reliability_word", ""), RELIABILITY_VALUE["none"]
        ),
        "audit_non_alignment_5km": 1.0 if row.get("audit5") == "1" else 0.0,
        "mbsp_funded_5km": 1.0 if _count(row.get("mbsp_within_5km")) >= 1 else 0.0,
        "cyclone_exposure": 0.0,  # OQ3: no licence to the cyclone track data yet
        "adii_lga": 0.0,  # OQ5: no ADII figure per LGA yet
    }


def normalise(raws: list[dict[str, float]], weights: list[dict]) -> list[dict[str, float]]:
    """Each component scaled to 0..1 across the whole set, by the transform the CSV names.

    ``log`` takes log10(1 + value) first, then scales; ``linear`` scales as it stands; ``map``
    is already 0..1 because the mapping put it there. A component that is the same for every
    community carries no information and scales to 0 rather than dividing by zero.
    """
    scaled: list[dict[str, float]] = [{} for _ in raws]
    for spec in weights:
        name = spec["component"]
        values = [raw[name] for raw in raws]
        if spec["transform"] == "log":
            values = [math.log10(1.0 + max(value, 0.0)) for value in values]
        if spec["transform"] in ("log", "linear"):
            low, high = min(values), max(values)
            span = high - low
            values = [0.0 if span == 0 else (value - low) / span for value in values]
        for target, value in zip(scaled, values, strict=True):
            target[name] = value
    return scaled


def score(row: dict[str, float], weights: list[dict]) -> dict:
    """One normalised component row (what ``normalise`` returns) scored against the weights."""
    components = []
    total = 0.0
    for spec in weights:
        value = float(row.get(spec["component"], 0.0))
        contribution = value * spec["weight"]
        total += contribution
        components.append(
            {
                "name": spec["component"],
                "value": value,
                "weight": spec["weight"],
                "contribution": contribution,
            }
        )
    return {"score": total, "components": components}


def intervention(row: dict[str, str]) -> tuple[str, str]:
    """``(intervention, addressee)`` for one capability-table row; the first rule that fires."""
    for word, addressee, fired in INTERVENTIONS:
        if fired(row):
            return word, addressee
    raise AssertionError("the last intervention rule must always fire")


def why(components: list[dict], word: str) -> str:
    """One sentence: the two largest contributions, then the rule that fired."""
    largest = [
        COMPONENT_LABEL[component["name"]]
        for component in sorted(components, key=lambda c: -c["contribution"])
        if component["contribution"] > 0
    ][:2]
    if not largest:
        driven = "No component scores above zero"
    elif len(largest) == 1:
        driven = f"{largest[0][0].upper()}{largest[0][1:]} ranks it here"
    else:
        driven = f"{largest[0][0].upper()}{largest[0][1:]} and {largest[1]} rank it here"
    return f"{driven}; {RULE_BECAUSE[word]}."


def ranked(rows: list[dict[str, str]], weights: list[dict]) -> list[dict]:
    """The rows in rank order, 1..n, every rank unique and reproducible.

    Rank is by score descending; ties break by telehealth verdict severity, then population
    descending, then ``bushtel_id`` ascending, so the order never depends on input order. The
    score the rank is taken on is the rounded one the pack shows, so two rows printed with the
    same number are ordered by the tiebreakers and not by an invisible digit.
    """
    scaled = normalise([raw_components(row) for row in rows], weights)
    entries = []
    for row, values in zip(rows, scaled, strict=True):
        scored = score(values, weights)
        word, addressee = intervention(row)
        entries.append(
            {
                "id": _count(row.get("bushtel_id")),
                "name": row.get("name", ""),
                "score": round(scored["score"], SCORE_DECIMALS),
                "components": scored["components"],
                "intervention": word,
                "addressee": addressee,
                "why": why(scored["components"], word),
                "_severity": TELEHEALTH_VALUE.get(row.get("telehealth_video", ""), 0.0),
                "_population": _count(row.get("population_abs2021")),
            }
        )
    entries.sort(
        key=lambda e: (-e["score"], -e["_severity"], -e["_population"], e["id"]),
    )
    for position, entry in enumerate(entries, 1):
        entry["rank"] = position
        del entry["_severity"]
        del entry["_population"]
    return entries


def spearman(first: dict[int, int], second: dict[int, int]) -> float:
    """Spearman's rho between two rankings of the same ids; both are 1..n with no ties."""
    n = len(first)
    if n < 2:
        return 1.0
    squared = sum((first[key] - second[key]) ** 2 for key in first)
    return 1.0 - 6.0 * squared / (n * (n * n - 1))


def sensitivity(rows: list[dict[str, str]], weights: list[dict]) -> list[dict]:
    """Every weight at half and at one and a half of itself: top-ten survival and rho.

    A weight of 0 is perturbed like any other and moves nothing, which is the honest answer
    for a component whose source has not arrived: the row is printed with overlap 10 and rho
    1.0 so the report can say so rather than leaving the component out.
    """
    baseline = ranked(rows, weights)
    base_rank = {entry["id"]: entry["rank"] for entry in baseline}
    base_top = {entry["id"] for entry in baseline[:TOP_N]}
    table = []
    for index, spec in enumerate(weights):
        for factor in SENSITIVITY_FACTORS:
            perturbed = [dict(other) for other in weights]
            perturbed[index]["weight"] = spec["weight"] * factor
            moved = ranked(rows, perturbed)
            moved_rank = {entry["id"]: entry["rank"] for entry in moved}
            moved_top = {entry["id"] for entry in moved[:TOP_N]}
            table.append(
                {
                    "component": spec["component"],
                    "factor": factor,
                    "weight": spec["weight"],
                    "perturbed_weight": round(spec["weight"] * factor, 4),
                    "top10_overlap": len(base_top & moved_top),
                    "spearman_rho": round(spearman(base_rank, moved_rank), 4),
                }
            )
    return table


def reliability_words(path: Path = RELIABILITY_CSV) -> dict[int, str]:
    """``{bushtel_id: claim reliability word}`` from the reliability run, empty when absent."""
    path = Path(path)
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {int(row["id"]): row["word"] for row in csv.DictReader(handle)}


def load_rows(table: Path = TABLE, reliability: Path = RELIABILITY_CSV) -> list[dict[str, str]]:
    """The capability table with the reliability word joined on, as plain string rows."""
    with Path(table).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    words = reliability_words(reliability)
    for row in rows:
        row["claim_reliability_word"] = words.get(_count(row.get("bushtel_id")), "none")
    return rows


def write_priority(entries: list[dict], weights: list[dict], path: Path = OUT_PRIORITY) -> Path:
    """The 96 in rank order: the score, one contribution column per component, and the words."""
    names = [spec["component"] for spec in weights]
    header = ["rank", "id", "name", "score", "intervention", "addressee", "why"]
    header += [f"c_{name}" for name in names]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for entry in entries:
            contributions = {c["name"]: c["contribution"] for c in entry["components"]}
            writer.writerow(
                [
                    entry["rank"],
                    entry["id"],
                    entry["name"],
                    f"{entry['score']:.{SCORE_DECIMALS}f}",
                    entry["intervention"],
                    entry["addressee"],
                    entry["why"],
                ]
                + [f"{contributions[name]:.{SCORE_DECIMALS}f}" for name in names]
            )
    return path


def write_sensitivity(table: list[dict], path: Path = OUT_SENSITIVITY) -> Path:
    """One row per (component, factor): the perturbed weight, top-ten overlap and rho."""
    fields = [
        "component",
        "factor",
        "weight",
        "perturbed_weight",
        "top10_overlap",
        "spearman_rho",
    ]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    return path


def main() -> None:
    weights = load_weights()
    rows = load_rows()
    entries = ranked(rows, weights)
    write_priority(entries, weights)
    write_sensitivity(sensitivity(rows, weights))
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["intervention"]] = counts.get(entry["intervention"], 0) + 1
    print(
        f"{OUT_PRIORITY.relative_to(ROOT).as_posix()}: {len(entries)} ranked, "
        f"top {entries[0]['name']} ({entries[0]['score']})"
    )
    print("   " + ", ".join(f"{word} {count}" for word, count in sorted(counts.items())))
    print(f"{OUT_SENSITIVITY.relative_to(ROOT).as_posix()}: {len(weights) * 2} rows")


if __name__ == "__main__":
    main()
