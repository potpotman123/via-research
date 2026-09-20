# Findings: Via Transportation (VIA) contract census vs. the Bleecker Street short thesis

Prepared 2026-09-20 for Kendall Wu. Price context: $27.98 (2026-09-18); Bleecker target $11.80.
Deliverables: `out/via_contract_census.csv` and `.xlsx` (census plus supporting tables), `out/claims_verification.md` (23 claims),
`out/post_bleecker_analysis.md` (contract flow since 2025-12-16), `out/analysis_summary.md` (regenerable tables), `docs/ntd_turnkey_summary.md`.

## What was built
- 327 Via contract actions across 169 US public-sector agencies in 38 states, from 661 primary documents (Legistar attachments from 306 agenda
  systems, Bleecker's 109-folder contract sample, council minutes and staff reports fetched for 37 gap agencies) plus FTA NTD contractor tables
  RY2019-RY2024, NTD monthly service data through July 2026, FMCSA registrations, the OMNIA cooperative price schedule, Via's SEC filings, 544 Via
  press releases and 229 news headlines. Separately: 28 competitor awards (Spare Labs, RideCo, Uber) at Via agencies and 62 app-only observations
  for agencies where a Via-branded rider app exists but no procurement document was found.
- Every row cites the document it came from. 108 rows are high confidence, 165 medium, 54 low (news-only). Bleecker's ~100-contract sample is
  a subset of this base; the census covers about three times as many contract actions.

## What the documents say about the thesis

**1. Via's revenue base is a labor contract base.** On a run-rate basis (latest priced action per agency), documented annual contract value is
78% Turnkey, 14% Hybrid, 2% Software-only and 7% Unknown; 84/15/2 excluding Unknowns. By count of actions it is 152 Turnkey, 9 Hybrid, 113
Software-only, 53 Unknown. The dollar view is a floor for software, because small subscriptions rarely carry a public price, but even the largest
documented software contracts are small: median software fee $43,260 a year, largest $927,000 (RTC Southern Nevada). The turnkey contracts are
priced per vehicle or driver hour at $35.83 to $147.32, median about $62, all-inclusive of drivers, vehicles and software. Bleecker's 72%
services figure is consistent with this and with the 10-K's tech-enabled-services cost of 51% of revenue.

**2. The pricing schedule proves the arithmetic.** Via's own OMNIA cooperative price list (contract R250802, effective 2025-08-01) prices microtransit
software at a few hundred dollars per vehicle per month and turnkey operations at $50.47 to $80.75 per vehicle hour. For a 10-vehicle fleet running
12 hours a day, software is 1.4% to 2.3% of first-year cost and the $27,758.50 installation fee is 54% of first-year software fees; Bleecker's
31%-153% implementation range is exactly this schedule from 20 vehicles down to 1. Claims 2 through 5 are reproduced, not merely supported.

**3. Growth is real, and it is turnkey.** NTD purchased-transportation payments to Via entities by full-reporting agencies rose from $9.4mm
(RY2020) to $42.7mm (RY2024), before LA Metro's operations contract ($135.0mm over the base and options, awarded 2024-10) enters the data.
Since 2024 Via has become the operator of entire transit systems: Sioux Falls ($11.2mm RY2024), Mobile ($12.1mm a year from 2025-09), TCATA
(2025-12), Rochester MN ($77.8mm over five years, 2026-07). Of 20 contract actions dated after the Bleecker report, 12 are Turnkey and 1 Hybrid;
the documented software-only new business has no stated price. NTD monthly revenue hours at most Via turnkey agencies were still rising in the
first seven months of 2026. The "organic decline" leg of the thesis is not visible in contracts; the contract flow is strongly positive.

**4. Via is losing the software contest while winning the operations contest.** Every documented competitor award since 2024 is a software
contract: Spare at Met Council, Baldwin County, LA Metro, AC Transit/BART; RideCo at Ben Franklin Transit, El Paso, Huntsville. In two of those,
LA Metro and Ben Franklin Transit, Via kept the driving. Turnkey losses (SacRT SmaRT Ride, SARTA Connect, Palo Alto's reduction, Milwaukee's cut)
were budget decisions, not competitive ones.

**5. Downsells exist that GRR would not count.** Palo Alto's ceiling fell from $3,244,000 to a $1,100,000 one-year continuation; Milwaukee's pilot
was cut to a $750,000 limited version; SacRT replaced an $8.4mm-a-year service with a smaller one; Arlington's ceiling fell from $30.2mm to
$20.8mm. Bleecker's reading of the GRR definition is confirmed by the 10-K text, and the census shows the behavior it hides.

**6. Two Bleecker specifics are not verifiable from documents.** Spare's "one cent" bid at LA Metro is not in any document found; the only Spare
price schedule in Bleecker's sample turned out to be Baldwin County's, misfiled in the LA Metro folder. Springfield's 34% upfront figure is also
absent. The insurance, gross-margin, GRR/NRR and organic-growth claims are internal-accounting matters that contracts cannot test.

**7. Insiders bought after the fall.** All seven 2026 Form 4s are acquisitions, including open-market purchases by the CEO, the CFO and two
directors in June and August 2026. No Form 4 sale appears. Lock-up venture holders were not checked.

## Implications for the long/short decision
The census settles the business-model question in Bleecker's favor: what Via sells to US public agencies is overwhelmingly hourly operations,
and the software attached to it is priced like an add-on. That argues for gross-profit-multiple framing rather than ARR framing, and it caps the
margin story: the OMNIA schedule leaves little room for a software-like margin on the dollars that matter.

The census does not support the "road to nowhere" leg. The company is winning large, multi-year operations contracts at a faster pace after the
report than before it, several of them displacing legacy operators (Transdev in Rochester) or filling gaps left by transit-agency exits (Plano,
Addison, Highland Park, Grand Prairie). Those contracts will show up as revenue growth through 2027, at services margins, funded mostly from local
budgets rather than expiring federal programs. A short premised on multiple compression has documentary support; a short premised on shrinking
revenue does not.

## Limits
- Coverage: 62 agencies with a Via-branded app have no located procurement document; 17 gap agencies rest on news only; 53 actions are Unknown
  scope. NTD covers full-reporting agencies only and lags a year; LA Metro's operations contract is not yet in NTD.
- Dollar mix understates software because most subscriptions fall below public approval thresholds. The count mix is the fairer view of the customer
  base by number; the dollar mix is the fairer view of revenue.
- Ceilings are treated as annual values when a document states them per year; actual spend is usually lower.
- Downtowner rows dated before 2025-12-12 (Denver, Placer/TART, Salisbury, Lake County) are flagged and excluded from the organic view.
- All classifications rest on document language about who supplies drivers and vehicles and how Via is billed; 31 Tier-3 corrections are logged
  with reasons in `shards/_corrections.csv`, and two rows (Erie, CO) were excluded as a different company, Via Mobility Services.

## Files
| Path | Contents |
|---|---|
| out/via_contract_census.csv / .xlsx | The census (327 Via actions, 28 competitor awards, 62 app-only), plus NTD, OMNIA, SAFER, targets, QA flags and corrections sheets |
| out/claims_verification.md | 23 Bleecker claims with verdicts and evidence |
| out/post_bleecker_analysis.md | Post-report wins, losses, ACV candidates, NTD trajectory, funding, insider filings |
| out/analysis_summary.md | Regenerable tables (`python scripts/p5_analysis.py`) |
| docs/ntd_turnkey_summary.md | NTD payments to Via entities by agency and year |
| text/enum/omnia_price_schedule.csv | Via's OMNIA R250802 price list, 126 lines |
| text/enum/targets.csv | 246 US public-sector customers with sources |
| docs/*.md, scripts/*.py | Method, briefs, pipeline (rerunnable end to end from raw/) |
