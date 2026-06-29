# Khepri

Når jeg først jobber med AI på mange felt, skulle det bare mangle å bidra her òg.

## Hva det er

Et lisens-rent, reproduserbart **per-sone karbonintensitet-signal for de norske budområdene NO1–NO5**, til bruk i karbon-bevisst databehandling — med **ærlig drift- og forecast-karakterisering**, ikke bare fem tall. Karbonintensiteten avledes deterministisk fra:

- **ENTSO-E** Actual Generation per Production Type (A75), per budområde, og
- **publiserte livssyklus-utslippsfaktorer** (IPCC AR5 Annex III, sitert).

Dette er det første per-sone NO CI-signalet med feltets eval-konvensjon og dokumentert drift/forecast-oppførsel — ikke en påstand om at «NO CI-forecasting er løst».

## Hva det erstatter

Verktøy som [codecarbon](https://github.com/mlco2/codecarbon) bruker i dag en **uniform statisk verdi på 18,0 gCO2eq/kWh for alle fem norske budområdene** (`nordic_emissions.json`, verifisert mot installert v3.2.8). Den er for lav for alle sonene og **~2,5× for lav for NO4**, og skiller dem ikke fra hverandre. Khepri produserer distinkte, kildesporbare per-sone-verdier i stedet (2025): NO1 23,3 · NO2 23,9 · NO3 21,5 · NO4 39,6 · NO5 24,5 gCO2eq/kWh.

## Lagene (ADR-forankret)

Hver metodevalg er låst i en ADR **før** beregning — etterprøvbart, ikke etter-rasjonalisert.

1. **Datakjerne** ([ADR-0001](docs/decisions/0001-ci-beregningsmetode.md), [0002](docs/decisions/0002-nan-materialitetsterskel.md)): produksjonsbasert per-sone CI, varighet-vektet, NaN-eksklusjon.
2. **Drift** ([ADR-0003](docs/decisions/0003-drift-metode.md), [resultat](docs/drift-results-2021-2025.md)): flerårig stabilitet 2021–2025.
3. **Forecast** ([ADR-0004](docs/decisions/0004-forecast-metode.md), [resultat](docs/forecast-results.md)): 96t per-sone prognose i CarbonCast/EnsembleCI-konvensjon.
4. **Adopsjon** ([ADR-0005](docs/decisions/0005-adopsjon-codecarbon.md)): integrasjon i codecarbon.

## Hovedfunn (ærlige, ikke seire-pyntet)

- **Drift (2021–2025):** NO1/NO2/NO3 er stabile år-til-år (<5 % → årlig oppdatering nok). NO4 er **hendelses-drevet** — gassturbinene ved Hammerfest LNG var ute etter brann (sept-2020 → restart juni-2022), så NO4-CI er periodeavhengig, ikke en konstant. NO5 viser reell gass-utfasing.
- **Forecast:** **H0 holder i hovedsak** — enkle baseliner (persistens/SARIMA) er hardt å slå for de stabile sonene; tung ML er ikke trygt bedre (gradient-boosting kollapser på den volatile NO4). NO4s hendelses-sprang forutsies *ikke* (som forventet — en brann ligger ikke i CI-historikken). NOs MAPE ligger i samme rom som CarbonCasts publiserte regioner (SE 5,78).
- **Ærlig grense:** produksjonsbasert NO-CI er **lav og lite distinkt mellom soner** unntatt der fossil gass forekommer (NO4). NO5s CI er nær matematisk låst til hydro-faktoren (~24) i rene vannkraft-perioder — det er lite forutsigbar informasjon å hente. Konsumbasert/flow-traced lag (import-justert) er **ikke bygget** — en separat, senere beslutning.

## Lisens (splittet)

- **Kode:** Apache-2.0 — se [LICENSE](LICENSE).
- **Data og dokumentasjon:** CC-BY-4.0 — se [LICENSE-DATA](LICENSE-DATA).

Rådata fra ENTSO-E committes ikke til dette repoet (se `.gitignore`); de hentes reproduserbart via API.

## Status

Datakjerne + drift + forecast bygget og verifisert (internt + mot ekstern litteratur). Adopsjon (codecarbon-integrasjon) og konsumbasert lag er neste/framtidige steg. Se ADR-ene for hva som faktisk er avgjort og hva som er åpent — ingenting her overselges.
