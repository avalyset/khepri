# ADR-0005: Adopsjon — codecarbon-integrasjon av NO per-sone CI

Status: Vedtatt
Dato: 2026-06-29
Bygger på: ADR-0001, ADR-0002, ADR-0003, ADR-0004

## Kontekst
Khepris mål er å fylle hullet i norsk karbon-bevisst databehandling: codecarbon (verktøyet som måler AI/ML-utslipp) bruker en uniform placeholder (18.0 gCO2eq/kWh) for alle NO-soner i sin produksjons-fallback (nordic_emissions.json). Recon (verifisert mot kilde) bekreftet: strukturen er allerede per-sone, metoden er produksjons-/generasjonsmiks-basert (matcher ADR-0001), eksterne faktor-PR-er merges (presedens #1039/#1224), testene leser dynamisk fra JSON (oppdatering bryter dem ikke), og åpningen er uclaimet. Adopsjonen er en PR som erstatter NO1-NO5-verdiene med Khepris avledede, drift-karakteriserte tall.

## Pre-registrerte beslutninger (låst før PR skrives)

### 1. Faktor-basis: IPCC AR5, arvet fra ADR-0001
PR-en bruker Khepris IPCC AR5 livssyklus-medianer (ADR-0001), IKKE codecarbons egne per-kilde-faktorer. Begrunnelse: (a) intern konsistens — samme tall i codecarbon som i Khepris DOI-artefakt, ellers to ulike NO4-tall i omløp og brutt reproduserbarhet; (b) IPCC AR5 er sitert/fagfellevurdert standard (CarbonCast/EnsembleCI-konvensjon), mens codecarbons egen tabell er metodisk blandet (direkte fossil + WNA-livssyklus). PR-en forklarer avviket fra codecarbons carbon_intensity_per_source.json eksplisitt og forsvarer IPCC AR5 som konsistent basis.

### 2. Hvilke verdier, hvilken periode
Per-sone årssnitt-CI, produksjonsbasert, fra det mest komplette tilgjengelige året (2025) med ADR-0001+0002-metoden. Verdier: NO1, NO2, NO3, NO4, NO5 som beregnet (ikke gjengitt her fra minne — PR henter dem fra Khepris committede output, B1).

### 3. Drift-karakteristikk MÅ følge med (ærlighet over ren erstatning)
PR-en dumper ikke bare fem tall. Metadata/notes per sone bærer drift-funnet (ADR-0003) og forecast-funnet (ADR-0004):
- NO1/NO2/NO3: stabile år-til-år (<5%), årlig oppdatering tilstrekkelig.
- NO4: hendelses-drevet variabilitet (Hammerfest LNG driftsstans 2020-2022, dokumentert) — verdien er periodeavhengig, ikke en stabil konstant. Flagges eksplisitt.
- NO5: produksjonsbasert CI nær matematisk låst til hydro-faktor i rene vannkraft-perioder.
- Ærlig grense oppgis: produksjonsbasert NO-CI er lav og lite distinkt mellom soner unntatt der fossil gass forekommer (NO4).

### 4. Metodisk transparens i PR
PR-en oppgir eksplisitt: (a) at dette erstatter produksjons-fallbacken, ikke Electricity Maps consumption-based primær-stien; (b) kilde (ENTSO-E + IPCC AR5, lenke til Khepri DOI når frosset); (c) at metoden er produksjonsbasert generasjonsmiks (matcher codecarbons egen fallback-metodikk); (d) reproduserbarhet (Khepri-repo, ADR-kjede).

### 5. Direkte PR (presedens-forankret)
codecarbon-recon viste presedens for eksterne direkte faktor-PR-er (#1039, #1224 begge merget). PR sendes direkte, ikke issue-først. MEN rett før innsending: forbigåelse-sjekk (gh pr list + issue list --search "Norway"/"NO1"/"nordic"/"emission factor" — har noen åpnet noe siden recon?) og verifiser at PR-en ikke kolliderer med pågående arbeid. PR-body forklarer forbedringen fyldig (som et issue ville), siden det ikke er et forutgående issue å lene seg på.

## Konsekvenser
- Hullet fylles ved kilden: norske codecarbon-brukere får per-sone-tall istedenfor uniform 18.0 (som er for lav for alle, 2.5x for lav for NO4).
- Khepri blir sitert kilde i et bredt brukt verktøy — adopsjon, ikke bare publisering.
- Drift-karakteristikken gjør PR-en ansvarlig: brukere vet hvilke soner som er stabile og hvilke som krever oppdatering.
- Avvik fra codecarbons egen faktortabell må forsvares i review — akseptert kostnad for konsistens med Khepris DOI-artefakt.

## Alternativer vurdert
- Faktor-basis B (rekompute med codecarbons egne faktorer): forkastet — ville gitt to ulike NO-tall (codecarbon vs Khepri DOI), brutt reproduserbarhet, og bundet oss til codecarbons metodisk blandede tabell.
- Ren tall-erstatning uten drift-metadata: forkastet — uærlig mot det drift/forecast-lagene påviste; en statisk NO4-verdi ville villede.
- Vente til DOI-frys før PR: vurdert — PR kan åpnes med lenke til Khepri-repo nå, DOI legges til når frosset. Ikke en blokker, men PR bør referere det kommende DOI-ankeret.

## Avhengighet
Adopsjon (denne) bygger på datakjerne+drift+forecast (alle ✅). Frys (Fase 5) er separat: DOI-frys av Khepri-artefaktet styrker PR-en (sitérbart anker) men blokkerer den ikke.
