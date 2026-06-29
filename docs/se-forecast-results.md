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

## B3 limitations

- Training window: 2 years (2022-2023). Annual seasonality weakly estimable.
- SE4 high MAPE (20.19%) reflects structural volatility/drift (ADR-0007), not method failure.
- Full results and raw data: ~/khepri-data/se/forecast/
