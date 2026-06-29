# Drift-resultat 2021–2025 (ADR-0003)

Produksjonsbasert CI per sone per år, ADR-0001+0002-pipeline. Terskel (pre-registrert i ADR-0003): år-til-år CI-endring > 15 % ELLER miks-skift > 5 pp = materiell drift.

## Årlig CI per sone (gCO2eq/kWh)

| Sone | 2021 | 2022 | 2023 | 2024 | 2025 | Verdikt |
|------|-----:|-----:|-----:|-----:|-----:|---------|
| NO1 | 23,63 | 23,31 | 23,48 | 23,45 | 23,31 | **stabil** (±1 %) |
| NO2 | 23,10 | 22,58 | 23,52 | 23,61 | 23,85 | **stabil** (<5 %) |
| NO3 | 21,65 | 20,95 | 20,89 | 20,75 | 21,46 | **stabil** (<4 %) |
| NO4 | 23,34 | 37,67 | 45,08 | 51,46 | 39,65 | **MATERIELL DRIFT** |
| NO5 | 34,90 | 28,75 | 24,93 | 25,00 | 24,46 | **MATERIELL DRIFT** |

## År-til-år endring (>15 % flagget)

- NO1/NO2/NO3: alle overganger < 5 %. Ingen flagg.
- **NO4:** 2021→22 **+61,4 %**, 2022→23 **+19,7 %**, 2023→24 +14,2 %, 2024→25 **−23,0 %**.
- **NO5:** 2021→22 **−17,6 %**, 2022→23 −13,3 %, deretter stabil.

## Regime-test: 2021-2022 (krise) vs 2023-2025

| Sone | Krise-snitt | Senere | Diff | Materiell? |
|------|-----:|-----:|-----:|---|
| NO1 | 23,47 | 23,41 | +0,2 % | nei (stabil) |
| NO2 | 22,84 | 23,66 | −3,5 % | nei |
| NO3 | 21,30 | 21,03 | +1,3 % | nei |
| NO4 | 30,51 | 45,40 | **−32,8 %** | **JA** |
| NO5 | 31,83 | 24,79 | **+28,4 %** | **JA** |

## NO4 — driveren målt (ikke jaget): gass-andel per år

KORRIGERT med 2019-2020-data (se «Korreksjon» under): driveren er Hammerfest-LNG-driftsstansen, ikke en ny gass-ramp.

| År | Fossil Gas snitt MW | Fossil Gas % av miks | CI | Hammerfest-LNG-status |
|----|-----:|-----:|-----:|---|
| 2019 | 194 | — | (utenfor primær-vindu) | normal drift |
| 2020 | 124 | — | — | brann sept. 2020 → stans |
| 2021 | 2 | ~0,07 % | 23,34 | **offline hele året** |
| 2022 | 111 | 3,14 % | 37,67 | restart 2. juni 2022 |
| 2023 | 152 | 4,78 % | 45,08 | full drift |
| 2024 | 168 | 6,23 % | 51,46 | full drift |
| 2025 | 105 | 3,63 % | 39,65 | drift |

NO4s CI følger Hammerfest LNG (Melkøya) sine gassturbiner. Anlegget stengte etter brann i sept. 2020, var offline ~20 mnd, og restartet 2. juni 2022 ([kilde](https://maritime-executive.com/article/lng-production-resumes-at-hammerfest-20-months-after-fire)). 2021-kollapsen (2 MW) er driftsstansen; «rampen» 2022-2024 er **gjenoppretting etter brannen**, ikke ny vekst.

### Korreksjon (R15 / B3)
Et tidligere utkast (commit 1ac6b96, pushet) beskrev NO4 som «Melkøya-gass-rampe 2022-24» og 2021 som «ingen gass-kolonne». Begge er feil: gass fantes (~194 MW) i 2019, og 2021-lavpunktet er en branndrevet driftsstans, ikke en baseline. Drift-analysen på 2021-2025 *alene* mistolket 2021-anomalien som utgangspunktet; pre-2021-data avslørte feilen. **Selve drift-tallene (CI per år, H0 forkastet for NO4) står — kun den kausale forklaringen er korrigert: hendelses-drevet driftsstans/gjenoppretting, ikke strukturell vekst.** Konsekvens for forecast: NO4s «drift» er en uforutsigbar industriell hendelse (brann), ikke en glatt trend — vanskeligere å forutsi enn sesong.

## Verdikt (H0: stabilt signal, fjorårs-CI god proxy)

- **NO1, NO2, NO3: H0 holder.** ±5 % over fem år. Fjorårs-CI er god proxy; årlig oppdatering holder for adopsjonslaget.
- **NO4, NO5: H0 forkastet.** Materiell drift over 15 %-terskelen. Fjorårs-CI er IKKE en trygg proxy — disse krever hyppigere oppdatering, og driften må dokumenteres i codecarbon-integrasjonen.

## NO5 — driver identifisert (nærsjekk, R15)

NO5s drift (34,90 → 24,46) er **gass-utfasing — speilbilde av NO4**. Fossil Gas falt 2,33 % (2021) → 0,10 % (2025); ved faktor 490 gir det −10,9 gCO2, som nesten eksakt forklarer CI-fallet på −10,4 gCO2. NO5 konvergerer mot den rene vannkraft-baselinen (~24) etter hvert som gassen fases ut.

| År | Fossil Gas % | CI | Hydro % | Total (TWh) | Dekning |
|----|-----:|-----:|-----:|-----:|-----:|
| 2021 | 2,33 | 34,90 | 90,2 | 31,0 | 100 % |
| 2022 | 1,02 | 28,75 | 96,4 | 27,6 | 100 % |
| 2023 | 0,20 | 24,93 | 96,3 | 30,2 | 100 % |
| 2024 | 0,21 | 25,00 | 96,6 | 32,2 | 100 % |
| 2025 | 0,10 | 24,46 | 96,7 | 32,1 | 94 % |

Utelukket: ikke dekningsartefakt (2021 = 100 %). De store flaggede miks-skiftene (Pumped Storage −4,1 pp, Run-of-river +5,2 pp) er CI-nøytrale — begge vannkraft (faktor 24), en ENTSO-E-omklassifisering. Den faktiske driveren er det mindre gass-skiftet, fordi gass har ~20× høyere faktor. 2021 var også et tørrere år (lavest hydro absolutt, 27,95 TWh) — konsistent kontekst, men gassen er CI-driveren.

→ Begge drift-utliggere forklart av samme mekanisme (fossil gass): NO4 rampe opp, NO5 fasing ned.

## Forbehold (B3)
- NO4 2021 mangler Fossil Gas-kolonne (gass ikke rapportert/produsert da) → first-vs-last miks-drift-oppsummering undertelte NO4; den korrekte utviklingen er per-års-gasstabellen over.
- 2021–2024 = 100 % dekning (hourly). 2025 = 88–100 % (blandet oppløsning, ADR-0002-håndtert). Drift-sammenligningen står på solid dekning.
- Deskriptiv regime-sammenligning (effektstørrelse mot terskel), ikke p-verdi — per ADR-0003 beslutning 3.
