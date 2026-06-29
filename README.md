# Khepri

Når jeg først jobber med AI på mange felt, skulle det bare mangle å bidra her òg.

## Hva det er

Et lisens-rent, reproduserbart **per-sone karbonintensitet-signal for de norske budområdene NO1–NO5**, til bruk i karbon-bevisst databehandling. Karbonintensiteten avledes deterministisk fra:

- **ENTSO-E** Actual Generation per Production Type (A75), per budområde, og
- **publiserte livssyklus-utslippsfaktorer** (IPCC AR5 Annex III, sitert).

## Hva det erstatter

Verktøy som [codecarbon](https://github.com/mlco2/codecarbon) bruker i dag en **uniform statisk verdi på 18,0 gCO2eq/kWh for alle fem norske budområdene**
(`codecarbon/data/private_infra/nordic_emissions.json`, verifisert mot installert v3.2.8). Den verdien skiller ikke sonene fra hverandre og er ikke avledet per sone. Khepri produserer **distinkte, kildesporbare per-sone-verdier** i stedet.

Metoden — og hver frihetsgrad i den — er låst i [docs/decisions/0001-ci-beregningsmetode.md](docs/decisions/0001-ci-beregningsmetode.md) før beregning, slik at tallene er etterprøvbare og ikke etter-rasjonaliserte.

## Lisens (splittet)

- **Kode:** Apache-2.0 — se [LICENSE](LICENSE).
- **Data og dokumentasjon:** CC-BY-4.0 — se [LICENSE-DATA](LICENSE-DATA).

Rådata fra ENTSO-E committes ikke til dette repoet (se `.gitignore`); de hentes reproduserbart via API.

## Status

Tidlig. Produksjonsbasert per-sone-CI er førstesteget; konsumbasert/flow-traced lag er en separat, senere beslutning (egen ADR). Ingenting her overselges — se ADR-ene for hva som faktisk er avgjort og hva som er åpent.
