"""Report figure: what the best available connection supports, per service (Crosscheck, DIC005).

Counts come from the pipeline's verdict table (data/out/tables/verdict_counts.csv), the same
numbers as Finding 2. Static PNG for print: every segment carries its count, so colour is never
the only cue.
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
TABLE = HERE.parents[2] / "data/out/tables/verdict_counts.csv"
OUT = HERE / "Crosscheck_figure_services.png"

VERDICTS = [("works", "Works", "#15803D", "white"), ("degraded", "Degraded", "#E3A21A", "#18181B"),
            ("fails", "Fails", "#B42318", "white"), ("nodata", "No data", "#A1A1AA", "#18181B")]
SERVICES = [("Telehealth video", "Telehealth video"), ("School video meeting", "Online school lesson"),
            ("myGov and banking", "Government websites"), ("Voice and SMS", "Voice calls and SMS")]
INK, INK_MUTED = "#18181B", "#52525B"
plt.rcParams["font.family"] = ["Calibri", "Arial", "DejaVu Sans"]

counts = {}
with TABLE.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        counts[(row["service"], row["verdict"])] = int(row["communities"])

fig, ax = plt.subplots(figsize=(6.3, 2.55), dpi=300)
for i, (key, label) in enumerate(SERVICES):
    y = len(SERVICES) - 1 - i
    left = 0
    for verdict, _, color, text_color in VERDICTS:
        n = counts.get((key, verdict), 0)
        if not n:
            continue
        ax.barh(y, n, left=left, height=0.5, color=color, edgecolor="white", linewidth=1.5)
        if n >= 4:
            ax.text(left + n / 2, y, str(n), ha="center", va="center", fontsize=8,
                    color=text_color, fontweight="bold")
        else:  # too narrow for a label inside: put it just above the bar
            ax.text(left + n / 2, y + 0.28, str(n), ha="center", va="bottom", fontsize=7, color=INK)
        left += n
    ax.text(-1.5, y, label, ha="right", va="center", fontsize=8.5, color=INK)

ax.set_xlim(0, 96); ax.set_ylim(-0.5, len(SERVICES) - 0.3)
ax.set_xticks([0, 24, 48, 72, 96]); ax.tick_params(axis="x", labelsize=7, colors=INK_MUTED, length=0)
ax.set_yticks([])
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#E4E4E7")
ax.set_xlabel("Communities (of 96)", fontsize=7.5, color=INK_MUTED)

fig.legend(handles=[Patch(facecolor=c, label=l) for _, l, c, _ in VERDICTS], loc="upper left",
           bbox_to_anchor=(0.30, 0.86), ncol=4, frameon=False, fontsize=7.5, handlelength=1.1,
           columnspacing=1.2, labelcolor=INK)
fig.text(0.02, 0.975, "What the best available connection supports", fontsize=11.5, fontweight="bold",
         color=INK, va="top")
fig.text(0.02, 0.9, "Only 1 of 96 communities has a path known to meet telehealth's 100 ms limit.",
         fontsize=8.3, color=INK_MUTED, va="top")
fig.text(0.02, 0.02, "\"No data\": no health centre or school recorded. Source: Crosscheck verdict table "
         "(data pack 2026-09-27).", fontsize=6.3, color=INK_MUTED)
fig.subplots_adjust(left=0.30, right=0.97, top=0.72, bottom=0.26)
fig.savefig(OUT, dpi=300, facecolor="white")
print(OUT)
