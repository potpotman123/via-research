# Bleecker Street "Road to Nowhere" (2025-12-16): claim-by-claim verification against primary documents

Prepared 2026-09-20 from the VIA contract census (`out/via_contract_census.csv`, 314 Via contract actions across 134 US public-sector
agencies, plus 28 competitor awards and 62 app-only observations), FTA National Transit Database contractor tables (RY2019-RY2024),
the OMNIA Partners / Region 4 ESC cooperative price schedule (contract R250802), FMCSA registrations, and Via's SEC filings (FY2025 10-K,
2025 424B4). Every number below is copied from a cited document; nothing is derived unless labelled as arithmetic on cited inputs.

Verdict scale: **Supported** (documents confirm the claim as stated) · **Partly supported** (direction confirmed, magnitude or framing
differs) · **Not supported** (documents contradict) · **Not testable here** (requires internal data; filings-only) · **Unverified**
(the specific document Bleecker relied on is not in the corpus).

## Summary table

| # | Bleecker claim | Verdict | One-line evidence |
|---|---|---|---|
| 1 | ~72% of revenue is services, ~28% software | **Supported (dollars); Partly supported (count)** | Run-rate view of latest priced action per agency: Turnkey 67%, Hybrid 13%, Software-only 13%, Unknown 8% of $171mm documented; 72/14/14 excluding Unknown. By count of actions: 146 Turnkey / 9 Hybrid / 110 Software-only / 49 Unknown. NTD purchased-transportation payments to Via entities: $42.7mm in RY2024. 10-K: tech-enabled services cost = 51% of FY25 revenue. |
| 2 | Software fees <5% of contract value in turnkey deals (Arlington) | **Supported** | OMNIA list pricing: software is 1.1%-2.7% of first-year turnkey cost for 5-40 vehicle fleets. Arlington 2024 renewal: River North Transit "self-performs 99.86% = $20,762,626.14" of $20,791,648.32. |
| 3 | Driver hours 96-98% of value in the OMNIA schedule sensitivity | **Supported** | Same OMNIA arithmetic: operations 97.3%-98.9% of first-year cost depending on fleet size and the $50.47-$80.75/vehicle-hour range. |
| 4 | Implementation fees 31%-153% of first-year software fees by fleet size | **Supported (list price); observed contracts lower** | OMNIA microtransit install $27,758.50 vs year-1 software: 153% (1 vehicle), 115% (2), 102% (3), 92% (5), 54% (10), 31% (20), 23% (40). Contracts with both fees stated: 5%-51% (Fort Lauderdale 5%, Doral 18%, Whatcom 23%, Lexington 25%, UTA 28%; five rows state 6%-51% explicitly). |
| 5 | Paratransit implementation 50%-240% of annual software fees upfront | **Supported (list price)** | OMNIA paratransit install $37,852.50 vs year-1 software: 240% (1 vehicle), 156% (5), 89% (10), ~50% (20). |
| 6 | Springfield OH ~34% of year-1 software cost upfront | **Unverified** | Springfield documents in corpus are a draft ordinance and unsigned master terms; the fee exhibit with the 34% figure is not present. |
| 7 | Implementation ~10% of year-1 service revenue in sample contracts | **Unverified** | Not reproducible from the corpus; OMNIA list arithmetic gives 1.2% for a 10-vehicle turnkey fleet. |
| 8 | Insurance and incident costs sit in G&A; reclassification cuts GM 3-4 pts; services GM ~26% / ~22% | **Not testable here** | Filings-only. Consistent context: OMNIA turnkey rate is "all-inclusive"; 10-K discloses self-insured retention on auto incidents where Via does fleet and driver operations; insurance payables $15.1mm (12/31/25). FMCSA: NoMad Transit LLC 80 power units / 250 drivers; Via Transit USA 64 / 65; Tidewater Transit 60 / 84; Truckee Downtowner 30 / 108. |
| 9 | GRR (>95%) ignores downsells; NRR (>120%) uses a survivorship-biased cohort | **Definitions confirmed; downsells documented** | 10-K text confirms both definitions. Census documents downsells that GRR would not count until full loss: Palo Alto $3.244mm NTE (2023) to $1.1mm one year (2025); Milwaukee same-day pilot cut to a $750k limited version (2026); SacRT SmaRT Ride ($8.4mm/yr) ended 12/2024 and replaced by a smaller SacRT Flex; SARTA Connect ended 12/28/2024; Baldwin, Hillsborough, Met Council, BFT paratransit software lost to Spare/RideCo. |
| 10 | Growth fueled by COVID/IIJA money; pilots 50-80% federally subsidized; 10-20% of pilots churned when grants ran out | **Partly supported** | Of 123 Via actions stating a funding source: 32 federal or federally-derived grants, 23 state grants, 41 local/general fund, 27 other. Documented grant-linked ends: Palo Alto (VTA grant sunset), SacRT SmaRT Ride, SARTA Connect (service cuts), Milwaukee (deficit), New Haven (grant-funded pilot). Post-report awards are mostly locally funded (Plano general fund, Addison street fund, Douglas County sales tax) or FTA 5307/CRRSAA (Grand Prairie, NJ Transit). |
| 11 | Organic growth negative; Downtowner (12/2025) masks it | **Not testable here; contract flow is positive** | Revenue growth is not observable from contracts. Contract flow after 12/16/2025: 18 actions, of which 11 Turnkey, 1 Hybrid, 2 Software-only, 4 Unknown; roughly $21mm of new annualized turnkey value plus Rochester ($77.8mm / 5 yrs). Downtowner pre-acquisition rows are flagged and excluded from the organic view (Denver $5.99mm, Placer/TART $3.5mm/yr NTD, Salisbury $2.895mm, Lake County $1.38mm). |
| 12 | LA Metro is the largest account (~$135mm); software went to Spare 3/2025; Spare bid one cent | **Supported except the one-cent bid (Unverified)** | Nov-2024 IDIQ awards to NoMad Transit LLC: $92,066,033.83 (North) + $42,953,484.45 (South), three-year base plus options = $135.0mm. Metro board: "On March 16, 2025 ... Crosby Street Transit LLC (aka Via) as the operations contractor and Spare Labs, Inc. as the software provider." Spare Modification No. 2 (11/13/2025) $386,150 for World Cup enhancements. The Spare price table Bleecker cites is not in the corpus; the only Spare schedule found was Baldwin County's, misfiled in the LA folder. Via never held the Metro Micro software contract: RideCo did (2018-2025, $28.9mm mod 2020; $57.3mm extension 2023). |
| 13 | Arlington TX ceiling $30.2mm to $20.8mm; priced per on-demand service hour; Micro TaaS 96% of 2026 revenue | **Supported** | 2022-11-29 award $30,247,642; 2024-12-17 renewal $20,791,648.32; contract: "fee shall be on a cost per on-demand service hour basis"; vehicles "on a rental basis to independent contractor driver partners"; 2023 software amendment $164,984 (0.5% of the 2022 ceiling). |
| 14 | Mobile AL: "17x revenue growth" via outsourced operations | **Supported in kind** | Council minutes 2025-09-16: "AUTHORIZE CONTRACT WITH PORT CITY TRANSIT, LLC FOR SERVICES TO OPERATE CITY'S TRANSIT SYSTEM; $12,100,000.00 PER YEAR", five years renewable once; Port City Transit LLC is a Via subsidiary (Exhibit 21.1; FMCSA 64 power units / 65 drivers). Fixed-route, paratransit and microtransit operations. |
| 15 | Met Council: Via 9/2022 to Spare 10/2024 | **Supported, with a nuance** | Spare Labs microtransit software contract 24P015, $852,100 (9/23-25/2024). Via Transit Twin Cities LLC still registered with 24 power units / 26 drivers. Via kept the planning-software relationship: Remix contract 24P233 $1,160,897 (4/23/2025). |
| 16 | Baldwin County: Via 2020 to Spare late 2024; terminated Q2'25 | **Supported (dates differ slightly)** | Via Mobility LLC service order 2020-06; renewals $162,000 (2021), $174,000 (2022), extension 2023-09-19, 2024-09-10; Spare Labs award 2025-01-31/03-05 (Year 1 base $19,200 + $2,800/vehicle); mutual termination 2025-01-01 and termination action 2025-08-06. |
| 17 | Ben Franklin Transit: renewed 11/2024 via "791" cooperative; paratransit software to RideCo 11/2025 | **Supported** | 2024-11-14 award $15,285,032 at $53.89/vehicle hour (Turnkey); 2025-11-13 Resolution 42-2025 awards paratransit scheduling software to RideCo, $2,358,300. NTD: BFT paid Via $3,319,553 in RY2024 (17 VOMS). |
| 18 | Palo Alto Link: grant sunset, wind-down | **Supported** | NoMad Transit LLC NTE $3,244,000 through 3/31/2025 (10 vehicles; Stanford $744,000); 2025-06-17 council approves $1.1mm one-year continuation. |
| 19 | Milwaukee County paratransit pilot: 2024 launch; June-2025 cost per trip; excluded from 2026 budget | **Supported, with a nuance** | Tidewater Transit dba Via, $98.73/vehicle hour, Aug 2024-Sep 2025; April 2025 cost $360/trip; report 25-792 (11/26/2025): base 2026 budget dropped it, then $750,000 of contingency retains "a reduced or limited version." |
| 20 | Hillsborough County dropped Via paratransit software via RFP | **Supported** | Contract terminated for cause 2024-08-07; RFP-23-24177 Notice of Intent to Award 2024-07-25, $1,027,877.16 to a competitor. |
| 21 | Hampton Roads Transit: operations replaced by Easton Coaches | **Partly supported; Via since re-won** | NTD payments to "VIA, T/A River North Transit" fell from $7,051,309 (RY2020, 91 VOMS) to $1,546,687 (RY2024). New microtransit contract 25-00363 awarded 10/2025: base year $2,929,066 + two option years $5,934,112 = $8,863,178, turnkey, three zones; expansion announced 1/13/2026. |
| 22 | Springfield OH | **Turnkey confirmed; fee figure unverified** | 2025 draft ordinance grants River North Transit LLC "the authority, right and privilege to establish, maintain and operate a public transportation system" for five years with two five-year options. |
| 23 | $11.80 target = LYFT 2.2x 2027E gross profit | **Not testable here** | Valuation framing; the census informs the mix input (share of gross profit that is labor-intensive), not the multiple. |

