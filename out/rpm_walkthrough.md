# VIA revenue projection model: end-to-end walkthrough (2026-09-21)

Companion to `out/rpm_spec.md` (tab-by-tab spec) and `out/growth_model_design.md` (derivations, sections 1-12). This document traces the build from
the question to the verified output.

## 1. The question and the outputs
Question: can Via sustain the ~27% growth in its 2026 guide and lift gross margin from ~40% toward its 50% target? The short says no to both.
Outputs the model must produce: revenue 2023A-2028E by geography (US, Germany, other) and by segment (services, software); a growth bridge that
separates annualization of signed contracts, new wins, expansion, churn/downsell, Downtowner and international; blended and segment gross margin; GAAP
operating loss and adjusted EBITDA; a SOTP with a scenario grid.

## 2. Architecture and why
Eight layers, each fed by the one above:
A. Anchors: reported actuals (10-K, 10-Qs, 8-Ks).
B. Segment split: services revenue = technology-enabled services cost / (1 - services GM); software = residual.
C. Services engine: contract layer (52 priced + 29 unpriced documented US operations contracts) + plugs (other US, Germany, other international,
   Downtowner) + new wins in vehicle-equivalents + factorized hazards (competitive x funding) + downsell.
D. Software engine: residual grown by logo growth (customer count) + price/upsell - competitive churn; named accounts carried separately.
E. Growth bridge with macro and acquisition tags.
F. Margin and income statement: share-weighted segment margins + implementation-fee effect; opex; SBC.
G. SOTP and scenarios.
H. Checks and backtests.

Why this shape and not the alternatives considered in the design doc:
- Census count scaling (rejected): the census is size-biased toward public, large, turnkey actions; scaling 329 actions to 847 customers would
  extrapolate that bias. The filings give the denominators, so the census is used for composition, calendar, rates and hazards only.
- Whole-book vehicle P x Q (rejected as driver, kept for new-win sizing): no fleet count exists; NTD covers 632 vehicles at 26 agencies (RY2024, corrected 2026-09-21).
- Top-down TAM (kept as ceiling only): says how big the market could be, not what Via wins next year.
- Filings-anchored split (chosen): one assumption (services GM) bounded by an identity; every other input is disclosed or dated.

