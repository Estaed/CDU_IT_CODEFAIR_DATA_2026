"""Lane NBN — which NBN access technology serves each of 96 remote NT communities.

Downloads the CC BY 4.0 NBN coverage footprint shapefiles published on data.gov.au
(dataset 9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e, data date 2024-03-26):

- Fixed line:     https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/nbn_coverage_fixedline_2024-03-26.zip
- Fixed wireless:  https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/nbn_coverage_wireless_2024-03-26.zip

Satellite (Sky Muster) has no published footprint polygon in this source: a community
point inside neither the fixed-line nor the fixed-wireless footprint is treated as
SATELLITE_RESIDUAL.

Idempotent: re-running skips downloads whose file already exists with the expected size,
and always rewrites spike/out/nbn.csv from scratch.

Run from the project root:
    PYTHONUTF8=1 .venv/Scripts/python.exe spike/lane_nbn.py
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
import requests
from shapely.geometry import Point

SPIKE_DIR = Path(__file__).resolve().parent
RAW_DIR = SPIKE_DIR / "raw"
OUT_DIR = SPIKE_DIR / "out"
COMMUNITIES_CSV = SPIKE_DIR / "communities.csv"
OUT_CSV = OUT_DIR / "nbn.csv"

USER_AGENT = "CDU-ITCodeFair-2026-spike/0.1"

SOURCES = {
    "fixedline": {
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc/download/"
            "nbn_coverage_fixedline_2024-03-26.zip"
        ),
        "zip_name": "nbn_coverage_fixedline_2024-03-26.zip",
        "expected_bytes": 9_460_437,
    },
    "wireless": {
        "url": (
            "https://data.gov.au/data/dataset/9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e/"
            "resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f/download/"
            "nbn_coverage_wireless_2024-03-26.zip"
        ),
        "zip_name": "nbn_coverage_wireless_2024-03-26.zip",
        "expected_bytes": 378_833_757,
    },
}

# NT bounding box (lon min, lat min, lon max, lat max) used to subset the large
# shapefiles at read time so the wireless footprint (national, ~370MB zipped) never
# needs to be fully materialised in memory.
NT_BBOX = (128.9, -26.1, 138.1, -10.8)

EPSG_WGS84 = 4326
EPSG_ALBERS = 3577  # GDA94 / Australian Albers, for metric distance measurement


def download(name: str, spec: dict) -> Path:
    dest = RAW_DIR / spec["zip_name"]
    if dest.exists() and dest.stat().st_size == spec["expected_bytes"]:
        print(f"[{name}] already downloaded: {dest.name} ({dest.stat().st_size} bytes)")
        return dest

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[{name}] downloading {spec['url']} ...")
    t0 = time.monotonic()
    headers = {"User-Agent": USER_AGENT}
    with requests.get(spec["url"], headers=headers, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        tmp.replace(dest)
    elapsed = time.monotonic() - t0
    size = dest.stat().st_size
    print(f"[{name}] downloaded {size} bytes in {elapsed:.1f}s -> {dest}")
    if size != spec["expected_bytes"]:
        print(
            f"[{name}] WARNING: size {size} does not match expected "
            f"{spec['expected_bytes']}"
        )
    return dest


def find_shapefile_member(zip_path: Path) -> str:
    """Return a GDAL /vsizip/ path to the .shp member inside the zip."""
    import zipfile

    with zipfile.ZipFile(zip_path) as zf:
        members = zf.namelist()
    shp_members = [m for m in members if m.lower().endswith(".shp")]
    if not shp_members:
        raise RuntimeError(f"No .shp member found in {zip_path}: {members}")
    if len(shp_members) > 1:
        print(f"WARNING: multiple .shp members in {zip_path}, using first: {shp_members}")
    return f"/vsizip/{zip_path}/{shp_members[0]}"


def load_nt_subset(name: str, zip_path: Path) -> gpd.GeoDataFrame:
    vsi_path = find_shapefile_member(zip_path)

    info = pyogrio.read_info(vsi_path)
    print(f"[{name}] pyogrio.read_info: {info}")

    gdf = gpd.read_file(vsi_path, engine="pyogrio", bbox=NT_BBOX)
    print(f"[{name}] raw CRS: {gdf.crs}")
    print(f"[{name}] NT-bbox row count: {len(gdf)}")
    print(f"[{name}] columns: {list(gdf.columns)}")
    if len(gdf) > 0:
        print(f"[{name}] sample rows:\n{gdf.head(3).drop(columns='geometry')}")

    if gdf.crs is not None and gdf.crs.to_epsg() != EPSG_WGS84:
        gdf = gdf.to_crs(epsg=EPSG_WGS84)
        print(f"[{name}] reprojected to EPSG:{EPSG_WGS84}")
    elif gdf.crs is None:
        print(f"[{name}] WARNING: no CRS found, assuming EPSG:{EPSG_WGS84}")
        gdf = gdf.set_crs(epsg=EPSG_WGS84)

    return gdf


def attrs_to_str(row: pd.Series, exclude: set[str]) -> str:
    parts = []
    for k, v in row.items():
        if k in exclude:
            continue
        parts.append(f"{k}={v}")
    return ";".join(parts)


def nearest_distance_km(point: Point, footprint: gpd.GeoDataFrame, point_albers_gdf, idx) -> float:
    """Great-circle-ish distance in km from a single community point (projected)
    to the nearest polygon in footprint (already projected to Albers). 0 if inside."""
    if footprint.empty:
        return float("nan")
    p = point_albers_gdf.geometry.iloc[idx]
    dists = footprint.geometry.distance(p)
    return float(dists.min()) / 1000.0


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fixedline_zip = download("fixedline", SOURCES["fixedline"])
    wireless_zip = download("wireless", SOURCES["wireless"])

    fixedline_gdf = load_nt_subset("fixedline", fixedline_zip)
    wireless_gdf = load_nt_subset("wireless", wireless_zip)

    communities = pd.read_csv(COMMUNITIES_CSV)
    print(f"communities.csv: {len(communities)} rows")

    geometry = [Point(lon, lat) for lon, lat in zip(communities["lon"], communities["lat"])]
    comm_gdf = gpd.GeoDataFrame(communities.copy(), geometry=geometry, crs=f"EPSG:{EPSG_WGS84}")

    # Spatial joins in WGS84 (within is scale-invariant for point-in-polygon).
    fl_join = gpd.sjoin(comm_gdf, fixedline_gdf, how="left", predicate="within")
    # sjoin can duplicate rows if a point falls in multiple overlapping polygons;
    # keep first match per community (bushtel_id is unique in the input).
    fl_join = fl_join[~fl_join.index.duplicated(keep="first")]

    fw_join = gpd.sjoin(comm_gdf, wireless_gdf, how="left", predicate="within")
    fw_join = fw_join[~fw_join.index.duplicated(keep="first")]

    fl_attr_cols = [c for c in fixedline_gdf.columns if c != "geometry"]
    fw_attr_cols = [c for c in wireless_gdf.columns if c != "geometry"]

    # Project for metric distance measurement.
    comm_albers = comm_gdf.to_crs(epsg=EPSG_ALBERS)
    fl_albers = fixedline_gdf.to_crs(epsg=EPSG_ALBERS) if not fixedline_gdf.empty else fixedline_gdf
    fw_albers = wireless_gdf.to_crs(epsg=EPSG_ALBERS) if not wireless_gdf.empty else wireless_gdf

    rows = []
    for pos, (idx, comm_row) in enumerate(comm_gdf.iterrows()):
        bushtel_id = comm_row["bushtel_id"]
        name = comm_row["name"]

        fl_row = fl_join.loc[idx] if idx in fl_join.index else None
        fw_row = fw_join.loc[idx] if idx in fw_join.index else None

        in_fixed_line = int(fl_row is not None and pd.notna(fl_row.get("index_right")))
        in_fixed_wireless = int(fw_row is not None and pd.notna(fw_row.get("index_right")))

        fixed_line_attrs = ""
        if in_fixed_line:
            fixed_line_attrs = attrs_to_str(fl_row[fl_attr_cols], exclude=set())

        fixed_wireless_attrs = ""
        if in_fixed_wireless:
            fixed_wireless_attrs = attrs_to_str(fw_row[fw_attr_cols], exclude=set())

        if in_fixed_line:
            nbn_technology = "FIXED_LINE"
        elif in_fixed_wireless:
            nbn_technology = "FIXED_WIRELESS"
        else:
            nbn_technology = "SATELLITE_RESIDUAL"

        dist_fl = 0.0 if in_fixed_line else nearest_distance_km(
            comm_row.geometry, fl_albers, comm_albers, pos
        )
        dist_fw = 0.0 if in_fixed_wireless else nearest_distance_km(
            comm_row.geometry, fw_albers, comm_albers, pos
        )

        rows.append(
            {
                "bushtel_id": bushtel_id,
                "name": name,
                "nbn_technology": nbn_technology,
                "in_fixed_line": in_fixed_line,
                "in_fixed_wireless": in_fixed_wireless,
                "dist_km_nearest_fixed_line": round(dist_fl, 3) if pd.notna(dist_fl) else "",
                "dist_km_nearest_fixed_wireless": round(dist_fw, 3) if pd.notna(dist_fw) else "",
                "fixed_line_attrs": fixed_line_attrs,
                "fixed_wireless_attrs": fixed_wireless_attrs,
            }
        )

    out_df = pd.DataFrame(rows).sort_values("bushtel_id")

    columns = [
        "bushtel_id",
        "name",
        "nbn_technology",
        "in_fixed_line",
        "in_fixed_wireless",
        "dist_km_nearest_fixed_line",
        "dist_km_nearest_fixed_wireless",
        "fixed_line_attrs",
        "fixed_wireless_attrs",
    ]
    out_df = out_df[columns]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        for _, r in out_df.iterrows():
            writer.writerow([r[c] for c in columns])

    print(f"Wrote {len(out_df)} rows to {OUT_CSV}")
    print("nbn_technology distribution:")
    print(out_df["nbn_technology"].value_counts())

    return 0


if __name__ == "__main__":
    sys.exit(main())
