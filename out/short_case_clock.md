# The short case after the report: what has to change, and when it shows up

Prepared 2026-09-20. Sources: Via 8-K earnings releases (4Q25 filed 2026-02-27, 1Q26 filed 2026-05-12, 2Q26 filed 2026-08-06; cached in
`raw/cache/exhibit/`), FY2025 10-K, EDGAR filing index, and the contract census (`out/via_contract_census.csv`). All dollars in thousands unless
marked $mm. Arithmetic on reported figures is labelled.

## 1. Gross margin has not moved in ten quarters

| Period | Revenue | Cost of revenue | Gross profit | GAAP GM (arith.) | Adjusted GM (reported) |
|---|---|---|---|---|---|
| FY2024 | 337,630 | 206,790 | 130,840 | 38.8% | 40% |
| 4Q24 | 91,684 | 54,705 | 36,979 | 40.3% | 41% |
| 1Q25 | 98,642 | 58,832 | 39,810 | 40.4% | 41% |
| 2Q25 | 107,133 | 65,182 | 41,951 | 39.2% | 40% |
| 4Q25 | 118,909 | 71,956 | 46,953 | 39.5% | 40% |
| FY2025 | 434,337 | 262,537 | 171,800 | 39.6% | 40% |
| 1Q26 | 127,434 | 77,379 | 50,055 | 39.3% | 40% |
| 2Q26 | 135,707 | 80,101 | 55,606 | 41.0% | 41% |

Revenue is up 27% year over year; gross margin is where it was in 2024. The long-term target is about 50%. The census says why the gap is not
closing: every large 2026 award is an operations contract priced per vehicle hour, and the newest ones (Rochester $77.8mm over five years, Mobile
$12.1mm a year, Plano about $8mm a year) have not started billing yet. Watch: 3Q26 print in November, and 2027 as Rochester and Mobile ramp.

## 2. "Profitability" is adjusted; GAAP losses are widening

| Period | Operating loss (GAAP) | Net loss | Adjusted EBITDA | Stock-based compensation | SBC as % of revenue (arith.) |
|---|---|---|---|---|---|
| FY2024 | (83,896) | (90,552) | (54,392) | 21,226 | 6.3% |
| FY2025 | (76,616) | (96,361) | (33,394) | 30,341 | 7.0% |
| 2Q25 | (16,110) | (21,221) | (9,055) | 4,662 | 4.4% |
| 1Q26 | (23,584) | (20,149) | (5,809) | 15,564 | 12.2% |
| 2Q26 | (21,754) | (19,556) | (3,441) | 16,010 | 11.8% |
| 1H26 | (45,338) | (39,705) | (9,250) | 31,574 | 12.0% |

Operating expenses rose 33% in 2Q26 (77,360 vs 58,061) against 27% revenue growth; G&A rose 56% (30,110 vs 19,351). The bridge from a $21.8mm
GAAP operating loss to a $3.4mm adjusted EBITDA loss is almost entirely stock-based compensation, which post-IPO runs near $64mm a year, about 12%
of revenue, on 81.3mm shares. Net loss looks better than operating loss because interest income is now $2.8mm a quarter on $336mm of IPO cash and
the pre-IPO debt is gone (interest expense 282 vs 2,419). The 4Q26 "first positive quarter" target is an adjusted EBITDA target.

## 3. Cash and working capital behave like a services company, not a subscription business

| Item | 12/31/2024 | 12/31/2025 | 6/30/2026 |
|---|---|---|---|
| Accounts receivable, net | 73,760 | 81,572 | 104,679 |
| Deferred revenue, current | 22,644 | 26,893 | 22,810 |
| Insurance payables (self-insured auto) | 12,186 | 15,144 | 15,329 |
| Cash and equivalents | | | 336,000 (3/31/26: 348,000) |

| Cash flow | FY2024 | FY2025 | 1H25 | 1H26 | 2Q25 | 2Q26 |
|---|---|---|---|---|---|---|
| Net cash used in operating activities | (69,962) | (30,869) | (21,884) | (31,842) | (16,288) | (10,645) |
| Change in accounts receivable | (15,554) | (1,700) | (6,254) | (23,641) | (5,803) | (9,853) |

Receivables grew 28% in six months while revenue grew 27% year over year; agencies pay monthly in arrears for hours delivered. Deferred revenue,
the prepaid-subscription balance a SaaS company grows, fell 15% in the same six months. Operating cash burn in the first half of 2026 was $10mm
worse than the first half of 2025 despite the adjusted-EBITDA improvement. Cash fell $12mm in the June quarter. None of this is distress with
$336mm on hand, but it is the cash profile of a contractor.

