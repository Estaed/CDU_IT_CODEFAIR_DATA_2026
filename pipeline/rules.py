"""Service verdict rules over one capability-table row.

Standard library only (CLAUDE.md Part 2, layer rule 1). Every rule takes a plain dict of
strings - one ``csv.DictReader`` row of the capability table - and returns a plain dict, so
the rules are unit-tested with hand-built rows and never touch a data frame.
"""

from __future__ import annotations

import csv
from pathlib import Path

RULE_NAME = "best-path rule"  # PRD section 5; was "spike rule" until 2026-09-13
RULE_DATE = "2026-09-12"
LICENSED_RADIUS_KM = 5

CARRIER_COLUMNS = (
    ("telstra_4g_2025", "Telstra"),
    ("optus_4g_2025", "Optus"),
    ("tpg_4g_2025", "TPG"),
)

NO_RECORD = "No fixed-access record for this community"
NO_REQUIREMENT = "Requirement figure not published"


def load_thresholds(path: Path) -> dict[str, dict]:
    """Read the requirement and capability table, keyed kind.service.metric."""
    table: dict[str, dict] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = f"{row['kind']}.{row['service']}.{row['metric']}"
            table[key] = {
                "value": float(row["value"]) if row["value"] else None,
                "unit": row["unit"],
                "direction": row["direction"],
                "source": row["source"],
                "source_url": row["source_url"],
                "checked": row["checked"],
                "note": row["note"],
            }
    return table


def fig(value: float, unit: str) -> str:
    """Render a figure the way the screens do: 5,000 kbps, 664.9 ms, 100 ms, in backticks."""
    number = f"{value:,.0f}" if float(value).is_integer() else f"{value:,}"
    return f"`{number} {unit}`"


def carrier_count(row: dict[str, str]) -> int:
    """The ACCC predicted 4G carrier count, 0 when the cell is empty."""
    return int(row["carriers_4g_count"]) if row["carriers_4g_count"] else 0


def carriers_4g(row: dict[str, str]) -> list[str]:
    """Named carriers with a predicted 4G polygon over the community."""
    return [name for column, name in CARRIER_COLUMNS if row[column] == "1"]


def join_names(names: list[str]) -> str:
    """Telstra / Telstra and Optus / Telstra, Optus and TPG; A carrier when the list is empty."""
    if not names:
        return "A carrier"
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} and {names[-1]}"


def verb(names: list[str]) -> str:
    """The verb that agrees with what join_names produced."""
    return "are" if len(names) > 1 else "is"


def best_path(row: dict[str, str]) -> str:
    """Best available path (PRD section 5), not the nbn technology."""
    if row["in_fixed_line"] == "1":
        return "fixed_line"
    if row["in_fixed_wireless"] == "1":
        return "fixed_wireless"
    if carrier_count(row) >= 1 and row["any_within_5km"] == "1":
        return "terrestrial_mobile"
    return "satellite"


def agreement(publishers: list[dict]) -> tuple[int, int]:
    """(covered, available) over the publisher lines that recorded anything."""
    available = sum(1 for line in publishers if line["says_covered"] != "not-recorded")
    covered = sum(1 for line in publishers if line["says_covered"] == "covered")
    return covered, available


def _nodata(reason: str) -> dict:
    return {"verdict": "nodata", "reason": reason, "sources": []}


def _figure(label: str, entry: dict) -> dict:
    return {"label": label, "source": entry["source"], "date": entry["checked"]}


def _path_source(row: dict[str, str]) -> dict:
    word = best_path(row).replace("_", " ")
    return {"label": "Path", "source": f"{word}, {RULE_NAME}", "date": RULE_DATE}


def _is_fixed(row: dict[str, str]) -> bool:
    return row["nbn_technology"] in ("FIXED_LINE", "FIXED_WIRELESS")


def _fixed_word(row: dict[str, str]) -> str:
    return "Fixed line" if row["nbn_technology"] == "FIXED_LINE" else "Fixed wireless"


