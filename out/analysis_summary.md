# VIA contract census: analysis summary

Generated from out/via_contract_census.csv: 351 rows = 264 Via contract actions (4 Downtowner pre-acquisition) + 25 competitor awards + 62 app-only observations.

## 1. Scope mix (Via contract actions, excl. Downtowner pre-acquisition)

| Scope | Actions (count) | Distinct agencies | Rows with $ | Annualized $mm (rows with $) |
|---|---|---|---|---|
| Turnkey | 104 | 54 | 55 | 180.8 |
| Hybrid | 10 | 9 | 3 | 34.1 |
| Software-only | 88 | 57 | 49 | 26.7 |
| Unknown | 58 | 42 | 16 | 79.2 |
| **Total** | **260** | **134** | | **320.8** |

Dollar-weighted shares among rows with a value and a known scope (annualized; NTE ceilings treated as annual where the document gave only a ceiling and a term, so this overstates spend): Turnkey 75%, Hybrid 14%, Software-only 11%

Caveats: annualized = annual_value_usd where stated, else total_value_usd / term_years; many software rows carry no dollar value (fees under council approval thresholds), so the dollar view is dominated by the large turnkey contracts that do get board approval. The count view is closer to Via's customer-count framing.

## 2. Actions dated after 2025-12-16 (Bleecker report date)

