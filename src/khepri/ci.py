"""
Per-zone carbon intensity (CI) from ENTSO-E generation per type.

Implements ADR-0001 EXACTLY:
  - Factor source: IPCC AR5 Annex III (see factors.py).
  - Production-based (imports explicitly excluded).
  - NaN exclusion: intervals with NaN in an INCLUDED (factor-carrying) type
    are dropped from the mean. Coverage is reported as provenance. NaN != 0.
  - DURATION-weighted: 2025 data has mixed resolution (15-min + 60-min).
    Energy per interval = MW * duration_hours; CI is energy-weighted.
  - Waste/Other/Other renewable: excluded from the primary figure (no verified
    factor), reported as sensitivity.
"""

import os
import glob
import pandas as pd

from .factors import (
    FACTORS,
    EXCLUDED_NO_VERIFIED_FACTOR,
    SENSITIVITY_PROXY,
    SOURCE,
)

RAW_DIR = os.environ.get("KHEPRI_RAW", os.path.expanduser("~/khepri-data/raw/entsoe-rest"))
OUT_DIR = os.environ.get("KHEPRI_OUT", os.path.expanduser("~/khepri-data/ci-2025"))

# ADR-0002 — PRE-REGISTERED materiality threshold (set before the re-run, not against coverage).
# A type is NEGLIGIBLE if its annual-mean contribution is < MATERIAL_MIN_SHARE_PCT of the
# zone's total mix OR < MATERIAL_MIN_MW absolute. NaN in a negligible type -> 0;
# an interval is excluded only on NaN in a MATERIAL type.
MATERIAL_MIN_SHARE_PCT = 0.5
MATERIAL_MIN_MW = 5.0


def ci_of_mix(mw_by_type, factors=FACTORS):
    """Pure function: CI (gCO2eq/kWh) for one instantaneous mix. Σ(MW*f)/Σ(MW).

    Used by the sanity test — hand-computable.
    """
    num = sum(mw * factors[t] for t, mw in mw_by_type.items())
    den = sum(mw_by_type.values())
    if den == 0:
        raise ValueError("Σ MW = 0")
    return num / den


def load_zone(path):
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def _durations_hours(index):
    """Duration (hours) per interval = gap to the next timestamp.

    The last interval inherits the previous duration. Handles mixed 15-/60-min.
    """
    secs = (index[1:] - index[:-1]).total_seconds()
    dur = list(secs / 3600.0)
    dur.append(dur[-1] if dur else 1.0)
    return pd.Series(dur, index=index)


