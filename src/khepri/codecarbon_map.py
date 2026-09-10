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
    "Fossil Brown coal/Lignite": (
        "coal",
        "codecarbon's table has one coal key, and the data behind it already "
        "includes lignite: the factors come from OWID's `coal_electricity`, "
        "which Ember builds by calculating hard coal and lignite separately "
        "and summing them into one published coal value (Ember, Electricity "
        "Data Methodology, 'Emissions from Electricity Generation - Coal'). "
        "Lignite is therefore not a type the table lacks; it is a type this "
        "mapping had not connected. See ADR-0014. Note the precision loss: "
        "995 is a blended coal figure, and lignite is dirtier than hard coal, "
        "so a lignite-heavy zone is understated by this key.",
    ),
    "Fossil Oil shale": (
        "petroleum",
        "Same table, same reasoning, different key. Ember files oil shale "
        "under 'Other Fossil' (oil and petroleum products), and OWID's export "
        "carries it in `oil_electricity`, not `coal_electricity` - Estonia, "
        "which burns almost nothing but oil shale, reads coal_TWh 0.00 against "
        "oil_TWh 3.56 in codecarbon's own `global_energy_mix.json`. The "
        "codecarbon key fed by `oil` is `petroleum`. See ADR-0014. Note the "
        "precision loss, which is larger here than for lignite: IPCC 2006 Vol. 2 "
        "Ch. 2 Tab. 2.2 puts oil shale at 107 000 kg CO2/TJ, above the whole coal "
        "range in that table (94 600-101 000) and above peat (106 000), so 816 is "
        "a floor for an oil-shale zone, not an estimate.",
    ),
    "Fossil Peat": (
        "petroleum",
        "Ember files peat under 'Other Fossil', which OWID exports through "
        "`oil_electricity` -> `oil_TWh`, and the codecarbon key fed by `oil` is "
        "`petroleum`. Measured against StatFin 12vp for 2023, codecarbon's "
        "Finnish `oil_TWh` of 2.35 is accounted for by oil 0.20 + peat 1.07 + "
        "other fossil 1.01 = 2.28; without peat 1.14 TWh is unexplained. See "
        "ADR-0014. Floor, not estimate: IPCC 2006 Vol. 2 Ch. 2 Tab. 2.2 puts "
        "peat at 106 000 kg CO2/TJ, above every coal grade in that table, so "
        "816 understates a peat-burning zone - and the CHP allocation question "
        "(459-1 922 gCO2eq/kWh_e on the same Finnish statistics) is not settled "
        "by this key, only bounded from below.",
    ),
    "Fossil Coal-derived gas": (
        "petroleum",
        "Same route as peat. Ember's footnote 5 puts 'manufactured gases' under "
        "'Other Fossil'; Eurostat defines manufactured gases as gas works gas, "
        "coke oven gas, blast furnace gas and other recovered gases, which is "
        "what ENTSO-E's coal-derived gas is. OWID carries Other Fossil in "
        "`oil_electricity`, so the key is `petroleum`. See ADR-0014. Floor, not "
        "estimate: the feedstock is coal, and IPCC 2006 Vol. 2 Ch. 2 Tab. 2.2 "
        "puts coal at 94 600-101 000 kg CO2/TJ, so 816 is below the fuel it "
        "derives from.",
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


#: ENTSO-E fossil production types with no codecarbon key. Empty since ADR-0014.
#:
#: ADR-0013 introduced this set with four members, on the reading that
#: codecarbon's table had no key for any of them. That reading was wrong for all
#: four, and ADR-0014 mapped them: lignite to `coal`, and oil shale, peat and
#: coal-derived gas to `petroleum`, each through the OWID/Ember data the factor
#: table is built from. The set is therefore empty, and the guard below is inert
#: by default.
#:
#: It is kept, and so is the guard, because the mechanism is the durable part.
#: The rule ADR-0013 states - that a known-fossil column must not be carried
#: silently at zero - held; what failed was the list of types it named. A future
#: ENTSO-E type with no key belongs here, and callers who want to exercise the
#: guard on a type this module has since mapped can pass `unfactored=` a set of
#: their own.
#:
#: What replaced the guard for these four is the floor caveat stated with each
#: mapping above: the key is a lower bound, and the direction of the error is
#: written down. That is a weaker claim than a factor and a stronger one than a
#: zero.
UNFACTORED_FOSSIL: Set[str] = set()


class UnfactoredFossilError(ValueError):
    """A known-fossil production type occurs with no factor and no decision."""


def codecarbon_factors(
    carry_unfactored: bool = True,
    occurring=None,
    fossil_decisions: Dict[str, float] = None,
    unfactored: Set[str] = None,
) -> Dict[str, float]:
    """
    Build the ENTSO-E-keyed factor table for a codecarbon-basis run.

    Args:
        carry_unfactored: When True (the delivery case), production types with
            no codecarbon key are included at factor 0 so they land in the
            denominator. When False, they are omitted from the table entirely
            and `ci.compute` will drop them from both numerator and denominator
            — the AR5-style treatment, useful for showing the difference.
        occurring: The production types actually present in the extract, if
            known. When given, any `UNFACTORED_FOSSIL` type among them that the
            caller has not decided raises `UnfactoredFossilError`. Omit it only
            for a zone already known to be free of those types; the delivery
            path should always pass `df.columns`.
        fossil_decisions: Explicit factor per unfactored type the caller has
            taken a position on. The position must be stated here, with its
            source, rather than falling out of a default.
        unfactored: The set of known-fossil types to guard, defaulting to
            `UNFACTORED_FOSSIL`. That set is empty since ADR-0014, so the guard
            is inert unless a caller names types explicitly. Pass a set here to
            exercise the mechanism, or to guard a type this module has mapped
            but the caller does not accept the mapping for.

    Returns:
        ENTSO-E production type -> gCO2eq/kWh, ready to pass as `factors=`.

    Raises:
        UnfactoredFossilError: `occurring` contains a known-fossil type with no
            codecarbon key that `fossil_decisions` does not resolve. Failing
            here is the point: the alternative is a silent zero that understates
            the zone, which is what happens without this guard.
    """
    table = {
        entsoe: CODECARBON_FACTORS[key]
        for entsoe, (key, _why) in ENTSOE_TO_CODECARBON.items()
    }
    if carry_unfactored:
        table.update({t: 0.0 for t in NO_CODECARBON_CATEGORY})

    guarded = UNFACTORED_FOSSIL if unfactored is None else set(unfactored)
    decided = dict(fossil_decisions or {})
    stray = sorted(set(decided) - guarded)
    if stray:
        raise ValueError(
            "fossil_decisions may only name guarded unfactored types; got "
            + ", ".join(stray)
        )

    if occurring is not None:
        undecided = sorted((set(occurring) & guarded) - set(decided))
        if undecided:
            raise UnfactoredFossilError(
                "known-fossil production type(s) with no codecarbon factor and no "
                "decision from the caller: " + ", ".join(undecided) + ". "
                "Carrying these at zero would assert the generation was clean. "
                "Pass fossil_decisions={'<type>': <gCO2eq/kWh>} with the source "
                "stated, or drop the zone."
            )

    table.update(decided)
    return table


def mapping_report() -> str:
    """Human-readable mapping table, for the delivery PR's provenance field."""
    lines = ["ENTSO-E type -> codecarbon key (gCO2eq/kWh) — why"]
    for entsoe, (key, why) in sorted(ENTSOE_TO_CODECARBON.items()):
        lines.append(f"  {entsoe:34} -> {key:18} ({CODECARBON_FACTORS[key]:>4}) — {why}")
    lines.append("  no codecarbon key, carried at 0: " + ", ".join(sorted(NO_CODECARBON_CATEGORY)))
    return "\n".join(lines)
