# ADR-0002: Materiality threshold for NaN exclusion

- **Status:** Accepted
- **Date:** 2026-06-29
- **Refines:** [ADR-0001](0001-ci-beregningsmetode.md), Decision 2.

## Context

ADR-0001 Decision 2 excludes an entire interval if *one* included
(factor-carrying) production type has NaN. The first 2025 run revealed that this
produces a **coverage artefact**: for NO2 and NO3 coverage fell to ~31% and ~27%,
driven exclusively by minor types with **negligible production** that are
unreported (NaN) for most of the year:

- NO2 **Wind Offshore**: NaN 55.9% of the year, but annual mean **2.5 MW** (~0.04% of the mix).
- NO3 **Solar**: NaN 66.6%, but annual mean **0.0 MW**.

An unreported type that contributes ~0 MW regardless is not a real data loss.
Letting it discard 2/3 of otherwise valid intervals leaves a known artefact in the
core figure.

## Decision

Distinguish between **material** and **negligible** production types, with a
threshold **pre-registered here — set on principled grounds, not tuned against
coverage**:

> A production type is considered **negligible** in a zone if its
> annual-mean contribution is **< 0.5% of the zone's total mix** OR **< 5 MW
> absolute**. Otherwise it is **material**.

Rules:
1. **NaN in a negligible type → treated as 0** (not a data loss).
2. An interval is **excluded only when NaN occurs in a material type**.
3. Coverage is still reported per zone. Which types were classified as negligible
   is reported as provenance.

## Rationale for the threshold

The threshold is chosen so that a type below it **cannot move the zone CI
measurably**: a type at < 5 MW or < 0.5% of the mix shifts the energy-weighted
average by a fraction of a gCO2eq/kWh regardless of its factor. The boundary is
principled (negligible = immeasurable effect), not empirically chosen to maximise
coverage. The double condition (relative OR absolute) captures both small zones
and small types.

## Consequences

- NO2/NO3 coverage rises to a representative level without touching the other
  zones (NO1/NO4/NO5 already have ≥ 93.6% coverage and no material NaN types).
- The core figure no longer rests on a ~30%-sample for NO2/NO3.
- The threshold is a fixed part of the method; changing it requires a new ADR.

## Alternatives considered (rejected)

- **Retain ADR-0001 strictly** — leaves a known artefact in the core figure.
- **Threshold chosen after seeing coverage** — would make "negligible" a degree
  of freedom to fish with; rejected. The threshold is pre-registered.
- **Drop NaN exclusion entirely (NaN=0)** — rejected in ADR-0001 (artificial for
  material types).

---

## Addendum 2026-10-01 — what the NaN in a material type is, and what the rule costs

Found while preparing the journal revision (EDS-2026-0107); the rule above is **unchanged for every 1.x version**.

1. **The NaN that costs coverage in 2025 is pumping, not missing data.** The intervals lost in NO2, NO3 and NO5 in 2025
   (coverage 87.7%, 93.8% and 93.6%) are not caused by the minor types this ADR was written for but by
   *Hydro Pumped Storage*, a material type whose generation column is NaN in the intervals where its consumption column
   is positive, that is, while the plant is pumping: 3 445 of 3 445 NaN intervals in NO2, 1 704 of 1 717 in NO3 and
   1 790 of 1 795 in NO5. ENTSO-E reports a pumping plant's output as absent rather than as zero, and the rule reads that
   absence as missing data.
2. **The cost, measured.** Recomputing every zone-year 2021–2025 with all NaN set to zero moves the annual CI by at most
   −0.12 gCO2eq/kWh (NO2 2025, −0.116); with no materiality threshold by at most −0.60 (NO2 2025); with linear
   interpolation of gaps up to 3 h by at most −0.002. Source: `~/khepri-data/eds-revisjon/04-nan-sensitivitet.md` (D3).
3. **The rationale's bound was too strong.** "A fraction of a gCO2eq/kWh regardless of its factor" holds for low-factor
   types only. Setting a type with energy share s and factor f to zero moves the energy-weighted average by
   s(CI − f)/(1 − s), so at the 0.5% threshold the effect is bounded by 0.005·f/0.995: 0.12 for a hydro type, 2.5 for gas
   and 4.1 for coal, and slightly less in practice since the effect scales with f − CI.

Reading pumping hours as zero generation is proposed for method version 2.x in
[ADR-0017](0017-pumpetimer-som-null-generering.md). It is not applied in 1.x, so the published 1.x series are unchanged.
