# SE drift results 2022–2025 (ADR-0007)

Production-based CI per zone per year, ADR-0001+0002 pipeline (unchanged), threshold
inherited from ADR-0003. Threshold (pre-registered in ADR-0003, before any SE data
existed): year-over-year CI change > 15% OR material mix-share shift > 5 pp = material
drift. Window 2022–2025 (2021 excluded: coverage 4.7%, ~two weeks).

Method: `drift.py` (ADR-0003) over `ci.py` (ADR-0001+0002, IPCC AR5, duration-weighted).
Values are computed from the ENTSO-E extract; the raw data is not committed (see
`.gitignore`) but is fetched reproducibly via the API.

## Annual CI per zone (gCO2eq/kWh)

| Zone | 2022 | 2023 | 2024 | 2025 | 4-yr mean |
|------|-----:|-----:|-----:|-----:|----------:|
| SE1  | 21.46 | 20.99 | 20.01 | 20.63 | 20.8 |
| SE2  | 20.60 | 20.25 | 19.80 | 20.11 | 20.2 |
| SE3  | 13.47 | 14.34 | 14.37 | 14.53 | 14.2 |
| SE4  | 15.12 | 16.21 | 16.70 | 17.42 | 16.4 |

The 2025 column matches the headline per-zone values (ADR-0006): SE3 is the lowest of
the nine Nordic zones (nuclear-dominated), SE4 the drifting one.

## Year-over-year CI change (%)

| Zone | 22→23 | 23→24 | 24→25 | 22→25 total | Material (>15%)? |
|------|------:|------:|------:|------------:|:----------------:|
| SE1  | −2.15% | −4.69% | +3.12% | −3.83% | no |
| SE2  | −1.66% | −2.22% | +1.54% | −2.36% | no |
| SE3  | +6.40% | +0.25% | +1.07% | +7.82% | no |
| SE4  | +7.22% | +3.01% | +4.32% | **+15.21%** | **yes (just over)** |

## SE4 — the borderline case, exact

- SE4 2022: 15.12 gCO2eq/kWh
- SE4 2025: 17.42 gCO2eq/kWh
- Change 2022→2025: **+15.2118%** — above the 15% threshold
- Material drift against the ADR-0003 threshold: **yes**

Year-over-year steps (monotone increase, no V-shape): +7.22% (2022→23), +3.01%
(2023→24), +4.32% (2024→25). The threshold is pre-registered in ADR-0003 (NO provenance,
set before SE data existed). +15.21% is above 15.0% and is reported as material drift;
the 0.21-point margin is not rounded away.

## Mix-share drift per zone (percentage points)

Note: SE3 2022 mix-share is computed with a nansum correction — `compute()` returns NaN
for the 2022 mix percentages because 'Marine' (a missing-factor, NaN-heavy column)
propagates NaN into the total via `numpy.sum`. The CI value (13.47) is correct; only the
mix-share reporting is affected (see caveats).

**SE1** — material types (Hydro Water Reservoir, Wind Onshore):

| Type | 2022 | 2023 | 2024 | 2025 | 22→25 | >5 pp? |
|------|-----:|-----:|-----:|-----:|------:|:------:|
| Hydro Water Reservoir | 79.9% | 76.3% | 68.8% | 73.7% | −6.2 pp | yes |
| Wind Onshore | 19.5% | 23.0% | 30.6% | 25.9% | +6.4 pp | yes |

Mix drift: yes (>5 pp both types). CI effect: neutralised (hydro 24 vs wind 11 gCO2eq/kWh).
Result: mix-share drift WITHOUT a corresponding CI drift (−3.83%). Stable CI, drifting mix.

**SE2** — material types (Hydro Water Reservoir, Wind Onshore):

| Type | 2022 | 2023 | 2024 | 2025 | 22→25 | >5 pp? |
|------|-----:|-----:|-----:|-----:|------:|:------:|
| Hydro Water Reservoir | 72.2% | 69.3% | 66.3% | 68.9% | −3.3 pp | no |
| Wind Onshore | 25.8% | 28.4% | 32.0% | 29.8% | +4.0 pp | no |

Mix drift: no (under 5 pp). CI drift: no (−2.36%). Result: stable — the only zone under
both thresholds.

