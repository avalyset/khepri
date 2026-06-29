# ADR-0006: SE per-sone CI — utvidelse av Khepri-metoden til svenske budområder

Status: Vedtatt
Dato: 2026-06-29
Bygger på: ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005

## Kontekst
Khepri-metoden (NO1-NO5) utvides til de svenske budområdene SE1-SE4. codecarbon har samme placeholder-defekt for SE som NO hadde: SE1-SE4 alle 18,0 gCO2eq/kWh uniform (verifisert mot nordic_emissions.json). CarbonCast/EnsembleCI dekker SE kun som land-aggregat (verifisert mot deres data/-kataloger — én SE/, ingen SE1-4), så per-sone SE er genuint nytt. Forbigåelse ren: ingen åpen SE per-sone CI-issue/PR i CarbonCast, EnsembleCI eller codecarbon.

## Beslutning: arv uendret metode, noter det SE-spesifikke

### 1. Metode arvet uendret fra ADR-0001 + ADR-0002
SE1-SE4 CI beregnes med NØYAKTIG samme ci.py-pipeline som NO: produksjonsbasert generasjonsmiks × IPCC AR5 lifecycle-faktorer, varighet-vektet aggregering, NaN-eksklusjon, materialitetsterskel (0,5% miks / 5 MW). Ingen metodeendring. Drift (ADR-0003) og forecast (ADR-0004) arves likeså.

### 2. EIC-koder (verifisert mot entsoe-py, ikke antatt)
SE1 10Y1001A1001A44P · SE2 10Y1001A1001A45N · SE3 10Y1001A1001A46L · SE4 10Y1001A1001A47J.
NB: 10YSE-1 er land-AGGREGATET, ikke per-sone — bekreftet og forkastet. Per-sone-koderne over er autoritative.

### 3. Kjernekraft (nytt mot NO, AR5-verifisert)
SE har produksjonstypen Nuclear (B14), fraværende i NO. Faktor = 12 gCO2eq/kWh (IPCC AR5 Annex III median, samme sekundærkilde som ADR-0001 — kryssjekket konsistent). Kjernekraft ble observert KUN i SE3 (døgn 2026-06-27), ikke SE1/SE2/SE4. SE3-eksklusivitet forventes strukturelt og bekreftes empirisk i datakjerne-kjøringen over fullt vindu (2021-2025) — det er der per-sone-variasjonens størrelse faktisk kvantifiseres, ikke i denne ADR-en. (Den observerte verdien var produksjon 2026-06-27, ikke installert kapasitet.) Kjernekraft i SE3 forventes å være hovedkilden til per-sone-variasjon — i kontrast til NO der variasjonen var gass-drevet (NO4) og ellers lav.

### 4. psrType-forbehold (B3, eksplisitt)
Det verifiserte psrType-settet er fra ett døgn (2026-06-27). Sjeldne typer (Waste, Biomass) som ikke produserte det døgnet kan forekomme i full årsdata. Disse dekkes automatisk av eksisterende factors.py-mekanisme (AR5-faktor eller EXCLUDED/SENSITIVITY_PROXY for under-materielle typer). SE har IKKE bare de seks typene observert ett døgn — full datakjerne-kjøring avdekker det faktiske settet, og metoden håndterer nye typer uten endring.

### 5. Bidrag — ærlig posisjonering (B3)
- Datakjerne + drift per-sone SE1-SE4: genuint nytt (ingen har per-sone, kun aggregat).
- Forecast: claimes som "første per-budområde SE1-SE4 CI-forecast", ALDRI som "første SE CI-forecast" (CarbonCast har SE-aggregat). Per-sone er det som gjør det nytt.
- codecarbon-fylling: reelt uavhengig av forecasting (placeholder er like gal for SE).

## Konsekvenser
- SE-artefaktet kan bli sterkere enn NO på forecast-leddet: SE3-kjernekraft gir reell per-sone-variasjon å forutsi, der NO var lavt/lite distinkt.
- Samme reproduserbarhet, ADR-kjede, DOI-disiplin som NO.
- Egen codecarbon-PR (parallell til #1260) for SE1-SE4.

## Alternativer vurdert
- Anta 10YSE-1: forkastet — det er aggregatet, ville kollapset per-sone-claimet (gaten fanget dette).
- Ny faktor for kjernekraft: forkastet — AR5-verdien (12) er allerede i factors.py og konsistent; ingen grunn til avvik.
- Bare codecarbon-fylling uten drift/forecast: forkastet — per-sone drift + forecast er det genuint nye bidraget feltet mangler.
