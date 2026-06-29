# ADR-0006: SE per-zone CI — extension of the Khepri method to Swedish bidding zones

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005

## Context
The Khepri method (NO1-NO5) is extended to the Swedish bidding zones SE1-SE4.
codecarbon has the same placeholder defect for SE as it had for NO: SE1-SE4 all
18.0 gCO2eq/kWh uniform (verified against nordic_emissions.json). CarbonCast/
EnsembleCI cover SE only as a country aggregate (verified against their data/
directories — one SE/, no SE1-4), so per-zone SE is genuinely new. Forbigåelse
check clean: no open SE per-zone CI issue/PR in CarbonCast, EnsembleCI or
codecarbon.

## Decision: inherit the unchanged method, note the SE-specific aspects

### 1. Method inherited unchanged from ADR-0001 + ADR-0002
SE1-SE4 CI is computed with the EXACT same ci.py pipeline as NO: production-based
generation-mix × IPCC AR5 lifecycle factors, duration-weighted aggregation, NaN
exclusion, materiality threshold (0.5% mix / 5 MW). No method change. Drift
(ADR-0003) and forecast (ADR-0004) are inherited likewise.

### 2. EIC codes (verified against entsoe-py, not assumed)
SE1 10Y1001A1001A44P · SE2 10Y1001A1001A45N · SE3 10Y1001A1001A46L · SE4
10Y1001A1001A47J. NB: 10YSE-1 is the country AGGREGATE, not per-zone — confirmed
and rejected. The per-zone codes above are authoritative.

### 3. Nuclear power (new relative to NO, AR5-verified)
SE has production type Nuclear (B14), absent in NO. Factor = 12 gCO2eq/kWh (IPCC
AR5 Annex III median, same secondary source as ADR-0001 — cross-checked
consistent). Nuclear was observed ONLY in SE3 (2026-06-27 intraday), not in
SE1/SE2/SE4. SE3 exclusivity is expected structurally and confirmed empirically in
the data-core run over the full window (2021-2025) — that is where the size of the
per-zone variation is quantified, not in this ADR. (The observed value was
production on 2026-06-27, not installed capacity.) Nuclear in SE3 is expected to
be the primary source of per-zone variation — in contrast to NO where variation was
gas-driven (NO4) and otherwise low.

### 4. psrType caveat (B3, explicit)
The verified psrType set is from one intraday period (2026-06-27). Rare types
(Waste, Biomass) that were not producing that day may appear in the full annual
data. These are handled automatically by the existing factors.py mechanism (AR5
factor or EXCLUDED/SENSITIVITY_PROXY for below-material types). SE does NOT have
only the six types observed on one day — the full data-core run reveals the actual
set, and the method handles new types without change.

### 5. Contribution — honest positioning (B3)
- Data-core + per-zone drift SE1-SE4: genuinely new (no one has per-zone, only
  aggregate).
- Forecast: claimed as "first per-bidding-zone SE1-SE4 CI forecast", NEVER as
  "first SE CI forecast" (CarbonCast has SE aggregate). Per-zone granularity is
  what is new.
- codecarbon gap-fill: genuinely independent of forecasting (the placeholder is
  equally wrong for SE).

## Consequences
- The SE artefact may be stronger than NO on the forecast layer: SE3 nuclear
  provides real per-zone variation to forecast, whereas NO was low and not very
  distinct.
- Same reproducibility, ADR chain, DOI discipline as NO.
- Separate codecarbon PR (parallel to #1260) for SE1-SE4.

## Alternatives considered
- Assume 10YSE-1: rejected — that is the aggregate, which would collapse the
  per-zone claim (the gate caught this).
- New factor for nuclear: rejected — the AR5 value (12) is already in factors.py
  and consistent; no reason to deviate.
- codecarbon gap-fill only, without drift/forecast: rejected — per-zone drift +
  forecast is the genuinely new contribution the field lacks.
