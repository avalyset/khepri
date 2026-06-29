# ADR-0004: Forecast-metode for per-sone CI

Status: Vedtatt
Dato: 2026-06-29
Bygger på: ADR-0001, ADR-0002, ADR-0003

## Kontekst
Adopsjonslaget (karbon-bevisst scheduling) trenger multi-døgns per-sone CI-prognose. Feltets eval-konvensjon er hentet fra primærkilder (CarbonCast BuildSys 2022, EnsembleCI arXiv 2505.01959, LiteCast arXiv 2511.06187) og styrer beslutning 2 og 4 — vi matcher feltet for sammenlignbarhet, ikke egen gjetting. NO er fraværende i alle tre (fil-belagt) — dette er bidraget.

## Pre-registrerte beslutninger (låst før resultat)

### 1. Prognose-mål
- Per sone (NO1–NO5), CI (gCO2eq/kWh, ADR-0001+0002-metoden), horisont 96 timer dag-vis (dag-1: 0-24t ... dag-4: 72-96t), timeoppløsning. Matcher CarbonCast/EnsembleCI-konvensjonen eksakt.
- Sliding-window (24t inn → neste 24t), snitt av 3 kjøringer for stokastiske modeller (CarbonCast §4.1-konvensjon). Deterministiske modeller (persistens, SARIMA): 1 kjøring.

### 2. Baseliner (feltets faktiske benchmark, ikke gjetting)
- Primær baseline å slå: **SARIMA** (Seasonal-ARIMA) — CarbonCasts egen SOTA-baseline (SOTA₁).
- Persistens inkluderes som gulv (LiteCast-presedens), ikke som hovedbaseline.
- Hvis CarbonCast-implementasjon kjørbar på NO-data: rapporter mot den som de-facto SOTA. Hvis ikke (akademisk repo, frosset main — jf. recon): SARIMA + persistens er ærlig benchmark, og fraværet av kjørbar CarbonCast-NO dokumenteres.
- B3: en forecast som ikke slår SARIMA er ikke et bidrag, rapporteres rett.

### 3. Modell-tilnærming
- Kompleksitet low→high, låst rekkefølge: SARIMA-baseline først, så evt. ML (gradient-boosting, jf. EnsembleCI LightGBM/CatBoost) kun hvis enkel modell dokumentert utilstrekkelig. Ikke hopp til tung modell uten at enklere er prøvd og rapportert.
- Predikere generation-per-type→avled CI, eller CI direkte: begge tillatt, rapporter hvilken og hvorfor.

### 4. Metrikk (forankret i felt + lav-CI-supplement)
- Primær: **MAPE** (mean/median/90./95.-persentil) — feltets standard, direkte sammenlignbar med CarbonCasts SE-tall (5,78 % livssyklus / 10,07 % direkte), nærmeste publiserte lav-CI-vannkraft-parallell.
- Supplement (pre-registrert, ikke post-hoc): **MAE + RMSE**, fordi norsk CI er lavt (~20-40) og MAPE er dokumentert ustabil i lav/volatile regimer (LiteCast: opptil 49 % Danmark). Begrunnelse forankret i LiteCast, ikke gjetting.
- Ranking-metrikk (**concordance-index**, LiteCast): rapporteres for scheduling-relevans (rett rekkefølge av rene/skitne timer betyr mer for adopsjon enn absolutt feil).
- Per sone, per dag-horisont (dag 1-4).

### 5. Split (DOBBEL: drift-bevisst primær + felt-eksakt sekundær)

**PRIMÆR (drift-bevisst):** train 2021-2023, validér 2024, test 2025; H1-2026 urørt slutt-test. Rapporter forecast-skill SEPARAT for drift-soner (NO4/NO5) vs stabile (NO1/NO2/NO3). Test eksplisitt om modellen fanger gass-drevet variasjon eller bare sesong. Begrunnelse: ADR-0003 viste NO4/NO5 strukturell drift post-2021; en pre-drift-test ville evaluere et ikke-representativt regime.

**SEKUNDÆR (felt-eksakt comparability-anker):** train 2019–H1 2021, test H2 2021 — replikerer CarbonCast/EnsembleCI eksakt for ett direkte-sammenlignbart MAPE-tall mot deres SE-tall (5,78 livssyklus / 10,07 direkte). Tydelig merket SEKUNDÆR/comparability. NB (verifisert mot data, ikke antatt): NO4 H2-2021 er i Hammerfest-LNG-driftsstansen — anlegget var offline etter brann sept. 2020, restart juni 2022 — så NO4-gass var ~2 MW i 2021 (mot ~194 MW i 2019). Det er IKKE «pre-gass»: gass fantes 2019-2020. H2-2021-tallet er for sammenlignbarhet, ikke drift-evaluering, og NO4 er da i et anomalt lav-gass-vindu (driftsstans), ikke et normalt regime.

Sammenlignbarhet bevares på **metrikk/horisont/format** (MAPE, 96t dag-vis, persentiler), ikke på test-periode. Ingen leakage: testsett røres ikke før endelig evaluering.

### 6. Null-hypotese (eksplisitt)
- H0: en enkel modell slår ikke SARIMA-baselinen meningsfullt for NO-soner (vannkraft-stabilt → lite å forutsi utover sesong).
- For drift-sonene (NO4/NO5) sekundær H0: ingen modell fanger gass-drevet drift bedre enn sesong.
- Negativt resultat (sesong/SARIMA er nok) er ekte funn med konsekvens: da trengs ingen tung modell i adopsjonslaget.

## Konsekvenser
- Slår modellen baseline: per-sone CI-forecast har operativ scheduling-verdi, går inn i adopsjonslaget.
- Slår den ikke: SARIMA/sesong er nok, forenkler adopsjon (rapporteres rett).
- NO blir første publiserte per-sone CI-forecast med feltets eval-konvensjon (CarbonCast-sammenlignbar), fyller det fil-belagte hullet.

## Alternativer vurdert
- 48t horisont (tidligere gjetting): forkastet, feltet bruker 96t — sammenlignbarhet krever match.
- Kun MAPE: forkastet, ustabil i lav-CI-regime (LiteCast-dokumentert); supplert MAE/RMSE/ranking.
- Kun persistens-baseline: forkastet, ikke feltets benchmark; SARIMA er SOTA-gulvet.
- H2 2021-test som ENESTE test (eksakt felt-match): forkastet, fanger ikke drift-regimet vårt eget ADR-0003 påviste; brukt som SEKUNDÆR comparability-anker ved siden av primær drift-bevisst split med separat drift-sone-rapportering.
