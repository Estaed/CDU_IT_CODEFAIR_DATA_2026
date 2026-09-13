"""Build data/out/data_pack.json, the subset of the capability table the app shows.

Every figure the app renders is decided here, never in the browser (CLAUDE.md Part 2).
Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python -m pipeline.pack``.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from pipeline import provenance, rules

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data/out/capability_table.csv"
THRESHOLDS = ROOT / "pipeline/thresholds.csv"
OUT_PACK = ROOT / "data/out/data_pack.json"
CONSTANTS = ROOT / "constants.md"

PACK_VERSION = 1
POPULATION_SOURCE = "ABS 2021 SA1 via BushTel"

# BushTel publishes no single date for the set: every line citing a profile carries that
# community's own stamp, so the registry's snapshot date must not stand in for it.
PER_COMMUNITY_SOURCES = ("BushTel profile",)

# PRD Open Question 1: BushTel reuse terms are unanswered, so the three free-text fields
# stay out of the pack. Flipping this constant is the whole change once OQ1 is closed.
BUSHTEL_TEXT_ALLOWED = False
BUSHTEL_TEXT_FIELDS = ("wifi_comment", "road_access_comment", "stand_comment")

PRESENT_SERVICES = (
    ("svc_health_centre", "Health centre"),
    ("svc_school", "School"),
    ("svc_store", "Store"),
    ("svc_police", "Police"),
    ("svc_library", "Library"),
    ("svc_council_centre", "Council service centre"),
    ("svc_employment", "Employment services"),
    ("svc_wifi", "Public WiFi"),
    ("svc_stand", "STAND site"),
    ("svc_aerodrome", "Aerodrome"),
)

NTG_SITE_TYPES = (
    ("ntg2022_macro", "Macro cell"),
    ("ntg2022_small", "Small cell"),
    ("ntg2022_proximity", "Proximity"),
)

POLYGON_DISTANCES = (
    ("dist_km_telstra_4g", "Telstra"),
    ("dist_km_optus_4g", "Optus"),
    ("dist_km_tpg_4g", "TPG"),
)

TRAILING_CAPS = re.compile(r"(\s+[A-Z][A-Z'-]*)+$")


def read_constant(name: str) -> str:
    """Read one value out of the constants.md table; never retype a constant."""
    target = f"`{name}`"
    for line in CONSTANTS.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) > 3 and cells[1] == target:
            return cells[2]
    raise KeyError(f"{name} is not in {CONSTANTS.name}")


def site_name(name: str) -> str:
    """Drop the trailing run of upper-case locality words from an ACMA site name."""
    return TRAILING_CAPS.sub("", name).strip()


def _nearest_polygon(row: dict[str, str]) -> tuple[str, float]:
    options = [
        (float(row[column]), carrier)
        for column, carrier in POLYGON_DISTANCES
        if row[column] != ""
    ]
    km, carrier = min(options)
    return carrier, km


def publisher_lines(row: dict[str, str], profile: str) -> list[dict]:
    """The four mobile publishers, in the order the screens show them."""
    names = rules.carriers_4g(row)
    if rules.carrier_count(row) >= 1:
        accc_detail = f"{rules.join_names(names)} 4G outdoor polygon, carrier prediction"
    else:
        carrier, km = _nearest_polygon(row)
        accc_detail = (
            "No carrier 4G polygon over the community, carrier prediction; "
            f"nearest {carrier} 4G polygon {rules.fig(km, 'km')}"
        )

    if row["ntg2022_listed"] == "1":
        site_type = next(label for column, label in NTG_SITE_TYPES if row[column] == "1")
        provider = "/".join(part.title() for part in row["ntg2022_provider"].split("/"))
        ntg_detail = f"{site_type}, {provider}"
    else:
        ntg_detail = "Not on the list"

    site_carrier = row["nearest_site_carrier"]
    site_km = rules.fig(float(row["nearest_site_km"]), "km")
    if row["any_within_5km"] == "1":
        rrl_detail = f"{site_carrier} site at {site_km}, {site_name(row['nearest_site_name'])}"
    else:
        radius = rules.fig(rules.LICENSED_RADIUS_KM, "km")
        rrl_detail = (
            f"No carrier cellular site licensed within {radius}; "
            f"nearest {site_carrier} site at {site_km}"
        )

    if row["svc_mobile_phone"] == "Y":
        bushtel = ("covered", "Mobile phone row: yes, links to Telstra's coverage map")
    elif row["svc_mobile_phone"] == "N":
        bushtel = ("not-covered", "Mobile phone row: no")
    else:
        bushtel = ("not-recorded", "Mobile phone row not recorded")

    return [
        {
            "publisher": "ACCC Mobile Infrastructure Report 2025",
            "kind": "predicted",
            "says_covered": "covered" if rules.carrier_count(row) >= 1 else "not-covered",
            "detail": accc_detail,
            "source": "ACCC MIR 2025",
            "date": "",
        },
        {
            "publisher": "NT Government 2022 coverage list",
            "kind": "listed",
            "says_covered": "covered" if row["ntg2022_listed"] == "1" else "not-covered",
            "detail": ntg_detail,
            "source": "NT Government 2022 list",
            "date": "",
        },
        {
            "publisher": "ACMA licence register",
            "kind": "licensed",
            "says_covered": "covered" if row["any_within_5km"] == "1" else "not-covered",
            "detail": rrl_detail,
            "source": "ACMA RRL",
            "date": "",
        },
        {
            "publisher": "BushTel",
            "kind": "portal",
            "says_covered": bushtel[0],
            "detail": bushtel[1],
            "source": "BushTel profile",
            "date": profile,
        },
    ]


def citations(thresholds: dict[str, dict]) -> dict[str, dict[str, str]]:
    """``{source name: {date, url, licence}}``: the requirement table under the registry.

    ``pipeline/thresholds.csv`` carries a URL and a checked date for every figure it holds;
    the provenance registry overrides both where it knows the source, so a publication date
    beats the day the figure was read.
    """
    cited: dict[str, dict[str, str]] = {}
    for entry in thresholds.values():
        if entry["source"]:
            cited[entry["source"]] = {"date": entry["checked"], "url": entry["source_url"]}
    for name, known in provenance.citations().items():
        cited[name] = {**cited.get(name, {}), **{k: v for k, v in known.items() if v}}
    return cited


def _dated(source: dict, profile: str, cited: dict[str, dict[str, str]]) -> dict:
    """A citing line's date: the registry's publication date, else its own, else the profile."""
    if source["source"] in PER_COMMUNITY_SOURCES:
        published = ""
    else:
        published = cited.get(source["source"], {}).get("date", "")
    return {**source, "date": published or source["date"] or profile}


def _path_note(row: dict[str, str], path: str) -> str:
    if path == "fixed_line":
        return "fixed line (nbn fixed-line footprint)"
    if path == "fixed_wireless":
        return "fixed wireless (nbn fixed-wireless footprint)"
    names = rules.carriers_4g(row)
    joined = rules.join_names(names)
    if path == "terrestrial_mobile":
        radius = rules.fig(rules.LICENSED_RADIUS_KM, "km")
        return f"terrestrial mobile ({joined} 4G predicted, licensed site within {radius})"
    note = "satellite (nbn satellite residual)"
    if rules.carrier_count(row) >= 1:
        note += f"; {joined} 4G {rules.verb(names)} predicted here"
    return note


def _community(row: dict[str, str], thresholds: dict[str, dict], cited: dict) -> dict:
    profile = row["profile_last_updated"]
    publishers = [_dated(line, profile, cited) for line in publisher_lines(row, profile)]
    covered, available = rules.agreement(publishers)
    path = rules.best_path(row)
    services = []
    for name, result in (
        ("telehealth_video", rules.telehealth_video(row, thresholds)),
        ("school_video_meeting", rules.school_video_meeting(row, thresholds)),
        ("mygov_text", rules.mygov_text(row, thresholds)),
        ("voice_sms", rules.voice_sms(row)),
    ):
        result["sources"] = [_dated(source, profile, cited) for source in result["sources"]]
        services.append({"service": name, **result})

    community = {
        "id": int(row["bushtel_id"]),
        "name": row["name"],
        "aliases": [alias.strip() for alias in row["aliases"].split(",") if alias.strip()],
        "type": row["community_type"],
        "region": row["nt_region"].title(),
        "population": _dated(
            {"value": int(row["population_abs2021"]), "source": POPULATION_SOURCE, "date": ""},
            profile,
            cited,
        ),
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "present": [{"name": label} for column, label in PRESENT_SERVICES if row[column] == "Y"],
        "publishers": publishers,
        "agreement": {
            "covered": covered,
            "available": available,
            "note": "Sources agree" if covered in (0, available) else "Sources disagree",
        },
        "path": {
            "value": path,
            "rule": rules.RULE_NAME,
            "date": rules.RULE_DATE,
            "note": _path_note(row, path),
        },
        "services": services,
        "flags": [
            _dated(flag, profile, cited)
            for flag in (
                {
                    "name": "road_seasonal_cut",
                    "value": row["road_seasonal_cut"] == "1",
                    "source": "BushTel profile",
                    "date": profile,
                },
                {
                    "name": "backhaul_2019",
                    "value": row["ntg2019_backhaul"] or "Not recorded",
                    "source": "NT Government 2019 coverage list",
                    "date": "",
                },
            )
        ],
        "actions": [],
    }
    if BUSHTEL_TEXT_ALLOWED:
        community["notes"] = [
            {"name": field, "text": row[field], "source": "BushTel profile", "date": profile}
            for field in BUSHTEL_TEXT_FIELDS
            if row[field]
        ]
    return community


def dated_lines(community: dict):
    """Every line in one community that cites a source on a date."""
    yield community["population"]
    yield from community["publishers"]
    for service in community["services"]:
        yield from service["sources"]
    yield from community["flags"]


def source_table(communities: list[dict], cited: dict[str, dict[str, str]]) -> dict[str, dict]:
    """Fold every (source, date) pair into one header entry and leave an ``src`` id behind.

    The same four publishers and the same requirement figures are cited by all 96
    communities; naming each of them once and referring to it by ``s<n>`` is what keeps the
    pack inside its byte budget (PRD decision log, 2026-09-13).
    """
    pairs = sorted({(line["source"], line["date"]) for c in communities for line in dated_lines(c)})
    ids = {pair: f"s{index}" for index, pair in enumerate(pairs, 1)}
    for community in communities:
        for line in dated_lines(community):
            line["src"] = ids[(line.pop("source"), line.pop("date"))]
    table = {}
    for (source, published), key in ids.items():
        entry = {"source": source, "date": published}
        known = cited.get(source, {})
        for field in ("url", "licence"):
            if known.get(field):
                entry[field] = known[field]
        table[key] = entry
    return table


def build_pack(
    rows: list[dict[str, str]], thresholds: dict[str, dict], app_url: str, built: str
) -> dict:
    """The whole pack, version 1, communities sorted by BushTel id."""
    cited = citations(thresholds)
    communities = sorted(
        (_community(row, thresholds, cited) for row in rows), key=lambda entry: entry["id"]
    )
    return {
        "pack_version": PACK_VERSION,
        "built": built,
        "app_url": app_url,
        "count": len(communities),
        "sources": source_table(communities, cited),
        "communities": communities,
    }


def main() -> None:
    with TABLE.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    pack = build_pack(
        rows,
        rules.load_thresholds(THRESHOLDS),
        read_constant("APP_URL"),
        date.today().isoformat(),
    )
    OUT_PACK.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n"
    OUT_PACK.write_text(text, encoding="utf-8", newline="\n")
    print(f"{OUT_PACK.relative_to(ROOT)}: {pack['count']} communities, {len(text)} chars")


if __name__ == "__main__":
    main()
