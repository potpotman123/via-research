# Organic growth position and SOTP model design for VIA

Prepared 2026-09-21. Sources: FY2025 10-K (`raw/cache/exhibit/10k_fy2025.txt`), 8-K earnings releases 3Q25-2Q26, contract census, NTD.
Figures in $mm unless noted. Anything marked "est." is my arithmetic on stated inputs with the assumption shown.

## 1. What the filings say about where growth comes from

| | 2023 | 2024 | 2025 | 2026E (guide) |
|---|---|---|---|---|
| Total revenue | 248.9 | 337.6 | 434.3 | 550.0-553.0 |
| Growth | | +35.7% | +28.6% | +26.6% to +27.3% (3Q26 guide +25.5% to +26.0%) |
| United States | 167.6 | 221.0 (+32%) | 309.7 (+40%) | |
| Germany | 43.8 | 78.5 (+79%) | 83.5 (+6%) | |
| All other countries | 37.5 | 38.1 (+2%) | 41.1 (+8%) | |
| Government customers | 222.3 | 311.0 | 406.4 (+31%) | |
| Commercial customers | 26.6 | 26.6 | 27.9 (+5%) | |
| Customers, year-end | | 665 | 821 (incl. 94 Downtowner; 727 organic, +9%) | 847 at 6/30/26 (753 organic, +3.6% in 1H) |
| Revenue per customer (est.) | | | 0.53 | ARR/customer 0.64 at 6/30/26 |
| RPO | | | 294.4 at 12/31/25 (60% recognized in 2026, 27% in 2027) | 318.3 at 6/30/26 |
| NRR / GRR | | >120% / >95% | 119% / 98% (4Q) | |

Reading:
- Growth is a US, government story. US added $88.7mm of the $96.7mm 2025 increase. Germany grew 79% in 2024 on a large deployment and then 6%; that is
  the template for how a big operations contract ramps and plateaus.
- Logo growth is single digit. Organic customers grew 9% in 2025 and about 4% in the first half of 2026. Revenue growth of 27% therefore comes from
  larger contracts per customer (NRR 119%), which in the census means more vehicle hours and whole-system operations awards.
- RPO covers about a third of a year. $294mm of RPO against $551mm of guided revenue, with 60% due in 2026, means most revenue is billed for hours
  delivered under contracts with no committed minimum. The word "subscription" in the filings (97% of revenue) describes recurring hourly billing.
- Downtowner is undisclosed. The 10-K says its post-acquisition revenue was "not material" for the 19 days it was owned and presents no pro forma.
  Its annual revenue must be estimated: known contracts (Denver Connector $5.99mm/yr, Placer TART $3.5mm NTD 2024, Salisbury $2.9mm NTE, Lake County
  $1.4mm) plus Truckee (30 vehicles, 108 drivers per FMCSA), Aspen, Park City, Jackson, Big Sky and others suggest $25mm-$45mm (est.). At $30mm it is
  about 5.5 points of 2026 growth, leaving organic growth near 21%.

## 2. The growth algebra for 2027

Revenue growth = NRR expansion on the existing book, plus new logos, plus acquisitions, minus churn. Management's 27% for 2026 decomposes roughly as
(est.): Downtowner ~5-6 pts; annualization of 2025 wins (LA Metro operations from 3/2025 about $27mm a year, Mobile $12.1mm from 9/2025, DCTA
$11.9mm, New Braunfels, HRT) ~6-8 pts; NRR-type expansion at existing turnkey accounts (UTA service orders, Douglas County, HRT zones, Community
Transit) ~6-8 pts; 2026 new wins in-year (Plano from 3/2026, Sunnyvale, Addison, Douglas 2026 PCS, Grand Prairie) ~4-6 pts; international ~1 pt.

For 2027 to grow 27% again, revenue must rise about $150mm. Sources visible in documents:

| Source | 2027 contribution (est.) | Basis |
|---|---|---|
| Annualization of 2026 wins | 30-40 | Rochester $15.6mm/yr from 9/2026 (+$10mm incremental), Plano full year, Grand Prairie $17.5mm award, Sunnyvale, Grand County, Addison |
| Expansion at existing accounts | 40-60 | 8-11% of the ~$550mm base; NTD hours at Via agencies +1% to +21% YTD 2026, two declining |
| New US logos signed in 2027 | 30-60 | documented 2026 pace of new annualized turnkey value is $50-60mm; assume it fades once the DART-exit wave and federal pilot money pass |
| International | 0-10 | Germany +6%, other +8% in 2025 |
| Downtowner | 0 | lapped by 12/2026 |
| Churn and downsells | (10)-(30) | Jersey City ($7.7mm at risk), DCTA renewal, Arlington renewal, Montgomery County zones, Sioux Falls labor, grant-funded pilots ending |
| **Total** | **90-140** | **16%-25% growth** |

