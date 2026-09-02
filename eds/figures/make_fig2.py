#!/usr/bin/env python3
"""Regenerate fig2.pdf: annual per-zone CI drift, Norway and Sweden.

Data source: docs/drift-results-2021-2025.md (ADR-0003) and
docs/se-drift-results-2022-2025.md (ADR-0007). Values are transcribed from
those tables, which are themselves produced by drift.py over ci.py.

Annotations report the NO4 fossil-gas share per year, taken from the
"NO4 - driver measured" table in docs/drift-results-2021-2025.md. ENTSO-E
reports generation per production type and not per plant, so no annotation
attributes the change to any individual facility.

Output geometry matches the figure it replaces: 513.071 x 192.756 pt.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PT = 1.0 / 72.0
FIGSIZE = (513.071 * PT, 192.756 * PT)

# docs/drift-results-2021-2025.md, "Annual CI per zone (gCO2eq/kWh)"
NO_YEARS = [2021, 2022, 2023, 2024, 2025]
NO = {
    "NO1": [23.63, 23.31, 23.48, 23.45, 23.31],
    "NO2": [23.10, 22.58, 23.52, 23.61, 23.85],
    "NO3": [21.65, 20.95, 20.89, 20.75, 21.46],
    "NO4": [23.34, 37.67, 45.08, 51.46, 39.65],
    "NO5": [34.90, 28.75, 24.93, 25.00, 24.46],
}

# docs/se-drift-results-2022-2025.md, "Annual CI per zone (gCO2eq/kWh)"
SE_YEARS = [2022, 2023, 2024, 2025]
SE = {
    "SE1": [21.46, 20.99, 20.01, 20.63],
    "SE2": [20.60, 20.25, 19.80, 20.11],
    "SE3": [13.47, 14.34, 14.37, 14.53],
    "SE4": [15.12, 16.21, 16.70, 17.42],
}

# marker, linestyle, greyscale level
STYLE = {
    "NO1": ("o", "-", "0.25"),
    "NO2": ("s", "--", "0.45"),
    "NO3": ("^", "-.", "0.62"),
    "NO4": ("D", ":", "0.00"),
    "NO5": ("v", "-", "0.32"),
    "SE1": ("o", "-", "0.25"),
    "SE2": ("s", "--", "0.45"),
    "SE3": ("^", "-.", "0.62"),
    "SE4": ("D", ":", "0.72"),
}

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 7.0,
        "axes.labelsize": 7.0,
        "axes.titlesize": 7.5,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "legend.fontsize": 6.5,
        "lines.linewidth": 0.9,
        "lines.markersize": 3.4,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "pdf.fonttype": 42,
    }
)

fig, (axa, axb) = plt.subplots(1, 2, figsize=FIGSIZE)

YLAB = "Carbon intensity (gCO$_2$eq/kWh)"

for zone in ["NO1", "NO2", "NO3", "NO4", "NO5"]:
    m, ls, c = STYLE[zone]
    axa.plot(NO_YEARS, NO[zone], marker=m, linestyle=ls, color=c, label=zone,
             markerfacecolor=c, markeredgecolor=c)

axa.set_title("(a) Norway, 2021--2025".replace("--", "–"))
axa.set_xlabel("Year")
axa.set_ylabel(YLAB)
axa.set_xticks(NO_YEARS)
axa.legend(loc="upper left", ncol=3, frameon=False, handlelength=2.0,
           columnspacing=1.1, borderaxespad=0.3)

# NO4 fossil-gas share per year, from the "NO4 - driver measured" table in
# docs/drift-results-2021-2025.md. Data-level only: ENTSO-E reports generation
# per production type and not per plant, so no facility is named.
# Placed in empty plot area with no leader line, to avoid crossing any series.
axa.text(2023.22, 30.2,
         "NO4 fossil-gas share\n2021: 0.07%   2024: 6.23%\n2025: 3.63%",
         fontsize=6.0, style="italic", linespacing=1.45,
         ha="left", va="bottom")

for zone in ["SE1", "SE2", "SE3", "SE4"]:
    m, ls, c = STYLE[zone]
    axb.plot(SE_YEARS, SE[zone], marker=m, linestyle=ls, color=c, label=zone,
             markerfacecolor=c, markeredgecolor=c)

axb.set_title("(b) Sweden, 2022--2025".replace("--", "–"))
axb.set_xlabel("Year")
axb.set_ylabel(YLAB)
axb.set_xticks(SE_YEARS)
# Legend below the SE1/SE2 pair, clear of every data marker.
axb.legend(loc="center left", ncol=2, frameon=False, handlelength=2.0,
           columnspacing=1.1, borderaxespad=0.4)

for ax in (axa, axb):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.06)

axa.set_ylim(18.5, 56.5)
axb.set_ylim(12.6, 22.6)

fig.tight_layout(pad=0.35, w_pad=1.6)
fig.savefig("fig2.pdf", format="pdf")
print("skrev fig2.pdf")
