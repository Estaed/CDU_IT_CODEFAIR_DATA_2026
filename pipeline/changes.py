"""Diff two capability-table snapshots and describe what changed in plain English.

Standard library only, like ``rules.py``. Both tables are plain dicts keyed on
``bushtel_id`` (one ``csv.DictReader`` row each), so this is unit-tested with hand-built
rows and never touches a data frame.
"""

from __future__ import annotations

import re
from pathlib import Path

# Only the columns the pack shows are compared: the four verdict words, the best-available
# path, the ten presence flags the app renders, and the four mobile "says covered" flags
# packed into ``mobile_says``. Everything else (free text, coordinates, the 5G columns that
# are not in the pack) is ignored on purpose so it never produces a row.
SVC_COLUMNS = (
    ("svc_health_centre", "Health centre"),
    ("svc_school", "School"),
    ("svc_store", "Store"),
    ("svc_police", "Police"),
    ("svc_library", "Library"),
    ("svc_council_centre", "Council service centre"),
    ("svc_employment", "Employment services"),
    ("svc_wifi", "Public Wi-Fi"),
    ("svc_stand", "STAND site"),
    ("svc_aerodrome", "Aerodrome"),
)

VERDICT_LABELS = {
    "telehealth_video": "Telehealth video",
    "school_video_meeting": "School video meeting",
    "mygov_text": "myGov and banking",
    "voice_sms": "Voice and SMS",
    "best_path": "Best available path",
}

# The four publishers packed into one ``mobile_says`` cell, e.g.
# "accc=1;ntg2022=1;rrl5=1;bushtel=1"; diffed as four columns so each publisher flip is its
# own row instead of one opaque string flip.
SAYS_COVERED_KEYS = {
    "accc_says_covered": ("accc", "ACCC coverage"),
    "ntg2022_says_covered": ("ntg2022", "NT Government 2022 list"),
    "rrl5_says_covered": ("rrl5", "Licensed site within 5 km"),
    "bushtel_says_covered": ("bushtel", "BushTel mobile phone row"),
}

LABELS = {**VERDICT_LABELS, **{key: label for key, (_, label) in SAYS_COVERED_KEYS.items()}}
SVC_LABELS = dict(SVC_COLUMNS)

DIFF_COLUMNS = (
    tuple(column for column, _ in SVC_COLUMNS)
    + tuple(VERDICT_LABELS)
    + tuple(SAYS_COVERED_KEYS)
)

HISTORY_NAME_RE = re.compile(r"capability_table_(\d{4}-\d{2}-\d{2})\.csv$")


def _parse_mobile_says(value: str) -> dict[str, str]:
    if not value:
        return {}
    return dict(part.split("=", 1) for part in value.split(";") if "=" in part)


def _value(row: dict[str, str], column: str) -> str:
    if column in SAYS_COVERED_KEYS:
        key, _ = SAYS_COVERED_KEYS[column]
        return _parse_mobile_says(row.get("mobile_says", "")).get(key, "")
    return row.get(column, "")


def diff_tables(older: list[dict], newer: list[dict]) -> list[dict]:
    """Rows that changed between two capability tables, in newer-table id order.

    Returns ``{bushtel_id, name, column, before, after}``; a community present in only one
    table produces one row with ``column == "bushtel_id"`` instead of a per-column diff.
    """
    older_by_id = {row["bushtel_id"]: row for row in older}
    newer_by_id = {row["bushtel_id"]: row for row in newer}
    rows: list[dict] = []

    for bushtel_id, new_row in sorted(newer_by_id.items(), key=lambda item: int(item[0])):
        old_row = older_by_id.get(bushtel_id)
        if old_row is None:
            rows.append(
                {
                    "bushtel_id": bushtel_id,
                    "name": new_row["name"],
                    "column": "bushtel_id",
                    "before": "",
                    "after": "present",
                }
            )
            continue
        for column in DIFF_COLUMNS:
            before = _value(old_row, column)
            after = _value(new_row, column)
            if before != after:
                rows.append(
                    {
                        "bushtel_id": bushtel_id,
                        "name": new_row["name"],
                        "column": column,
                        "before": before,
                        "after": after,
                    }
                )

    for bushtel_id, old_row in sorted(older_by_id.items(), key=lambda item: int(item[0])):
        if bushtel_id not in newer_by_id:
            rows.append(
                {
                    "bushtel_id": bushtel_id,
                    "name": old_row["name"],
                    "column": "bushtel_id",
                    "before": "present",
                    "after": "",
                }
            )

    return rows


def sentence(row: dict) -> str:
    """One row from ``diff_tables`` in plain English."""
    column = row["column"]
    if column == "bushtel_id":
        if row["after"] == "present":
            return f"{row['name']} added to the capability table"
        return f"{row['name']} removed from the capability table"
    if column in SVC_LABELS:
        label = SVC_LABELS[column]
        return f"{label} now listed" if row["after"] == "Y" else f"{label} no longer listed"
    label = LABELS.get(column, column)
    return f"{label}: {row['before']} -> {row['after']}"


def date_of(path: Path) -> str:
    """The ``YYYY-MM-DD`` a history file's name carries."""
    match = HISTORY_NAME_RE.search(Path(path).name)
    if not match:
        raise ValueError(f"not a history file name: {path}")
    return match.group(1)


def newest_pair(history_dir: Path) -> tuple[Path, Path] | None:
    """The two newest history snapshots, oldest first; ``None`` when fewer than two exist."""
    candidates = Path(history_dir).glob("capability_table_*.csv")
    files = sorted(
        (path for path in candidates if HISTORY_NAME_RE.search(path.name)),
        key=lambda path: HISTORY_NAME_RE.search(path.name).group(1),
    )
    if len(files) < 2:
        return None
    return files[-2], files[-1]
