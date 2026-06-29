# ADR-0003: Drift measurement in the CI signal

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0001, ADR-0002

## Context
Khepri's adoption layer (codecarbon integration) needs to know whether a CI figure
computed for one year is valid for the next, or whether the Norwegian generation mix
drifts enough that the signal decays and must be retrained. This is measured on the
production-based CI signal (ADR-0001+0002 method) over 2021–H1 2026 per NO zone.
Pre-registration is locked before the drift result is observed.

## Pre-registered decisions (locked before result)

### 1. Drift metric
- Primary: annual CI per zone, computed with the EXACT ADR-0001+0002 pipeline per
  year (same factors, NaN exclusion, duration-weighting, materiality threshold).
  Year-over-year change in percent.
- Secondary: mix share per psrType per year, year-over-year drift in percentage
  points.

### 2. Threshold for material drift (pre-registered)
- Year-over-year CI change > 15% OR mix-share shift > 5 percentage points for a
  material type (material per ADR-0002: ≥ 0.5% mix or ≥ 5 MW) counts as material
  drift.
- Rationale: below this threshold a prior-year CI figure is usable as a proxy for
  the current year (adoption-relevant: update frequency can be annual). Above it,
  that is no longer true and more frequent retraining is required.

### 3. Regime test (energy crisis 2021-2022)
- Test whether 2021-2022 is statistically distinct from 2023-2026 per zone: compare
  annual-mean CI and mix shares. Flag if crisis years deviate > threshold (Decision
  2) from the later regime.
- Pre-specified: this is a descriptive regime comparison, not a hypothesis test with
  p-value — we report the size of the difference against the threshold, not
  significance.

### 4. Null hypothesis (explicit)
- H0: Norwegian per-zone CI is stable year-over-year (hydro-dominated → low drift,
  prior-year figures are a good proxy).
- We test whether H0 holds. We do NOT expect a particular outcome. A stable signal
  and a drifting signal are both genuine, publishable findings with different
  consequences for the adoption layer's update frequency.

## Consequences
- Stable signal (drift < threshold): prior-year CI is a good proxy; the codecarbon
  integration can be updated annually.
- Drifting signal (drift > threshold): the signal decays; more frequent retraining
  is required, and this must be documented in the adoption deliverable.
- NO4 gas share is measured per year as part of mix drift (a driver we know is
  present; we measure its evolution, not hunt for it).

## Alternatives considered
- Lower threshold (5%): rejected — captures seasonal/weather noise that is not real
  structural drift.
- Hypothesis test with p-value on regime: rejected — we have the full population
  (all intervals), not a sample; effect size against threshold is more appropriate
  than significance.
