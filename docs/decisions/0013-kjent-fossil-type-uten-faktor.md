# ADR-0013 — Kjent fossil produksjonstype skal ikke bæres på null

Status: akseptert
Dato: 2026-09-09
Forholder seg til: ADR-0009 (bæring i nevneren for codecarbon-leveransen).
Supersederer ingenting. Navngir en antakelse ADR-0009 hviler på uten å si den,
og fastsetter hva som skjer når den ikke holder.

## Kontekst

ADR-0009 lar ubefaktorerte produksjonstyper bli stående i nevneren med faktor 0,
slik at den leverte verdien er en fullstendig faktor over all produksjon i sonen.
Regelen er riktig for den leveransen og står.

Regelen hviler på en antakelse som ikke står noe sted i ADR-0009: **at en
ubefaktorert type enten er lav-karbon eller genuint uklassifisert.**

For de typene som faktisk forekommer i NO1–NO5 og SE1–SE4 holder antakelsen.
`Biomass` og `Marine` er lav-karbon. `Other`, `Other renewable` og `Waste` er
uklassifiserte samlekategorier. Å bære dem på null er en innrømmelse av
uvitenhet: den fortynner CI-en litt, og fortynningen rapporteres gjennom
dekningsfeltet. Leseren kan selv vurdere hvor mye vekt tallet tåler.

Antakelsen holder ikke for **torv**. `Fossil Peat` er utvetydig fossil, og
CodeCarbons faktortabell har ingen nøkkel for den. Bæres den på null, uttrykker
nullen ikke uvitenhet — den påstår, stilltiende og feil, at produksjonen var ren.
Forskjellen er ikke gradsforskjell. De andre nullene sier «vet ikke»; denne sier
«null utslipp» om noe vi vet forbrenner.

Torv forekommer ikke i noen norsk eller svensk sone. Den forekommer i Finland,
i alle fem årene 2021–2025, og Finland er allerede et felt i den leverte
`nordic_emissions.json`.

**Tallgrunnlag:** en femårskjøring 2021–2025 med `khepri.ci.compute` på CodeCarbons
faktortabell, mot ENTSO-E A75 for FI, kjørt 2026-09-09. ENTSO-E-uttrekkene
redistribueres ikke — plattformens vilkår tillater det ikke — men hentes
reproduserbart gjennom de dokumenterte API-spørringene. Kort: den stille nullen
underdriver FI med rundt 40–50 % i hvert av de fem årene, og torvandelen faller
gjennom perioden, så feilen krymper uten å forsvinne.

### Et beslektet, mindre tilfelle: `Energy storage`

ENTSO-E begynte å føre `Energy storage` for FI i 2025. Det er ikke produksjon i
det hele tatt — det er uttak av energi som ble produsert tidligere, av noe annet.
Bæres den i nevneren, telles den energien to ganger: én gang der den ble
produsert, én gang der den ble sluppet ut igjen. Andelen er i dag forsvinnende
(1e-4 %), så dette handler ikke om tallet nå, men om at kategorien er strukturelt
feil plassert og vil vokse.

## Beslutning

**1. Ubefaktorert fossil type stopper beregningen.**
`UNFACTORED_FOSSIL` navngir de ENTSO-E-typene som er utvetydig fossile og som
CodeCarbons tabell mangler nøkkel for: `Fossil Peat`, `Fossil Brown coal/Lignite`,
`Fossil Coal-derived gas`, `Fossil Oil shale`. Når `codecarbon_factors()` får vite
hvilke typer som forekommer, og en av disse er blant dem uten at kalleren har
oppgitt en eksplisitt faktor, reises `UnfactoredFossilError`.

**2. `Energy storage` fjernes før nevneren velges.**
`NOT_GENERATION` trekkes fra `occurring` i `ci.compute()` før nevneren settes, så
typen ikke kan nå den på noen basis. Det er strengere enn å bære den på null,
og med vilje: en null-båret kolonne fortynner stille, og for en ikke-produksjons-
kolonne har fortynningen ingen fysisk betydning.

### Hvorfor feile framfor å gjette

Tre veier ble vurdert.

- **Bære videre på null.** Forkastet. Det er dagens oppførsel, og den produserer
  et tall som ser gyldig ut og er 40–50 % for lavt. Verst mulige feilmodus:
  stille og troverdig.
- **Sette inn en standardfaktor for torv.** Forkastet. Enhver verdi vi velger må
  hentes fra en kilde utenfor CodeCarbons tabell — Ecoinvent gir 1071 — og da er
  det ikke lenger «CodeCarbons egen faktorbase», som er hele begrunnelsen for at
  leveransen regnes på den tabellen (ADR-0009). Å blande inn én fremmed verdi
  bryter konsistensen i det skjulte.
- **Feile høyt, og kreve at kalleren tar stilling.** Valgt. Faktoren *kan*
  oppgis — `fossil_decisions={"Fossil Peat": 1071.0}` — men den må oppgis
  eksplisitt, av et menneske, med kilden skrevet ned. Beslutningen flyttes fra en
  default ingen ser, til et sted den er synlig i koden som kaller.

Ingen publisert verdi flytter seg. Verifisert bit-identisk mot v1.3-grunnlinjen for
alle ni soner, samme SHA256 over fullpresisjonsverdiene før og etter. Verdiene er
pinnet i `tests/test_peat_guard.py`, som feiler på en ulp avdrift.

## Konsekvens: dekningsfeltet er ikke nok

Dekningsfeltet i `nordic_emissions.json` oppgir hvor stor andel av produksjonen
som bærer en faktor. **Det skiller ikke mellom uklassifisert og kjent fossil
udekket andel.** SE4 og FI er nesten identiske på dette feltet — begge rundt 85 %
— men de to tallene betyr helt ulike ting:

- SE4s udekkede andel er `Other`, en samlekategori vi ikke vet innholdet av.
  Retningen på feilen er ukjent.
- FIs udekkede andel inneholder torv, som vi vet er fossil. Retningen på feilen
  er kjent, og den er nedover.

En leser som sammenligner de to dekningstallene vil tro situasjonene er
likeverdige. Det er de ikke. Feltet er derfor en nødvendig, men ikke tilstrekkelig
kvalifikasjon, og formuleringen «Where coverage is well below 100% the value is a
lower bound» i den leverte metadataen er sann for FI og upresis for SE4, der
avviket kan gå begge veier.

**Nummerering.** 0013 er ledig over alle refs: 0001-0009 er i bruk på `main`,
`release/v1.3` og fix-grenene, og `v2-dev-dk-fi` bruker i tillegg 0010, 0011 og 0012.
Merk at 0012 der er `0012-resolution-alignment-gen-load.md` og ikke en omnummerert 0009 —
bærings-ADR-en (0009) finnes ikke på den grenen. Numre allokeres over alle refs, ikke over
gjeldende gren.

**Ikke besluttet her:** om dekningsfeltet skal deles i to (uklassifisert andel
kontra kjent-fossil andel), eller om FI i det hele tatt skal leveres til
CodeCarbon. Det andre spørsmålet henger sammen med at FI-feltet i dag bærer en
arvet verdi på 72,0 som ikke er utledet av denne metoden.

## Status for tekst som allerede er ute

ADR-0009-teksten sier ikke at antakelsen finnes. Den bør få en setning som
navngir den og peker hit. Det er en endring i `docs/decisions/0009-*.md`, ikke i
noe publisert artefakt, og den er ikke gjort.
