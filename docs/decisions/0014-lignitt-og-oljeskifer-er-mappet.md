# ADR-0014 — Lignitt og oljeskifer er mappet, ikke ubefaktorerte

Status: accepted
Dato: 2026-09-10
Forholder seg til: ADR-0013 (kjent fossil type uten faktor) og ADR-0009
(bæring i nevneren for codecarbon-leveransen).
Supersederer ingenting. Korrigerer medlemslisten i ADR-0013s
`UNFACTORED_FOSSIL`, ikke mekanismen.

## Kontekst

ADR-0013 innførte `UNFACTORED_FOSSIL` med fire typer, definert i koden som
«ENTSO-E fossil production types that codecarbon has NO key for»:

    Fossil Peat
    Fossil Brown coal/Lignite
    Fossil Coal-derived gas
    Fossil Oil shale

Definisjonen ble aldri etterprøvd mot CodeCarbons faktiske datakjede. Den ble
utledet av at `carbon_intensity_per_source.json` ikke har en nøkkel som *heter*
`lignite` eller `oil_shale`. Det er riktig om nøkkelnavnene og feil om dataene.

Foranledningen var kartleggingen i `~/khepri-data/udekket-europa/`: 43 budsoner
for 2025, der lignitt var den største udekkede typen i tretten soner og alene
sto for 64,65 % av miksen i RS, 61,24 % i BA og 51,54 % i MK.

## Belegget

### Lignitt er inne i CodeCarbons `coal`

`carbon_intensity_per_source.json` fylles ikke uavhengig av CodeCarbons
landstabell. Begge stammer fra samme kjede, dokumentert i
`codecarbon/data/private_infra/our_world_in_data.ipynb`: celle 2 henter
`owid-energy-data.csv`, celle 7 mapper `'coal_electricity':'coal_TWh'`.

OWID henter i sin tur fra Ember. Embers *Electricity Data Methodology*,
seksjonen «Emissions from Electricity Generation → Coal», sier:

> «Where data is available distinguishing between hard coal and lignite, we
> calculate emissions separately for these and sum them to give our published
> coal value.»

Og under «Fuel Types»:

> «In our global dataset, fuel data is mapped into nine generation types:
> Bioenergy, Coal, Gas, Hydro, Nuclear, Other Fossil, Other Renewables, Solar,
> and Wind. In our European dataset, Coal is further split into Hard Coal and
> Lignite […]»

Lignitt splittes altså ut bare i det *europeiske* datasettet. Kolonnen OWID
eksporterer, og som CodeCarbon leser, er den aggregerte.

### Oljeskifer er inne i CodeCarbons `petroleum`

Ember fører oljeskifer under «Other Fossil», som fotnote 5 definerer som
«generation from oil and petroleum products, as well as manufactured gases and
waste». OWIDs eksport har ingen `other_fossil`-kolonne; den splitter fossilt i
`coal` / `oil` / `gas`.

Motprøven ligger i CodeCarbons egen `global_energy_mix.json`. Estland brenner
nesten utelukkende oljeskifer, og oppføringen leser:

    "EST": { "coal_TWh": 0.0, "oil_TWh": 3.56, "gas_TWh": 0.05, … }

Hadde oljeskifer vært ført som kull, kunne `coal_TWh` ikke vært 0,0. Nøkkelen
som mates av `oil` i CodeCarbons faktortabell er `petroleum`.

### Kryssjekk

Serbia, Bosnia og Nord-Makedonia har praktisk talt ingen steinkullkraft.
`global_energy_mix.json` gir dem likevel `coal_TWh` 23,54 / 9,99 / 2,72 — tall
som bare gir mening om lignitt er talt med, og som ligger innenfor 1–4
prosentpoeng av lignittandelene målt i ENTSO-E A75 for 2025.

## Beslutning

**1. `Fossil Brown coal/Lignite` mappes til `coal` (995).**

**2. `Fossil Oil shale` mappes til `petroleum` (816).**

**3. Begge fjernes fra `UNFACTORED_FOSSIL`.** Listen står igjen med to typer:

    Fossil Peat
    Fossil Coal-derived gas