The clean statement is not "growth stops." It is that 27% requires every 2026 tailwind to repeat in 2027, and three of them (Downtowner, the DART-exit
cluster, the LA Metro/Mobile step-ups) are one-time. A base case of high-teens organic growth in 2027 against a market extrapolating mid-20s is the
short's top-line leg. Note the guide already decelerates: 36% (2024), 29% (2025), 27% (2026), 25.5%-26% (3Q26).

## 3. Top-down TAM: use it to size the ceiling, not the forecast

- Software TAM is small relative to Via. About 2,200 NTD-reporting agencies plus municipalities and campuses; census ACVs run $11k to $927k with a
  $43k median and Remix minimums of $19k-$29k. Even 1,500 US public software customers at $75k is about $110mm a year, less than Via's 2025 US
  growth alone. Software cannot carry 27% growth on a $550mm base.
- Operations TAM is large and low-margin. It is the purchased-transportation line of US transit budgets (demand response, paratransit, and contracted
  fixed route), competed against Transdev, MV, Keolis, RATP Dev and agencies' own workforces. Via's documented US operations run-rate is roughly $160mm
  against a market measured in billions, so share gain can fund growth for years, at services margins. Pull the exact denominator from the NTD Annual
  Database "Operating Expenses" table (TOS = PT, modes DR, DT, MB) with the same headful-browser download used for the contractor table; that gives
  national purchased-transportation spend by mode for RY2019-RY2024 and Via's share by year.
- The TAM therefore supports a mix conclusion rather than a growth conclusion: sustained high growth is only available in the operations market, so the
  faster Via grows, the more its gross margin converges toward the operations margin. That links the top-line leg to the margin leg.

## 4. SOTP model specification

Two operating segments defined by cost structure, not by customer label, because the filings only give a cost split.

**Segment A: Operations (driver management, fleet management, customer support).**
- Revenue build: (a) documented US book by contract from `out/via_contract_census.csv` run-rate view, each with start, term, escalator (3%-4% per
  year on hourly rates; the census shows UTA rates moving $55.23 to $68.33 over 2022-2024), renewal probability at expiry (use the calendar in
  `out/short_case_clock.md`), and volume growth from NTD hours; (b) Downtowner at $25mm-$45mm; (c) international operations plug (Germany $83.5mm
  is mostly one large deployment); (d) undocumented US operations plug so that A + B reconciles to reported revenue; (e) new-win layer: $X of annualized
  value signed per year, ramping over 6-9 months, with X = 50-60 in 2026 fading to 30-40 by 2028 in the base case.
- Cost of revenue: driver hours x loaded driver cost, vehicles, insurance (self-insured retention; insurance payables $15.3mm), support. Simpler:
  gross margin 24%-28% with 26% as base (Bleecker) and a check that 2025 segment revenue x (1 - GM) = $223.5mm of tech-enabled-services cost.
- Reconciliation: at 26% GM, 2025 services revenue = 223.5 / 0.74 = $302mm (70% of total); Segment B = $132mm.

**Segment B: Platform (software subscriptions, Remix, Citymapper, software-only microtransit and paratransit).**
- Revenue build: customers x ACV. Organic logo growth 4%-9% (filings); ACV growth via upsell 5%-10%; churn to Spare and RideCo (documented at Met
  Council, Baldwin, LA Metro, BFT, El Paso, Hillsborough) 2%-5% of base per year; implementation fees at ~3% of revenue recognized in year one.
- Cost of revenue: IT and hosting ($13.3mm in 2025) plus a share of launch/support personnel ($25.8mm); gross margin 70%-80%.

**Below gross profit (consolidated, then allocated for the SOTP).** 2025 opex: R&D $92.4mm, S&M $67.4mm, G&A $88.6mm; SBC $30.3mm in 2025 and
$31.6mm in 1H26 alone (about 12% of revenue post-IPO). Allocate R&D mostly to B, S&M by revenue, G&A by revenue with insurance and incident costs
in A. Interest income about $11mm a year on $336mm of cash.

**Valuation.** A at a transit-operator multiple (5x-7x EBITDA, or Lyft's 2.2x gross profit as Bleecker does); B at a software multiple (6x-10x gross
profit); plus cash. Present the market-implied software multiple at today's price as the headline: at $1.94bn EV and Lyft's multiple on the services
book, the software slice is carrying about $1.7bn, roughly 15x its gross profit.

