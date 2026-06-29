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

| År | Fossil Gas % av miks | CI |
|----|-----:|-----:|
| 2021 | (ingen gass-kolonne) | 23,34 |
| 2022 | 3,14 % | 37,67 |
| 2023 | 4,78 % | 45,08 |
| 2024 | 6,23 % | 51,46 |
| 2025 | 3,63 % | 39,65 |

NO4s CI følger gasskraften (Melkøya/Hammerfest): fraværende/urapportert 2021, rampet opp 2022–2024 (topp 51,5 ved 6,2 % gass), delvis reversering 2025. Strukturell endring, ikke støy.

## Verdikt (H0: stabilt signal, fjorårs-CI god proxy)

- **NO1, NO2, NO3: H0 holder.** ±5 % over fem år. Fjorårs-CI er god proxy; årlig oppdatering holder for adopsjonslaget.
- **NO4, NO5: H0 forkastet.** Materiell drift over 15 %-terskelen. Fjorårs-CI er IKKE en trygg proxy — disse krever hyppigere oppdatering, og driften må dokumenteres i codecarbon-integrasjonen.

## Forbehold (B3)
- NO4 2021 mangler Fossil Gas-kolonne (gass ikke rapportert/produsert da) → first-vs-last miks-drift-oppsummering undertelte NO4; den korrekte utviklingen er per-års-gasstabellen over.
- NO5s drift (35→24) er reell mot terskel, men driveren er mindre entydig enn NO4s gass — fortjener egen nærsjekk (egen oppfølging, ikke konkludert her).
- 2021–2024 = 100 % dekning (hourly). 2025 = 88–100 % (blandet oppløsning, ADR-0002-håndtert). Drift-sammenligningen står på solid dekning.
- Deskriptiv regime-sammenligning (effektstørrelse mot terskel), ikke p-verdi — per ADR-0003 beslutning 3.
