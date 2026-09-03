"""Regression: both published bases, all nine zones, pinned to the shipped values.

Two numbers exist per zone and they are not interchangeable:

  * the AR5 figure, which is what the archive, the manuscript and every `docs/`
    table report, computed with unfactored types excluded (ADR-0001);
  * the codecarbon figure, computed on that tool's own factor table with
    unfactored types carried in the denominator at zero (ADR-0009), which is
    what the upstream pull requests ship.

v1.2 could produce the second only as an undocumented side effect of passing
`excluded=set()` together with a factor table containing zeros. Nothing recorded
that, so the shipped values were not reproducible from the archive in any
meaningful sense. These tests pin both, so neither can drift without failing.

The expected values are the published ones: the AR5 column is Table 1 of the
manuscript, the codecarbon column is `nordic_emissions.json` on the branches of
mlco2/codecarbon#1260 and #1262.
"""

import json
import pathlib

import pandas as pd
import pytest

from khepri.ci import compute
from khepri.codecarbon_map import (
    CODECARBON_FACTORS,
    ENTSOE_TO_CODECARBON,
    NO_CODECARBON_CATEGORY,
    codecarbon_factors,
)
from khepri.factors import EXCLUDED_NO_VERIFIED_FACTOR, FACTORS

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

#: Manuscript Table 1 — AR5 basis, unfactored excluded.
AR5_EXPECTED = {
    "NO1": 23.31, "NO2": 23.85, "NO3": 21.46, "NO4": 39.65, "NO5": 24.46,
    "SE1": 20.63, "SE2": 20.11, "SE3": 14.53, "SE4": 17.42,
}

#: nordic_emissions.json as shipped in the two upstream PRs — codecarbon basis,
#: unfactored carried at zero. One decimal, as the file stores them.
CODECARBON_EXPECTED = {
    "NO1": 26.0, "NO2": 27.0, "NO3": 25.8, "NO4": 51.7, "NO5": 26.6,
    "SE1": 25.9, "SE2": 25.7, "SE3": 27.0, "SE4": 24.7,
}

#: Coverage per zone — the share of generation carrying a codecarbon factor.
#: Identical on both bases: coverage depends on which types lack a factor, not
#: on the factor values.
#:
#: Measured over the same clean intervals the CI itself uses, which is why NO3
#: reads 99.32 and not the 99.31 a naive all-intervals sum gives — NO3 drops
#: 6.15 % of intervals on a NaN in a material type, and coverage has to be
#: quoted on the same footing as the number it qualifies.
COVERAGE_EXPECTED = {
    "NO1": 99.58, "NO2": 99.89, "NO3": 99.32, "NO4": 98.65, "NO5": 99.67,
    "SE1": 99.59, "SE2": 98.92, "SE3": 94.58, "SE4": 85.05,
}

ZONES = sorted(AR5_EXPECTED)


def _load(zone):
    path = FIXTURES / f"{zone}_generation_2025.csv"
    if not path.exists():
        pytest.skip(
            f"fixture {path.name} absent — ENTSO-E terms do not permit "
            "redistributing raw extracts; see README for the documented query"
        )
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True, format="mixed")
    return df.apply(pd.to_numeric, errors="coerce")


@pytest.mark.parametrize("zone", ZONES)
def test_ar5_basis_reproduces_the_manuscript(zone):
    r = compute(_load(zone), factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR)
    assert round(r["ci"], 2) == AR5_EXPECTED[zone]
    assert r["carried_at_zero"] is False


@pytest.mark.parametrize("zone", ZONES)
def test_codecarbon_basis_reproduces_the_shipped_value(zone):
    r = compute(
        _load(zone),
        factors=codecarbon_factors(carry_unfactored=True),
        excluded=set(),
        carry_unfactored_at_zero=True,
    )
    assert round(r["ci"], 1) == CODECARBON_EXPECTED[zone]
    assert r["carried_at_zero"] is True


@pytest.mark.parametrize("zone", ZONES)
def test_coverage_is_the_same_on_both_bases(zone):
    df = _load(zone)
    a = compute(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR)
    b = compute(df, factors=codecarbon_factors(carry_unfactored=False), excluded=set())
    assert round(a["included_energy_share_pct"], 2) == COVERAGE_EXPECTED[zone]
    assert round(b["included_energy_share_pct"], 2) == COVERAGE_EXPECTED[zone]


@pytest.mark.parametrize("zone", ZONES)
def test_carrying_never_raises_the_value(zone):
    """Adding to the denominator and nothing to the numerator can only lower it."""
    df = _load(zone)
    excluding = compute(df, factors=codecarbon_factors(carry_unfactored=False),
                        excluded=set())
    carried = compute(df, factors=codecarbon_factors(carry_unfactored=True),
                      excluded=set(), carry_unfactored_at_zero=True)
    assert carried["ci"] <= excluding["ci"] + 1e-9


def test_the_default_is_the_archived_behaviour():
    """v1.2 reproduces unchanged: the new parameter must be opt-in."""
    import inspect

    sig = inspect.signature(compute)
    assert sig.parameters["carry_unfactored_at_zero"].default is False


def test_every_mapped_key_exists_in_the_codecarbon_table():
    for entsoe, (key, why) in ENTSOE_TO_CODECARBON.items():
        assert key in CODECARBON_FACTORS, f"{entsoe} maps to unknown key {key}"
        assert why.strip(), f"{entsoe} has no stated reason"


def test_no_type_is_both_mapped_and_unmapped():
    assert not (set(ENTSOE_TO_CODECARBON) & NO_CODECARBON_CATEGORY)


def test_unfactored_types_are_zero_not_absent():
    """The zero is the mechanism — an absent key would drop them from the denominator."""
    table = codecarbon_factors(carry_unfactored=True)
    for t in NO_CODECARBON_CATEGORY:
        assert table[t] == 0.0
    lean = codecarbon_factors(carry_unfactored=False)
    for t in NO_CODECARBON_CATEGORY:
        assert t not in lean


def test_the_two_bases_disagree_about_the_placeholder():
    """18.0 is wrong in both directions on AR5, and too low everywhere on codecarbon's.

    This is the claim the manuscript and the op-ed make, and it does not survive
    the basis change. Pinned so the asymmetry stays visible.
    """
    placeholder = 18.0
    ar5_high = [z for z, v in AR5_EXPECTED.items() if v < placeholder]
    ar5_low = [z for z, v in AR5_EXPECTED.items() if v > placeholder]
    assert ar5_high == ["SE3", "SE4"] or sorted(ar5_high) == ["SE3", "SE4"]
    assert len(ar5_low) == 7
    assert all(v > placeholder for v in CODECARBON_EXPECTED.values())
