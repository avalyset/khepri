"""
Per-sone karbonintensitet (CI) fra ENTSO-E generation per type.

Implementerer ADR-0001 NØYAKTIG:
  - Faktorkilde: IPCC AR5 Annex III (se factors.py).
  - Produksjonsbasert (import eksplisitt utelatt).
  - NaN-eksklusjon: intervaller med NaN i en INKLUDERT (faktor-bærende) type
    droppes fra snittet. Dekningsgrad rapporteres som provenans. NaN != 0.
  - VARIGHET-vektet: 2025-data har blandet oppløsning (15-min + 60-min).
    Energi per intervall = MW * varighet_timer; CI vektes på energi.
  - Waste/Other/Other renewable: ekskludert fra primær (ingen verifisert faktor),
    rapportert som sensitivitet.
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

# ADR-0002 — PRE-REGISTRERT materialitetsterskel (satt før re-kjøring, ikke mot dekning).
# En type er NEGLISJERBAR hvis årssnitt-bidrag < MATERIAL_MIN_SHARE_PCT av sonens
# totale miks ELLER < MATERIAL_MIN_MW absolutt. NaN i neglisjerbar type -> 0;
# intervall ekskluderes kun ved NaN i en MATERIELL type.
MATERIAL_MIN_SHARE_PCT = 0.5
MATERIAL_MIN_MW = 5.0


def ci_of_mix(mw_by_type, factors=FACTORS):
    """Ren funksjon: CI (gCO2eq/kWh) for én øyeblikks-miks. Σ(MW*f)/Σ(MW).

    Brukes av sanity-testen — håndregnbar.
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
    """Varighet (timer) per intervall = gap til neste tidsstempel.

    Siste intervall arver forrige varighet. Håndterer blandet 15-/60-min.
    """
    secs = (index[1:] - index[:-1]).total_seconds()
    dur = list(secs / 3600.0)
    dur.append(dur[-1] if dur else 1.0)
    return pd.Series(dur, index=index)


def compute(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR):
    """Energi-vektet, varighet-korrekt, NaN-ekskludert CI for én sone (ADR-0001+0002)."""
    occurring = list(df.columns)
    included = [c for c in occurring if c in factors and c not in excluded]
    missing_factor = [c for c in occurring
                      if c not in factors and c not in excluded]

    # ADR-0002: materialitet per inkludert type (mot pre-registrert terskel).
    zone_total_mean = float(df[occurring].mean().sum())  # sonens totale miks (snitt MW)
    material, negligible = [], []
    for c in included:
        type_mean = float(df[c].mean())  # snitt over ikke-NaN
        share_pct = (type_mean / zone_total_mean * 100) if zone_total_mean else 0.0
        if share_pct >= MATERIAL_MIN_SHARE_PCT and type_mean >= MATERIAL_MIN_MW:
            material.append(c)
        else:
            negligible.append(c)

    dur = _durations_hours(df.index)
    # Intervall ekskluderes KUN ved NaN i en MATERIELL type.
    clean = df[material].notna().all(axis=1) if material else df.index.to_series().apply(lambda _: True)

    # NaN i neglisjerbar type -> 0 (ikke datatap); materielle er allerede ikke-NaN her.
    sub = df[included][clean].fillna(0.0)
    g = sub.clip(lower=0)                  # MW per inkludert type, rene intervaller
    d = dur[clean]                        # timer
    energy = g.mul(d, axis=0)            # MWh per type
    tot_energy = float(energy.to_numpy().sum())
    emis = float(sum(energy[c] * factors[c] for c in included).sum())  # ∝ gCO2
    ci = emis / tot_energy if tot_energy > 0 else float("nan")

    # intervall-CI for min/maks
    gsum = g.sum(axis=1)
    erate = sum(g[c] * factors[c] for c in included)
    ici = (erate / gsum).replace([float("inf"), float("-inf")], pd.NA).dropna()

    # energi-vektet miks-andel over ALLE forekommende typer (rene intervaller)
    all_energy = df[occurring][clean].clip(lower=0).mul(d, axis=0)
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
        "included_energy_share_pct": included_share,
        "mix_pct": mix,
        "interval_ci": ici,
    }


def compute_sensitivity(df):
    """Som compute(), men inkluderer Waste/Other/Other renewable på flaggede proxyer."""
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
            print(f"{zid}: MANGLER råfil"); continue
        df = load_zone(paths[0])
        r = compute(df)
        s = compute_sensitivity(df)
        r["ci_sensitivity"] = s["ci"]
        rows.append((zid, r))
        # per-sone intervall-tidsserie
        r["interval_ci"].rename("CI_gCO2_per_kWh").to_csv(
            os.path.join(OUT_DIR, f"{zid}_interval_ci_2025.csv"))
    return rows
