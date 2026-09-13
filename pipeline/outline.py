"""The NT outline as one SVG path string, projected into the mirror's 300x480 view box.

Reads the ABS ASGS Edition 3 (2021) State and Territory boundary
(``data/raw/abs_ste_2021_shp.zip``, fetched by ``pipeline.fetch.abs_boundary``), keeps the
three largest polygons of the Northern Territory's multipolygon (mainland, Tiwi, Groote — the
same three the map screen's reference build draws), simplifies each with
``shapely.simplify(preserve_topology=True)`` and projects every vertex with the mirror's own
projection constants (``K = 30, X0 = 128.5, Y0 = -10.5``).

``TOLERANCE_DEG = 0.0199`` is the largest tolerance (measured in steps of 0.0001, starting at
0.02) that keeps the three-polygon path under the 8,000 byte budget: measured 7,977 bytes on
2026-09-13 against ``data/raw/abs_ste_2021_shp.zip``.

pyogrio and shapely are the only geo imports here; nothing outside this module's own reach
is imported (CLAUDE.md Part 2, layer rule 6).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

# The raw file pipeline.fetch.abs_boundary writes, and the command that re-fetches it; named
# here (as the source modules name theirs) so the pack build never imports a fetch module.
RAW_NAME = "abs_ste_2021_shp.zip"
FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_boundary"

K = 30
X0 = 128.5
Y0 = -10.5

TOLERANCE_DEG = 0.0199

STATE_COLUMN = "STE_NAME21"
STATE_NAME = "Northern Territory"
KEPT_POLYGONS = 3


def project(lat: float, lon: float) -> tuple[float, float]:
    """The mirror's projection: (lat, lon) into the 300x480 view box, one decimal."""
    x = round((lon - X0) * K, 1)
    y = round((Y0 - lat) * K, 1)
    return x + 0.0, y + 0.0  # normalise -0.0 to 0.0


def _ring_path(coords: list[tuple[float, float]]) -> str:
    """One closed sub-path, ``M x y L x y ... Z``, from a polygon's exterior ring."""
    tokens: list[str] = []
    for index, (lon, lat) in enumerate(coords):
        x, y = project(lat, lon)
        tokens.append("M" if index == 0 else "L")
        tokens.append(f"{x}")
        tokens.append(f"{y}")
    tokens.append("Z")
    return " ".join(tokens)


def _read_path(path: str | Path):
    """A GDAL/pyogrio-readable path: zipped shapefiles need the ``zip://`` VSI prefix."""
    text = str(path)
    if text.endswith(".zip") and not text.startswith("zip://"):
        text = f"zip://{text}"
    return text


def outline_path(path: str | Path, tolerance_deg: float = TOLERANCE_DEG) -> str:
    """The NT outline (mainland, Tiwi, Groote) as one ``M...Z M...Z M...Z`` path string."""
    frame = gpd.read_file(_read_path(path))
    matches = frame[frame[STATE_COLUMN] == STATE_NAME]
    if matches.empty:
        raise ValueError(f"no {STATE_NAME} feature in {path}")
    geometry = matches.geometry.iloc[0]
    polygons = sorted(geometry.geoms, key=lambda polygon: polygon.area, reverse=True)
    kept = polygons[:KEPT_POLYGONS]
    return " ".join(
        _ring_path(list(polygon.simplify(tolerance_deg, preserve_topology=True).exterior.coords))
        for polygon in kept
    )


if __name__ == "__main__":
    raw = Path(__file__).resolve().parent.parent / "data" / "raw" / RAW_NAME
    result = outline_path(raw)
    print(f"{len(result.encode('utf-8'))} bytes")