**Scenarios.** Bear: 2027 growth 16%, GM 39%, SBC 11%. Base: 20%, 40%, 11%. Bull: 26%, 42%, 10%. Show 2027E revenue, gross profit, adjusted and
GAAP EBITDA, and the implied price under each SOTP.

## 5. Data still to fill
1. Downtowner annual revenue: not in the 10-K; check the FY2026 10-Q acquisition note or ask IR; otherwise carry the $25mm-$45mm range.
2. NTD national purchased-transportation spend by mode (Operating Expenses table), for the TAM denominator and Via's share trend.
3. Germany contract structure (who supplies drivers in the BVG deployment), to place $83.5mm in A or B.
4. Quarterly customer counts and NRR/GRR from each 10-Q, to model expansion and churn by quarter.
5. LA Metro RY2025 NTD payments (publish ~October 2026), to anchor the largest operations contract.
6. Street 2027 revenue and margin expectations, to define what "the market extrapolates" means numerically.

## 6. Addendum (2026-09-21): geography by quarter, Berlin, NYC DOE, and the bottom-up US build

Quarterly geographic revenue (10-Qs, $ thousands):

| | 1Q25 | 1Q26 | 2Q25 | 2Q26 | 1H25 | 1H26 |
|---|---|---|---|---|---|---|
| United States | 69,520 | 94,343 (+36%) | 76,759 | 103,347 (+35%) | 146,279 | 197,690 (+35%) |
| Germany | 19,805 | 20,464 (+3%) | 20,737 | 18,280 (-12%) | 40,542 | 38,744 (-4%) |
| All other | 9,317 | 12,627 (+36%) | 9,637 | 14,080 (+46%) | 18,954 | 26,707 (+41%) |
| Total | 98,642 | 127,434 | 107,133 | 135,707 | 205,775 | 263,141 |

Germany turned negative in 2Q26. BVG's Muva on-demand service in Berlin, operated under a contract with ViaVan worth about EUR 10 million, ceased
operations on 2026-02-28 and was replaced by a taxi-based Senate service (VBB-BAV) from 2026-01-01; BVG's chief called Muva "a business disaster" at
about 160 riders a day (taxi-times.com; BVG; VBB press release). The $2.5mm year-over-year decline in 2Q26 German revenue is consistent with that
contract's size. The 10-K does not name Berlin; it refers to "several contracts in Germany." Recurring subscription fees fell to 95% of revenue in 2Q26
(98% a year earlier) as implementation fees from new launches rose.

RPO: $275.5mm (3/31/26), $318.3mm (6/30/26); 45% due in the rest of 2026 and 37% ($118mm) in 2027, about 17% of a 2027 revenue base grown 27%.

NYC Department of Education: five-year $36mm routing/tracking contract announced summer 2019; cumulative awards $51.7mm; Software-only (Chalkbeat
2026-05-18; NYC Comptroller). Added to the census as a manual row; it is the largest US software account found.

### Bottom-up US build (`scripts/p7_us_build.py` -> `out/us_revenue_build.csv`)
Stratified by evidence quality, with each layer's assumption written into the row:
1. NTD-paid operators: actual RY2024 payments ($42.7mm, 15 agencies), grown 10% for 2025 and 8% for 2026 (NTD hours), 4% escalator after.
2. Census-priced operations not in NTD: ceiling x 0.80 (NTD payments ran 0.75-0.93 of documented ceilings for Arlington, BFT, Grand Prairie),
   prorated by start date; concurrent same-day awards summed (LA Metro North + South = $22.5mm x 0.8).
3. Documented operators with no stated price: $1.5mm each (small operators in NTD run $0.6mm-$1.1mm).
4. App-only agencies: 30% probability of a $0.8mm operations contract, 70% of a $60k subscription.
5. Documented software: stated fee, else $60k.
6. Remix cities not enumerated: 250 x $30k.
7. Downtowner: $25mm-$45mm, midpoint.

Result vs the 10-K anchors: the build explains $202mm of $221mm US revenue in 2024 (91%) and $224mm of $310mm in 2025 (72%); it projects $286mm for
2026 against roughly $420mm implied by guidance if international is flat, and $303mm for 2027 before new wins. The residual ($86mm in 2025, growing)
is the undocumented US book: large software accounts like NYC DOE ($7.2mm a year) and King County, commercial customers (~$28mm globally), imputed
layers set conservatively, and agencies outside Legistar, NTD and the app store. The model should carry that residual explicitly and split it by
scenario, because the split is exactly the services-versus-software question: if Germany is mostly operations, US services revenue implied by the
$223.5mm services cost is about $200mm, close to the build's $190mm for 2025, and the residual is software; if Germany is software, the residual is
undocumented operations.
