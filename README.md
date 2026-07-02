# Khepri

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21042581.svg)](https://doi.org/10.5281/zenodo.21042581)
[![ci](https://github.com/avalyset/khepri/actions/workflows/ci.yml/badge.svg)](https://github.com/avalyset/khepri/actions/workflows/ci.yml)

Khepri is a reproducible, per–bidding-zone carbon-intensity (CI) dataset and method for the nine Nordic electricity bidding zones — **NO1–NO5** (Norway) and **SE1–SE4** (Sweden) — for use in carbon-aware computing. Carbon intensity is derived deterministically from:

- **ENTSO-E** Actual Generation per Production Type (A75), per bidding zone, and
- **IPCC AR5 Annex III** lifecycle emission factors.

The method is production-based and spans a data core, multi-year drift characterisation, and 96-hour per-zone forecasts. It provides the first per–bidding-zone SE1–SE4 CI signal; the Swedish contribution is per-zone granularity, and the cross-zone spread is narrower in Sweden (5.6–8.0 gCO2eq/kWh) than in Norway (16.7–30.7).

## What it replaces

[codecarbon](https://github.com/mlco2/codecarbon) assigns a single static value of **18.0 gCO2eq/kWh to every Norwegian and Swedish bidding zone** (`nordic_emissions.json`, verified against v3.2.8). This value is inaccurate for every zone and in both directions: too low for most zones — about **2.2× too low for NO4** — and too high for the nuclear-dominated zone SE3, whose 2025 CI is 14.53. Khepri provides distinct, source-traceable per-zone values.

## 2025 per-zone values (gCO2eq/kWh)

| Zone | CI | Note |
|------|-----:|------|
| NO1 | 23.31 | |
| NO2 | 23.85 | |
| NO3 | 21.46 | |
| NO4 | 39.65 | gas-turbine dependent (Hammerfest LNG) |
| NO5 | 24.46 | |
| SE1 | 20.63 | |
| SE2 | 20.11 | |
| SE3 | 14.53 | nuclear-dominant (~63%); lowest of the nine zones |
| SE4 | 17.42 | drifting (see SE drift) |

## Method

Each method choice is fixed in an architecture decision record (ADR) before computation, so the figures are verifiable rather than post-rationalised. The full chain — data core, drift, forecast, adoption, and the SE extension (ADR-0001 through ADR-0008) — is in [docs/decisions/](docs/decisions/). Result documents: [NO drift](docs/drift-results-2021-2025.md), [SE drift](docs/se-drift-results-2022-2025.md), [NO forecast](docs/forecast-results.md), [SE forecast](docs/se-forecast-results.md).

Carbon intensity is production-based: it weights the generation produced within a zone. Consumption-based flow-tracing (imports and exports) and marginal emissions are not implemented; they are a separate, later layer.

## Findings

**Norway (2021–2025).** NO1, NO2, and NO3 are stable year to year (under 5%, so an annual update is sufficient). NO4 is event-driven: the Hammerfest LNG gas turbines were offline after a September 2020 fire and restarted in June 2022, so NO4's CI is period-dependent rather than a constant. NO5 shows a real gas phase-out. In forecasting, simple baselines (persistence and SARIMA) are hard to beat for the stable zones, and gradient boosting collapses on the volatile NO4; the null hypothesis that simple baselines suffice holds broadly. NO4's event step is not predicted, as expected — a fire is not present in the CI history. NO forecast accuracy is of the same order as published regional results: the CarbonCast Swedish aggregate is 8.87% day-1 (EnsembleCI Table 2), which is a country aggregate and not directly comparable to the per-zone figures here.

**Sweden (2022–2025).** SE1, SE2, and SE3 hold their CI stable; SE4 crosses the pre-registered 15% year-over-year threshold (+15.21%, solar-driven). In forecasting, SARIMA beats gradient boosting in all four zones, so the null hypothesis is not rejected. SE3 reaches 4.55% MAPE (nuclear-dominated, low variance); SE4 is 20.19% (drift-driven). SE1 and SE2 have a concordance index near 0.58–0.60: level accuracy is acceptable but direction tracking is limited, which reduces scheduling value in those two zones.

Carbon intensity here is production-based and does not capture consumption-based, flow-traced, or marginal emissions.

## Adoption

The per-zone values are contributed upstream to codecarbon in two pull requests — NO ([#1260](https://github.com/mlco2/codecarbon/pull/1260)) and SE ([#1262](https://github.com/mlco2/codecarbon/pull/1262)); the SE one covers the two-way placeholder error. Both are under review — see the links for current status. The values are citable from this archived artifact independently of the pull requests.

## Reproduce

```bash
git clone https://github.com/avalyset/khepri.git
cd khepri
pip install -r requirements.txt
python -m pytest            # CI + forecast unit tests (tests add src/ to the path)
```

The unit tests run without external data. To regenerate the published per-zone results, raw ENTSO-E *Actual Generation per Production Type* CSVs (one per zone-year) are required. They are not committed (see `.gitignore`); fetch them with `entsoe-py` using an ENTSO-E Transparency Platform API token, then point `KHEPRI_RAW` at the directory:

```bash
export KHEPRI_RAW=/path/to/entsoe-csvs
PYTHONPATH=src python -c "import khepri.ci as ci; ci.run_all()"   # per-zone interval CI (2025)
```

The CI, drift, and forecast steps are in `src/khepri/` (`ci.py`, `drift.py`, `forecast.py`); the emission factors are in `factors.py`. The method for each step is fixed in the ADRs under `docs/decisions/`.

## License

- **Code:** Apache-2.0 — see [LICENSE](LICENSE).
- **Data and documentation:** CC-BY-4.0 — see [LICENSE-DATA](LICENSE-DATA).

## Status

Data core, drift, and forecast are complete and verified for all nine bidding zones (NO1–NO5, SE1–SE4). Adoption pull requests are open for NO (#1260) and SE (#1262). The consumption-based layer is not implemented. The current release is version 1.2.0; the concept DOI resolves to the latest archived version.