def compute(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR,
            carry_unfactored_at_zero=False):
    """Energy-weighted, duration-correct, NaN-excluded CI for one zone (ADR-0001+0002).

    Args:
        df: Generation per production type (MW), one column per type.
        factors: ENTSO-E type -> gCO2eq/kWh. Defaults to the AR5 table.
        excluded: Types to leave out of the primary CI entirely (ADR-0001).
        carry_unfactored_at_zero: When True, production types with no factor are
            kept in the DENOMINATOR at factor 0 instead of being dropped from
            both sides. The CI then answers "gCO2eq per kWh of all generation"
            rather than "per kWh of the generation we have factors for".

            Default False, so the archived v1.2 figures reproduce unchanged.
            Set True only for a consumer that applies the number to all energy —
            see ADR-0009 for why the codecarbon delivery does exactly that.
            Enabling it always lowers or leaves the CI unchanged, never raises
            it, since it adds to the denominator and nothing to the numerator.
    """
    occurring = list(df.columns)
    included = [c for c in occurring if c in factors and c not in excluded]
    missing_factor = [c for c in occurring
                      if c not in factors and c not in excluded]

    # Types with no factor at all. Under ADR-0001 they leave the calculation;
    # under ADR-0009 they stay in the denominator contributing zero emissions.
    unfactored = [c for c in occurring if c not in included]
    denominator_types = occurring if carry_unfactored_at_zero else included

    # ADR-0002: materiality per included type (against the pre-registered threshold).
    zone_total_mean = float(df[occurring].mean().sum())  # zone's total mix (mean MW)
    material, negligible = [], []
    for c in included:
        type_mean = float(df[c].mean())  # mean over non-NaN
        share_pct = (type_mean / zone_total_mean * 100) if zone_total_mean else 0.0
        if share_pct >= MATERIAL_MIN_SHARE_PCT and type_mean >= MATERIAL_MIN_MW:
            material.append(c)
        else:
            negligible.append(c)

    dur = _durations_hours(df.index)
    # An interval is excluded ONLY on NaN in a MATERIAL type.
    clean = df[material].notna().all(axis=1) if material else df.index.to_series().apply(lambda _: True)

    # NaN in a negligible type -> 0 (not data loss); material types are already non-NaN here.
    sub = df[included][clean].fillna(0.0)
    g = sub.clip(lower=0)                  # MW per included type, clean intervals
    d = dur[clean]                        # hours
    energy = g.mul(d, axis=0)            # MWh per type

    # The numerator is always the factor-carrying types — an unfactored type
    # contributes no emissions either way. Only the denominator moves.
    emis = float(sum(energy[c] * factors[c] for c in included).sum())  # ∝ gCO2
    denom_energy = (
        df[denominator_types][clean].fillna(0.0).clip(lower=0).mul(d, axis=0)
    )
    tot_energy = float(denom_energy.to_numpy().sum())
    ci = emis / tot_energy if tot_energy > 0 else float("nan")

    # interval CI for min/max
    gsum = g.sum(axis=1)
    erate = sum(g[c] * factors[c] for c in included)
    ici = (erate / gsum).replace([float("inf"), float("-inf")], pd.NA).dropna()

    # energy-weighted mix share over ALL occurring types (clean intervals)
    # .fillna(0.0) before summing, exactly as the numerator does above. Without
    # it a single NaN in ANY occurring type — including an excluded one the CI
    # never touches — poisons all_tot, and both `mix_pct` and
    # `included_energy_share_pct` come back NaN for the whole zone. That is what
    # v1.2 did for NO2 and NO3 (a NaN in Waste / Other), and it is why NO4's
    # 2021 gas share read NaN rather than 0.07 %. ADR-0002 already says a NaN in
    # a negligible type is a zero, not data loss; this makes the mix obey it.
    all_energy = df[occurring][clean].fillna(0.0).clip(lower=0).mul(d, axis=0)
    all_tot = float(all_energy.to_numpy().sum())
    mix = (all_energy.sum() / all_tot * 100).sort_values(ascending=False)
    included_share = energy.to_numpy().sum() / all_tot * 100 if all_tot else float("nan")

    return {
        "ci": ci,
        "ci_min": float(ici.min()) if len(ici) else float("nan"),
        "ci_max": float(ici.max()) if len(ici) else float("nan"),
        "n_total": int(len(clean)),
        "n_clean": int(clean.sum()),
        "coverage_pct": clean.sum() / len(clean) * 100 if len(clean) else float("nan"),
        "included": included,
        "material": material,
        "negligible": negligible,
        "missing_factor": missing_factor,
        "unfactored": unfactored,
        "carried_at_zero": bool(carry_unfactored_at_zero),
        "included_energy_share_pct": included_share,
        "mix_pct": mix,
        "interval_ci": ici,
    }


def ci_series(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR):
    """Per-interval CI (gCO2eq/kWh) as a pandas Series — ADR-0001+0002.

    Materiality (ADR-0002): NaN in a negligible type -> 0; an interval is NaN in the
    series only if a MATERIAL type is NaN. Used by the forecast layer (ADR-0004).
    """
    import pandas as _pd
    occurring = list(df.columns)
    included = [c for c in occurring if c in factors and c not in excluded]
    zone_total_mean = float(df[occurring].mean().sum())
    material = []
    for c in included:
        tm = float(df[c].mean())
        sh = (tm / zone_total_mean * 100) if zone_total_mean else 0.0
        if sh >= MATERIAL_MIN_SHARE_PCT and tm >= MATERIAL_MIN_MW:
            material.append(c)
    clean = df[material].notna().all(axis=1) if material else _pd.Series(True, index=df.index)
    sub = df[included].fillna(0.0).clip(lower=0)
    num = sum(sub[c] * factors[c] for c in included)
    den = sub.sum(axis=1)
    ci = (num / den).where(den > 0)
    return ci.where(clean)


def compute_sensitivity(df):
    """Like compute(), but includes Waste/Other/Other renewable on flagged proxies."""
    factors2 = dict(FACTORS)
    for t, (f, _note) in SENSITIVITY_PROXY.items():
        factors2[t] = f
    return compute(df, factors=factors2, excluded=set())


def run_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    for zid in ["NO1", "NO2", "NO3", "NO4", "NO5"]:
        paths = glob.glob(os.path.join(RAW_DIR, f"{zid}_generation_2025.csv"))
        if not paths:
            print(f"{zid}: MISSING raw file"); continue
        df = load_zone(paths[0])
        r = compute(df)
        s = compute_sensitivity(df)
        r["ci_sensitivity"] = s["ci"]
        rows.append((zid, r))
        # per-zone interval time series
        r["interval_ci"].rename("CI_gCO2_per_kWh").to_csv(
            os.path.join(OUT_DIR, f"{zid}_interval_ci_2025.csv"))
    return rows
