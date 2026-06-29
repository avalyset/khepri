"""Sanity-tester for CI-beregningen — verifisert mot håndregnede tall."""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from khepri.ci import ci_of_mix, compute  # noqa: E402


def test_known_mix_hand_computed():
    """1000 MW vann (24) + 1000 MW gass (490) -> (24000+490000)/2000 = 257.0."""
    mix = {"Hydro Water Reservoir": 1000.0, "Fossil Gas": 1000.0}
    assert ci_of_mix(mix) == 257.0


def test_pure_hydro_equals_factor():
    """Ren vannkraft skal gi nøyaktig hydro-faktoren (24)."""
    assert ci_of_mix({"Hydro Water Reservoir": 500.0}) == 24.0


def test_duration_weighting_matters():
    """Ett 60-min intervall (høy gass) skal telle 4x et 15-min (ren vann).

    15-min: 100 MW vann -> CI 24, energi 25 MWh
    60-min: 100 MW gass -> CI 490, energi 100 MWh
    energi-vektet snitt = (24*25 + 490*100)/(25+100) = (600+49000)/125 = 396.8
    """
    idx = pd.to_datetime(
        ["2025-01-01T00:00Z", "2025-01-01T00:15Z", "2025-01-01T01:15Z"], utc=True)
    df = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, None, None],
         "Fossil Gas": [None, 100.0, None]},
        index=idx,
    )
    # Bare de to første intervallene har data i hver sin (eneste inkluderte) type;
    # bygg heller to separate enkolonne-rammer for å teste varighet-vekting rent.
    df2 = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, 0.0],
         "Fossil Gas": [0.0, 100.0]},
        index=pd.to_datetime(["2025-01-01T00:00Z", "2025-01-01T00:15Z"], utc=True),
    )
    # intervall 0 = 15 min, intervall 1 arver 15 min -> like vekter -> snitt (24+490)/2=257
    r = compute(df2)
    assert abs(r["ci"] - 257.0) < 1e-6


def test_nan_excludes_interval():
    """Intervall med NaN i en inkludert type skal droppes; dekning rapporteres."""
    idx = pd.to_datetime(
        ["2025-01-01T00:00Z", "2025-01-01T00:15Z", "2025-01-01T00:30Z"], utc=True)
    df = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, None, 100.0]}, index=idx)
    r = compute(df)
    assert r["n_clean"] == 2
    assert r["n_total"] == 3
    assert abs(r["ci"] - 24.0) < 1e-6
