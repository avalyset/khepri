"""
The guard against a known-fossil production type carried silently at zero.

ADR-0009 lets `ci.compute` keep unfactored production types in the denominator
at factor 0, so the delivered number is a complete factor over all generation.
That rule rests on an assumption it never states: that an unfactored type is
either low-carbon or genuinely unclassified. The assumption holds for every
type present in NO1-NO5 and SE1-SE4. It fails for Finnish peat, which is
unambiguously fossil and has no key in codecarbon's table — so the zero does
not express ignorance, it asserts cleanliness.

These tests pin three things:
  1. the guard fires when a known-fossil unfactored type occurs,
  2. it stays silent once the caller has taken an explicit position,
  3. neither the guard nor NOT_GENERATION moves any published NO/SE figure.
"""

import os
import pathlib

import pandas as pd
import pytest

from khepri.ci import compute, load_zone, NOT_GENERATION
from khepri.codecarbon_map import (
    UNFACTORED_FOSSIL,
    UnfactoredFossilError,
    codecarbon_factors,
)
from khepri.factors import EXCLUDED_NO_VERIFIED_FACTOR, FACTORS

DATA = pathlib.Path(os.path.expanduser("~/khepri-data"))
NO_RAW = DATA / "raw" / "entsoe-rest"
SE_RAW = DATA / "se" / "raw" / "entsoe-rest"
FI_RAW = DATA / "v2-dk-fi"

#: The archived v1.3 values, captured from `main` before this branch
#: existed and pasted in at full precision — so a one-ulp drift fails.
AR5_V13 = {
    "NO1": 23.31162858891313,
    "NO2": 23.851315739018723,
    "NO3": 21.457208033933394,
    "NO4": 39.64679307631032,
    "NO5": 24.456171524455687,
    "SE1": 20.634644893839152,
    "SE2": 20.109625975166228,
    "SE3": 14.526500226853216,
    "SE4": 17.417209452008876,
}
CC_V13 = {
    "NO1": 26.02602949183897,
    "NO2": 27.04065740131279,
    "NO3": 25.822848533954453,
    "NO4": 51.702379543808725,
    "NO5": 26.614926530458803,
    "SE1": 25.901683698334576,
    "SE2": 25.748416488725407,
    "SE3": 27.027457158261804,
    "SE4": 24.68319804035372,
}
ZONES = sorted(AR5_V13)


def _path(zone):
    root = SE_RAW if zone.startswith("SE") else NO_RAW
    return root / f"{zone}_generation_2025.csv"


def _load(zone):
    p = _path(zone)
    if not p.exists():
        pytest.skip(
            f"{p.name} absent — ENTSO-E terms do not permit redistributing raw "
            "extracts; see README for the documented query"
        )
    return load_zone(p)


# --- 1. the guard fires ---------------------------------------------------

def test_peat_is_registered_as_unfactored_fossil():
    assert "Fossil Peat" in UNFACTORED_FOSSIL
    # and it genuinely has no codecarbon key
    assert "Fossil Peat" not in codecarbon_factors(carry_unfactored=True)


def test_guard_raises_when_a_known_fossil_type_occurs_undecided():
    with pytest.raises(UnfactoredFossilError) as exc:
        codecarbon_factors(True, occurring=["Nuclear", "Fossil Peat", "Wind Onshore"])
    assert "Fossil Peat" in str(exc.value)


def test_guard_names_every_undecided_type_not_just_the_first():
    # The pair is peat + coal-derived gas because ADR-0014 mapped oil shale,
    # which used to stand here. The property under test is unchanged: every
    # undecided type must be named, not just the one sorted first.
    with pytest.raises(UnfactoredFossilError) as exc:
        codecarbon_factors(True, occurring=["Fossil Peat", "Fossil Coal-derived gas"])
    msg = str(exc.value)
    assert "Fossil Peat" in msg and "Fossil Coal-derived gas" in msg


def test_guard_is_silent_once_the_caller_has_decided():
    t = codecarbon_factors(
        True, occurring=["Fossil Peat", "Nuclear"],
        fossil_decisions={"Fossil Peat": 1071.0},
    )
    assert t["Fossil Peat"] == 1071.0
    assert t["Nuclear"] == 29


def test_a_decision_on_a_type_that_is_not_unfactored_fossil_is_rejected():
    with pytest.raises(ValueError):
        codecarbon_factors(True, fossil_decisions={"Nuclear": 1.0})


def test_omitting_occurring_keeps_the_old_signature_working():
    """The pre-guard call must return exactly the pre-guard table."""
    t = codecarbon_factors(carry_unfactored=True)
    assert t["Fossil Gas"] == 743 and t["Other"] == 0.0
    assert "Fossil Peat" not in t


@pytest.mark.skipif(not (FI_RAW / "FI_generation_2025.csv").exists(),
                    reason="FI extract absent")
def test_finland_fails_high_rather_than_silently_low():
    """FI is the zone the guard exists for: it must not compute by accident."""
    df = load_zone(FI_RAW / "FI_generation_2025.csv")
    assert "Fossil Peat" in df.columns
    with pytest.raises(UnfactoredFossilError):
        codecarbon_factors(True, occurring=df.columns)


@pytest.mark.skipif(not (FI_RAW / "FI_generation_2025.csv").exists(),
                    reason="FI extract absent")
def test_the_silent_zero_understates_finland_materially():
    """Quantifies what the guard prevents, so the cost is on the record."""
    df = load_zone(FI_RAW / "FI_generation_2025.csv")
    silent = compute(df, factors=codecarbon_factors(True), excluded=set(),
                     carry_unfactored_at_zero=True)["ci"]
    decided = compute(
        df,
        factors=codecarbon_factors(True, occurring=df.columns,
                                   fossil_decisions={"Fossil Peat": 1071.0}),
        excluded=set(), carry_unfactored_at_zero=True,
    )["ci"]
    assert decided > silent
    assert (decided - silent) / silent > 0.30   # measured: ~42 % in 2025


