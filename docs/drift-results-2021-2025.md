# Drift results 2021–2025 (ADR-0003)

Production-based CI per zone per year, ADR-0001+0002 pipeline. Threshold
(pre-registered in ADR-0003): year-over-year CI change > 15% OR mix shift > 5 pp
= material drift.

## Correction 2026-10-01 (version 1.5)

The mix arm of the drift rule was not applied as registered. The verdict further down rests on the CI arm: it calls
NO1–NO3 stable without applying the mix arm, and it attributes the NO4 and NO5 drift to gas. Recomputed by the rule (journal revision
EDS-2026-0107; source: `~/khepri-data/eds-revisjon/07-tabell3-korreksjon.md`), both readings are given: year over year
(ADR-0003) and first year against last (the window used in the paper's Table 3). The text below the block is the
version 1.4 text, kept unchanged for the record.

The rule (ADR-0003 §2, verbatim): «Year-over-year CI change > 15% OR mix-share shift > 5 percentage points for a
material type (material per ADR-0002: ≥ 0.5% mix or ≥ 5 MW) counts as material drift.» Operationalised here: share =
`mix_pct` (energy-weighted share of all generation in clean intervals, the basis of this document); a type counts in a pair of
years if it is material as `ci.py` implements ADR-0002 (≥ 0.5% **and** ≥ 5 MW; see the ADR-0003 addendum on the "or") in
either year. Types without a verified factor (Other, Other renewable, Waste) are excluded before classification and do not
count. Nothing in the CI figures changes.

| Zone | Largest YoY CI change | CI arm, YoY | Mix arm, YoY: material types > 5 pp | CI change 2021→2025 | CI arm, window | Mix arm, window: material types > 5 pp |
|---|---|:-:|---|---|:-:|---|
| NO1 | -1.33% (2021→2022) | not exceeded | 2021→2022: Hydro Run-of-river and poundage +34.67; Hydro Water Reservoir -37.20 *(hydro categories only)* | -1.34% | not exceeded | Hydro Run-of-river and poundage +33.00; Hydro Water Reservoir -36.47 *(hydro categories only)* |
| NO2 | +4.20% (2022→2023) | not exceeded | 2021→2022: Hydro Pumped Storage -5.79; Hydro Run-of-river and poundage +5.45 *(hydro categories only)* | +3.27% | not exceeded | none |
| NO3 | +3.42% (2024→2025) | not exceeded | 2021→2022: Hydro Run-of-river and poundage +8.86; Hydro Water Reservoir -11.79; Wind Onshore +5.30 · 2024→2025: Hydro Water Reservoir +7.42; Wind Onshore -5.40 | -0.87% | not exceeded | Hydro Run-of-river and poundage +9.60; Hydro Water Reservoir -8.89 *(hydro categories only)* |
| NO4 | +61.38% (2021→2022) | exceeded | 2021→2022: Hydro Water Reservoir -7.66 *(hydro categories only)* · 2023→2024: Hydro Water Reservoir -7.71 *(hydro categories only)* · 2024→2025: Hydro Water Reservoir +6.45 *(hydro categories only)* | +69.84% | exceeded | Hydro Water Reservoir -12.67 *(hydro categories only)* |
| NO5 | -17.61% (2021→2022) | exceeded | 2021→2022: Hydro Run-of-river and poundage +5.40 *(hydro categories only)* | -29.92% | exceeded | Hydro Run-of-river and poundage +5.22 *(hydro categories only)* |

**What this changes in the sections below.**
- *Verdict, NO1–NO3 "H0 holds"*: true on the CI arm (every year-over-year change within ±5%). All three cross the mix arm,
  through shifts between Hydro Water Reservoir and Hydro Run-of-river and poundage (and, in NO2, Pumped Storage), which carry
  the same factor (24) and leave CI unchanged; NO3 also crosses through Wind Onshore year over year (+5.30 in 2021→2022,
  −5.40 in 2024→2025).
- *NO4 and NO5*: the CI arm is crossed as stated. The mix arm is crossed by hydro categories, not by gas: the largest
  year-over-year change in the fossil-gas share is +3.07 pp in NO4 (2021→2022) and -1.31 pp in NO5 (2021→2022). The
  CI arm is what identifies gas.
- *Regime test 2021–2022 against 2023–2025*: unchanged (+0.2 / −3.5 / +1.3 / −32.8 / +28.4%).

**Observation, unconfirmed.** In all five Norwegian zones the shift between reservoir and run-of-river happens in the same hour,
27 October 2021 10:00–11:00 UTC; in each zone it is the largest hourly change in run-of-river output of the year (rank 1 of
8 759), and total hydro output is nearly unchanged:

| Zone | Hydro Water Reservoir (MW) | Run-of-river and poundage (MW) | Pumped storage (MW) | Total hydro |
|---|---|---|---|---|
| NO1 | 1742.5 → 810.2 | 555.1 → 1473.8 | – | 2297.6 → 2284.1 (-0.6%) |
| NO2 | 3501.1 → 3316.9 | 403.9 → 703.2 | 217.9 → 0.2 | 4122.9 → 4020.3 (-2.5%) |
| NO3 | 2124.0 → 1675.1 | 393.2 → 859.2 | 0.0 → 0.0 | 2517.2 → 2534.4 (+0.7%) |
| NO4 | 2316.4 → 2014.2 | 67.5 → 297.4 | – | 2384.0 → 2311.6 (-3.0%) |
| NO5 | 2769.3 → 2616.5 | 140.1 → 496.8 | 273.8 → 34.3 | 3183.2 → 3147.6 (-1.1%) |

This is consistent with units being reclassified between ENTSO-E production types in the reporting chain rather than with a
change in generation. It has **not** been confirmed with Statnett or ENTSO-E. The phrase "an ENTSO-E reclassification" in the
NO5 section below refers to this observation and should be read as unconfirmed.

---

*Version 1.4 text follows, unchanged.*

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

CORRECTED with 2019-2020 data (see "Correction" below): the driver is a
temporary absence of gas generation, not a new gas ramp.

| Year | Fossil Gas mean MW | Fossil Gas % of mix | CI |
|----|-----:|-----:|-----:|
| 2019 | 194 | — | (outside primary window) |
| 2020 | 124 | — | — |
| 2021 | 2 | ~0.07% | 23.34 |
| 2022 | 111 | 3.14% | 37.67 |
| 2023 | 152 | 4.78% | 45.08 |
| 2024 | 168 | 6.23% | 51.46 |
| 2025 | 105 | 3.63% | 39.65 |

NO4's CI tracks its fossil-gas share, which is what the table above measures.
The 2021 value (2 MW mean, ~0.07% of the mix) is a near-total absence of gas
generation; the rise through 2022-2024 returns the share to the level seen in
2019 (194 MW mean). On the data alone this is a **return to the earlier level**,
not new growth. What took gas out of NO4 in 2021 is not derivable from the
ENTSO-E extract, which reports generation per production type and not per plant;
no external attribution is made here.

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