## 3. Numbers and where each comes from
| Layer | Input | Value | Source |
|---|---|---|---|
| A | Revenue 2023/2024/2025 | 248.9 / 337.6 / 434.3 | 10-K FY2025 statement of operations |
| A | Revenue 1H25 / 1H26 | 205.8 / 263.1 | 10-Q 2Q26 |
| A | US / Germany / other, 2025 | 309.7 / 83.5 / 41.1 | 10-K note, revenue by geographic area (p.101); 2024 = 221.0 / 78.5 / 38.1; 2023 = 167.6 / 43.8 / 37.5 |
| A | US / Germany / other, 1H26 | 197.7 / 38.7 / 26.7 | 10-Q 2Q26 geography note |
| A | Cost of revenue 2024 / 2025 | 206.8 / 262.5 | income statement |
| A | Tech-enabled services cost 2025 | 223.5 (plus launch/support 25.8, IT 13.3) | 10-K MD&A cost-of-revenue paragraph |
| A | Same, 2024 / 2023 | 167.7 / 117.5 | backed out of MD&A change sentences (+55.8; +50.2) |
| A | Same, 1H26 | 137.5 (est.) | 10-Q deltas +18.0 (1Q) and +13.6 (2Q) on a pro-rated 1H25 level of 105.9; label as estimate |
| A | Opex 2025 R&D / S&M / G&A | 92.4 / 67.4 / 88.6; 1H26 50.6 / 41.6 / 58.7 | income statements |
| A | SBC 2024 / 2025 / 1H26 | 21.2 / 30.3 / 31.6 | 8-K non-GAAP reconciliations |
| A | Adjusted EBITDA 2024 / 2025 / 1H26 | (54.4) / (33.4) / (9.3) | 8-K press releases |
| A | 2026 guidance | revenue 550-553; adj. EBITDA (12.5)-(7.5) | 8-K 2026-08-06 |
| A | Customers | 665 (Dec-24), 689 (Jun-25), 821 (Dec-25, incl. 94 Downtowner), 847 (Jun-26) | 10-K, 10-Q KPI tables; definition: distinct legal entities generating Platform revenue in the quarter |
| A | RPO | 294.4 at Dec-25 (60% in 2026, 27% in 2027); 318.3 at Jun-26 (37% due 2027) | 10-K RPO note; 10-Q |
| A | Cash, shares, price | 336; 81.3-81.5mm; $27.98 (2026-09-18) | 10-Q balance sheet; cover page; market |
| B | Services GM | 26% base; 22% / 30% cases; identity band 20%-32% | design doc section 9 (cost-of-revenue identity with software GM 70%-80%) |
| B | Services revenue at 26% | 158.8 / 226.6 / 302.0 (2023-25); 185.8 1H26 | arithmetic on A |
| B | Software residual at 26% | 90.1 / 111.0 / 132.3; 77.3 1H26 | arithmetic on A |
| C | NTD payments to Via entities | 96.8 (RY2024) across 26 agencies; 2.0 / 9.7 / 17.6 / 37.2 / 58.6 for RY2019-23 (agency fiscal years; corrected 2026-09-21 after widening the seller-name match) | FTA NTD contractual relationship tables, `docs/ntd_turnkey_summary.md` |
| C | Census-priced operations | 37 contracts, 88.4 in 2025 after haircut | `out/via_contract_census.csv`, `out/us_revenue_build.csv` layer 2 |
| C | Ceiling-to-spend haircut | 0.80 (Arlington 0.75, BFT 0.80, Grand Prairie 0.93) | census ceilings vs NTD payments at overlap agencies |
| C | Unpriced documented operations | 29 contracts, 43.5 imputed | build layer 3 |
| C | Rate per vehicle hour | $52-$70 microtransit; median ~$60; OMNIA list $50.47-$80.75 | census hourly_rate_usd; `text/enum/omnia_price_schedule.csv` |
| C | Revenue per contracted vehicle-year | ~$153k | NTD RY2024 $96.8mm / 632 vehicles |
| C | Hours per vehicle-year | 2,755 (Arlington) to ~4,400 (HRT) | NTD monthly module |
| C | Escalator | 3%-4% a year (UTA account ran ~10%) | census rate history |
| C | 2026 signed wins | Rochester $15.6mm/yr from Sep-26; Mobile $12.1mm/yr; Plano ~$8mm; Sunnyvale $8.358mm total; Douglas +$1.5mm; Addison; Grand Prairie; Grand County | `out/post_bleecker_analysis.md` |
| C | New-win volume | 250 / 150 / 100 vehicle-equivalents 2026-28 base | judgment anchored on 2026 signings (+200 to +300) |
| C | Competitive hazard | software 3%-4%/yr (6 displacements since 2024); turnkey: no competitive loss found in NTD RY2019-24 (the apparent HRT 2021 drop was a seller-name change in the table); exits are budget decisions | competitor-award rows; loss list; NTD |
| C | Funding hazard | local ~2%/yr + downsell 2%-4%; federal formula 5%-15% level-cut judgment; one-time federal 40%-50% at expiry; state grant 25%-35% at expiry | design doc sections 10-11 |
| C | Funding exposure | local ~45%, grant-linked ~30%, unknown ~20% of documented dollars | census funding_source |
| C | Germany | 83.5 in 2025; -9% 2026 (Muva ~EUR10mm ended 2026-02-28; 2Q26 -12%); -5% 2027; flat after | 10-Q; BVG/press |
| C | Other international | 41.1 in 2025; +30% / +20% / +15% | 10-Q (1H26 +41% off small base) |
| C | Downtowner | $15-35mm 2026 (base 25); undisclosed; 10-K says pro forma not material | 10-K acquisition note |
| D | Logo growth | ~9% organic (753 vs 689) | KPI table |
| D | Software growth history | +23% / +19% / +23% (2024 / 2025 / 1H26) | residual arithmetic |
| D | Named accounts | NYC DOE 7.2/yr ($36mm/5yr); Miami-Dade 0.32; El Paso 0.25; MTA Maryland 0.22 | census |
| D | Documented ACV | median $43k; OMNIA $303-$1,514 per vehicle-month; Remix minimums $19k-$29k | census; OMNIA |
| D | Implementation fees | ~3% of revenue (5% in 2Q26 vs 2%) | 10-K; 10-Q 2Q26 |
| F | Software GM | 75% flat (70%-80%) | identity in section 9 |
| F | Services GM path | 26.0% / 25.5% / 25.0% (2026-28) | judgment: wage inflation vs 3%-4% escalators |
| G | Multiples | services GP 2.2x (Lyft 2027E; 1.5x-4.0x); software GP 10x (6x-15x) | Bleecker; comps |

## 4. Build sequence
1. Anchors tab from filings; every cell cites filing and page.
2. Split tab: services GM input; services and software revenue for 2023-25 and 1H26; check implied software GM lands 70%-80%.
3. Services engine: contract rows (agency, entity, scope, labor-only tag, start, term end, ceiling or NTD payment, haircut, escalator, funding tag,
   hazards, downsell) rolled 2024A-2028E; plugs sized by subtraction from the split for 2024-25 and grown at the documented layer's organic rate;
   new wins; Downtowner; Germany; other international.
