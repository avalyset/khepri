# Khepri v2 — state of record (dev)

**Status:** work in progress on local branch `v2-dev-dk-fi` (not pushed; repo is PUBLIC).
**Last verified against disk:** 2026-07-09.
**Scope of v2:** geographic completion of the production-based per-zone CI to the
continental Nordic zones (DK1, DK2, FI) + a demand (load) side for all twelve zones,
as the substrate for a later **consumption-based CI** layer. Iceland is out of scope
(isolated system, not in ENTSO-E).

> This file is the single verified base for the next work step. It is **dev-facing**;
> the published-facing `README.md` stays v1.2 (NO+SE) and must not carry v2-dev state.
> "v2" here is the DK/FI + demand + consumption roadmap — distinct from the earlier
> "SE v2" extension, which is already published inside v1.2.

## What is decided vs gated

- **Done & verified:** DK1/DK2/FI production-based CI (2025); demand/load for all 12
  zones (2025); load↔generation resolution alignment characterised (ADR-0009).
- **Gated (not started):** consumption-based CI. Blocked on external zonal
  flow-tracing data + a balancing method (INATECH Freiburg, expected later). The
  resolution choice (ADR-0009) stays **Proposed** until that method's native grid is
  known — the consumption layer must inherit the same balancing grid.
- **Not in v2 scope:** cross-border flows/exchanges (partner's layer), marginal
  emissions.

## v2 repo footprint (branch `v2-dev-dk-fi` vs `main`)

Three commits; complete list of repo files touched:

| Commit | Files | What |
|--------|-------|------|
| `898ec50` | `src/khepri/ci.py`, `src/khepri/factors.py` | `run_all(zones, year)` parametrised (default NO = v1 repro); `ZONES_V2_ADDED=[DK1,DK2,FI]`. `Fossil Peat` excluded + flagged sensitivity proxy. |
| `91ddc6b` | `src/khepri/factors.py` | Peat proxy relabelled a **floor** not a ceiling (value 820 unchanged; label/comment only). |
| `6a863ca` | `docs/decisions/0009-resolution-alignment-gen-load.md` | ADR-0009 (Proposed). |

The compute method is zone-agnostic (`ci.compute(df)`); only orchestration lists
zones. Fetch/compute/align **drivers and all raw/derived data live outside git** in
the working area (see below), mirroring how the v1 SE workflow was run.

## Verified per-zone CI (2025, production-based, gCO2eq/kWh)

v2-added zones only (NO/SE are the v1 base, in README):

| Zone | Primary CI | Sensitivity (incl. Waste/Peat proxies) | Note |
|------|-----------:|---------------------------------------:|------|
| DK1 | **88.6** | 102.4 | wind-heavy but coal/gas/waste present |
| DK2 | **157.4** | 197.8 | more fossil/CHP + waste (Waste 9.55% of mix, material) |
| FI  | **48.2** | 71.9 | nuclear+hydro moderate; Peat excluded from primary |

Materiality caveat: Waste (DK) and Peat (FI) are material and excluded from the
primary → primary biases **downward**; compare `compute_sensitivity()`. Peat has no
IPCC AR5 median; 820 is a coal-equivalent **floor** proxy (sensitivity only), so
FI-with-peat ≥ 71.9. `Energy storage` in FI has no factor → flagged `missing_factor`,
excluded (near-empty ENTSO-E column, ~all NaN).

## Data coverage matrix (per zone, 2025)

| Zone | generation (location) | load | aligned load | CI computed |
|------|----------------------|:----:|:-----------:|:-----------:|
| NO1–NO5 | `~/khepri-data/raw/entsoe-rest/` (v1) | ✓ | ✓ | v1 |
| SE1–SE4 | `~/khepri-data/se/raw/entsoe-rest/` (v1) | ✓ | ✓ | v1 |
| DK1, DK2, FI | `~/khepri-data/v2-dk-fi/` (v2) | ✓ | ✓ | v2 (above) |

All load + aligned-load CSVs (12 zones) and DK/FI generation live in the working
area `~/khepri-data/v2-dk-fi/`. NO/SE generation stays in its v1 canonical location;
`align_load.py` reads generation from the correct per-family path.

## Resolution matrix (empirical, ADR-0009)

Native resolution shifts mid-2025 (pan-European 15-min ISP rollout), on **different
dates per zone/data-type**. Measured from timestamp deltas, not assumed.

| Zone | gen native | load native | gen 60→15 | load 60→15 | aligned coverage |
|------|-----------|-------------|-----------|------------|-----------------:|
| NO1–NO5 | 60→15-min | 60→15-min | 2025-04-10 | 2025-03-18 | 100 % |
| SE1–SE4 | 60→15-min | 60→15-min | 2025-12-01 | 2025-12-01 | 100 % |
| DK1, DK2 | 60→15-min | **60-min all year** | 2025-04-08 | **no switch** | **~31 %** |
| FI | 15-min all year | 15-min all year | (const) | (const) | 100 % |

- NO/SE/FI align 100 % (load is never coarser than gen → superset). **The alignment
  break is DK-isolated**: after 08 April DK gen is 15-min but DK load stays 60-min, so
  ~69 % of DK gen timestamps have NaN load (genuinely missing, **not interpolated**).
- DST 2025 clean: **0 duplicate timestamps** in any zone (gen+load); UTC handling
  correct. Genuine data holes (NaN, not DST): DK gen+load outage 2025-05-08; isolated
  DK1 load holes (01-07, 02-28); ~5 h DK load hole around the autumn DST (10-25→26).

## ADRs in force

`0001`–`0008` **Accepted** (NO/SE CI, NaN threshold, drift, forecast, adoption, SE
extension). `0009` **Proposed** — gen/load resolution alignment (decision deferred,
see above).

## What remains (next steps)

1. Consumption-CI layer — **gated** on flow-tracing data + balancing method (INATECH).
2. On arrival of the balancing method: resolve ADR-0009 (path A downsample gen→60min /
   B upsample load→15min / C keep native separate) and move it to Accepted, declaring
   the grid **per zone**.
3. Optional: drift/forecast layers for DK/FI (currently NO/SE only; `drift.ZONES` is
   NO-only).

Working-area file guide: `~/khepri-data/v2-dk-fi/INDEX.md`.
