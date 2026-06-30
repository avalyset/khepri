# Khepri

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21042581.svg)](https://doi.org/10.5281/zenodo.21042581)

Since I work with AI across many fields, it would be remiss not to contribute here too.

## What it is

A license-clean, reproducible **per-zone carbon-intensity signal for nine Nordic electricity bidding zones — NO1–NO5 and SE1–SE4** — for use in carbon-aware computing, with **honest drift and forecast characterisation**, not just raw numbers. Carbon intensity is derived deterministically from:

- **ENTSO-E** Actual Generation per Production Type (A75), per bidding zone, and
- **published lifecycle emission factors** (IPCC AR5 Annex III, cited).

This is the first per-zone NO CI signal with the field's eval convention and documented drift/forecast behaviour. The SE extension adds the first per-bidding-zone SE1–SE4 CI signal; novelty comes from granularity (zone-level), not signal strength — SE cross-zone spread is 5.6–8.0 gCO2eq/kWh vs NO 16.7–30.7. Neither is claimed stronger than the other.

## What it replaces

Tools such as [codecarbon](https://github.com/mlco2/codecarbon) use a **uniform static value of 18.0 gCO2eq/kWh for all Norwegian and Swedish bidding zones** (`nordic_emissions.json`, verified against installed v3.2.8). This is wrong for every zone and in both directions — too low for most zones (**~2.5× too low for NO4**), yet too high for nuclear-dominated SE3 (true CI 14.5) — and it does not distinguish the zones from one another. Khepri produces distinct, source-traceable per-zone values instead.

**2025 per-zone values (gCO2eq/kWh):**

| Zone | CI | Note |
|------|----|------|
| NO1  | 23.3 | |
| NO2  | 23.9 | |
| NO3  | 21.5 | |
| NO4  | 39.6 | gas-turbine dependent (Hammerfest LNG) |
| NO5  | 24.5 | |
| SE1  | 20.6 | |
| SE2  | 20.1 | |
| SE3  | 14.5 | nuclear-dominant (~63%); lowest of the nine zones |
| SE4  | 17.4 | structurally drifting (ADR-0007) |

## Layers (ADR-anchored)

Every method choice is locked in an ADR **before** computation — verifiable, not post-rationalised. Full ADR chain 0001–0008 (English).

1. **Data core** ([ADR-0001](docs/decisions/0001-ci-beregningsmetode.md), [ADR-0002](docs/decisions/0002-nan-materialitetsterskel.md)): production-based per-zone CI, duration-weighted, NaN exclusion.
2. **Drift** ([ADR-0003](docs/decisions/0003-drift-metode.md), [NO results](docs/drift-results-2021-2025.md)): multi-year stability 2021–2025.
3. **Forecast** ([ADR-0004](docs/decisions/0004-forecast-metode.md), [NO results](docs/forecast-results.md)): 96-hour per-zone forecast in the CarbonCast/EnsembleCI convention.
4. **Adoption** ([ADR-0005](docs/decisions/0005-adopsjon-codecarbon.md)): codecarbon integration.
5. **SE data core** ([ADR-0006](docs/decisions/0006-se-per-sone.md)): SE1–SE4 CI by the same pipeline; nuclear (B14, 12 gCO2eq/kWh, IPCC AR5) added; SE3 is nuclear-dominant.
6. **SE drift** ([ADR-0007](docs/decisions/0007-se-drift.md)): SE1/SE2/SE3 stable; SE4 structurally drifting (>15% YoY criterion, pre-registered from ADR-0003). Window 2022–2025 (2021 coverage 4.7%, excluded).
7. **SE forecast** ([ADR-0008](docs/decisions/0008-se-forecast-method.md), [SE results](docs/se-forecast-results.md)): 96-hour per-zone SARIMA + persistence floor. H0 (heavy ML does not beat simple baselines) **not rejected** — GBM degraded in all four SE zones. SE3 MAPE 4.55%; SE4 20.19% (structural drift, not method failure). SE1/SE2 concordance ~0.58–0.60: level accuracy acceptable, direction tracking limited — noted limitation for scheduling use.

## Key findings (honest, not victory-dressed)

**NO (2021–2025):**
- NO1/NO2/NO3 are stable year-to-year (<5% → annual update sufficient). NO4 is **event-driven** — gas turbines at Hammerfest LNG were offline after a fire (Sept 2020 → restart June 2022), so NO4 CI is period-dependent, not a constant. NO5 shows real gas phase-out.
- **Forecast:** H0 holds broadly — simple baselines (persistence/SARIMA) are hard to beat for the stable zones; heavy ML is not safely better (gradient boosting collapses on the volatile NO4). NO4's event-step is not predicted (expected — a fire is not in the CI history). NO MAPE is in the same ballpark as CarbonCast's published regions — their SE aggregate is 8.87% day-1 (EnsembleCI Table 2-verified), though that's aggregate vs our per-zone, not apples-to-apples.

**SE (2022–2025):**
- SE1/SE2/SE3 stable; SE4 structurally drifting (pre-registered threshold, ADR-0007 provenance clean).
- **Forecast H0 not rejected:** SARIMA beats GBM in all four zones. SE3 achieves MAPE 4.55% (nuclear-dominated, low variance); SE4 MAPE 20.19% (drift-driven, not method failure).
- **Honest SE limit:** SE cross-zone spread is 5.6–8.0 gCO2eq/kWh — narrower than NO. SE1/SE2 concordance ~0.58: direction tracking is limited (scheduling value reduced for those two zones). This is documented, not hidden.

**Shared honest limit:** production-based CI is **not consumption-based** — import/export flow-tracing is not built. A separate, later decision.

## Two-way SE placeholder

Two codecarbon PRs are open — NO ([#1260](https://github.com/mlco2/codecarbon/pull/1260)) and SE ([#1262](https://github.com/mlco2/codecarbon/pull/1262)), the SE one covering the two-way placeholder error — both awaiting maintainer review. The SE values are citable from this artifact.

## License (split)

- **Code:** Apache-2.0 — see [LICENSE](LICENSE).
- **Data and documentation:** CC-BY-4.0 — see [LICENSE-DATA](LICENSE-DATA).

Raw ENTSO-E data is not committed to this repo (see `.gitignore`); it is fetched reproducibly via API.

## Status

Data core + drift + forecast built and verified for nine bidding zones (NO1–NO5, SE1–SE4). Adoption: codecarbon PRs open for both NO (#1260) and SE (#1262). Consumption-based layer is not built. See the ADRs for what is actually decided and what is open — nothing here is oversold.
