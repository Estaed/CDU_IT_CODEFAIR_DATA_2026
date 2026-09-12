"""Services present per community, from the BushTel profile snapshot.

Source: data/raw/bushtel_community_detail_2026-09-12.json, fetched 2026-09-12 from
https://bushtel.nt.gov.au/api/Community/{id} (undocumented public API, (c) Northern Territory
Government, licence TBD -- Bushtel@nt.gov.au asked). Only the 96 Major/Minor communities in
spike/communities.csv are emitted.

Run from the project root: PYTHONUTF8=1 .venv/Scripts/python.exe spike/lane_bushtel.py
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAIL = ROOT / "data" / "raw" / "bushtel_community_detail_2026-09-12.json"
COMMUNITIES = ROOT / "spike" / "communities.csv"
OUT = ROOT / "spike" / "out" / "bushtel.csv"

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


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    with COMMUNITIES.open(encoding="utf-8", newline="") as f:
        wanted = {int(r["bushtel_id"]): r["name"] for r in csv.DictReader(f)}
    detail = {int(c["Id"]): c for c in json.loads(DETAIL.read_text(encoding="utf-8"))}
    missing = sorted(set(wanted) - set(detail))
    if missing:
        raise SystemExit(f"communities without a BushTel detail record: {missing}")

    fields = ["bushtel_id", "name", "cap_mobile", "cap_internet", "cap_fixed_phone", "cap_road"]
    for stem in SERVICE_COLUMNS.values():
        fields.append(f"svc_{stem}")
        if stem in COMMENT_COLUMNS:
            fields.append(f"{stem}_comment")
    fields += ["road_seasonal_cut", "service_types_listed", "profile_last_updated"]

    rows = []
    for cid in sorted(wanted):
        c = detail[cid]
        cap = c.get("Capabilities") or {}
        services = {s["ServiceType"]: s for s in (c.get("Services") or [])}
        row = {
            "bushtel_id": cid,
            "name": wanted[cid],
            "cap_mobile": int(bool(cap.get("Mobile"))),
            "cap_internet": int(bool(cap.get("Internet"))),
            "cap_fixed_phone": int(bool(cap.get("FixedPhone"))),
            "cap_road": int(bool(cap.get("RoadAccess"))),
        }
        for service_type, stem in SERVICE_COLUMNS.items():
            s = services.get(service_type)
            row[f"svc_{stem}"] = (s or {}).get("Status", "")
            if stem in COMMENT_COLUMNS:
                row[f"{stem}_comment"] = strip_html((s or {}).get("Comments", ""))
        row["road_seasonal_cut"] = int(bool(SEASONAL.search(row["road_access_comment"])))
        row["service_types_listed"] = len(services)
        row["profile_last_updated"] = (c.get("LastUpdated") or {}).get("Profile", "")
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
