# VIA revenue projection model (RPM) and SOTP: build specification

Version 2026-09-21. Companion to `out/growth_model_design.md` (sections 8-12 hold the derivations). Every default below cites its source; change the input,
not the formula. Units $mm unless noted.

## Tab 1: Anchors (actuals, from filings)
| Item | 2023 | 2024 | 2025 | 1H25 | 1H26 | Source |
|---|---|---|---|---|---|---|
| Revenue | 248.9 | 337.6 | 434.3 | 205.8 | 263.1 | 10-K, 10-Q |
| US / Germany / other | 167.6 / 43.8 / 37.5 | 221.0 / 78.5 / 38.1 | 309.7 / 83.5 / 41.1 | 146.3 / 40.5 / 19.0 | 197.7 / 38.7 / 26.7 | 10-K, 10-Q geography note |
| Cost of revenue | | 206.8 | 262.5 | 124.0 | 157.5 | income statement |
| of which tech-enabled services | 117.5 | 167.7 | 223.5 | 105.9 est. | 137.5 | 10-K/10-Q MD&A deltas |
| Launch/support personnel; IT | | | 25.8; 13.3 | | | 10-K |
| Gross margin (GAAP) | 40.1% | 38.8% | 39.6% | 39.7% | 40.2% | arithmetic |
| Opex: R&D / S&M / G&A | | 89.0 / 55.5 / 70.3 | 92.4 / 67.4 / 88.6 | | 50.6 / 41.6 / 58.7 | income statement |
| SBC | | 21.2 | 30.3 | 9.4 | 31.6 | non-GAAP reconciliation |
| Adjusted EBITDA | | (54.4) | (33.4) | | (9.3) | press releases |
| Customers (organic) | | 665 | 821 (727) | | 847 (753) | KPIs |
| RPO | | | 294.4 | | 318.3 (37% due 2027) | notes |
| FY2026 guide | | | | | revenue 550-553; adj. EBITDA (12.5)-(7.5) | 8-K 2026-08-06 |

## Tab 2: Segment split (derived)
Input: services GM (default 26%; cases 22% / 30%). Services revenue_t = tech-enabled services cost_t / (1 - GM). Software = total - services.
Defaults produce services 64% / 67% / 70% / 71% of revenue for 2023 / 2024 / 2025 / 1H26.
Software cost of revenue = IT + 50% of launch/support (default); implied software GM check should land 70%-80%.

## Tab 3: Services engine (US contract layer + plugs)
Rows: one per large documented operations contract from `out/us_revenue_build.csv` layers 1-2 (about 40 rows). Columns: agency, entity, scope, start,
term end, ceiling or NTD payment, haircut (0.80 on ceilings, 1.00 on NTD payments), rate escalator (3%-4%), funding tag (local / federal formula /
federal one-time / state / unknown), competitive hazard (turnkey <1%), funding hazard (by tag, section 11), downsell rate (2%-4% locally funded),
2024A-2028E revenue. Plugs: (a) other US services = services revenue (Tab 2, US share) - contract layer, grown with the layer's organic rate; (b) Downtowner
2026 = $15-35mm (default 25), then +4%; (c) Germany services (default: all of Germany) -9% 2026, -5% 2027, 0% after; (d) other international +30% / +20% / +15%.
New wins: vehicle-equivalents x $140k per vehicle-year (NTD 2024: $42.7mm / 304 vehicles), 6-9 month ramp; default 250 (2026) / 150 (2027) / 100 (2028);
bear 250 / 100 / 60; bull 250 / 220 / 200.

## Tab 4: Software engine
Small SaaS: customers_t = customers_{t-1} x (1 + logo growth 4%-9% - competitive churn 3%-4%); ACV_t = ACV_{t-1} x (1 + 3%-5%). Base = software revenue (Tab 2)
less named accounts. Named accounts: NYC DOE 7.2, RTC Southern Nevada 0.9, Miami-Dade 1.0, others as found; each with a hazard. Germany software (if any)
declines with Muva. Implementation fees = 3% of revenue (10-K), modeled as 30% of new contract value in the launch year.

## Tab 5: Growth bridge and tags
Year-over-year change decomposed into: annualization of prior-year wins; expansion at existing accounts; new wins; Downtowner; international; churn and
downsell. Each contract row carries a macro tag: pandemic federal money / IIJA formula / state program / DART exit / paratransit substitution / operator
outsourcing / German public funding / none. Report growth by tag and the share from one-off or expiring tags.

## Tab 6: Margins and income statement
Blended GM = weighted segment GMs + implementation-fee effect (fees at ~90% GM). GM_services path: 26.0% / 25.5% / 25.0% (2026-28 base); GM_software 75% flat.
Opex growth: R&D 8%-10%, S&M 15%-20%, G&A 12%-15% (1H26 run-rates); SBC 11%-12% of revenue. Interest income 3% on cash. Outputs: GAAP operating loss, net loss,
adjusted EBITDA (add back SBC, D&A, transaction and litigation costs), free cash flow (operating cash flow less ~$5mm capex; working capital: receivables at
~70 days of services revenue).

## Tab 7: SOTP
Services gross profit x multiple (default 2.2x, Lyft 2027E; sensitivity 1.5x-4.0x). Software gross profit x multiple (default 10x; sensitivity 6x-15x). Plus
cash 336. Divide by 81.3mm shares. Also show the market-implied software multiple at the current price. Scenario grid: 2027 growth (16% / 20% / 26%) x
services GM (22% / 26% / 30%) x software multiple.

## Tab 8: Checks
1. Tab 2 + Tab 3 + Tab 4 = reported revenue for 2023-2025 and 1H26 (tolerance 0). 2. 2026E within guide 550-553. 3. NTD 2024 payments per agency within
+/-25% of the contract-layer 2024 value. 4. RPO 2027 ($118mm) <= 2027E services revenue. 5. Blended GM 2026E within 40%-41%. 6. Adjusted EBITDA 2026E within
guide (12.5)-(7.5). 7. Organic ex-Downtowner 2026 growth in 19%-24%.

## Known gaps to state in the pitch
Downtowner revenue (undisclosed), Germany's segment (assumed services), the undocumented US residual (~$80mm in 2025, split by scenario), the services GM
assumption (bounded 20%-32%), and federal formula continuation after 2026-09-30 (no history).
