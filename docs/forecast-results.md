# Forecast results (ADR-0004)

Per-zone CI forecast, 96h day-wise, daily 00:00 origin (CarbonCast convention).
Models: flat/diurnal persistence (floor), SARIMA (field baseline), LightGBM (ML).
Metrics: MAPE-mean (average over days 1-4) + MAE/RMSE/concordance (full data in
`~/khepri-data/forecast/`).

## Correction 2026-10-01 (version 1.5)

Three departures from ADR-0004 in the runs reported further down were found while preparing the
journal revision (Environmental Data Science, EDS-2026-0107). The code is corrected in
`src/khepri/forecast.py` (version 1.5; dated addendum in ADR-0004). The tables in this block are the
corrected runs, with the version 1.4 GBM figures beside them. The text below the block is the
version 1.4 text, kept unchanged for the record.

1. **The GBM was trained on 34 daily origins, not 365.** The training window was anchored at
   `test_start − 400 days` and cut at `train_end`. For the primary split that left the 34 origins
   28 November–31 December 2023, and the targets of the last four reached up to 96 h past
   `train_end` (148 targets). Corrected: the last 365 daily origins whose 96-h targets all lie at or
   before `train_end` (primary split: 28 December 2022 → 27 December 2023).
2. **Secondary split: GBM training targets inside the test period.** There the window did hold 365
   origins (1 July 2020 → 30 June 2021), but the targets of the last four — 148 hours, 1–4 July 2021 —
   fall inside the test period H2 2021. Corrected with the same boundary (27 June 2020 → 26 June 2021).
   The corrected mean MAPE differs from the published one by at most 0.18 percentage points (NO5).
3. **History.** The Norwegian primary split already loaded 2021–2025, so its flat, diurnal and SARIMA
   figures are unchanged. (The Swedish split did not load 2024; see `se-forecast-results.md`.)

SARIMA's fallback to diurnal persistence occurred at none of the origins in any of the 14 zone-splits
of the version 1.4 runs. From version 1.5 a fallback is logged, flagged per row and counted instead of
being silent.

**What this changes in the findings below.**
- Finding 1: for NO3 2025 flat persistence (6.84) is no longer the best model; the corrected GBM is
  6.58. Relative to flat persistence the corrected GBM improves mean MAPE by 12.8% (NO1), 14.3% (NO2)
  and 3.8% (NO3).
- Finding 3: the "GBM collapse on NO4 2025 (MAPE 35.65)" was the 34-origin training. The corrected GBM
  scores 10.16 on NO4, still worse than SARIMA (7.24). The NO4 conclusion — the gas-share steps are not
  predictable from the CI history — stands. The collapse does not.
- Finding 4: on the corrected runs the GBM has lower mean MAPE than SARIMA in NO1, NO2 and NO3 (by
  0.16–0.54 percentage points) and higher in NO4 (+2.92) and NO5 (+0.53). ADR-0004 registered no
  numerical threshold for "meaningfully", so the result is reported as direction and size per zone.
- Finding 5 (secondary split, field comparability): unchanged within 0.18 percentage points.
- The H1-2026 split (`slutt_h1_2026`; the "NO4 2025/2026 … 10.51" and "NO5 2026" figures) was not
  rerun for this correction.

### Primary split (test 2025, train ≤ 2023), mean MAPE over days 1–4 (%)

| Zone | flat | diurnal | SARIMA | GBM (corrected) | GBM (v1.4, as published) | GBM − SARIMA (pp) |
|------|-----:|-----:|-----:|-----:|-----:|-----:|
| NO1 | 2.65 | 2.71 | 2.47 | 2.31 | 2.58 | -0.16 |
| NO2 | 3.99 | 4.28 | 3.96 | 3.42 | 3.94 | -0.54 |
| NO3 | 6.84 | 7.48 | 6.87 | 6.58 | 7.89 | -0.29 |
| NO4 | 7.86 | 7.88 | 7.24 | 10.16 | 35.65 | +2.92 |
| NO5 | 0.83 | 0.76 | 0.72 | 1.26 | 3.75 | +0.53 |

