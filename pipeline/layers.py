"""The pack's map layers: five towns, ABS SA3 regions and three carrier coverage areas.

PRD OQ13/OQ16, Part 2 "Map layer" seam. Geometry via geopandas/shapely, the same tools
``pipeline.outline`` uses; every vertex is projected with ``outline.project`` (the mirror's
300x480 view box) and rounded to one decimal by that function. Highways are deferred to
Task-23 (both candidate sources failed a scripted download, ``reports/2026-09-15-map-bytes.md``
"Highways" section): no ``highways()`` function exists here yet.

Byte budget, decided by the main loop on 2026-09-15 from ``reports/2026-09-15-map-bytes.md``
(OQ13), not re-derived here: tolerance ``0.02`` degrees for every layer (the 0.01 and 0.02
renders are indistinguishable at phone scale). Measured bytes at that tolerance, clipped to
the Northern Territory:
    cov-telstra (telstra_4g):  81,012
    cov-optus   (optus_4g):    53,546
    cov-tpg     (mocn_4g):     35,165  -- labelled "TPG (Optus sites, MOCN)": TPG's own 4G
                                           file collapses to one ring in the NT and MOCN is
                                           what a TPG customer actually gets there
    regions-sa3 (SA3 2021):    13,663
    towns (5 points):             208
Measured sum about 184 KB on top of the ~260 KB pack; the pack cap became 512,000 bytes
(``scripts/gate.py`` ``PACK_MAX_BYTES``, ``tests/test_pack.py``).

Nothing outside this module's own reach is imported beyond ``pipeline.outline`` (for the
projection) and ``pipeline.sources.accc`` (its ACCC KML cache, reused rather than re-parsed,
per the task's own instruction -- layer rule 2 restricts imports *within*
``pipeline/sources/``, not a sibling module reusing one of them).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

from pipeline import outline
from pipeline.sources import accc

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "out" / "cache"

TOLERANCE_DEG = 0.02
MIN_PROJECTED_AREA = 4.0  # sq. units in the 300x480 view box (K=30), per the task
MIN_DEGREE_AREA = MIN_PROJECTED_AREA / (outline.K**2)

# Duplicated from pipeline.fetch.abs_sa3 / abs_ucl so the pack build never imports a fetch
# module (layer rule 3).
SA3_RAW_PATTERN = "abs_sa3_20*"
SA3_FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_sa3"
UCL_RAW_PATTERN = "abs_ucl_20*"
UCL_FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_ucl"

STATE_COLUMN = "STE_NAME21"
STATE_NAME = "Northern Territory"

SA3_NAME_COLUMN = "SA3_NAME21"
UCL_NAME_COLUMN = "UCL_NAME21"

# Source registered in pipeline.provenance; matched against provenance.citations() keys.
ACCC_PACK_SOURCE = "ACCC MIR 2025"
SA3_PACK_SOURCE = "ABS ASGS SA3 2021"
UCL_PACK_SOURCE = "ABS ASGS UCL 2021"

# Five towns, taken from the UCL centroids, never typed by hand as coordinates.
TOWN_NAMES = ("Darwin", "Katherine", "Tennant Creek", "Alice Springs", "Nhulunbuy")

# The three ACCC coverage layers this task ships, in pack order.
COVERAGE_LAYERS = (
    ("cov-telstra", "Telstra 4G", "telstra_4g"),
    ("cov-optus", "Optus 4G", "optus_4g"),
    ("cov-tpg", "TPG (Optus sites, MOCN)", "mocn_4g"),
)


def _read_path(path: str | Path) -> str:
    """A GDAL/pyogrio-readable path: zipped shapefiles need the ``zip://`` VSI prefix."""
    text = str(path)
    if text.endswith(".zip") and not text.startswith("zip://"):
        text = f"zip://{text}"
    return text


def _newest(raw_dir: Path, pattern: str, fetch_command: str) -> Path:
    found = sorted(Path(raw_dir).glob(pattern))
    if not found:
        raise FileNotFoundError(
            f"no file matches {pattern} under {raw_dir}. Re-fetch it with: {fetch_command}"
        )
    return found[-1]


def _ring_path(coords: list[tuple[float, float]]) -> str:
    """One closed sub-path, ``M x y L x y ... Z``, matching ``outline._ring_path``'s grammar."""
    tokens: list[str] = []
    for index, (lon, lat) in enumerate(coords):
        x, y = outline.project(lat, lon)
        tokens.append("M" if index == 0 else "L")
        tokens.append(f"{x}")
        tokens.append(f"{y}")
    tokens.append("Z")
    return " ".join(tokens)


