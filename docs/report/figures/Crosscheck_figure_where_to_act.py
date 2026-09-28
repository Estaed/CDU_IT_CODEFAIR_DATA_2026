"""Example report figure: where to act first (Crosscheck, DIC005).

Reads the app's data pack (same numbers as the report), draws the NT outline, the carriers' own
4G claims as one faint ochre surface (as the app's map does), and the 96 communities by action
group, numbering the top ten of the service-gap group. Colours are the app's "Territory" palette
(app/theme.css, design/deviations.md): ink and greys for the groups, ochre only for the claims.
Every dot is one size; the group is told by tone, not by size. Static PNG for print.
"""
import json
import math
import re
from pathlib import Path

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as MPath

HERE = Path(__file__).resolve().parent
PACK = HERE.parents[2] / "data/out/data_pack.json"
OUT = HERE / "Crosscheck_figure_where_to_act.png"

SERVICE = "#141414"     # key series: service gap, the app's ink
CHECK = "#8A8A86"       # neutral, mid grey
MONITOR = "#C4C4BF"     # neutral, light grey
OCHRE, CLAIM_ALPHA = "#CB6015", 0.16   # NT ochre; the carriers' 4G claims, as in the app
INK, INK_MUTED, LAND, EDGE = "#141414", "#585858", "#F4F4F4", "#A8A8A3"
HALO = [pe.withStroke(linewidth=2.5, foreground="white")]
plt.rcParams["font.family"] = ["Calibri", "Arial", "DejaVu Sans"]

pack = json.loads(PACK.read_text(encoding="utf-8"))
com = {c["id"]: c for c in pack["communities"]}


def outline_path(d):
    verts, codes = [], []
    for cmd, x, y in re.findall(r"([MLZ])\s*(-?[\d.]+)?\s*(-?[\d.]+)?", d):
        if cmd == "Z":
            verts.append(verts[-1])
            codes.append(MPath.CLOSEPOLY)
        else:
            verts.append((float(x), -float(y)))
            codes.append(MPath.MOVETO if cmd == "M" else MPath.LINETO)
    return MPath(verts, codes)


fig = plt.figure(figsize=(6.3, 5.4), dpi=300)
ax = fig.add_axes([0.0, 0.06, 0.66, 0.80])
ax.add_patch(PathPatch(outline_path(pack["outline"]), facecolor=LAND, edgecolor=EDGE, lw=0.8))

# The three carriers' claimed 4G footprints (ACCC MIR 2025), overlapping: shade deepens where
# more than one carrier claims coverage.
for layer in pack["layers"]:
    if layer["kind"] == "area":
        for d in layer["paths"]:
            ax.add_patch(PathPatch(outline_path(d), facecolor=OCHRE, alpha=CLAIM_ALPHA, lw=0,
                                   zorder=1.5))

groups = {"monitor": (MONITOR, 2), "check": (CHECK, 2.5), "service": (SERVICE, 3)}
for g, (color, z) in groups.items():
    pts = [com[p["id"]] for p in pack["priority"] if p["g"] == g]
    ax.scatter([c["x"] for c in pts], [-c["y"] for c in pts], s=16, c=color, zorder=z,
               edgecolors="white", linewidths=0.6)

# Top ten: numbered markers in place; ones crowded by another top-ten point move to a column
# east of the coast with a leader line, so no number hides another.
top = [p for p in pack["priority"] if p["g"] == "service"][:10]
pos = {p["rank"]: (com[p["id"]]["x"], -com[p["id"]]["y"]) for p in top}
crowded = sorted((r for r in pos if any(r != o and math.dist(pos[r], pos[o]) < 18 for o in pos)),
                 key=lambda r: -pos[r][1])
column_x, column_top = 312, max(pos[r][1] for r in crowded) + 18 if crowded else 0
for rank in sorted(pos):
    x, y = pos[rank]
    if rank in crowded:
        k = crowded.index(rank)
        lx, ly = column_x, column_top - 20 * k
        ax.plot([x, lx], [y, ly], color=SERVICE, lw=0.6, zorder=3, solid_capstyle="round")
        ax.scatter(x, y, s=16, c=SERVICE, zorder=4, edgecolors="white", linewidths=0.6)
    else:
        lx, ly = x, y
    ax.scatter(lx, ly, s=120, c=SERVICE, zorder=5, edgecolors="white", linewidths=1.0,
               clip_on=False)
    ax.text(lx, ly, str(rank), color="white", fontsize=6.5, fontweight="bold",
            ha="center", va="center", zorder=6, clip_on=False)

# Orientation towns, muted, with a white halo so dots never cut the words.
xs = [c["x"] for c in pack["communities"]]
ys = [c["y"] for c in pack["communities"]]
lon = [c["lon"] for c in pack["communities"]]
lat = [c["lat"] for c in pack["communities"]]
kx = (max(xs) - min(xs)) / (max(lon) - min(lon))
ky = (max(ys) - min(ys)) / (min(lat) - max(lat))
bx = min(xs) - kx * min(lon)
by = min(ys) - ky * max(lat)
for name, la, lo in (("Darwin", -12.46, 130.84), ("Katherine", -14.47, 132.26),
                     ("Tennant Creek", -19.65, 134.19), ("Alice Springs", -23.70, 133.88)):
    x, y = bx + kx * lo, by + ky * la
    ax.plot(x, -y, marker="s", ms=2.6, color=INK_MUTED, zorder=6)
    ax.text(x + 5, -y, name, fontsize=6.8, color=INK_MUTED, va="center", zorder=6,
            path_effects=HALO)

ax.set_xlim(8, 330)
ax.set_ylim(-472, -10)
ax.set_aspect("equal")
ax.axis("off")

counts = {g: sum(1 for p in pack["priority"] if p["g"] == g) for g in groups}
legend = [
    Line2D([], [], marker="o", ls="", ms=4.5, mfc=SERVICE, mec="white",
           label=f"Service gap ({counts['service']})\na published verdict says\n"
                 "telehealth or calls fail"),
    Line2D([], [], marker="o", ls="", ms=4.5, mfc=CHECK, mec="white",
           label=f"Check the evidence ({counts['check']})\nverify, measure or\npower the link"),
    Line2D([], [], marker="o", ls="", ms=4.5, mfc=MONITOR, mec="white",
           label=f"Monitor ({counts['monitor']})"),
    Patch(facecolor=OCHRE, alpha=CLAIM_ALPHA * 2, lw=0,
          label="Shaded: a carrier's map\nclaims 4G; darker where\nmore carriers claim it"),
]
fig.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.67, 0.80), frameon=False,
           fontsize=7.5, labelcolor=INK, handletextpad=0.5, labelspacing=1.1, borderaxespad=0)
fig.text(0.67, 0.36, "Numbers: the top ten of the\nservice-gap group (Finding 4).", fontsize=7.2,
         color=INK_MUTED, va="top")
fig.text(0.02, 0.965, "Where to act first", fontsize=12, fontweight="bold", color=INK, va="top")
fig.text(0.02, 0.918, "11 of the 20 service-gap communities are in East Arnhem and Big Rivers.",
         fontsize=8.5, color=INK_MUTED, va="top")
fig.text(0.02, 0.015, "Source: Crosscheck pipeline (data pack 2026-09-27); ACCC MIR 2025, "
         "NT Government, ACMA RRL, BushTel, National Audit.", fontsize=6.3, color=INK_MUTED)
fig.savefig(OUT, dpi=300, facecolor="white")
print(OUT, "crowded:", crowded)
