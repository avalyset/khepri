# ADR-0017: Pumping hours as zero generation from method version 2.x

- **Status:** Proposed
- **Date:** 2026-10-01
- **Would refine:** [ADR-0002](0002-nan-materialitetsterskel.md), rule 2.
- **Does not apply to:** any 1.x version. The published 1.x series keep ADR-0002 as written.

## Context

ADR-0002 excludes an interval when a material production type is NaN. Its 2026-10-01 addendum records what that NaN mostly
is in 2025: *Hydro Pumped Storage* reports NaN generation in the intervals where its consumption column is positive, that
is, while the plant is pumping (3 445 of 3 445 NaN intervals in NO2, 1 704 of 1 717 in NO3, 1 790 of 1 795 in NO5). A
pumping plant generates nothing in those intervals; ENTSO-E reports the output as absent rather than as zero. The rule
reads the absence as missing data and drops the interval, which costs NO2, NO3 and NO5 6–12% of their 2025 intervals for
a reason that is not a data gap.

The consumption-based layer (version 2) already sets every NaN to zero, so the two layers do not rest on the same
intervals in NO2, NO3 and NO5.

## Proposed decision

From method version 2.x, a NaN in a *Hydro Pumped Storage* generation column is read as **0 generation** when the same
interval's pumped-storage consumption column is positive. Every other NaN is handled as in ADR-0002.

## Expected consequences (to be measured before acceptance)

- Coverage in NO2, NO3 and NO5 rises to near 100%; the remaining NaN intervals (13 in NO3, 5 in NO5 in 2025) are
  handled by ADR-0002 as before.
- The annual CI should move by about the amount of the all-NaN-to-zero variant in the ADR-0002 addendum, at most
  −0.12 gCO2eq/kWh in 2021–2025 (NO2 2025). That variant is not the same rule, so the effect must be recomputed under
  this one before acceptance.
- The production- and consumption-based layers then drop the same intervals in those zones.

## Alternatives considered

- **Keep ADR-0002 unchanged in 2.x**: leaves a known misreading in the core figure.
- **Set all NaN to zero, as version 2 does**: also zero-fills genuinely unreported generation, the bias ADR-0001 rejected.
- **Change 1.x now**: rejected. The 1.x figures are published and archived; the change goes into a new method version.

## Acceptance

Accepted only when the rule is implemented behind a version switch, the effect is recomputed per zone-year 2021–2025 under
this rule (not the all-NaN variant), and both are recorded in an addendum here.
