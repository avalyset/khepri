"""
Per-zone CI forecast (ADR-0004).

Horizon 96h day-wise, forecast origin daily at 00:00 (CarbonCast convention:
"predict the next 96 hours at 00:00"). Baselines: flat + diurnal persistence (floor),
SARIMA (the field's SOTA baseline to beat). Models: SARIMA itself, + a light GBM
(LightGBM) to test whether ML beats it (ADR-0004 decision 3, low->high).

Metrics per (zone, model, split, day-horizon): MAPE (mean/median/90th/95th pct),
MAE, RMSE, concordance index (LiteCast, ranking relevance for scheduling).

NO4 EXPECTATION (pre-registered, ADR-0004 correction): NO4's large CI movements
track a step change in its fossil-gas share (near zero in 2021, 6.23% in 2024,
3.63% in 2025), not a smooth trend. A model should NOT be able to predict these
steps from CI history alone. High NO4 skill across the step boundaries =>
suspect leakage, not skill.

VERSION 1.5 CORRECTIONS (2026-10-01; ADR-0004 and ADR-0008 addenda). Three
departures from the registered design were found at journal revision and are
corrected here. The published 1.4 runs are reported next to the corrected ones in
docs/forecast-results.md and docs/se-forecast-results.md.
  (i)   History: eval_split loaded only the training years plus the test year, so in
        the Swedish split 2024 was absent and the gap was filled forward with the last
        value. It now loads every year from the first training year through the test
        year (`history_years`).
  (ii)  GBM training origins: the window was anchored at test_start - 400 days and cut
        at train_end, which left 34 origins (28 Nov-31 Dec 2023) instead of 365, and let
        targets of the last origins reach past train_end. It is now the last 365 daily
        origins whose 96-h targets all lie at or before train_end
        (`gbm_train_origins`).
  (iii) SARIMA fallback: a failed apply()/forecast() was replaced by diurnal
        persistence without a trace. The substitution is kept, but it is now logged,
        flagged per row (`fallback`) and counted in the return value.
The hour-of-day features (sin/cos of the origin hour) were removed: the origin is
always 00:00, so they were constant and received no splits.
"""

import logging
import os
import warnings
import numpy as np
import pandas as pd

from .ci import load_zone, ci_series, RAW_DIR

warnings.simplefilter("ignore")
log = logging.getLogger(__name__)
OUT_DIR = os.environ.get("KHEPRI_FC_OUT", os.path.expanduser("~/khepri-data/forecast"))
H = 96  # horizon (hours)


def hourly_ci(zone, years):
    """Contiguous hourly-resolution CI series for a zone over the given years."""
    parts = []
    for y in years:
        fp = os.path.join(RAW_DIR, f"{zone}_generation_{y}.csv")
        if not os.path.exists(fp):
            continue
        df = load_zone(fp)
        s = ci_series(df)
        parts.append(s)
    if not parts:
        return None
    s = pd.concat(parts).sort_index()
    s = s[~s.index.duplicated(keep="first")]
    # hourly resolution (2025 is mixed 15/60 -> hourly mean); reindex to a full hourly series
    s = s.resample("1h").mean()
    full = pd.date_range(s.index.min(), s.index.max(), freq="1h", tz="UTC")
    s = s.reindex(full)
    # short gaps interpolated (the forecast needs contiguous history); long-gap fraction reported
    gap_frac = s.isna().mean()
    s = s.interpolate(limit=6).ffill().bfill()
    return s, gap_frac


# ---------- baselines & models ----------
def fc_flat(hist, origin):
    v = hist.loc[origin]
    return np.full(H, v)


def fc_diurnal(hist, origin):
    # repeat the last 24h profile 4 times
    last24 = hist.loc[origin - pd.Timedelta(hours=23): origin].values
    if len(last24) < 24:
        return np.full(H, hist.loc[origin])
    return np.tile(last24[-24:], 4)[:H]


# SARIMA is rolled incrementally in eval_split (append per day), not re-applied per origin.


def build_gbm(hist, train_origins):
    import lightgbm as lgb
    X, y = [], []
    for o in train_origins:
        feats_base = _features(hist, o)
        for h in range(1, H + 1):
            tgt_t = o + pd.Timedelta(hours=h)
            if tgt_t not in hist.index or pd.isna(hist.loc[tgt_t]):
                continue
            X.append(feats_base + [h])
            y.append(hist.loc[tgt_t])
    if not X:
        return None
    models = []
    for seed in (0, 1, 2):  # mean of 3 runs (stochastic)
        m = lgb.LGBMRegressor(n_estimators=200, num_leaves=31, learning_rate=0.05,
                              random_state=seed, verbose=-1)
        m.fit(np.array(X), np.array(y))
        models.append(m)
    return models


