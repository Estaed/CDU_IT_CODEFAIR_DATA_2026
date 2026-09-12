"""ACCC lane — for each of 96 remote NT communities, does each carrier's 2025
predicted outdoor coverage polygon contain the community point?

Source: CKAN package ``4b472a18-d0fa-409c-994a-ab17162bcb90``
(``accc-mobile-infrastructure-report-data-release``) on data.gov.au — the ACCC
Mobile Infrastructure Report data release. Licence: Creative Commons
Attribution 2.5 Australia (CC BY 2.5 AU). Release used: the 2025 release,
newest resource ``Last-Modified: 2025-11-10``, covering reporting years
2018-2025. Authors: ACCC, Singtel Optus, Telstra, TPG Telecom.

Resources actually used (``Coverage map - <MNO> - <tech> - Outdoor - 2025``,
resolved at runtime via ``package_show`` — URLs below are what this script
downloaded on 2026-09-12):

    Telstra 4G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/f900c540-4184-4aa5-88cf-7047e8a17d8c/download/coverage-map-telstra-4g-outdoor-2025.kml
    Optus   4G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/e8096d93-610f-44da-9ea2-a28322819f90/download/coverage-map-optus-4g-outdoor-2025.zip
    TPG     4G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/21241ba2-6417-4c8d-b94c-ebac590d3e7f/download/coverage-map-tpg-4g-outdoor-2025.kml
    MOCN    4G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/74b9ef8a-61a6-47ee-91bb-4ad948e888d0/download/coverage-map-optus-tpg-mocn-4g-outdoor-2025.zip
    Optus   3G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/52147286-9492-4044-bbf9-a74159d9568c/download/coverage-map-optus-3g-outdoor-2025.kml
    Telstra 5G  https://data.gov.au/data/dataset/4b472a18-d0fa-409c-994a-ab17162bcb90/resource/ce194ab2-3022-4f21-be68-270790409983/download/coverage-map-telstra-5g-outdoor-2025.kml

    NOT downloaded — no such 2025 "Outdoor" resource exists on the dataset:
    ``Coverage map - Telstra - 3G - Outdoor - 2025``. Telstra's newest 3G
    Outdoor resource on this dataset is 2024; 2025 only has "Ext Ant" (not the
    axis this spike uses). Recorded as -1 ("not downloaded") throughout.

    NOT downloaded — priority-order download budget (1.5 GB / 15 min,
    checked cumulatively as each file completes) was exhausted before
    reaching them: ``Coverage map - Optus - 5G - Outdoor - 2025`` (measured
    759,940,261 bytes) and ``Coverage map - TPG - 5G - Outdoor - 2025``.
    Recorded as -1 ("not downloaded") throughout.

Run: ``PYTHONUTF8=1 .venv/Scripts/python.exe spike/lane_accc.py`` from the
project root. Idempotent: a download already present at the resource's
declared size is not re-fetched; the KML parse and CSV write always re-run.

Distance approximation: for a community not contained in any polygon of a
file, "distance to nearest NT polygon of that file" is computed as
``geometry.distance()`` in decimal degrees, multiplied by 111 to get
kilometres. This is a flat-earth approximation (1 degree of latitude is
~111.0 km everywhere; 1 degree of longitude is ~111 km only near the equator
and shrinks by cos(latitude) at NT latitudes, so east-west distances are
overstated by roughly 5-15% across the NT's latitude range). Acceptable for
a one-day spike distinguishing "close" from "far", not for precise ranging.
"""

from __future__ import annotations

import csv
import os
import shutil
import sys
import time
import zipfile

import requests
from lxml import etree
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

PACKAGE_ID = "4b472a18-d0fa-409c-994a-ab17162bcb90"
PACKAGE_SHOW_URL = (
    f"https://data.gov.au/data/api/3/action/package_show?id={PACKAGE_ID}"
)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_DIR = os.path.join(HERE, "out")
COMMUNITIES_CSV = os.path.join(HERE, "communities.csv")
OUT_CSV = os.path.join(OUT_DIR, "accc.csv")

KML_NS = "{http://www.opengis.net/kml/2.2}"
PLACEMARK_TAG = KML_NS + "Placemark"

# lon_min, lon_max, lat_min, lat_max
NT_BBOX = (128.9, 138.1, -26.1, -10.8)

# 1.5 GB (decimal) and 15 minutes.
DOWNLOAD_BUDGET_BYTES = 1_500_000_000
DOWNLOAD_BUDGET_SECONDS = 15 * 60

