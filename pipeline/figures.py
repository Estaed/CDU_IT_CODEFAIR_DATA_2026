"""Report-ready figures and tables for the Findings section (PRD section 4.1, item 3).

Reads ``data/out/capability_table.csv`` (already carries the merged verdicts and the
mobile disagreement pattern, both written by ``merge.py``) and writes two static NT maps
as PNG to ``data/out/figures/`` plus three CSV tables to ``data/out/tables/``. Colours and
glyphs are read from ``design/ds/design/tokens.json``, never retyped (CLAUDE.md Part 2,
layer rule 5). Run from the project root:
``PYTHONUTF8=1 .venv/Scripts/python -m pipeline.figures``.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

from pipeline import outline  # noqa: E402

plt.rcParams["font.family"] = "sans-serif"

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data/out/capability_table.csv"
TOKENS_PATH = ROOT / "design/ds/design/tokens.json"
BOUNDARY_RAW = ROOT / "data/raw" / outline.RAW_NAME
FIGURES_DIR = ROOT / "data/out/figures"
TABLES_DIR = ROOT / "data/out/tables"

PNG_WIDTH_PX = 2000
PNG_HEIGHT_PX = 3200
VIEW_W = 300
VIEW_H = 480
DPI = 200
FIGSIZE = (PNG_WIDTH_PX / DPI, PNG_HEIGHT_PX / DPI)

VERDICT_ORDER = ("works", "degraded", "fails", "nodata")
SERVICES = ("telehealth_video", "school_video_meeting", "mygov_text", "voice_sms")
SERVICE_LABELS = {
    "telehealth_video": "Telehealth video",
    "school_video_meeting": "School video meeting",
    "mygov_text": "myGov and banking",
    "voice_sms": "Voice and SMS",
}
POPULATION_SUPPRESS_BELOW = 100

SOURCE_LINE = "Sources: ACCC MIR 2025, NT Government 2022 list, ACMA RRL, BushTel profiles"

# The eight disagreement patterns among the 96 communities (2026-09-12 spike), with a plain
# reading of what each publisher combination says. Keyed on merge.py's ``mobile_says`` string.
DISAGREEMENT_READINGS = {
    "accc=0;ntg2022=0;rrl5=1;bushtel=0": (
        "Licensed site within 5 km; no carrier prediction, no 2022 listing, no BushTel record"
    ),
    "accc=0;ntg2022=0;rrl5=1;bushtel=1": (
        "Licensed site within 5 km and BushTel says covered; no carrier prediction, "
        "no 2022 listing"
    ),
    "accc=1;ntg2022=0;rrl5=0;bushtel=0": (
        "Carrier predicts coverage; not on the 2022 list, no licensed site within 5 km, "
        "no BushTel record"
    ),
    "accc=1;ntg2022=0;rrl5=1;bushtel=0": (
        "Carrier predicts coverage and a licensed site is within 5 km; not on the 2022 list, "
        "no BushTel record"
    ),
    "accc=1;ntg2022=0;rrl5=1;bushtel=1": (
        "Carrier predicts coverage, licensed site within 5 km, BushTel says covered; "
        "not on the 2022 list"
    ),
    "accc=1;ntg2022=1;rrl5=0;bushtel=0": (
        "Carrier predicts coverage and it is on the 2022 list; no licensed site within 5 km, "
        "no BushTel record"
    ),
    "accc=1;ntg2022=1;rrl5=0;bushtel=1": (
        "Carrier predicts coverage, on the 2022 list, BushTel says covered; "
        "no licensed site within 5 km"
    ),
    "accc=1;ntg2022=1;rrl5=1;bushtel=0": (
        "Carrier predicts coverage, on the 2022 list, licensed site within 5 km; "
        "no BushTel record"
    ),
}
UNANIMOUS_COVERED = "accc=1;ntg2022=1;rrl5=1;bushtel=1"
UNANIMOUS_NOT_COVERED = "accc=0;ntg2022=0;rrl5=0;bushtel=0"


def load_rows() -> list[dict[str, str]]:
    with TABLE.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def _resolve(tokens: dict, ref: str) -> str:
    """Resolve a ``{color.name}`` reference against ``tokens['color']``."""
    if ref.startswith("{") and ref.endswith("}"):
        node = tokens
        for part in ref[1:-1].split("."):
            node = node[part]
        return node
    return ref


def _parse_outline_path(path_str: str) -> MplPath:
    """Turn the pack's ``M x y L x y ... Z`` SVG path string into a matplotlib Path."""
    words = path_str.split()
    vertices: list[tuple[float, float]] = []
    codes: list[int] = []
    index = 0
    while index < len(words):
        command = words[index]
        if command in ("M", "L"):
            x, y = float(words[index + 1]), float(words[index + 2])
            vertices.append((x, y))
            codes.append(MplPath.MOVETO if command == "M" else MplPath.LINETO)
            index += 3
        elif command == "Z":
            vertices.append((0.0, 0.0))
            codes.append(MplPath.CLOSEPOLY)
            index += 1
        else:
            raise ValueError(f"unexpected token {command!r} in outline path")
    return MplPath(vertices, codes)


