# VIA — independent test of Bleecker Street's short thesis on Via Transportation (NYSE: VIA)

Owner: Kendall Wu (KW). Created 2026-09-20. This folder is separate from the Copart repo at `~/cprt`.

## Purpose

Bleecker Street Research, "Via Transportation (VIA): Road to Nowhere" (2025-12-16,
https://www.bleeckerstreetresearch.com/research/via) argues Via is a labor-intensive transit
contractor (drivers/vehicles billed per hour) presented as a software company. They sampled ~100
contracts. This project re-runs that test on the full population of publicly documented US Via
contract actions, then checks whether business signed after 2025-12-16 looks more SaaS-like.

Price $27.98 (2026-09-18). Bleecker target $11.80 = LYFT's 2.2x 2027E gross profit.

## Deliverables

1. `out/via_contract_census.csv` — one row per contract action (schema in `shards/HEADER.csv`),
   every number copied exactly from a cited source, blanks where unknown.
2. `out/claims_verification.md` — each Bleecker claim, evidence for/against, verdict.
3. `out/post_bleecker_analysis.md` — every win/renewal/loss dated after 2025-12-16, pre vs post mix,
   the four 1H26 network contracts totaling >$40mm ACV (per 2Q26 call).
4. `out/findings.md` — short memo for the long/short decision.

## Decisions made

- Enterprise Claude Code license only. No personal API key, no Batch API.
- Model tiering via subagents: regex (no model) → Haiku → Sonnet → main thread.
- Two to three concurrent subagents max. Prior run with 7 parallel agents hit the rate limit and wrote nothing.
- One-shot data pull. No continuous monitor (Phase 7 dropped).
- WebFetch never sources a number. PDFs are downloaded and extracted locally.
- Everything checkpoints to disk: `raw/` (cache), `text/` (extracted text + FTS index), `snippets/`, `shards/`.

## Pipeline

**Phase 0 — setup (done).** Folder skeleton, schema header, git.

**Phase 1 — enumerate.** Build the target list (agency, Via entity, dates, candidate URLs) from registries, not search:
- Bleecker's Drive folder (pre-collected ~100 contracts): https://drive.google.com/drive/folders/1jFI7x1sodivnF2uCUtpNrRC65ojkl4VA (gdown)
- Apple App Store developer account Via Transportation, Inc., artistId 657777018.
  `raw/appstore_via_apps_us_2026-09-20.json` has the first 200 apps (limit hit; more exist — paginate via
  other storefronts or Google Play `google-play-scraper` developer()). Each agency-branded app = one deployment.
  Wayback snapshots of the developer page give add/remove dates. Exclude non-US (Abu Dhabi, Dubai, Ajman, BC Transit...).
- NTD: annual Contractual Relationships table (contractor name, mode, amount) — published as annual data tables on
  transit.dot.gov; not found on Socrata, confirm location. NTD monthly module IS on Socrata:
  datahub.transportation.gov dataset `8bui-9xvu` "Complete Monthly Ridership (with Adjustments and Estimates)"
  (VRH/UPT/VOMS by agency/mode/TOS) — trajectory check for turnkey agencies.
- Legistar Web API (verified working): `https://webapi.legistar.com/v1/{client}/matters?$filter=substringof('River North',MatterTitle)`
  Sweep all known clients with each entity name. Attachments via `/matters/{id}/attachments`.
- EDGAR full-text search (verified, 4 hits for "River North Transit"): `https://efts.sec.gov/LATEST/search-index?q=...`
  with User-Agent header. Also Form 4s since ~March 2026 lock-up expiry.
- FMCSA SAFER / QCMobile for the operating LLCs (power units, drivers, insurance).
- State WARN notices (`warn-scraper`), OpenCorporates foreign registrations, driver job postings (Wayback).
- GDELT DOC API for launch/loss news; MuckRock for fulfilled records requests; state contract registries
  (NJ Transit, DART DE, CTtransit, UTA, state DOTs).
- ridewithvia.com sitemap.xml for case studies / city pages.

**Phase 2 — fetch and filter (scripted, zero model tokens).**
- Throttled parallel downloader → `raw/` keyed by URL hash. `civic-scraper` (Big Local News) for CivicPlus,
  CivicClerk, Granicus, Legistar, PrimeGov portals; Playwright for anything else JS-rendered.
- PyMuPDF text per page → SQLite FTS5 index in `text/`. `ocrmac` (Apple Vision) only for pages with empty text layer.
- Query entity names + pricing terms → hit pages ±1 → `snippets/`. Dedup by content hash.
- pdfplumber/docling table extraction only on hit pages containing pricing tables.

**Phase 3 — classify.** Snippet → row.
| Tier | Runs on | Handles |
|---|---|---|
| 0 | regex | entity + per-hour billing (turnkey) or entity + subscription/license (software), all fields present |
| 1 | Haiku subagent | partial regex hits, clean staff reports, URL triage; marks Unknown rather than guessing |
| 2 | Sonnet subagent | hybrid scope, messy pricing tables, multiple actions per document |
| 3 | main thread | low-confidence rows, Bleecker's named accounts |
Agents append to `shards/<name>.csv` and return a row count only.

**Phase 4 — merge + QA.** `scripts/merge.py`: concat shards, validate schema, dedupe (agency, action, date),
reject any row with a number and no URL, route rejects up a tier. Known-answer test = Bleecker's named accounts.
Hand spot-check a random sample.

**Phase 5 — analysis.** Services share dollar- and count-weighted vs 72%; margin triangle (blended 40%);
pre/post 2025-12-16 by approval date (note RFP issue date); four >$40mm ACV 1H26 contracts; churn taxonomy
(competitive / funding cliff / budget); IIJA (expires 2026-09-30) and ARPA (spend by 2026-12-31) exposure;
NTD monthly VRH at Via agencies; Form 4s.

**Phase 6 — deliverables.** Files in `out/`. Commit.

## Classification rubric (scope_type)

- **Turnkey** — Via or its subcontractor supplies drivers and/or vehicles; bills per revenue/service/vehicle hour or per trip.
  Subcontracted or independent-contractor drivers still count as turnkey (Via recognizes gross, 10-K Note 2).
- **Software-only** — agency or its own contractor supplies drivers and vehicles; pays Via subscription/license/implementation fees.
- **Hybrid** — mix; explain in notes.
- **Unknown** — insufficient evidence.

Separate columns for drivers_supplied_by and vehicles_supplied_by. Keep total / annual / NTE-ceiling distinct;
never derive annual by dividing unless the document does.

## Via contracting entities (Exhibit 21.1, FY2025 10-K) — search these, not just "Via"

River North Transit LLC (most common); Via Mobility, LLC; NoMad Transit LLC (LA Metro contracting entity);
Crosby Street Transit LLC (LA Metro operations; absorbed 145 Metro operators); Flatiron Transit LLC;
Greenpoint Transit LLC; Port City Transit LLC (likely Mobile AL); Tidewater Transit LLC (likely Hampton Roads);
Sioux Falls Transit LLC; Via Transit Twin Cities LLC (Met Council); Via Transit East LLC; Via Transit (USA) LLC;
Remix Technologies LLC (fixed-route planning software); Citymapper; Downtowner Transportation LLC, Downtowner App LLC
and resort-town LLCs: Aspen Downtowner Group, Basalt, Carbondale, CB (Crested Butte), Glenwood, Leadville, Steamboat,
Montbello (Denver), Park City, Empire Pass, Kimball Circulator, Moab, Jackson WY, Big Sky MT, Idaho Falls, Twin Falls,
Tahoe, South Lake, Truckee, Palisades, Savannah, NC, Aero.

Downtowner acquired 2025-12-12 ($40.7mm cash, +94 customers in 4Q25). Flag Downtowner rows pre/post acquisition;
they are inorganic and must not contaminate the post-Bleecker organic analysis. Downtowner is a resort-town on-demand
shuttle operator (turnkey by nature), not Florida's Freebee.

## Bleecker's claims to verify

- ~72% revenue services / ~28% software; software fees <5% of contract value (Arlington TX); driver hours 96–98% of
  value in the OMNIA cooperative schedule sensitivity (pricing PDF p.~72).
- Implementation fees ~31–153% of first-year contract value by fleet size; paratransit 50–240% of annual software fees
  upfront; Springfield OH ~34% of yr-1 software cost upfront; ~10% of yr-1 service revenue in sample contracts.
- Insurance/driver-incident costs in G&A (Uber/Lyft: cost of revenue); reclass cuts GM 3–4 pts; services GM ~26%, ~22% ex support staff.
- GRR (>95%) ignores downsells; NRR (>120%) survivorship-biased (116% vs 85% standardized illustration).
- Growth fueled by COVID/IIJA; IIJA expires 9/2026; 10–20% of pilots churned when grants ran out; pilots 50–80% federally subsidized.
- Organic growth negative; Downtowner M&A masks it into lock-up expiry (~$1.2bn shares).
- Named accounts: LA Metro, Arlington TX, Mobile AL, Met Council MN, Baldwin County AL BRATS, Ben Franklin Transit WA,
  Palo Alto Link, Milwaukee County paratransit pilot, Hillsborough County FL, Hampton Roads Transit, Springfield OH.
  (Details and primary-source links: `docs/bleecker_sources.md`.)

## Established from SEC filings (FY2025 10-K 2026-03-06; 424B4 2025-09-15) — reuse, do not redo

- FY25 cost of revenue $262.5mm = $223.5mm tech-enabled services (driver mgmt, fleet mgmt, customer support)
  + $25.8mm launch/support personnel + $13.3mm IT. Tech-enabled services cost = 51% of FY25 revenue ($434.3mm), 85% of COGS
  → services revenue plausibly 61–73% of total.
- Note 2: Driver Management and Fleet Management are performance obligations recognized gross; unit of volume is fleet size,
  minimum vehicles, or vehicle-hours. RPO computed from expected driver hours and service hours.
- 97% of 2024/2025 revenue recurring subscription; 3% one-time implementation/consulting/advertising recognized in year 1.
  Platform ARR = quarterly revenue × 4 (135.7 × 4 = 542.8 at 6/30/26), so it includes hourly services and one-time fees.
- G&A includes insurance; self-insured retention risk on auto incidents where Via does fleet mgmt / driver ops.
  Insurance payables $15.1mm (12/31/25) vs $12.2mm.
- GRR excludes expansion/upsell/downsell/cross-sell. NRR cohort = customers with revenue in each quarter of prior year.
  NRR >120% (2023–24), 119% (2025); GRR >95%, 98% in 4Q25.
- Legacy segment = one pure ops contract ended June 2024. Mgmt: 2025 organic customer growth ~9%.
  GM 39% (2024) → 40% (2025) → 41% (2Q26); LT target ~50%.
- FY25 rev 434.3, net loss (96.4), Adj. EBITDA (33.4); 2Q26 rev 135.7 (+27%), Adj. EBITDA (3.4);
  FY26 guide rev $550–553mm, Adj. EBITDA $(12.5)–(7.5), first positive quarter targeted 4Q26;
  847 customers, ARR $542.8mm, RPO $318.3mm (6/30/26); pipeline >$700mm ACV;
  "four new major network contracts in 1H26, >$40mm total ACV". 81.5mm basic shares, cash $335.9mm, no debt.
- Margin triangle: if services = 72% at 26% GM, implied software GM ≈ 76%. If services = 60%, implied software GM ≈ 61%.

## Partial finds from the aborted run (keep)

- Pierce Transit (WA) "Runner" Contract 1750 — turnkey (Via supplies vehicles + drivers, per vehicle hour, "no capital costs"):
  $3.9mm (2023) → $7.1mm NTE (2025) → 2026-06-08 board extended by $15mm to $22.1mm NTE through 2029-06-30 (post-Bleecker);
  2025 agency cost $90/service hour, $48/boarding; 983 → 1,172 weekly hours. Source: piercetransit.org 2026-06-08 BOC agenda packet.
- LA Metro: Spare Labs awarded software 2025-03-04 (PS124278(2)); Via/NoMad RSH bid $82.35 vs competitors $101.44–147.88
  (MV, Southland, Circuit); July-2025 blended cost/RSH $82.40, cost/trip $24.90; first-year N+S funding $11.95mm for rest of FY25.
  Source: https://datamade-metro-pdf-merger.s3.amazonaws.com/2025-0473.pdf and Metro board reports.

## Known/likely programs by region

Northeast: NJ Transit MicroLink (Monmouth/Bergen, 4/2026), Jersey City Via, Newark Go, NYC DOE school-bus routing,
Montgomery County MD Ride On Flex, DART Connect (DE), CTtransit microtransit, Green Mountain Transit MyRide (VT), WMATA.
Southeast: Mobile AL, Baldwin County AL, Hampton Roads Transit, Wilson NC RIDE, MARTA Reach, Ride Gwinnett, Savannah,
Miami-Dade GO Connect, Sarasota Breeze OnDemand, Palm Tran Go Glades, West Palm Beach/Beep AV (2026), JTA, Hillsborough/HART,
CARTA GO (Chattanooga), Nashville WeGo Link, Rock Region METRO.
Midwest: Met Council Metro micro, Milwaukee MCTS, Springfield OH, COTA//Plus, Sioux Falls, KC RideKC, Des Moines DART, Pace.
TX/SW/Mountain: Arlington TX, Trinity Metro ZIPZONE, DART GoLink, CapMetro Pickup, Houston METRO, UTA On Demand,
RTC Southern Nevada, Denver RTD, Downtowner mountain towns (Aspen/RFTA, Park City, Jackson, Big Sky, Steamboat,
Crested Butte, Moab, Idaho Falls, Twin Falls).
West: LA Metro Micro, Palo Alto Link, Sunnyvale Beam (launched 2026-09-01), Cupertino, SacRT SmaRT Ride, Marin Connect,
King County Metro Flex, Pierce Transit Runner, Ben Franklin Transit, Tahoe/Truckee TART Connect (Downtowner).

## Technical notes

- SEC requests need `User-Agent: Kendall Wu kendall_wu@college.harvard.edu`.
- Legistar `substringof('Via',...)` over-matches; use entity names or 'Via Transportation' / 'microtransit'.
- Bash scripts print one-line summaries; results go to disk. Every model token spent on printed output is wasted.
- Paywall/gating expected: HigherGov, Springfield News-Sun, possibly the Drive folder. Leave blanks, never guess.

## Results (2026-09-20)

Deliverables are in `out/`: `findings.md` (memo), `claims_verification.md` (23 claims), `post_bleecker_analysis.md`, `via_contract_census.csv` /
`.xlsx`, `analysis_summary.md` (regenerate with `scripts/p5_analysis.py`). Census: 327 Via contract actions, 169 agencies, 38 states; 152 Turnkey /
9 Hybrid / 113 Software-only / 53 Unknown; run-rate dollars 78% Turnkey, 14% Hybrid, 2% Software-only, 7% Unknown. Post-report (after 2025-12-16):
20 actions, 12 Turnkey, 1 Hybrid, 2 Software-only, 5 Unknown.

Pipeline is rerunnable: `p1_*` enumerators -> `p2_fetch/extract/ocr/snippets/packets` -> `p3_batches` + agent shards in `shards/` ->
`p4_merge` (validation, aliases, corrections in `shards/_corrections.csv`, exclusions) -> `p5_analysis` -> `p6_export`.
Batch ledger: `shards/batches/STATUS.csv`. Tier-3 adjudications are logged with reasons in `shards/_corrections.csv`.
Known gaps: 62 app-only agencies without documents (`shards/apponly_observed.csv`), GDELT unusable (rate-limited), WARN covered 30 states with no Via hits,
NTD RY2025 (LA Metro operations) not yet published, Spare's LA Metro price and Springfield's fee exhibit not located.
