# Implementing the RPM inside "KW VIA MODEL.xlsx": build plan (2026-09-21)

Target workbook: `~/Downloads/KW VIA MODEL.xlsx` (132 KB; 7 sheets: Cover, WACC and Reverse DCF (KW), Summary, Revenue Build (KW), Three Statements (KW),
DCF + EPS (KW), Street Consensus). Work happens on a copy in `~/Documents/VIA/model/`; the Downloads original is never overwritten.

## What the workbook looks like today (from targeted probes, not a full dump)
- Period columns are identical on every model sheet: C FY2023A, D FY2024A, E-H 1Q25A-4Q25A, I FY2025A, J-K 1Q26A-2Q26A, L-M 3Q26E-4Q26E, N FY2026E,
  O-R 1Q27E-4Q27E, S FY2027E, T-AA FY2028E-FY2035E; AB holds notes. Row 3 = Historical/Projected bar, row 4 = period labels, col A labels (width 54), col B units.
- Colour legend on the Cover: blue = reported input, red = assumption, black = formula, green = link to another sheet. Font Garamond on KW-built cells.
- Revenue Build (KW): geography rows 8/12/16 grow off red YoY inputs, but Total Revenue (row 20) grows off its own hardcoded 26.7% and the geographies do
  not sum to it. Customers (row 30) grow off a hardcoded 20%. These are placeholders the new engines replace.
- Three Statements (KW): revenue row 7 links to Revenue Build row 20; cost of revenue row 10 = revenue x a hardcoded 59% (row 11); SBC = 11.5% of revenue;
  balance sheet, cash flow, DCF and Reverse DCF all flow from rows 7-13.
- Cross-sheet dependencies that must not move: Revenue Build row 20 (14 cells in Three Statements) and row 30 (8 cells in Summary); Three Statements rows
  7-13 (DCF 13 cells, WACC 12, Summary 16, Street 5, Revenue Build 25). Nothing else references the Revenue Build.
- No charts, images, data validation, conditional formatting, array or dynamic-array formulas anywhere: an openpyxl round trip is safe. Six hyperlinks on
  the Cover are preserved by openpyxl.
- LibreOffice is installed (`/opt/homebrew/bin/soffice`), so formulas can be recalculated headlessly for verification without opening Excel.

## Build principles
1. Never insert or delete rows or columns in an existing sheet: openpyxl does not rewrite cross-sheet references, so an insert silently breaks the DCF.
   New content lives on new sheets or below the last used row of an existing sheet; existing cells are re-pointed by writing new formulas into them.
2. Formulas stay live. Data tabs hold values (blue) with a source column; engines hold formulas (black) and assumptions (red); links across sheets are green.
3. Only functions LibreOffice and Excel both evaluate identically: INDEX/MATCH, SUMIFS, SUMPRODUCT, IF, MIN/MAX, EDATE, DATE, ROUND. No XLOOKUP, LET,
   FILTER, dynamic arrays or Excel what-if Data Tables (openpyxl cannot author them and LibreOffice will not recalculate them); scenario grids are explicit formulas.
4. Engines are annual (FY2024A-FY2030E explicit, FY2031E-FY2035E fade inputs). Quarterly cells 3Q26E-4Q27E are derived: FY2026E less 1H26A split by
   the 2025 3Q/4Q shares; 2027 quarters = FY2027E x 2025 quarterly shares. This is an approximation and is labelled as one.
5. Every number that came from the census, NTD or filings carries its source in the notes column or the data tab; the design doc section is cited.