def _new_axes():
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_axes((0.03, 0.06, 0.94, 0.86))
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(VIEW_H, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _draw_outline(ax, tokens: dict) -> None:
    path = _parse_outline_path(outline.outline_path(BOUNDARY_RAW))
    land = _resolve(tokens, tokens["semantic"]["map-land"])
    line = _resolve(tokens, tokens["semantic"]["map-outline"])
    ax.add_patch(PathPatch(path, facecolor=land, edgecolor=line, linewidth=1.0, zorder=1))


def _title(ax, text: str) -> None:
    ax.set_title(text, loc="left", fontsize=20, pad=16)


def _source_line(fig, text: str) -> None:
    fig.text(0.02, 0.012, text, fontsize=11)


def map_verdict(rows: list[dict[str, str]], tokens: dict, out_png: Path) -> None:
    """Map coloured by the telehealth video verdict, one point per community."""
    fig, ax = _new_axes()
    _draw_outline(ax, tokens)
    counts = {verdict: 0 for verdict in VERDICT_ORDER}
    for row in rows:
        verdict = row["telehealth_video"]
        counts[verdict] += 1
        x, y = outline.project(float(row["lat"]), float(row["lon"]))
        entry = tokens["verdict"][verdict]
        ax.scatter(
            [x], [y], s=70, color=entry["fill"], edgecolors=entry["text"], linewidths=1.2, zorder=2
        )
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=tokens["verdict"][verdict]["fill"],
            markeredgecolor=tokens["verdict"][verdict]["text"],
            markersize=12,
            label=f"{tokens['verdict'][verdict]['glyph']} {tokens['verdict'][verdict]['word']} "
            f"({counts[verdict]})",
        )
        for verdict in VERDICT_ORDER
    ]
    ax.legend(handles=handles, loc="lower left", title="Telehealth video verdict", frameon=False)
    _title(ax, "Telehealth video verdict by community")
    _source_line(fig, SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def map_agreement(rows: list[dict[str, str]], tokens: dict, out_png: Path) -> None:
    """Map coloured by how many of the four mobile publishers agree the site is covered."""
    fig, ax = _new_axes()
    _draw_outline(ax, tokens)
    cmap = matplotlib.colormaps["RdYlGn"]
    ink = tokens["color"]["ink"]
    counts = {n: 0 for n in range(5)}
    for row in rows:
        covered = int(row["mobile_sources_covered"])
        counts[covered] += 1
        x, y = outline.project(float(row["lat"]), float(row["lon"]))
        ax.scatter(
            [x], [y], s=70, color=cmap(covered / 4), edgecolors=ink, linewidths=1.0, zorder=2
        )
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=cmap(n / 4),
            markeredgecolor=ink,
            markersize=12,
            label=f"{n} of 4 publishers agree covered ({counts[n]})",
        )
        for n in range(5)
    ]
    ax.legend(handles=handles, loc="lower left", title="Publisher agreement count", frameon=False)
    _title(ax, "Publisher agreement count by community")
    _source_line(fig, SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def write_disagreement_patterns(rows: list[dict[str, str]], out_csv: Path) -> None:
    """One row per distinct ``mobile_says`` pattern: count, plain reading, community names."""
    groups: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        groups[row["mobile_says"]].append(row["name"])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["pattern", "n", "reading", "communities"])
        for pattern in sorted(groups):
            names = sorted(groups[pattern])
            if pattern == UNANIMOUS_COVERED:
                reading = "All four publishers agree the community is covered"
            elif pattern == UNANIMOUS_NOT_COVERED:
                reading = "All four publishers agree the community has no recorded path"
            else:
                reading = DISAGREEMENT_READINGS[pattern]
            writer.writerow([pattern, len(names), reading, "; ".join(names)])