def telehealth_video(row: dict[str, str], thresholds: dict[str, dict]) -> dict:
    """healthdirect Video Call: a latency requirement satellite cannot meet."""
    if row["svc_health_centre"] != "Y":
        return _nodata("No health centre recorded on BushTel")
    if row["nbn_technology"] == "":
        return _nodata(NO_RECORD)
    required = thresholds["requirement.telehealth_video.latency"]
    if required["value"] is None:
        return _nodata(NO_REQUIREMENT)
    need = fig(required["value"], required["unit"])
    path = _path_source(row)
    if _is_fixed(row):
        return {
            "verdict": "works",
            "reason": (
                f"{_fixed_word(row)} footprint contains the community; "
                f"latency is under the {need} requirement on fixed access"
            ),
            "sources": [_figure("Required figure", required), path],
            "assumption": (
                "No fixed-access latency figure is sourced yet; fixed access is treated as "
                f"under {need} until the ACCC figure is added."
            ),
        }
    measured = thresholds["capability.nbn_satellite.latency"]
    have = fig(measured["value"], measured["unit"])
    sources = [_figure("Failing figure", measured), _figure("Required figure", required), path]
    if carrier_count(row) >= 1:
        return {
            "verdict": "degraded",
            "reason": f"Latency {have} on satellite vs {need} required",
            "sources": sources,
            "assumption": (
                f"Could work over {join_names(carriers_4g(row))} 4G if latency is under {need}. "
                "No measurement exists here."
            ),
        }
    return {
        "verdict": "fails",
        "reason": f"Latency {have} on satellite vs {need} required; no carrier 4G polygon",
        "sources": sources,
    }


def school_video_meeting(row: dict[str, str], thresholds: dict[str, dict]) -> dict:
    """Microsoft Teams: an upload requirement satellite clears, with no published latency."""
    if row["svc_school"] != "Y":
        return _nodata("No school recorded on BushTel")
    if row["nbn_technology"] == "":
        return _nodata(NO_RECORD)
    required = thresholds["requirement.school_video_meeting.bandwidth_up"]
    if required["value"] is None:
        return _nodata(NO_REQUIREMENT)
    need = fig(required["value"], required["unit"])
    path = _path_source(row)
    if _is_fixed(row):
        return {
            "verdict": "works",
            "reason": (
                f"{_fixed_word(row)} footprint contains the community; "
                f"the {need} upload requirement is cleared on fixed access"
            ),
            "sources": [_figure("Required figure", required), path],
        }
    capacity = thresholds["capability.nbn_satellite.bandwidth_up_max"]
    have = fig(capacity["value"], capacity["unit"])
    return {
        "verdict": "degraded",
        "reason": (
            f"Upload {have} on satellite vs {need} required; "
            "the latency requirement is not published"
        ),
        "sources": [
            _figure("Capacity figure", capacity),
            _figure("Required figure", required),
            path,
        ],
        "assumption": (
            "Microsoft Teams publishes no latency requirement. "
            "Treated as Degraded on satellite until one is sourced."
        ),
    }


def mygov_text(row: dict[str, str], thresholds: dict[str, dict]) -> dict:
    """myGov and banking: text-first, so there is no published requirement to fail."""
    if row["nbn_technology"] == "":
        return _nodata(NO_RECORD)
    required = thresholds["requirement.mygov_banking.bandwidth_down"]
    return {
        "verdict": "works",
        "reason": "Text-first services reach any working link; no published requirement",
        "sources": [_figure("Required figure", required), _path_source(row)],
    }


def voice_sms(row: dict[str, str]) -> dict:
    """Voice and SMS: what the mobile publishers say, with public WiFi as the fallback."""
    names = carriers_4g(row)
    listed = row["ntg2022_listed"] == "1"
    sources = [
        {"label": "Predicted", "source": "ACCC MIR 2025", "date": ""},
        {"label": "Listed", "source": "NT Government 2022 list", "date": ""},
    ]
    if carrier_count(row) >= 1:
        predicted = f"{join_names(names)} 4G {verb(names)} predicted here"
        reason = (
            f"{predicted} and the community is on the 2022 list"
            if listed
            else f"{predicted}; the community is not on the 2022 list"
        )
        return {"verdict": "works", "reason": reason, "sources": sources}
    if listed:
        return {
            "verdict": "works",
            "reason": "The community is on the 2022 list; no carrier 4G polygon over the community",
            "sources": sources,
        }
    sources.append({"label": "WiFi", "source": "BushTel profile", "date": ""})
    if row["svc_wifi"] == "Y":
        return {
            "verdict": "degraded",
            "reason": "No carrier 4G polygon and not on the 2022 list; public WiFi only",
            "sources": sources,
        }
    return {
        "verdict": "fails",
        "reason": "No carrier 4G polygon and not on the 2022 list; no public WiFi recorded",
        "sources": sources,
    }