# (job key, MNO name as it appears in the resource name, technology)
JOBS = [
    ("telstra_4g", "Telstra", "4G"),
    ("optus_4g", "Optus", "4G"),
    ("tpg_4g", "TPG", "4G"),
    ("mocn_4g", "Optus-TPG MOCN", "4G"),
    ("telstra_3g", "Telstra", "3G"),
    ("optus_3g", "Optus", "3G"),
    ("telstra_5g", "Telstra", "5G"),
    ("optus_5g", "Optus", "5G"),
    ("tpg_5g", "TPG", "5G"),
]

# End of the mandatory 4G set — budget is first checked here.
FOUR_G_SET_END_INDEX = 4  # jobs[0:4] are the 4G set

SANITY_IDS = {
    426: "Wadeye",
    362: "Maningrida",
    492: "Galiwinku",
    198: "Yuendumu",
    633: "Ngukurr",
    72: "Kintore",
    458: "Baniyala",
    294: "Belyuen",
    9: "Amoonguna",
}


def load_communities():
    communities = []
    with open(COMMUNITIES_CSV, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            communities.append(
                {
                    "bushtel_id": int(row["bushtel_id"]),
                    "name": row["name"],
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                }
            )
    communities.sort(key=lambda c: c["bushtel_id"])
    return communities


def fetch_resource_index():
    r = requests.get(PACKAGE_SHOW_URL, timeout=60)
    r.raise_for_status()
    resources = r.json()["result"]["resources"]
    print(f"package_show: {len(resources)} resources total")
    return resources


def find_resource(resources, mno, tech):
    target = f"Coverage map - {mno} - {tech} - Outdoor - 2025"
    for res in resources:
        if res.get("name") == target:
            return res
    return None


def raw_path(key, ext):
    return os.path.join(RAW_DIR, f"accc_{key}_outdoor_2025.{ext}")


def download_file(url, dest_path, expected_size=None):
    """Download url to dest_path via streaming GET. Skips if dest_path
    already exists at expected_size. Returns (bytes_downloaded, seconds)
    where bytes_downloaded is 0 if skipped."""
    if os.path.exists(dest_path):
        actual = os.path.getsize(dest_path)
        if expected_size is None or actual == expected_size:
            print(f"  exists at expected size, skip: {dest_path} ({actual} bytes)")
            return 0, 0.0
        print(
            f"  exists but size mismatch ({actual} != {expected_size}), "
            f"re-downloading: {dest_path}"
        )

    t0 = time.time()
    tmp = dest_path + ".part"
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
    os.replace(tmp, dest_path)
    dt = time.time() - t0
    size = os.path.getsize(dest_path)
    rate = size / dt / 1e6 if dt > 0 else 0.0
    print(f"  downloaded {dest_path}: {size} bytes in {dt:.1f}s ({rate:.2f} MB/s)")
    return size, dt


def extract_kml_from_zip(zip_path, dest_kml_path):
    if os.path.exists(dest_kml_path):
        print(f"  already extracted, skip: {dest_kml_path}")
        return
    with zipfile.ZipFile(zip_path) as zf:
        kml_members = [n for n in zf.namelist() if n.lower().endswith(".kml")]
        if not kml_members:
            raise RuntimeError(f"no .kml member found inside {zip_path}")
        member = kml_members[0]
        tmp = dest_kml_path + ".part"
        with zf.open(member) as src, open(tmp, "wb") as dst:
            shutil.copyfileobj(src, dst)
        os.replace(tmp, dest_kml_path)
    print(f"  extracted {member} -> {dest_kml_path} ({os.path.getsize(dest_kml_path)} bytes)")


def download_all(resources):
    """Returns dict job_key -> kml file path, or None if not downloaded."""
    os.makedirs(RAW_DIR, exist_ok=True)
    kml_paths = {}
    cumulative_bytes = 0
    start = time.time()
    stopped = False

    for idx, (key, mno, tech) in enumerate(JOBS):
        if idx == FOUR_G_SET_END_INDEX:
            elapsed = time.time() - start
            if cumulative_bytes > DOWNLOAD_BUDGET_BYTES or elapsed > DOWNLOAD_BUDGET_SECONDS:
                print(
                    f"Budget exceeded after 4G set "
                    f"({cumulative_bytes} bytes, {elapsed:.0f}s) — stopping."
                )
                stopped = True

        if stopped:
            print(f"[{key}] skipped: download budget exhausted")
            kml_paths[key] = None
            continue

        resource = find_resource(resources, mno, tech)
        if resource is None:
            print(f"[{key}] no 2025 Outdoor resource named 'Coverage map - {mno} - {tech} - Outdoor - 2025' — skipping")
            kml_paths[key] = None
            continue

        size = resource.get("size") or 0
        elapsed = time.time() - start
        if idx >= FOUR_G_SET_END_INDEX and (
            cumulative_bytes + size > DOWNLOAD_BUDGET_BYTES or elapsed > DOWNLOAD_BUDGET_SECONDS
        ):
            print(
                f"[{key}] skipped: downloading {size} bytes would exceed budget "
                f"(cumulative {cumulative_bytes}, elapsed {elapsed:.0f}s) — stopping remaining downloads"
            )
            stopped = True
            kml_paths[key] = None
            continue

        fmt = (resource.get("format") or "").upper()
        url = resource["url"]
        print(f"[{key}] {resource['name']} | {fmt} | {size} bytes | {url}")

        if fmt == "ZIP":
            zip_dest = raw_path(key, "zip")
            downloaded, dt = download_file(url, zip_dest, expected_size=size)
            cumulative_bytes += downloaded
            kml_dest = raw_path(key, "kml")
            extract_kml_from_zip(zip_dest, kml_dest)
            kml_paths[key] = kml_dest
        else:
            kml_dest = raw_path(key, "kml")
            downloaded, dt = download_file(url, kml_dest, expected_size=size)
            cumulative_bytes += downloaded
            kml_paths[key] = kml_dest

    print(
        f"Total downloaded this run: {cumulative_bytes} bytes in "
        f"{time.time() - start:.1f}s"
    )
    return kml_paths


def parse_coords(text):
    pts = []
    for tok in text.split():
        parts = tok.split(",")
        pts.append((float(parts[0]), float(parts[1])))
    return pts


def ring_bbox(coords):
    lons = [p[0] for p in coords]
    lats = [p[1] for p in coords]
    return min(lons), max(lons), min(lats), max(lats)


def bbox_intersects(a, b):
    return not (a[1] < b[0] or a[0] > b[1] or a[3] < b[2] or a[2] > b[3])


def iter_polygons(placemark_elem):
    for poly_el in placemark_elem.iter(KML_NS + "Polygon"):
        outer_el = poly_el.find(
            f"{KML_NS}outerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates"
        )
        if outer_el is None or not outer_el.text or not outer_el.text.strip():
            continue
        outer = parse_coords(outer_el.text)
        if len(outer) < 3:
            continue
        holes = []
        for inner_el in poly_el.findall(
            f"{KML_NS}innerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates"
        ):
            if inner_el.text and inner_el.text.strip():
                hole = parse_coords(inner_el.text)
                if len(hole) >= 3:
                    holes.append(hole)
        yield outer, holes


def clear_element(elem):
    elem.clear()
    while elem.getprevious() is not None:
        del elem.getparent()[0]


def parse_kml_for_communities(path, communities):
    """Streams a KML's Placemarks and tests each of the 96 community points
    for containment in NT-bbox polygons. Returns a dict with per-community
    'inside' (0/1) and 'dist_km' (0 if inside, else approximate km to
    nearest NT polygon in this file; see module docstring for the
    approximation), plus summary counters."""
    t0 = time.time()
    total_placemarks = 0
    nt_bbox_placemarks = 0
    invalid_count = 0
    nt_polygons = []
    inside = {c["bushtel_id"]: 0 for c in communities}

    context = etree.iterparse(path, tag=PLACEMARK_TAG, huge_tree=True)
    for _event, elem in context:
        total_placemarks += 1
        kept_any = False
        for outer, holes in iter_polygons(elem):
            obox = ring_bbox(outer)
            if not bbox_intersects(obox, NT_BBOX):
                continue
            kept_any = True
            poly = Polygon(outer, holes)
            if not poly.is_valid:
                invalid_count += 1
                poly = poly.buffer(0)
            if poly.is_empty:
                continue
            nt_polygons.append(poly)
            for c in communities:
                if obox[0] <= c["lon"] <= obox[1] and obox[2] <= c["lat"] <= obox[3]:
                    if inside[c["bushtel_id"]] == 0 and poly.contains(
                        Point(c["lon"], c["lat"])
                    ):
                        inside[c["bushtel_id"]] = 1
        if kept_any:
            nt_bbox_placemarks += 1
        clear_element(elem)

    dist_km = {c["bushtel_id"]: 0.0 for c in communities}
    not_inside = [c for c in communities if inside[c["bushtel_id"]] == 0]
    if not_inside and nt_polygons:
        tree = STRtree(nt_polygons)
        for c in not_inside:
            pt = Point(c["lon"], c["lat"])
            nearest_idx = tree.nearest(pt)
            nearest_poly = nt_polygons[nearest_idx]
            dist_km[c["bushtel_id"]] = nearest_poly.distance(pt) * 111.0
    elif not_inside and not nt_polygons:
        # No NT geometry at all in this file for this carrier/tech.
        for c in not_inside:
            dist_km[c["bushtel_id"]] = -1.0

    elapsed = time.time() - t0
    print(
        f"  parsed {path}: total_placemarks={total_placemarks} "
        f"nt_bbox_placemarks={nt_bbox_placemarks} invalid_geometry={invalid_count} "
        f"elapsed={elapsed:.1f}s"
    )
    return {
        "inside": inside,
        "dist_km": dist_km,
        "total_placemarks": total_placemarks,
        "nt_bbox_placemarks": nt_bbox_placemarks,
        "invalid_count": invalid_count,
        "elapsed": elapsed,
    }


def main():
    communities = load_communities()
    resources = fetch_resource_index()

    print("\nMatching 2025 Outdoor coverage-map resources:")
    for _key, mno, tech in JOBS:
        res = find_resource(resources, mno, tech)
        if res is None:
            print(f"  Coverage map - {mno} - {tech} - Outdoor - 2025: NOT FOUND")
        else:
            print(
                f"  {res['name']} | {res.get('format')} | {res.get('size')} bytes | {res['url']}"
            )

    print("\nDownloading (priority order, 1.5 GB / 15 min budget after the 4G set):")
    kml_paths = download_all(resources)

    print("\nParsing:")
    results = {}
    for key, _mno, _tech in JOBS:
        path = kml_paths.get(key)
        if path is None or not os.path.exists(path):
            results[key] = None
            continue
        results[key] = parse_kml_for_communities(path, communities)

    os.makedirs(OUT_DIR, exist_ok=True)
    fieldnames = [
        "bushtel_id",
        "name",
        "telstra_4g_2025",
        "optus_4g_2025",
        "tpg_4g_2025",
        "mocn_4g_2025",
        "telstra_3g_2025",
        "optus_3g_2025",
        "telstra_5g_2025",
        "optus_5g_2025",
        "tpg_5g_2025",
        "carriers_4g_count",
        "dist_km_telstra_4g",
        "dist_km_optus_4g",
        "dist_km_tpg_4g",
    ]

    def flag(key, bushtel_id):
        r = results.get(key)
        if r is None:
            return -1
        return r["inside"][bushtel_id]

    def dist(key, bushtel_id):
        r = results.get(key)
        if r is None:
            return -1.0
        if r["inside"][bushtel_id] == 1:
            return 0.0
        return round(r["dist_km"][bushtel_id], 3)

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for c in communities:
            bid = c["bushtel_id"]
            t4 = flag("telstra_4g", bid)
            o4 = flag("optus_4g", bid)
            tp4 = flag("tpg_4g", bid)
            m4 = flag("mocn_4g", bid)
            carriers_4g = max(t4, 0) + max(o4, 0) + max(max(tp4, 0), max(m4, 0))
            writer.writerow(
                {
                    "bushtel_id": bid,
                    "name": c["name"],
                    "telstra_4g_2025": t4,
                    "optus_4g_2025": o4,
                    "tpg_4g_2025": tp4,
                    "mocn_4g_2025": m4,
                    "telstra_3g_2025": flag("telstra_3g", bid),
                    "optus_3g_2025": flag("optus_3g", bid),
                    "telstra_5g_2025": flag("telstra_5g", bid),
                    "optus_5g_2025": flag("optus_5g", bid),
                    "tpg_5g_2025": flag("tpg_5g", bid),
                    "carriers_4g_count": carriers_4g,
                    "dist_km_telstra_4g": dist("telstra_4g", bid),
                    "dist_km_optus_4g": dist("optus_4g", bid),
                    "dist_km_tpg_4g": dist("tpg_4g", bid),
                }
            )
    print(f"\nWrote {OUT_CSV} ({len(communities)} rows)")

    print("\nSanity checks:")
    by_id = {c["bushtel_id"]: c for c in communities}
    for bid, expected_name in SANITY_IDS.items():
        c = by_id.get(bid)
        if c is None:
            print(f"  {bid} ({expected_name}): NOT IN communities.csv")
            continue
        print(
            f"  {bid} {c['name']}: telstra_4g={flag('telstra_4g', bid)} "
            f"optus_4g={flag('optus_4g', bid)} tpg_4g={flag('tpg_4g', bid)} "
            f"mocn_4g={flag('mocn_4g', bid)}"
        )

    counts = [
        max(flag("telstra_4g", c["bushtel_id"]), 0)
        + max(flag("optus_4g", c["bushtel_id"]), 0)
        + max(
            max(flag("tpg_4g", c["bushtel_id"]), 0),
            max(flag("mocn_4g", c["bushtel_id"]), 0),
        )
        for c in communities
    ]
    print(f"\ncarriers_4g_count distribution over 96: {sorted(counts)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
