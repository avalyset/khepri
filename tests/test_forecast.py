"""Sanity-tester for forecast-laget (ADR-0004) — metrikk + baseliner, håndregnet."""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from khepri.forecast import mape, cindex, fc_flat, fc_diurnal, H  # noqa: E402


def test_mape_zero_on_perfect():
    a = np.array([20.0, 30.0, 40.0])
    assert mape(a, a) == 0.0


def test_mape_known_value():
    # faktisk 100, forecast 110 -> 10% MAPE
    assert abs(mape(np.array([100.0]), np.array([110.0])) - 10.0) < 1e-9


def test_cindex_perfect_order():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    f = np.array([0.5, 0.9, 2.2, 5.0])  # samme rekkefølge
    assert cindex(a, f) == 1.0


def test_cindex_reversed():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    f = np.array([4.0, 3.0, 2.0, 1.0])  # motsatt rekkefølge
    assert cindex(a, f) == 0.0


def test_flat_persistence_is_constant():
    idx = pd.date_range("2025-01-01", periods=200, freq="1h", tz="UTC")
    hist = pd.Series(np.arange(200, dtype=float), index=idx)
    o = idx[100]
    f = fc_flat(hist, o)
    assert len(f) == H
    assert np.all(f == hist.loc[o])


def test_diurnal_repeats_last_day():
    idx = pd.date_range("2025-01-01", periods=200, freq="1h", tz="UTC")
    # CI = time-på-døgnet, så siste 24t = 0..23 gjentatt
    hist = pd.Series([i % 24 for i in range(200)], index=idx, dtype=float)
    o = idx[120]
    f = fc_diurnal(hist, o)
    assert len(f) == H
    # forecast for h=1 skal matche samme time neste dag-profil
    assert f[0] == hist.loc[o - pd.Timedelta(hours=23)]
