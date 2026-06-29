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
