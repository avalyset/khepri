# ADR-0014 — Alle fire ubefaktorerte fossiltyper er mappet

Status: accepted
Dato: 2026-09-11
Forholder seg til: ADR-0013 (kjent fossil type uten faktor) og ADR-0009
(bæring i nevneren for codecarbon-leveransen).
**Supersederer:** seksjonen «Systemgrense C» i ADR-0013, slik den ble utvidet
2026-09-10 på `docs/adr-0013-kolonne-vs-produksjon` (`df236f0`). Se egen seksjon.

## Kontekst

ADR-0013 innførte `UNFACTORED_FOSSIL` med fire typer, definert i koden som
«ENTSO-E fossil production types that codecarbon has NO key for»:

    Fossil Peat
    Fossil Brown coal/Lignite
    Fossil Coal-derived gas
    Fossil Oil shale

Definisjonen ble utledet av nøkkelnavnene i `carbon_intensity_per_source.json`:
der står ingen `lignite`, ingen `peat`, ingen `oil_shale`. Det er riktig om
navnene og feil om dataene. Faktortabellen og landstabellen bygges fra samme
kjede, dokumentert i `codecarbon/data/private_infra/our_world_in_data.ipynb`:
celle 2 henter `owid-energy-data.csv`, celle 7 mapper kolonnene, celle 16 skriver
`global_energy_mix.json`. OWID henter fra Ember. **Spørsmålet om hvor en
ENTSO-E-type hører hjemme avgjøres derfor i Ember-leddet, ikke av nøkkelnavnene.**

Ember mapper alt brensel inn i ni typer: Bioenergy, Coal, Gas, Hydro, Nuclear,
Other Fossil, Other Renewables, Solar, Wind. Alle fire typene får plass der.

## Belegget

### Lignitt er inne i `coal`

Embers *Electricity Data Methodology*, «Emissions from Electricity Generation →
Coal»:

> «Where data is available distinguishing between hard coal and lignite, we
> calculate emissions separately for these and sum them to give our published
> coal value.»

og under «Fuel Types», at lignitt bare splittes ut i det *europeiske* datasettet
— ikke i det globale som OWID eksporterer gjennom `coal_electricity`.

**Kryssjekk.** Serbia, Bosnia og Nord-Makedonia har praktisk talt ingen
steinkullkraft; kullflåten er lignitt. `global_energy_mix.json` gir dem likevel
`coal_TWh` 23,54 / 9,99 / 2,72 — tall som ikke kan være steinkull alene. Og
andelene stemmer: Bankwatch oppgir kullavhengigheten i kraftproduksjonen til
67 / 65 / 51 %, mot lignittandeler målt i ENTSO-E A75 for 2025 på
**64,65 / 61,24 / 51,54 %** — avvik på henholdsvis +2,35, +3,76 og −0,54
prosentpoeng. De to kildene måler ulike år og ulike avgrensninger, så
sammenfallet er en retningskontroll, ikke en identitet.

### Oljeskifer, torv og koksgass er inne i `petroleum`

Embers fotnote 5 definerer Other Fossil som

> «generation from oil and petroleum products, as well as manufactured gases and
> waste».

OWIDs eksport har ingen `other_fossil`-kolonne; den splitter fossilt i
`coal` / `oil` / `gas`, og Other Fossil havner i `oil_electricity` → `oil_TWh`.
CodeCarbon-nøkkelen som mates av `oil` er `petroleum`.

**Oljeskifer — EST-testen.** Estland brenner nesten utelukkende oljeskifer, og
oppføringen leser `"coal_TWh": 0.0` mot `"oil_TWh": 3.56`. Hadde oljeskifer vært
ført som kull, kunne `coal_TWh` ikke vært null.

**Torv — FIN-testen.** Samme form, målt mot Statistics Finland, StatFin-tabell
**12vp**, «Supply of electricity by energy source», hentet 2026-09-11 fra
`https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12vp.px`. CodeCarbons
FIN-oppføring er for år 2023, så sammenligningen er 2023 mot 2023:

| | codecarbon `global_energy_mix.json` | StatFin 12vp | diff |
|---|---:|---:|---:|
| `coal_TWh` ↔ 1.5 Hard Coal | 1,58 | 1,48 | +0,10 |
| `oil_TWh` ↔ 1.6 Oil | **2,35** | **0,20** | **+2,15** |
| `gas_TWh` ↔ 1.7 Natural gas | 0,53 | 0,63 | −0,10 |
| `hydroelectricity_TWh` ↔ 1.1 Hydro | 15,11 | 15,03 | +0,08 |
| `nuclear_TWh` ↔ 1.4 Nuclear | 33,92 | 32,76 | +1,16 |
| `wind_TWh` ↔ 1.2 Wind | 14,63 | 14,46 | +0,17 |
| `solar_TWh` ↔ 1.3 Solar | 0,65 | 0,72 | −0,07 |
| `biofuel_TWh` ↔ 1.9 Wood fuels | 11,07 | 10,20 | +0,87 |
| `total_TWh` ↔ 1 ELECTRICITY PRODUCTION | 79,84 | 78,28 | +1,56 |