## 4. The contract calendar (from the census; terms as stated in documents)

| Agency | Run-rate $mm/yr | Term as documented | Next decision | Federal money in the contract |
|---|---|---|---|---|
| Denton County (DCTA GoZone) | 11.9 | one-year award 2025-09-24 for FY26 | renewal due now (FY27 starts 10/1/2026) | not stated |
| City of Arlington, TX | 10.4 | two-year renewal 2024-12-17, ceiling cut from $30.2mm to $20.8mm | late 2026 | ~40% FTA formula funds per 2022 staff report |
| Jersey City | 7.7 | 2025 renewal, two years plus three-year option | 2026 budget fight unresolved (Gothamist 5/13, NorthJersey 6/18) | not stated |
| Douglas County, CO | 4.4 | annual PCS, 2026 | 1Q27 | local sales tax plus state grants |
| Birmingham (BJCTA transfer) | 2.5 | one year from 2025-09-23 | now | city budget |
| Lorain County | 2.2 | one-year extension 2025-07-01 | mid-2027 | $2.8mm federal expansion grant (12/2025) |
| Grand Prairie | 3.5 est. | bridge to 2026-09-30, then $17.5mm cooperative award | now | "primarily federal transit grant funds" |
| Ben Franklin Transit | 4.1 | 2024-11 award, 3.5 yrs | 2027-28 | local; paratransit software already lost to RideCo |
| Hampton Roads Transit | 3.0 | base year + two options from 10/2025 | annual options | TRiP grant funds |
| LA Metro operations (NoMad) | 15.3 | three-year base from 2025-03 plus options | 2028 | not stated |
| Trinity Metro (Tidewater) | 15.9 | five years from 2024-06 | 2029 | operating funds |
| Mobile (Port City Transit) | 12.1 | five years from 2025-09, renewable once | 2030 | general fund |
| Rochester (Via Transit Twin Cities) | 15.6 | five years from 2026-09 | 2031 | not stated |
| Sioux Falls (Sioux Falls Transit LLC) | 11.2 (NTD RY2024) | not in corpus | driver dispute reported 2026-08-28 | not stated |

Rows citing federal or federally-derived funding among turnkey and hybrid actions: Arlington (FTA ~40%), Grand Prairie (primarily federal), Valdosta
(FTA 5307, 80%), New Braunfels (FTA, TxDOT, ARPA), NJ Transit MicroLink ($7mm CRRSAA), Cobb County (70% state and federal), Moab, Stark (SARTA,
already ended), TART (ARPA), LA Metro's 2018 pilot (FTA MOD Sandbox). IIJA authorization lapses 2026-09-30; ARPA funds must be spent by 2026-12-31.
Across the census, 32 of 123 actions that state a funding source are federal.

## 5. Concentration
LA Metro ($15.3mm a year on the six-year IDIQ view, more on the three-year base), Trinity Metro, Rochester, Mobile, DCTA, Arlington and Sioux Falls
together are roughly $80mm of annual run-rate, about 15% of 2026 guided revenue, in seven hourly contracts. Software churn at those accounts has
already happened at two (LA Metro to Spare, Ben Franklin to RideCo) without touching the driving; the next churn event at any of them is an
operations rebid.

## 6. Supply
No S-3 or Form 144 has been filed since the IPO. Four Schedule 13G filings (passive holders). All seven 2026 Form 4s are purchases or grants.
The lock-up stock has not shown up as registered selling. A resale shelf would be the first visible sign.

## 7. What the multiple is paying for
Enterprise value about $1.94bn (81.3mm shares at $27.98 less $336mm cash). On 2026 guidance: 3.5x revenue, about 8.6x gross profit. Lyft trades
near 2.2x 2027E gross profit (Bleecker's comp). Valuing the services book at Lyft's multiple leaves about $1.7bn of value on a software slice that,
by the census, produces a low-single-digit to low-teens share of documented contract dollars and is losing head-to-head software awards.

## The clock, in order
1. 2026-09-30: IIJA authorization lapse; DCTA GoZone FY27 renewal; Grand Prairie bridge expiry.
2. October 2026: NTD RY2025 contractor tables publish (LA Metro operations payments appear).
3. November 2026: 3Q26 print. Gross margin against 41%; operating cash flow; receivables; any change to the 4Q26 adjusted-EBITDA breakeven target.
4. December 2026: Arlington two-year renewal decision; Jersey City budget; ARPA spend deadline.
5. February 2027: 4Q26 print, the promised first positive adjusted-EBITDA quarter, and FY2027 guidance including Rochester and Mobile at services margins.
6. 2027 renewal season: grant-funded pilots convert to local money or end; Douglas County, Lorain, Hampton Roads options.
