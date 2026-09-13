"""BushTel source: identity, services present and capability flags for 96 communities.

Reads the frozen detail snapshot written by ``pipeline.fetch.bushtel`` and emits the base
frame every other source joins onto, keyed on ``bushtel_id``. Ported from
``spike/lane_bushtel.py`` (2026-09-12); the spike's ``communities.csv`` is not read here
because the detail snapshot already carries every identity field it held.

Source: https://bushtel.nt.gov.au/api/Community/{id} (undocumented public API, (c) Northern
Territory Government, licence TBD).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel"
COMMUNITY_TYPES = ("Major", "Minor")
COORD_DECIMALS = 6

# BushTel ServiceType -> output column stem. Status is Y / N / U (unknown) or "" when the
# service type is not listed for that community at all.
SERVICE_COLUMNS = {
    "Health centre": "health_centre",
    "School": "school",
    "Community store": "store",
    "Police station": "police",
    "Library": "library",
    "Regional council service centre": "council_centre",
    "Employment services": "employment",
    "WiFi": "wifi",
    "STAND Site": "stand",
    "Internet": "internet",
    "Mobile phone": "mobile_phone",
    "Aerodrome": "aerodrome",
    "Accessible by road": "road_access",
}
# Comments are kept for the service types where the free text carries a fact the table needs
# (opening hours, operator, seasonal road cut).
COMMENT_COLUMNS = {"wifi", "stand", "internet", "mobile_phone", "road_access"}
SEASONAL = re.compile(r"wet season|dry season|flood|impassable|closed|cut off|not accessible", re.I)

IDENTITY_COLUMNS = [
    "bushtel_id",
    "name",
    "aliases",
    "community_type",
    "nt_region",
    "population_abs2021",
    "sa1_code",
    "lat",
    "lon",
]


def columns() -> list[str]:
    """The frame's columns, in order: identity first, then the spike's service columns."""
    fields = list(IDENTITY_COLUMNS)
    fields += ["cap_mobile", "cap_internet", "cap_fixed_phone", "cap_road"]
    for stem in SERVICE_COLUMNS.values():
        fields.append(f"svc_{stem}")
        if stem in COMMENT_COLUMNS:
            fields.append(f"{stem}_comment")
    fields += ["road_seasonal_cut", "service_types_listed", "profile_last_updated"]
    return fields


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def to_iso_date(stamp: str) -> str:
    """``dd/mm/yyyy, hh:mm:ss AM`` -> ``yyyy-mm-dd``; empty stays empty."""
    match = re.match(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})", stamp or "")
    if not match:
        return ""
    day, month, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _row(community: dict) -> dict:
    cap = community.get("Capabilities") or {}
    point = community.get("Point") or {}
    services = {s["ServiceType"]: s for s in (community.get("Services") or [])}
    row = {
        "bushtel_id": int(community["Id"]),
        "name": community.get("DefaultName") or "",
        "aliases": community.get("AliasNamesString") or "",
        "community_type": community.get("CommunityTypeName") or "",
        "nt_region": community.get("NTRegionName") or "",
        "population_abs2021": int(community.get("Population") or 0),
        "sa1_code": community.get("Sa1Code") or "",
        # BushTel returns full float precision; the spike's table is 6 dp (~0.1 m) and the
        # regression fixture is written against that.
        "lat": round(float(point.get("Latitude")), COORD_DECIMALS),
        "lon": round(float(point.get("Longitude")), COORD_DECIMALS),
        "cap_mobile": str(int(bool(cap.get("Mobile")))),
        "cap_internet": str(int(bool(cap.get("Internet")))),
        "cap_fixed_phone": str(int(bool(cap.get("FixedPhone")))),
        "cap_road": str(int(bool(cap.get("RoadAccess")))),
    }
    for service_type, stem in SERVICE_COLUMNS.items():
        service = services.get(service_type) or {}
        row[f"svc_{stem}"] = service.get("Status", "")
        if stem in COMMENT_COLUMNS:
            row[f"{stem}_comment"] = strip_html(service.get("Comments", ""))
    row["road_seasonal_cut"] = str(int(bool(SEASONAL.search(row["road_access_comment"]))))
    row["service_types_listed"] = str(len(services))
    row["profile_last_updated"] = to_iso_date((community.get("LastUpdated") or {}).get("Profile"))
    return row


def load(detail_path: Path) -> pd.DataFrame:
    """One row per Major/Minor BushTel community, sorted by ``bushtel_id``."""
    detail_path = Path(detail_path)
    if not detail_path.is_file():
        raise FileNotFoundError(
            f"BushTel snapshot not found: {detail_path}. Re-fetch it with: {FETCH_COMMAND}"
        )
    records = json.loads(detail_path.read_text(encoding="utf-8"))
    rows = [_row(c) for c in records if c.get("CommunityTypeName") in COMMUNITY_TYPES]
    rows.sort(key=lambda r: r["bushtel_id"])
    return pd.DataFrame(rows, columns=columns())