def _features(hist, origin):
    # origin calendar + recent CI lags (24h). The origin is always 00:00, so no
    # hour-of-day feature: it would be constant (removed in 1.5, see module docstring).
    feats = [origin.dayofweek, origin.month, float(hist.loc[origin])]
    lags = hist.loc[origin - pd.Timedelta(hours=24): origin].values[-24:]
    feats += list(lags) if len(lags) == 24 else [float(hist.loc[origin])] * 24
    return feats


def fc_gbm(models, hist, origin):
    base = _features(hist, origin)
    Xo = np.array([base + [h] for h in range(1, H + 1)])
    preds = np.mean([m.predict(Xo) for m in models], axis=0)
    return preds


# ---------- metrics ----------
def mape(a, f):
    a = np.asarray(a, float); f = np.asarray(f, float)
    mask = np.abs(a) > 1e-6
    return np.mean(np.abs((a[mask] - f[mask]) / a[mask])) * 100 if mask.any() else np.nan


def cindex(a, f):
    """Concordance: fraction of pairs the forecast ranks in the same order as actual."""
    a = np.asarray(a, float); f = np.asarray(f, float)
    n = len(a); c = t = 0
    for i in range(n):
        for j in range(i + 1, n):
            da, df_ = a[i] - a[j], f[i] - f[j]
            if da == 0:
                continue
            t += 1
            if (da > 0) == (df_ > 0):
                c += 1
    return c / t if t else np.nan


def actual_window(hist, origin):
    idx = [origin + pd.Timedelta(hours=h) for h in range(1, H + 1)]
    return hist.reindex(idx).values


def history_years(train_years, test_end):
    """Every year from the first training year through the test year (1.5 correction (i))."""
    return list(range(min(train_years), test_end.year + 1))


def gbm_train_origins(hist, train_end, n=365):
    """The last `n` daily 00:00 origins whose H-hour targets all lie at or before
    `train_end` (1.5 correction (ii)): the last origin is the day of train_end - H."""
    last = (train_end - pd.Timedelta(hours=H)).normalize()
    cand = pd.date_range(last - pd.Timedelta(days=n - 1), last, freq="1D", tz="UTC")
    return [o for o in cand if o in hist.index][-n:]


def eval_split(zone, train_years, train_end, test_start, test_end, models_on=True):
    """Evaluate all models on one zone split.

    Returns (rows, n_origins, gap_fraction, sarima_fitted, gbm_trained, n_sarima_fallback).
    The sixth element is new in 1.5: the number of origins where SARIMA apply()/forecast()
    failed and diurnal persistence was substituted; those SARIMA rows carry fallback=True.
    """
    res = hourly_ci(zone, history_years(train_years, test_end))
    if res is None:
        return None
    hist, gap = res
    # origins = daily 00:00 in the test period with a full 96h ground truth
    origins = [o for o in pd.date_range(test_start, test_end, freq="1D", tz="UTC")
               if o in hist.index and (o + pd.Timedelta(hours=H)) <= hist.index.max()]
    # SARIMA fit on the training part
    fitted = None
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        tr = hist.loc[:train_end]
        fitted = SARIMAX(tr, order=(2, 0, 1), seasonal_order=(1, 1, 0, 24),
                         enforce_stationarity=False, enforce_invertibility=False
                         ).fit(disp=False, maxiter=50)
    except Exception as e:
        fitted = None
        log.warning("%s: SARIMA fit failed, no SARIMA rows: %r", zone, e)
    gbm = None
    if models_on:
        train_origins = gbm_train_origins(hist, train_end)
        gbm = build_gbm(hist, train_origins) if train_origins else None

    # SARIMA per origin on a bounded 45-day window (memory-safe, captures daily seasonality)
    WIN = pd.Timedelta(days=45)
    rows = []
    n_fallback = 0
    for o in origins:
        actual = actual_window(hist, o)
        if np.isnan(actual).any():
            continue
        preds = {"flat": fc_flat(hist, o), "diurnal": fc_diurnal(hist, o)}
        fell_back = False
        if fitted is not None:
            try:
                w = hist.loc[o - WIN: o]
                preds["SARIMA"] = np.asarray(fitted.apply(w).forecast(H))
            except Exception as e:
                preds["SARIMA"] = fc_diurnal(hist, o)
                fell_back = True
                n_fallback += 1
                log.warning("%s %s: SARIMA apply/forecast failed, diurnal persistence "
                            "substituted (counted, row flagged): %r", zone, o, e)
        if gbm is not None:
            preds["GBM"] = fc_gbm(gbm, hist, o)
        for model, f in preds.items():
            for day in range(4):
                sl = slice(day * 24, (day + 1) * 24)
                a, p = actual[sl], np.asarray(f)[sl]
                rows.append({"zone": zone, "model": model, "day": day + 1,
                             "mape": mape(a, p), "mae": np.mean(np.abs(a - p)),
                             "rmse": np.sqrt(np.mean((a - p) ** 2)), "cidx": cindex(a, p),
                             "fallback": bool(model == "SARIMA" and fell_back)})
    df = pd.DataFrame(rows)
    return df, len(origins), gap, (fitted is not None), (gbm is not None), n_fallback
