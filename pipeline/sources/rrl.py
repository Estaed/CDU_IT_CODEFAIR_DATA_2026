"""ACMA RRL source: carrier cellular-band transmit sites near each of the 96 communities.

Reads the frozen bulk extract of the ACMA Register of Radiocommunications Licences written by
``pipeline.fetch.rrl`` and emits the *licensed* publisher line, keyed on ``bushtel_id``: for
each carrier group, whether a site lies within 5, 10 and 40 km, and the nearest site's
distance, carrier, name and precision. Ported from ``spike/lane_rrl_ntg.py`` part (a)
(2026-09-12) without changing the licence filtering.

Source: https://web.acma.gov.au/rrl/spectra_rrl.zip (301 -> https://cdn.acma.gov.au/rrl/
spectra_rrl.zip), daily bulk extract, no key; landing page
https://www.acma.gov.au/radiocomms-licence-data. Fetch date 2026-09-12.

Licence (LICENCE.TXT inside the zip, condensed): intellectual property in the Register is
retained by the ACMA, which grants a non-transferable, non-exclusive licence to use, reproduce
and adapt the Register, develop derivative material from it and distribute that material to
third parties. Client information may be used only for spectrum management under the
Radiocommunications Act 1992, never for unsolicited commercial messages or telemarketing.
Required attribution: "Based on Australian Communications and Media Authority information."

Join path: client.csv -> licence.csv -> device_details.csv -> site.csv, streamed from inside
the zip. Cellular base stations sit under Spectrum and PTS licences, not Land Mobile; see
reports/2026-09-12-arena-reconcile.md S3.
"""

from __future__ import annotations

import csv
import io
import math
import re
import zipfile
from pathlib import Path

import pandas as pd

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.rrl"

# Inclusion by substring on LICENCEE or TRADING_NAME (uppercased); MOBILE JV is its own group.
CARRIER_KEYWORDS = {
    "telstra": ["TELSTRA"],
    "optus": ["OPTUS"],
    "tpg": ["VODAFONE", "TPG"],
    "jv": ["MOBILE JV"],
}
# Non-mobile affiliates and personal-name false positives to drop regardless of keyword hit.
EXCLUDE_SUBSTRINGS = [
    "PAY TV",
    "BROADCAST SERVICES",
    "VISION MEDIA",
    "SATELLITE NETWORK",
    "TPG TV",
]
EXCLUDE_EXACT_NAMES = {"RJ & DC HUTCHISON", "JASON HUTCHISON"}

CARRIER_LABEL = {"telstra": "Telstra", "optus": "Optus", "tpg": "TPG/Vodafone", "jv": "Mobile JV"}

# Cellular band windows in Hz (device_details.FREQUENCY is in Hz: 778000000 with emission
# 20M0W7D is 778 MHz, inside the 700 MHz band). See reports/2026-09-12-arena-reconcile.md S3.5.
CELLULAR_BANDS_HZ = {
    "700": (703_000_000, 803_000_000),
    "850": (803_000_000, 873_000_000),
    "900": (873_000_000, 960_000_000),
    "1800": (1_710_000_000, 1_880_000_000),
    "2100": (1_900_000_000, 2_170_000_000),
    "2300": (2_300_000_000, 2_400_000_000),
    "2600": (2_500_000_000, 2_690_000_000),
    "3500": (3_300_000_000, 3_800_000_000),
    "26000": (24_250_000_000, 29_500_000_000),
}

GRANTED_STATUS = "1"  # licence_status.csv: 1 = Granted
TRANSMIT_DEVICE = "T"
THRESHOLDS_KM = [5, 10, 40]
EARTH_RADIUS_KM = 6371.0088

SITE_COLUMNS = [
    "site_id",
    "lat",
    "lon",
    "name",
    "precision",
    "carrier_group",
    "bands",
    "device_count",
]