**SE3** — material types (Nuclear, Hydro, Wind Onshore, Solar):

| Type | 2022 | 2023 | 2024 | 2025 | 22→25 | >5 pp? |
|------|-----:|-----:|-----:|-----:|------:|:------:|
| Nuclear | 69.5% | 64.0% | 64.6% | 63.1% | −6.4 pp | yes |
| Hydro Water Reservoir | 10.1% | 16.1% | 15.5% | 14.7% | +4.6 pp | no |
| Wind Onshore | 11.8% | 12.4% | 13.4% | 14.8% | +3.0 pp | no |
| Solar | 0.7% | 1.0% | 1.4% | 1.9% | +1.3 pp | no |

Nuclear falls −6.4 pp (2022→2025). CI effect is small (nuclear 12, hydro 24, wind 11
gCO2eq/kWh) — even a 6.4 pp nuclear fall to hydro/wind gives only +7.82% CI rise
(13.47 → 14.53). CI drift: no (7.82% < 15%). Mix drift: yes (nuclear >5 pp). Result:
mix-share drift (nuclear) with a limited CI effect. Mix drifts, CI stable.

**SE4** — material types (Wind Onshore, Other, Hydro Water Reservoir, Solar):

| Type | 2022 | 2023 | 2024 | 2025 | 22→25 | >5 pp? |
|------|-----:|-----:|-----:|-----:|------:|:------:|
| Wind Onshore | 62.2% | 61.8% | 63.9% | 63.6% | +1.4 pp | no |
| Other (excluded) | 21.0% | 14.6% | 12.8% | 15.0% | −6.1 pp | yes |
| Hydro Water Reservoir | 12.8% | 18.0% | 15.5% | 11.2% | −1.7 pp | no |
| Solar | 3.9% | 5.6% | 7.8% | 10.3% | +6.3 pp | yes |

Other (excluded from CI, no verified AR5 factor) falls −6.1 pp; Solar rises +6.3 pp
(Solar = 48 gCO2eq/kWh, a higher factor than wind/hydro). Mix drift: yes (Solar and Other
both >5 pp). CI drift: yes (15.21% > 15%). Result: drifting — solar growth drives CI up
monotonically 2022–2025.

## Threshold summary per zone

| Zone | CI drift 22→25 | >15%? | Material mix drift (>5 pp) | Verdict |
|------|---------------:|:-----:|---------------------------|---------|
| SE1 | −3.83% | no | yes (Hydro −6.2 pp, Wind +6.4 pp) | mix-drifting |
| SE2 | −2.36% | no | no | stable |
| SE3 | +7.82% | no | yes (Nuclear −6.4 pp) | mix-drifting |
| SE4 | +15.21% | **yes** | yes (Solar +6.3 pp, Other −6.1 pp) | drifting |

Threshold application (ADR-0003): EITHER CI >15% OR mix >5 pp = material drift. SE1 and
SE3 hold their CI stable but register material mix-share drift; SE2 is the only zone under
both arms; SE4 crosses both (CI +15.21% and Solar +6.3 pp). A CI-only reading would call
SE1/SE2/SE3 stable; the full OR-threshold reading is reported here.

## Implication for codecarbon update frequency

| Zone | Update frequency (ADR-0003 logic) |
|------|-----------------------------------|
| SE1 | More than annual (mix drift, though CI stable) |
| SE2 | Annual sufficient (only zone under both thresholds) |
| SE3 | More than annual (nuclear mix drifts) |
| SE4 | More than annual (CI drift AND mix drift, monotone rise) |

## Caveats (B3)

- SE3 2022 mix-share: `compute()` returns NaN because 'Marine' (a missing-factor,
  NaN-heavy column) propagates NaN into the total via `numpy.sum`. The CI value is
  correct; the mix shares for this analysis are computed with a nansum correction. This is
  a known edge case in `compute()` that does not affect the CI figure, only mix-share
  reporting.
- 2021 excluded (4.7% coverage, ~two weeks) — the drift characterisation applies to
  2022–2025 only.
- SE4 borderline: +15.2118% is above the threshold. Reported as material drift; the
  pre-registered threshold is 15.0% and the 0.21-point margin is not rounded away.