**4. Presisjonstapet skrives ned der mappingen står.** 995 er en blandet
kullverdi, og lignitt er skitnere enn steinkull, så en lignitt-tung sone
underestimeres av nøkkelen. Det er en kjent unøyaktighet i en mapping vi har
valgt, ikke et hull i tabellen — og det er en annen slags feil enn den ADR-0013
handler om.

## Hva dette ikke er

**Mekanismen i ADR-0013 står.** En kjent fossil type uten faktor skal fortsatt
ikke passere stille på null, guarden reiser seg fortsatt på at kolonnen finnes
og ikke på at det produseres i den, og `fossil_decisions` står fortsatt åpen for
den som vil ta stilling eksplisitt. Det som var galt var listen, ikke regelen.

**ADR-0013 endres ikke.** Teksten står som skrevet, inkludert seksjonen
«Systemgrense C» og den opprinnelige firetypelisten. Den er frosset: den
beskriver hva som ble besluttet 2026-09-09 og 2026-09-10 på det grunnlaget som
forelå da. Rettelsen hører hjemme her, ikke i en omskriving av en akseptert ADR.

**ADR-0009 endres ikke.** Bæring på null i nevneren gjelder uendret for de
typene som fortsatt ikke har nøkkel.

## Torv står fortsatt uten faktor

CodeCarbons tabell har en nøkkel til som ikke er brukt i denne mappingen:
`fossil: 635` (`carbon_intensity_per_source.json` linje 11, kildeoppgitt til
EPAs eGRID på linje 12). Den er lest av `codecarbon/core/emissions.py:353-354`,
som stripper `_TWh` av feltnavnet og slår opp resultatet, og den mates av
`fossil_electricity` → `fossil_TWh` (samme notebook, celle 7) — som OWIDs
kodebok definerer som «Electricity generation from coal, oil, and gas».

`fossil` er altså intensiteten til det aggregerte kull-, olje- og gassmikset,
ikke en per-teknologi-nøkkel for uklassifisert fossil produksjon; og med 635
ligger den under `coal` (995), mens IPCC 2006 setter torv over bituminøst kull
per TJ. Å mappe torv dit ville derfor underestimere den, ikke løse spørsmålet.

Torv er dessuten ikke nevnt i Embers metodedokument i det hele tatt — hverken
under Coal eller under Other Fossil. Der lignitt og oljeskifer kunne avgjøres av
kilden, kan torv det ikke. **Systemgrense C står uendret.**

## Konsekvenser

- **Ingen publisert verdi flytter seg.** Ingen av NO1–NO5 eller SE1–SE4
  inneholder lignitt eller oljeskifer i noe år av det publiserte uttrekket.
  Ni-sone-baselinen er bit-identisk, SHA256 `a86d8dd2…` uendret.
- **`~/khepri-data/udekket-europa/TABELL.md` regnes om.** Med den nye mappingen
  faller antall soner over 1 % udekket fra 36 av 43 til 29 av 43, og
  guard-utslagene fra 21 til 11. Den gamle beregningen beholdes som vedlegg.
- **Kartleggingens karakter endres.** Den ble skrevet som en observasjon om hva
  CodeCarbons tabell mangler. For lignitt og oljeskifer var det i stedet en
  observasjon om hva vår egen mapping manglet. Det er en intern dekningsnote,
  ikke et funn om verktøyet.
- **`Fossil Coal-derived gas` er den gjenværende åpne saken** på fossilsiden.
  Embers fotnote 5 legger «manufactured gases» under «Other Fossil». Ember
  navngir ikke ENTSO-E-typen selv, så koblingen går via standard
  energistatistikk-terminologi: Eurostat definerer *manufactured gases* som
  gassverksgass, koksgass, masovngass og andre gjenvunne gasser, og bruker
  *derived gases* om det samme. `Fossil Coal-derived gas` faller innenfor den
  definisjonen. Konklusjonen er uansett den samme som om koblingen ikke holdt:
  CodeCarbons tabell har ingen per-teknologi-nøkkel å mappe til. Guarden holder
  typen, og ingen faktor foreslås her.