def columns() -> list[str]:
    """The frame's columns, in order."""
    fields = ["bushtel_id"]
    for group in CARRIER_LABEL:
        fields += [f"{group}_within_{t}km" for t in THRESHOLDS_KM]
    fields += [f"any_within_{t}km" for t in THRESHOLDS_KM]
    fields += [
        "nearest_site_km",
        "nearest_site_carrier",
        "nearest_site_name",
        "nearest_site_precision",
    ]
    return fields


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def normalise_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


def _reader(handle) -> csv.DictReader:
    return csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8", errors="replace"))


def classify_carrier(licencee: str, trading_name: str) -> str | None:
    lic = (licencee or "").upper()
    trd = (trading_name or "").upper()
    combined = f"{lic} {trd}"
    if lic.strip() in EXCLUDE_EXACT_NAMES or trd.strip() in EXCLUDE_EXACT_NAMES:
        return None
    if any(sub in combined for sub in EXCLUDE_SUBSTRINGS):
        return None
    for group, keywords in CARRIER_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return group
    return None


def load_carrier_clients(zf: zipfile.ZipFile) -> dict[str, str]:
    """``{CLIENT_NO: carrier_group}`` for kept carrier clients."""
    kept: dict[str, str] = {}
    with zf.open("client.csv") as f:
        for row in _reader(f):
            lic = row.get("LICENCEE", "") or ""
            trd = row.get("TRADING_NAME", "") or ""
            combined = f"{lic.upper()} {trd.upper()}"
            candidate = any(kw in combined for kws in CARRIER_KEYWORDS.values() for kw in kws)
            if not candidate:
                continue
            group = classify_carrier(lic, trd)
            if group is not None:
                kept[row["CLIENT_NO"]] = group
    return kept


def load_carrier_licences(zf: zipfile.ZipFile, client_groups: dict[str, str]) -> dict[str, str]:
    """``{LICENCE_NO: carrier_group}`` for granted licences held by kept carrier clients."""
    licence_group: dict[str, str] = {}
    with zf.open("licence.csv") as f:
        for row in _reader(f):
            group = client_groups.get(row.get("CLIENT_NO", ""))
            if group is None:
                continue
            if row.get("STATUS", "") != GRANTED_STATUS:
                continue
            licence_group[row["LICENCE_NO"]] = group
    return licence_group


def frequency_band(freq_hz: float) -> str | None:
    for band, (lo, hi) in CELLULAR_BANDS_HZ.items():
        if lo <= freq_hz <= hi:
            return band
    return None


def stream_carrier_devices(zf: zipfile.ZipFile, licence_group: dict[str, str]) -> dict[str, dict]:
    """Stream device_details.csv without extracting it.

    Returns ``{SITE_ID: {group: {"bands": set, "device_count": int}}}``.
    """
    site_groups: dict[str, dict] = {}
    with zf.open("device_details.csv") as f:
        for row in _reader(f):
            group = licence_group.get(row.get("LICENCE_NO", ""))
            if group is None:
                continue
            if row.get("DEVICE_TYPE") != TRANSMIT_DEVICE:
                continue
            freq_raw = row.get("FREQUENCY", "")
            if not freq_raw:
                continue
            band = frequency_band(float(freq_raw))
            if band is None:
                continue
            site_id = row.get("SITE_ID", "")
            if not site_id:
                continue
            site_entry = site_groups.setdefault(site_id, {})
            group_entry = site_entry.setdefault(group, {"bands": set(), "device_count": 0})
            group_entry["bands"].add(band)
            group_entry["device_count"] += 1
    return site_groups


def load_nt_sites(zf: zipfile.ZipFile) -> dict[str, dict]:
    nt_sites: dict[str, dict] = {}
    with zf.open("site.csv") as f:
        for row in _reader(f):
            if row.get("STATE") != "NT":
                continue
            try:
                lat = float(row["LATITUDE"])
                lon = float(row["LONGITUDE"])
            except (KeyError, ValueError, TypeError):
                continue
            nt_sites[row["SITE_ID"]] = {
                "lat": lat,
                "lon": lon,
                "name": row.get("NAME", ""),
                "precision": row.get("SITE_PRECISION", ""),
            }
    return nt_sites


