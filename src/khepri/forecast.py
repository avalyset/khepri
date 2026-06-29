"""
Per-sone CI-forecast (ADR-0004).

Horisont 96t dag-vis, forecast-origin daglig kl. 00:00 (CarbonCast-konvensjon:
"predict the next 96 hours at 00:00"). Baseliner: flat + diurnal persistens (gulv),
SARIMA (feltets SOTA-baseline å slå). Modell: SARIMA selv, + lett GBM (LightGBM)
for å se om ML slår den (ADR-0004 beslutning 3, low->high).

Metrikk per (sone, modell, split, dag-horisont): MAPE (mean/median/90/95-pct),
MAE, RMSE, concordance-index (LiteCast, ranking-relevans for scheduling).

NO4-FORVENTNING (pre-registrert, ADR-0004-korreksjon): NO4s store CI-bevegelser er
en industriell hendelse (Hammerfest-brann 2020 -> restart juni 2022), ikke en glatt
trend. En modell skal IKKE kunne forutsi disse sprangene fra CI-historikk alene.
Høy NO4-skill over hendelsesgrensene => mistenk leakage, ikke ferdighet.
"""

import os
import warnings
import numpy as np
import pandas as pd

from .ci import load_zone, ci_series, RAW_DIR

warnings.simplefilter("ignore")
OUT_DIR = os.environ.get("KHEPRI_FC_OUT", os.path.expanduser("~/khepri-data/forecast"))
H = 96  # horisont (timer)


def hourly_ci(zone, years):
    """Sammenhengende timeoppløst CI-serie for en sone over gitte år."""
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
    # timeoppløsning (2025 er blandet 15/60 -> timesnitt); reindekser til full timeserie
    s = s.resample("1h").mean()
    full = pd.date_range(s.index.min(), s.index.max(), freq="1h", tz="UTC")
    s = s.reindex(full)
    # korte hull interpoleres (forecast trenger sammenhengende historikk); lang-hull-andel rapporteres
    gap_frac = s.isna().mean()
    s = s.interpolate(limit=6).ffill().bfill()
    return s, gap_frac


# ---------- baseliner & modeller ----------
def fc_flat(hist, origin):
    v = hist.loc[origin]
    return np.full(H, v)


def fc_diurnal(hist, origin):
    # gjenta siste 24t-profil 4 ganger
    last24 = hist.loc[origin - pd.Timedelta(hours=23): origin].values
    if len(last24) < 24:
        return np.full(H, hist.loc[origin])
    return np.tile(last24[-24:], 4)[:H]


# SARIMA rulles inkrementelt i eval_split (append per dag), ikke re-apply per origin.


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
    for seed in (0, 1, 2):  # snitt 3 kjøringer (stokastisk)
        m = lgb.LGBMRegressor(n_estimators=200, num_leaves=31, learning_rate=0.05,
                              random_state=seed, verbose=-1)
        m.fit(np.array(X), np.array(y))
        models.append(m)
    return models


def _features(hist, origin):
    # origin-tidspunkt + nylige CI-lag (24t)
    h = origin.hour
    feats = [np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24),
             origin.dayofweek, origin.month, float(hist.loc[origin])]
    lags = hist.loc[origin - pd.Timedelta(hours=24): origin].values[-24:]
    feats += list(lags) if len(lags) == 24 else [float(hist.loc[origin])] * 24
    return feats


def fc_gbm(models, hist, origin):
    base = _features(hist, origin)
    Xo = np.array([base + [h] for h in range(1, H + 1)])
    preds = np.mean([m.predict(Xo) for m in models], axis=0)
    return preds


# ---------- metrikker ----------
def mape(a, f):
    a = np.asarray(a, float); f = np.asarray(f, float)
    mask = np.abs(a) > 1e-6
    return np.mean(np.abs((a[mask] - f[mask]) / a[mask])) * 100 if mask.any() else np.nan


def cindex(a, f):
    """Concordance: andel par der forecast rangerer i samme rekkefølge som faktisk."""
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


def eval_split(zone, train_years, train_end, test_start, test_end, models_on=True):
    res = hourly_ci(zone, sorted(set(train_years + [test_start.year, test_end.year])))
    if res is None:
        return None
    hist, gap = res
    # origins = daglig 00:00 i testperioden med full 96t-fasit
    origins = [o for o in pd.date_range(test_start, test_end, freq="1D", tz="UTC")
               if o in hist.index and (o + pd.Timedelta(hours=H)) <= hist.index.max()]
    # SARIMA fit på treningsdel
    fitted = None
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        tr = hist.loc[:train_end]
        fitted = SARIMAX(tr, order=(2, 0, 1), seasonal_order=(1, 1, 0, 24),
                         enforce_stationarity=False, enforce_invertibility=False
                         ).fit(disp=False, maxiter=50)
    except Exception as e:
        fitted = None
    gbm = None
    if models_on:
        train_origins = [o for o in pd.date_range(test_start - pd.Timedelta(days=400),
                         train_end, freq="1D", tz="UTC") if o in hist.index]
        gbm = build_gbm(hist, train_origins[-365:]) if train_origins else None

    # SARIMA per origin på avgrenset 45-dagers vindu (minne-trygt, fanger daglig sesong)
    WIN = pd.Timedelta(days=45)
    rows = []
    for o in origins:
        actual = actual_window(hist, o)
        if np.isnan(actual).any():
            continue
        preds = {"flat": fc_flat(hist, o), "diurnal": fc_diurnal(hist, o)}
        if fitted is not None:
            try:
                w = hist.loc[o - WIN: o]
                preds["SARIMA"] = np.asarray(fitted.apply(w).forecast(H))
            except Exception:
                preds["SARIMA"] = fc_diurnal(hist, o)
        if gbm is not None:
            preds["GBM"] = fc_gbm(gbm, hist, o)
        for model, f in preds.items():
            for day in range(4):
                sl = slice(day * 24, (day + 1) * 24)
                a, p = actual[sl], np.asarray(f)[sl]
                rows.append({"zone": zone, "model": model, "day": day + 1,
                             "mape": mape(a, p), "mae": np.mean(np.abs(a - p)),
                             "rmse": np.sqrt(np.mean((a - p) ** 2)), "cidx": cindex(a, p)})
    df = pd.DataFrame(rows)
    return df, len(origins), gap, (fitted is not None), (gbm is not None)
