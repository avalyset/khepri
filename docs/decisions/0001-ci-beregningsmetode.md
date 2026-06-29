# ADR-0001: CI-beregningsmetode for norske budområder (NO1–NO5)

- **Status:** Vedtatt
- **Dato:** 2026-06-29

## Kontekst

Vi avleder per-sone karbonintensitet (CI, gCO2eq/kWh) for NO1–NO5 fra ENTSO-E
Actual Generation per Production Type (A75) og publiserte livssyklus-faktorer.
Beregningen er aritmetisk, men har fire metodevalg med frihetsgrad. De festes
**før** beregning, slik at tallene er etterprøvbare og ikke etter-rasjonaliserte.
Hver faktor og hver datakarakteristikk er verifisert mot navngitt kilde (ikke fra
hukommelse) — se loggen i § "Verifisering".

## Beslutning 1 — Faktorkilde

**IPCC WG3 AR5 Annex III, Table A.III.2** — livssyklus-medianer (gCO2eq/kWh).
Livssyklus, ikke direkte drift. IPCC-primær-PDF er ikke direkte nåbar fra
byggemiljøet; verdiene er hentet fra en **sjekkbar sekundærkilde som navngir
tabellen** (Wikipedia: *Life-cycle greenhouse gas emissions of energy sources*,
kolonnen som siterer IPCC Annex III Table A.III.2). Dette er eksplisitt en
sekundærkilde — normal praksis så lenge den navngis. Coal=820 / gas=490 er
uavhengig bekreftet mot IPCC-dokumentets egen PDF-URL via søk.

Hver faktor er sitert per rad i `src/khepri/factors.py`. Faktortabell (typer som
faktisk forekommer i NO 2025-data):

| Produksjonstype | gCO2eq/kWh | Mapping |
|---|---|---|
| Fossil Gas | 490 | IPCC 'Gas – combined cycle' (direkte) |
| Hydro Water Reservoir | 24 | IPCC 'Hydropower' (direkte) |
| Hydro Run-of-river and poundage | 24 | IPCC 'Hydropower' (én hydro-kategori) |
| Hydro Pumped Storage | 24 | **PROXY** hydro; fotavtrykk avhenger av ladekilde |
| Wind Onshore | 11 | IPCC 'Wind onshore' (direkte) |
| Wind Offshore | 12 | IPCC 'Wind offshore' (direkte) |
| Solar | 48 | IPCC 'Solar PV – utility' (direkte) |
| Biomass | 230 | IPCC 'Biomass – dedicated' (direkte) |

## Beslutning 2 — NaN / manglende data

Intervaller med **NaN i en inkludert (faktor-bærende) produksjonstype
EKSKLUDERES** fra CI-snittet (valg a). NaN ≠ 0. **Dekningsgrad** (% intervaller
brukt etter eksklusjon) rapporteres som provenans per sone. En type som er
fraværende i en sone (ikke en kolonne) bidrar med 0, ikke NaN.

**Uverifiserte typer** (Waste, Other, Other renewable) har ingen verifisert faktor
i den valgte kilden. De **ekskluderes fra primær-CI**, og effekten rapporteres som
**sensitivitet** (CI med dem inkludert på flaggede proxyer). De gjettes ikke inn i
primærtallet. Andelen av total energi disse utgjør rapporteres som dekning.

## Beslutning 3 — Produksjonsbasert

CI er **produksjonsbasert**. Import/forbruk er **eksplisitt utelatt**.
Konsumbasert / flow-traced CI er et separat, senere lag med egen ADR.

## Beslutning 4 — Varighet-vektet aggregering

2025-data har **blandet oppløsning** (15-min og 60-min perioder; verifisert på
disk). CI-snittet vektes på **intervall-VARIGHET** (timer), ikke antall
intervaller.

- CI per intervall: `Σ(MW_type × faktor_type) / Σ(MW_type)`
- Periode-snitt (energi-vektet): `Σ(MW × faktor × varighet) / Σ(MW × varighet)`

dvs. total utslipp / total energi over rene intervaller.

## Konsekvenser

- Deterministisk og reproduserbart fra rådata + denne ADR-en.
- NO-CI blir lav (vannkraft-dominert) og lite distinkt **unntatt NO4**, som har
  dokumentert fossil gass **år-rundt** (til stede i 98,8 % av 2025-intervallene,
  alle fire kvartaler) — en strukturell, ikke sesong-, egenskap.
- Erstatter codecarbons verifiserte uniforme placeholder (18,0 gCO2eq/kWh for alle
  NO-soner, `nordic_emissions.json`, v3.2.8).
- Proxy- og uverifiserte typer er eksplisitt flagget; ingen faktor gjettet inn.

## Alternativer vurdert (forkastet)

- **Direkte drifts-faktorer** — mindre sammenlignbart med livssyklus-litteraturen.
- **codecarbons egen faktortabell** — metodisk blandet (direkte fossil + WNA-
  livssyklus) og mangler biomass + waste; forkastet til fordel for konsistent
  livssyklus.
- **Uvektet snitt av intervall-CI** — energi-forvrengende.
- **Antall-vekting** — feil ved blandet 15-/60-min oppløsning.
- **NaN = 0** — kunstig; undervurderer ved manglende data.

## Verifisering

- EIC-koder NO1–NO5: identiske med `entsoe.mappings.Area`.
- psrType→navn: identiske med `entsoe.mappings.PSRTYPE_MAPPINGS`.
- Placeholder 18,0: lest direkte i installert `codecarbon` v3.2.8
  `data/private_infra/nordic_emissions.json`.
- Faktorer: se `src/khepri/factors.py` med kilde-streng per rad.
