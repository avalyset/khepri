"""Sanity tests for the forecast layer (ADR-0004) — metrics + baselines, hand-computed."""

import numpy as np
import pandas as pd

from khepri.forecast import mape, cindex, fc_flat, fc_diurnal, H


def test_mape_zero_on_perfect():
    a = np.array([20.0, 30.0, 40.0])
    assert mape(a, a) == 0.0


def test_mape_known_value():
    # actual 100, forecast 110 -> 10% MAPE
    assert abs(mape(np.array([100.0]), np.array([110.0])) - 10.0) < 1e-9


def test_cindex_perfect_order():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    f = np.array([0.5, 0.9, 2.2, 5.0])  # same order
    assert cindex(a, f) == 1.0


def test_cindex_reversed():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    f = np.array([4.0, 3.0, 2.0, 1.0])  # reversed order
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
    # CI = hour-of-day, so the last 24h = 0..23 repeated
    hist = pd.Series([i % 24 for i in range(200)], index=idx, dtype=float)
    o = idx[120]
    f = fc_diurnal(hist, o)
    assert len(f) == H
    # forecast for h=1 should match the same hour in the next-day profile
    assert f[0] == hist.loc[o - pd.Timedelta(hours=23)]


# ---------- 1.5 corrections (ADR-0004 / ADR-0008 addenda, 2026-10-01) ----------

import khepri.forecast as fc


def test_history_years_spans_first_training_year_to_test_year():
    # (i) the Swedish split trains on 2022-2023 and tests on 2025: 2024 must be loaded
    assert fc.history_years([2022, 2023], pd.Timestamp("2025-12-31", tz="UTC")) == [2022, 2023, 2024, 2025]
    assert fc.history_years([2019, 2020, 2021], pd.Timestamp("2021-12-31", tz="UTC")) == [2019, 2020, 2021]


def test_gbm_train_origins_365_and_no_target_after_train_end():
    # (ii) 365 daily origins, the last one's 96-h targets end at or before train_end
    idx = pd.date_range("2021-01-01", "2025-12-31 23:00", freq="1h", tz="UTC")
    hist = pd.Series(1.0, index=idx)
    train_end = pd.Timestamp("2023-12-31 23:00", tz="UTC")
    tro = fc.gbm_train_origins(hist, train_end)
    assert len(tro) == 365
    assert tro[-1] == pd.Timestamp("2023-12-27", tz="UTC")
    assert tro[0] == pd.Timestamp("2022-12-28", tz="UTC")
    assert all(o.hour == 0 for o in tro)
    assert max(o + pd.Timedelta(hours=fc.H) for o in tro) <= train_end


def test_features_have_no_constant_hour_of_day():
    idx = pd.date_range("2025-01-01", periods=200, freq="1h", tz="UTC")
    hist = pd.Series(np.arange(200, dtype=float), index=idx)
    f = fc._features(hist, idx[48])
    assert len(f) == 3 + 24  # day of week, month, CI at origin, 24 lags
    assert f[2] == hist.loc[idx[48]]


def test_sarima_fallback_is_counted_and_flagged(monkeypatch):
    # (iii) a failing apply() is substituted by diurnal persistence, but counted and flagged
    import statsmodels.tsa.statespace.sarimax as smx

    class _Fitted:
        def apply(self, w):
            raise ValueError("forced failure")

    class _SARIMAX:
        def __init__(self, *a, **k):
            pass

        def fit(self, *a, **k):
            return _Fitted()

    idx = pd.date_range("2024-11-01", "2025-01-10 23:00", freq="1h", tz="UTC")
    hist = pd.Series(20.0 + (np.arange(len(idx)) % 24), index=idx)
    monkeypatch.setattr(fc, "hourly_ci", lambda zone, years: (hist, 0.0))
    monkeypatch.setattr(smx, "SARIMAX", _SARIMAX)
    df, n_orig, gap, sar_ok, gbm_ok, n_fb = fc.eval_split(
        "XX", [2024], pd.Timestamp("2024-12-31 23:00", tz="UTC"),
        pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2025-01-05", tz="UTC"), models_on=False)
    assert sar_ok and not gbm_ok
    assert n_fb == n_orig == 5
    s = df[df.model == "SARIMA"]
    assert len(s) == 5 * 4 and s.fallback.all()
    assert not df[df.model != "SARIMA"].fallback.any()