| Date | Agency | State | Action | Scope | Total $ | Annual $ | $/hr | Basis | Src | Conf | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023-12-27 | City of Fargo | ND | award | Software-only | 108400 | 54200 |  | per vehicle per mo | contract | high | Via Mobility LLC. Work Order Request RFP23215 through North Dakota State Contract #283. Post-implementation paratransit and microtransit sof |
| 2024-12-16 | City of Santa Rosa | CA | award | Software-only |  |  |  | annual subscriptio | staff-re | medium | Remix Technologies LLC. Professional Services Agreement for transit scheduling and planning software. 5-year base term with 2-year options.  |
| 2025-09-02 | City of Mobile | AL | award | Turnkey | 121000000 | 12100000 |  | not stated | contract | high | Port City Transit LLC (Via subsidiary); 5 years renewable for 1 additional 5-year period; turnkey management, operations, maintenance, marke |
| 2026-02-11 | City of Sunnyvale | CA | award | Unknown | $8,358,000 |  |  | not stated | staff-re | medium | Matter 26-0333 (2026-02-11, continued from February 10, 2026): 'Authorize the Issuance of the Service Order for the Sunnyvale Microtransit S |
| 2026-02-24 | Douglas County (Board of County Commissi | CO | award | Turnkey | 4404615 |  |  | per vehicle hour | staff-re | medium | 2026 Public Contract for Services (PCS) between Douglas County Board of County Commissioners and River North Transit LLC (per matter title), |
| 2026-02-24 | Douglas County Board of County Commissio | CO | renewal | Unknown | 4404615 |  |  | not stated | staff-re | medium | Signing entity: River North Transit LLC, a subsidiary of Via Transportation Inc. Quote: '2026 Public Contract for Services with River North  |
| 2026-03-16 | Utah Transit Authority | UT | award | Turnkey | 3463509 |  |  | per driver hour | contract | medium | Signing entities: River North Transit, LLC ('Via') and Utah Transit Authority. Service Order No. 9 under On-Demand Technologies MSA (UTA Con |
| 2026-04-10 | Region 4 Education Service Center | TX | award | Unknown | 100000 |  |  | not stated | staff-re | medium | Cooperative purchasing action per brief (agency recorded as the cooperative's lead agency, Region 4 Education Service Center, a Texas local  |
| 2026-05-11 | Sacramento Regional Transit District (Sa | CA | extension | Turnkey | 3760000 |  |  | not stated | news | medium | $3.76M CPUC Access for All Program award funding a 3-year phase (July 1, 2026-June 30, 2029) sustaining/expanding SacRT Flex, a wheelchair-a |
| 2026-05-26 | Douglas County | CO | award | Unknown | 141000 |  |  | fixed fee | contract | medium | Contract Staff Report dated May 19, 2026, matter 4721, for Board of County Commissioners' Business Meeting May 26, 2026: 'Douglas County int |
| 2026-05-26 | Douglas County Board of County Commissio | CO | award | Unknown | 141000 |  |  | fixed fee | staff-re | medium | Signing entity: River North Transit LLC, a subsidiary of Via Transportation, Inc. Quote: 'Public Contract for Services with River North Tran |
| 2026-07-01 | City of Homewood | AL | pilot | Unknown |  |  |  | not stated | news | low | Homewood City Council voted (article says 'Monday'; article's own displayed date 'June 9, 2026' is actually a Tuesday, so exact date is inco |
| 2026-07-06 | Rochester Public Transit | MN | award | Hybrid | 77800000 |  |  | not stated | news | medium | Rochester City Council unanimously approved (Monday, 2026-07-06, per Post Bulletin datePublished) a five-year contract with Via Transit Twin |
| 2026-08-27 | Suburban Mobility Authority for Regional | MI | other | Software-only |  |  |  | not stated | news | medium | Via press release 2026-08-27: 'Via and SMART Expand On-Demand Microtransit Into Northern Macomb County... New partnership with Richmond Leno |

Post-report mix by count: {'Software-only': 3, 'Turnkey': 4, 'Unknown': 6, 'Hybrid': 1}. Annualized $ by scope: {'Software-only': 0.1, 'Turnkey': 13.4, 'Unknown': 0.0, 'Hybrid': 7.8} ($mm)

## 3. Losses, terminations, budget exclusions and competitor awards

| Date | Agency | State | Action | Scope | $ | Notes |
|---|---|---|---|---|---|---|
| 2018-03-15 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only |  | Same matter 2018-0117 (2018-03-15), DEOD Summary Attachment B: RideCo, Inc. awarded parallel firm-fixed-price contract PS46292001 with 28.59% SBE / 3. |
| 2018-04-26 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only | 219650.26 | Same board item as NoMad Transit LLC row above (Item 38, 2018-0117, 04/26/2018): 'A. Contract No. PS46292001 to RideCo in the amount of $219,650.26 fo |
| 2019-11-25 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only | 28874747.50 | Competitor-award: LA Metro Modification No. 5 to Contract PS46292001 with RideCo, Inc. for MicroTransit Pilot Project Part B (Implementation), displac |
| 2020-02-20 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Hybrid | 28874747.50 | Competitor-award, not a Via contract. Signing/contracting entity: RideCo., Inc. ('private partner and technology firm'). Item: 'EXECUTE Modification N |
| 2020-05-28 | Transportation Authority of Marin (TAM)  | CA | competitor-award | Hybrid |  | Competitor-award: Uber Technologies, Inc. (score 84) selected as top-ranked firm over Via Mobility, LLC (score 75, tied with Spare Labs, Inc. and Ride |
| 2020-06-30 | Denton County Transportation Authority | TX | competitor-award | Software-only |  | Competitor: Spare Labs, Inc. (Spare Platform), not Via. Quote (p.418): "Task Order #1 Lewisville Lakeway Zone and Denton Evening Zone was issued to Sp |
| 2020-11-17 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only | 5970870 | Competitor award, not a Via contract -- recorded per brief instruction that a RideCo award at an agency is a competitor-award row. Signing/contracting |
| 2021-08-17 | Capital Metropolitan Transportation Auth | TX | competitor-award | Software-only | 4201206 | Competitor award (Spare Labs Inc.) for a Demand Response Transit System solution; matter AI-2021-179 (2021-08-17), base period of twenty-two (22) mont |
| 2023-07-17 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only | 57346758 | RideCo, Inc. (competitor) contract PS46292001 at LA Metro, MicroTransit Pilot Project. This action = Contract Modification No. 11 extending contract 1 |
| 2024-03-27 | Los Alamos County | NM | competitor-award | Software-only | 2806814.96 | COMPETITOR AWARD (Spare Labs Inc., not Via). Los Alamos County, NM; Legistar matter AGR1040-24 (2024-03-27): "Approval of Services Agreement No. AGR 2 |
| 2024-03-28 | City of Huntsville | AL | competitor-award | Software-only | 106000 | Competitor award: RideCo US Inc. for paratransit dispatching software. City cost: $21,200; Total: $106,000; Grant: $84,800. |
| 2024-04-24 | Alameda-Contra Costa Transit District (A | CA | competitor-award | Software-only |  | Spare Labs Inc. (competitor). 7-year term: up to 2-year implementation period + 5-year operational period. SaaS with turnkey implementation and suppor |
| 2024-04-24 | AC Transit and BART (East Bay Paratransi | CA | competitor-award | Software-only | 4566000 | Competitor-award: AC Transit Board (staff report meeting 4/24/2024) considers authorizing a joint contract with BART, with Spare Labs Inc. for Softwar |
| 2024-07-25 | Hillsborough County | FL | competitor-award | Software-only | 1027877.16 | Revised Notice of Intent to Award, RFP-23-24177, Paratransit Scheduling Software System, posted July 25, 2024 -- County terminates Via Transportation, |
| 2024-09-23 | Metropolitan Council | MN | competitor-award | Software-only | 852100 | Competitor award (Spare Labs, Inc.), no Via entity involved. Quote (p.3): '5. 2024-216 SW: Microtransit Software, Contract 24P015. It was moved by Car |
| 2024-09-25 | Metropolitan Council | MN | competitor-award | Software-only | 852100 | Contracting entity Spare Labs, Inc. (Via competitor). Quote: "That the Metropolitan Council authorize the Regional Administrator to negotiate and exec |
| 2024-12-16 | City of Santa Rosa | CA | competitor-award | Software-only |  | Competitor award: Remix Technologies LLC (Delaware LLC). Professional Services Agreement F002920 for transit scheduling and planning software, integra |
| 2025-01-01 | Baldwin County Commission | AL | termination | Software-only |  | Via Mobility LLC; mutual termination agreement; original contract approved June 16, 2020 |
| 2025-01-31 | Baldwin County Commission | AL | competitor-award | Software-only |  | Spare Labs, Inc. (competitor). Microtransit Software contract. Year 1: Base $19,200 + $2,800/vehicle (1-30) + $3,300/vehicle (30+) + $12,000 service/m |
| 2025-03-16 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only |  | RFP Award Listing for 'MICRO-TRANSIT SOFTWARE FOR PUBLIC TRANSPORTATION,' Vendor: Spare Labs, Inc. Pricing table (Years 1/2/3): Base Operating Cost $1 |
| 2025-05-13 | Sun Metro (City of El Paso) | TX | competitor-award | Software-only | 1350671.56 | Competitor-award: Solicitation 2025-0132R Paratransit Software awarded to Rideco US Inc. (Los Angeles, CA), displacing Via Transportation Inc. dba Via |
| 2025-08-06 | Baldwin County Commission | AL | termination | Software-only |  | Signing entities Baldwin County Commission and Via Mobility, LLC (Delaware LLC). Quote: "The Parties are bound by that certain Contract for Profession |
| 2025-11-13 | Ben Franklin Transit | WA | competitor-award | Software-only | 2358300 | Competitor-award: Resolution 42-2025 authorizes BFT to award On-Demand Paratransit Route Scheduling & Management Software & Hardware Solution (Contrac |
| 2025-11-13 | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only | 386150 | Contracting entity Spare Labs, Inc. (Via competitor) for LA Metro's "Metro Micro" on-demand shuttle brand. Quote: "AUTHORIZE the Chief Executive Offic |
|  | Sacramento Regional Transit District (Sa | CA | termination | Turnkey |  | SmaRT Ride, Via-operated on-demand microtransit launched Jan 2020 (Via press release: "the largest on-demand microtransit system in America with 42 ve |
|  | City of Jersey City | NJ | budget-exclusion | Turnkey |  | PROPOSED, NOT YET ACTED ON as of the source articles (post-2025-12-16 budget-crisis development; exact council-vote date left blank/unknown since no v |
|  | Hillsborough County | FL | termination | Software-only | 860825.00 | RFP-23-24177 Paratransit Scheduling Software System, Revised Notice of Intent to Award, posted July 25, 2024. Original contract had been awarded to Vi |
|  | Baldwin County Commission | AL | competitor-award | Software-only |  | Competitor award: Baldwin County Commission Contract for Professional Services with Spare Labs, Inc. (Suite 810, 815 W Hastings St, Vancouver BC), for |
|  | San Francisco Bay Area Rapid Transit Dis | CA | competitor-award | Software-only | 5246000 | Competitor-award: Spare Labs Inc. awarded Contract No. 6M4830 for East Bay Paratransit Consortium (EBPC) scheduling software, replacing the incumbent  |
|  | Los Angeles County Metropolitan Transpor | CA | competitor-award | Software-only |  | Same DEOD Summary as the NoMad Transit LLC (Via) row (packet 460): Rideco is Prime for PS46292001 with SBE/DVBE subcontractors Civic Projects Incorpor |

## 4. Stated per-hour rates (turnkey / operations)

| $/hr | Agency | State | Date | Basis | Scope |
|---|---|---|---|---|---|
| 35.83 | City of Cupertino | CA | 2022-07-19 | per vehicle hour | Turnkey |
| 35.83 | City of Cupertino | CA | 2019-08-06 | per service hour | Turnkey |
| 52.23 | City of West Sacramento | CA | 2023-06-07 | per vehicle hour | Turnkey |
| 53.89 | Ben Franklin Transit | WA | 2024-11-14 | per vehicle hour | Turnkey |
| 55.23 | Utah Transit Authority | UT | 2023-10-11 | per revenue hour | Turnkey |
| 55.97 | Utah Transit Authority (UTA) | UT | 2022-07-13 | per driver hour | Turnkey |
| 57.50 | Miami-Dade County | FL |  | per service hour | Turnkey |
| 57.50 | Ben Franklin Transit | WA | 2024-01-11 | per vehicle hour | Turnkey |
| 58.83 | Utah Transit Authority (UTA) | UT | 2021-09-16 | per driver hour | Turnkey |
| 62.65 | Utah Transit Authority | UT |  | per service hour (bill | Turnkey |
| 62.65 | Utah Transit Authority (UTA) | UT | 2022-11-29 | per vehicle hour | Turnkey |
| 68.33 | Utah Transit Authority | UT | 2024-03-01 | per vehicle hour | Turnkey |
| 70.00 | City of Wilmington | NC |  | per vehicle hour | Turnkey |
| 70.19 | Douglas County | CO | 2025-03-25 | per vehicle hour | Turnkey |
| 93.87 | City of Cupertino | CA | 2023-02-08 | per vehicle hour | Turnkey |
| 94.83 | City of Norman | OK |  | per driver hour | Turnkey |
| 98.73 | Milwaukee County | WI | 2024-08-01 | per vehicle hour | Turnkey |
| 99.70 | City of Norman | OK |  | per vehicle hour | Turnkey |
| 147.32 | Summit County | UT | 2021-04-13 | per revenue hour | Hybrid |

n=19, min 35.83, median 62.65, max 147.32. OMNIA R250802 list: microtransit turnkey $50.47-$80.75/vehicle hour, paratransit $60.56-$100.94, fixed route $90.85-$141.32 (net).

## 5. Stated software fees and implementation fees

| Agency | State | Date | Software fee | Basis | Implementation fee | Impl % yr1 | Scope |
|---|---|---|---|---|---|---|---|
| Baldwin County | AL |  | 550 | per vehicle per month | 110000 |  | Software-only |
| Baldwin County Commission | AL |  | 550 | per vehicle per month |  |  | Software-only |
| Baldwin County Commission | AL |  | 550 | per vehicle per month | 110000 | 50.9% | Software-only |
| Baldwin County Commission | AL | 2021-09-11 | 550 | per vehicle per month |  |  | Software-only |
| Baldwin County Commission | AL | 2022-09-20 | 590 | per vehicle per month |  |  | Software-only |
| Broward County | FL |  | 62000 | annual subscription (Yea |  |  | Software-only |
| City and County of Denver | CO | 2024-10-14 | 5991681 | turnkey operations contr |  |  | Turnkey |
| City of Asheville | NC | 2025-01-28 | 26000 | per year |  |  | Software-only |
| City of Cottonwood | AZ | 2025-03-04 | 400 | per vehicle per month | 15000 |  | Software-only |
| City of Doral | FL |  | 11000 | per year | 2000 |  | Software-only |
| City of Doral | FL | 2020-08-12 | 11000 | per year | 2000 |  | Software-only |
| City of Doral | FL |  | 12000 | per year |  |  | Software-only |
| City of El Paso | TX | 2022-07-19 | 755080 | 3-year total |  |  | Software-only |
| City of Fargo | ND | 2023-12-27 | 4100 | per month (up to 13 vehi | 10000 |  | Software-only |
| City of Fort Lauderdale | FL | 2021-09-15 | 39500 | per year | 2000 |  | Software-only |
| City of Galveston | TX | 2021-09-09 | 17500 | per year |  |  | Software-only |
| City of Key West | FL | 2023-12-01 | 54000 | per year |  |  | Software-only |
| City of Key West | FL | 2022-05-11 | 248880 | NTE contract amount |  |  | Software-only |
| City of Key West | FL | 2023-10-20 | 270000 | 5 years |  |  | Software-only |
| City of Lexington | KY | 2021-03-01 | 10000 | per year | 2500 | 25 | Software-only |
| City of Philadelphia | PA |  | 43260 | per year |  |  | Software-only |
| City of Philadelphia | PA |  | 84000 | not stated |  |  | Software-only |
| Fresno | CA | 2024-08-06 | 197000 | fixed contract amount |  |  | Software-only |
| Hillsborough County | FL | 2023-12-20 | 235 | per vehicle per month (Y | 35000 |  | Software-only |
| Lake Havasu City | AZ | 2023-09-19 | 3000 | per vehicle per month (f | 35000 |  | Software-only |
| LakeXpress (Lake County Board of County  | FL |  | 31000 | per year, based on total | 2000 | 6.45% | Software-only |
| Lee County (LeeTran) | FL |  | 200.00 | per vehicle per month | 14000.00 | 11.8% | Software-only |
| Los Angeles County Metropolitan Transpor | CA | 2025-11-13 | 447400.01 | total contract value wit |  |  | Software-only |
| MET Transit |  | 2023-04-10 | 41166 | per year average |  |  | Software-only |
| North County Transit District | CA |  | 362643.01 | not stated |  |  | Software-only |
| Orange County | NC |  | 34000 | NTE/fixed (term unspecif |  |  | Software-only |
| Regional Transportation Commission of So | NV | 2025-05-22 | 77250 | annual subscription (Saa |  |  | Software-only |
| Tahoe Truckee Area Regional Transportati | CA | 2023-11-28 | 400000 | pilot program funding |  |  | Turnkey |
| Toledo Area Regional Transit Authority | OH | 2024-02-15 | 135000 | 3 years |  |  | Software-only |
| Town of Morrisville | NC |  | 142280 | NTE (term unspecified) |  |  | Software-only |
| Utah Transit Authority | UT |  | 15244 | per month |  |  | Turnkey |
| Utah Transit Authority (UTA) | UT | 2021-09-16 | 8781 | per month |  |  | Turnkey |
| Utah Transit Authority (UTA) | UT | 2022-07-13 | 8308 | per month |  |  | Turnkey |
| Utah Transit Authority (UTA) | UT | 2022-11-29 | 15244 | per month (fixed technol | 51800 |  | Turnkey |
| Wake County | NC |  | 42493 | NTE (term unspecified);  |  |  | Unknown |
| Whatcom Transportation Authority | WA |  | 22200 | per year | 5000 |  | Software-only |
| Whatcom Transportation Authority | WA |  | 25361.28 | per year |  |  | Software-only |
| Whatcom Transportation Authority | WA | 2023-05-01 | 4400 | 8 months (prorated from  |  |  | Software-only |
| YVEDDI | NC |  | 7695 | NTE/fixed (term unspecif |  |  | Software-only |

Implementation fee as % of year-1 fees where both were stated: n=5, range 6%-51%
OMNIA list: microtransit software installation $27,758.50 (<=20 vehicles) / $37,852.50 (>20); per vehicle per month tiers $1,514.10 (vehicle 1) down to $302.82 (vehicles 21+). Example 10-vehicle fleet: monthly software = 1,514.10+504.70+252.35+151.41+100.94+5x353.29 = $4,289.95 -> $51,479/yr; installation $27,758.50 = 54% of year-1 software fees.

## 6. Downtowner (pre-acquisition) actions captured

- 2025-08-05 City of Salisbury (NC): award, Turnkey, total 2895000, annual 
- 2023-08-24 Washoe County (NV): extension, Turnkey, total , annual 400000
- 2016-06-21 City of Manhattan Beach (CA): award, Turnkey, total , annual 
- 2017-07-18 City of Manhattan Beach (CA): extension, Turnkey, total , annual 

## 7. Unknown-scope actions with dollars (Tier-3 adjudication queue)

| Annualized $mm | Agency | Date | Action | Total | Notes |
|---|---|---|---|---|---|
| 21.0 | Utah Transit Authority | 2024-04-17 | amendment | 52516459 | Entity: River North Transit, LLC (Via). UTA Contract 20-03399 (On Demand Technologies Master Service Agreement, approved |
| 10.8 | City of Arlington | 2020-10-13 | renewal | 10817468 | Entity: Via Transportation, Inc. Quote (p.1): "On October 13, 2020, City Council approved Resolution No. 20-280, executi |
| 10.4 | City of Arlington | 2024-12-17 | renewal | 20791648.32 | Entity: River North Transit, LLC (not a MWBE firm; self-performs 99.86% = $20,762,626.14; subcontractor Holt Communicati |
| 10.2 | City of Arlington | 2021-11-30 | renewal | 10186523 | Entity: Via Transportation, Inc. (not a MWBE firm). Quote (p.1): "Approve a resolution authorizing the City Manager or h |
| 6.3 | Bi-State Development Agency (Metro Trans | 2025-04-18 | extension | 6344000 | Resolution #1421, Bi-State Development Agency Board of Commissioners, April 18, 2025. Quote: "authorizes the President a |
| 4.6 | City of Arlington | 2019-12-03 | renewal | 4552510 | Entity: Via Transportation, Inc. Quote (p.1): "On December 3, 2019, City Council approved Resolution No. 19-325, executi |
| 3.0 | City of Arlington | 2022-11-29 | renewal | 30200000 | News article: Arlington City Council voted to continue citywide Via on-demand rideshare service through Dec. 2024 with f |
| 2.6 | City of Arlington | 2018-12-04 | renewal | 2617375 | Entity: Via Transportation, Inc. Quote (p.1): "On December 4, 2018, City Council approved Resolution No. 18-313, executi |
| 2.4 | City of Norwalk | 2025-10-07 | pilot | 2440370 | Signing entity: Nomad Transit LLC, a wholly owned subsidiary of Via Transportation, Inc. Quote (p.4): 'RESOLUTION NO. 25 |
| 2.2 | Lorain County | 2025-07-01 | extension | 2200000 | Lorain County Board agenda item #26 (07/01/25). Signing entity: River North Transit, LLC, 'a wholly owned subsidiary of  |
| 2.0 | Trinity Metro (Fort Worth Transportation | 2018-12-17 | pilot | 10000000 | Background recital in packet 387 (Trinity Metro BA2024-12): 'On December 17, 2018, the Trinity Metro Board of Directors  |
| 2.0 | City and County of Denver | 2024-10-29 | award | $5,991,681 | Resolution CR24-1443 (matter 24-1443) approving contract between City & County of Denver and Montbello Downtowner, LLC ' |
| 0.9 | City of New Haven | 2023-04-06 | pilot | 3500000 | Board of Alders resolution LM-2023-0251 (matter dated 2023-04-06), 'AUTHORIZING THE MAYOR TO APPLY FOR AND ACCEPT GRANT  |
| 0.7 | Los Angeles County Metropolitan Transpor | 2018-04-26 | award | 348684.69 | LA Metro Regular Board Meeting Minutes, April 26, 2018, Item 38 (2018-0117), 'MICROTRANSIT PILOT PROJECT (MTP)': 'AUTHOR |
| 0.1 | Capital Metropolitan Transportation Auth | 2023-10-26 | award | 362520 | Signing entity: Via Mobility, LLC (Exhibit B parent-company disclosure, p.6, names parent as Via Transportation, Inc., 1 |
| 0.0 | Region 4 Education Service Center | 2026-04-10 | award | 100000 | Cooperative purchasing action per brief (agency recorded as the cooperative's lead agency, Region 4 Education Service Ce |