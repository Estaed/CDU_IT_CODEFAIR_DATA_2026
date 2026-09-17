"""National Audit source: government drive-test non-alignment tiles near each community.

Reads the frozen non-alignment CSV written by ``pipeline.fetch.audit`` and emits the
*measured* publisher line, keyed on ``bushtel_id``. A non-alignment tile is a ~1 km square
where the Audit's drive testing found no coverage while the carrier's map claims there is
some: every one of the 237 NT rows carries ``Audit Data = "No audit roads coverage"`` against
``MNO Predicted Coverage = "With MNO claimed coverage"``
(``reports/2026-09-12-arena-measured.md`` S3.1.5-3.1.7).

``audit5`` is deliberately three-valued and this module writes only two of the three:

* ``"1"``  at least one non-alignment tile within 5 km of the community point;
* ``"0"``  an audited road passed within 5 km and carried no non-alignment -- **never written
  here**, because this CSV lists non-alignments only and cannot say where the Audit drove and
  found nothing wrong. Task-39 samples the audited roads and fills it without a schema change;
* ``""``   nothing known within 5 km.

Distances are metres in GDA2020 MGA (zone 52 west of 132 deg E, zone 53 east of it), the two
zones that cover the NT.

Source: https://www.infrastructure.gov.au/sites/default/files/documents/
national_audit_of_mobile_coverage_non-alignment_data_may_2026.csv, published 27 May 2026.
Licence unstated on the page (PRD Open Question 2); the attribution line is in
``pipeline.provenance``.
"""

from __future__ import annotations

import csv
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point

FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.audit"

COLUMNS = ["bushtel_id", "audit5", "audit_nearest_km", "audit_carriers", "audit_year"]
TABLE_COLUMNS = ["bushtel_id", "name", "audit_carriers", "audit_nearest_km", "audit_year"]

STATE = "NT"
NEAR_M = 5_000.0  # the licensed-site radius the rest of the pipeline uses
FAR_M = 40_000.0  # beyond this the nearest tile says nothing and the cell stays empty

EPSG_WGS84 = 4326
# GDA2020 MGA zone 52 (126-132 deg E) and zone 53 (132-138 deg E) cover the NT between them.
MGA_ZONE_EPSG = {52: 7852, 53: 7853}
ZONE_SPLIT_LON = 132.0


def _require(path: Path) -> Path:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"National Audit non-alignment CSV not found: {path}. "
            f"Re-fetch it with: {FETCH_COMMAND}"
        )
    return path


def tiles(csv_path: Path) -> gpd.GeoDataFrame:
    """The NT non-alignment tiles as polygons in WGS84, one row per published tile.

    The published file repeats its header as the first data row (a parsing trap noted in
    ``reports/2026-09-12-arena-measured.md`` S3.1.5); the ``State`` filter drops it.
    """
    csv_path = _require(csv_path)
    records = []
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("State") != STATE:
                continue
            records.append(
                {
                    "tile_id": row.get("Tile Id", ""),
                    "carrier": row.get("MNO", ""),
                    "year": row.get("Year", ""),
                    "geometry": wkt.loads(row["WKT"]),
                }
            )
    return gpd.GeoDataFrame(records, geometry="geometry", crs=f"EPSG:{EPSG_WGS84}")


def _zone(lon: float) -> int:
    return 52 if lon < ZONE_SPLIT_LON else 53


def _row(community: dict, distances_m: pd.Series, tile_frame: gpd.GeoDataFrame) -> dict:
    row = {"bushtel_id": int(community["bushtel_id"])}
    near = tile_frame[distances_m <= NEAR_M]
    nearest_m = float(distances_m.min()) if len(distances_m) else float("inf")

    row["audit5"] = "1" if len(near) else ""
    row["audit_carriers"] = "/".join(sorted(set(near["carrier"]))) if len(near) else ""
    if nearest_m <= FAR_M:
        nearest = tile_frame.iloc[int(distances_m.argmin())]
        row["audit_nearest_km"] = f"{round(nearest_m / 1000.0, 1)}"
        row["audit_year"] = str(nearest["year"])
    else:
        row["audit_nearest_km"] = ""
        row["audit_year"] = ""
    return row


def load(csv_path: Path, communities: pd.DataFrame) -> pd.DataFrame:
    """One row per community in ``communities``, sorted by ``bushtel_id``.

    ``communities`` is the frame from ``pipeline.sources.bushtel.load``, passed in by the
    caller (layer rule 2: modules in ``pipeline/sources`` never import each other); only its
    ``bushtel_id``, ``lat``, ``lon`` columns are read.
    """
    tile_frame = tiles(csv_path)
    comm = communities[["bushtel_id", "lat", "lon"]].to_dict("records")
    points = gpd.GeoSeries(
        [Point(float(c["lon"]), float(c["lat"])) for c in comm], crs=f"EPSG:{EPSG_WGS84}"
    )

    by_zone = {zone: tile_frame.to_crs(epsg=epsg) for zone, epsg in MGA_ZONE_EPSG.items()}
    points_by_zone = {zone: points.to_crs(epsg=epsg) for zone, epsg in MGA_ZONE_EPSG.items()}

    rows = []
    for index, community in enumerate(comm):
        zone = _zone(float(community["lon"]))
        distances = by_zone[zone].geometry.distance(points_by_zone[zone].iloc[index])
        rows.append(_row(community, distances, tile_frame))
    rows.sort(key=lambda r: r["bushtel_id"])
    return pd.DataFrame(rows, columns=COLUMNS)


def write_table(frame: pd.DataFrame, communities: pd.DataFrame, path: Path) -> Path:
    """Write the report table: one row per community with a non-alignment tile within 5 km."""
    names = {int(c["bushtel_id"]): c["name"] for c in communities.to_dict("records")}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(TABLE_COLUMNS)
        for record in frame.to_dict("records"):
            if record["audit5"] != "1":
                continue
            writer.writerow(
                [
                    record["bushtel_id"],
                    names.get(int(record["bushtel_id"]), ""),
                    record["audit_carriers"],
                    record["audit_nearest_km"],
                    record["audit_year"],
                ]
            )
    return path
