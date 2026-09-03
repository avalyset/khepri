"""
ENTSO-E production type -> codecarbon emission factor, for the upstream delivery.

Khepri's own figures use IPCC AR5 Annex III lifecycle medians (`factors.py`).
That is the right basis for the archived dataset and the manuscript, and it does
not change. This module exists for a different consumer: the per-zone values
contributed to codecarbon, which its maintainer asked to be derived on
codecarbon's own factor table so they stay internally consistent with the rest
of that tool. See ADR-0009.

The two bases differ materially for exactly the sources that dominate the Nordic
mix, which is why the same zone gets two different numbers:

    source          AR5 (khepri)   codecarbon
    nuclear                   12           29
    wind                      11           26
    hydro                     24           26
    natural gas              490          743

Every mapping below is stated with the codecarbon key it resolves to and why.
A production type that codecarbon has no key for is NOT given an invented
factor: it is listed in `NO_CODECARBON_CATEGORY` and carried at zero (ADR-0009),
which is what makes the shipped number a complete factor over all generation.
"""

from typing import Dict, Set

#: codecarbon's own table, `codecarbon/data/private_infra/carbon_intensity_per_source.json`,
#: as of codecarbon 3.2.8. Values in gCO2eq/kWh. Reproduced here so the mapping is
#: auditable without a codecarbon checkout; the delivery script should read the
#: live file and assert equality against this dict rather than trusting the copy.
CODECARBON_FACTORS: Dict[str, float] = {
    "coal": 995,
    "petroleum": 816,
    "natural_gas": 743,
    "geothermal": 38,
    "solar": 48,
    "hydroelectricity": 26,
    "wind": 26,
    "nuclear": 29,
}

#: ENTSO-E production type -> (codecarbon key, why this key).
#:
#: ENTSO-E is finer-grained than codecarbon on hydro and wind, so several ENTSO-E
#: types collapse onto one codecarbon key. That is a loss of resolution, not an
#: assumption: codecarbon simply has no separate onshore/offshore or
#: reservoir/run-of-river figure to map to.
ENTSOE_TO_CODECARBON: Dict[str, tuple] = {
    "Fossil Gas": (
        "natural_gas",
        "Direct. codecarbon's only gas key.",
    ),
    "Fossil Hard coal": (
        "coal",
        "Direct. Does not occur in any Nordic zone-year in this dataset.",
    ),
    "Fossil Oil": (
        "petroleum",
        "Direct. Zero in every Nordic zone-year in this dataset.",
    ),
    "Nuclear": (
        "nuclear",
        "Direct. Occurs only in SE3 among the nine zones.",
    ),
    "Solar": (
        "solar",
        "Direct. codecarbon has one solar figure and does not split "
        "utility/rooftop/CSP the way AR5 does.",
    ),
    "Geothermal": (
        "geothermal",
        "Direct. Does not occur in any Nordic zone-year in this dataset.",
    ),
    "Hydro Water Reservoir": (
        "hydroelectricity",
        "codecarbon has a single hydro key; reservoir, run-of-river and pumped "
        "storage all resolve to it.",
    ),
    "Hydro Run-of-river and poundage": (
        "hydroelectricity",
        "As above — same key, no separate run-of-river figure exists.",
    ),
    "Hydro Pumped Storage": (
        "hydroelectricity",
        "As above. Note this inherits AR5's known weakness: the real footprint "
        "depends on the charging source, which neither table models.",
    ),
    "Wind Onshore": (
        "wind",
        "codecarbon has a single wind key; onshore and offshore both resolve to it.",
    ),
    "Wind Offshore": (
        "wind",
        "As above — same key, no separate offshore figure exists.",
    ),
}

#: ENTSO-E types that occur in Nordic data and have NO codecarbon key.
#:
#: Not an oversight and not a gap to be filled with a proxy. codecarbon's table
#: is a list of generation technologies; these ENTSO-E categories are either
#: unspecified ("Other") or a technology codecarbon does not carry a figure for.
#: Under ADR-0009 they are carried in the denominator at factor zero rather than
#: removed, and the resulting coverage is reported per zone.
NO_CODECARBON_CATEGORY: Set[str] = {
    "Other",
    "Other renewable",
    "Waste",
    "Biomass",
    "Marine",
}


def codecarbon_factors(carry_unfactored: bool = True) -> Dict[str, float]:
    """
    Build the ENTSO-E-keyed factor table for a codecarbon-basis run.

    Args:
        carry_unfactored: When True (the delivery case), production types with
            no codecarbon key are included at factor 0 so they land in the
            denominator. When False, they are omitted from the table entirely
            and `ci.compute` will drop them from both numerator and denominator
            — the AR5-style treatment, useful for showing the difference.

    Returns:
        ENTSO-E production type -> gCO2eq/kWh, ready to pass as `factors=`.
    """
    table = {
        entsoe: CODECARBON_FACTORS[key]
        for entsoe, (key, _why) in ENTSOE_TO_CODECARBON.items()
    }
    if carry_unfactored:
        table.update({t: 0.0 for t in NO_CODECARBON_CATEGORY})
    return table


def mapping_report() -> str:
    """Human-readable mapping table, for the delivery PR's provenance field."""
    lines = ["ENTSO-E type -> codecarbon key (gCO2eq/kWh) — why"]
    for entsoe, (key, why) in sorted(ENTSOE_TO_CODECARBON.items()):
        lines.append(f"  {entsoe:34} -> {key:18} ({CODECARBON_FACTORS[key]:>4}) — {why}")
    lines.append("  no codecarbon key, carried at 0: " + ", ".join(sorted(NO_CODECARBON_CATEGORY)))
    return "\n".join(lines)
