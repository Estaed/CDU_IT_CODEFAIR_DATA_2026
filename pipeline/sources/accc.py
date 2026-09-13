"""ACCC source: carrier predicted outdoor coverage 2025 for 96 communities.

For each carrier and technology in the ACCC Mobile Infrastructure Report 2025 outdoor coverage
polygons, whether the community point is inside, the distance in km to the nearest 4G polygon
per carrier, and ``carriers_4g_count``. Every value is a carrier *prediction*, not a
measurement, and must be labelled so downstream.

Source: CKAN package ``4b472a18-d0fa-409c-994a-ab17162bcb90``
(``accc-mobile-infrastructure-report-data-release``) on data.gov.au, the ACCC Mobile
Infrastructure Report data release. Licence: Creative Commons Attribution 2.5 Australia
(CC BY 2.5 AU). Release used: 2025, newest resource ``Last-Modified: 2025-11-10``. Resources
``Coverage map - <MNO> - <tech> - Outdoor - 2025``, fetched by ``pipeline.fetch.accc`` to
``accc_<key>_outdoor_2025.kml``.

Files in the 2026-09-12 snapshot are the six ``REQUIRED`` keys; a required file missing is an
error. The other three are recorded as ``-1`` ("file not available") when absent and parsed
when present: Telstra 3G Outdoor 2025 does not exist on the dataset (2025 only has "Ext Ant"),
and Optus 5G and TPG 5G exceeded the 2026-09-12 download budget.

The KMLs are up to 1.4 GB and a streaming parse of all six takes about 50 minutes, so the NT
subset of each file is parsed once and cached under ``cache_dir`` as WKB, keyed on the KML's
size and mtime.

Distance approximation: for a point outside every polygon of a file, the distance to the
nearest NT polygon is ``geometry.distance()`` in decimal degrees multiplied by 111.0. This is
a flat-earth approximation (east-west distances overstated by roughly 5-15% at NT latitudes),
kept because the 2026-09-12 regression fixture holds these values; it separates "close" from
"far", it is not precise ranging.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import shapely
from lxml import etree
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.accc"

KML_NS = "{http://www.opengis.net/kml/2.2}"
PLACEMARK_TAG = KML_NS + "Placemark"

# lon_min, lon_max, lat_min, lat_max
NT_BBOX = (128.9, 138.1, -26.1, -10.8)
KM_PER_DEGREE = 111.0

JOBS = (
    "telstra_4g",
    "optus_4g",
    "tpg_4g",
    "mocn_4g",
    "telstra_3g",
    "optus_3g",
    "telstra_5g",
    "optus_5g",
    "tpg_5g",
)
REQUIRED = ("telstra_4g", "optus_4g", "tpg_4g", "mocn_4g", "optus_3g", "telstra_5g")
DISTANCE_JOBS = ("telstra_4g", "optus_4g", "tpg_4g")

COLUMNS = (
    ["bushtel_id"]
    + [f"{key}_2025" for key in JOBS]
    + ["carriers_4g_count"]
    + [f"dist_km_{key}" for key in DISTANCE_JOBS]
)


def kml_path(kml_dir: Path, key: str) -> Path:
    return Path(kml_dir) / f"accc_{key}_outdoor_2025.kml"


def parse_coords(text: str) -> list[tuple[float, float]]:
    points = []
    for token in text.split():
        parts = token.split(",")
        points.append((float(parts[0]), float(parts[1])))
    return points


def ring_bbox(coords: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    lons = [p[0] for p in coords]
    lats = [p[1] for p in coords]
    return min(lons), max(lons), min(lats), max(lats)


def bbox_intersects(a: tuple, b: tuple) -> bool:
    return not (a[1] < b[0] or a[0] > b[1] or a[3] < b[2] or a[2] > b[3])


def iter_polygons(placemark):
    """Yield ``(outer, holes)`` coordinate lists for every ``<Polygon>`` under a Placemark."""
    for polygon_el in placemark.iter(KML_NS + "Polygon"):
        outer_el = polygon_el.find(
            f"{KML_NS}outerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates"
        )
        if outer_el is None or not outer_el.text or not outer_el.text.strip():
            continue
        outer = parse_coords(outer_el.text)
        if len(outer) < 3:
            continue
        holes = []
        for inner_el in polygon_el.findall(
            f"{KML_NS}innerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates"
        ):
            if inner_el.text and inner_el.text.strip():
                hole = parse_coords(inner_el.text)
                if len(hole) >= 3:
                    holes.append(hole)
        yield outer, holes


def clear_element(elem) -> None:
    elem.clear()
    while elem.getprevious() is not None:
        del elem.getparent()[0]


def parse_nt_polygons(kml_path: Path) -> list[BaseGeometry]:
    """Stream a KML's Placemarks and return every polygon whose outer ring touches the NT."""
    polygons: list[BaseGeometry] = []
    context = etree.iterparse(str(kml_path), tag=PLACEMARK_TAG, huge_tree=True)
    for _event, elem in context:
        for outer, holes in iter_polygons(elem):
            if not bbox_intersects(ring_bbox(outer), NT_BBOX):
                continue
            polygon = Polygon(outer, holes)
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
            if polygon.is_empty:
                continue
            polygons.append(polygon)
        clear_element(elem)
    return polygons