Day by day, MAPE (%):

| Zone | Model | Day 1 | Day 2 | Day 3 | Day 4 |
|------|-------|-----:|-----:|-----:|-----:|
| NO1 | flat | 1.87 | 2.73 | 2.93 | 3.06 |
| NO1 | diurnal | 2.38 | 2.64 | 2.94 | 2.90 |
| NO1 | SARIMA | 1.81 | 2.51 | 2.73 | 2.80 |
| NO1 | GBM (corrected) | 1.82 | 2.46 | 2.50 | 2.46 |
| NO1 | GBM (v1.4) | 2.08 | 2.72 | 2.83 | 2.71 |
| NO2 | flat | 2.86 | 4.11 | 4.54 | 4.47 |
| NO2 | diurnal | 3.72 | 4.32 | 4.59 | 4.48 |
| NO2 | SARIMA | 3.04 | 4.08 | 4.40 | 4.35 |
| NO2 | GBM (corrected) | 2.87 | 3.43 | 3.66 | 3.73 |
| NO2 | GBM (v1.4) | 3.56 | 3.98 | 4.06 | 4.15 |
| NO3 | flat | 4.58 | 7.15 | 7.65 | 7.99 |
| NO3 | diurnal | 6.46 | 7.65 | 7.79 | 8.00 |
| NO3 | SARIMA | 5.00 | 7.15 | 7.50 | 7.85 |
| NO3 | GBM (corrected) | 5.06 | 6.94 | 7.13 | 7.20 |
| NO3 | GBM (v1.4) | 5.74 | 7.68 | 9.27 | 8.88 |
| NO4 | flat | 5.59 | 7.82 | 8.72 | 9.30 |
| NO4 | diurnal | 6.36 | 7.80 | 8.49 | 8.86 |
| NO4 | SARIMA | 5.37 | 7.28 | 7.92 | 8.40 |
| NO4 | GBM (corrected) | 7.55 | 9.57 | 11.21 | 12.31 |
| NO4 | GBM (v1.4) | 22.91 | 39.36 | 45.49 | 34.84 |
| NO5 | flat | 0.61 | 0.83 | 0.92 | 0.98 |
| NO5 | diurnal | 0.61 | 0.76 | 0.82 | 0.88 |
| NO5 | SARIMA | 0.52 | 0.72 | 0.79 | 0.85 |
| NO5 | GBM (corrected) | 0.84 | 1.18 | 1.38 | 1.62 |
| NO5 | GBM (v1.4) | 2.65 | 3.49 | 4.28 | 4.57 |

Concordance, mean over days 1–4 (day 1 in parentheses):

| Zone | SARIMA | GBM (corrected) | GBM (v1.4, as published) |
|------|-----:|-----:|-----:|
| NO1 | 0.577 (0.599) | 0.597 (0.632) | 0.525 (0.559) |
| NO2 | 0.535 (0.561) | 0.539 (0.586) | 0.523 (0.539) |
| NO3 | 0.519 (0.524) | 0.522 (0.567) | 0.514 (0.566) |
| NO4 | 0.559 (0.578) | 0.575 (0.581) | 0.544 (0.543) |
| NO5 | 0.569 (0.582) | 0.558 (0.566) | 0.537 (0.537) |

### Secondary split (test H2 2021, train 2019–H1 2021), mean MAPE over days 1–4 (%)

flat, diurnal and SARIMA are the version 1.4 figures (unaffected); GBM corrected as in item 2.

| Zone | flat | diurnal | SARIMA | GBM (corrected) | GBM (v1.4, as published) | GBM − SARIMA (pp) |
|------|-----:|-----:|-----:|-----:|-----:|-----:|
| NO1 | 1.50 | 1.45 | 1.43 | 1.20 | 1.20 | -0.23 |
| NO2 | 4.79 | 4.57 | 4.13 | 3.46 | 3.50 | -0.66 |
| NO3 | 7.52 | 8.07 | 7.41 | 6.47 | 6.45 | -0.94 |
| NO4 | 3.23 | 3.18 | 2.94 | 3.36 | 3.29 | +0.42 |
| NO5 | 16.11 | 11.40 | 10.55 | 8.93 | 8.75 | -1.62 |

