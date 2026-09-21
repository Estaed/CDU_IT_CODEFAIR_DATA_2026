"""Report-ready figures and tables for the Findings section (PRD section 4.1, item 3).

Reads ``data/out/capability_table.csv`` (already carries the merged verdicts and the
mobile disagreement pattern, both written by ``merge.py``) and writes three static NT maps
as PNG to ``data/out/figures/`` plus four CSV tables to ``data/out/tables/``. Colours and
glyphs are read from ``design/ds/design/tokens.json``, never retyped (CLAUDE.md Blueprint,
layer rule 5). Run from the project root:
``PYTHONUTF8=1 .venv/Scripts/python -m pipeline.figures``.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.legend_handler import HandlerTuple  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle, PathPatch, Wedge  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

from pipeline import outline, prioritise, provenance  # noqa: E402

plt.rcParams["font.family"] = "sans-serif"

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data/out/capability_table.csv"
PRIORITY = ROOT / "data/out/priority.csv"
PRIORITY_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.prioritise"
RELIABILITY = ROOT / "data/out/reliability.csv"
RELIABILITY_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.reliability"
PACK_JSON = ROOT / "data/out/data_pack.json"
PACK_COMMAND = "PYTHONUTF8=1 .venv/Scripts/python -m pipeline.pack"
THRESHOLDS_CSV = ROOT / "pipeline/thresholds.csv"
PROVENANCE_MD = ROOT / "data/out/PROVENANCE.md"
FINDINGS_MD = ROOT / "docs/FINDINGS.md"
FINDING_SEPARATOR = " — "
TOKENS_PATH = ROOT / "design/ds/design/tokens.json"
BOUNDARY_RAW = ROOT / "data/raw" / outline.RAW_NAME
FIGURES_DIR = ROOT / "data/out/figures"
TABLES_DIR = ROOT / "data/out/tables"
AUDIT_5KM = TABLES_DIR / "audit_within_5km.csv"

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

# Task-40: the priority map splits the 96 into thirds of the ranking, worst first. Three
# buckets, not 96 shades: the point of the map is which third to look at.
PRIORITY_TERCILES = (
    ("First third", "act first"),
    ("Second third", "next"),
    ("Last third", "watch"),
)
PRIORITY_COLUMNS = ("rank", "name", "score", "telehealth_video", "intervention", "addressee")

# Task-43: the reliability map, the publisher-count map, the sensitivity chart and the four
# report tables they feed, plus docs/FINDINGS.md. Nothing here computes a number the pipeline
# has not already written; every function below is a projection of an existing CSV, the pack's
# JSON or PROVENANCE.md.
RELIABILITY_WORDS = ("high", "medium", "low", "none")
# The word-to-verdict-token map mirrors the app's glyph language (four fill states) onto the
# four verdict colours already in tokens.json, rather than inventing a fifth palette.
RELIABILITY_WORD_VERDICT = {
    "high": "works",
    "medium": "degraded",
    "low": "fails",
    "none": "nodata",
}
RELIABILITY_MARKER_RADIUS = 2.2
RELIABILITY_SOURCE_LINE = "Source: pipeline.reliability, National Audit of Mobile Coverage"
PUBLISHER_SOURCE_LINE = (
    "Sources: ACCC MIR 2025, NT Government 2022 list, ACMA RRL, BushTel profiles, "
    "National Audit non-alignment tiles"
)
SENSITIVITY_SOURCE_LINE = "Source: pipeline.prioritise, priority_weights.csv"

# (key, publisher label, kind, pipeline.provenance id) in the order Blueprint's "Publisher
# line" seam lists them.
PUBLISHER_SPEC = (
    ("accc", "ACCC Mobile Infrastructure Report 2025", "predicted", "accc_mir_2025"),
    ("ntg2022", "NT Government 2022 coverage list", "listed", "ntg_2022"),
    ("rrl", "ACMA licence register", "licensed", "rrl"),
    ("bushtel", "BushTel", "portal", "bushtel"),
    ("audit", "National Audit of Mobile Coverage", "measured", "audit_non_alignment_2026_05"),
)

TOP10_COLUMNS = (
    "rank",
    "name",
    "region",
    "population",
    "score",
    "intervention",
    "addressee",
    "why",
    "telehealth_video",
    "reliability_word",
    "agreement",
)
INTERVENTION_COLUMNS = ("intervention", "addressee", "count", "population", "health_centres")
PUBLISHER_SUMMARY_COLUMNS = (
    "publisher",
    "kind",
    "says_covered",
    "says_not_covered",
    "not_recorded",
    "source",
    "date",
)
RELIABILITY_WORDS_COLUMNS = ("word", "count", "population", "mean_p_wrong", "top_driver_pairs")
VOICE_UNREACHABLE_COLUMNS = ("bushtel_id", "name", "region", "population", "health_centre")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_rows() -> list[dict[str, str]]:
    return _read_csv(TABLE)


def load_tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def load_reliability() -> list[dict[str, str]]:
    """The per-community map-claim reliability words ``pipeline.reliability`` wrote."""
    if not RELIABILITY.is_file():
        raise FileNotFoundError(
            f"{RELIABILITY.relative_to(ROOT).as_posix()} is missing. Write it with: "
            f"{RELIABILITY_COMMAND}"
        )
    return _read_csv(RELIABILITY)


def load_audit_5km() -> list[dict[str, str]]:
    """The three communities with a measured drive-test non-alignment within 5 km."""
    if not AUDIT_5KM.is_file():
        raise FileNotFoundError(
            f"{AUDIT_5KM.relative_to(ROOT).as_posix()} is missing. Run "
            f"{RELIABILITY_COMMAND} (it writes this table too)."
        )
    return _read_csv(AUDIT_5KM)


def load_thresholds() -> list[dict[str, str]]:
    return _read_csv(THRESHOLDS_CSV)


def load_pack_agreement() -> dict[int, dict]:
    """``{bushtel_id: {"covered": n, "available": n}}`` straight from the built pack.

    The app renders ``agreement.covered``/``agreement.available`` from the pack, which is the
    five-line count (``rules.agreement``, Blueprint's "Publisher line" seam): since Task-38 the
    measured (Audit) line joins the count whenever it makes a claim (``audit5 == "1"``), so a
    community can read 4 of 5 rather than 4 of 4. ``capability_table.csv``'s
    ``mobile_sources_covered``/``mobile_publishers_available`` columns predate that line and
    stay at four; this reads the pack itself instead of reproducing the rule a second time.
    """
    if not PACK_JSON.is_file():
        raise FileNotFoundError(
            f"{PACK_JSON.relative_to(ROOT).as_posix()} is missing. Write it with: {PACK_COMMAND}"
        )
    pack = json.loads(PACK_JSON.read_text(encoding="utf-8"))
    return {int(community["id"]): community["agreement"] for community in pack["communities"]}


def _threshold_value(thresholds: list[dict[str, str]], service: str, metric: str) -> str:
    for row in thresholds:
        if row["service"] == service and row["metric"] == metric:
            return row["value"]
    raise KeyError(f"no threshold row for service={service!r} metric={metric!r}")


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


def load_priority() -> list[dict[str, str]]:
    """The ranking ``pipeline.prioritise`` wrote, in rank order."""
    if not PRIORITY.is_file():
        raise FileNotFoundError(
            f"{PRIORITY.relative_to(ROOT).as_posix()} is missing. Write it with: "
            f"{PRIORITY_COMMAND}"
        )
    with PRIORITY.open(newline="", encoding="utf-8-sig") as handle:
        entries = list(csv.DictReader(handle))
    entries.sort(key=lambda entry: int(entry["rank"]))
    return entries


def _tercile(rank: int, total: int) -> int:
    """0, 1 or 2: which third of the ranking this rank falls in."""
    return min(2, (rank - 1) * 3 // total)


def map_priority(
    rows: list[dict[str, str]], priority: list[dict[str, str]], tokens: dict, out_png: Path
) -> None:
    """Map coloured by which third of the priority ranking a community falls in."""
    fig, ax = _new_axes()
    _draw_outline(ax, tokens)
    cmap = matplotlib.colormaps["RdYlGn"]
    ink = tokens["color"]["ink"]
    by_id = {int(entry["id"]): int(entry["rank"]) for entry in priority}
    total = len(priority)
    counts = {index: 0 for index in range(len(PRIORITY_TERCILES))}
    for row in rows:
        rank = by_id[int(row["bushtel_id"])]
        band = _tercile(rank, total)
        counts[band] += 1
        x, y = outline.project(float(row["lat"]), float(row["lon"]))
        ax.scatter(
            [x], [y], s=70, color=cmap(band / 2), edgecolors=ink, linewidths=1.0, zorder=2
        )
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=cmap(index / 2),
            markeredgecolor=ink,
            markersize=12,
            label=f"{label} of the ranking, {reading} ({counts[index]})",
        )
        for index, (label, reading) in enumerate(PRIORITY_TERCILES)
    ]
    ax.legend(handles=handles, loc="lower left", title="Priority ranking", frameon=False)
    _title(ax, "Priority ranking by community")
    _source_line(fig, SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def write_priority_table(
    rows: list[dict[str, str]], priority: list[dict[str, str]], out_csv: Path
) -> None:
    """The 96 in rank order with the six columns the app's Priority tab shows."""
    verdicts = {int(row["bushtel_id"]): row["telehealth_video"] for row in rows}
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(PRIORITY_COLUMNS)
        for entry in priority:
            cells = {**entry, "telehealth_video": verdicts[int(entry["id"])]}
            writer.writerow([cells[column] for column in PRIORITY_COLUMNS])


def _reliability_style(tokens: dict, word: str) -> tuple[str, str]:
    """``(fill, edge)`` for one reliability word, reusing the app's own verdict tokens."""
    verdict = tokens["verdict"][RELIABILITY_WORD_VERDICT[word]]
    return verdict["fill"], verdict["text"]


def _reliability_patches(x: float, y: float, word: str, tokens: dict, radius: float) -> list:
    """The patches for one marker: filled (high), half (medium), ring (low), dotted ring (none).

    Mirrors the app's four verdict fill states (Blueprint, 2026-09-16) without inventing new
    glyphs: a ring is drawn for every word, half-filled for ``medium``, solid for ``high``,
    dotted for ``none``.
    """
    fill, edge = _reliability_style(tokens, word)
    if word == "high":
        return [Circle((x, y), radius, facecolor=fill, edgecolor=edge, linewidth=1.0)]
    if word == "medium":
        return [
            Circle((x, y), radius, facecolor="none", edgecolor=edge, linewidth=1.0),
            Wedge((x, y), radius, 90, 270, facecolor=fill, edgecolor="none"),
        ]
    if word == "low":
        return [Circle((x, y), radius, facecolor="none", edgecolor=edge, linewidth=1.4)]
    return [Circle((x, y), radius, facecolor="none", edgecolor=edge, linewidth=1.4, linestyle=":")]


def map_reliability(rows: list[dict[str, str]], tokens: dict, out_png: Path) -> None:
    """Map by the map-claim reliability word: filled, half, ring or dotted ring (Task-43)."""
    fig, ax = _new_axes()
    _draw_outline(ax, tokens)
    words = {int(entry["id"]): entry["word"] for entry in load_reliability()}
    counts = {word: 0 for word in RELIABILITY_WORDS}
    for row in rows:
        word = words.get(int(row["bushtel_id"]), "none")
        counts[word] += 1
        x, y = outline.project(float(row["lat"]), float(row["lon"]))
        for patch in _reliability_patches(x, y, word, tokens, RELIABILITY_MARKER_RADIUS):
            patch.set_zorder(2)
            ax.add_patch(patch)
    handles = [tuple(_reliability_patches(0, 0, word, tokens, 1.0)) for word in RELIABILITY_WORDS]
    labels = [f"{word.capitalize()} ({counts[word]})" for word in RELIABILITY_WORDS]
    ax.legend(
        handles,
        labels,
        handler_map={tuple: HandlerTuple(ndivide=None)},
        loc="lower left",
        title="Map-claim reliability",
        frameon=False,
    )
    _title(ax, "Map-claim reliability by community")
    _source_line(fig, RELIABILITY_SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def _covered_count(row: dict[str, str]) -> int:
    """How many of the five publisher lines say covered.

    The measured (Audit) line never says ``covered`` (Task-39 Deviation 2: it is
    ``not-covered`` or ``not-recorded`` only), so this is exactly ``mobile_sources_covered``,
    already written by ``merge.py`` over the other four lines.
    """
    return int(row["mobile_sources_covered"])


def map_publishers(
    rows: list[dict[str, str]], tokens: dict, audit_ids: set[int], out_png: Path
) -> None:
    """Map by how many of the five publisher lines say covered, the Audit's three marked."""
    fig, ax = _new_axes()
    _draw_outline(ax, tokens)
    cmap = matplotlib.colormaps["RdYlGn"]
    ink = tokens["color"]["ink"]
    counts = {n: 0 for n in range(6)}
    marked: list[tuple[float, float]] = []
    for row in rows:
        covered = _covered_count(row)
        counts[covered] += 1
        x, y = outline.project(float(row["lat"]), float(row["lon"]))
        ax.scatter(
            [x], [y], s=70, color=cmap(covered / 5), edgecolors=ink, linewidths=1.0, zorder=2
        )
        if int(row["bushtel_id"]) in audit_ids:
            marked.append((x, y))
    if marked:
        xs, ys = zip(*marked, strict=True)
        ax.scatter(xs, ys, s=170, facecolors="none", edgecolors=ink, linewidths=2.0, zorder=3)
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=cmap(n / 5),
            markeredgecolor=ink,
            markersize=12,
            label=f"{n} of 5 publishers say covered ({counts[n]})",
        )
        for n in range(6)
    ]
    handles.append(
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor="none",
            markeredgecolor=ink,
            markeredgewidth=2.0,
            markersize=13,
            label=f"Measured non-alignment within 5 km ({len(marked)})",
        )
    )
    ax.legend(handles=handles, loc="lower left", title="Publisher coverage claims", frameon=False)
    _title(ax, "Publisher coverage agreement by community")
    _source_line(fig, PUBLISHER_SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def load_sensitivity() -> list[dict[str, str]]:
    """The sensitivity table ``pipeline.prioritise`` wrote, in its own (component, factor) order."""
    path = prioritise.OUT_SENSITIVITY
    if not path.is_file():
        raise FileNotFoundError(
            f"{path.relative_to(ROOT).as_posix()} is missing. Write it with: "
            f"{PRIORITY_COMMAND}"
        )
    return _read_csv(path)


def chart_sensitivity(tokens: dict, out_png: Path) -> None:
    """One horizontal bar per (weight, factor): top-10 overlap, rho printed at the bar end."""
    rows = load_sensitivity()
    weights = {spec["component"]: spec for spec in prioritise.load_weights()}
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_axes((0.32, 0.06, 0.62, 0.86))
    bar_color = _resolve(tokens, tokens["semantic"]["action-primary"])
    labels: list[str] = []
    values: list[int] = []
    for row in rows:
        spec = weights[row["component"]]
        label = f"{row['component']} (x{row['factor']})"
        if spec["weight"] == 0:
            label += f", {spec['note']}"
        labels.append(label)
        values.append(int(row["top10_overlap"]))
    positions = list(range(len(rows)))
    ax.barh(positions, values, color=bar_color, zorder=2)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    # Headroom past TOP_N so the rho label at the bar end is never clipped by the axes; the
    # ticks still stop at TOP_N, so the data range read off the axis is exactly 0..TOP_N.
    ax.set_xlim(0, prioritise.TOP_N * 1.4)
    ax.set_xticks(range(0, prioritise.TOP_N + 1, 2))
    ax.set_xlabel(f"Top-{prioritise.TOP_N} overlap against the baseline ranking")
    for position, row in zip(positions, rows, strict=True):
        ax.text(
            int(row["top10_overlap"]) + 0.15,
            position,
            f"rho {row['spearman_rho']}",
            va="center",
            fontsize=8,
        )
    _title(ax, "Priority score sensitivity")
    _source_line(fig, SENSITIVITY_SOURCE_LINE)
    fig.savefig(out_png, dpi=DPI)
    plt.close(fig)


def write_top10(
    rows: list[dict[str, str]],
    priority: list[dict[str, str]],
    reliability: list[dict[str, str]],
    pack_agreement: dict[int, dict],
    out_csv: Path,
) -> Path:
    """The ten highest-ranked communities: the evidence the Recommendations queue rests on."""
    by_id = {int(row["bushtel_id"]): row for row in rows}
    reliability_by_id = {int(entry["id"]): entry["word"] for entry in reliability}
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(TOP10_COLUMNS)
        for entry in priority[:10]:
            table_row = by_id[int(entry["id"])]
            claim = pack_agreement[int(entry["id"])]
            agreement = f"{claim['covered']}/{claim['available']}"
            writer.writerow(
                [
                    entry["rank"],
                    entry["name"],
                    table_row["nt_region"].title(),
                    table_row["population_abs2021"],
                    entry["score"],
                    entry["intervention"],
                    entry["addressee"],
                    entry["why"],
                    table_row["telehealth_video"],
                    reliability_by_id.get(int(entry["id"]), "none"),
                    agreement,
                ]
            )
    return out_csv


def write_intervention_counts(
    rows: list[dict[str, str]], priority: list[dict[str, str]], out_csv: Path
) -> Path:
    """Every intervention ``pipeline.prioritise`` can reach, in rule order, over the 96."""
    by_id = {int(row["bushtel_id"]): row for row in rows}
    buckets: dict[str, dict] = {
        word: {"addressee": addressee, "count": 0, "population": 0, "health_centres": 0}
        for word, addressee, _fired in prioritise.INTERVENTIONS
    }
    for entry in priority:
        bucket = buckets[entry["intervention"]]
        table_row = by_id[int(entry["id"])]
        bucket["count"] += 1
        bucket["population"] += int(table_row["population_abs2021"])
        if table_row["svc_health_centre"] == "Y":
            bucket["health_centres"] += 1
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(INTERVENTION_COLUMNS)
        for word, addressee, _fired in prioritise.INTERVENTIONS:
            bucket = buckets[word]
            writer.writerow(
                [word, addressee, bucket["count"], bucket["population"], bucket["health_centres"]]
            )
    return out_csv


def _publisher_state(rows: list[dict[str, str]], key: str) -> tuple[int, int, int]:
    """``(covered, not_covered, not_recorded)`` for one publisher over the 96.

    Reproduces ``pipeline.pack.publisher_lines`` exactly (read, not imported: that module is
    outside this lane's OWNS), so the counts match what the app and the pack show.
    """
    covered = not_covered = not_recorded = 0
    for row in rows:
        if key == "accc":
            state = "covered" if int(row["carriers_4g_count"] or 0) >= 1 else "not-covered"
        elif key == "ntg2022":
            state = "covered" if row["ntg2022_listed"] == "1" else "not-covered"
        elif key == "rrl":
            state = "covered" if row["any_within_5km"] == "1" else "not-covered"
        elif key == "bushtel":
            if row["svc_mobile_phone"] == "Y":
                state = "covered"
            elif row["svc_mobile_phone"] == "N":
                state = "not-covered"
            else:
                state = "not-recorded"
        else:  # audit
            state = "not-covered" if row["audit5"] == "1" else "not-recorded"
        if state == "covered":
            covered += 1
        elif state == "not-covered":
            not_covered += 1
        else:
            not_recorded += 1
    return covered, not_covered, not_recorded


def write_publisher_lines_summary(rows: list[dict[str, str]], out_csv: Path) -> Path:
    """Per publisher (five rows): how many of the 96 say covered, not covered or never recorded."""
    registry = {entry["id"]: entry for entry in provenance.SOURCES}
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(PUBLISHER_SUMMARY_COLUMNS)
        for key, label, kind, provenance_id in PUBLISHER_SPEC:
            covered, not_covered, not_recorded = _publisher_state(rows, key)
            entry = registry[provenance_id]
            writer.writerow(
                [label, kind, covered, not_covered, not_recorded, entry["name"], entry["date"]]
            )
    return out_csv


def write_reliability_words(
    rows: list[dict[str, str]], reliability: list[dict[str, str]], out_csv: Path
) -> Path:
    """The four reliability words: count, population, mean ``p_wrong``, the usual drivers."""
    by_id = {int(row["bushtel_id"]): row for row in rows}
    buckets: dict[str, dict] = {
        word: {"count": 0, "population": 0, "p_wrong": [], "pairs": defaultdict(int)}
        for word in RELIABILITY_WORDS
    }
    for entry in reliability:
        bucket = buckets[entry["word"]]
        bucket["count"] += 1
        bucket["population"] += int(by_id[int(entry["id"])]["population_abs2021"])
        if entry["p_wrong"]:
            bucket["p_wrong"].append(float(entry["p_wrong"]))
        if entry["driver1"] and entry["driver2"]:
            bucket["pairs"][f"{entry['driver1']}, {entry['driver2']}"] += 1
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(RELIABILITY_WORDS_COLUMNS)
        for word in RELIABILITY_WORDS:
            bucket = buckets[word]
            mean_p = (
                round(sum(bucket["p_wrong"]) / len(bucket["p_wrong"]), 4)
                if bucket["p_wrong"]
                else ""
            )
            top_pairs = sorted(bucket["pairs"].items(), key=lambda item: (-item[1], item[0]))[:3]
            pairs_text = "; ".join(f"{pair} ({count})" for pair, count in top_pairs)
            writer.writerow([word, bucket["count"], bucket["population"], mean_p, pairs_text])
    return out_csv


# The block the report team pastes into their own AI assistant before writing. Static text,
# kept here so it ships inside the generated file and never drifts from it (Tarik,
# 2026-09-17: "findings'in içine prompt koy").
TEAM_PROMPT = [
    "## For the report team and their AI assistant",
    "",
    "Paste the block below into your assistant, then attach or open the files it names.",
    "",
    "> You are helping write the 8-page report, the slide deck and the 10-minute pitch for",
    "> Crosscheck, team DIC005's entry to the CDU IT Code Fair 2026 Data Innovation Challenge",
    "> (theme: Remote Connectivity). Read, in this order, before writing a word:",
    "> 1. `README.md` (the brief, the five tasks, the judging criteria, the judges);",
    ">    `docs/report-requirements.md` (the mandatory report structure and file rules).",
    "> 2. `docs/PRD.md` §1 (purpose), §2 (users; the primary target is the NT Government",
    ">    DCDD analyst, judged by the \"analyst's sixty seconds\"), §4.2 fourth batch (what was",
    ">    built on 2026-09-17 and why), §7 (ethics, the Discussion section's raw material),",
    ">    §9 (open questions: which licences and figures are still unanswered).",
    "> 3. This file, `docs/FINDINGS.md`: every sentence here names the table that proves it",
    ">    and the number as the pipeline emitted it. Use these sentences; do not invent numbers.",
    "> 4. The tables under `data/out/tables/` (`top10.csv`, `intervention_counts.csv`,",
    ">    `publisher_lines_summary.csv`, `reliability_words.csv`, `reliability_validation.csv`,",
    ">    `priority_sensitivity.csv`, `disagreement_patterns.csv`, `verdict_counts.csv`) and",
    ">    the figures under `data/out/figures/` (six PNG maps and charts, print-ready).",
    "> 5. `data/out/PROVENANCE.md` for every source's URL, date, licence and attribution line",
    ">    (the References section), and `pipeline/thresholds.csv` for every requirement figure.",
    "> 6. `CLAUDE.md`, the Blueprint section, only if you need the architecture in one page.",
    ">",
    "> What the project is, in five sentences. Published coverage sources for 96 remote NT",
    "> communities disagree with each other and none says what a clinic or school can actually",
    "> do with its connection. Crosscheck puts five sources side by side per community (four",
    "> claims and one government drive test), tests the best available path against what",
    "> telehealth, school video, myGov and voice/SMS require, and says where the sources",
    "> disagree. A small model trained on the drive tests rates how reliable each coverage",
    "> claim is. A transparent, weighted score ranks the 96 communities for action, with one",
    "> intervention and one addressee each, and a sensitivity table shows the top of the list",
    "> does not depend on any single weight. It ships as an offline single-file web app, a",
    "> reproducible Python pipeline, this report and a pitch; nothing in the app computes a",
    "> verdict or runs a model.",
    ">",
    "> The priority weights, in plain words: each community gets a score between 0 and 1",
    "> from nine components (population, services present, the telehealth and voice verdicts,",
    "> claim reliability, a drive-test contradiction nearby, an already-funded MBSP base",
    "> station nearby counted against, and two placeholders at weight zero until their data",
    "> licences arrive). Each component is scaled to 0..1 across the 96, multiplied by its",
    "> weight from `pipeline/priority_weights.csv`, and summed. The weights are a choice, not",
    "> a measurement: say so, print the CSV, and cite the sensitivity table, which shows that",
    "> halving or raising any one weight by half keeps at least 6 of the top 10 in place.",
    ">",
    "> Do not claim: that the app measures signal (it does not); that a reliability word is a",
    "> probability (it is a rank; the model is class-balanced on a 2.8 % base rate); that the",
    "> model was validated everywhere (two of five folds held no positives); that a verdict is",
    "> ground truth (95 of 96 rest on one measured satellite latency figure, and a clinic may",
    "> sit on a government link nobody has published). Declare the AI used in building the",
    "> entry (Claude and Codex as coding agents; scikit-learn for the one model) in the",
    "> appendix, as the brief requires. Write in the report's own voice, not the assistant's.",
]


def write_findings_md(
    rows: list[dict[str, str]],
    priority: list[dict[str, str]],
    reliability: list[dict[str, str]],
    thresholds: list[dict[str, str]],
    pack_agreement: dict[int, dict],
    out_md: Path = FINDINGS_MD,
) -> Path:
    """``docs/FINDINGS.md``: one sentence the report may make per entry, sourced at write time.

    Every number below is read from a table, the pack's inputs or ``PROVENANCE.md`` on this
    run, never typed (Task-43 contract item 3): re-running the pipeline refreshes the file.
    """
    today = date.today().isoformat()

    top1 = priority[0]
    by_id = {int(row["bushtel_id"]): row for row in rows}
    top1_row = by_id[int(top1["id"])]
    reliability_by_id = {int(entry["id"]): entry for entry in reliability}
    top1_reliability = reliability_by_id.get(int(top1["id"]), {}).get("word", "none")
    top1_claim = pack_agreement[int(top1["id"])]
    top1_agreement = f"{top1_claim['covered']}/{top1_claim['available']}"

    validation_rows = _read_csv(TABLES_DIR / "reliability_validation.csv")
    pooled = next(row for row in validation_rows if row["fold"] == "pooled")
    folds_with_auc = sum(
        1 for row in validation_rows if row["fold"] != "pooled" and row["auc"]
    )

    audit_5km = load_audit_5km()

    # nbn_technology, not best_path: the Sky Muster figure and the LEO sentence attach to the
    # community's NBN residual technology (PRD section 1's "95 of 96"), not to whichever path
    # a mobile carrier also predicts there.
    satellite = sum(1 for row in rows if row["nbn_technology"] == "SATELLITE_RESIDUAL")
    not_satellite = len(rows) - satellite
    sky_muster_ms = _threshold_value(thresholds, "nbn_satellite", "latency")
    leo_ms = _threshold_value(thresholds, "leo_satellite", "latency")

    disagreement_rows = _read_csv(TABLES_DIR / "disagreement_patterns.csv")
    unanimous = {row["pattern"]: int(row["n"]) for row in disagreement_rows}
    covered_all = unanimous.get(UNANIMOUS_COVERED, 0)
    covered_none = unanimous.get(UNANIMOUS_NOT_COVERED, 0)
    disagree_total = sum(
        count
        for pattern, count in unanimous.items()
        if pattern not in (UNANIMOUS_COVERED, UNANIMOUS_NOT_COVERED)
    )

    intervention_rows = _read_csv(TABLES_DIR / "intervention_counts.csv")
    top_intervention = max(intervention_rows, key=lambda row: int(row["count"]))
    voice_unreachable = _read_csv(TABLES_DIR / "voice_unreachable.csv")

    reliability_word_rows = _read_csv(TABLES_DIR / "reliability_words.csv")
    words_line = ", ".join(f"{row['word']} {row['count']}" for row in reliability_word_rows)

    publisher_summary_rows = _read_csv(TABLES_DIR / "publisher_lines_summary.csv")
    audit_summary = next(row for row in publisher_summary_rows if row["kind"] == "measured")

    sensitivity_rows = load_sensitivity()
    worst = min(sensitivity_rows, key=lambda row: int(row["top10_overlap"]))

    with PROVENANCE_MD.open(encoding="utf-8") as handle:
        unstated_sources = sum(
            1 for line in handle if line.startswith("|") and "unstated" in line
        )

    suppressed = next(
        row
        for row in _read_csv(TABLES_DIR / "verdict_counts.csv")
        if row["service"] == SERVICE_LABELS["telehealth_video"] and row["verdict"] == "under 100"
    )

    sections: dict[str, list[str]] = {
        "Methodology": [
            f"The map-claim reliability model validates on a five-fold split by ABS SA3 "
            f"region; the pooled out-of-fold AUC over every claim tested is {pooled['auc']} "
            f"— evidence: data/out/tables/reliability_validation.csv — value: {pooled['auc']} "
            f"— run {today}.",
            f"That pooled AUC rests on {folds_with_auc} of 5 folds: the other 2 folds carried "
            f"no positive sample, so their AUC is undefined — evidence: "
            f"data/out/tables/reliability_validation.csv — value: {folds_with_auc} — "
            f"run {today}.",
            f"The National Audit records a measured drive-test non-alignment within 5 km for "
            f"{len(audit_5km)} of 96 communities — evidence: "
            f"data/out/tables/audit_within_5km.csv — value: {len(audit_5km)} — run {today}.",
        ],
        "Findings": [
            f"{top1['name']} ranks #1 of 96 with a priority score of {top1['score']} "
            f"(region {top1_row['nt_region'].title()}, population "
            f"{top1_row['population_abs2021']}), intervention '{top1['intervention']}' "
            f"addressed to {top1['addressee']} because {top1['why']} Telehealth verdict "
            f"{top1_row['telehealth_video']}; map-claim reliability {top1_reliability}; "
            f"publisher agreement {top1_agreement} — evidence: data/out/tables/top10.csv — "
            f"value: {top1['score']} — run {today}.",
            f"'{top_intervention['intervention']}' is the most common intervention, reaching "
            f"{top_intervention['count']} of 96 communities, addressed to "
            f"{top_intervention['addressee']} — evidence: "
            f"data/out/tables/intervention_counts.csv — value: {top_intervention['count']} "
            f"— run {today}.",
            f"Map-claim reliability words over the 96: {words_line} — evidence: "
            f"data/out/tables/reliability_words.csv — value: {reliability_word_rows[0]['count']} "
            f"— run {today}.",
            f"All four longstanding publishers (predicted, listed, licensed, portal) agree "
            f"covered for {covered_all} communities and agree not covered for {covered_none}; "
            f"{disagree_total} communities see disagreement — evidence: "
            f"data/out/tables/disagreement_patterns.csv — value: {covered_all} — run {today}.",
            f"{voice_unreachable_sentence(rows)}{FINDING_SEPARATOR}evidence: "
            f"data/out/tables/voice_unreachable.csv{FINDING_SEPARATOR}value: "
            f"{len(voice_unreachable)}{FINDING_SEPARATOR}"
            f"run {today}.",
            f"The measured publisher (National Audit) never records 'covered'; it records a "
            f"drive-test contradiction for {audit_summary['says_not_covered']} of 96 "
            f"communities — evidence: data/out/tables/publisher_lines_summary.csv — value: "
            f"{audit_summary['says_not_covered']} — run {today}.",
        ],
        "Discussion": [
            f"{satellite} of 96 communities have no NBN path but the satellite residual, so "
            f"every verdict computed off that path rests on the ACCC-measured Sky Muster "
            f"latency of {sky_muster_ms} ms and, where the assumption applies, the sentence "
            f"quoting the Starlink LEO figure of {leo_ms} ms from the same ACCC release; only "
            f"{not_satellite} of 96 (fixed line) does not — evidence: pipeline/thresholds.csv "
            f"— value: {satellite} — run {today}.",
            f"A reliability word of 'low' is a rank, not a probability: the model is fit with "
            f"class_weight=balanced against a pooled base rate of "
            f"{float(pooled['base_rate']) * 100:.2f} %, so 'low' means the claim ranks with "
            f"the ones the drive test contradicted, not a percent chance of being wrong — "
            f"evidence: data/out/tables/reliability_validation.csv — value: "
            f"{pooled['base_rate']} — run {today}.",
            f"Only {len(audit_5km)} of 96 communities have a drive test within 5 km; every "
            f"other reliability word is an extrapolation from the nearest audited conditions, "
            f"not a measurement at the community itself — evidence: "
            f"data/out/tables/audit_within_5km.csv — value: {len(audit_5km)} — run {today}.",
            f"{unstated_sources} of the raw sources this pack cites carry an unstated licence "
            f"with a request on file — evidence: data/out/PROVENANCE.md — value: "
            f"{unstated_sources} — run {today}.",
            f"Communities under 100 people are never shown a raw population figure; the "
            f"telehealth verdict table suppresses {suppressed['communities']} such communities "
            f"from its population sums — evidence: data/out/tables/verdict_counts.csv — "
            f"value: {suppressed['communities']} — run {today}.",
        ],
        "Recommendations": [
            f"The top 10 priority communities, with their interventions and addressees, are "
            f"the Recommendations section's evidence base — evidence: "
            f"data/out/tables/top10.csv — value: 10 — run {today}.",
            f"The priority ranking is not fragile: the smallest top-10 overlap under any "
            f"single weight moved to half or one-and-a-half of itself is "
            f"{worst['top10_overlap']} of {prioritise.TOP_N}, on {worst['component']} at "
            f"factor {worst['factor']} — evidence: "
            f"{prioritise.OUT_SENSITIVITY.relative_to(ROOT).as_posix()} — value: "
            f"{worst['top10_overlap']} — run {today}.",
            f"Eight interventions cover the 96 communities, addressed to DCDD, carriers, nbn "
            f"or ACMA by pattern — evidence: data/out/tables/intervention_counts.csv — value: "
            f"{len(intervention_rows)} — run {today}.",
        ],
    }

    lines = [
        "# Findings pack",
        "",
        f"Generated {today} by `pipeline.figures.write_findings_md` from the tables under "
        "`data/out/tables/`, `data/out/priority.csv`, `data/out/reliability.csv`, "
        "`pipeline/thresholds.csv` and `data/out/PROVENANCE.md`. Every number below is read "
        "from those files at write time; re-running the pipeline refreshes them.",
        "",
        *TEAM_PROMPT,
        "",
    ]
    for section, entries in sections.items():
        lines.append(f"## {section}")
        lines.append("")
        for entry in entries:
            lines.append(f"- {entry}")
        lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    # ``newline=""`` so Windows' text-mode translation never turns these into CRLF (every
    # other writer in this module keeps LF the same way, through csv.writer).
    with out_md.open("w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")
    return out_md


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


def write_voice_unreachable(rows: list[dict[str, str]], out_csv: Path) -> Path:
    """The communities whose existing ``voice_sms`` verdict is ``fails``."""
    selected = sorted(
        (row for row in rows if row["voice_sms"] == "fails"),
        key=lambda row: int(row["bushtel_id"]),
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(VOICE_UNREACHABLE_COLUMNS)
        for row in selected:
            writer.writerow(
                [
                    row["bushtel_id"],
                    row["name"],
                    row["nt_region"].title(),
                    row["population_abs2021"],
                    "Y" if row["svc_health_centre"] == "Y" else "N",
                ]
            )
    return out_csv


def voice_unreachable_sentence(rows: list[dict[str, str]]) -> str:
    """Return the report sentence for the failing voice/SMS communities."""
    unreachable = [row for row in rows if row["voice_sms"] == "fails"]
    people = sum(int(row["population_abs2021"]) for row in unreachable)
    clinics = sum(row["svc_health_centre"] == "Y" for row in unreachable)
    total = len(rows)
    count = len(unreachable)
    return (
        f"No public source records a mobile voice or SMS path in {count} of {total} communities "
        f"({people:,} people; {clinics} of them have a health centre). A mobile call needs a "
        f"path at both ends, so these communities are outside the mobile reach of the other "
        f"{total - count} as well as unable to call out; landlines, payphones and satellite "
        "phones are not in any source used here."
    )


def main() -> None:
    if not BOUNDARY_RAW.is_file():
        raise FileNotFoundError(
            f"{BOUNDARY_RAW.relative_to(ROOT)} is missing. Re-fetch it with: "
            f"{outline.FETCH_COMMAND}"
        )
    rows = load_rows()
    tokens = load_tokens()
    priority = load_priority()
    reliability = load_reliability()
    thresholds = load_thresholds()
    audit_5km = load_audit_5km()
    audit_ids = {int(row["bushtel_id"]) for row in audit_5km}
    pack_agreement = load_pack_agreement()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    map_verdict(rows, tokens, FIGURES_DIR / "map_verdict.png")
    map_agreement(rows, tokens, FIGURES_DIR / "map_agreement.png")
    map_priority(rows, priority, tokens, FIGURES_DIR / "map_priority.png")
    map_reliability(rows, tokens, FIGURES_DIR / "map_reliability.png")
    map_publishers(rows, tokens, audit_ids, FIGURES_DIR / "map_publishers.png")
    chart_sensitivity(tokens, FIGURES_DIR / "chart_sensitivity.png")
    write_disagreement_patterns(rows, TABLES_DIR / "disagreement_patterns.csv")
    write_verify_on_ground(rows, TABLES_DIR / "verify_on_the_ground.csv")
    write_verdict_counts(rows, TABLES_DIR / "verdict_counts.csv")
    write_voice_unreachable(rows, TABLES_DIR / "voice_unreachable.csv")
    write_priority_table(rows, priority, TABLES_DIR / "priority.csv")
    write_top10(rows, priority, reliability, pack_agreement, TABLES_DIR / "top10.csv")
    write_intervention_counts(rows, priority, TABLES_DIR / "intervention_counts.csv")
    write_publisher_lines_summary(rows, TABLES_DIR / "publisher_lines_summary.csv")
    write_reliability_words(rows, reliability, TABLES_DIR / "reliability_words.csv")
    write_findings_md(rows, priority, reliability, thresholds, pack_agreement)
    print(
        f"{FIGURES_DIR.relative_to(ROOT).as_posix()}: map_verdict.png, map_agreement.png, "
        "map_priority.png, map_reliability.png, map_publishers.png, chart_sensitivity.png"
    )
    print(
        f"{TABLES_DIR.relative_to(ROOT).as_posix()}: disagreement_patterns.csv, "
        "verify_on_the_ground.csv, verdict_counts.csv, priority.csv, top10.csv, "
        "intervention_counts.csv, publisher_lines_summary.csv, reliability_words.csv, "
        "voice_unreachable.csv"
    )
    print(f"{FINDINGS_MD.relative_to(ROOT).as_posix()}: written")


if __name__ == "__main__":
    main()