def _explode(geom) -> list:
    """Every polygonal part of a Polygon/MultiPolygon/GeometryCollection/empty result."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type == "MultiPolygon":
        return list(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        parts: list = []
        for part in geom.geoms:
            parts.extend(_explode(part))
        return parts
    return []  # lines/points left over from a clip along the boundary: not polygonal


def simplify_to_paths(geoms: list, tolerance_deg: float = TOLERANCE_DEG) -> list[str]:
    """Simplify, explode, drop rings under the area floor, project: one path string per ring.

    Exterior rings only (holes dropped), matching ``pipeline.outline``'s own convention.
    """
    if tolerance_deg > 0:
        arr = np.array(geoms, dtype=object)
        simplified = shapely.simplify(arr, tolerance_deg, preserve_topology=True)
    else:
        simplified = geoms
    paths: list[str] = []
    for geom in simplified:
        for part in _explode(geom):
            if part.is_empty or not part.exterior.coords:
                continue
            if part.area < MIN_DEGREE_AREA:
                continue
            paths.append(_ring_path(list(part.exterior.coords)))
    return paths


def load_boundary_union(boundary_path: str | Path) -> BaseGeometry:
    """The full (unsimplified) Northern Territory multipolygon, unioned and prepared.

    Used to clip the coverage layers precisely; ``pipeline.outline`` keeps only its three
    largest parts for the outline *path*, which is too coarse a mask for clipping (the same
    distinction the 2026-09-15 byte-budget measurement drew, ``reports/2026-09-15-map-bytes.md``).
    """
    frame = gpd.read_file(_read_path(boundary_path))
    matches = frame[frame[STATE_COLUMN] == STATE_NAME]
    if matches.empty:
        raise ValueError(f"no {STATE_NAME} feature in {boundary_path}")
    geometry = matches.geometry.iloc[0]
    union = shapely.union_all(list(geometry.geoms))
    shapely.prepare(union)
    return union


def _clip_to_boundary(geoms: list, boundary: BaseGeometry) -> list:
    """Clip a polygon list to ``boundary``: only border-crossers pay for ``intersection()``."""
    if not geoms:
        return []
    arr = np.array(geoms, dtype=object)
    within = shapely.contains(boundary, arr)
    intersects = shapely.intersects(boundary, arr)
    on_border = intersects & ~within
    kept = list(arr[within])
    if on_border.any():
        clipped = shapely.intersection(arr[on_border], boundary)
        for geom in clipped:
            kept.extend(_explode(geom))
    return kept


def coverage(
    layer_id: str,
    label: str,
    kml_path: str | Path,
    boundary: BaseGeometry,
    cache_dir: Path = CACHE_DIR,
    tolerance_deg: float = TOLERANCE_DEG,
) -> dict:
    """One ACCC predicted-coverage layer: NT-clipped, simplified carrier polygons.

    Reuses ``pipeline.sources.accc.nt_polygons``'s own WKB cache under ``data/out/cache/``
    rather than re-parsing the KML (the task's own instruction).
    """
    polygons = accc.nt_polygons(Path(kml_path), Path(cache_dir))
    clipped = _clip_to_boundary(polygons, boundary)
    paths = simplify_to_paths(clipped, tolerance_deg)
    return {"id": layer_id, "label": label, "kind": "area", "src": ACCC_PACK_SOURCE, "paths": paths}


def regions(sa3_zip: str | Path, tolerance_deg: float = TOLERANCE_DEG) -> dict:
    """The ABS SA3 2021 region borders inside the Northern Territory."""
    frame = gpd.read_file(_read_path(sa3_zip))
    nt = frame[frame[STATE_COLUMN] == STATE_NAME]
    nt = nt[nt.geometry.notna() & ~nt.geometry.is_empty]
    geoms: list = []
    for geom in nt.geometry:
        geoms.extend(_explode(geom))
    paths = simplify_to_paths(geoms, tolerance_deg)
    return {
        "id": "regions-sa3",
        "label": "SA3 regions",
        "kind": "line",
        "src": SA3_PACK_SOURCE,
        "paths": paths,
    }


def towns(ucl_zip: str | Path) -> dict:
    """The five town points, from ABS UCL 2021 polygon centroids -- never typed by hand."""
    frame = gpd.read_file(_read_path(ucl_zip))
    points = []
    for name in TOWN_NAMES:
        matches = frame[frame[UCL_NAME_COLUMN].astype(str).str.strip() == name]
        if matches.empty:
            raise ValueError(f"no UCL polygon named {name!r} in {ucl_zip}")
        geometry = shapely.union_all(matches.geometry.tolist())
        centroid = geometry.centroid
        x, y = outline.project(centroid.y, centroid.x)
        points.append({"x": x, "y": y, "label": name})
    return {
        "id": "towns",
        "label": "Towns",
        "kind": "point",
        "src": UCL_PACK_SOURCE,
        "paths": points,
    }


def build_layers(
    raw_dir: str | Path,
    boundary_path: str | Path,
    cache_dir: Path = CACHE_DIR,
    tolerance_deg: float = TOLERANCE_DEG,
) -> list[dict]:
    """All map layers, in pack order: the three ACCC coverage layers, SA3 regions, towns."""
    raw_dir = Path(raw_dir)
    boundary = load_boundary_union(boundary_path)
    sa3_zip = _newest(raw_dir, SA3_RAW_PATTERN, SA3_FETCH_COMMAND)
    ucl_zip = _newest(raw_dir, UCL_RAW_PATTERN, UCL_FETCH_COMMAND)
    layers = [
        coverage(layer_id, label, accc.kml_path(raw_dir, key), boundary, cache_dir, tolerance_deg)
        for layer_id, label, key in COVERAGE_LAYERS
    ]
    layers.append(regions(sa3_zip, tolerance_deg))
    layers.append(towns(ucl_zip))
    return layers
