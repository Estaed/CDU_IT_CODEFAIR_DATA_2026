"""Throwaway measurement script for the 2026-09-15 map-bytes report (PRD OQ13).

Measures how many bytes each candidate map layer would add to ``data_pack.json`` if
embedded as SVG path strings in the pack's projected coordinate space
(``pipeline.outline.project``, the 300x480 view box), at three ``shapely.simplify``
tolerances plus an unsimplified baseline.

Read-only against ``pipeline/`` and ``data/``: imports ``pipeline.outline.project`` and
``pipeline.sources.accc`` to reuse the pipeline's own projection and its already-cached
NT-clipped ACCC polygons, but calls no pipeline entry point and writes nothing under
``data/out/`` or ``dist/``. All output (the PNGs) goes to this same throwaway folder.

Run from the project root:

    PYTHONUTF8=1 .venv/Scripts/python reports/spike-map-bytes/measure.py

Prints one JSON blob to stdout with every number the report needs; a human report is
written by hand from that output, not generated here.
"""

from __future__ import annotations

import gzip
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapely

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pipeline.outline import K, project  # noqa: E402  (path set above)
from pipeline.sources.accc import JOBS, kml_path, nt_polygons  # noqa: E402

RAW = ROOT / "data" / "raw"
CACHE = ROOT / "data" / "out" / "cache"
OUT_DIR = Path(__file__).resolve().parent

TOLERANCES = [0.0, 0.005, 0.01, 0.02]  # degrees; 0.0 = unsimplified baseline
MIN_PROJECTED_AREA = 4.0  # sq. units in the 300x480 view box, per the task
MIN_DEGREE_AREA = MIN_PROJECTED_AREA / (K * K)  # project() is an isotropic affine map

# ACCC carriers/technologies measured: all REQUIRED plus the optional ones already cached
# (telstra_3g does not exist on the 2025 ACCC release, per pipeline/sources/accc.py).
ACCC_KEYS = [key for key in JOBS if (RAW / f"accc_{key}_outdoor_2025.kml").is_file()]

# Five NT towns, noted per the task ("bytes are trivial, just note them"): approximate
# town-centre coordinates, NOT fetched. A real build would take these from ABS UCL 2021
# centroids or a roads dataset's place-name points.
TOWNS = {
    "Darwin": (-12.4634, 130.8456),
    "Katherine": (-14.4652, 132.2635),
    "Tennant Creek": (-19.6544, 134.1873),
    "Alice Springs": (-23.6980, 133.8807),
    "Nhulunbuy": (-12.1833, 136.7833),
}


def log(*args: object) -> None:
    print(*args, file=sys.stderr, flush=True)


def ring_path(coords: list[tuple[float, float]]) -> str:
    """Same convention as ``pipeline.outline._ring_path``: exterior ring only, one decimal."""
    tokens: list[str] = []
    for index, (lon, lat) in enumerate(coords):
        x, y = project(lat, lon)
        tokens.append("M" if index == 0 else "L")
        tokens.append(f"{x}")
        tokens.append(f"{y}")
    tokens.append("Z")
    return " ".join(tokens)


