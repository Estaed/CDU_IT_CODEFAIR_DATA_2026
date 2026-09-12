"""Lane RRL/NTG — ACMA licensed cellular sites near each community, and NT Government
mobile-coverage list membership, for 96 remote NT communities.

Part (a) — ACMA Register of Radiocommunications Licences (RRL), daily bulk extract,
no key required:
    https://web.acma.gov.au/rrl/spectra_rrl.zip  (301 -> https://cdn.acma.gov.au/rrl/spectra_rrl.zip)
Landing page: https://www.acma.gov.au/radiocomms-licence-data

Licence note (from LICENCE.TXT inside the zip, verbatim, condensed to two lines):
    "Intellectual Property in the Register is retained by the ACMA... [but] the ACMA
    grants you a non-transferable, non-exclusive Licence to use, reproduce and adapt
    the Register... to develop derivative material based on the Register, and to
    distribute any derivatives developed by you to third parties."
Client/personal information may only be used for spectrum management under the
Radiocommunications Act 1992, never for unsolicited commercial messages or
telemarketing. Required attribution when derived material is published: "Based on
Australian Communications and Media Authority information."

The join path used here is client.csv -> licence.csv -> device_details.csv -> site.csv.
Cellular base stations sit under `Spectrum` (SV_ID 85) and `PTS` licences, NOT
`Land Mobile` (private radio) -- see reports/2026-09-12-arena-reconcile.md S3 for the
full reconciliation that this module reimplements.

Part (b) — NT Government open-data mobile coverage lists (data.nt.gov.au, CC BY),
resolved via the CKAN API (package_show) rather than hardcoded download URLs, because
resource IDs are stable but the CKAN API is the documented way to resolve them:
    - 2019: list-of-remote-communities-with-mobile-coverage
    - 2021: remote-communities-with-mobile-coverage
    - 2022: mobile-phone-coverage-in-remote-areas-of-the-nt
    - small cell: remote-sites-with-mobile-phone-small-cell-coverage
See reports/2026-09-12-arena-reconcile.md S4 for column layouts and header offsets.

Fetch date: 2026-09-12.

Idempotent: re-running skips the RRL download when a same-size file already exists
in spike/raw/, always re-downloads the (small) NTG xlsx files, and always rewrites the
three spike/out/*.csv files from scratch.

Run from the project root:
    PYTHONUTF8=1 .venv/Scripts/python.exe spike/lane_rrl_ntg.py
"""

from __future__ import annotations

import csv
import io
import math
import re
import sys
import time
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd
import requests

SPIKE_DIR = Path(__file__).resolve().parent
RAW_DIR = SPIKE_DIR / "raw"
OUT_DIR = SPIKE_DIR / "out"
COMMUNITIES_CSV = SPIKE_DIR / "communities.csv"

RRL_URL = "https://web.acma.gov.au/rrl/spectra_rrl.zip"
RRL_ZIP = RAW_DIR / "spectra_rrl.zip"

USER_AGENT = "CDU-ITCodeFair-2026-spike/0.1"

# --- NT Government CKAN package names and the xlsx we save each resource as -------------
NTG_PACKAGES = {
    "2019": "list-of-remote-communities-with-mobile-coverage",
    "2021": "remote-communities-with-mobile-coverage",
    "2022": "mobile-phone-coverage-in-remote-areas-of-the-nt",
    "smallcell": "remote-sites-with-mobile-phone-small-cell-coverage",
}
CKAN_PACKAGE_SHOW = "https://data.nt.gov.au/api/3/action/package_show"

# --- Carrier client classification -------------------------------------------------------
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

# Cellular band windows in Hz, ±~60 MHz around the nominal band centre/range quoted in
# reports/2026-09-12-arena-reconcile.md S3.5. device_details.FREQUENCY is confirmed in Hz
# below (sample row: FREQUENCY=778000000 with EMISSION 20M0W7D -> 778 MHz, inside the
# Australian 700 MHz band 703-803 MHz).
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

