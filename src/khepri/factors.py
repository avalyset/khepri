"""
Life-cycle emission factors per ENTSO-E production type (gCO2eq/kWh).

SOURCE (Decision 1, ADR-0001): IPCC WG3 AR5 Annex III, Table A.III.2
"Emissions of selected electricity supply technologies (gCO2eq/kWh)",
column "Lifecycle emissions (incl. albedo effect)", Median.

Every value below has been verified against that table in the PRIMARY source:
  https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf
  downloaded 2026-09-01, 757191 bytes, 22 pages
  sha256 dec39383e03caf843f833ad8f4b373f72be3b86ada6d826bd172e8955ffe24c2

Three entries are NOT a direct read of an AR5 median, and are marked as such below:
  - Fossil Oil (650): AR5 Table A.III.2 has no oil row at all. This is a flagged
    approximation. It never occurs in the Nordic extract (0 MW in every zone-year),
    so it does not enter any published figure.
  - Hydro Pumped Storage (24): AR5 has no pumped-storage row; PROXY to the
    Hydropower median. The real footprint depends on the charging source.
  - Solar (48): AR5 carries three solar rows — Solar PV utility 48, Solar PV
    rooftop 41, Concentrated Solar Power 27 — and utility is chosen because
    ENTSO-E reports grid-connected generation. This is the only mapping choice
    with a measurable effect on the published per-zone values: at most
    0.85 gCO2eq/kWh, on SE4, which would read 16.57 instead of 17.42 on the
    rooftop row.

Each factor below is annotated with its source and whether the mapping is DIRECT or PROXY.
"""

SOURCE = (
    "IPCC WG3 AR5 Annex III, Table A.III.2 (lifecycle median, gCO2eq/kWh); "
    "primary source verified 2026-09-01, "
    "sha256 dec39383e03caf843f833ad8f4b373f72be3b86ada6d826bd172e8955ffe24c2"
)

# (factor, source-/mapping note)
FACTOR_TABLE = {
    "Fossil Gas":                      (490, "IPCC AR5 'Gas – combined cycle' median (direct match)"),
    "Hydro Water Reservoir":           (24,  "IPCC AR5 'Hydropower' median (direct match)"),
    "Hydro Run-of-river and poundage": (24,  "IPCC AR5 'Hydropower' median (IPCC has one hydro category)"),
    "Hydro Pumped Storage":            (24,  "PROXY: IPCC 'Hydropower' 24; real footprint depends on the charging source"),
    "Wind Onshore":                    (11,  "IPCC AR5 'Wind onshore' median (direct match)"),
    "Wind Offshore":                   (12,  "IPCC AR5 'Wind offshore' median (direct match)"),
    "Solar":                           (48,  "IPCC AR5 'Solar PV – utility' median; utility row chosen because ENTSO-E reports grid-connected generation (rooftop 41 / CSP 27 also exist)"),
    "Biomass":                         (230, "IPCC AR5 'Biomass – dedicated' median (direct match)"),
    # For robustness (rare/absent in NO 2025 data, but mapped in case it appears; all are
    # MATERIAL and directly matched for the v2 DK/FI zones — coal/oil/gas for DK, nuclear for FI):
    "Fossil Hard coal":                (820, "IPCC AR5 'Coal – PC' median (direct match); material in DK1/DK2"),
    "Geothermal":                      (38,  "IPCC AR5 'Geothermal' median (direct match)"),
    "Nuclear":                         (12,  "IPCC AR5 'Nuclear' median (direct match); dominant in FI"),
    "Marine":                          (17,  "IPCC AR5 'Ocean' median (direct match); occurs in SE3 2021-2022 with zero generation"),
    "Fossil Oil":                      (650, "FLAG: oil has no clean IPCC AR5 median; 650 is a flagged approximation (zero in every NO/SE zone-year; occurs in DK/FI peaking/CHP)"),
}

FACTORS = {k: v[0] for k, v in FACTOR_TABLE.items()}

# Types that occur in the ENTSO-E data but WITHOUT a verified factor in the chosen source.
# Decision 2/consequence (ADR-0001): EXCLUDED from the primary CI; sensitivity is reported.
#   - Waste/Other/Other renewable: original NO/SE set (v1).
#   - "Fossil Peat": added for v2 (occurs materially in FI). IPCC AR5 Annex III has NO peat
#     life-cycle median, so — consistent with the v1 discipline for oil/waste — no authoritative
#     primary factor is invented; peat is EXCLUDED from primary and reported as sensitivity.
# NOTE (v2 materiality caveat): in NO/SE these excluded types are negligible, so the primary CI
# is barely affected. In DK, "Waste" (waste-to-energy CHP) is MATERIAL; excluding it therefore
# biases the DK primary CI DOWNWARD. This is flagged, not silently absorbed — compare the primary
# CI against compute_sensitivity() and report the included-energy share for DK.
EXCLUDED_NO_VERIFIED_FACTOR = {"Waste", "Other", "Other renewable", "Fossil Peat"}

# ONLY for the sensitivity run (never primary). Flagged proxies without their own primary source.
SENSITIVITY_PROXY = {
    "Waste": (580, "FLAG/proxy: waste-to-energy ~580, no IPCC median; sensitivity only"),
    "Other renewable": (230, "FLAG/proxy: assumed biomass-like 230; sensitivity only"),
    # v2 correction: 475 was previously attributed to an IEA world average. That
    # attribution was wrong — IEA Electricity 2026 reports 435 gCO2/kWh for the 2025
    # world average (Electricity 2025: 445 for 2024), and 475 matches no recent IEA
    # figure. The VALUE is retained deliberately: "Other" is an unresolved residual
    # category, and 475 is a deliberately high proxy used to keep the sensitivity run
    # conservative. Only the source claim is corrected, not the number.
    "Other": (475, "FLAG/proxy: deliberately high proxy for an unresolved residual category, not sourced to any published average; sensitivity only (reference point: IEA world average 435 gCO2/kWh for 2025, IEA Electricity 2026)"),
    # v2: IPCC AR5 has no peat median, and no verified peat life-cycle factor exists to invent one.
    # DIRECTION (verified): IPCC 2006 default direct CO2 puts peat at 106 t/TJ ABOVE bituminous coal
    # at 94.6 t/TJ, and peat is NOT treated as biomass (it emits). So peat's true life-cycle value is
    # >= the coal AR5 lifecycle median (820) — 820 is a FLOOR, not a ceiling. 820 is therefore a
    # FLAGGED coal-equivalent LOWER-bound proxy for the sensitivity run ONLY; the true peat value is
    # higher and unbounded above without a verified peat factor. Never the primary figure, never an AR5 value.
    "Fossil Peat": (820, "FLAG/proxy: no IPCC AR5 peat median; coal-equivalent 820 is a LOWER-bound (floor) proxy — true peat >= 820 (IPCC 2006: peat 106 t/TJ > coal 94.6 t/TJ, not biomass); sensitivity only, floor not ceiling"),
}