## Evidence detail

### Claim 1: services vs software mix
- **Run-rate view** (`out/analysis_summary.md` §1b): one value per agency, latest priced action, annual_value where stated else total/term.
  Turnkey 35 agencies $130.9mm; Hybrid 2 agencies $23.7mm (Trinity Metro $79.38mm/5; Rochester $77.8mm/5); Software-only 32 agencies $2.7mm;
  Unknown 8 agencies $13.9mm. Software rows with a value have a median of $0.05mm; most software subscriptions (Remix, small microtransit
  SaaS) fall under council approval thresholds and carry no public dollar figure, so the software dollar share is a floor, not an estimate.
- **NTD** (`docs/ntd_turnkey_summary.md`): purchased-transportation payments to Via entities by full reporters: RY2019 $1,957,698; RY2020
  $9,410,293; RY2021 $8,748,527; RY2022 $15,822,213; RY2023 $25,973,137; RY2024 $42,705,490 (16 agencies). LA Metro's operations contract
  starts in RY2025, which is not yet published.
- **Filings**: FY25 cost of revenue $262.5mm includes $223.5mm "technology-enabled services" (driver management, fleet management, customer
  support), 51% of revenue and 85% of COGS. At Bleecker's 26% services gross margin that implies services revenue of roughly $302mm, 70% of $434.3mm.