4. Software engine: residual 2025 base; logo growth x ACV growth - churn; named accounts with hazards; Germany software if any.
5. Bridge: year-over-year change by driver and by macro tag (pandemic federal money, IIJA formula, state program, DART exit, paratransit
   substitution, operator outsourcing, German public funding, none).
6. Margin and income statement: blended GM from shares; implementation-fee effect; opex growth; SBC; adjusted EBITDA; FCF with receivables at
   ~70 days of services revenue.
7. SOTP: segment gross profit x multiple + cash, per share; market-implied software multiple at the current price; scenario grid.
8. Checks tab (section 5 below) with pass/fail flags.

## 5. Backtests and verification
The split ties to reported totals by construction, so the tests are on the engines, on out-of-sample periods, and on implications.

1. Walk-forward 2024 to 2025 (the primary backtest). Freeze the contract layer at 2024 (NTD RY2024 payments, census contracts signed by
   2024-12-31), roll to 2025 with escalators, annualization of 2024 signings, 2025 signings with actual start months, and realized losses (SARTA
   2024-11, Palo Alto reduction). Compare the layer's growth to the filings-derived services growth of +33%. Preliminary result from the current build:
   the priced layer grew 17% and the documented layer 13% on the pre-correction build; on the corrected build (2026-09-21) the NTD layer is 96.8 to 109.7 (+13%, an assumed hours growth) and layers 1-3 sum to 158.9 (2024, with mid-year starts prorated) to 207.0 (2025), +30%, against +33% for services and +6% for Germany. Layer-1 2025 values are still NTD x assumed growth until RY2025 publishes. The gap must
   be explained before the 2026-28 engine is trusted. Candidate explanations to test in order: (a) layer 1 uses NTD RY2024 x escalator for 2025 and so
   misses volume expansions at NTD agencies (fix: use NTD monthly revenue hours through July 2026 to update 2025-26 volumes per agency); (b) partial-year
   timing of Mobile (Sep-25) and DCTA (Sep-25) understates their 2025 run-rate contribution relative to the filings' quarterly recognition; (c) the
   undocumented tail (private, enterprise, small agencies, other international) grew faster than the documented book; (d) services GM rose, which would
   lower the true services growth. Each has a different implication for 2027, so record which one the data supports.
2. NTD per-agency test. Contract-layer 2024 value vs NTD RY2024 payment at the 15 overlap agencies; tolerance +/-25%; this is how the 0.80 haircut was
   set. Rerun on RY2025 when FTA publishes it (expected October 2026).
3. Guidance test. 2026E must land inside 550-553 without a plug; 1H26 actual 263.1 implies 2H26 of 287-290, so the engine's 2H26 must show that
   sequential step from Mobile, Rochester (Sep), Plano, Downtowner and the 3Q seasonal pattern.
4. RPO test. 2027 contracted revenue in RPO (~$118mm at Jun-26) must be <= 2027E services revenue; RPO growth (294.4 to 318.3) vs services growth.
5. Customer-count test. Modeled logo adds vs the disclosed quarterly count; organic growth ~9%.
6. Margin test, out of sample. Predict 1Q26 GM (reported 39%) and 2Q26 GM (reported 41%) from the modeled mix and the disclosed implementation-fee
   share (5% vs 2%); the model should reproduce the dip and the recovery without a margin plug.
7. Hazard backtest. Apply the section 11 survival cells to the 2021-2023 cohort of census contracts and compare to realized outcomes by 2025 (HRT,
   SacRT, SARTA, Palo Alto, Milwaukee, Jersey City budget, Montgomery zones, Beverly Hills rejection, Sioux Falls labor issues, six software
   displacements). If realized loss is outside the modeled band, recalibrate the cells, not the outputs.
8. Quarterly out-of-sample going forward. Each 10-Q gives four fresh checks: revenue by geography, services-cost delta, customer count, RPO. 3Q26
   (due November 2026) is the first true out-of-sample quarter for this model.
9. Implication checks. Implied average software ACV (residual / implied software customers) vs documented $43k median; implied contracted
   vehicle-years (US services / $140k) vs NTD 304 plus census fleet sizes; services GM vs transit-operator peers (15%-25%); software GM 70%-80%.
10. Scenario discipline. Bear/base/bull differ only in named inputs (2027 new-win volume, funding hazards, services GM, multiples); no scenario may
    change a disclosed anchor.

## 6. Gaps carried explicitly
Downtowner revenue (undisclosed); Germany's segment (assumed services); the undocumented US residual (~$80mm of 2025 US revenue); the software
customer count (derived, not disclosed); services GM (assumption, bounded); federal formula continuation after 2026-09-30 (no history); the
2024-to-2025 walk-forward gap in section 5.1 until resolved.
