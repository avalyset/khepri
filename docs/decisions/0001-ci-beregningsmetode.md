# ADR-0001: CI calculation method for Norwegian bidding zones (NO1–NO5)

- **Status:** Accepted
- **Date:** 2026-06-29

## Context

We derive per-zone carbon intensity (CI, gCO2eq/kWh) for NO1–NO5 from ENTSO-E
Actual Generation per Production Type (A75) and published lifecycle factors.
The calculation is arithmetic, but involves four method choices with degrees of
freedom. These are fixed **before** computation, so the numbers are verifiable
and not post-rationalised.
Each factor and each data characteristic has been verified against a named source
(not from memory) — see the log in § "Verification".

## Decision 1 — Factor source

**IPCC WG3 AR5 Annex III** — lifecycle medians (gCO2eq/kWh).
Lifecycle, not direct operation. The IPCC primary PDF is not directly reachable
from the build environment; values are taken from a **checkable secondary source
that names the table** (Wikipedia: *Life-cycle greenhouse gas emissions of energy
sources*, the column citing IPCC Annex III lifecycle medians). This is explicitly a
secondary source — standard practice as long as it is named. Coal=820 / gas=490
independently confirmed against the IPCC document's own PDF-URL via search.

Each factor is cited per row in `src/khepri/factors.py`. Factor table (types
that actually appear in NO 2025 data):

| Production type | gCO2eq/kWh | Mapping |
|---|---|---|
| Fossil Gas | 490 | IPCC 'Gas – combined cycle' (direct) |
| Hydro Water Reservoir | 24 | IPCC 'Hydropower' (direct) |
| Hydro Run-of-river and poundage | 24 | IPCC 'Hydropower' (one hydro category) |
| Hydro Pumped Storage | 24 | **PROXY** hydro; footprint depends on charging source |
| Wind Onshore | 11 | IPCC 'Wind onshore' (direct) |
| Wind Offshore | 12 | IPCC 'Wind offshore' (direct) |
| Solar | 48 | IPCC 'Solar PV – utility' (direct) |
| Biomass | 230 | IPCC 'Biomass – dedicated' (direct) |

## Decision 2 — NaN / missing data

Intervals with **NaN in an included (factor-carrying) production type are
EXCLUDED** from the CI average (choice a). NaN ≠ 0. **Coverage** (% intervals
used after exclusion) is reported as provenance per zone. A type that is absent
in a zone (not a column) contributes 0, not NaN.

**Unverified types** (Waste, Other, Other renewable) have no verified factor in
the chosen source. They are **excluded from primary CI**, and the effect is
reported as **sensitivity** (CI with them included on flagged proxies). They are
not guessed into the primary figure. The fraction of total energy they represent
is reported as coverage.

## Decision 3 — Production-based

CI is **production-based**. Import/consumption is **explicitly excluded**.
Consumption-based / flow-traced CI is a separate, later layer with its own ADR.

## Decision 4 — Duration-weighted aggregation

2025 data has **mixed resolution** (15-min and 60-min periods; verified on
disk). The CI average is weighted by **interval DURATION** (hours), not number
of intervals.

- CI per interval: `Σ(MW_type × factor_type) / Σ(MW_type)`
- Period average (energy-weighted): `Σ(MW × factor × duration) / Σ(MW × duration)`

i.e. total emissions / total energy over clean intervals.

## Consequences

- Deterministic and reproducible from raw data + this ADR.
- NO CI is low (hydro-dominated) and weakly distinct **except NO4**, which has
  documented fossil gas **year-round** (present in 98.8% of 2025 intervals,
  all four quarters) — a structural, not seasonal, property.
- Replaces codecarbon's verified uniform placeholder (18.0 gCO2eq/kWh for all
  NO zones, `nordic_emissions.json`, v3.2.8).
- Proxy and unverified types are explicitly flagged; no factor guessed in.

## Alternatives considered (rejected)

- **Direct operation factors** — less comparable with lifecycle literature.
- **codecarbon's own factor table** — methodologically mixed (direct fossil +
  WNA lifecycle) and missing biomass + waste; rejected in favour of consistent
  lifecycle approach.
- **Unweighted average of interval CI** — energy-distorting.
- **Count-weighting** — wrong under mixed 15-/60-min resolution.
- **NaN = 0** — artificial; under-estimates when data is missing.

## Verification

- EIC codes NO1–NO5: identical to `entsoe.mappings.Area`.
- psrType→name: identical to `entsoe.mappings.PSRTYPE_MAPPINGS`.
- Placeholder 18.0: read directly in installed `codecarbon` v3.2.8
  `data/private_infra/nordic_emissions.json`.
- Factors: see `src/khepri/factors.py` with source string per row.