# --- 2. NOT_GENERATION ----------------------------------------------------

def test_energy_storage_is_not_generation():
    assert "Energy storage" in NOT_GENERATION


def test_energy_storage_never_reaches_the_denominator():
    idx = pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC")
    df = pd.DataFrame(
        {"Wind Onshore": [100.0] * 4, "Energy storage": [900.0] * 4}, index=idx
    )
    r = compute(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR)
    # Wind alone: 11 gCO2eq/kWh. If storage diluted the denominator it would be 1.1.
    assert r["ci"] == pytest.approx(11.0)
    assert r["dropped_not_generation"] == ["Energy storage"]


def test_opting_out_of_not_generation_restores_the_old_behaviour():
    idx = pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC")
    df = pd.DataFrame(
        {"Wind Onshore": [100.0] * 4, "Energy storage": [900.0] * 4}, index=idx
    )
    r = compute(df, factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR,
                carry_unfactored_at_zero=True, not_generation=frozenset())
    assert r["ci"] == pytest.approx(1.1)


# --- 3. nothing published moves -------------------------------------------

@pytest.mark.parametrize("zone", ZONES)
def test_no_and_se_are_bit_identical_on_the_ar5_basis(zone):
    r = compute(_load(zone), factors=FACTORS, excluded=EXCLUDED_NO_VERIFIED_FACTOR)
    assert r["ci"] == AR5_V13[zone]


@pytest.mark.parametrize("zone", ZONES)
def test_no_and_se_are_bit_identical_on_the_codecarbon_basis(zone):
    df = _load(zone)
    r = compute(df, factors=codecarbon_factors(True, occurring=df.columns),
                excluded=set(), carry_unfactored_at_zero=True)
    assert r["ci"] == CC_V13[zone]


@pytest.mark.parametrize("zone", ZONES)
def test_the_guard_does_not_fire_for_any_published_zone(zone):
    """No NO/SE zone contains a known-fossil unfactored type — so the guard is
    inert for everything already published. That is why it is safe to default on."""
    df = _load(zone)
    codecarbon_factors(True, occurring=df.columns)          # must not raise
    assert set(df.columns) & set(NOT_GENERATION) == set()


# --- 4. ADR-0014: the guard's list is shorter, and the line is where it belongs ---

def test_lignite_and_oil_shale_are_mapped_not_guarded():
    """ADR-0014. Both were in UNFACTORED_FOSSIL on the reading that codecarbon
    had no key for them. It has: lignite sits inside `coal` and oil shale
    inside `petroleum`, through the OWID/Ember data the table is built from."""
    t = codecarbon_factors(carry_unfactored=True)
    assert t["Fossil Brown coal/Lignite"] == 995
    assert t["Fossil Oil shale"] == 816
    assert "Fossil Brown coal/Lignite" not in UNFACTORED_FOSSIL
    assert "Fossil Oil shale" not in UNFACTORED_FOSSIL


def test_the_guard_still_holds_peat_and_coal_derived_gas():
    """The residue is genuine: the source taxonomy does not name peat at all,
    and files coal-derived gas under 'Other Fossil' with no key to map to."""
    assert UNFACTORED_FOSSIL == {"Fossil Peat", "Fossil Coal-derived gas"}
    t = codecarbon_factors(carry_unfactored=True)
    assert "Fossil Peat" not in t
    assert "Fossil Coal-derived gas" not in t


def test_a_lignite_heavy_mix_passes_the_guard():
    """A DE_LU-shaped mix: lignite, gas, wind, solar, biomass. Before ADR-0014
    this raised; now the lignite is factored and the zone computes."""
    occurring = ["Fossil Brown coal/Lignite", "Fossil Gas", "Wind Onshore",
                 "Solar", "Biomass", "Waste"]
    t = codecarbon_factors(True, occurring=occurring)      # must not raise
    assert t["Fossil Brown coal/Lignite"] == 995
    assert t["Biomass"] == 0.0                             # still carried at zero


def test_peat_still_raises_in_the_same_mix():
    """Same zone shape plus peat: the guard fires, and names only peat."""
    occurring = ["Fossil Brown coal/Lignite", "Fossil Gas", "Wind Onshore",
                 "Solar", "Biomass", "Waste", "Fossil Peat"]
    with pytest.raises(UnfactoredFossilError) as exc:
        codecarbon_factors(True, occurring=occurring)
    msg = str(exc.value)
    assert "Fossil Peat" in msg
    assert "Fossil Brown coal/Lignite" not in msg


def test_a_lignite_zone_computes_a_higher_ci_than_it_did_at_zero():
    """The point of the mapping, on a synthetic BA-shaped mix: 61 % lignite
    carried at zero reads clean; mapped to `coal` it does not."""
    df = pd.DataFrame(
        {"Fossil Brown coal/Lignite": [61.0], "Hydro Water Reservoir": [39.0]},
        index=pd.to_datetime(["2025-01-01T00:00Z", "2025-01-01T01:00Z"])[:1],
    )
    mapped = compute(df, factors=codecarbon_factors(True, occurring=df.columns),
                     excluded=set(), carry_unfactored_at_zero=True)
    at_zero = compute(df, factors={"Hydro Water Reservoir": 26.0,
                                   "Fossil Brown coal/Lignite": 0.0},
                      excluded=set(), carry_unfactored_at_zero=True)
    assert at_zero["ci"] == pytest.approx(10.14, abs=0.01)
    assert mapped["ci"] == pytest.approx(617.09, abs=0.01)
    assert mapped["ci"] > at_zero["ci"]
