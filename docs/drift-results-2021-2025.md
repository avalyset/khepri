# Drift results 2021–2025 (ADR-0003)

Production-based CI per zone per year, ADR-0001+0002 pipeline. Threshold
(pre-registered in ADR-0003): year-over-year CI change > 15% OR mix shift > 5 pp
= material drift.

## Annual CI per zone (gCO2eq/kWh)

| Zone | 2021 | 2022 | 2023 | 2024 | 2025 | Verdict |
|------|-----:|-----:|-----:|-----:|-----:|---------|
| NO1 | 23.63 | 23.31 | 23.48 | 23.45 | 23.31 | **stable** (±1%) |
| NO2 | 23.10 | 22.58 | 23.52 | 23.61 | 23.85 | **stable** (<5%) |
| NO3 | 21.65 | 20.95 | 20.89 | 20.75 | 21.46 | **stable** (<4%) |
| NO4 | 23.34 | 37.67 | 45.08 | 51.46 | 39.65 | **MATERIAL DRIFT** |
| NO5 | 34.90 | 28.75 | 24.93 | 25.00 | 24.46 | **MATERIAL DRIFT** |

## Year-over-year change (>15% flagged)

- NO1/NO2/NO3: all transitions < 5%. No flags.
- **NO4:** 2021→22 **+61.4%**, 2022→23 **+19.7%**, 2023→24 +14.2%, 2024→25 **−23.0%**.
- **NO5:** 2021→22 **−17.6%**, 2022→23 −13.3%, then stable.

## Regime test: 2021-2022 (crisis) vs 2023-2025

| Zone | Crisis mean | Later | Diff | Material? |
|------|-----:|-----:|-----:|---|
| NO1 | 23.47 | 23.41 | +0.2% | no (stable) |
| NO2 | 22.84 | 23.66 | −3.5% | no |
| NO3 | 21.30 | 21.03 | +1.3% | no |
| NO4 | 30.51 | 45.40 | **−32.8%** | **YES** |
| NO5 | 31.83 | 24.79 | **+28.4%** | **YES** |

## NO4 — driver measured (not hunted): gas share per year

CORRECTED with 2019-2020 data (see "Correction" below): the driver is the
Hammerfest LNG outage, not a new gas ramp.

| Year | Fossil Gas mean MW | Fossil Gas % of mix | CI | Hammerfest LNG status |
|----|-----:|-----:|-----:|---|
| 2019 | 194 | — | (outside primary window) | normal operation |
| 2020 | 124 | — | — | fire Sept. 2020 → outage |
| 2021 | 2 | ~0.07% | 23.34 | **offline all year** |
| 2022 | 111 | 3.14% | 37.67 | restart 2 June 2022 |
| 2023 | 152 | 4.78% | 45.08 | full operation |
| 2024 | 168 | 6.23% | 51.46 | full operation |
| 2025 | 105 | 3.63% | 39.65 | operation |

NO4's CI tracks the Hammerfest LNG (Melkøya) gas turbines. The plant shut down
after a fire in Sept. 2020, was offline ~20 months, and restarted 2 June 2022
([source](https://maritime-executive.com/article/lng-production-resumes-at-hammerfest-20-months-after-fire)).
The 2021 collapse (2 MW) is the outage; the "ramp" 2022-2024 is **recovery after
the fire**, not new growth.

### Correction (R15 / B3)
An earlier draft (commit 1ac6b96, pushed) described NO4 as a "Melkøya gas ramp
2022-24" and 2021 as "no gas column". Both are wrong: gas existed (~194 MW) in
2019, and the 2021 low point is a fire-driven outage, not a baseline. Drift
analysis on 2021-2025 alone misread the 2021 anomaly as the starting point;
pre-2021 data revealed the error. **The drift figures themselves (CI per year, H0
rejected for NO4) stand — only the causal explanation is corrected: event-driven
outage/recovery, not structural growth.** Consequence for forecast: NO4's "drift"
is an unpredictable industrial event (fire), not a smooth trend — harder to
forecast than seasonality.

## Verdict (H0: stable signal, prior-year CI a good proxy)

- **NO1, NO2, NO3: H0 holds.** ±5% over five years. Prior-year CI is a good
  proxy; annual updates are sufficient for the adoption layer.
- **NO4, NO5: H0 rejected.** Material drift above the 15% threshold. Prior-year
  CI is NOT a safe proxy — these zones require more frequent updates, and the drift
  must be documented in the codecarbon integration.

## NO5 — driver identified (close inspection, R15)

NO5's drift (34.90 → 24.46) is **genuine gas phase-out**. Fossil Gas fell 2.33%
(2021) → 0.10% (2025); at a factor of 490 that gives −10.9 gCO2, almost exactly
explaining the CI drop of −10.4 gCO2. NO5 is converging towards the pure-hydro
baseline (~24) as gas is phased out.

Confirmed against 2019-2020 data (same sanity that revealed the NO4 error): NO5
gas was a steady ~80 MW in 2019-2021, then a monotonic decline 2022→2025 (32→7→2
MW). This is a **genuine trend**, not a 2021 anomaly. Both gas-driven outliers thus
have DIFFERENT mechanisms: NO4 = V-shape (fire-driven outage + recovery), NO5 =
monotonic phase-out. The earlier "mirror-image" description was imprecise — what
they share is that gas is the driver.

| Year | Fossil Gas % | CI | Hydro % | Total (TWh) | Coverage |
|----|-----:|-----:|-----:|-----:|-----:|
| 2021 | 2.33 | 34.90 | 90.2 | 31.0 | 100% |
| 2022 | 1.02 | 28.75 | 96.4 | 27.6 | 100% |
| 2023 | 0.20 | 24.93 | 96.3 | 30.2 | 100% |
| 2024 | 0.21 | 25.00 | 96.6 | 32.2 | 100% |
| 2025 | 0.10 | 24.46 | 96.7 | 32.1 | 94% |

Excluded: not a coverage artefact (2021 = 100%). The large flagged mix shifts
(Pumped Storage −4.1 pp, Run-of-river +5.2 pp) are CI-neutral — both hydro
(factor 24), an ENTSO-E reclassification. The actual driver is the smaller gas
shift, because gas has a ~20× higher factor. 2021 was also a drier year (lowest
hydro in absolute terms, 27.95 TWh) — consistent context, but gas is the CI
driver.

→ Both drift outliers explained by the same mechanism (fossil gas): NO4 ramping
up, NO5 phasing out.

## Caveats (B3)
- NO4 2021 lacks a Fossil Gas column (gas not reported/produced then) → first-vs-
  last mix-drift summary undercounted NO4; the correct evolution is the per-year
  gas table above.
- 2021–2024 = 100% coverage (hourly). 2025 = 88–100% (mixed resolution,
  ADR-0002-handled). Drift comparison rests on solid coverage.
- Descriptive regime comparison (effect size against threshold), not p-value —
  per ADR-0003 Decision 3.