StatFin-poster uten egen kolonne hos codecarbon: **1.8 Peat 1,07**,
1.10 Other renewables 0,52, **1.11 Other fossil fuels 1,01**,
1.12 Other energy sources 0,21.

Hva forklarer `oil_TWh` = 2,35?

| Kombinasjon | TWh | diff |
|---|---:|---:|
| 1.6 Oil alene | 0,20 | +2,15 |
| 1.6 + 1.8 (olje + torv) | 1,27 | +1,08 |
| 1.6 + 1.11 (olje + other fossil, **uten torv**) | 1,21 | **+1,14** |
| **1.6 + 1.8 + 1.11** | **2,28** | **+0,07** |
| 1.6 + 1.8 + 1.11 + 1.12 | 2,49 | −0,14 |

Uten torv står 1,14 TWh uforklart. Med torv og other fossil er residualet 0,07.

**Hva testen ikke fastslår.** De øvrige radene avviker med opptil +1,16
(kjernekraft) og +0,87 (biomasse), så vintage og avgrensning skiller de to
kildene uavhengig av torvspørsmålet, og residualet på 0,07 må leses mot den
bakgrunnsstøyen. StatFins 1.11 «Other fossil fuels» er dessuten en samlekategori
som ikke er brutt ned her. Testen er konsistent med at torv ligger i `oil_TWh`
og utelukker ikke andre sammensetninger som summerer likt. Belegget for
plasseringen er primært Embers taksonomi; FIN-testen er korroborasjon.

**Koksgass.** Ember navngir ikke ENTSO-E-typen. Koblingen går via standard
energistatistikk-terminologi: Eurostat definerer *manufactured gases* som
gassverksgass, koksgass, masovngass og andre gjenvunne gasser, og bruker
*derived gases* om det samme. `Fossil Coal-derived gas` faller innenfor.

## Beslutning

Alle fire typene mappes. `UNFACTORED_FOSSIL` blir tom.

| ENTSO-E-type | codecarbon-nøkkel | gCO2eq/kWh | Via |
|---|---|---:|---|
| `Fossil Brown coal/Lignite` | `coal` | **995** | Ember Coal → OWID `coal_electricity` |
| `Fossil Oil shale` | `petroleum` | **816** | Ember Other Fossil → OWID `oil_electricity` |
| `Fossil Peat` | `petroleum` | **816** | Ember Other Fossil → OWID `oil_electricity` |
| `Fossil Coal-derived gas` | `petroleum` | **816** | Ember Other Fossil → OWID `oil_electricity` |

**Guarden og `fossil_decisions` består som mekanisme.** Regelen ADR-0013 slår
fast — at en kjent fossil kolonne ikke skal bæres stille på null — holdt. Det som
falt var listen over typer den navnga. `UNFACTORED_FOSSIL` er tom og guarden
derfor inert som standard, men parameteren `unfactored=` lar en kaller navngi
typer selv, og `fossil_decisions` står uendret for den som vil overstyre en
mapping med en egen verdi og kilde. En framtidig ENTSO-E-type uten nøkkel hører
hjemme i settet.

### Alle fire er gulv, ikke anslag

Retningen på feilen er kjent og ensidig for alle fire. IPCC 2006 Vol. 2 Ch. 2
Tab. 2.2, direkte CO2 ved forbrenning:

| Brensel | kg CO2/TJ | Mot mappet nøkkel |
|---|---:|---|
| Kull (spennet i tabellen) | 94 600 – 101 000 | `coal` 995 er en **blandet** kullverdi; lignitt ligger i øvre ende |
| Torv | **106 000** | over hvert kullsjikt — `petroleum` 816 er under `coal` 995 |
| Oljeskifer og koks | **107 000** | høyest i tabellen — samme nøkkel, 816 |
| Ved (til sammenligning) | 112 000 | ikke mappet her |

`Fossil Coal-derived gas` er avledet av kull, og faller inn under kullspennet på
brenselsiden. Alle fire nøklene ligger dermed **under** brenselets egen
utslippsfaktor per TJ, og lignitt-, torv-, oljeskifer- og koksgass-tunge soner er
**underestimert**. Det er en kjent unøyaktighet i en mapping vi har valgt, ikke
et hull i tabellen — og en annen slags feil enn den ADR-0013 handler om.

Caveaten gjelder **plasseringen av tallet, ikke av typen**. Kategoriseringen
følger av kilden. Hvor grov faktoren er innenfor kategorien er et eget spørsmål,
og det er ikke løst her.

### Torv i særdeleshet: hvorfor 816 er et gulv og ikke et valg

FI 2025 på codecarbon-basis, kjørt 2026-09-11 mot
`~/khepri-data/v2-dk-fi/FI_generation_2025.csv`:

| Torvfaktor | FI-CI 2025 | Merknad |
|---|---:|---|
| 0 (pre-ADR-0014, båret på null) | **36,2063** | den stille nullen ADR-0013 avviste |
| **816** (`petroleum`, denne beslutningen) | **47,8250** | +32,1 % mot nullen |
| 820 (IPCC AR5 «Coal – PC», khepris egen base) | 47,8820 | ikke brukt her: annen faktorbase, jf. ADR-0009 |
| 995 (`coal`) | 50,3738 | +39,1 % mot nullen |
| 1071 (ecoinvent via Clauß et al. 2019) | 51,4559 | +42,1 % mot nullen |

