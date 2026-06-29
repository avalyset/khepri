# ADR-0003: Drift-måling i CI-signalet

Status: Vedtatt
Dato: 2026-06-29
Bygger på: ADR-0001, ADR-0002

## Kontekst
Khepris adopsjonslag (codecarbon-integrasjon) krever å vite om et CI-tall beregnet på ett år er gyldig for neste, eller om den norske kraftmiksen driver nok til at signalet forfaller og må retrenes. Dette måles på det produksjonsbaserte CI-signalet (ADR-0001+0002-metoden) over 2021–H1.2026 per NO-sone. Pre-registreringen låses før drift-resultatet ses.

## Pre-registrerte beslutninger (låst før resultat)

### 1. Drift-metrikk
- Primær: årlig CI per sone, beregnet med NØYAKTIG ADR-0001+0002-pipeline per år (samme faktorer, NaN-eksklusjon, varighet-vekting, materialitetsterskel). År-til-år endring i prosent.
- Sekundær: miks-andel per psrType per år, år-til-år drift i prosentpoeng.

### 2. Terskel for materiell drift (pre-registrert)
- År-til-år CI-endring > 15 % ELLER miks-andel-skift > 5 prosentpoeng for en materiell type (materiell per ADR-0002: ≥0,5 % miks eller ≥5 MW) regnes som materiell drift.
- Begrunnelse: under denne terskelen er et fjorårs-CI-tall brukbart som proxy for inneværende år (adopsjons-relevant: oppdateringsfrekvens kan være årlig). Over terskelen er det ikke, og hyppigere retrening kreves.

### 3. Regime-test (energikrise 2021-2022)
- Test om 2021-2022 er statistisk distinkt fra 2023-2026 per sone: sammenlign årssnitt-CI og miks-andeler. Flagg om krise-årene avviker > terskel (beslutning 2) fra det senere regimet.
- Pre-spesifisert: dette er en deskriptiv regime-sammenligning, ikke en hypotesetest med p-verdi — vi rapporterer størrelsen på forskjellen mot terskel, ikke signifikans.

### 4. Null-hypotese (eksplisitt)
- H0: norsk per-sone CI er stabilt år-til-år (vannkraft-dominert → lav drift, fjorårs-tall er god proxy).
- Vi tester om H0 holder. Vi forventer IKKE et bestemt utfall. Et stabilt signal og et driftende signal er begge ekte, publiserbare funn med ulik konsekvens for adopsjonslagets oppdateringsfrekvens.

## Konsekvenser
- Stabilt signal (drift < terskel): fjorårs-CI er god proxy; codecarbon-integrasjonen kan oppdateres årlig.
- Driftende signal (drift > terskel): signalet forfaller; hyppigere retrening kreves, og dette må dokumenteres i adopsjons-leveransen.
- NO4-gass-andel måles per år som del av miks-drift (driver vi vet er der; vi måler utviklingen, jakter den ikke).

## Alternativer vurdert
- Lavere terskel (5 %): forkastet, fanger sesong-/værstøy som ikke er reell strukturell drift.
- Hypotesetest med p-verdi på regime: forkastet, vi har hele populasjonen (alle intervaller), ikke et utvalg — effektstørrelse mot terskel er riktigere enn signifikans.
