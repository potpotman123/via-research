# Classification brief for Phase 3 agents (Haiku / Sonnet)

You are turning one procurement document ("packet") into zero or more rows of a contract census for Via Transportation
(NYSE: VIA). No web browsing. Use only the packet text. Copy numbers exactly as written. Blank beats a guess.

## Input
A packet file `snippets/packets/<doc_id>.txt`: header lines (`# source_url`, `# path`, `# context` with the Legistar client
and matter title, or the Bleecker Drive folder name) followed by the most informative pages of the document.

## Output
Append rows to your shard CSV `shards/<your_shard>.csv` using EXACTLY the header in `shards/HEADER.csv`:

agency, city, state, program_name, service_type, contract_action, award_or_approval_date, term_start, term_years_incl_options,
total_value_usd, annual_value_usd, pricing_basis, hourly_rate_usd, software_fee_usd, software_fee_basis, implementation_fee_usd,
implementation_fee_pct_of_year1, scope_type, drivers_supplied_by, vehicles_supplied_by, fleet_size, funding_source,
signed_after_2025_12_16, status, source_url_1, source_url_2, source_type, confidence, notes

One row per contract ACTION (award, renewal, amendment, extension, termination, budget exclusion, competitor award at a Via
agency). A staff report approving a 3-year contract with two 1-year options is ONE row (term_years_incl_options = 5).
An amendment that raises the ceiling is a separate row. If the packet is not about a contract action (a news article, a
generic Via marketing deck, an unrelated "Downtowner" saloon), write NO row and note it in your return message.

## Field rules
- agency: the public body that is party to the contract. city/state: of the agency. program_name: service brand (GoZone, Metro Micro).
- service_type: microtransit | paratransit | fixed-route | planning-software | school | campus-shuttle | other.
- contract_action: award | renewal | amendment | extension | termination | non-renewal | budget-exclusion | competitor-award | pilot | other.
- award_or_approval_date: the board/council approval date (YYYY-MM-DD) if in the packet, else blank. term_start likewise.
- total_value_usd: the not-to-exceed or total contract value as written. annual_value_usd: only if the document states an annual figure.
  NEVER derive annual by dividing total by years.
- pricing_basis: per revenue hour | per service hour | per vehicle hour | per trip | per vehicle per month | annual subscription |
  fixed fee | not stated. hourly_rate_usd: the rate if stated (e.g., 82.35).
- software_fee_usd / software_fee_basis: platform, license or subscription fee and its unit (per month, per year, per vehicle per month).
- implementation_fee_usd: one-time implementation/launch/onboarding fee. implementation_fee_pct_of_year1: compute ONLY if both
  the implementation fee and a year-1 fee are stated on the same page; otherwise blank.
- scope_type (the key field):
  - **Turnkey**: Via or its subcontractor supplies drivers and/or vehicles and bills per revenue/service/vehicle hour or per trip.
    Drivers sourced through a staffing agency or independent contractors still count as Turnkey. "No capital costs to the agency"
    and "Via will provide N vehicles" are Turnkey markers.
  - **Software-only**: the agency or its own operations contractor (MV, Transdev, First Transit, etc.) supplies drivers and vehicles;
    Via is paid a subscription/license/platform fee plus implementation. Remix planning software is always Software-only.
  - **Hybrid**: a genuine mix (e.g., Via supplies drivers, agency supplies vehicles; or software plus a small Via-operated overflow fleet). Explain in notes.
  - **Unknown**: the packet does not say who supplies drivers/vehicles or how Via is paid.
- drivers_supplied_by / vehicles_supplied_by: Via | Via subcontractor | agency | agency contractor (name it) | not stated.
- fleet_size: number of vehicles in the service if stated.
- funding_source: as stated (FTA 5307, 5310, 5311, CRRSAA, ARPA, CMAQ, state grant name, local sales tax, general fund, TIRCP...).
- signed_after_2025_12_16: 1 if award_or_approval_date is after 2025-12-16, else 0; blank if the date is unknown.
- status: active | ended | terminated | pending | unknown.
- source_url_1: the `# source_url` from the packet header. For Bleecker Drive files with no URL, put `bleecker-drive:<path>`.
- source_type: staff-report | contract | amendment | minutes | rfp | budget | news | other.
- confidence: high (all key fields explicit) | medium | low.
- notes: the signing legal entity (River North Transit LLC, NoMad Transit LLC, Via Mobility LLC, Remix Technologies LLC...),
  the exact pricing-table lines you relied on (quote them), page numbers, and anything that made classification hard.

## Downtowner and cooperative contracts (read carefully)
- Downtowner LLCs ARE Via companies. Via acquired Downtowner on 2025-12-12; its 10-K lists Downtowner Transportation LLC, Downtowner App LLC
  and town LLCs (Aspen Downtowner Group, Basalt, Carbondale, CB/Crested Butte, Glenwood, Leadville, Steamboat, Montbello/Denver Connector,
  Park City, Empire Pass, Kimball Circulator, Moab, Jackson WY, Big Sky MT, Idaho Falls, Twin Falls, Tahoe, South Lake, Truckee, Palisades,
  Savannah, NC, Aero). A contract with any of them gets a row (scope is usually Turnkey: Downtowner supplies drivers and vehicles). If the
  action is dated before 2025-12-12 write "Downtowner, pre-acquisition" at the start of notes so it can be excluded from organic analysis.
- Cooperative purchasing contracts and their price schedules (OMNIA Partners / Region 4 ESC contract R250802 or 2199, the "791" Purchasing
  Cooperative, TIPS) ARE contract actions: agency = the cooperative's lead agency, contract_action = award, and the price schedule lines
  (software fee per vehicle per month, driver-hour rates, implementation fees) go in the fee columns and notes. Via's RFP response that
  became the awarded cooperative contract counts; a losing proposal does not.

## Traps
- "Via Mobility Services" (Boulder/Denver, CO) is an unrelated nonprofit. "VIA Metropolitan Transit" is San Antonio's transit agency.
  "Downtowner Saloon" / "Historic Downtowner" (Fort Lauderdale) is a bar; Albuquerque "Downtowner" items are real estate. Write no row for these.
- A Spare Labs or RideCo award at an agency is a `competitor-award` row (scope_type = Software-only for the competitor's product;
  note that it displaces Via if the document says so).
- Ceilings are not spend. Put NTE amounts in total_value_usd and say "NTE" in pricing_basis notes.
- Do not infer Turnkey from the existence of a rider app; infer only from who supplies drivers/vehicles or per-hour billing.

## Return message
Only: `rows: N; skipped: M (reasons: ...)`.
