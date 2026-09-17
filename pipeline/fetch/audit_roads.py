"""Re-fetch the National Audit's audited road centrelines for the Northern Territory.

The negatives the reliability model needs: the Audit published the tiles where it found no
signal inside claimed coverage (``pipeline.fetch.audit``) but not the roads it drove, so a
road sample with no non-alignment on it is the only "the map was right here" the dataset can
give. Run by hand, never by a test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.audit_roads

Writes ``data/raw/audit_roads_<today>.geojson``: one feature per audited road segment inside
the NT envelope, in WGS84, carrying the year it was audited in. A snapshot already on disk is
left alone.

Source: the ArcGIS MapServer at
https://spatial.infrastructure.gov.au/server/rest/services/Main_Audit_Roads_DITRDCA_2024/MapServer
(verified 2026-09-17: answers without a token, while the ``/Hosted/`` path of the same service
wants one, and no open ``FeatureServer`` exists). Layers ``0`` Year_1_Roads, ``1``
Year_2_Roads, ``2`` Year_3_Roads; 2,518 / 4,191 / 4,191 features inside the NT envelope
``129,-26,138,-10.9``, which is the completeness check at the end of the run.

**The ``query`` endpoint returns attributes but never geometry** on this service (checked
2026-09-17 in every combination: ``f=json``, ``f=geojson``, ``f=pbf``, with and without
``outSR``, by ``objectIds``, with and without paging; the responses carry no
``geometryType`` at all, and every feature's ``geometry`` is ``null``). ``identify`` on the
same layers does return the paths, so that is what this module uses: an envelope per tile,
all three layers per call, deduplicated on ``(layer, OBJECTID)``. ``identify`` caps a
response at the layer's ``maxRecordCount`` of 2,000 and says nothing when it truncates, so a
tile that comes back full is split into four and re-asked until it does not. Geometry comes
back generalised to ``maxAllowableOffset`` (0.001 degrees, about 100 m), which is well inside
the 1 km sampling step ``pipeline.reliability`` places on these lines.

Licence unstated on the page, like the non-alignment CSV (PRD Open Question 2); the
attribution line is in ``pipeline.provenance``.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
SERVICE = (
    "https://spatial.infrastructure.gov.au/server/rest/services/"
    "Main_Audit_Roads_DITRDCA_2024/MapServer"
)
# Layer id -> the year label kept on every feature it yields, and the count the service
# reports inside the NT envelope (returnCountOnly, 2026-09-17): the completeness check.
LAYERS = {0: ("Year 1", 2_518), 1: ("Year 2", 4_191), 2: ("Year 3", 4_191)}
# lon_min, lat_min, lon_max, lat_max.
NT_ENVELOPE = (129.0, -26.0, 138.0, -10.9)
TILE_DEGREES = 1.0
MAX_RECORDS = 2_000  # the layers' maxRecordCount; a full response means the tile truncated
MAX_DEPTH = 6  # 1 degree / 2**6 is about 1.7 km: far below any real road density
OFFSET_DEGREES = 0.001  # geometry generalisation, about 100 m
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 300
PATTERN = "audit_roads_*.geojson"


def _identify(box: tuple[float, float, float, float]) -> list[dict]:
    """Every audited road segment ``identify`` reports inside one envelope."""
    xmin, ymin, xmax, ymax = box
    envelope = {
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
        "spatialReference": {"wkid": 4326},
    }
    params = {
        "geometry": json.dumps(envelope),
        "geometryType": "esriGeometryEnvelope",
        "sr": "4326",
        "layers": "all:" + ",".join(str(layer) for layer in LAYERS),
        "tolerance": "0",
        "mapExtent": f"{xmin},{ymin},{xmax},{ymax}",
        "imageDisplay": "4000,4000,96",
        "returnGeometry": "true",
        "maxAllowableOffset": str(OFFSET_DEGREES),
        "f": "json",
    }
    response = requests.get(
        f"{SERVICE}/identify", params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"identify {box}: {payload['error']}")
    return payload.get("results", [])


def _collect(box: tuple[float, float, float, float], found: dict, depth: int = 0) -> None:
    """Fill ``found`` from one envelope, splitting it in four while the answer comes back full."""
    results = _identify(box)
    if len(results) >= MAX_RECORDS and depth < MAX_DEPTH:
        xmin, ymin, xmax, ymax = box
        xmid, ymid = (xmin + xmax) / 2, (ymin + ymax) / 2
        for quarter in (
            (xmin, ymin, xmid, ymid),
            (xmid, ymin, xmax, ymid),
            (xmin, ymid, xmid, ymax),
            (xmid, ymid, xmax, ymax),
        ):
            _collect(quarter, found, depth + 1)
        return
    for result in results:
        layer = int(result["layerId"])
        attributes = result.get("attributes") or {}
        object_id = attributes.get("OBJECTID")
        paths = (result.get("geometry") or {}).get("paths")
        if object_id is None or not paths:
            continue
        found[(layer, str(object_id))] = {
            "type": "Feature",
            "properties": {
                "layer": layer,
                "year": LAYERS[layer][0],
                "OBJECTID": object_id,
                "name": attributes.get("name", ""),
                "Major_Urban": attributes.get("Major_Urban", ""),
            },
            "geometry": {"type": "MultiLineString", "coordinates": paths},
        }


def tiles() -> list[tuple[float, float, float, float]]:
    """The NT envelope cut into whole-degree tiles, west to east and south to north."""
    xmin, ymin, xmax, ymax = NT_ENVELOPE
    boxes = []
    x = xmin
    while x < xmax:
        y = ymin
        while y < ymax:
            boxes.append((x, y, min(x + TILE_DEGREES, xmax), min(y + TILE_DEGREES, ymax)))
            y += TILE_DEGREES
        x += TILE_DEGREES
    return boxes


def download() -> Path:
    existing = sorted(RAW.glob(PATTERN))
    if existing:
        dest = existing[-1]
        print(f"already downloaded: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest

    found: dict[tuple[int, str], dict] = {}
    boxes = tiles()
    for index, box in enumerate(boxes, 1):
        _collect(box, found)
        print(f"  tile {index}/{len(boxes)} {box}: {len(found)} segments so far")

    for layer, (year, expected) in LAYERS.items():
        got = sum(1 for key in found if key[0] == layer)
        print(f"layer {layer} ({year}): {got} of {expected} segments")
        if got < expected:
            print(
                f"  WARNING: {expected - got} segments short; the service capped a tile that "
                "was not split far enough (raise MAX_DEPTH) or dropped a geometry"
            )

    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / f"audit_roads_{date.today().isoformat()}.geojson"
    features = [found[key] for key in sorted(found)]
    with dest.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump({"type": "FeatureCollection", "features": features}, handle)
    print(f"wrote {dest} ({dest.stat().st_size:,} bytes, {len(features)} segments)")
    return dest


def main() -> None:
    download()


if __name__ == "__main__":
    main()
