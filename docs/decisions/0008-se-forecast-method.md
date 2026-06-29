# ADR-0008: SE per-zone forecast — inheritance of ADR-0004 method

Status: Accepted
Date: 2026-06-29
Builds on: ADR-0004 (NO forecast), ADR-0006 (SE per-zone CI), ADR-0007 (SE drift)

## Context
SE per-zone CI (SE1-SE4) has been computed (ADR-0006) and drift-characterized (ADR-0007). The forecast layer produces per-zone 96-hour CI forecasts using the same method as NO (ADR-0004). Per-zone SE forecasting does not exist in the field: CarbonCast and EnsembleCI cover SE only as a country aggregate (verified against their data/ directories). Novelty comes from granularity (per bidding zone), not signal strength — SE is less distinct than NO (ADR-0006: cross-zone spread 5.6-8.0 vs NO 16.7-30.7), and it is nowhere claimed that SE is a stronger artifact than NO.

## Decision

### 1. Method inherited unchanged from ADR-0004
Same forecast.py: SARIMA baseline + persistence floor, 96 hours day-wise, sliding window. MAPE primary; MAE/RMSE/concordance secondary. Run per zone (SE1-SE4) separately. Complexity escalated low→high: SARIMA/persistence first, GBM only if baseline MAPE is insufficient AND the improvement is material. No method change from NO.

### 2. Split — drift-aware primary, no field-exact secondary (justified)
Primary split: train 2022-2023, validation 2024, test 2025. Drift-aware (ADR-0007: SE4 drifting, SE2 stable — testing on the final year captures generalization under drift).

No field-exact secondary split (in contrast to NO). Justification, explicit:
- (a) Data window: SE has no pre-2022 data with sufficient coverage (2021 = 4.7%, dropped in ADR-0006). A field-exact period match is impossible.
- (b) No reference to match: the NO secondary split existed to reproduce CarbonCast's field-exact period and yielded a directly citable number (and caught the Hammerfest error). For SE, CarbonCast coverage is AGGREGATE — a field-exact per-zone comparison does not exist. A secondary split would merely be another period with no external per-zone reference to lock against, so no comparability is gained. It is dropped because it does not give what it gave for NO, not for convenience.

### 3. CarbonCast comparison — pre-approved METHOD, conclusion follows the numbers (B3)
This ADR pre-approves the comparison METHOD, not its conclusion:
- The only VERIFIED CarbonCast SE figure: EnsembleCI Table 2 (arXiv 2505.01959v1, HTML-verified), CarbonCast SE-AGGREGATE day 1 = 8.87% MAPE.
- CarbonCast's own paper SE figures (Tab 4/5) are UNVERIFIED — the PDF returned binary/403 during recon. They are never used, whatever memory might suggest.
- Pre-approved reporting method: report SE per-zone MAPE against the verified 8.87% aggregate, ALWAYS with the aggregate-vs-per-zone caveat stated explicitly. Primary reporting is SE per-zone MAPE in itself, not as a difference against anyone.
- Conditional phrasing: IF measured per-zone MAPE is of comparable order of magnitude, the phrasing "simple per-zone baselines achieve MAPE of the same order of magnitude as heavy aggregate models (CarbonCast SE-aggregate day 1 = 8.87%, EnsembleCI Table 2-verified)" is permitted. IF there is material deviation (either direction), report the difference straight. The conclusion follows the numbers, not this ADR.
- FORBIDDEN regardless of outcome: "beats CarbonCast" as a bare claim, or per-zone MAPE compared against aggregate as if apples-to-apples.

### 4. Pre-registered H0 (model complexity)
H0: per-zone SE CI does not require heavy ML beyond SARIMA/persistence for a usable 96h forecast — i.e. a heavy model (GBM) does not meaningfully beat a SARIMA/seasonal baseline. This is a falsifiable methodological claim about the field's model choice, not a magnitude claim. The materiality threshold for "meaningful improvement" is inherited from ADR-0004 (no new degree of freedom introduced here). A negative result (heavy ML needed / baseline insufficient) is an equally real and reportable finding. The outcome is not assumed before the run.

## Positioning (applies to all output from this layer)
First per-bidding-zone SE1-SE4 CI forecast (granularity novelty, verified against aggregate coverage at CarbonCast/EnsembleCI). NEVER "first SE CI forecast" (aggregate exists). NEVER "stronger/richer than NO". The magnitude claim is dead.

## B3 caveat
The effective training window is short: 2 years (2022-2023) for training. For a 96h horizon the relevant seasonal structure is primarily diurnal/weekly (captured by 2 years), but annual seasonality is weakly estimable. Reported as a limitation, not hidden. Results are interpreted within this window.

## Consequences
- Per-zone forecast MAPE feeds the SE codecarbon contribution argument (drift-differentiated update frequency, ADR-0007).
- Same ADR chain, reproducibility, and DOI discipline as NO.

## Alternatives considered
- Field-exact secondary split as for NO: rejected — no per-zone reference to match (CarbonCast is aggregate), and the data window lacks pre-2022. Does not give what it gave for NO.
- Using CarbonCast's own paper SE figures as comparison: rejected — unverified (PDF inaccessible). Only the EnsembleCI Table 2 figure is used.
- Starting with heavy ML: rejected — ADR-0004 inheritance escalates low→high; H0 is tested with the baseline first.
