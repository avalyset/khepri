"""
Livssyklus-utslippsfaktorer per ENTSO-E produksjonstype (gCO2eq/kWh).

KILDE (Beslutning 1, ADR-0001): IPCC WG3 AR5 Annex III, Table A.III.2 —
livssyklus-medianer. Primærkilde (IPCC-PDF) ikke direkte nåbar fra byggemiljøet;
verdiene er hentet fra en sjekkbar SEKUNDÆRKILDE som navngir tabellen:
  https://en.wikipedia.org/wiki/Life-cycle_greenhouse_gas_emissions_of_energy_sources
  (kolonne "IPCC 2014 / Annex III, Table A.III.2", median g CO2eq/kWh)
Uavhengig bekreftet for coal=820 / gas=490 mot:
  https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf

Hver faktor under er merket med kilde og om mappingen er DIREKTE eller PROXY.
"""

SOURCE = (
    "IPCC WG3 AR5 Annex III, Table A.III.2 (livssyklus-median, gCO2eq/kWh); "
    "sekundærkilde: en.wikipedia.org/wiki/Life-cycle_greenhouse_gas_emissions_of_energy_sources"
)

# (faktor, kilde-/mapping-merknad)
FACTOR_TABLE = {
    "Fossil Gas":                      (490, "IPCC AR5 'Gas – combined cycle' median (direkte match)"),
    "Hydro Water Reservoir":           (24,  "IPCC AR5 'Hydropower' median (direkte match)"),
    "Hydro Run-of-river and poundage": (24,  "IPCC AR5 'Hydropower' median (IPCC har én hydro-kategori)"),
    "Hydro Pumped Storage":            (24,  "PROXY: IPCC 'Hydropower' 24; reelt fotavtrykk avhenger av ladekilde"),
    "Wind Onshore":                    (11,  "IPCC AR5 'Wind onshore' median (direkte match)"),
    "Wind Offshore":                   (12,  "IPCC AR5 'Wind offshore' median (direkte match)"),
    "Solar":                           (48,  "IPCC AR5 'Solar PV – utility' median (direkte match)"),
    "Biomass":                         (230, "IPCC AR5 'Biomass – dedicated' median (direkte match)"),
    # For robusthet (forekommer ikke i NO 2025-data, men mappet om de dukker opp):
    "Fossil Hard coal":                (820, "IPCC AR5 'Coal – PC' median (direkte match)"),
    "Geothermal":                      (38,  "IPCC AR5 'Geothermal' median (direkte match)"),
    "Nuclear":                         (12,  "IPCC AR5 'Nuclear' median (direkte match)"),
    "Fossil Oil":                      (650, "FLAGG: olje har ingen ren IPCC AR5-median; 650 er en flagget approks. (forekommer ikke i NO 2025)"),
}

FACTORS = {k: v[0] for k, v in FACTOR_TABLE.items()}

# Typer som forekommer i NO-data, men UTEN verifisert faktor i den valgte kilden.
# Beslutning 2/konsekvens (ADR-0001): EKSKLUDERES fra primær-CI; sensitivitet rapporteres.
EXCLUDED_NO_VERIFIED_FACTOR = {"Waste", "Other", "Other renewable"}

# KUN for sensitivitets-kjøring (aldri primær). Flaggede proxyer uten egen primærkilde.
SENSITIVITY_PROXY = {
    "Waste": (580, "FLAGG/proxy: waste-to-energy ~580, ingen IPCC-median; kun sensitivitet"),
    "Other renewable": (230, "FLAGG/proxy: antatt biomass-lik 230; kun sensitivitet"),
    "Other": (475, "FLAGG/proxy: IEA verdens-snitt 475; kun sensitivitet"),
}