## Steps
| # | Step | Output | Limitation to manage |
|---|---|---|---|
| 0 | Copy the workbook to `model/KW VIA MODEL.xlsx`; keep `model/KW VIA MODEL v1 baseline.xlsx` untouched; recalc the baseline with LibreOffice and record key outputs (revenue, GM, adj. EBITDA, DCF value per share) for a before/after diff | baseline file + `model/baseline_outputs.csv` | openpyxl drops cached values; recalculation is required before any value can be read back |
| 1 | Data tabs written by script from repo CSVs: `Data - Filings` (anchors table), `Data - Contracts` (~85 operations rows: agency, entity, scope, labor-only flag, start, end, base value, basis, haircut, funding tag, source URL), `Data - NTD` (26 agencies x RY2019-24, VOMS, fares retained), `Data - Hazards` (8 survival cells, funding exposure), `Data - Rates` (OMNIA, hourly rates, $153k per vehicle-year) | 5 value-only sheets with a "generated from / on" stamp | snapshots; refresh by re-running the script, not by editing cells |
| 2 | `Segment Split (KW)`: anchors + services GM input (26%, cases 22/30) -> services and software revenue 2023A-2025A and 1H26A; implied software GM check; shares | formulas | the split ties to totals by construction; only its implications are testable |
| 3 | `Contract Layer (KW)`: one formula row per contract, FY2024A-FY2030E: base x (1+escalator)^n x survival(funding tag, year) less downsell, zero after termination or term end unless renewal flag; blocks for new wins (vehicle-equivalents x $153k x ramp), Downtowner, Germany, other international, and an "Other US services" plug = Segment Split US services less documented layers for 2024A/2025A, grown at the documented layer's organic rate | ~110 formula rows | NTD is agency-fiscal-year; RY2025 arrives Oct 2026; the plug can go negative if services GM is really above 26%, and the Checks tab must show that rather than hide it |
| 4 | `Software Engine (KW)`: residual base; net logo growth (5%-7% base, 9% bull), price/upsell, churn (3%-4%); named accounts with hazards; implied average ACV vs documented $43k | formulas | software customer count is derived, not disclosed |
| 5 | Re-wire `Revenue Build (KW)`: rows 8/12/16 annual cells link to the engines (green); quarterly cells derived per principle 4; row 20 = SUM of geographies; rows 9/13/17/21 become computed growth; FY2031E-FY2035E keep red fade inputs; row 30 customers links to the engines' customer path | existing sheet, same row positions | the old red growth inputs are overwritten; the 26.7% hardcode disappears |
| 6 | `Margin Bridge (KW)`: segment shares x segment GM (services 26.0/25.5/25.0, software 75) + implementation-fee effect -> blended GM by period; historical rows compare mix-implied to reported GM (1Q26 39%, 2Q26 41%); Three Statements row 11 links to 1 - blended GM (green), replacing the 59% hardcodes | new sheet + 20 re-pointed cells | changes flow through the balance sheet, DCF and Reverse DCF; the before/after diff from step 0 documents the move |
| 7 | `Growth Bridge (KW)`: YoY $ change by driver and by macro tag; share of growth from one-off or expiring sources | formulas | tags are judgments recorded per contract in `Data - Contracts` |
| 8 | `SOTP (KW)`: segment gross profit x multiples (red) + cash - debt, per share vs $27.98; market-implied software multiple; explicit scenario grid (2027 growth x services GM x software multiple) | formulas | no Data Table; the grid recomputes the key lines inline |
| 9 | `Checks (KW)`: reconciliation to actuals, guidance 550-553, RPO 2027 cover, NTD per-agency within 25%, customer count, margin 1Q/2Q26 out-of-sample, organic 2026 growth 19%-24%, implied ACV, implied vehicle-years; each PASS/FAIL; a single flag surfaced on Cover and Summary | new sheet + 2 cells | checks are only meaningful after recalculation |
| 10 | Recalc-and-verify loop: `soffice --headless --convert-to xlsx`, read the Checks sheet with data_only=True, grep all formulas for #REF!/#NAME?/#DIV/0!, confirm historical columns of Three Statements are unchanged, iterate | verified file | each iteration costs about 1-2k tokens; keep the loop to check cells, never dump sheets |
| 11 | Style pass: Garamond, colour legend, number formats (#,##0 and 0.0%), widths (A 54, B 9, C+ 13), freeze panes, Historical/Projected bars, Cover TOC rows and hyperlinks for the new sheets | consistent workbook | copy styles from existing cells rather than restyling old sheets |
| 12 | Deliver: save `model/KW VIA MODEL.xlsx`, copy to `~/Downloads/KW VIA MODEL v2.xlsx`, commit both baseline and v2, send the file with the before/after diff | files + commit | xlsx is binary in git; one commit per version with a changelog line |

## Token and tooling limits, stated plainly
- Reading: a full cell dump of this workbook (about 3,700 formulas and 2,400 values) would cost on the order of 150k-300k tokens. The probes used so far
  cost about 15k. Rule: read only header rows, label columns and a few formula cells per sheet; never print whole sheets.
- Writing: cost scales with script length, not cell count. Six scripts of 100-250 lines each is roughly 40k-60k tokens for the whole build.
- Verification: reading 30-40 check cells after a LibreOffice recalc is about 1-2k tokens per iteration.
- openpyxl: preserves formulas, styles, merges, freeze panes and hyperlinks; loses cached values (recomputed on open or by LibreOffice); cannot create
  what-if Data Tables or charts we would want to keep; does not adjust references on row insertion.
- LibreOffice: evaluates the function set in principle 3 identically to Excel; a formula Excel accepts but LibreOffice does not would show as #NAME? in the loop.
- Data: NTD report year is the agency fiscal year; RY2025 is not yet published; services GM is an assumption bounded 20%-32%; Downtowner revenue is
  undisclosed; the software customer count is derived. The workbook carries each as a labelled input, not a buried constant.
