"""Map-claim reliability: how much to trust a carrier's claim where nobody drove.

Four publishers claim coverage and one measured it: the National Audit drove NT roads and
published the tiles where it found no signal inside a carrier's claimed coverage
(``pipeline.sources.audit``). This module turns those tiles into labels, samples the audited
roads for the places the Audit drove and found nothing wrong, fits one small model on the
features the pack already has per community, and applies it at the 96 community points.

The one module in the repository that imports scikit-learn (CLAUDE.md layer rule 9). It runs
once in the pipeline, after the capability table is written and before the pack is built, and
ships **numbers**: the product itself contains no model (PRD section 3).

**The kill criterion was fixed on 2026-09-17, before the first fit** (Task-39 contract item
5): pooled held-out AUC below ``AUC_FLOOR`` and the model does not ship -- every community
gets the word ``none`` and a null probability, the validation table is still written, and the
pipeline completes. No feature and no cut point is tuned after seeing a held-out result.

**What a word means, and what it does not.** The model is trained on road samples and applied
to community points: a community's word is an extrapolation from the nearest audited
conditions, not a measurement at the community. That sentence ships once, on the pack's
``sources`` entry for this model, which every community's ``claim_reliability`` points at.

Validation is a five-fold split **by ABS SA3 region** (``data/raw/abs_sa3_2021_shp.zip``), so
no region is on both sides of a fold: a road sample 2 km from its training neighbour would
otherwise make an untrained model look accurate.

Distances are metres in GDA94 Australian Albers (EPSG:3577), one equal-area projection across
the whole NT; ``pipeline.sources.audit`` cross-checked it against the MGA zones on 2026-09-17
and they agreed within 10 m.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.strtree import STRtree
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from pipeline.sources import accc, audit, rrl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
OUT = ROOT / "data/out"
CACHE = OUT / "cache"
TABLE_CSV = OUT / "capability_table.csv"
TABLE_XLSX = OUT / "capability_table.xlsx"
RELIABILITY_CSV = OUT / "reliability.csv"
VALIDATION_CSV = OUT / "tables/reliability_validation.csv"
COEFFICIENTS_CSV = OUT / "tables/reliability_coefficients.csv"

ROADS_PATTERN = "audit_roads_*.geojson"
ROADS_FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.audit_roads"
SA3_PATTERN = "abs_sa3_20*"
SA3_FETCH_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_sa3"
SA3_STATE_COLUMN = "STE_NAME21"
SA3_NAME_COLUMN = "SA3_NAME21"
SA3_STATE = "Northern Territory"

METRIC_EPSG = 3577
WGS84_EPSG = 4326
SPACING_M = 1_000.0  # one sample per kilometre of audited road
THIN_M = 1_000.0  # two samples of the same label closer than this are one sample
FOLDS = 5
RANDOM_STATE = 0
MAX_ITER = 1_000

# Fixed 2026-09-17 before the first fit; not tuned afterwards (contract item 5).
AUC_FLOOR = 0.65
# Fixed with it: the words a probability of a wrong claim maps to (contract item 6).
CUT_MEDIUM = 0.25
CUT_LOW = 0.50

FEATURE_NAMES = ("site_km", "depth_km", "sites_10km", "sites_20km", "carriers_claiming")
# relief_m is in the contract only if data/raw/ holds a coarse DEM when the task starts. It
# does not (checked 2026-09-17), so the feature is absent; adding it later is a new name here
# and a new key in the dict features() reads.

# The three MNOs the Audit names, with the ACCC 2025 polygon keys that count as that
# carrier's claim and the rrl.sites carrier group that counts as its licensed site. MOCN is
# TPG's network on Optus sites, not a fourth carrier (pipeline.sources.accc).
CARRIERS = {
    "Telstra": {"claims": ("telstra_4g",), "sites": "telstra"},
    "Optus": {"claims": ("optus_4g",), "sites": "optus"},
    "TPG": {"claims": ("tpg_4g", "mocn_4g"), "sites": "tpg"},
}

WORDS = ("high", "medium", "low", "none")
RELIABILITY_COLUMNS = ("id", "name", "word", "p_wrong", "carrier", "driver1", "driver2")
VALIDATION_COLUMNS = (
    "fold",
    "regions",
    "samples",
    "positives",
    "base_rate",
    "auc",
    "precision_at_0.5",
    "recall_at_0.5",
)
COEFFICIENT_COLUMNS = ("feature", "coefficient", "mean", "scale")


def features(row: dict) -> dict:
    """The model's features for one point and one claiming carrier.

    ``row`` is a plain dict so the same code runs on a road sample and on a community row:
    ``carrier_site_km`` (the nearest licensed site of the claiming carrier, km),
    ``boundary_km`` and ``inside`` (how far the point is from the claiming polygon's
    boundary, and which side of it), ``site_distances_km`` (every licensed site's distance,
    any carrier) and ``carriers_claiming``.
    """
    distances = row["site_distances_km"]
    boundary = float(row["boundary_km"])
    return {
        "site_km": round(float(row["carrier_site_km"]), 3),
        "depth_km": round(boundary if row["inside"] else -boundary, 3),
        "sites_10km": sum(1 for d in distances if d <= 10.0),
        "sites_20km": sum(1 for d in distances if d <= 20.0),
        "carriers_claiming": int(row["carriers_claiming"]),
    }


def word_for(p_wrong: float | None) -> str:
    """The reliability word for a probability, by the cut points fixed in the contract."""
    if p_wrong is None:
        return "none"
    if p_wrong < CUT_MEDIUM:
        return "high"
    if p_wrong < CUT_LOW:
        return "medium"
    return "low"


def newest(pattern: str, fetch_command: str) -> Path:
    found = sorted(RAW.glob(pattern))
    if not found:
        raise FileNotFoundError(
            f"no file matches {pattern} under {RAW}. Re-fetch it with: {fetch_command}"
        )
    return found[-1]


def project(points: np.ndarray) -> np.ndarray:
    """WGS84 points to the metric CRS every distance in this module is measured in."""
    return np.array(
        gpd.GeoSeries(points, crs=f"EPSG:{WGS84_EPSG}").to_crs(epsg=METRIC_EPSG).values,
        dtype=object,
    )


def road_points(roads_path: Path, spacing_m: float = SPACING_M) -> np.ndarray:
    """One point per ``spacing_m`` along every audited road segment, in EPSG:3577.

    The three yearly layers overlap (a road driven in two years is published twice), so
    coincident samples are collapsed to one before anything is computed on them.
    """
    roads = gpd.read_file(roads_path).to_crs(epsg=METRIC_EPSG)
    coordinates: list[tuple[float, float]] = []
    for geometry in roads.geometry:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiLineString" else [geometry]
        for line in parts:
            for step in range(int(line.length // spacing_m) + 1):
                point = line.interpolate(step * spacing_m)
                coordinates.append((point.x, point.y))
    unique = np.unique(np.round(np.array(coordinates), 0), axis=0)
    return shapely.points(unique[:, 0], unique[:, 1])


class Geography:
    """Every spatial index the model needs, built once and held in metres (EPSG:3577).

    One object answers the same questions for a road sample and for a community point, which
    is what keeps the training set and the application honest: the features cannot drift
    apart because there is only one code path.
    """

    def __init__(self, raw_dir: Path, cache_dir: Path, sites_frame: pd.DataFrame):
        self.claims: dict[str, tuple[np.ndarray, STRtree]] = {}
        for carrier, spec in CARRIERS.items():
            polygons: list = []
            for key in spec["claims"]:
                polygons.extend(accc.nt_polygons(accc.kml_path(raw_dir, key), cache_dir))
            projected = project(np.array(polygons, dtype=object))
            shapely.prepare(projected)
            self.claims[carrier] = (projected, STRtree(projected))

        tile_frame = audit.tiles(newest("audit_non_alignment_*.csv", audit.FETCH_COMMAND))
        tiles_projected = tile_frame.to_crs(epsg=METRIC_EPSG)
        self.tiles: dict[str, STRtree] = {}
        for carrier in CARRIERS:
            geometries = np.array(
                tiles_projected[tiles_projected["carrier"] == carrier].geometry.values,
                dtype=object,
            )
            self.tiles[carrier] = STRtree(geometries) if len(geometries) else None

        sites = project(
            shapely.points(sites_frame["lon"].to_numpy(), sites_frame["lat"].to_numpy())
        )
        site_xy = np.column_stack([shapely.get_x(sites), shapely.get_y(sites)])
        groups = sites_frame["carrier_group"].to_numpy()
        self.carrier_xy = {
            carrier: site_xy[groups == spec["sites"]] for carrier, spec in CARRIERS.items()
        }
        # A site carrying two carriers' devices is one mast: the 10 and 20 km counts are of
        # distinct masts, while the per-carrier distance is of that carrier's own.
        _, first = np.unique(sites_frame["site_id"].to_numpy(), return_index=True)
        self.mast_xy = site_xy[np.sort(first)]

    def _depth_km(self, carrier: str, point, polygon_indices: list[int]) -> float:
        """How far inside its claiming polygon the point sits, in km.

        A point covered by two of a carrier's polygons (TPG's own and the MOCN footprint)
        takes the deeper of the two: the carrier claims it twice over.
        """
        polygons, _tree = self.claims[carrier]
        depths = [
            shapely.distance(point, shapely.boundary(polygons[index]))
            for index in polygon_indices
        ]
        return max(depths) / 1000.0

    def rows(self, points: np.ndarray) -> list[dict]:
        """One raw row per (point, claiming carrier), ready for ``features``.

        A point no carrier claims yields no row at all: there is no claim to score.
        """
        claimed: dict[str, dict[int, list[int]]] = {}
        for carrier, (_polygons, tree) in self.claims.items():
            hits: dict[int, list[int]] = {}
            pairs = tree.query(points, predicate="covered_by")
            for point_index, polygon_index in zip(pairs[0], pairs[1], strict=True):
                hits.setdefault(int(point_index), []).append(int(polygon_index))
            claimed[carrier] = hits

        counts = np.zeros(len(points), dtype=int)
        for hits in claimed.values():
            for point_index in hits:
                counts[point_index] += 1

        xs = shapely.get_x(points)
        ys = shapely.get_y(points)
        rows: list[dict] = []
        for carrier, hits in claimed.items():
            own = self.carrier_xy[carrier]
            for point_index, polygon_indices in sorted(hits.items()):
                x, y = xs[point_index], ys[point_index]
                masts_km = np.hypot(self.mast_xy[:, 0] - x, self.mast_xy[:, 1] - y) / 1000.0
                own_km = np.hypot(own[:, 0] - x, own[:, 1] - y) / 1000.0
                rows.append(
                    {
                        "point_index": point_index,
                        "x": float(x),
                        "y": float(y),
                        "carrier": carrier,
                        "carrier_site_km": float(own_km.min()) if len(own_km) else float("inf"),
                        "boundary_km": self._depth_km(
                            carrier, points[point_index], polygon_indices
                        ),
                        "inside": True,
                        "site_distances_km": masts_km,
                        "carriers_claiming": int(counts[point_index]),
                    }
                )
        return rows

    def non_alignment(self, carrier: str, points: np.ndarray) -> set[int]:
        """The indices of ``points`` that fall inside a non-alignment tile of ``carrier``."""
        tree = self.tiles.get(carrier)
        if tree is None:
            return set()
        pairs = tree.query(points, predicate="covered_by")
        return {int(index) for index in pairs[0]}


def thin(points: np.ndarray, labels: np.ndarray, radius_m: float = THIN_M) -> np.ndarray:
    """Indices kept when two samples of the same label closer than ``radius_m`` become one.

    A grid of ``radius_m`` cells: a candidate is kept unless a kept sample of its own label
    already sits within the radius in its own or a neighbouring cell. Deterministic, because
    the candidates are walked in index order.
    """
    xs, ys = shapely.get_x(points), shapely.get_y(points)
    kept: list[int] = []
    grid: dict[tuple[int, int, int], list[int]] = {}
    for index in range(len(points)):
        label = int(labels[index])
        cell_x, cell_y = int(xs[index] // radius_m), int(ys[index] // radius_m)
        close = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for other in grid.get((label, cell_x + dx, cell_y + dy), ()):
                    if np.hypot(xs[index] - xs[other], ys[index] - ys[other]) < radius_m:
                        close = True
                        break
                if close:
                    break
            if close:
                break
        if close:
            continue
        kept.append(index)
        grid.setdefault((label, cell_x, cell_y), []).append(index)
    return np.array(kept, dtype=int)


def regions_for(points: np.ndarray, sa3_zip: Path) -> np.ndarray:
    """The ABS SA3 2021 region name each point falls in, ``""`` outside every NT region."""
    path = str(sa3_zip)
    frame = gpd.read_file(f"zip://{path}" if path.endswith(".zip") else path)
    nt = frame[frame[SA3_STATE_COLUMN] == SA3_STATE]
    nt = nt[nt.geometry.notna() & ~nt.geometry.is_empty].to_crs(epsg=METRIC_EPSG)
    geometries = np.array(nt.geometry.values, dtype=object)
    names = nt[SA3_NAME_COLUMN].to_numpy()
    shapely.prepare(geometries)
    tree = STRtree(geometries)
    out = np.array([""] * len(points), dtype=object)
    pairs = tree.query(points, predicate="covered_by")
    for point_index, region_index in zip(pairs[0], pairs[1], strict=True):
        if out[int(point_index)] == "":
            out[int(point_index)] = names[int(region_index)]
    return out


def fold_of_region(regions: list[str], folds: int = FOLDS, seed: int = RANDOM_STATE) -> dict:
    """``{region: fold}``: the regions shuffled once with a recorded seed, then dealt round.

    Every sample of a region is on the same side of every split, so a fold's test set is
    ground the model has never seen.
    """
    ordered = sorted(set(regions))
    shuffled = list(np.random.default_rng(seed).permutation(np.array(ordered, dtype=object)))
    return {str(region): index % folds for index, region in enumerate(shuffled)}


def samples(raw_dir: Path = RAW, cache_dir: Path = CACHE) -> tuple[pd.DataFrame, Geography, list]:
    """The labelled training set: one row per (audited road point, claiming carrier).

    A point is a positive for a carrier when it lies inside one of that carrier's
    non-alignment tiles -- the government drove there and found no signal where the carrier's
    map claims some. Every other claimed point is a negative: the Audit drove past and
    published nothing against the claim.
    """
    points = road_points(newest(ROADS_PATTERN, ROADS_FETCH_COMMAND))
    sites_frame = rrl.sites(newest("spectra_rrl_*.zip", rrl.FETCH_COMMAND))
    geography = Geography(raw_dir, cache_dir, sites_frame)

    positives = {carrier: geography.non_alignment(carrier, points) for carrier in CARRIERS}
    point_label = np.zeros(len(points), dtype=int)
    for indices in positives.values():
        for index in indices:
            point_label[index] = 1

    kept = thin(points, point_label)
    keep = set(int(index) for index in kept)

    rows = []
    for row in geography.rows(points):
        if row["point_index"] not in keep:
            continue
        rows.append(
            {
                "x": row["x"],
                "y": row["y"],
                "carrier": row["carrier"],
                "label": 1 if row["point_index"] in positives[row["carrier"]] else 0,
                **features(row),
            }
        )

    frame = pd.DataFrame(rows)
    sample_points = shapely.points(frame["x"].to_numpy(), frame["y"].to_numpy())
    frame["region"] = regions_for(sample_points, newest(SA3_PATTERN, SA3_FETCH_COMMAND))
    frame = frame[frame["region"] != ""].reset_index(drop=True)
    return frame, geography, points


def _metrics(truth: np.ndarray, probability: np.ndarray) -> dict:
    """AUC and precision/recall at 0.5, each blank when the fold cannot define it."""
    predicted = (probability >= 0.5).astype(int)
    positives = int(truth.sum())
    auc = ""
    if 0 < positives < len(truth):
        auc = round(float(roc_auc_score(truth, probability)), 4)
    called = int(predicted.sum())
    precision = round(float(truth[predicted == 1].mean()), 4) if called else ""
    recall = round(float(predicted[truth == 1].mean()), 4) if positives else ""
    return {
        "samples": len(truth),
        "positives": positives,
        "base_rate": round(positives / len(truth), 5) if len(truth) else "",
        "auc": auc,
        "precision_at_0.5": precision,
        "recall_at_0.5": recall,
    }


def _model() -> LogisticRegression:
    return LogisticRegression(
        class_weight="balanced", random_state=RANDOM_STATE, max_iter=MAX_ITER
    )


def evaluate(frame: pd.DataFrame) -> tuple[list[dict], float]:
    """Five folds over SA3 regions: one row per fold, then the pooled out-of-fold row.

    The pooled AUC -- every sample scored by a model that never saw its region -- is the
    number the kill criterion reads.
    """
    assignment = fold_of_region(list(frame["region"]))
    fold = frame["region"].map(assignment).to_numpy()
    matrix = frame[list(FEATURE_NAMES)].to_numpy(dtype=float)
    truth = frame["label"].to_numpy(dtype=int)

    rows: list[dict] = []
    pooled = np.zeros(len(frame), dtype=float)
    for index in range(FOLDS):
        test = fold == index
        train = ~test
        scaler = StandardScaler().fit(matrix[train])
        model = _model().fit(scaler.transform(matrix[train]), truth[train])
        probability = model.predict_proba(scaler.transform(matrix[test]))[:, 1]
        pooled[test] = probability
        regions = sorted({region for region, f in assignment.items() if f == index})
        rows.append(
            {
                "fold": index + 1,
                "regions": ";".join(regions),
                **_metrics(truth[test], probability),
            }
        )

    pooled_row = {
        "fold": "pooled",
        "regions": f"{len(set(frame['region']))} SA3 regions, seed {RANDOM_STATE}",
        **_metrics(truth, pooled),
    }
    rows.append(pooled_row)
    return rows, float(pooled_row["auc"]) if pooled_row["auc"] != "" else 0.0


def fit(frame: pd.DataFrame) -> tuple[LogisticRegression, StandardScaler]:
    """The shipped model: one fit over every sample, after validation has spoken."""
    matrix = frame[list(FEATURE_NAMES)].to_numpy(dtype=float)
    scaler = StandardScaler().fit(matrix)
    return _model().fit(scaler.transform(matrix), frame["label"].to_numpy(dtype=int)), scaler


def community_rows(
    table: list[dict], geography: Geography, model, scaler
) -> list[dict]:
    """One reliability row per community: the worst claim any claiming carrier makes there.

    ``model`` is ``None`` on the kill path, and then every row is the ``none`` word with no
    probability, which is exactly what the pack ships.
    """
    points = project(
        shapely.points(
            [float(row["lon"]) for row in table], [float(row["lat"]) for row in table]
        )
    )
    by_point: dict[int, list[dict]] = {}
    for raw in geography.rows(points):
        by_point.setdefault(raw["point_index"], []).append(raw)

    rows = []
    for index, row in enumerate(table):
        claims = by_point.get(index, [])
        record = {
            "id": int(row["bushtel_id"]),
            "name": row["name"],
            "word": "none",
            "p_wrong": None,
            "carrier": "",
            "driver1": "",
            "driver2": "",
        }
        if claims and model is not None:
            matrix = np.array(
                [[features(raw)[name] for name in FEATURE_NAMES] for raw in claims], dtype=float
            )
            standardised = scaler.transform(matrix)
            probability = model.predict_proba(standardised)[:, 1]
            worst = int(np.argmax(probability))
            contribution = np.abs(model.coef_[0] * standardised[worst])
            drivers = [FEATURE_NAMES[i] for i in np.argsort(-contribution)[:2]]
            record.update(
                word=word_for(float(probability[worst])),
                p_wrong=round(float(probability[worst]), 4),
                carrier=claims[worst]["carrier"],
                driver1=drivers[0],
                driver2=drivers[1],
            )
        rows.append(record)
    return rows


def _write(path: Path, columns, rows) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow(["" if row[c] is None else row[c] for c in columns])
    return path


def write_reliability(rows: list[dict], path: Path = RELIABILITY_CSV) -> Path:
    return _write(path, RELIABILITY_COLUMNS, rows)


def write_validation(rows: list[dict], path: Path = VALIDATION_CSV) -> Path:
    return _write(path, VALIDATION_COLUMNS, rows)


def write_coefficients(model, scaler, path: Path = COEFFICIENTS_CSV) -> Path:
    """The standardised coefficients with their feature names, and the intercept."""
    rows = []
    if model is not None:
        for index, name in enumerate(FEATURE_NAMES):
            rows.append(
                {
                    "feature": name,
                    "coefficient": round(float(model.coef_[0][index]), 5),
                    "mean": round(float(scaler.mean_[index]), 4),
                    "scale": round(float(scaler.scale_[index]), 4),
                }
            )
        rows.append(
            {
                "feature": "intercept",
                "coefficient": round(float(model.intercept_[0]), 5),
                "mean": "",
                "scale": "",
            }
        )
    return _write(path, COEFFICIENT_COLUMNS, rows)


def fill_audit_zero(table: pd.DataFrame, audited: set[int]) -> int:
    """Write ``audit5 = "0"`` where a road was audited within 5 km and nothing was wrong.

    ``pipeline.sources.audit`` defines the value and never writes it: the non-alignment CSV
    lists non-alignments only, so only the road samples can say where the Audit drove past
    and published nothing. Returns how many cells changed.
    """
    changed = 0
    for index, row in table.iterrows():
        if row["audit5"] == "" and int(row["bushtel_id"]) in audited:
            table.loc[index, "audit5"] = "0"
            changed += 1
    return changed


def main() -> None:
    frame, geography, points = samples()
    positives = int(frame["label"].sum())
    print(
        f"reliability: {len(frame)} samples over {len(set(frame['region']))} SA3 regions, "
        f"{positives} positives ({positives / len(frame):.3%})"
    )

    validation, pooled_auc = evaluate(frame)
    write_validation(validation, VALIDATION_CSV)
    for row in validation:
        print(
            f"  fold {row['fold']}: n={row['samples']} pos={row['positives']} "
            f"auc={row['auc']} precision={row['precision_at_0.5']} recall={row['recall_at_0.5']}"
        )

    shipped = pooled_auc >= AUC_FLOOR
    print(
        f"  pooled held-out AUC {pooled_auc} against the floor {AUC_FLOOR}: "
        f"{'the model ships' if shipped else 'the kill path runs, every word is none'}"
    )

    model, scaler = fit(frame) if shipped else (None, None)
    write_coefficients(model, scaler, COEFFICIENTS_CSV)

    table = pd.read_csv(TABLE_CSV, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    rows = community_rows(table.to_dict("records"), geography, model, scaler)
    write_reliability(rows, RELIABILITY_CSV)
    counts = {word: sum(1 for row in rows if row["word"] == word) for word in WORDS}
    print(f"  words over the 96: {counts}")

    audited = audit.audited_within(table, points, METRIC_EPSG)
    changed = fill_audit_zero(table, audited)
    table.to_csv(TABLE_CSV, index=False, lineterminator="\n", encoding="utf-8")
    table.to_excel(TABLE_XLSX, index=False, engine="openpyxl")
    print(f"  audit5='0' written for {changed} communities with an audited road within 5 km")
    print(f"  {RELIABILITY_CSV.name}: {len(rows)} rows, fit {date.today().isoformat()}")


if __name__ == "__main__":
    main()
