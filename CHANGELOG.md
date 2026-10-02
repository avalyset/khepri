# Changelog

## 1.5.0 — 2026-10-02

No CI figure changes: the 2025 per-zone values are bit-identical to 1.4.0 (baseline SHA256 `a86d8dd2…`).

- `src/khepri/forecast.py`, corrected to ADR-0004/0008:
  - history: every year from the first training year through the test year is loaded (`history_years`); the Swedish split had no 2024 history and filled the gap forward;
  - GBM training origins: the last 365 daily origins whose 96-h targets all lie at or before `train_end` (`gbm_train_origins`); 1.4 trained on 34;
  - SARIMA fallback: a failed `apply()`/`forecast()` is still replaced by diurnal persistence, but logged, flagged per row (`fallback`) and counted in a sixth return value;
  - origin feature: the constant hour-of-day features are removed (the origin is always 00:00);
  - tests for all four.
- `docs/forecast-results.md`, `docs/se-forecast-results.md`: dated correction blocks with the corrected runs beside the published ones.
- `docs/drift-results-2021-2025.md`, `docs/se-drift-results-2022-2025.md`: dated correction blocks applying the mix arm as registered, in both readings; the 27 October 2021 hydro shift reported as an unconfirmed observation.
- Dated addenda to ADR-0002, ADR-0003, ADR-0004 and ADR-0008; ADR-0017 (Proposed): pumping hours as zero generation from 2.x.
- README: Findings corrected; Adoption states how the codecarbon factor basis was chosen and that the shipped values match 1.4.