RRL_SITES_NT_CSV = OUT_DIR / "rrl_sites_nt.csv"
RRL_OUT_CSV = OUT_DIR / "rrl.csv"
NTG_OUT_CSV = OUT_DIR / "ntg.csv"

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def normalise_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


# --- Part (a): RRL ------------------------------------------------------------------------


def download_rrl_zip() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    if RRL_ZIP.exists():
        head = requests.head(RRL_URL, headers=headers, timeout=60, allow_redirects=True)
        remote_size = int(head.headers.get("Content-Length", -1))
        local_size = RRL_ZIP.stat().st_size
        if remote_size == local_size:
            print(f"[rrl] already downloaded, size matches remote: {local_size} bytes")
            return RRL_ZIP
        print(f"[rrl] local size {local_size} != remote {remote_size}, re-downloading")

    print(f"[rrl] downloading {RRL_URL} ...")
    t0 = time.monotonic()
    tmp = RRL_ZIP.with_suffix(RRL_ZIP.suffix + ".part")
    with requests.get(RRL_URL, headers=headers, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    tmp.replace(RRL_ZIP)
    elapsed = time.monotonic() - t0
    size = RRL_ZIP.stat().st_size
    print(f"[rrl] downloaded {size} bytes in {elapsed:.1f}s -> {RRL_ZIP}")
    return RRL_ZIP


def read_licence_txt(zf: zipfile.ZipFile) -> None:
    text = zf.read("LICENCE.TXT").decode("utf-8", errors="replace")
    print("[rrl] LICENCE.TXT (verbatim, first 400 chars):")
    print(text[:400])


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
    """Return {CLIENT_NO: carrier_group} for kept carrier clients, printing kept/excluded."""
    kept: dict[str, str] = {}
    kept_rows = []
    excluded_rows = []
    with zf.open("client.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
        for row in reader:
            lic = row.get("LICENCEE", "") or ""
            trd = row.get("TRADING_NAME", "") or ""
            combined = f"{lic.upper()} {trd.upper()}"
            candidate = any(
                kw in combined for kws in CARRIER_KEYWORDS.values() for kw in kws
            )
            if not candidate:
                continue
            group = classify_carrier(lic, trd)
            if group is None:
                excluded_rows.append((row["CLIENT_NO"], lic, trd))
            else:
                kept[row["CLIENT_NO"]] = group
                kept_rows.append((row["CLIENT_NO"], group, lic, trd))

    print(f"[rrl] carrier client rows kept: {len(kept_rows)}")
    for client_no, group, lic, trd in kept_rows:
        print(f"  KEEP  {client_no} [{group}] {lic!r} / {trd!r}")
    print(f"[rrl] carrier client rows excluded: {len(excluded_rows)}")
    for client_no, lic, trd in excluded_rows:
        print(f"  DROP  {client_no} {lic!r} / {trd!r}")
    return kept


def load_carrier_licences(zf: zipfile.ZipFile, client_groups: dict[str, str]) -> dict[str, str]:
    """Return {LICENCE_NO: carrier_group} for granted licences held by kept carrier clients."""
    licence_group: dict[str, str] = {}
    status_seen: dict[str, int] = {}
    with zf.open("licence.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
        for row in reader:
            client_no = row.get("CLIENT_NO", "")
            group = client_groups.get(client_no)
            if group is None:
                continue
            status = row.get("STATUS", "")
            status_seen[status] = status_seen.get(status, 0) + 1
            if status != GRANTED_STATUS:
                continue
            licence_group[row["LICENCE_NO"]] = group
    print(f"[rrl] licence STATUS values seen among carrier-client licences: {status_seen}")
    print(f"[rrl] STATUS kept: {GRANTED_STATUS!r} (Granted); licences kept: {len(licence_group)}")
    return licence_group


def frequency_band(freq_hz: float) -> str | None:
    for band, (lo, hi) in CELLULAR_BANDS_HZ.items():
        if lo <= freq_hz <= hi:
            return band
    return None


def stream_carrier_devices(
    zf: zipfile.ZipFile, licence_group: dict[str, str]
) -> dict[str, dict]:
    """Stream device_details.csv (385MB) without extracting; return
    {SITE_ID: {"groups": {group: {"bands": set(), "device_count": int}}}}."""
    site_groups: dict[str, dict] = {}
    n_rows = 0
    n_transmit_carrier = 0
    unit_sample_printed = False
    with zf.open("device_details.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
        for row in reader:
            n_rows += 1
            licence_no = row.get("LICENCE_NO", "")
            group = licence_group.get(licence_no)
            if group is None:
                continue
            if row.get("DEVICE_TYPE") != "T":
                continue
            freq_raw = row.get("FREQUENCY", "")
            if not freq_raw:
                continue
            freq_hz = float(freq_raw)
            if not unit_sample_printed:
                print(
                    f"[rrl] FREQUENCY unit check: raw={freq_raw!r} "
                    f"-> interpreted as {freq_hz / 1e6:.3f} MHz (assuming Hz)"
                )
                unit_sample_printed = True
            band = frequency_band(freq_hz)
            if band is None:
                continue
            n_transmit_carrier += 1
            site_id = row.get("SITE_ID", "")
            if not site_id:
                continue
            site_entry = site_groups.setdefault(site_id, {})
            group_entry = site_entry.setdefault(group, {"bands": set(), "device_count": 0})
            group_entry["bands"].add(band)
            group_entry["device_count"] += 1
    print(f"[rrl] device_details.csv rows streamed: {n_rows}")
    print(f"[rrl] carrier transmit rows in cellular bands (pre-NT-filter): {n_transmit_carrier}")
    return site_groups


def load_nt_sites(zf: zipfile.ZipFile) -> dict[str, dict]:
    sites: dict[str, dict] = {}
    with zf.open("site.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
        for row in reader:
            if row.get("STATE") != "NT":
                continue
            try:
                lat = float(row["LATITUDE"])
                lon = float(row["LONGITUDE"])
            except (KeyError, ValueError, TypeError):
                continue
            sites[row["SITE_ID"]] = {
                "lat": lat,
                "lon": lon,
                "name": row.get("NAME", ""),
                "precision": row.get("SITE_PRECISION", ""),
            }
    print(f"[rrl] NT sites in site.csv: {len(sites)}")
    return sites


def build_rrl_sites_nt(zf: zipfile.ZipFile) -> pd.DataFrame:
    read_licence_txt(zf)
    client_groups = load_carrier_clients(zf)
    licence_group = load_carrier_licences(zf, client_groups)
    site_groups = stream_carrier_devices(zf, licence_group)
    nt_sites = load_nt_sites(zf)

    rows = []
    per_carrier_sites: dict[str, set] = {g: set() for g in CARRIER_LABEL}
    for site_id, group_entry in site_groups.items():
        site_info = nt_sites.get(site_id)
        if site_info is None:
            continue  # not an NT site
        for group, data in group_entry.items():
            per_carrier_sites[group].add(site_id)
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

    df = pd.DataFrame(rows).sort_values(["carrier_group", "site_id"]).reset_index(drop=True)

    print("[rrl] NT cellular-band transmit sites by carrier group (reference: 464 union / "
          "Telstra 333 / Optus 162 / TPG 81):")
    all_sites = set()
    for group in CARRIER_LABEL:
        n = len(per_carrier_sites[group])
        all_sites |= per_carrier_sites[group]
        print(f"  {CARRIER_LABEL[group]}: {n} distinct sites")
    print(f"  Union (any carrier group): {len(all_sites)} distinct sites")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RRL_SITES_NT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        columns = ["site_id", "lat", "lon", "name", "precision", "carrier_group", "bands", "device_count"]
        writer.writerow(columns)
        for _, r in df.iterrows():
            writer.writerow([r[c] for c in columns])
    print(f"[rrl] wrote {len(df)} rows to {RRL_SITES_NT_CSV}")
    return df


def build_rrl_csv(communities: pd.DataFrame, sites_df: pd.DataFrame) -> pd.DataFrame:
    thresholds_km = [5, 10, 40]
    groups = list(CARRIER_LABEL.keys())

    sites_by_group = {g: sites_df[sites_df["carrier_group"] == g] for g in groups}

    rows = []
    for _, comm in communities.iterrows():
        bushtel_id = comm["bushtel_id"]
        name = comm["name"]
        clat, clon = comm["lat"], comm["lon"]

        row = {"bushtel_id": bushtel_id, "name": name}
        any_within = {t: 0 for t in thresholds_km}
        nearest_km = float("inf")
        nearest_site = None

        for group in groups:
            gsites = sites_by_group[group]
            within = {t: 0 for t in thresholds_km}
            for _, site in gsites.iterrows():
                d = haversine_km(clat, clon, site["lat"], site["lon"])
                for t in thresholds_km:
                    if d <= t:
                        within[t] = 1
                        any_within[t] = 1
                if d < nearest_km:
                    nearest_km = d
                    nearest_site = site
            for t in thresholds_km:
                row[f"{group}_within_{t}km"] = within[t]

        for t in thresholds_km:
            row[f"any_within_{t}km"] = any_within[t]

        if nearest_site is not None and math.isfinite(nearest_km):
            row["nearest_site_km"] = round(nearest_km, 3)
            row["nearest_site_carrier"] = CARRIER_LABEL[nearest_site["carrier_group"]]
            row["nearest_site_name"] = nearest_site["name"]
            row["nearest_site_precision"] = nearest_site["precision"]
        else:
            row["nearest_site_km"] = ""
            row["nearest_site_carrier"] = ""
            row["nearest_site_name"] = ""
            row["nearest_site_precision"] = ""

        rows.append(row)

    df = pd.DataFrame(rows).sort_values("bushtel_id").reset_index(drop=True)

    columns = ["bushtel_id", "name"]
    for group in ["telstra", "optus", "tpg", "jv"]:
        for t in thresholds_km:
            columns.append(f"{group}_within_{t}km")
    for t in thresholds_km:
        columns.append(f"any_within_{t}km")
    columns += ["nearest_site_km", "nearest_site_carrier", "nearest_site_name", "nearest_site_precision"]

    df = df[columns]
    with open(RRL_OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        for _, r in df.iterrows():
            writer.writerow([r[c] for c in columns])
    print(f"[rrl] wrote {len(df)} rows to {RRL_OUT_CSV}")
    return df


# --- Part (b): NT Government coverage lists ------------------------------------------------


def resolve_ntg_urls() -> dict[str, str]:
    urls = {}
    headers = {"User-Agent": USER_AGENT}
    for key, package_name in NTG_PACKAGES.items():
        resp = requests.get(CKAN_PACKAGE_SHOW, params={"id": package_name}, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        resources = data["result"]["resources"]
        xlsx_resources = [r for r in resources if r.get("format", "").upper() == "XLSX"]
        if not xlsx_resources:
            raise RuntimeError(f"No XLSX resource found for package {package_name}")
        urls[key] = xlsx_resources[0]["url"]
        print(f"[ntg] resolved {key} -> {urls[key]}")
    return urls


def download_ntg_files() -> dict[str, Path]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    urls = resolve_ntg_urls()
    headers = {"User-Agent": USER_AGENT}
    paths = {}
    for key, url in urls.items():
        dest = RAW_DIR / f"ntg_{key}.xlsx"
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        print(f"[ntg] downloaded {key}: {len(resp.content)} bytes -> {dest}")
        paths[key] = dest
    return paths


def load_2019(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Sheet1"]
    rows = []
    for r in range(3, ws.max_row + 1):
        vals = [c.value for c in ws[r]]
        if not vals or vals[0] is None:
            continue
        rows.append(
            {
                "name": vals[0],
                "lat": vals[1],
                "lon": vals[2],
                "backhaul": vals[3],
                "provider": vals[4],
            }
        )
    return rows


def load_2021(path: Path) -> tuple[list[dict], list[dict]]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws_with_mobile = wb["Communities with Mobile"]
    with_mobile = []
    for r in range(2, ws_with_mobile.max_row + 1):
        vals = [c.value for c in ws_with_mobile[r]]
        if not vals or vals[0] is None:
            continue
        with_mobile.append({"name": vals[0], "type": vals[1], "lon": vals[2], "lat": vals[3]})

    ws_all = wb["Communities"]
    gazetteer = []
    for r in range(2, ws_all.max_row + 1):
        vals = [c.value for c in ws_all[r]]
        if not vals or vals[0] is None:
            continue
        gazetteer.append(
            {
                "name": vals[0],
                "type": vals[1],
                "lon": vals[2],
                "lat": vals[3],
                "mobile_phone": vals[4],
                "comment": vals[5],
            }
        )
    return with_mobile, gazetteer


def load_2022(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Communities with Mobile"]
    rows = []
    for r in range(6, ws.max_row + 1):
        vals = [c.value for c in ws[r]]
        if not vals or vals[0] is None:
            continue
        rows.append(
            {
                "name": vals[0],
                "site_type": vals[1],
                "population": vals[2],
                "macro": vals[3],
                "small": vals[4],
                "proximity": vals[5],
                "provider": vals[6],
                "lat": vals[7],
                "lon": vals[8],
            }
        )
    return rows


def load_smallcell(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Sheet1"]
    rows = []
    for r in range(3, ws.max_row + 1):
        vals = [c.value for c in ws[r]]
        if not vals or vals[0] is None:
            continue
        rows.append({"name": vals[0], "lat": vals[1], "lon": vals[2], "provider": vals[3]})
    return rows


def match_community(
    comm_names_norm: set[str], list_rows: list[dict], name_key: str = "name"
) -> dict | None:
    """Return the first list row whose normalised name matches any of the community's
    normalised name/aliases, or None."""
    for row in list_rows:
        if normalise_name(row[name_key]) in comm_names_norm:
            return row
    return None


def build_ntg_csv(communities: pd.DataFrame, ntg_paths: dict[str, Path]) -> pd.DataFrame:
    rows_2019 = load_2019(ntg_paths["2019"])
    with_mobile_2021, gazetteer_2021 = load_2021(ntg_paths["2021"])
    rows_2022 = load_2022(ntg_paths["2022"])
    rows_smallcell = load_smallcell(ntg_paths["smallcell"])

    print(f"[ntg] 2019 rows: {len(rows_2019)}; 2021 with-mobile: {len(with_mobile_2021)}, "
          f"gazetteer: {len(gazetteer_2021)}; 2022 rows: {len(rows_2022)}; "
          f"smallcell rows: {len(rows_smallcell)}")

    matched_2022_names = set()
    out_rows = []
    for _, comm in communities.iterrows():
        bushtel_id = comm["bushtel_id"]
        name = comm["name"]
        clat, clon = comm["lat"], comm["lon"]
        aliases = [a.strip() for a in str(comm.get("aliases", "") or "").split(",") if a.strip()]
        names_norm = {normalise_name(name)} | {normalise_name(a) for a in aliases}

        row = {"bushtel_id": bushtel_id, "name": name}

        m2022 = match_community(names_norm, rows_2022)
        if m2022 is not None:
            matched_2022_names.add(normalise_name(m2022["name"]))
            dist = ""
            if m2022.get("lat") is not None and m2022.get("lon") is not None:
                dist = round(haversine_km(clat, clon, float(m2022["lat"]), float(m2022["lon"])), 3)
            row.update(
                {
                    "ntg2022_listed": 1,
                    "ntg2022_matched_name": m2022["name"],
                    "ntg2022_site_type": m2022["site_type"] or "",
                    "ntg2022_macro": 1 if m2022["macro"] else 0,
                    "ntg2022_small": 1 if m2022["small"] else 0,
                    "ntg2022_proximity": 1 if m2022["proximity"] else 0,
                    "ntg2022_provider": m2022["provider"] or "",
                    "ntg2022_population": m2022["population"] if m2022["population"] is not None else "",
                    "ntg2022_coord_dist_km": dist,
                }
            )
        else:
            row.update(
                {
                    "ntg2022_listed": 0,
                    "ntg2022_matched_name": "",
                    "ntg2022_site_type": "",
                    "ntg2022_macro": "",
                    "ntg2022_small": "",
                    "ntg2022_proximity": "",
                    "ntg2022_provider": "",
                    "ntg2022_population": "",
                    "ntg2022_coord_dist_km": "",
                }
            )

        m2021_wm = match_community(names_norm, with_mobile_2021)
        row["ntg2021_with_mobile_listed"] = 1 if m2021_wm is not None else 0

        m2021_gaz = match_community(names_norm, gazetteer_2021)
        if m2021_gaz is not None:
            row["ntg2021_mobile_phone"] = m2021_gaz["mobile_phone"] or ""
            row["ntg2021_comment"] = m2021_gaz["comment"] or ""
        else:
            row["ntg2021_mobile_phone"] = ""
            row["ntg2021_comment"] = ""

        m2019 = match_community(names_norm, rows_2019)
        if m2019 is not None:
            dist = ""
            if m2019.get("lat") is not None and m2019.get("lon") is not None:
                dist = round(haversine_km(clat, clon, float(m2019["lat"]), float(m2019["lon"])), 3)
            row.update(
                {
                    "ntg2019_listed": 1,
                    "ntg2019_backhaul": m2019["backhaul"] or "",
                    "ntg2019_provider": m2019["provider"] or "",
                    "ntg2019_coord_dist_km": dist,
                }
            )
        else:
            row.update(
                {
                    "ntg2019_listed": 0,
                    "ntg2019_backhaul": "",
                    "ntg2019_provider": "",
                    "ntg2019_coord_dist_km": "",
                }
            )

        msmall = match_community(names_norm, rows_smallcell)
        if msmall is not None:
            row["smallcell_listed"] = 1
            row["smallcell_provider"] = msmall["provider"] or ""
        else:
            row["smallcell_listed"] = 0
            row["smallcell_provider"] = ""

        out_rows.append(row)

    unmatched_community_2022 = [
        r["name"]
        for r in rows_2022
        if str(r["site_type"] or "").upper() == "COMMUNITY"
        and normalise_name(r["name"]) not in matched_2022_names
    ]
    print(f"[ntg] unmatched 2022 SITE TYPE=COMMUNITY names ({len(unmatched_community_2022)}): "
          f"{unmatched_community_2022}")

    df = pd.DataFrame(out_rows).sort_values("bushtel_id").reset_index(drop=True)
    columns = [
        "bushtel_id", "name",
        "ntg2022_listed", "ntg2022_matched_name", "ntg2022_site_type", "ntg2022_macro",
        "ntg2022_small", "ntg2022_proximity", "ntg2022_provider", "ntg2022_population",
        "ntg2022_coord_dist_km",
        "ntg2021_with_mobile_listed", "ntg2021_mobile_phone", "ntg2021_comment",
        "ntg2019_listed", "ntg2019_backhaul", "ntg2019_provider", "ntg2019_coord_dist_km",
        "smallcell_listed", "smallcell_provider",
    ]
    df = df[columns]
    with open(NTG_OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        for _, r in df.iterrows():
            writer.writerow([r[c] for c in columns])
    print(f"[ntg] wrote {len(df)} rows to {NTG_OUT_CSV}")
    return df


# --- Sanity checks -------------------------------------------------------------------------


def run_sanity_checks(rrl_df: pd.DataFrame, ntg_df: pd.DataFrame, communities: pd.DataFrame) -> None:
    print("\n[sanity] --- checks ---")

    def rrl_row(bid):
        r = rrl_df[rrl_df["bushtel_id"] == bid]
        return r.iloc[0] if len(r) else None

    def ntg_row(bid):
        r = ntg_df[ntg_df["bushtel_id"] == bid]
        return r.iloc[0] if len(r) else None

    wadeye = rrl_row(426)
    wadeye_ntg = ntg_row(426)
    print(f"[sanity] Wadeye (426) telstra_within_5km={wadeye['telstra_within_5km'] if wadeye is not None else 'MISSING'}, "
          f"ntg2022_macro={wadeye_ntg['ntg2022_macro'] if wadeye_ntg is not None else 'MISSING'}")

    nturiya_ntg = ntg_row(127)
    print(f"[sanity] Nturiya (127) ntg2019_coord_dist_km={nturiya_ntg['ntg2019_coord_dist_km'] if nturiya_ntg is not None else 'MISSING'} "
          f"(expect ~16 km)")

    kalkarindji = ntg_row(603)
    print(f"[sanity] Kalkarindji (603) ntg2019_listed={kalkarindji['ntg2019_listed'] if kalkarindji is not None else 'MISSING'}, "
          f"ntg2021_with_mobile_listed={kalkarindji['ntg2021_with_mobile_listed'] if kalkarindji is not None else 'MISSING'}, "
          f"ntg2022_listed={kalkarindji['ntg2022_listed'] if kalkarindji is not None else 'MISSING'}")

    finke = ntg_row(36)
    print(f"[sanity] Finke (36) ntg2021_with_mobile_listed={finke['ntg2021_with_mobile_listed'] if finke is not None else 'MISSING'}, "
          f"ntg2022_listed={finke['ntg2022_listed'] if finke is not None else 'MISSING'}")

    baniyala = rrl_row(458)
    mapuru = rrl_row(524)
    print(f"[sanity] Baniyala (458) nearest_site_km={baniyala['nearest_site_km'] if baniyala is not None else 'MISSING'}")
    print(f"[sanity] Mapuru (524) nearest_site_km={mapuru['nearest_site_km'] if mapuru is not None else 'MISSING'}")


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    communities = pd.read_csv(COMMUNITIES_CSV)
    print(f"communities.csv: {len(communities)} rows")

    rrl_zip_path = download_rrl_zip()
    with zipfile.ZipFile(rrl_zip_path) as zf:
        sites_df = build_rrl_sites_nt(zf)
    rrl_df = build_rrl_csv(communities, sites_df)

    ntg_paths = download_ntg_files()
    ntg_df = build_ntg_csv(communities, ntg_paths)

    run_sanity_checks(rrl_df, ntg_df, communities)

    print("\n[rrl] any_within_5km distribution (all 96):")
    print(rrl_df["any_within_5km"].value_counts())
    print("[rrl] any_within_40km distribution (all 96):")
    print(rrl_df["any_within_40km"].value_counts())

    spike20_ids = communities.loc[communities["spike20"] == 1, "bushtel_id"]
    rrl_spike20 = rrl_df[rrl_df["bushtel_id"].isin(spike20_ids)]
    print("[rrl] any_within_5km distribution (spike20=1, 20 communities):")
    print(rrl_spike20["any_within_5km"].value_counts())
    print("[rrl] any_within_40km distribution (spike20=1, 20 communities):")
    print(rrl_spike20["any_within_40km"].value_counts())

    print("\n[ntg] listed counts (of 96):")
    for col in ["ntg2022_listed", "ntg2021_with_mobile_listed", "ntg2019_listed", "smallcell_listed"]:
        print(f"  {col}: {int(ntg_df[col].sum())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
