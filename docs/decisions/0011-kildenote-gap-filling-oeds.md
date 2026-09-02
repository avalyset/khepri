# ADR-0011: Source note — gap-filling in the delivered OEDS dataset

- **Status:** Accepted (source note; records a property of an external input, decides nothing)
- **Date:** 2026-09-02
- **Relates to:** [ADR-0010](0010-balansering-forbrukslag.md) (balancing for the consumption layer), [ADR-0002](0002-nan-materialitetsterskel.md) (NaN = genuinely missing, not zero).

## Context

The flow-tracing delivery we hold (`import-values-nordics.csv`, 2025) is the
output of `INATECH-CIG/OEDS-scrips`, branch `bulk-agft`. Gap-filling is applied to
generation, load and flows **before** tracing runs, and the delivered table
carries the filled values without marking them.

This note records what the filling does, so that anything built on the data can
cite it. It takes no position on whether the filling is appropriate.

## The rules, as coded

`exchange_analysis/utils.py:799-834`, `default_rules`. The default is `ZERO`
(line 805); more specific rules override it in this order:

| Method | Condition | Line |
|---|---|---|
| `WEEK_BEFORE` | gap ≤ 1 week, and ≥ 1 week into the series | 811-814 |
| `LINEAR` | gap ≤ 3 hours, interior to the series | 816-819 |
| `FORWARD_FILL` | gap ≤ 3 hours, ending at the last point | 821-824 |
| `BACKWARD_FILL` | gap ≤ 3 hours, starting at the first point | 826-829 |

Values filtered as outliers are relabelled `FILTERED_OUTLIER_*` (lines 831-833)
but are filled by the same rules. Execution is in `fill_gaps_series`
(`utils.py:834-859`).

**A gap that matches none of the above is filled with zero.** That is the
default, not a fallback for exotic cases: any gap longer than one week, and any
gap longer than three hours that is not covered by `WEEK_BEFORE`, becomes zero.

## The day-ahead proxy

`exchange_analysis/utils.py:937-976`, `patch_gaps_with_dayahead`. For physical
flow gaps **longer than one week** (`min_gap_length = pd.Timedelta(weeks=1)`,
line 944), the missing block is replaced with the corresponding day-ahead
commercial schedule from `{bz}_raw_commercial_flows_dayahead` (lines 958-968) and
tagged `DAYAHEAD_PROXY`.

**Consequence: parts of what the delivery labels physical flow are scheduled
values, not measurements.** Since aggregated tracing takes its nodal injections
from exactly these physical net-export columns
(`data_analysis.py:289-296`), any such block propagates into the traced result.

## Where the filling is applied

`exchange_analysis/download_data.py`:

| Line | Call | Applies to |
|---|---|---|
| 117 | `fill_gaps_wrapper(gen_df, …)` | generation |
| 153 | `fill_gaps_wrapper(load_df, …)` | load |
| 167 | `correct_zero_values(gen_df, …)` | generation |
| 289 | `fill_gaps_wrapper(df_resampled, …)` | flows |
| 307 | `correct_zero_values(…, flow_type=…)` | flows |

All of these run before the analysis phase. The day-ahead patch is invoked from
`fill_gaps_wrapper` (`utils.py:998`).

## Consequences

- **The delivery does not distinguish filled from measured values.** The gap
  method is recorded upstream in separate gap logs and in a `ROW`/method column
  written by `_record_gap_method` (`utils.py:29-45`); neither is present in the
  CSV we hold.
- **Any consumption layer built on this data must state the gap method**, and
  must state that day-ahead schedules stand in for physical flow in long-gap
  blocks. Reporting a traced figure without that is reporting a partly scheduled
  quantity as a measured one.
- This is in tension with [ADR-0002](0002-nan-materialitetsterskel.md), which
  holds that missing data stays NaN rather than becoming zero. The upstream
  default is the opposite. The tension is recorded here, not resolved: it is
  their pipeline, and the choice is theirs to make.
- Obtaining the gap logs alongside the values would let a downstream layer mark
  filled intervals. Not requested yet.

## What this note does not do

It does not evaluate the filling, does not propose changing it, and does not bear
on the balancing choice in ADR-0010. It exists so that the property is written
down where a reader of the method will find it.
