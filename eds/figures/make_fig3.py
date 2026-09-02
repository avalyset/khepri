#!/usr/bin/env python3
"""Regenerate fig3.pdf: forecast MAPE by zone and model.

Data source, read directly from the archived raw results of the 2026-06-29 runs:
  ~/khepri-data/forecast/primaer_2025_raw.csv        (NO primary split, panel a)
  ~/khepri-data/se/forecast/se_forecast_results_raw.csv (SE split, panel b)

Panel (a): Norway, mean MAPE over days 1-4, test 2025, four models per zone.
Panel (b): Sweden, day-1 SARIMA MAPE as bars; the GBM degradation printed above
each bar is the mean over days 1-4, not day 1 -- the two horizons are different
quantities and each label says which one it is.

Output geometry matches the figure it replaces: 513.071 x 204.094 pt.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PT = 1.0 / 72.0
FIGSIZE = (513.071 * PT, 204.094 * PT)

NO_RAW = os.path.expanduser("~/khepri-data/forecast/primaer_2025_raw.csv")
SE_RAW = os.path.expanduser("~/khepri-data/se/forecast/se_forecast_results_raw.csv")

NO_ZONES = ["NO1", "NO2", "NO3", "NO4", "NO5"]
SE_ZONES = ["SE1", "SE2", "SE3", "SE4"]
MODELS = ["flat", "diurnal", "SARIMA", "GBM"]

# fill, hatch  -- greyscale, distinguishable in print
STYLE = {"flat": ("0.35", ""), "diurnal": ("0.55", "//"),
         "SARIMA": ("0.75", ".."), "GBM": ("0.88", "xx")}

no = pd.read_csv(NO_RAW)
se = pd.read_csv(SE_RAW)

# panel (a): mean over days 1-4
no_mean = no.groupby(["zone", "model"])["mape"].mean().unstack()
# panel (b): day-1 SARIMA bars, and the days 1-4 mean degradation GBM - SARIMA
se_d1 = se[se.day == 1].groupby(["zone", "model"])["mape"].mean().unstack()
se_all = se.groupby(["zone", "model"])["mape"].mean().unstack()
se_deg = se_all["GBM"] - se_all["SARIMA"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 7.0, "axes.labelsize": 7.0, "axes.titlesize": 7.5,
    "xtick.labelsize": 7.0, "ytick.labelsize": 7.0, "legend.fontsize": 6.5,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "hatch.linewidth": 0.4, "pdf.fonttype": 42,
})

fig = plt.figure(figsize=FIGSIZE)
gs = fig.add_gridspec(2, 2, height_ratios=[1, 4], width_ratios=[1, 1],
                      hspace=0.10, wspace=0.24)
ax_hi = fig.add_subplot(gs[0, 0])          # panel (a) upper segment (broken axis)
ax_lo = fig.add_subplot(gs[1, 0])          # panel (a) lower segment
axb = fig.add_subplot(gs[:, 1])            # panel (b)

# ---------------- panel (a) ----------------
x = np.arange(len(NO_ZONES))
w = 0.20
for i, m in enumerate(MODELS):
    vals = [no_mean.loc[z, m] for z in NO_ZONES]
    off = (i - 1.5) * w
    for ax in (ax_hi, ax_lo):
        ax.bar(x + off, vals, w, facecolor=STYLE[m][0], hatch=STYLE[m][1],
               edgecolor="black", linewidth=0.5, label=m if ax is ax_lo else None)

ax_lo.set_ylim(0, 12)
ax_hi.set_ylim(34, 36.6)
ax_hi.set_yticks([34, 36])
for ax in (ax_hi, ax_lo):
    ax.set_xlim(-0.55, len(NO_ZONES) - 0.45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
ax_hi.spines["bottom"].set_visible(False)
ax_hi.tick_params(axis="x", bottom=False, labelbottom=False)
ax_lo.set_xticks(x)
ax_lo.set_xticklabels(NO_ZONES)

# axis-break marks
d = 0.012
for ax, ys in ((ax_hi, (-0.02,)), (ax_lo, (1.0,))):
    for yy in ys:
        ax.plot((-d, +d), (yy - d * 4, yy + d * 4), transform=ax.transAxes,
                color="k", clip_on=False, lw=0.6)

ax_lo.set_ylabel("MAPE (%)")
ax_lo.yaxis.set_label_coords(-0.105, 0.62)
ax_hi.set_title("(a) Norway: mean MAPE, days 1--4 (test 2025)".replace("--", "–"))

# NO4 GBM value label, on the upper segment
no4_gbm = no_mean.loc["NO4", "GBM"]
ax_hi.text(x[3] + 1.5 * w, no4_gbm + 0.25, "%.2f" % no4_gbm,
           ha="center", va="bottom", fontsize=6.4)
# annotation placed over empty space above NO5, clear of every bar
ax_lo.text(x[4] + 0.42, 10.6, "GBM collapse\non NO4", fontsize=6.2, style="italic",
           ha="right", va="top", linespacing=1.4)

# legend over the short NO1/NO2 bars, clear of the tall NO4 GBM bar
ax_lo.legend(loc="upper left", ncol=2, frameon=False, handlelength=1.5,
             handleheight=1.0, columnspacing=1.0, borderaxespad=0.3)

# ---------------- panel (b) ----------------
xb = np.arange(len(SE_ZONES))
bars = [se_d1.loc[z, "SARIMA"] for z in SE_ZONES]
axb.bar(xb, bars, 0.55, facecolor="0.62", edgecolor="black", linewidth=0.6)
axb.set_xticks(xb)
axb.set_xticklabels(SE_ZONES)
axb.set_ylim(0, 20)
axb.set_yticks(range(0, 21, 2))
axb.set_ylabel("day-1 SARIMA MAPE (%)")
axb.set_title("(b) Sweden: day-1 SARIMA MAPE")
axb.spines["top"].set_visible(False)
axb.spines["right"].set_visible(False)

for xi, z in zip(xb, SE_ZONES):
    v = se_d1.loc[z, "SARIMA"]
    axb.text(xi, v + 0.30, "%.2f" % v, ha="center", va="bottom", fontsize=6.6)
    # the degradation is the days 1-4 mean, a different horizon from the bar
    axb.text(xi, v + 1.65, "GBM d1–4\n$+$%.1f pp" % se_deg[z], ha="center",
             va="bottom", fontsize=5.9, style="italic", linespacing=1.35)

fig.subplots_adjust(left=0.075, right=0.985, top=0.90, bottom=0.115)
fig.savefig("fig3.pdf", format="pdf")
print("skrev fig3.pdf")
print("panel (a) dag 1-4:\n", no_mean[MODELS].round(2).to_string())
print("panel (b) day-1 SARIMA:", {z: round(se_d1.loc[z, "SARIMA"], 2) for z in SE_ZONES})
print("panel (b) degradering d1-4:", {z: round(se_deg[z], 1) for z in SE_ZONES})
