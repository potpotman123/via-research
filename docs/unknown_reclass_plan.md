# Unknown-scope rows: why they exist and how to resolve them (2026-09-21)

Population: 53 Via contract actions at 47 agencies carry scope_type = Unknown (of 329 actions), plus 62 app-only observations that are Unknown by
construction. 17 of the 53 carry a dollar figure; none carries an hourly rate; one carries a software fee. Confidence: 6 high, 21 medium, 26 low.

## Why they are Unknown (root causes, with counts)
| Cause | Rows | Examples | Nature |
|---|---|---|---|
| News-only source; article never says who supplies drivers or vehicles | 22 | Camden, Glendale, Torrance, West Covina, Newark, Homewood, Howard County, Kanawha, St. Clair, Butler County, Highland Park | Rubric working as designed (no inference from launch coverage) |
| Ancillary document on a program that has a classified sibling row | ~17 (15 agencies) | Summit indemnification amendment, SARTA termination notice, UTA change order, Norwalk and Brighton budget resolutions, Valdosta contract-history recital, launch news at Salem, Omaha, DART, ICTC, Chandler, Middlesex | Pipeline gap: no inheritance step across rows of one program |
| Cooperative master agreements and consulting contracts with no deployment scope | 8 | 791 Purchasing Cooperative (2), TIPS 240101, NEORide, Region 4 2026 action, League of Oregon Cities RFP-2360, Vermont PS1018 (2) | Taxonomy gap: no bucket for procurement vehicles |
| Priced authorizing document that describes no service | ~10 | Bi-State $6.34mm extension, New Haven $3.5mm grant, Passaic $1.6mm, Pace $1.36mm, Middlesex $1.14mm, CapMetro $362k, Wake $308k deck, El Paso CO $305k, Douglas $141k, Lorain $48k | Resolutions authorize the award; the staff report or contract holds the scope |

## Signals available without new documents (tested on the 276 classified rows)
| Signal | Precision on classified rows | Unknown rows it reaches |
|---|---|---|
| Signing entity River North Transit LLC | 64 Turnkey, 1 Hybrid, 3 Software-only of 68 (96% operations) | 16 |
| Signing entity NoMad Transit LLC | 31 of 31 Turnkey | 3 |
| Signing entity Tidewater / Port City / Sioux Falls Transit / Twin Cities | 8 of 8 operations | 0 |
| Signing entity Via Mobility LLC | 32 Software-only, 1 Turnkey of 33 (97%) | 5 |
| Signing entity Remix Technologies | 55 Software-only, 2 Turnkey | 1 |
| Signing entity "Via Transportation, Inc." | 36 Turnkey, 18 Software-only, 3 Hybrid: no rule | 17 (unresolved by entity) |
| Annual value >= $1mm at a single city or county, no hourly rate | Documented software median $43k; largest ex-NYC DOE under $1mm | 8 (Bi-State, New Haven, Chandler, Norwalk, Passaic, Highland Park, Pace, Middlesex) |
| Sibling-row inheritance (same agency, same program) | n/a | ~17 |
| NTD contractual table (Via entity as purchased-transportation seller) | definitional | 3 (Suffolk, Valdosta, Lorain; all also covered by inheritance) |
| Via press-release wording ("Via will operate", "driver partners", "Via's fleet" vs "powered by Via", "using Via's technology") | to be measured on classified rows before use | most of the 22 news-only rows and the 62 app-only rows |
| Via driver-recruiting market list (ridewithvia.com drive pages, plus Wayback history) | to be measured | news-only and app-only rows |

## Plan (in order of cost)
1. Retag the 8 cooperative and consulting rows with contract_action = cooperative-vehicle or consulting and remove them from the scope mix. Zero
   classification risk; they are not deployments. Also move the Chandler/Waymo partnership announcement (Hybrid, no dollars) to 'other'.
2. Inheritance pass: for each Unknown row whose agency has a classified row on the same program (same program_name, or same signing entity and
   service), inherit that scope with confidence one notch lower and reason "inherited from <row>" in shards/_corrections.csv. ~17 rows.
3. Entity rule: River North and NoMad rows to Turnkey, Via Mobility LLC and Remix rows to Software-only, confidence medium, reason "entity rule
   (precision 96%/100%/97%/96% on classified rows)". Do not apply to "Via Transportation, Inc." ~20 rows net of overlap with step 2.
4. Dollar rule as a tiebreaker only where steps 2-3 are silent: Bi-State, New Haven, Highland Park to Turnkey, confidence low, reason stated.
5. Press-release wording classifier: grep the 544 cached Via releases for each remaining Unknown and each app-only agency; score with the phrase
   lists above; measure precision on classified rows first; apply only if precision >= 90%; confidence low.
6. Driver-recruiting enumerator: fetch Via's driver market pages and Wayback snapshots; a market listing is independent evidence of Turnkey.
7. Targeted document pull for what remains (expected 8-12 agencies: Chandler, Glendale, Torrance, West Covina, Howard County via Legistar; Newark,
   Camden, Homewood, Kanawha, St. Clair, Wake, Highland Park via agenda search); one Sonnet batch with the strict brief.
8. Recompute the mix. Expected effect: Unknown dollar share (7% of run-rate) flows almost entirely to Turnkey, since the large Unknown rows are
   multi-million single-city contracts signed by operating LLCs; count mix moves little. Report the entity-rule and inherited rows as a separate
   confidence tier so the pitch can quote the document-only mix alongside the completed mix.

## Hybrid rows (9 actions, 7 agencies) and how the model treats them
Rochester ($77.8mm/5yr, Via drivers, agency buses), Sioux Falls (Via drivers, agency vehicles), Citilink Fort Wayne paratransit (Via drivers, agency
vehicles), Summit County fixed route (Via subcontractor drivers, mixed vehicles), Trinity Metro (shared fleet, Tidewater drivers on Via zones),
Region 4/OMNIA response (cooperative vehicle, retag), Met Council (agency contractor supplies drivers and vehicles: this is Software-only under the
rubric, correct it), Chandler/Waymo (partnership announcement, retag to 'other').

The real hybrids are labor-only operations: Via supplies drivers and software, the agency supplies vehicles. Treatment:
- Segment: services. Billing is per hour; the embedded software fee is 2%-8% of contract value (OMNIA per-vehicle software against $60/hr x 3,000
  hours), so splitting it out changes the segment totals by under $2mm. Keep whole in the services engine; optionally carry a memo line moving 5% of
  hybrid value to software as a sensitivity.
- Margin: no vehicle cost in Via's stack, so a labor-only contract should earn 3-5 points more than all-inclusive turnkey, offset by lower revenue
  per hour. Tag these rows "labor-only" in the contract layer so the margin sensitivity can apply an uplift to that subset (~$35mm-$40mm of 2027
  services revenue, so about $1.5mm of gross profit: immaterial to the thesis). The spine keeps one services margin because the filings cannot split it.
- Hazards: these are whole-system operations contracts. Funding is local or formula; the competitive hazard is a legacy operator (Transdev, MV, First
  Transit) rebidding at term end, so use the turnkey hazards and put the term-end dates (Rochester 2031, Trinity 2029, Sioux Falls 2028) in the calendar.
