# ADR-0007: SE per-sone drift — arv av ADR-0003-metode

Status: Vedtatt
Dato: 2026-06-29
Bygger på: ADR-0003 (drift), ADR-0006 (SE per-sone CI)

## Kontekst
SE per-sone CI (SE1-SE4, ADR-0006) er beregnet for 2022-2025. Drift-laget karakteriserer år-til-år-stabilitet per sone med samme metode som NO (ADR-0003). 2021 er ekskludert (dekning 4,7 %, ~2 uker data); effektivt vindu 2022-2025.

## Beslutning: arv ADR-0003-drift-metode uendret, pre-registrert terskel

### 1. Metode og terskel arvet fra ADR-0003 (pre-registrert proveniens)
Drift-metoden (drift.py) brukes uendret. Materialitetsterskel er arvet fra ADR-0003, satt for NO FØR noen SE-data eksisterte: >15 % år-til-år CI-endring ELLER >5pp miks-andel-skift for materiell type = materiell drift. Terskelen er IKKE valgt for å passe SE-tall — dens proveniens er ADR-0003 (NO), forut for all SE-data. Den anvendes på SE uten justering. Grensetilfeller (verdier rett over terskel) rapporteres som materiell drift mot den forhåndssatte terskelen, ikke bortjustert fordi de er nære.

### 2. Test-vindu
2022 vs 2025 per sone mot terskel; år-til-år-endringer rapporteres for hele 2022-2025. 2021 ekskludert (dekning).

### 3. SE-spesifikt forbehold (B3)
2021 ekskludert (4,7 % dekning). SE har ikke NOs energikrise-spesifikke 2021-2022-regimeskift målbart i dette vinduet, siden 2021 mangler. Drift-karakteriseringen gjelder 2022-2025.

## Konsekvenser
- Per-sone oppdateringsfrekvens for codecarbon-bidraget informeres av drift: stabile soner trenger sjeldnere oppdatering enn driftende.
- Samme ADR-kjede, reproduserbarhet og DOI-disiplin som NO.