- **Reading**: on dollars, the documented contract base is 67%-83% turnkey-plus-hybrid depending on how Unknowns are treated. On counts, it is
  roughly half turnkey, a third software, and the rest unknown. Both statements are true at once; Bleecker's figure is a dollar statement.

### Claims 2-5: OMNIA price schedule arithmetic (`text/enum/omnia_price_schedule.csv`, RFP 25-08 response, contract effective 2025-08-01)
| Line | Item | Net price |
|---|---|---|
| 1 / 2 | Microtransit software installation, <=20 / >20 vehicles | $27,758.50 / $37,852.50 |
| 3 / 4 | Paratransit software installation, <=20 / >20 vehicles | $37,852.50 / $47,946.50 |
| 5-15 | Microtransit software per vehicle per month: vehicle 1 $1,514.10; 2 $504.70; 3 $252.35; 4 $151.41; 5 $100.94; 6-10 $353.29 each; 11-20 $328.06; 21+ $302.82 | |
| 16-23 | Paratransit software per vehicle per month: vehicle 1 $1,312.22; 2 $277.59; 3 $201.88; 4 $126.18; 5 $100.94; 6-10 $302.82; 21+ $252.35 | |
| 24 | Via turnkey operations, all-inclusive fee per vehicle hour | $50.47-$80.75 |
| 30 | TaaS for Schools operations per vehicle hour (driver-owned vehicles) | $60.56-$80.75 |
| 31 | Paratransit operations per vehicle hour | $60.56-$100.94 |
| 32 | Fixed-route operations per vehicle hour | $90.85-$141.32 |
| 33 | End-to-end management of a full transit service, annual | $201,880-$504,700 |

