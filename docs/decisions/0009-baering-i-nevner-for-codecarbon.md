# ADR-0009 — Carrying unfactored generation in the denominator, for the codecarbon delivery only

Status: accepted
Date: 2026-09-03
Supersedes: nothing. Narrows ADR-0001 Decision 2 for one named consumer.

## Context

ADR-0001 Decision 2 says that production types without a verified factor
(Waste, Other, Other renewable) are **excluded from the primary CI**, and that
the fraction of energy they represent is reported as coverage. That is the right
rule for Khepri's own figures, and it stands: the published dataset, the
manuscript, and every number in `docs/` use it unchanged.

It is the wrong rule for one specific consumer.

The per-zone values contributed to codecarbon are applied by that tool as

    emissions = (emission_factor_g / 1000) * energy.kWh

— `codecarbon/core/emissions.py`, `_try_get_nordic_region_emissions`. The stored
number is multiplied by **all** consumed energy. There is no coverage field on
the receiving side, no partial application, no way for the tool to know that the
figure was an average over 85 % of SE4's generation rather than all of it.

Under ADR-0001's rule the delivered number would therefore be applied to energy
it was never averaged over. For a zone with high coverage that is a rounding
question. For SE4, where ENTSO-E books 14.95 % of generation as unspecified
"Other", it is a systematic overstatement of about 17 %: the covered subset is
dirtier than the whole, so dividing by the subset and then multiplying by the
whole inflates the result.

## Decision

For the codecarbon delivery, and only there, unfactored production types are
**carried in the denominator at factor 0** instead of being removed from both
numerator and denominator.

This is exposed as a named parameter, `carry_unfactored_at_zero`, on
`ci.compute`. It defaults to `False`, so every archived figure reproduces
unchanged and the AR5 numbers in the manuscript are untouched. The delivery
passes `True` together with the codecarbon-basis factor table from
`codecarbon_map.py`.

The parameter is deliberately named rather than achieved as a side effect. The
same arithmetic can be produced by passing `excluded=set()` and a factor table
that happens to contain zeros, and v1.2 could in fact do that — but nothing in
v1.2 said so, no ADR described it, and reading the code would tell you the
opposite. A behaviour that only exists as an undocumented parameter combination
is not reproducible in any useful sense, whatever the arithmetic says.

## Consequences

**The two bases give different answers, and the difference has a sign.**
Carrying at zero adds to the denominator and nothing to the numerator, so the
result is always lower than or equal to the excluding variant. On the nine
Nordic zones:

| zone | codecarbon basis, excluding | codecarbon basis, carried at 0 | coverage |
|---|---|---|---|
| SE3 | 28.58 | 27.03 | 94.58 % |
| SE4 | 29.04 | 24.70 | 85.05 % |
| NO4 | 52.41 | 51.70 | 98.65 % |

**The delivered value is a lower bound where coverage is low.** It is a complete
factor over all generation, which is what the consumer needs, but the uncovered
share contributes zero emissions when its true contribution is unknown and
almost certainly positive. The shipped JSON states coverage per zone and says so
for SE4 explicitly. No factor is invented for the uncovered types; that would be
a guess dressed as data, which ADR-0001 rejects for good reason.

**"The placeholder is wrong in both directions" does not survive the basis
change.** On AR5, codecarbon's uniform 18.0 is too high for SE3 (14.53) and SE4
(17.42) and too low for the other seven. On codecarbon's own factor table every
one of the nine zones is above 18.0, so the placeholder is too low everywhere.
Both statements are true of their own basis; neither is true of the other. Any
text making the two-way claim must say which basis it means.

## Alternatives rejected

**Proxy factors for the uncovered types.** `factors.py` already carries
`SENSITIVITY_PROXY` for exactly this, and it is right that it is sensitivity-only.
Shipping a guessed 475 gCO2eq/kWh for "Other" as though it were measured would
make the delivered number look more complete than the evidence supports, which
is the objection that started this.

**Delivering the excluding value with a coverage caveat.** The caveat has
nowhere to live: codecarbon reads one float. A caveat the consumer cannot act on
is not a caveat.

**Changing ADR-0001 globally.** The excluding rule is correct for a published
dataset whose users can read the coverage field, and changing it would move
every figure in the manuscript for the benefit of one downstream consumer.


## Tillegg 2026-09-11 — antakelsen denne beslutningen hviler på

Beslutningen over sier at ubefaktorerte produksjonstyper blir stående i nevneren med
faktor 0. Den sier ikke hva som må være sant for at det skal være forsvarlig.

Antakelsen er at **en ubefaktorert type enten er lav-karbon eller genuint uklassifisert.**
Holder den, er nullen en innrømmelse av uvitenhet: den fortynner CI-en litt, og
fortynningen rapporteres gjennom dekningsfeltet. Holder den ikke — er typen kjent fossil —
uttrykker nullen ikke uvitenhet, men påstår at produksjonen var ren.

Antakelsen holder for hver type som forekommer i NO1–NO5 og SE1–SE4, og det er derfor
denne ADR-en kunne skrives uten å nevne den. Den svikter for finsk torv.

Se **ADR-0013**, som navngir kategorien, gjør bruddet til en feil framfor et stille tall,
og redegjør for hvorfor dekningsfeltet alene ikke fanger forskjellen. Se videre
**ADR-0014**, som fant at kilden bak CodeCarbons faktortabell faktisk plasserer alle fire
typene ADR-0013 navnga, og mappet dem — hvorpå `UNFACTORED_FOSSIL` ble tom og guarden
inert som standard. Mekanismen består; det var listen som var feil, ikke regelen.

Bæring på null gjelder etter dette de typene som verken er kjent fossile eller mappet av
kilden: `Waste`, `Biomass`, `Other`, `Other renewable` og `Marine`.

Ingen verdi i denne ADR-en endres av tillegget. Ingen publisert figur flyttes.
