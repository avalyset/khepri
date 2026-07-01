"""
Drift measurement in the CI signal (ADR-0003).

Uses the ADR-0001+0002 pipeline (khepri.ci.compute) EXACTLY, per zone per year.
Measures: annual CI per zone, year-over-year change %, mix-share drift per material
type (percentage points), NO4 gas share per year, and a regime test 2021-2022 vs 2023+.
Threshold (pre-registered in ADR-0003): CI change > 15% OR mix shift > 5 pp.
"""

import os
import glob
import re

from .ci import load_zone, compute, RAW_DIR

CI_DRIFT_THRESHOLD_PCT = 15.0      # ADR-0003 decision 2
MIX_SHIFT_THRESHOLD_PP = 5.0       # ADR-0003 decision 2
ZONES = ["NO1", "NO2", "NO3", "NO4", "NO5"]


def available_years(zid):
    out = []
    for p in glob.glob(os.path.join(RAW_DIR, f"{zid}_generation_*.csv")):
        m = re.search(rf"{zid}_generation_(\d{{4}})\.csv$", p)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def zone_year_result(zid, year):
    fp = os.path.join(RAW_DIR, f"{zid}_generation_{year}.csv")
    df = load_zone(fp)
    r = compute(df)
    return r


def build():
    """Returns {zid: {year: result}} for all available zone-years."""
    data = {}
    for zid in ZONES:
        data[zid] = {}
        for y in available_years(zid):
            try:
                data[zid][y] = zone_year_result(zid, y)
            except Exception as e:
                data[zid][y] = {"error": str(e)}
    return data


def yoy_changes(ci_by_year):
    """Year-over-year CI change in %. {(y0,y1): pct}."""
    years = sorted(ci_by_year)
    out = {}
    for a, b in zip(years, years[1:]):
        if ci_by_year[a]:
            out[(a, b)] = (ci_by_year[b] - ci_by_year[a]) / ci_by_year[a] * 100
    return out


def regime_compare(ci_by_year, crisis=(2021, 2022), later=(2023, 2024, 2025)):
    """Descriptive regime comparison (ADR-0003 decision 3). Effect size, not p-value."""
    cz = [ci_by_year[y] for y in crisis if y in ci_by_year]
    lz = [ci_by_year[y] for y in later if y in ci_by_year]
    if not cz or not lz:
        return None
    mc, ml = sum(cz) / len(cz), sum(lz) / len(lz)
    pct = (mc - ml) / ml * 100 if ml else float("nan")
    return {"crisis_mean": mc, "later_mean": ml, "diff_pct": pct,
            "material": abs(pct) > CI_DRIFT_THRESHOLD_PCT}