Arithmetic (12 service hours per vehicle per day, 365 days):

| Fleet | Software $/yr | Install | Ops $/yr at $50.47 | Ops $/yr at $80.75 | Software share | Install / yr-1 software |
|---|---|---|---|---|---|---|
| 5 | 30,282 | 27,758.50 | 1,105,293 | 1,768,425 | 1.7%-2.7% | 92% |
| 10 | 51,479 | 27,758.50 | 2,210,586 | 3,536,850 | 1.4%-2.3% | 54% |
| 20 | 90,847 | 27,758.50 | 4,421,172 | 7,073,700 | 1.3%-2.0% | 31% |
| 40 | 163,523 | 37,852.50 | 8,842,344 | 14,147,400 | 1.1%-1.8% | 23% |

Bleecker's 31%-153% is exactly the 20-vehicle to 1-vehicle span of this schedule; the 96%-98% driver-hour share corresponds to shorter
service days than assumed here (at 8 hours per weekday the software share roughly doubles to 3%-5%).

### Stated hourly rates in signed documents (Turnkey)
West Sacramento $52.23 (2023); Cupertino $35.83 (2019); Ben Franklin Transit $57.50 (2024 amendment), $53.89 (2024 award); UTA $55.23, $62.65,
$68.33 (2022-2024 service orders); Norman OK $94.83 per driver hour; Douglas County CO $70.19 (2025); Wilmington NC $70.00; Milwaukee $98.73;
Addison TX $61.10 (2026); Summit County UT $147.32 per revenue hour (2021, Hybrid). Median of stated rates about $62 per hour.

### Named-account chronology (all rows in the census with sources)
- **LA Metro**: RideCo Contract PS46292001 (2018 award $219,650.26; Mod 5 2019 $28,874,747.50; Mod 7 2020 $5,970,870; Mod 10 2023 $8,292,453;
  Mod 11 2023 $57,346,758 one-year extension). Via/NoMad Transit LLC pilot 2018 ($2,506,410) and six-month extension 2019 ($1,530,332). IDIQ awards
  2024-10-03: OP122943001 $92,066,033.83 and $42,953,484.45. Transition 2025-03-16 to Crosby Street Transit LLC (operations) and Spare Labs (software).
- **Arlington TX**: awards/renewals 2017-11-07 $922,500; 2018-12-04 $2,617,375; 2019-12-03 $4,552,510; 2020-10-13 $10,817,468; 2021-11-30 $10,186,523;
  2022-11-29 $30,247,642; 2023-05-23 software amendment $164,984; 2024-12-17 renewal $20,791,648.32. NTD payments RY2020-RY2024: $1.98mm, $6.06mm,
  $7.99mm, $9.30mm, $7.75mm.
- **Utah Transit Authority**: MSA 20-03399 ceiling amendments $13,371,175 (2022), $21,793,653 (2023), $52,516,459 (2024-04), $65,647,075 (2024-12),
  $56,003,742 (2025-02); Service Order 9 (2026-03-16) $3,463,509 per driver hour.
- **Sioux Falls**: Sioux Falls Transit LLC operates fixed-route and paratransit: NTD RY2024 $11,230,459 (18 + 18 VOMS). August 2026 headline: drivers
  "at odds with Sioux Falls transit contractor."
- **Trinity Metro (Fort Worth)**: 2018 pilot $10,000,000 (Turnkey per NTD RY2019); 2020 task-order extension $1,035,000; 2024-02-20 award to Tidewater
  Transit LLC $79,380,000 (Hybrid).
- **Denton County (DCTA GoZone)**: River North Transit operates GoZone; board memo (2024-08-22) puts the annual cost at $11,347,100.

## What the census cannot settle
Insurance classification, gross-margin splits, GRR/NRR mechanics and organic revenue growth are internal-accounting questions; the census can
only show that the underlying contracts are hourly labor contracts (which they are, for the large ones) and that downsells and quiet endings exist
(which they do). Where Bleecker cites a document not in the corpus (Spare's LA Metro price, Springfield's fee exhibit, the $42-per-ride Metro figure),
the claim is marked Unverified rather than rejected.