def nt_polygons(kml_path: Path, cache_dir: Path) -> list[BaseGeometry]:
    """The NT polygons of a KML, from the cache when its size and mtime still match."""
    kml_path = Path(kml_path)
    cache_dir = Path(cache_dir)
    stat = kml_path.stat()
    cache_path = cache_dir / f"{kml_path.stem}.nt.pkl"
    if cache_path.is_file():
        with cache_path.open("rb") as f:
            cached = pickle.load(f)
        if cached.get("size") == stat.st_size and cached.get("mtime_ns") == stat.st_mtime_ns:
            return list(shapely.from_wkb(cached["polygons"]))

    polygons = parse_nt_polygons(kml_path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "kml": kml_path.name,
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "polygons": [shapely.to_wkb(p) for p in polygons],
    }
    temporary = cache_path.with_name(cache_path.name + ".part")
    with temporary.open("wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(cache_path)
    return polygons


def point_results(
    polygons: list[BaseGeometry], communities: pd.DataFrame
) -> tuple[dict[int, int], dict[int, float]]:
    """Containment (1/0) and distance in km to the nearest polygon for each community.

    Distance is 0.0 when inside, degrees * 111.0 otherwise (see the module docstring), and -1.0
    for every community when the file had no NT polygon at all.
    """
    points = {
        int(bushtel_id): Point(float(lon), float(lat))
        for bushtel_id, lat, lon in zip(
            communities["bushtel_id"], communities["lat"], communities["lon"], strict=True
        )
    }
    inside = dict.fromkeys(points, 0)
    dist_km = dict.fromkeys(points, 0.0)
    if not polygons:
        return inside, dict.fromkeys(points, -1.0)

    tree = STRtree(polygons)
    for bushtel_id, point in points.items():
        # The tree query returns the polygons whose bounds contain the point.
        if any(polygons[int(i)].contains(point) for i in tree.query(point)):
            inside[bushtel_id] = 1

    for bushtel_id, point in points.items():
        if not inside[bushtel_id]:
            nearest = polygons[int(tree.nearest(point))]
            dist_km[bushtel_id] = nearest.distance(point) * KM_PER_DEGREE
    return inside, dist_km


def load(kml_dir: Path, communities: pd.DataFrame, cache_dir: Path) -> pd.DataFrame:
    """One row per community, sorted by ``bushtel_id``; every non-key column a string."""
    kml_dir = Path(kml_dir)
    for key in REQUIRED:
        path = kml_path(kml_dir, key)
        if not path.is_file():
            raise FileNotFoundError(
                f"ACCC coverage KML not found: {path}. Fetch it with: {FETCH_COMMAND}"
            )

    results: dict[str, tuple[dict[int, int], dict[int, float]] | None] = {}
    for key in JOBS:
        path = kml_path(kml_dir, key)
        if not path.is_file():
            results[key] = None
            continue
        results[key] = point_results(nt_polygons(path, cache_dir), communities)

    def flag(key: str, bushtel_id: int) -> int:
        result = results[key]
        return -1 if result is None else result[0][bushtel_id]

    def distance(key: str, bushtel_id: int) -> float:
        result = results[key]
        if result is None:
            return -1.0
        if result[0][bushtel_id] == 1:
            return 0.0
        return round(result[1][bushtel_id], 3)

    rows = []
    for bushtel_id in sorted(int(b) for b in communities["bushtel_id"]):
        row: dict[str, object] = {"bushtel_id": bushtel_id}
        for key in JOBS:
            row[f"{key}_2025"] = str(flag(key, bushtel_id))
        t4, o4, tp4, m4 = (flag(key, bushtel_id) for key in JOBS[:4])
        # MOCN is TPG's network on Optus sites, not a fourth carrier.
        row["carriers_4g_count"] = str(max(t4, 0) + max(o4, 0) + max(max(tp4, 0), max(m4, 0)))
        for key in DISTANCE_JOBS:
            row[f"dist_km_{key}"] = str(distance(key, bushtel_id))
        rows.append(row)
    return pd.DataFrame(rows, columns=COLUMNS)
