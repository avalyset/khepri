# ADR-0004: Forecast method for per-zone CI

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0001, ADR-0002, ADR-0003

## Context
The adoption layer (carbon-aware scheduling) needs a multi-day per-zone CI forecast.
The field's evaluation convention is drawn from primary sources (CarbonCast BuildSys
2022, EnsembleCI arXiv 2505.01959, LiteCast arXiv 2511.06187) and governs Decisions
2 and 4 — we match the field for comparability, not our own guessing. NO is absent
from all three (file-verified) — this is the contribution.

## Pre-registered decisions (locked before result)

### 1. Forecast target
- Per zone (NO1–NO5), CI (gCO2eq/kWh, ADR-0001+0002 method), horizon 96 hours
  day-wise (day-1: 0-24h ... day-4: 72-96h), hourly resolution. Matches
  CarbonCast/EnsembleCI convention exactly.
- Sliding window (24h in → next 24h), mean of 3 runs for stochastic models
  (CarbonCast §4.1 convention). Deterministic models (persistence, SARIMA): 1 run.

### 2. Baselines (the field's actual benchmark, not guessing)
- Primary baseline to beat: **SARIMA** (Seasonal-ARIMA) — CarbonCast's own
  SOTA baseline (SOTA₁).
- Persistence included as floor (LiteCast precedent), not as primary baseline.
- If CarbonCast implementation is runnable on NO data: report against it as
  de-facto SOTA. If not (academic repo, frozen main — per recon): SARIMA +
  persistence is an honest benchmark, and the absence of a runnable CarbonCast-NO
  is documented.
- B3: a forecast that does not beat SARIMA is not a contribution; reported straight.

### 3. Model approach
- Complexity low→high, locked order: SARIMA baseline first, then ML (gradient
  boosting, cf. EnsembleCI LightGBM/CatBoost) only if the simple model is
  documented as insufficient. Do not jump to a heavy model before the simpler one
  has been tried and reported.
- Predict generation-per-type→derive CI, or CI directly: both permitted; report
  which and why.

### 4. Metrics (anchored in the field + low-CI supplement)
- Primary: **MAPE** (mean/median/90th/95th percentile) — the field's standard,
  directly comparable with CarbonCast's SE figures (5.78% lifecycle / 10.07%
  direct), the nearest published low-CI hydropower parallel.
- Supplement (pre-registered, not post-hoc): **MAE + RMSE**, because Norwegian CI
  is low (~20-40) and MAPE is documented as unstable in low/volatile regimes
  (LiteCast: up to 49% for Denmark). Rationale anchored in LiteCast, not guessing.
- Ranking metric (**concordance index**, LiteCast): reported for scheduling
  relevance (getting the order of clean/dirty hours right matters more for adoption
  than absolute error).
- Per zone, per day-horizon (days 1-4).

### 5. Split (DOUBLE: drift-aware primary + field-exact secondary)

**PRIMARY (drift-aware):** train 2021-2023, validate 2024, test 2025; H1-2026
untouched as final holdout. Report forecast skill SEPARATELY for drifting zones
(NO4/NO5) vs stable (NO1/NO2/NO3). Explicitly test whether the model captures
gas-driven variation or just seasonality. Rationale: ADR-0003 showed NO4/NO5
structural drift post-2021; a pre-drift test would evaluate a non-representative
regime.

**SECONDARY (field-exact comparability anchor):** train 2019–H1 2021, test H2
2021 — replicates CarbonCast/EnsembleCI exactly for one directly comparable MAPE
figure against their SE figures (5.78 lifecycle / 10.07 direct). Clearly labelled
SECONDARY/comparability. NB (verified against data, not assumed): NO4 H2-2021 is
within the Hammerfest LNG outage — the plant was offline after the Sept-2020 fire,
restart June 2022 — so NO4 gas was ~2 MW in 2021 (vs ~194 MW in 2019). This is
NOT "pre-gas": gas existed 2019-2020. The H2-2021 figure is for comparability, not
drift evaluation, and NO4 is in an anomalously low-gas window (outage), not a
normal regime.

Comparability is preserved on **metric/horizon/format** (MAPE, 96h day-wise,
percentiles), not on test period. No leakage: the test set is not touched before
final evaluation.

### 6. Null hypothesis (explicit)
- H0: a simple model does not meaningfully beat the SARIMA baseline for NO zones
  (hydro-stable → little to predict beyond seasonality).
- For the drifting zones (NO4/NO5) secondary H0: no model captures gas-driven drift
  better than seasonality.
- A negative result (seasonality/SARIMA is sufficient) is a genuine finding with
  consequences: no heavy model is needed in the adoption layer.

## Consequences
- Model beats baseline: per-zone CI forecast has operational scheduling value; goes
  into the adoption layer.
- Does not beat: SARIMA/seasonality is sufficient, simplifying adoption (reported
  straight).
- NO becomes the first published per-zone CI forecast with the field's evaluation
  convention (CarbonCast-comparable), filling the file-verified gap.

## Alternatives considered
- 48h horizon (earlier guess): rejected — the field uses 96h; comparability requires
  a match.
- MAPE only: rejected — unstable in the low-CI regime (LiteCast-documented);
  supplemented with MAE/RMSE/ranking.
- Persistence baseline only: rejected — not the field's benchmark; SARIMA is the
  SOTA floor.
- H2 2021 test as the ONLY test (exact field match): rejected — does not capture
  the drift regime our own ADR-0003 identified; used as SECONDARY comparability
  anchor alongside the primary drift-aware split with separate drift-zone reporting.
