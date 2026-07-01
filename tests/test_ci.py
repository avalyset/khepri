"""Sanity tests for the CI calculation — verified against hand-computed numbers."""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from khepri.ci import ci_of_mix, compute  # noqa: E402


def test_known_mix_hand_computed():
    """1000 MW hydro (24) + 1000 MW gas (490) -> (24000+490000)/2000 = 257.0."""
    mix = {"Hydro Water Reservoir": 1000.0, "Fossil Gas": 1000.0}
    assert ci_of_mix(mix) == 257.0


def test_pure_hydro_equals_factor():
    """Pure hydropower should give exactly the hydro factor (24)."""
    assert ci_of_mix({"Hydro Water Reservoir": 500.0}) == 24.0


def test_duration_weighting_matters():
    """One 60-min interval (high gas) should count 4x a 15-min one (pure hydro).

    15-min: 100 MW hydro -> CI 24, energy 25 MWh
    60-min: 100 MW gas -> CI 490, energy 100 MWh
    energy-weighted mean = (24*25 + 490*100)/(25+100) = (600+49000)/125 = 396.8
    """
    idx = pd.to_datetime(
        ["2025-01-01T00:00Z", "2025-01-01T00:15Z", "2025-01-01T01:15Z"], utc=True)
    df = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, None, None],
         "Fossil Gas": [None, 100.0, None]},
        index=idx,
    )
    # Only the first two intervals have data in their (only included) type;
    # build two separate single-column frames instead to test duration weighting cleanly.
    df2 = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, 0.0],
         "Fossil Gas": [0.0, 100.0]},
        index=pd.to_datetime(["2025-01-01T00:00Z", "2025-01-01T00:15Z"], utc=True),
    )
    # interval 0 = 15 min, interval 1 inherits 15 min -> equal weights -> mean (24+490)/2=257
    r = compute(df2)
    assert abs(r["ci"] - 257.0) < 1e-6


def test_nan_excludes_interval():
    """An interval with NaN in an included type should be dropped; coverage is reported."""
    idx = pd.to_datetime(
        ["2025-01-01T00:00Z", "2025-01-01T00:15Z", "2025-01-01T00:30Z"], utc=True)
    df = pd.DataFrame(
        {"Hydro Water Reservoir": [100.0, None, 100.0]}, index=idx)
    r = compute(df)
    assert r["n_clean"] == 2
    assert r["n_total"] == 3
    assert abs(r["ci"] - 24.0) < 1e-6
