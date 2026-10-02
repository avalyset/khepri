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

---

## Addendum 2026-10-01 — the materiality "or", and the mix arm as applied

Found while preparing the journal revision (EDS-2026-0107). The decisions above are unchanged.

1. **"or" in Decision 2 should read "and".** The parenthesis "material per ADR-0002: ≥ 0.5% mix or ≥ 5 MW" inverts
   ADR-0002, which defines a type as *negligible* if it is below 0.5% **or** below 5 MW, so a *material* type is at or above
   0.5% **and** at or above 5 MW. That is what `ci.py` implements (`share_pct >= MATERIAL_MIN_SHARE_PCT and
   type_mean >= MATERIAL_MIN_MW`) and what every published figure uses. ADR-0002 and the code govern.
2. **The mix arm in the published documents departed from the rule.** `docs/drift-results-2021-2025.md` called NO1–NO3
   stable on the CI arm alone and attributed the NO4/NO5 mix shift to gas; the paper's Table 3 (EDS submission) judged the
   mix arm on the gas share. Applied as registered — any material type, more than 5 pp, year over year — the mix arm is
   crossed in every zone except SE2, and in all five Norwegian zones by shifts between hydro categories (same factor, CI
   unchanged), not by gas. The recomputation is in the dated correction blocks of both drift documents, in both readings
   (year over year, and first year against last as ADR-0007 registers). No CI figure changes.
3. **Regime window.** Decision 3 says 2023-2026; `drift.regime_compare` and the drift document use 2023–2025. The
   published comparison is 2023–2025; with H1 2026 added the differences move by at most 1.1 percentage points and no
   zone changes side of the 15% threshold (`~/khepri-data/eds-revisjon/07-tabell3-korreksjon.md`).