Spennet mellom 816 og 1071 er 7,6 % på FI-CI. Det er lite mot den egentlige
usikkerheten: **metodevalget for kraftvarme alene gir 459–1 922 gCO2eq/kWh_e**
for torv på samme finske statistikk (Tilastokeskus 13j5, 2000–2024), en faktor
4,2, uten at noen av verdiene er gale — de måler ulike ting. Fire familier er i
samtidig bruk: fixed-heat-efficiency (IEA, η_varme 0,90), 1/3:2/3 DUKES (DEFRA),
efficiency/hyödynjako (GHG Protocol og SYKE, matematisk identiske) og eksergi
(ecoinvent). Se `~/khepri-data/finland/TORV-VIRKNINGSGRAD.md` og
`~/khepri-data/prior-art/RAPPORT-CHP-ALLOKERING.md`.

**Derfor er 816 ikke et anslag på torvens utslippsintensitet.** Det er nøkkelen
kildens egen taksonomi fører torv til, og den er et gulv. Allokeringsspørsmålet
er ikke løst av denne beslutningen — det er avgrenset bort, fordi leveransen
regnes på CodeCarbons tabell og den tabellen ikke allokerer.

## Supersederer: «Systemgrense C» i ADR-0013

Seksjonen «Systemgrense C: torv gis ingen faktor», lagt til i ADR-0013 på
`df236f0` og datert **2026-09-10**, er superseded av denne ADR-en **2026-09-11**.

**Premisset som falt.** C hvilte på at kilden ikke kunne avgjøre torv. Ordrett
fra seksjonens grunnlag: torv nevnes ikke i Embers metodedokument — 0 treff på
`peat` mot 3 på kontrollstrengen `lignite`. Det stemmer fortsatt om ordet. Men
fraværet av ordet ble lest som fravær av en plassering, og det følger ikke:
Embers ni typer er uttømmende for brenselet, Other Fossil er samlekategorien for
fossilt som ikke er kull eller gass, og FIN-testen viser at torv faktisk følger
den ruten inn i `oil_TWh`. **Kilden hadde plassert torv; vi hadde ikke lest
plasseringen ut av den.**

**Hva som var riktig i C og består.** At torv ikke skal bæres stille på null. At
en verdi ikke skal velges på tynt grunnlag. At allokeringsspørsmålet er uløst og
metodefamilien må navngis når et spenn brukes. ADR-0014 endrer ikke noe av dette
— den erstatter «ingen faktor, kostnaden ved nullen rapporteres» med «kildens
egen nøkkel, oppgitt som gulv, med allokeringsspørsmålet eksplisitt avgrenset
bort».

**Hva som er strøket.** Setningen «Torv står fortsatt uten faktor» og
argumentet fra utelatelse den hvilte på — herunder resonnementet om at
`fossil: 635` ikke kunne brukes fordi torv sto utenfor tabellen. `fossil: 635`
er fortsatt ikke brukt, men nå av en annen grunn: det er intensiteten til det
aggregerte kull-, olje- og gassmikset, ikke nøkkelen Other Fossil ruter til.
Ruten går til `oil` → `petroleum`.

ADR-0013s øvrige tekst står uendret, inkludert mekanismen og seksjonen om at
guarden reagerer på kolonnen framfor på produksjonen. Taggen `v1.4` inneholder
ikke «Systemgrense C» — seksjonen har aldri vært på `main` — så ingenting
publisert bærer den superseder'te teksten.

## Konsekvenser

- **Ingen publisert verdi flytter seg.** Ingen av NO1–NO5 eller SE1–SE4
  inneholder noen av de fire typene i noe år av det publiserte uttrekket.
  Ni-sone-baselinen er bit-identisk, SHA256 `a86d8dd2…` uendret.
- **FI flytter seg.** FI 2025 på codecarbon-basis går fra 36,2063 til **47,8250**
  (+11,6187, +32,1 %), dekning 84,876 → 86,300 %. DK1 (89,6179) og DK2
  (117,9416) er uendret — ingen av de fire typene forekommer der.
- **`~/khepri-data/udekket-europa/TABELL.md` regnes om.** Soner over 1 % udekket
  faller fra 36 av 43 til **28 av 43**; guard-utslagene fra 21 til **0**.
- **Kartleggingens karakter endres.** Den ble skrevet som en observasjon om hva
  CodeCarbons tabell mangler. For alle fire typene var det i stedet en
  observasjon om hva vår egen mapping manglet. Det er en intern dekningsnote,
  ikke et funn om verktøyet.
- **Det som gjenstår som udekket er avfall, biomasse og samlekategoriene.**
  `Waste`, `Biomass`, `Other`, `Other renewable` og `Marine` bæres fortsatt på
  null etter ADR-0009. Ingen av dem er kjent fossil, så antakelsen ADR-0013
  navnga holder for dem.
