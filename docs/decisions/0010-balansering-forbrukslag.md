# ADR-0010: Balancing for the consumption-based layer

- **Status:** Proposed
- **Date:** 2026-09-02
- **Supersedes:** [ADR-0009](0009-resolution-alignment-gen-load.md) (gen/load resolution alignment)
- **Builds on:** [ADR-0001](0001-ci-beregningsmetode.md) (production-based, duration-weighted CI), [ADR-0002](0002-nan-materialitetsterskel.md) (NaN = genuinely missing, not zero).

> **This ADR is Proposed, not Accepted.** It states what the upstream input
> actually is, and lays out the balancing families available to us. It does
> **not** pick one, and nothing below should be read as indicating which way the
> choice will go.

## Context

### What aggregated coupling flow tracing gives us

The upstream input is the `Agg Flow Tracing` measure from INATECH's OEDS
pipeline (`INATECH-CIG/OEDS-scrips`, branch `bulk-agft`). Read from source:

- `exchange_analysis/data_analysis.py:256-367`, `perform_aggregated_flow_tracing`.
  Per hour, a characteristic matrix `A` and injection vector `Pin` are built from
  the physical net-export columns between neighbouring zones, and the topology is
  inverted (`q = np.dot(np.linalg.inv(A), Pin)`, line 344). Nodal injections are
  **net positions**; no load enters the construction at any point. Generation and
  physical flows are resampled to `1h` before the inversion (lines 268-270), so
  sub-hourly structure is gone by the time tracing runs.
- `exchange_analysis/data_analysis.py:188-252`, `_decompose_and_save`. The traced
  volumes are split by production type using `gen_fractions[n] = df[gen_types] /
  df["Total Generation"]` (lines 208-213) applied as
  `gen_fractions[n].mul(traced_dfs[bz][n], axis=0)` (line 229). The type split
  therefore comes **entirely from the exporting zone's own generation mix**.

Confirmed by the method's author (Schäfer, INATECH, 2026-09-02): *"Aggregated
coupling flow tracing does not need any balancing, since the tracing works on net
positions (derived from flows), and the results are multiplied by generation
shares. If you want to calculate consumption mixes, you must do your own
balancing, because aggregated coupling flow tracing only provides the mix of net
imports. The original purpose was to document origin of imports, not consumption
mixes."*

### What that leaves open

The delivered measure is a **net-import mix**, not a consumption mix. Turning one
into the other requires closing generation, load and net flows per zone, and that
closure is a modelling choice we own. ADR-0009 assumed the choice was inherited
from upstream; it is not.

## Decision (Proposed — the balancing choice, open)

Three families are available. Each is stated with what it preserves, what it
gives up, and which gen/load grid it commits us to.

### (A) Load and flows as given; scale generation

Take measured load and measured net flows as fixed, and scale the generation
vector so the zone balances.

- **Preserves:** the load series as reported, and the flow series the tracing is
  already built on — so the consumption layer rests on the same flows as the
  upstream input.
- **Gives up:** the measured generation mix as an exact quantity. Scaling moves
  the residual into production, which is also the quantity our production-based
  CI is derived from (ADR-0001). The two layers would then rest on different
  generation numbers unless that is stated.
- **Binds us to:** the grid the **load** is reported on. For DK after 2025-04-08
  that is 60-min, per the matrix carried over from ADR-0009.
- **Precedent, not recommendation:** this is what INATECH do for *direct*
  coupling flow tracing — *"here we usually take flows and load as given and
  scale the generation for the balancing"* (Schäfer, 2026-09-02). Their direct
  method needs balancing; the aggregated one we were given does not. The
  precedent is recorded because it exists, not because it decides anything here.

### (B) Generation and flows as given; load as residual

Take measured generation and measured net flows as fixed, and derive load as
generation minus net export.

- **Preserves:** the generation mix exactly as measured, so the consumption layer
  and the production-based CI rest on the same production numbers.
- **Gives up:** load as an observed quantity. It becomes a computed residual that
  absorbs every reporting inconsistency in generation and flows, including the
  known DK gaps.
- **Binds us to:** the grid the **generation** is reported on — 15-min in DK
  after 2025-04-08, which is finer than the reported load and would make the
  derived load finer than any measurement supporting it.

### (C) Distribute the residual across both sides

Close the balance by apportioning the mismatch over generation and load by a rule
fixed before computation.

- **Preserves:** neither series exactly, but treats both as measured with error
  rather than one as ground truth.
- **Gives up:** the ability to say that any single reported series is carried
  through untouched, and requires the apportionment rule itself to be justified
  and pre-registered.
- **Binds us to:** whichever grid the rule is defined on; a rule stated per
  interval requires a common grid, which for DK does not exist across the year.

## Consequences

- **The balancing choice determines the resolution choice, not the reverse.**
  ADR-0009 deferred the gen/load resolution decision until an upstream method was
  known. With no upstream balancing to inherit, the order is inverted: whichever
  family is chosen here fixes which series is authoritative, and that fixes the
  grid. Options (A), (B) and (C) from ADR-0009 remain available and are decided
  downstream of this ADR.
- **The resolution matrix stands.** Per-zone native resolutions, the 60→15-min
  switch dates, the DK-isolated alignment break, the DST verification and the
  genuine data holes are our own measurements on our own extract and are carried
  over from ADR-0009 unchanged.
- **The upstream input carries gap-filled values.** See
  [ADR-0011](0011-kildenote-gap-filling-oeds.md); any layer built on the delivered
  data must state the gap method.
- Whichever family is chosen must be declared per zone in the method note, with
  the same explicitness ADR-0009 required for the resolution choice.

## Alternatives considered

- **Use `Direct Flow Tracing` instead.** It is the other traced measure in the
  delivery and does carry a balancing convention upstream. Not evaluated here;
  it would change what the input is, not remove the need for this decision.
- **Skip balancing and publish the net-import mix as-is.** Honest and immediately
  available, but it is not a consumption-based CI and must not be labelled as one.
  Retained as a live option precisely because it makes no claim it cannot support.