Day by day, MAPE (%):

| Zone | Model | Day 1 | Day 2 | Day 3 | Day 4 |
|------|-------|-----:|-----:|-----:|-----:|
| NO1 | flat | 1.07 | 1.48 | 1.72 | 1.70 |
| NO1 | diurnal | 1.22 | 1.45 | 1.59 | 1.52 |
| NO1 | SARIMA | 1.03 | 1.44 | 1.63 | 1.61 |
| NO1 | GBM (corrected) | 0.99 | 1.25 | 1.28 | 1.26 |
| NO1 | GBM (v1.4) | 0.96 | 1.26 | 1.28 | 1.28 |
| NO2 | flat | 3.44 | 4.86 | 5.25 | 5.62 |
| NO2 | diurnal | 3.91 | 4.57 | 4.90 | 4.89 |
| NO2 | SARIMA | 2.88 | 4.27 | 4.54 | 4.82 |
| NO2 | GBM (corrected) | 2.77 | 3.61 | 3.71 | 3.78 |
| NO2 | GBM (v1.4) | 2.81 | 3.61 | 3.72 | 3.86 |
| NO3 | flat | 4.75 | 7.66 | 8.74 | 8.92 |
| NO3 | diurnal | 6.43 | 8.18 | 8.97 | 8.69 |
| NO3 | SARIMA | 4.99 | 7.63 | 8.55 | 8.47 |
| NO3 | GBM (corrected) | 4.73 | 6.87 | 7.19 | 7.08 |
| NO3 | GBM (v1.4) | 4.81 | 6.88 | 7.12 | 7.01 |
| NO4 | flat | 2.28 | 3.38 | 3.62 | 3.65 |
| NO4 | diurnal | 2.71 | 3.24 | 3.43 | 3.34 |
| NO4 | SARIMA | 2.13 | 3.10 | 3.27 | 3.26 |
| NO4 | GBM (corrected) | 2.32 | 3.38 | 3.81 | 3.94 |
| NO4 | GBM (v1.4) | 2.25 | 3.27 | 3.71 | 3.92 |
| NO5 | flat | 12.84 | 15.89 | 17.42 | 18.30 |
| NO5 | diurnal | 9.18 | 11.36 | 12.20 | 12.86 |
| NO5 | SARIMA | 7.58 | 10.63 | 11.67 | 12.32 |
| NO5 | GBM (corrected) | 6.55 | 8.99 | 9.94 | 10.25 |
| NO5 | GBM (v1.4) | 6.51 | 8.91 | 9.70 | 9.87 |

Concordance, mean over days 1–4 (day 1 in parentheses):

| Zone | SARIMA | GBM (corrected) | GBM (v1.4, as published) |
|------|-----:|-----:|-----:|
| NO1 | 0.573 (0.594) | 0.600 (0.630) | 0.595 (0.627) |
| NO2 | 0.583 (0.614) | 0.584 (0.600) | 0.581 (0.598) |
| NO3 | 0.540 (0.571) | 0.566 (0.602) | 0.555 (0.592) |
| NO4 | 0.542 (0.570) | 0.532 (0.569) | 0.527 (0.577) |
| NO5 | 0.718 (0.736) | 0.754 (0.766) | 0.753 (0.765) |

Data: `~/khepri-data/eds-revisjon/_data/s2-j2b/` (flat, diurnal, SARIMA, primary split) and
`~/khepri-data/eds-revisjon/_data/s2-ren/` (GBM), produced with the version 1.4 functions and the
corrected boundaries; the version 1.5 code reproduces them exactly (SE1 checked, every row identical).

---

*Version 1.4 text follows, unchanged.*

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
Pre-registered expectation (ADR-0004 correction): NO4's large CI movements track
a step change in its fossil-gas share, not predictable from CI history. Confirmed
against data:
- **NO4 H2-2021 (gas near zero, pure hydro): MAPE 2.94 — trivially easy** (gas
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
