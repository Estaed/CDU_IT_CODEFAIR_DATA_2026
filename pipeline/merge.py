"""Join the six source frames into one capability row per community and score each service.

The six frames arrive keyed on ``bushtel_id`` from ``pipeline.sources.*``; BushTel is the
base frame and the join is a left join onto it, so the result always carries exactly the
communities BushTel lists and a source that recorded nothing yields empty cells rather than a
dropped row. Every cell of the result is a string: the table is written to CSV and read back
by ``pipeline.pack`` as text, and the verdict rules take plain string rows (layer rule 1).

The verdicts themselves live in ``pipeline.rules`` and the requirement figures in
``pipeline/thresholds.csv``; nothing numeric is written down here.
"""

from __future__ import annotations

import pandas as pd

from pipeline import rules

# Columns a source frame may carry for readability and the merged table takes from BushTel.
DROPPED = ("name",)

SERVICES = ("telehealth_video", "school_video_meeting", "mygov_text", "voice_sms")
PUBLISHER_KEYS = ("accc", "ntg2022", "rrl5", "bushtel")
SATELLITE = "SATELLITE_RESIDUAL"


def _cell(value: object) -> str:
    """One frame cell as the string the CSV carries; a missing value is the empty string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def _strings(frame: pd.DataFrame, base: bool) -> pd.DataFrame:
    """A copy of ``frame`` with every cell a string and the duplicated columns removed."""
    columns = [c for c in frame.columns if base or c not in DROPPED]
    out = pd.DataFrame({c: [_cell(v) for v in frame[c]] for c in columns}, columns=columns)
    out["bushtel_id"] = [int(v) for v in out["bushtel_id"]]
    return out


def _int(row: dict[str, str], column: str) -> int:
    """A counted column as an integer; empty, missing or unparseable reads as 0."""
    value = row.get(column, "")
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _publisher_flags(row: dict[str, str]) -> dict[str, int]:
    """What each of the four mobile publishers says about this community, as 0/1."""
    return {
        "accc": int(_int(row, "carriers_4g_count") >= 1),
        "ntg2022": int(_int(row, "ntg2022_listed") == 1),
        "rrl5": int(_int(row, "any_within_5km") >= 1),
        "bushtel": int(row.get("svc_mobile_phone", "") == "Y"),
    }


def _latency(row: dict[str, str], thresholds: dict[str, dict]) -> str:
    """Fixed-access latency for the row: the measured satellite figure, or the open marker."""
    if row.get("nbn_technology", "") == SATELLITE:
        return _cell(thresholds["capability.nbn_satellite.latency"]["value"])
    # No fixed-line or fixed-wireless latency figure is sourced yet (thresholds.csv); the
    # marker names the requirement it is assumed to clear rather than a figure of its own.
    required = thresholds["requirement.telehealth_video.latency"]["value"]
    return f"<{_cell(int(required))} (TBD)"


def _derive(row: dict[str, str], thresholds: dict[str, dict]) -> dict[str, str]:
    """The derived half of one capability row, from the joined source columns."""
    flags = _publisher_flags(row)
    covered = sum(flags.values())
    verdicts = {
        "telehealth_video": rules.telehealth_video(row, thresholds),
        "school_video_meeting": rules.school_video_meeting(row, thresholds),
        "mygov_text": rules.mygov_text(row, thresholds),
        "voice_sms": rules.voice_sms(row),
    }
    words = {name: result["verdict"] for name, result in verdicts.items()}
    derived = {
        "fixed_latency_ms": _latency(row, thresholds),
        "mobile_publishers_available": str(len(PUBLISHER_KEYS)),
        "mobile_sources_covered": str(covered),
        "mobile_sources_disagree": str(int(0 < covered < len(PUBLISHER_KEYS))),
        "mobile_says": ";".join(f"{key}={flags[key]}" for key in PUBLISHER_KEYS),
        "best_path": rules.best_path(row),
    }
    derived.update(words)
    derived["telehealth_reason"] = verdicts["telehealth_video"]["reason"]
    derived["services_failing"] = str(sum(1 for word in words.values() if word == "fails"))
    derived["services_degraded"] = str(sum(1 for word in words.values() if word == "degraded"))
    derived["backhaul_2019"] = row.get("ntg2019_backhaul", "")
    return derived


def _ordered(columns: list[str]) -> list[str]:
    """Derived columns in the order the capability table has always carried them."""
    order = [
        "fixed_latency_ms",
        "mobile_publishers_available",
        "mobile_sources_covered",
        "mobile_sources_disagree",
        "mobile_says",
        "best_path",
        "telehealth_video",
        "telehealth_reason",
        "school_video_meeting",
        "mygov_text",
        "voice_sms",
        "services_failing",
        "services_degraded",
        "backhaul_2019",
    ]
    return [c for c in columns if c not in order] + order


def merge(
    bushtel: pd.DataFrame,
    nbn: pd.DataFrame,
    accc: pd.DataFrame,
    rrl: pd.DataFrame,
    ntg: pd.DataFrame,
    audit: pd.DataFrame,
    thresholds: dict[str, dict],
) -> pd.DataFrame:
    """One row per BushTel community, source columns joined and every verdict decided.

    ``thresholds`` is what ``pipeline.rules.load_thresholds`` returns. The frames may be the
    ones ``pipeline.sources.*.load`` return or the frozen CSV fixtures read as strings; the
    columns each frame happens to carry are passed through untouched, so the two give the
    same answer on every column they share.
    """
    table = _strings(bushtel, base=True)
    for frame in (nbn, accc, rrl, audit, ntg):
        table = table.merge(_strings(frame, base=False), on="bushtel_id", how="left")
    table = table.fillna("")
    table = table.sort_values("bushtel_id").reset_index(drop=True)

    rows = table.to_dict("records")
    derived = pd.DataFrame([_derive(row, thresholds) for row in rows], index=table.index)
    joined = pd.concat([table.drop(columns=derived.columns, errors="ignore"), derived], axis=1)
    joined["bushtel_id"] = [str(value) for value in joined["bushtel_id"]]
    return joined[_ordered(list(joined.columns))]
