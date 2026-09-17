"""Mobile Black Spot Program source: funded base stations near each of the 96 communities.

Reads the frozen bulk extract written by ``pipeline.fetch.mbsp`` and emits two columns keyed
on ``bushtel_id``: ``mbsp_within_5km`` (how many funded sites lie within 5 km) and
``mbsp_nearest_km``. It is not a publisher line and it makes no coverage claim: a funded site
says money has already been committed here, which is why the priority score counts it
*against* a community rather than for it (Task-40, ``pipeline/priority_weights.csv``).

**The duplication trap.** ``reports/2026-09-12-arena-failure.md`` section 1.4 records that every
NT location appears exactly twice per round file, so a naive loader double-counts. The cause
is visible in the KML: each site is published as two ``Placemark`` elements carrying identical
attributes, one with a ``Point`` and one with a coverage ``Polygon``. Reading ``Point``
placemarks only de-duplicates exactly, and reproduces the arena report's 49 unique NT sites
across the eight rounds.

Sites are kept across the whole NT-plus-margin bounding box rather than on ``State == "NT"``,
so a funded site just over a border still counts for a community beside it. The margin also
keeps every kept site inside the two MGA zones the projection uses.

Distances are metres in GDA2020 MGA (zone 52 west of 132 deg E, zone 53 east of it), the same
two zones ``pipeline.sources.audit`` measures in.

Source: https://data.gov.au/data/dataset/mobile-black-spot-program-mbsp, resource
``MBSP - All Funded Base Stations.zip``, licence CC BY 4.0. The attribution line is in
``pipeline.provenance``.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
from lxml import etree
from shapely.geometry import Point

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.mbsp"

COLUMNS = ["bushtel_id", "mbsp_within_5km", "mbsp_nearest_km"]
SITE_COLUMNS = ["mbsp_id", "location", "round", "lat", "lon"]

KML_NS = "{http://www.opengis.net/kml/2.2}"
PLACEMARK_TAG = KML_NS + "Placemark"
POINT_COORDINATES = f".//{KML_NS}Point/{KML_NS}coordinates"

NEAR_M = 5_000.0  # the same radius the ACMA licensed-site and Audit columns use
FAR_M = 400_000.0  # beyond this the nearest site says nothing and the cell stays empty

# The NT with a margin wide enough for a cross-border site to count, and narrow enough that
# every kept site stays inside MGA zones 52 and 53.
BOUNDS = (124.0, -27.5, 141.0, -9.5)  # min lon, min lat, max lon, max lat

EPSG_WGS84 = 4326
MGA_ZONE_EPSG = {52: 7852, 53: 7853}
ZONE_SPLIT_LON = 132.0


def _require(path: Path) -> Path:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"MBSP funded base stations zip not found: {path}. Re-fetch it with: {FETCH_COMMAND}"
        )
    return path


def _round_name(member: str) -> str:
    """``MBSP - Round 5A Funded Base Stations.kml`` -> ``Round 5A``."""
    stem = Path(member).stem
    return stem.split(" - ", 1)[-1].replace(" Funded Base Stations", "")


def sites(mbsp_zip: Path) -> pd.DataFrame:
    """One row per funded base station inside ``BOUNDS``, de-duplicated across the rounds."""
    mbsp_zip = _require(mbsp_zip)
    min_lon, min_lat, max_lon, max_lat = BOUNDS
    rows: dict[str, dict] = {}
    with zipfile.ZipFile(mbsp_zip) as archive:
        for member in sorted(archive.namelist()):
            if not member.lower().endswith(".kml"):
                continue
            with archive.open(member) as handle:
                root = etree.parse(handle).getroot()
            for placemark in root.iter(PLACEMARK_TAG):
                element = placemark.find(POINT_COORDINATES)
                if element is None:
                    continue  # the coverage-polygon twin of a site already read here
                parts = (element.text or "").strip().split(",")
                if len(parts) < 2:
                    continue
                lon, lat = float(parts[0]), float(parts[1])
                if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    continue
                fields = {
                    data.get("name"): (data.text or "")
                    for data in placemark.iter(KML_NS + "SimpleData")
                }
                mbsp_id = fields.get("MBSP_ID", "") or f"{member}:{lon},{lat}"
                rows[mbsp_id] = {
                    "mbsp_id": mbsp_id,
                    "location": fields.get("Location", ""),
                    "round": _round_name(member),
                    "lat": lat,
                    "lon": lon,
                }
    ordered = sorted(rows.values(), key=lambda site: site["mbsp_id"])
    return pd.DataFrame(ordered, columns=SITE_COLUMNS)


def _row(bushtel_id: int, distances_m) -> dict:
    if not len(distances_m):
        return {"bushtel_id": bushtel_id, "mbsp_within_5km": "0", "mbsp_nearest_km": ""}
    nearest_m = float(distances_m.min())
    return {
        "bushtel_id": bushtel_id,
        "mbsp_within_5km": str(int((distances_m <= NEAR_M).sum())),
        "mbsp_nearest_km": f"{round(nearest_m / 1000.0, 1)}" if nearest_m <= FAR_M else "",
    }


def load(mbsp_zip: Path, communities: pd.DataFrame) -> pd.DataFrame:
    """One row per community in ``communities``, sorted by ``bushtel_id``.

    ``communities`` is the frame from ``pipeline.sources.bushtel.load``, passed in by the
    caller (layer rule 2: modules in ``pipeline/sources`` never import each other); only its
    ``bushtel_id``, ``lat``, ``lon`` columns are read.
    """
    site_frame = sites(mbsp_zip)
    site_points = gpd.GeoSeries(
        [Point(site["lon"], site["lat"]) for site in site_frame.to_dict("records")],
        crs=f"EPSG:{EPSG_WGS84}",
    )
    comm = communities[["bushtel_id", "lat", "lon"]].to_dict("records")
    community_points = gpd.GeoSeries(
        [Point(float(c["lon"]), float(c["lat"])) for c in comm], crs=f"EPSG:{EPSG_WGS84}"
    )

    sites_by_zone = {zone: site_points.to_crs(epsg=epsg) for zone, epsg in MGA_ZONE_EPSG.items()}
    comm_by_zone = {
        zone: community_points.to_crs(epsg=epsg) for zone, epsg in MGA_ZONE_EPSG.items()
    }

    rows = []
    for index, community in enumerate(comm):
        zone = 52 if float(community["lon"]) < ZONE_SPLIT_LON else 53
        distances = sites_by_zone[zone].distance(comm_by_zone[zone].iloc[index])
        rows.append(_row(int(community["bushtel_id"]), distances))
    rows.sort(key=lambda r: r["bushtel_id"])
    return pd.DataFrame(rows, columns=COLUMNS)
