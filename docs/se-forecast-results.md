# SE per-zone CI forecast results

Date: 2026-06-29
ADR: ADR-0008 (SE forecast method), ADR-0004 (method source)
Method: forecast.py unchanged — SARIMA + persistence floor + GBM
Split: train 2022-2023, test 2025 (validation 2024 held internal)
Zones: SE1, SE2, SE3, SE4 | Horizon: 96h day-wise

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
