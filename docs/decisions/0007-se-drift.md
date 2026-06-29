# ADR-0007: SE per-zone drift — inheritance of the ADR-0003 method

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0003 (drift), ADR-0006 (SE per-zone CI)

## Context
SE per-zone CI (SE1-SE4, ADR-0006) has been computed for 2022-2025. The drift
layer characterises year-over-year stability per zone using the same method as NO
(ADR-0003). 2021 is excluded (coverage 4.7%, approximately two weeks of data);
effective window 2022-2025.

## Decision: inherit the ADR-0003 drift method unchanged, pre-registered threshold

### 1. Method and threshold inherited from ADR-0003 (pre-registered provenance)
The drift method (drift.py) is used unchanged. The materiality threshold is
inherited from ADR-0003, set for NO BEFORE any SE data existed: > 15%
year-over-year CI change OR > 5 pp mix-share shift for a material type (material
per ADR-0002) = material drift. The threshold is NOT chosen to fit SE figures —
its provenance is ADR-0003 (NO), prior to all SE data. It is applied to SE without
adjustment. Borderline cases (values just above the threshold) are reported as
material drift against the pre-set threshold, not smoothed away because they are
close.

### 2. Test window
2022 vs 2025 per zone against threshold; year-over-year changes reported for the
full 2022-2025 span. 2021 excluded (coverage).

### 3. SE-specific caveat (B3)
2021 excluded (4.7% coverage). SE does not have the energy-crisis-specific
2021-2022 regime shift measurable in this window, since 2021 is absent. The drift
characterisation applies to 2022-2025.

## Consequences
- Per-zone update frequency for the codecarbon contribution is informed by drift:
  stable zones require less frequent updates than drifting ones.
- Same ADR chain, reproducibility, and DOI discipline as NO.
