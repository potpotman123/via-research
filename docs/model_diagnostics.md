# Model diagnostics (2026-09-21): what drives the DCF, what the hazards are, and how to fix the funding tags

## 1. Scenario runs (scratch copies of KW VIA MODEL.xlsx; `scripts/m3_scenarios.py`)
| Scenario | 2027 growth | 2027 services growth | 2035 revenue | 2035 GM | 2035 adj. EBITDA margin | UFCF 2030 / 2035 | DCF blended $/sh | SOTP $/sh |
|---|---|---|---|---|---|---|---|---|
| S0 base | 12.1% | 13.5% | 1,103 | 36.2% | 8.6% | (52) / 14 | 3.85 | 19.73 |
| S1 all hazards, cuts and expiry losses off | 15.3% | 17.8% | 1,176 | 35.4% | 7.9% | (63) / 8 | 3.06 | 19.85 |
| S2 high services growth (400/350/300/300 vehicle-equivalents, plug +30/25/20/15%, expansion 10/8/6/5%, intl +10/10/8/6%, fades 12-6%) | 19.2% | 22.6% | 1,515 | 34.0% | 6.3% | (88) / (9) | 1.26 | 20.12 |
| S3 = S2 + services GM held at 26% | 19.2% | 22.6% | 1,515 | 35.6% | 7.9% | (72) / 10 | 3.44 | 20.18 |
| S4 = S3 + opex path for a services-heavy company (R&D 14%->8%, S&M 12%->7%, G&A 15%->8.5% of revenue, 2028-35) | 19.2% | 22.6% | 1,515 | 35.6% | 18.4% | 8 / 129 | 16.59 | 20.18 |

Reading: growth does not move the DCF. Doubling 2035 revenue (S2 vs S0) lowers it, because at a ~36% blended gross margin and operating expenses held at 34%
of revenue plus 5% stock compensation, each incremental services dollar carries a negative operating margin. The DCF is a function of the cost structure
in the Three Statements, which was built for a software company 2.3x this size. With an opex path fit to a services-heavy company (S4), the same revenue
engine gives $16.59 a share against a $19-20 SOTP, and the two methods agree on a 30%-40% downside.

## 2. Hazards: what each one is and where the number came from
The contract layer multiplies each contract's run-rate by (1 - annual hazard) every year after 2025, applies a one-time level cut in FY2027, and after
the contract's end date multiplies by a renewal probability. Each figure is an input on the Contract Layer (rows 82-90).
| Parameter | Value | Basis | Status |
|---|---|---|---|
| Competitive hazard, turnkey | 0.5%/yr | No competitive turnkey loss in NTD RY2019-24 across 26 agencies (~80 agency-years); a floor, not an observation | measured (zero) |
| Competitive churn, software | 3.5%/yr | 6-7 Spare/RideCo displacements in ~2.5 years among ~70 documented software relationships | measured |
| Local funding hazard | 2%/yr | Budget-driven exits in the census (SacRT, SARTA, Palo Alto, Milwaukee, Jersey City, Montgomery): ~6 in 3 years among ~100 operations agencies | semi-measured |
| Downsell, locally funded operations | 3%/yr | Ceiling cuts GRR does not count (Palo Alto $3.24mm to $1.1mm, Arlington $30.2mm to $20.8mm, Milwaukee to $0.75mm); dollar-weighted judgment | judgment |
| Federal formula: annual / FY2027 level cut / renewal | 0% / 10% / 0.85 | Formula funds continue; the FY2027 cut is an appropriations judgment; 0.85 at re-bid | judgment |
| Federal one-time: renewal at expiry | 0.55 | CARES/ARPA/Sandbox pilots: Volusia and Suffolk continued, Milwaukee cut, SARTA ended: about half | semi-measured, small sample |
| State grant: renewal at expiry | 0.70 | TRiP, LCTOP, CPUC cycles renew most of the time | judgment |
| Unknown tag: 1%/yr, 0.75 renewal, 3% cut | blend | weighted by the documented funding mix (local ~45%, grant-linked ~30%) | guess by construction |
Effect: S1 shows the hazards remove ~4 points of 2027 services growth and ~7% of 2035 revenue. They matter for the growth bridge; they do not decide the valuation.

## 3. Funding tags: 35 of 59 rows are 'unknown'. Three ways to resolve them, cheapest first
1. Mine the corpus we already hold. 24 of the 35 unknown agencies have pages in `text/corpus.db` containing funding language (Bi-State 606 pages, King County
   338, CATS Baton Rouge 295, DCTA 67, Lake County 30, Sunnyvale 14, Trinity 12, Jersey City 9, Grand County 8, San Diego 8, Passaic 2 with a 5310 award,
   Milwaukee 2 with a 5307 table, Suffolk 3 with IMI state funds, Norwalk with 5310/5311). Much of it is boilerplate federal-clause text, so the step is
   one Sonnet batch with a strict brief: for each agency, what pays for the Via contract (general fund or sales tax, federal formula, one-time federal
   grant, state grant), quoting the page. Expected to resolve 15-20 rows.
2. NTD funding-source tables. Every NTD reporter files operating funding by source (local, state, federal, fares). For the 26 NTD-paid agencies, the
   agency's own funding mix is a defensible proxy: hazard = sum of share x hazard by source, one number per agency instead of one blanket 'unknown'.
   Same download route as the contractual tables (headful Playwright click on transit.dot.gov).
3. Budget documents for the rest (11 agencies with no funding page: Hampton Roads, Muskegon, Norman, BJCTA, Rochester, Placer, Gastonia, Addison,
   Omaha, Brighton, Tacoma schools): adopted-budget PDFs name the fund for each contract line. One fetch each.
Until then, the honest presentation is the S1 bracket: hazards on (base) versus off, ~4 points of 2027 services growth.
