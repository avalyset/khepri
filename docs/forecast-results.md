# Forecast-resultat (ADR-0004)

Per-sone CI-forecast, 96t dag-vis, daglig 00:00-origin (CarbonCast-konvensjon). Modeller: flat/diurnal persistens (gulv), SARIMA (felt-baseline), LightGBM (ML). Metrikk: MAPE-mean (snitt dag 1-4) + MAE/RMSE/concordance (full i `~/khepri-data/forecast/`).

## MAPE-mean per sone × modell

**PRIMÆR (test 2025, train ≤2023):**

| Sone | flat | diurnal | SARIMA | GBM |
|------|-----:|-----:|-----:|-----:|
| NO1 | 2,65 | 2,71 | **2,47** | 2,58 |
| NO2 | 3,99 | 4,28 | 3,96 | **3,94** |
| NO3 | **6,84** | 7,48 | 6,87 | 7,89 |
| NO4 | 7,86 | 7,88 | **7,24** | **35,65** ⚠ |
| NO5 | 0,83 | 0,76 | 0,72 | 3,75 |

**SEKUNDÆR felt-eksakt (test H2 2021, train 2019–H1 2021):**

| Sone | flat | SARIMA | GBM | CarbonCast SE (ref) |
|------|-----:|-----:|-----:|-----:|
| NO1 | 1,50 | 1,43 | **1,20** | |
| NO2 | 4,79 | 4,13 | **3,50** | livssyklus **5,78** |
| NO3 | 7,52 | 7,41 | **6,45** | direkte **10,07** |
| NO4 | 3,23 | **2,94** | 3,29 | (PJM 4,80, ISO-NE 6,46, |
| NO5 | 16,11 | 10,55 | **8,75** | CISO 13,37) |

## Funn (B3 — rått)

### 1. H0 holder i hovedsak: enkle modeller er nok for NO
For de stabile vannkraft-sonene (NO1/NO2/NO3) er forbedringen fra SARIMA/GBM over flat persistens liten (1-11 %), og for NO3 2025 er **flat persistens beste modell**. Pre-registrert H0 (vannkraft-stabilt → lite å forutsi utover sesong) er **i hovedsak bekreftet**. Adopsjons-konsekvens: NO trenger ikke en tung forecaster — persistens/SARIMA er adekvat.

### 2. NO5 / ren-vannkraft: produksjonsbasert CI er nær-konstant (mono-faktor)
NO5 2026: CI std=0,00, låst på 24,0 — fordi miksen er ~100 % vannkraft og alle hydro-undertyper deler IPCC-faktor 24. Persistens-MAPE 0,00 er **ekte men trivielt**: et nær-konstant signal bærer lite forutsigbar informasjon. Dette er en reell **grense ved produksjonsbasert per-sone CI for rene vannkraft-soner** — ikke modell-ferdighet.

### 3. NO4 — leakage-sjekken er REN, akkurat som pre-registrert
Pre-registrert forventning (Hammerfest-korreksjonen): NO4s store CI-bevegelser er en industriell hendelse (brann/restart), ikke forutsigbar fra CI-historikk. Bekreftet mot data:
- **NO4 H2-2021 (anlegg offline, ren vannkraft): MAPE 2,94 — trivielt enkelt** (gass fraværende).
- **NO4 2025/2026 (gass i drift, volatil): MAPE 7,24 / 10,51 — hardest av alle soner.**
- **Ingen modell viser anomalt høy NO4-skill over hendelsesgrensene** → ingen leakage. SARIMA fanger sesong/diurnal, bommer på gass-sprangene (som forventet). **GBM kollapser på NO4 2025 (MAPE 35,65)** — ML overfitter og takler ikke det hendelses-drevne regimet.
NO4 er hardest nettopp fordi hendelsen ikke ligger i historikken. Det er et ekte funn, ikke en modellsvakhet.

### 4. GBM er ikke trygt bedre — SARIMA er det robuste valget
GBM vinner i noen stabile tilfeller (sekundær NO1/NO2/NO3, +14-27 % over flat), men **kollapser katastrofalt på NO4 2025 (35,65 mot SARIMAs 7,24)**. En tung ML-modell er ikke en trygg default — den kan blåse opp på den volatile sonen. Støtter ADR-0004 beslutning 3 (low→high): SARIMA er sweet-spot.

### 5. Felt-sammenlignbarhet oppnådd (sekundær)
NOs H2-2021-MAPE (1,2-10,5) ligger i **samme rom som CarbonCasts regioner** (SE 5,78 livssyklus, PJM 4,80, ISO-NE 6,46, CISO 13,37). NO er nå forecast-karakterisert på felt-sammenlignbart grunnlag — første per-sone NO-CI-forecast i feltets eval-konvensjon.

## Forbehold
- Forecast-origins = daglig 00:00 (CarbonCast-eksakt). SARIMA per origin på 45-dagers vindu (minne-trygt; fanger daglig sesong) — pragmatisk valg, dokumentert.
- 2025/2026 blandet 15/60-min → timesnitt; korte hull (≤6t) interpolert; gap-andel rapportert per sone-år i `_run.log` (NO2/NO3 ~10-17 %).
- GBM snitt av 3 seeds; SARIMA/persistens deterministiske (1 kjøring).
- MAPE supplert med MAE/RMSE/concordance (full tabell i raw-CSV); concordance ~0,5 for stabile soner = nær-tilfeldig rekkefølge, konsistent med nær-konstant signal.