def explode(geom) -> list:
    """Every polygonal part of a Polygon/MultiPolygon/GeometryCollection/empty result."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type == "MultiPolygon":
        return list(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        out = []
        for part in geom.geoms:
            out.extend(explode(part))
        return out
    return []  # lines/points left over from a clip along the boundary: not polygonal


def load_nt_union():
    frame = gpd.read_file(f"zip://{RAW / 'abs_ste_2021_shp.zip'}")
    nt = frame[frame["STE_NAME21"] == "Northern Territory"].geometry.iloc[0]
    union = shapely.union_all(list(nt.geoms))
    shapely.prepare(union)  # speeds up the contains/intersects masks below
    return union


def clip_to_nt(polygons: list, nt_union) -> list:
    """Clip a polygon list to the NT boundary, fast: only actual border-crossers pay for
    a real ``intersection()`` call; polygons fully inside or fully outside are a cheap
    prepared-geometry predicate. (90210-polygon optus_4g: 374s naive vs 6.4s masked,
    measured 2026-09-15.)"""
    if not polygons:
        return []
    arr = np.array(polygons, dtype=object)
    within = shapely.contains(nt_union, arr)
    intersects = shapely.intersects(nt_union, arr)
    boundary = intersects & ~within
    kept = list(arr[within])
    if boundary.any():
        clipped = shapely.intersection(arr[boundary], nt_union)
        for geom in clipped:
            kept.extend(explode(geom))
    return kept


def measure_layer(polygons: list, tolerance: float) -> dict:
    """One (layer, tolerance) row: bytes, ring/vertex counts, dropped-ring count."""
    if tolerance > 0:
        arr = np.array(polygons, dtype=object)
        simplified = shapely.simplify(arr, tolerance, preserve_topology=True)
    else:
        simplified = polygons

    kept_rings: list[list[tuple[float, float]]] = []
    dropped = 0
    for geom in simplified:
        for part in explode(geom) if geom.geom_type != "Polygon" else [geom]:
            if part.is_empty or not part.exterior.coords:
                continue
            if part.area < MIN_DEGREE_AREA:
                dropped += 1
                continue
            kept_rings.append(list(part.exterior.coords))

    path = " ".join(ring_path(ring) for ring in kept_rings)
    vertex_count = sum(len(ring) for ring in kept_rings)
    note = ""
    if not kept_rings:
        note = "collapses to nothing at this tolerance"
    elif len(kept_rings) <= 2 and len(polygons) > 50:
        note = f"collapses from {len(polygons)} source polygons to {len(kept_rings)}"

    return {
        "bytes": len(path.encode("utf-8")),
        "rings": len(kept_rings),
        "vertices": vertex_count,
        "dropped": dropped,
        "note": note,
        "path": path,
    }


def measure_accc() -> dict:
    results: dict[str, dict] = {}
    nt_union = load_nt_union()
    for key in ACCC_KEYS:
        t0 = time.time()
        raw_polygons = nt_polygons(kml_path(RAW, key), CACHE)
        clipped = clip_to_nt(raw_polygons, nt_union)
        t1 = time.time()
        log(f"accc/{key}: {len(raw_polygons)} raw -> {len(clipped)} clipped ({t1 - t0:.1f}s)")
        rows = {}
        for tol in TOLERANCES:
            rows[tol] = measure_layer(clipped, tol)
        results[key] = {"source_count": len(raw_polygons), "clipped_count": len(clipped), "rows": rows}
    return results


def measure_abs_regions(zip_name: str, code_col: str, name_col: str) -> dict:
    frame = gpd.read_file(f"zip://{RAW / zip_name}")
    nt = frame[frame["STE_NAME21"] == "Northern Territory"]
    nt = nt[nt.geometry.notna() & ~nt.geometry.is_empty]
    polygons: list = []
    for geom in nt.geometry:
        polygons.extend(explode(geom))
    log(f"{zip_name}: {len(nt)} NT regions ({nt[name_col].tolist()}), {len(polygons)} polygon parts")
    rows = {tol: measure_layer(polygons, tol) for tol in TOLERANCES}
    return {"region_count": len(nt), "polygon_parts": len(polygons), "rows": rows}


def measure_towns() -> dict:
    points = []
    for name, (lat, lon) in TOWNS.items():
        x, y = project(lat, lon)
        points.append({"name": name, "x": x, "y": y})
    blob = json.dumps(points, separators=(",", ":"))
    return {"count": len(points), "bytes": len(blob.encode("utf-8")), "sample": blob}


def render_telstra_pngs(nt_union) -> None:
    nt_union_gs = gpd.GeoSeries([nt_union])
    raw_polygons = nt_polygons(kml_path(RAW, "telstra_4g"), CACHE)
    clipped = clip_to_nt(raw_polygons, nt_union)
    arr = np.array(clipped, dtype=object)
    for tol in (0.005, 0.01, 0.02):
        simplified = shapely.simplify(arr, tol, preserve_topology=True)
        kept = [g for g in simplified if not g.is_empty and g.area >= MIN_DEGREE_AREA]
        fig, ax = plt.subplots(figsize=(6, 4.8), dpi=100)
        nt_union_gs.boundary.plot(ax=ax, color="black", linewidth=0.5)
        if kept:
            gpd.GeoSeries(kept).plot(ax=ax, color="crimson", alpha=0.5, edgecolor="none")
        ax.set_title(f"ACCC Telstra 4G outdoor 2025, NT, tolerance={tol}", fontsize=8)
        ax.set_axis_off()
        out_path = OUT_DIR / f"telstra_4g_tol_{tol}.png"
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        log(f"wrote {out_path.name} ({out_path.stat().st_size} bytes, {len(kept)} polygons)")


def gzip_size(blob: bytes) -> int:
    return len(gzip.compress(blob, compresslevel=9))


def main() -> None:
    nt_union = load_nt_union()

    accc_results = measure_accc()
    sa3 = measure_abs_regions("abs_sa3_2021_shp.zip", "SA3_CODE21", "SA3_NAME21")
    sa4 = measure_abs_regions("abs_sa4_2021_shp.zip", "SA4_CODE21", "SA4_NAME21")
    towns = measure_towns()

    render_telstra_pngs(nt_union)

    # "All layers" = every ACCC carrier/tech + SA3 boundaries + towns (fixed, not
    # tolerance-dependent). Highways: TBD, contributes 0. SA4 reported separately, not
    # summed in (SA3 is the layer named in the task; SA4 is the "if easy" extra).
    summary = {}
    for tol in TOLERANCES:
        raw_bytes = 0
        blob_parts = []
        for key in ACCC_KEYS:
            row = accc_results[key]["rows"][tol]
            raw_bytes += row["bytes"]
            blob_parts.append(row["path"])
        raw_bytes += sa3["rows"][tol]["bytes"]
        blob_parts.append(sa3["rows"][tol]["path"])
        raw_bytes += towns["bytes"]
        blob_parts.append(towns["sample"])
        blob = " ".join(blob_parts).encode("utf-8")
        summary[tol] = {"raw_bytes": raw_bytes, "gzip_bytes": gzip_size(blob)}

    output = {
        "accc": {
            key: {
                "source_count": v["source_count"],
                "clipped_count": v["clipped_count"],
                "rows": {
                    tol: {k: vv for k, vv in row.items() if k != "path"}
                    for tol, row in v["rows"].items()
                },
            }
            for key, v in accc_results.items()
        },
        "sa3": {
            "region_count": sa3["region_count"],
            "polygon_parts": sa3["polygon_parts"],
            "rows": {tol: {k: vv for k, vv in row.items() if k != "path"} for tol, row in sa3["rows"].items()},
        },
        "sa4": {
            "region_count": sa4["region_count"],
            "polygon_parts": sa4["polygon_parts"],
            "rows": {tol: {k: vv for k, vv in row.items() if k != "path"} for tol, row in sa4["rows"].items()},
        },
        "towns": {"count": towns["count"], "bytes": towns["bytes"]},
        "summary": summary,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
