# ADR-0009: Resolution alignment of generation and load (gen/load grid)

- **Status:** Proposed
- **Date:** 2026-07-09
- **Builds on:** [ADR-0001](0001-ci-beregningsmetode.md) (production-based, duration-weighted CI), [ADR-0002](0002-nan-materialitetsterskel.md) (NaN = genuinely missing, not zero).

> **This ADR is Proposed, not Accepted.** It documents a resolution mismatch and
> lays out the alignment options, but does **not** pick one. The choice is gated on
> the external zonal flow-tracing / balancing method (expected next week): the
> consumption-CI layer must inherit the *same* balancing grid for consistency, so
> the resolution decision is deferred until that method's native resolution is known.

## Context

The Khepri-Nordic extension adds demand (Actual Total Load, A65) alongside generation (Actual
Generation per Production Type, A75) for the twelve Nordic bidding zones
(NO1–NO5, SE1–SE4, DK1, DK2, FI), full-year 2025. Any generation+demand balance —
and the consumption-based CI layer that will sit on the partner's flow-tracing —
requires generation and load on the **same interval grid per zone**.

ENTSO-E publishes different data types on different Market Time Units (MTU), and the
pan-European 15-minute Imbalance Settlement Period (ISP) went live during 2025, so
generation and load **do not switch to 15-min on the same date, and in one family
do not both switch at all**. This resolution heterogeneity in ENTSO-E is a known
property, not a new finding (cf. Hirth, Mühlenpfordt & Bulkeley, *Applied Energy*
225, 2018, on the ENTSO-E Transparency Platform's reporting inconsistencies). The
value of this ADR is the **explicit, reproducible per-zone handling**, not the
observation itself.

### Verified resolution matrix (empirical, read from the staged 2025 CSVs)

Native resolution is measured from timestamp deltas (UTC), not assumed. "Shift" is a
sustained 60→15-min regime change during 2025.

| Zone | gen native | load native | gen 60→15 switch | load 60→15 switch | aligned coverage |
|------|-----------|-------------|------------------|-------------------|-----------------:|
| NO1–NO5 | 60→15-min | 60→15-min | **2025-04-10** | **2025-03-18** | **100 %** |
| SE1–SE4 | 60→15-min | 60→15-min | **2025-12-01** | **2025-12-01** | **100 %** |
| DK1, DK2 | 60→15-min | **60-min all year** | **2025-04-08** | **no switch** | **~31 %** |
| FI | 15-min all year | 15-min all year | (constant) | (constant) | **100 %** |

Reading of the matrix:

- **NO** — gen and load both reach 15-min, but load switches ~3 weeks *earlier*
  than gen (03-18 vs 04-10). Because load is never coarser than gen, every gen
  timestamp exists in load → 100 % coverage holds despite the different dates.
- **SE** — gen and load switch on the **same** date (12-01); identical grids all
  year → 100 %.
- **DK1/DK2** — the only broken case. Gen switches to 15-min on **2025-04-08**
  while load stays 60-min for the whole year. After 08 April, gen is *finer* than
  load, so only the hour-aligned gen timestamps have a matching load value:
  ~31 % conservative coverage; the other ~69 % are **NaN (genuinely missing, not
  interpolated)**. Before 08 April both were 60-min and aligned.
- **FI** — both constant 15-min → 100 %.

**The alignment break is DK-isolated.** Resolution *heterogeneity and mid-year
shifts* are system-wide (a 2025 ISP-rollout artefact), but the only family where
generation becomes finer than load — and alignment therefore fails — is DK.

Likely cause (context, **not** verified from disk): generation and load are carried
on different reporting streams / MTUs per area, and the Danish load stream had not
migrated to 15-min in this 2025 extract. Stated as plausible context only.

### DST and data-hole integrity (verified)

- **DST 2025** (spring 2025-03-30 hour skipped; autumn 2025-10-26 hour doubled):
  in UTC there is no gap or duplicate. **Zero duplicate timestamps** in every zone,
  gen and load; the transition windows show normal 15/60-min spacing. UTC handling
  is clean.
- **Genuine data holes** (NaN, per ADR-0002 — not DST, not resolution): concentrated
  in DK — a shared gen+load outage window on **2025-05-08** (gen ~3.5 h; load ~6 h),
  a few isolated hourly load holes (DK1 2025-01-07, 2025-02-28), and a ~5 h DK load
  hole spanning the autumn DST (2025-10-25→26). These are real missing intervals,
  left as NaN.

## Decision (Proposed — the resolution choice, deferred)

Two forced-alignment paths, each with a directional bias made explicit:

- **(A) Downsample generation 15→60-min where load is 60-min (i.e. DK).**
  Honest: fabricates **no** load points; aggregates gen to the coarser grid the load
  is actually reported on. Cost: loses intra-hour generation variation — negligible
  for annual aggregates, larger for hour-resolved analysis.
- **(B) Upsample load 60→15-min (i.e. DK).**
  Keeps gen's native resolution, but **fabricates load points**: the gen+demand
  balance would rest on invented demand in 3 of every 4 quarter-hours after 08 April.
  A silent assumption that should be avoided.

The **open question that decides A vs B** is the native resolution of the external
zonal flow-tracing / balancing method: an hourly balancing method favours (A); a
sub-hourly one would need (B) and must own the interpolation explicitly. Because the
consumption-CI layer must inherit the same balancing grid, the decision stays
**Proposed** until that method is known.

## Consequences

- The chosen path must be **declared explicitly per zone** in the Khepri-Nordic method note,
  e.g. *"DK balanced on 60-min (native load resolution); NO/SE/FI on their common
  grid."* — no single global resolution is truthful for 2025.
- **Reproducibility / comparability:** whichever path is taken, the switch dates
  above are part of the record; a reader must be able to reconstruct the grid per
  zone per date. The Khepri v2.0 preprint's method section must state the per-zone grid and
  the A/B/C choice.
- NO/SE/FI need no forced alignment for 2025 (already 100 %); only DK carries the
  resolution decision.

## Alternatives considered

- **(C) Keep both grids separate; report each series on its native resolution, no
  forced alignment.** Preserves every native point and fabricates nothing, but
  defers the gen+demand balance entirely to the consumer of the data. Viable as the
  most conservative option, and the natural default if the balancing method is not
  fixed in time. Retained as a live third path, not rejected.
- **Silent resample (either direction) without recording it** — rejected: it would
  hide fabricated points (B) or lost variation (A) behind a uniform-looking grid,
  the exact opposite of ADR-0002's NaN-honesty.
