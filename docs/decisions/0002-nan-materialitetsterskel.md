# ADR-0002: Materialitetsterskel for NaN-eksklusjon

- **Status:** Vedtatt
- **Dato:** 2026-06-29
- **Presiserer:** [ADR-0001](0001-ci-beregningsmetode.md), Beslutning 2.

## Kontekst

ADR-0001 Beslutning 2 ekskluderer et helt intervall hvis *en* inkludert
(faktor-bærende) produksjonstype har NaN. Første 2025-kjøring avdekket at dette
gir et **dekningsartefakt**: for NO2 og NO3 falt dekningen til ~31 % og ~27 %,
drevet utelukkende av bi-typer med **neglisjerbar produksjon** som er urapportert
(NaN) mesteparten av året:

- NO2 **Wind Offshore**: NaN 55,9 % av året, men årssnitt **2,5 MW** (~0,04 % av miksen).
- NO3 **Solar**: NaN 66,6 %, men årssnitt **0,0 MW**.

En urapportert type som uansett bidrar ~0 MW er ikke et reelt datatap. Å la den
kaste 2/3 av ellers gyldige intervaller lar en kjent artefakt stå i kjernetallet.

## Beslutning

Skill mellom **materielle** og **neglisjerbare** produksjonstyper, med en terskel
**pre-registrert her — satt på prinsipielt grunnlag, ikke justert mot dekning**:

> En produksjonstype regnes som **neglisjerbar** i en sone dersom dens
> årssnitt-bidrag er **< 0,5 % av sonens totale miks** ELLER **< 5 MW absolutt**.
> Ellers er den **materiell**.

Regler:
1. **NaN i en neglisjerbar type → behandles som 0** (ikke datatap).
2. Et intervall **ekskluderes kun ved NaN i en materiell type**.
3. Dekningsgrad rapporteres fortsatt per sone. Hvilke typer som ble klassifisert
   neglisjerbare rapporteres som provenans.

## Begrunnelse for terskelen

Terskelen er valgt slik at en type under den **ikke kan flytte sone-CI målbart**:
en type på < 5 MW eller < 0,5 % av miksen endrer det energi-vektede snittet med en
brøkdel av en gCO2eq/kWh uansett hvilken faktor den har. Grensen er prinsipiell
(neglisjerbar = umålbar effekt), ikke empirisk valgt for å maksimere dekning.
Dobbel betingelse (relativ ELLER absolutt) fanger både små soner og små typer.

## Konsekvenser

- NO2/NO3-dekningen løftes til et representativt nivå uten å røre de andre sonene
  (NO1/NO4/NO5 har allerede ≥ 93,6 % dekning og ingen materielle NaN-typer).
- Kjernetallet hviler ikke lenger på et ~30 %-utvalg for NO2/NO3.
- Terskelen er en fast del av metoden; endres den, kreves ny ADR.

## Alternativer vurdert (forkastet)

- **Behold ADR-0001 strengt** — lar et kjent artefakt stå i kjernetallet.
- **Terskel valgt etter å ha sett dekningen** — ville gjort "neglisjerbar" til en
  frihetsgrad å fiske i; forkastet. Terskelen er pre-registrert.
- **Dropp NaN-eksklusjon helt (NaN=0)** — forkastet i ADR-0001 (kunstig for
  materielle typer).
