"""
Drift-måling i CI-signalet (ADR-0003).

Bruker NØYAKTIG ADR-0001+0002-pipelinen (khepri.ci.compute) per sone per år.
Måler: årlig CI per sone, år-til-år endring %, miks-andel-drift per materiell
type (prosentpoeng), NO4-gass-andel per år, og regime-test 2021-2022 vs 2023+.
Terskel (pre-registrert i ADR-0003): CI-endring > 15 % ELLER miks-skift > 5 pp.
"""

import os
import glob
import re

from .ci import load_zone, compute, RAW_DIR

CI_DRIFT_THRESHOLD_PCT = 15.0      # ADR-0003 beslutning 2
MIX_SHIFT_THRESHOLD_PP = 5.0       # ADR-0003 beslutning 2
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
    """Returnerer {zid: {year: result}} for alle tilgjengelige sone-år."""
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
    """År-til-år CI-endring i %. {(y0,y1): pct}."""
    years = sorted(ci_by_year)
    out = {}
    for a, b in zip(years, years[1:]):
        if ci_by_year[a]:
            out[(a, b)] = (ci_by_year[b] - ci_by_year[a]) / ci_by_year[a] * 100
    return out


def regime_compare(ci_by_year, crisis=(2021, 2022), later=(2023, 2024, 2025)):
    """Deskriptiv regime-sammenligning (ADR-0003 beslutning 3). Effektstørrelse, ikke p-verdi."""
    cz = [ci_by_year[y] for y in crisis if y in ci_by_year]
    lz = [ci_by_year[y] for y in later if y in ci_by_year]
    if not cz or not lz:
        return None
    mc, ml = sum(cz) / len(cz), sum(lz) / len(lz)
    pct = (mc - ml) / ml * 100 if ml else float("nan")
    return {"crisis_mean": mc, "later_mean": ml, "diff_pct": pct,
            "material": abs(pct) > CI_DRIFT_THRESHOLD_PCT}
