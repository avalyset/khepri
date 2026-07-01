"""
Life-cycle emission factors per ENTSO-E production type (gCO2eq/kWh).

SOURCE (Decision 1, ADR-0001): IPCC WG3 AR5 Annex III, Table A.III.2 —
life-cycle medians. The primary source (IPCC PDF) is not directly reachable from the
build environment; the values are taken from a checkable SECONDARY SOURCE that names
the table:
  https://en.wikipedia.org/wiki/Life-cycle_greenhouse_gas_emissions_of_energy_sources
  (column "IPCC 2014 / Annex III, Table A.III.2", median g CO2eq/kWh)
Independently confirmed for coal=820 / gas=490 against:
  https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf

Each factor below is annotated with its source and whether the mapping is DIRECT or PROXY.
"""

SOURCE = (
    "IPCC WG3 AR5 Annex III, Table A.III.2 (life-cycle median, gCO2eq/kWh); "
    "secondary source: en.wikipedia.org/wiki/Life-cycle_greenhouse_gas_emissions_of_energy_sources"
)

# (factor, source-/mapping note)
FACTOR_TABLE = {
    "Fossil Gas":                      (490, "IPCC AR5 'Gas – combined cycle' median (direct match)"),
    "Hydro Water Reservoir":           (24,  "IPCC AR5 'Hydropower' median (direct match)"),
    "Hydro Run-of-river and poundage": (24,  "IPCC AR5 'Hydropower' median (IPCC has one hydro category)"),
    "Hydro Pumped Storage":            (24,  "PROXY: IPCC 'Hydropower' 24; real footprint depends on the charging source"),
    "Wind Onshore":                    (11,  "IPCC AR5 'Wind onshore' median (direct match)"),
    "Wind Offshore":                   (12,  "IPCC AR5 'Wind offshore' median (direct match)"),
    "Solar":                           (48,  "IPCC AR5 'Solar PV – utility' median (direct match)"),
    "Biomass":                         (230, "IPCC AR5 'Biomass – dedicated' median (direct match)"),
    # For robustness (does not occur in NO 2025 data, but mapped in case it appears):
    "Fossil Hard coal":                (820, "IPCC AR5 'Coal – PC' median (direct match)"),
    "Geothermal":                      (38,  "IPCC AR5 'Geothermal' median (direct match)"),
    "Nuclear":                         (12,  "IPCC AR5 'Nuclear' median (direct match)"),
    "Fossil Oil":                      (650, "FLAG: oil has no clean IPCC AR5 median; 650 is a flagged approximation (does not occur in NO 2025)"),
}

FACTORS = {k: v[0] for k, v in FACTOR_TABLE.items()}

# Types that occur in NO data but WITHOUT a verified factor in the chosen source.
# Decision 2/consequence (ADR-0001): EXCLUDED from the primary CI; sensitivity is reported.
EXCLUDED_NO_VERIFIED_FACTOR = {"Waste", "Other", "Other renewable"}

# ONLY for the sensitivity run (never primary). Flagged proxies without their own primary source.
SENSITIVITY_PROXY = {
    "Waste": (580, "FLAG/proxy: waste-to-energy ~580, no IPCC median; sensitivity only"),
    "Other renewable": (230, "FLAG/proxy: assumed biomass-like 230; sensitivity only"),
    "Other": (475, "FLAG/proxy: IEA world average 475; sensitivity only"),
}
