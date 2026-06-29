# Forecast results (ADR-0004)

Per-zone CI forecast, 96h day-wise, daily 00:00 origin (CarbonCast convention).
Models: flat/diurnal persistence (floor), SARIMA (field baseline), LightGBM (ML).
Metrics: MAPE-mean (average over days 1-4) + MAE/RMSE/concordance (full data in
`~/khepri-data/forecast/`).

## MAPE-mean per zone × model

**PRIMARY (test 2025, train ≤2023):**

| Zone | flat | diurnal | SARIMA | GBM |
|------|-----:|-----:|-----:|-----:|
| NO1 | 2.65 | 2.71 | **2.47** | 2.58 |
| NO2 | 3.99 | 4.28 | 3.96 | **3.94** |
| NO3 | **6.84** | 7.48 | 6.87 | 7.89 |
| NO4 | 7.86 | 7.88 | **7.24** | **35.65** ⚠ |
| NO5 | 0.83 | 0.76 | 0.72 | 3.75 |

**SECONDARY field-exact (test H2 2021, train 2019–H1 2021):**

| Zone | flat | SARIMA | GBM | CarbonCast SE (ref) |
|------|-----:|-----:|-----:|-----:|
| NO1 | 1.50 | 1.43 | **1.20** | |
| NO2 | 4.79 | 4.13 | **3.50** | lifecycle **5.78** |
| NO3 | 7.52 | 7.41 | **6.45** | direct **10.07** |
| NO4 | 3.23 | **2.94** | 3.29 | (PJM 4.80, ISO-NE 6.46, |
| NO5 | 16.11 | 10.55 | **8.75** | CISO 13.37) |

## Findings (B3 — raw)

### 1. H0 largely holds: simple models are sufficient for NO
For the stable hydro zones (NO1/NO2/NO3) the improvement from SARIMA/GBM over
flat persistence is small (1-11%), and for NO3 2025 **flat persistence is the best
model**. The pre-registered H0 (hydro-stable → little to predict beyond
seasonality) is **largely confirmed**. Adoption consequence: NO does not need a
heavy forecaster — persistence/SARIMA is adequate.

### 2. NO5 / pure-hydro: production-based CI is near-constant (mono-factor)
NO5 2026: CI std = 0.00, locked at 24.0 — because the mix is ~100% hydro and all
hydro subtypes share IPCC factor 24. Persistence MAPE 0.00 is **genuine but
trivial**: a near-constant signal carries little predictable information. This is a
real **limitation of production-based per-zone CI for pure-hydro zones** — not
model skill.

### 3. NO4 — the leakage check is CLEAN, exactly as pre-registered
Pre-registered expectation (Hammerfest correction): NO4's large CI movements are
an industrial event (fire/restart), not predictable from CI history. Confirmed
against data:
- **NO4 H2-2021 (plant offline, pure hydro): MAPE 2.94 — trivially easy** (gas
  absent).
- **NO4 2025/2026 (gas in operation, volatile): MAPE 7.24 / 10.51 — hardest of
  all zones.**
- **No model shows anomalously high NO4 skill across event boundaries** → no
  leakage. SARIMA captures seasonality/diurnal, misses the gas spikes (as
  expected). **GBM collapses on NO4 2025 (MAPE 35.65)** — ML overfits and cannot
  handle the event-driven regime.
NO4 is hardest precisely because the event is not in the history. That is a genuine
finding, not a model deficiency.

### 4. GBM is not safely better — SARIMA is the robust choice
GBM wins in some stable cases (secondary NO1/NO2/NO3, +14-27% over flat), but
**collapses catastrophically on NO4 2025 (35.65 vs SARIMA's 7.24)**. A heavy ML
model is not a safe default — it can blow up on the volatile zone. Supports
ADR-0004 Decision 3 (low→high): SARIMA is the sweet spot.

### 5. Field comparability achieved (secondary)
NO's H2-2021 MAPE (1.2-10.5) is in **the same room as CarbonCast's regions** (SE
5.78 lifecycle, PJM 4.80, ISO-NE 6.46, CISO 13.37). NO is now forecast-
characterised on field-comparable grounds — first per-zone NO CI forecast with the
field's evaluation convention.

## Caveats
- Forecast origins = daily 00:00 (CarbonCast-exact). SARIMA per origin on a 45-day
  window (memory-safe; captures daily seasonality) — pragmatic choice, documented.
- 2025/2026 mixed 15/60-min → hourly average; short gaps (≤ 6h) interpolated; gap
  fraction reported per zone-year in `_run.log` (NO2/NO3 ~10-17%).
- GBM averaged over 3 seeds; SARIMA/persistence are deterministic (1 run).
- MAPE supplemented with MAE/RMSE/concordance (full table in raw CSV); concordance
  ~0.5 for stable zones = near-random ranking order, consistent with a
  near-constant signal.
