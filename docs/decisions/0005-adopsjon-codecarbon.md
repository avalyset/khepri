# ADR-0005: Adoption — codecarbon integration of NO per-zone CI

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0001, ADR-0002, ADR-0003, ADR-0004

## Context
Khepri's goal is to fill the gap in Norwegian carbon-aware computing: codecarbon
(the tool that measures AI/ML emissions) uses a uniform placeholder (18.0
gCO2eq/kWh) for all NO zones in its production fallback (nordic_emissions.json).
Recon (verified against source) confirmed: the structure is already per-zone, the
method is production-/generation-mix-based (matches ADR-0001), external factor PRs
are merged (precedent #1039/#1224), the tests read dynamically from JSON (an update
does not break them), and the opening is unclaimed. Adoption is a PR that replaces
the NO1-NO5 values with Khepri's derived, drift-characterised figures.

## Pre-registered decisions (locked before the PR is written)

### 1. Factor basis: IPCC AR5, inherited from ADR-0001
The PR uses Khepri's IPCC AR5 lifecycle medians (ADR-0001), NOT codecarbon's own
per-source factors. Rationale: (a) internal consistency — the same figures in
codecarbon as in Khepri's DOI artefact; otherwise two different NO4 values exist in
the wild and reproducibility is broken; (b) IPCC AR5 is a cited/peer-reviewed
standard (CarbonCast/EnsembleCI convention), whereas codecarbon's own table is
methodologically mixed (direct fossil + WNA lifecycle). The PR explains the
divergence from codecarbon's carbon_intensity_per_source.json explicitly and
defends IPCC AR5 as a consistent basis.

### 2. Which values, which period
Per-zone annual-mean CI, production-based, from the most complete available year
(2025) using the ADR-0001+0002 method. Values: NO1, NO2, NO3, NO4, NO5 as
computed (not stated from memory — the PR fetches them from Khepri's committed
output, B1).

### 3. Drift characterisation MUST accompany the values (honesty over bare replacement)
The PR does not simply drop five figures. Metadata/notes per zone carry the drift
finding (ADR-0003) and forecast finding (ADR-0004):
- NO1/NO2/NO3: stable year-over-year (<5%); annual update is sufficient.
- NO4: event-driven variability (Hammerfest LNG outage 2020-2022, documented) —
  the value is period-dependent, not a stable constant. Flagged explicitly.
- NO5: production-based CI near the hydro lifecycle floor (~24) in pure-hydropower
  periods.
- Honest limit stated: production-based NO CI is low and not very distinct between
  zones except where fossil gas occurs (NO4).

### 4. Methodological transparency in the PR
The PR states explicitly: (a) that this replaces the production fallback, not the
Electricity Maps consumption-based primary path; (b) source (ENTSO-E + IPCC AR5,
link to Khepri DOI once frozen); (c) that the method is production-based
generation-mix (matches codecarbon's own fallback methodology); (d)
reproducibility (Khepri repo, ADR chain).

### 5. Direct PR (precedent-grounded)
codecarbon recon showed precedent for external direct factor PRs (#1039, #1224,
both merged). PR sent directly, no prior issue. BUT immediately before submission:
forbigåelse check (gh pr list + issue list --search "Norway"/"NO1"/"nordic"/
"emission factor" — has anyone opened anything since recon?) and verify the PR
does not collide with ongoing work. The PR body explains the improvement fully
(as an issue would), since there is no prior issue to lean on.

## Consequences
- The gap is filled at source: Norwegian codecarbon users get per-zone figures
  instead of a uniform 18.0 (which is too low for all, 2.5× too low for NO4).
- Khepri becomes a cited source in a widely used tool — adoption, not just
  publication.
- The drift characterisation makes the PR accountable: users know which zones are
  stable and which require updates.
- Divergence from codecarbon's own factor table must be defended in review —
  accepted cost for consistency with Khepri's DOI artefact.

## Alternatives considered
- Factor basis B (recompute with codecarbon's own factors): rejected — would
  produce two different NO values (codecarbon vs Khepri DOI), break
  reproducibility, and tie us to codecarbon's methodologically mixed table.
- Bare value replacement without drift metadata: rejected — dishonest about what
  the drift/forecast layers found; a static NO4 value would mislead.
- Wait for DOI freeze before the PR: considered — the PR can be opened with a link
  to the Khepri repo now, the DOI added once frozen. Not a blocker, but the PR
  should reference the forthcoming DOI anchor.

## Dependency
Adoption (this ADR) builds on data-core + drift + forecast (all complete). Freeze
(Phase 5) is separate: DOI freeze of the Khepri artefact strengthens the PR
(citable anchor) but does not block it.