def _require(path: Path) -> Path:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"ACMA RRL extract not found: {path}. Re-fetch it with: {FETCH_COMMAND}"
        )
    return path


def sites(rrl_zip: Path) -> pd.DataFrame:
    """One row per (NT site, carrier group) with a granted cellular-band transmitter."""
    rrl_zip = _require(rrl_zip)
    with zipfile.ZipFile(rrl_zip) as zf:
        client_groups = load_carrier_clients(zf)
        licence_group = load_carrier_licences(zf, client_groups)
        site_groups = stream_carrier_devices(zf, licence_group)
        nt_sites = load_nt_sites(zf)

    rows = []
    for site_id, group_entry in site_groups.items():
        site_info = nt_sites.get(site_id)
        if site_info is None:
            continue  # not an NT site
        for group, data in group_entry.items():
            rows.append(
                {
                    "site_id": site_id,
                    "lat": site_info["lat"],
                    "lon": site_info["lon"],
                    "name": site_info["name"],
                    "precision": site_info["precision"],
                    "carrier_group": group,
                    "bands": ";".join(sorted(data["bands"])),
                    "device_count": data["device_count"],
                }
            )
    rows.sort(key=lambda r: (r["carrier_group"], r["site_id"]))
    return pd.DataFrame(rows, columns=SITE_COLUMNS)


def write_sites(frame: pd.DataFrame, path: Path) -> None:
    """Write the per-site table as UTF-8 CSV with LF line endings."""
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(SITE_COLUMNS)
        for record in frame[SITE_COLUMNS].itertuples(index=False):
            writer.writerow(list(record))


def _row(community: dict, sites_by_group: dict[str, list[dict]]) -> dict:
    clat, clon = community["lat"], community["lon"]
    row: dict = {"bushtel_id": int(community["bushtel_id"])}
    any_within = {t: 0 for t in THRESHOLDS_KM}
    nearest_km = float("inf")
    nearest_site = None

    for group in CARRIER_LABEL:
        within = {t: 0 for t in THRESHOLDS_KM}
        for site in sites_by_group[group]:
            d = haversine_km(clat, clon, site["lat"], site["lon"])
            for t in THRESHOLDS_KM:
                if d <= t:
                    within[t] = 1
                    any_within[t] = 1
            if d < nearest_km:
                nearest_km = d
                nearest_site = site
        for t in THRESHOLDS_KM:
            row[f"{group}_within_{t}km"] = str(within[t])

    for t in THRESHOLDS_KM:
        row[f"any_within_{t}km"] = str(any_within[t])

    if nearest_site is not None and math.isfinite(nearest_km):
        row["nearest_site_km"] = str(round(nearest_km, 3))
        row["nearest_site_carrier"] = CARRIER_LABEL[nearest_site["carrier_group"]]
        row["nearest_site_name"] = str(nearest_site["name"])
        row["nearest_site_precision"] = str(nearest_site["precision"])
    else:
        row["nearest_site_km"] = ""
        row["nearest_site_carrier"] = ""
        row["nearest_site_name"] = ""
        row["nearest_site_precision"] = ""
    return row


def load(rrl_zip: Path, communities: pd.DataFrame) -> pd.DataFrame:
    """One row per community in ``communities``, sorted by ``bushtel_id``."""
    site_records = sites(rrl_zip).to_dict("records")
    sites_by_group = {
        group: [s for s in site_records if s["carrier_group"] == group] for group in CARRIER_LABEL
    }
    rows = [
        _row(community, sites_by_group)
        for community in communities[["bushtel_id", "lat", "lon"]].to_dict("records")
    ]
    rows.sort(key=lambda r: r["bushtel_id"])
    return pd.DataFrame(rows, columns=columns())