def write_verify_on_ground(rows: list[dict[str, str]], out_csv: Path) -> None:
    """The 11 "licensed mast, no coverage map" communities (same filter as the pack)."""
    selected = sorted(
        (
            row
            for row in rows
            if row["mobile_says"].startswith("accc=0;") and ";rrl5=1;" in row["mobile_says"]
        ),
        key=lambda row: row["name"],
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "name",
                "region",
                "population",
                "nearest_site_km",
                "nearest_site_name",
                "nearest_site_precision",
                "accc_4g",
                "ntg2022_listed",
            ]
        )
        for row in selected:
            writer.writerow(
                [
                    row["name"],
                    row["nt_region"].title(),
                    row["population_abs2021"],
                    row["nearest_site_km"],
                    row["nearest_site_name"],
                    row["nearest_site_precision"],
                    "Y" if "accc=1;" in row["mobile_says"] else "N",
                    "Y" if row["ntg2022_listed"] == "1" else "N",
                ]
            )


def write_verdict_counts(rows: list[dict[str, str]], out_csv: Path) -> None:
    """Per service, per verdict: community count and population sum.

    A community's population is left out of the sum below ``POPULATION_SUPPRESS_BELOW``
    (PRD section 7); those communities are counted instead in a trailing "under 100" row
    per service, with no population figure attached.
    """
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["service", "verdict", "communities", "population"])
        for service in SERVICES:
            buckets: dict[str, list[dict[str, str]]] = {verdict: [] for verdict in VERDICT_ORDER}
            for row in rows:
                buckets[row[service]].append(row)
            suppressed = 0
            for verdict in VERDICT_ORDER:
                members = buckets[verdict]
                population = 0
                for member in members:
                    value = int(member["population_abs2021"])
                    if value >= POPULATION_SUPPRESS_BELOW:
                        population += value
                    else:
                        suppressed += 1
                writer.writerow([SERVICE_LABELS[service], verdict, len(members), population])
            writer.writerow([SERVICE_LABELS[service], "under 100", suppressed, "suppressed"])


def main() -> None:
    if not BOUNDARY_RAW.is_file():
        raise FileNotFoundError(
            f"{BOUNDARY_RAW.relative_to(ROOT)} is missing. Re-fetch it with: "
            f"{outline.FETCH_COMMAND}"
        )
    rows = load_rows()
    tokens = load_tokens()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    map_verdict(rows, tokens, FIGURES_DIR / "map_verdict.png")
    map_agreement(rows, tokens, FIGURES_DIR / "map_agreement.png")
    write_disagreement_patterns(rows, TABLES_DIR / "disagreement_patterns.csv")
    write_verify_on_ground(rows, TABLES_DIR / "verify_on_the_ground.csv")
    write_verdict_counts(rows, TABLES_DIR / "verdict_counts.csv")
    print(f"{FIGURES_DIR.relative_to(ROOT).as_posix()}: map_verdict.png, map_agreement.png")
    print(
        f"{TABLES_DIR.relative_to(ROOT).as_posix()}: disagreement_patterns.csv, "
        "verify_on_the_ground.csv, verdict_counts.csv"
    )


if __name__ == "__main__":
    main()
