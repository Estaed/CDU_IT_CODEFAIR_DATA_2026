"""NBN source: fixed-line / fixed-wireless footprint membership and distance for 96 communities.

Reads the frozen CC BY 4.0 NBN coverage footprint shapefiles (data.gov.au dataset
9005c4ad-fc82-4f3f-a54e-bc6c62bbc45e, data date 2024-03-26) and emits one row per community,
keyed on ``bushtel_id``. Satellite (Sky Muster) has no published footprint polygon in this
source: a community point inside neither footprint is ``SATELLITE_RESIDUAL``.

Distances are measured in EPSG:3577 (GDA94 / Australian Albers): the regression fixture was
computed in that CRS, and one CRS for the whole NT beats a per-zone MGA split for a 3-dp
regression.

Ported from ``spike/lane_nbn.py`` (2026-09-12) without changing the maths.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.nbn"

# NT bounding box (lon min, lat min, lon max, lat max), used to subset the national shapefiles
# at read time so the wireless footprint (~370 MB zipped) never needs to be fully materialised.
NT_BBOX = (128.9, -26.1, 138.1, -10.8)

EPSG_WGS84 = 4326
EPSG_ALBERS = 3577  # GDA94 / Australian Albers, for metric distance measurement

COLUMNS = [
    "bushtel_id",
    "nbn_technology",
    "in_fixed_line",
    "in_fixed_wireless",
    "dist_km_nearest_fixed_line",
    "dist_km_nearest_fixed_wireless",
    "fixed_line_attrs",
    "fixed_wireless_attrs",
]


def _find_shapefile_member(zip_path: Path) -> str:
    """Return a GDAL /vsizip/ path to the .shp member inside the zip."""
    with zipfile.ZipFile(zip_path) as zf:
        members = zf.namelist()
    shp_members = [m for m in members if m.lower().endswith(".shp")]
    if not shp_members:
        raise RuntimeError(f"No .shp member found in {zip_path}: {members}")
    return f"/vsizip/{zip_path}/{shp_members[0]}"


def _load_nt_subset(zip_path: Path) -> gpd.GeoDataFrame:
    if not zip_path.is_file():
        raise FileNotFoundError(
            f"NBN footprint zip not found: {zip_path}. Re-fetch it with: {FETCH_COMMAND}"
        )
    vsi_path = _find_shapefile_member(zip_path)
    gdf = gpd.read_file(vsi_path, engine="pyogrio", bbox=NT_BBOX)
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=EPSG_WGS84)
    elif gdf.crs.to_epsg() != EPSG_WGS84:
        gdf = gdf.to_crs(epsg=EPSG_WGS84)
    return gdf


def _attrs_to_str(row: pd.Series) -> str:
    return ";".join(f"{k}={v}" for k, v in row.items())


def _nearest_distance_km(point, footprint: gpd.GeoDataFrame) -> float:
    if footprint.empty:
        return float("nan")
    return float(footprint.geometry.distance(point).min()) / 1000.0


def load(fixedline_zip: Path, wireless_zip: Path, communities: pd.DataFrame) -> pd.DataFrame:
    """One row per community in ``communities``, sorted by ``bushtel_id``.

    ``communities`` is the frame from ``pipeline.sources.bushtel.load``, passed in by the
    caller (layer rule 2: modules in ``pipeline/sources`` never import each other); only its
    ``bushtel_id``, ``lat``, ``lon`` columns are read.
    """
    fixedline_zip = Path(fixedline_zip)
    wireless_zip = Path(wireless_zip)

    fixedline_gdf = _load_nt_subset(fixedline_zip)
    wireless_gdf = _load_nt_subset(wireless_zip)

    comm = communities[["bushtel_id", "lat", "lon"]].reset_index(drop=True)
    geometry = [Point(lon, lat) for lon, lat in zip(comm["lon"], comm["lat"], strict=True)]
    comm_gdf = gpd.GeoDataFrame(comm, geometry=geometry, crs=f"EPSG:{EPSG_WGS84}")

    # Spatial joins in WGS84 (within is scale-invariant for point-in-polygon).
    fl_join = gpd.sjoin(comm_gdf, fixedline_gdf, how="left", predicate="within")
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
        bushtel_id = int(comm_row["bushtel_id"])

        fl_row = fl_join.loc[idx] if idx in fl_join.index else None
        fw_row = fw_join.loc[idx] if idx in fw_join.index else None

        in_fixed_line = int(fl_row is not None and pd.notna(fl_row.get("index_right")))
        in_fixed_wireless = int(fw_row is not None and pd.notna(fw_row.get("index_right")))

        fixed_line_attrs = _attrs_to_str(fl_row[fl_attr_cols]) if in_fixed_line else ""
        fixed_wireless_attrs = _attrs_to_str(fw_row[fw_attr_cols]) if in_fixed_wireless else ""

        if in_fixed_line:
            nbn_technology = "FIXED_LINE"
        elif in_fixed_wireless:
            nbn_technology = "FIXED_WIRELESS"
        else:
            nbn_technology = "SATELLITE_RESIDUAL"

        point_albers = comm_albers.geometry.iloc[pos]
        dist_fl = 0.0 if in_fixed_line else _nearest_distance_km(point_albers, fl_albers)
        dist_fw = 0.0 if in_fixed_wireless else _nearest_distance_km(point_albers, fw_albers)

        rows.append(
            {
                "bushtel_id": bushtel_id,
                "nbn_technology": nbn_technology,
                "in_fixed_line": str(in_fixed_line),
                "in_fixed_wireless": str(in_fixed_wireless),
                "dist_km_nearest_fixed_line": str(round(dist_fl, 3)),
                "dist_km_nearest_fixed_wireless": str(round(dist_fw, 3)),
                "fixed_line_attrs": fixed_line_attrs,
                "fixed_wireless_attrs": fixed_wireless_attrs,
            }
        )

    rows.sort(key=lambda r: r["bushtel_id"])
    return pd.DataFrame(rows, columns=COLUMNS)
