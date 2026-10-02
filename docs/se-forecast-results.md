# SE per-zone CI forecast results

Date: 2026-06-29
ADR: ADR-0008 (SE forecast method), ADR-0004 (method source)
Method: forecast.py unchanged — SARIMA + persistence floor + GBM
Split: train 2022-2023, test 2025 (validation 2024 held internal)
Zones: SE1, SE2, SE3, SE4 | Horizon: 96h day-wise

## Correction 2026-10-01 (version 1.5)

Two departures from ADR-0008 (which inherits ADR-0004's method) in the runs reported further down
were found while preparing the journal revision (Environmental Data Science, EDS-2026-0107). The code
is corrected in `src/khepri/forecast.py` (version 1.5; dated addendum in ADR-0008). The tables in this
block are the corrected runs, with the version 1.4 GBM figures beside them. The text below the block is
the version 1.4 text, kept unchanged for the record.

1. **2024 was not loaded as history.** `eval_split` loaded the training years and the test year only
   (2022, 2023, 2025). The 2024 gap was filled forward with the last value, so the first 45 origins of
   2025 saw a constant in their 45-day SARIMA window and in the GBM lags. Corrected: every year
   2022–2025 is loaded. SARIMA mean MAPE moves from 11.65 / 10.48 / 4.55 / 20.19 to
   11.64 / 10.42 / 4.54 / 20.19, and day-1 MAPE from 7.85 / 6.75 / 3.38 / 16.06 to
   7.81 / 6.69 / 3.37 / 16.07 (SE1 / SE2 / SE3 / SE4).
2. **The GBM was trained on 34 daily origins, not 365** (28 November–31 December 2023), as in the
   Norwegian primary split. The targets of the last four reached up to 96 h past `train_end`. Here they
   fell in the forward-filled 2024 stretch. Corrected: the last 365 daily origins whose 96-h targets all
   lie at or before `train_end` (28 December 2022 → 27 December 2023).

SARIMA's fallback to diurnal persistence occurred at none of the origins in the version 1.4 runs.
From version 1.5 a fallback is logged, flagged per row and counted instead of being silent.

**What this changes in the sections below.**
- *H0 outcome*: "SARIMA beats GBM in all four zones" and the GBM degradation +1.0 / +1.5 / +4.3 /
  +3.6 pp are the 34-origin training. On the corrected runs the GBM has lower mean MAPE than SARIMA in
  all four Swedish zones: −0.88 (SE1), −0.85 (SE2), −0.02 (SE3) and −2.64 (SE4) percentage points.
  ADR-0004 registered no numerical threshold for "meaningfully", so the outcome is reported as
  direction and size per zone.
- *Concordance*: SARIMA's SE1/SE2 figures are unchanged (0.581 / 0.596). The corrected GBM ranks hours
  better (0.622 / 0.624), so the direction-tracking weakness is reduced, not removed.
- *2024-gap verification*: superseded by item 1. The gap was in the input and is now loaded.

### Mean MAPE over days 1–4 (%), test 2025

| Zone | flat | diurnal | SARIMA | GBM (corrected) | GBM (v1.4, as published) | GBM − SARIMA (pp) |
|------|-----:|-----:|-----:|-----:|-----:|-----:|
| SE1 | 12.28 | 12.90 | 11.64 | 10.76 | 12.66 | -0.88 |
| SE2 | 10.89 | 11.85 | 10.42 | 9.57 | 11.95 | -0.85 |
| SE3 | 7.87 | 4.96 | 4.54 | 4.53 | 8.88 | -0.02 |
| SE4 | 25.51 | 21.74 | 20.19 | 17.54 | 23.77 | -2.64 |

Day by day, MAPE (%):

| Zone | Model | Day 1 | Day 2 | Day 3 | Day 4 |
|------|-------|-----:|-----:|-----:|-----:|
| SE1 | flat | 8.10 | 12.41 | 14.12 | 14.50 |
| SE1 | diurnal | 10.63 | 12.77 | 14.03 | 14.19 |
| SE1 | SARIMA | 7.81 | 11.88 | 13.26 | 13.61 |
| SE1 | GBM (corrected) | 8.19 | 11.30 | 11.71 | 11.83 |
| SE1 | GBM (v1.4) | 9.69 | 13.17 | 13.89 | 13.90 |
| SE2 | flat | 7.02 | 10.92 | 12.56 | 13.05 |
| SE2 | diurnal | 9.94 | 11.56 | 12.90 | 12.99 |
| SE2 | SARIMA | 6.69 | 10.65 | 11.90 | 12.42 |
| SE2 | GBM (corrected) | 7.17 | 9.88 | 10.52 | 10.71 |
| SE2 | GBM (v1.4) | 9.43 | 13.05 | 12.73 | 12.60 |
| SE3 | flat | 6.98 | 7.83 | 8.24 | 8.41 |
| SE3 | diurnal | 3.99 | 4.95 | 5.38 | 5.51 |
| SE3 | SARIMA | 3.37 | 4.61 | 4.98 | 5.21 |
| SE3 | GBM (corrected) | 3.79 | 4.58 | 4.84 | 4.89 |
| SE3 | GBM (v1.4) | 6.84 | 9.45 | 9.61 | 9.62 |
| SE4 | flat | 22.86 | 25.54 | 26.47 | 27.17 |
| SE4 | diurnal | 17.94 | 21.58 | 23.45 | 23.99 |
| SE4 | SARIMA | 16.07 | 20.34 | 21.87 | 22.46 |
| SE4 | GBM (corrected) | 15.03 | 18.23 | 18.26 | 18.66 |
| SE4 | GBM (v1.4) | 21.64 | 25.31 | 24.30 | 23.83 |

Concordance, mean over days 1–4 (day 1 in parentheses):

| Zone | SARIMA | GBM (corrected) | GBM (v1.4, as published) |
|------|-----:|-----:|-----:|
| SE1 | 0.581 (0.610) | 0.622 (0.658) | 0.560 (0.597) |
| SE2 | 0.596 (0.626) | 0.624 (0.653) | 0.587 (0.613) |
| SE3 | 0.843 (0.847) | 0.856 (0.860) | 0.761 (0.786) |
| SE4 | 0.822 (0.828) | 0.825 (0.835) | 0.680 (0.697) |

Data: `~/khepri-data/eds-revisjon/_data/s2-j2b/` (flat, diurnal, SARIMA) and
`~/khepri-data/eds-revisjon/_data/s2-ren/` (GBM). The version 1.5 code reproduces SE1 exactly
(`~/khepri-data/eds-revisjon/_data/s3-v15/`, every row identical).

---

*Version 1.4 text follows, unchanged.*

## SARIMA — mean MAPE over days 1-4 (primary metric)

| Zone | MAPE (%) | MAE (gCO2eq/kWh) | RMSE  | Concordance |
|------|----------|-----------------|-------|-------------|
| SE1  | 11.65    | 2.285           | 2.535 | 0.581       |
| SE2  | 10.48    | 2.064           | 2.271 | 0.596       |
| SE3  |  4.55    | 0.683           | 0.799 | 0.842       |
| SE4  | 20.19    | 3.979           | 4.997 | 0.822       |

## SARIMA — day-1 MAPE

| Zone | Day 1 (%) | Day 2 (%) | Day 3 (%) | Day 4 (%) |
|------|-----------|-----------|-----------|-----------|
| SE1  |  7.85     | 11.88     | 13.26     | 13.60     |
| SE2  |  6.75     | 10.70     | 11.96     | 12.50     |
| SE3  |  3.38     |  4.62     |  4.99     |  5.22     |
| SE4  | 16.06     | 20.35     | 21.87     | 22.47     |

## H0 outcome (pre-registered ADR-0008 §4)

H0: heavy ML (GBM) does not meaningfully beat SARIMA/persistence.
**H0 NOT REJECTED.** SARIMA beats GBM in all four zones.

GBM degradation vs SARIMA: SE1 +1.0pp, SE2 +1.5pp, SE3 +4.3pp, SE4 +3.6pp.
Escalation to GBM not warranted. Simple baselines are sufficient for SE.

## CarbonCast comparison (ADR-0008 §3)

Reference: CarbonCast SE-AGGREGATE day-1 = 8.87% MAPE (EnsembleCI Table 2, arXiv
2505.01959v1, HTML-verified). CAVEAT: per-zone vs aggregate — not apples-to-apples.

Simple per-zone SARIMA baselines achieve day-1 MAPE of 3.38-7.85% on SE1/SE2/SE3,
of comparable order of magnitude to CarbonCast SE-aggregate day-1 = 8.87% (EnsembleCI
Table 2-verified). SE4 is 16.06%, reflecting documented structural drift (ADR-0007).
Comparison is per-zone vs country-aggregate — not directly equivalent.

## Positioning

First per-bidding-zone SE1-SE4 CI forecast (granularity novelty).
CarbonCast and EnsembleCI cover SE as country aggregate only (verified).
NEVER "first SE CI forecast" (aggregate exists).
SE cross-zone spread 5.6-8.0 gCO2eq/kWh vs NO 16.7-30.7 (ADR-0006).

## SE1/SE2 concordance limitation — direction tracking

SE1 concordance 0.581, SE2 concordance 0.596. These are barely above a coin flip (0.5).

The forecast gets the CI LEVEL roughly right (SE1 day-1 MAPE 7.85%, SE2 6.75% — acceptable),
but it tracks the DIRECTION of hourly CI change poorly in these two zones. A MAPE-only reading
misses this: MAPE measures level accuracy, concordance measures whether the forecast correctly
ranks higher-vs-lower CI periods relative to each other.

This is a real limitation for carbon-aware scheduling, whose job is timing — knowing WHEN CI is
low enough to defer a workload. A tool that predicts the right average but gets the direction
wrong provides limited scheduling value for SE1/SE2. ADR-0004 includes concordance precisely
to surface this gap.

Contrast: SE3 concordance 0.842, SE4 concordance 0.822. Direction tracking is strong in both;
scheduling use-cases are better supported there.

## B3 limitations

- Training window: 2 years (2022-2023). Annual seasonality weakly estimable.
- SE4 high MAPE (20.19%) reflects structural volatility/drift (ADR-0007), not method failure.
- SE1/SE2 low concordance (0.581/0.596): see section above.
- Full results and raw data: ~/khepri-data/se/forecast/

## 2024-gap verification

The evaluation series loads 2022, 2023, 2025 — 2024 is the validation year, absent from the
hourly_ci hist series. The SARIMA 45-day apply() window (WIN=45d) therefore reaches into
absent 2024 data for origins Jan 1 through Feb 14 2025 (45 origins). Those windows are served
by bfill-interpolated values (Dec 31 2023 carried forward).

Verified from raw CSV (se_forecast_results_raw.csv, n=361 origins per zone, row order =
chronological). Comparison: gap-period origins (Jan 1 - Feb 14, n=45) vs clean-window origins
(Feb 15 - Dec 27, n=316), SARIMA day-1 MAPE:

| Zone | Gap-period MAPE | Rest MAPE | Delta   | t-stat |
|------|----------------|-----------|---------|--------|
| SE1  | 9.72%          | 7.58%     | +2.14pp | 2.14   |
| SE2  | 7.78%          | 6.60%     | +1.18pp | 1.69   |
| SE3  | 2.53%          | 3.50%     | -0.97pp | -3.56  |
| SE4  | 13.42%         | 16.43%    | -3.02pp | -2.32  |

Verdict: gap is benign. SE1 shows marginal elevation (+2.14pp, t=2.14) but the effect is
0.40x the within-group std (SE1 daily MAPE CV=70%); SE2 is below significance (t=1.69).
SE3 and SE4 show the opposite direction — early January 2025 was simply easier to forecast
in those zones (stable nuclear signal in SE3; calmer early-Jan CI in SE4 before the high-
volatility summer months). No exclusion or flagging of early-2025 results is warranted.
This was verified from numbers, not assumed.
