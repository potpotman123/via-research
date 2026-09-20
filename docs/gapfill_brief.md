# Gap-fill brief (Phase 2/3 for targets with no documents in the corpus)

You are given a batch of target_ids. Each is a US public-sector customer of Via Transportation (NYSE: VIA) for which we
have NO procurement document yet. Your job, per target: find the governing contract action(s) in primary sources, save the
documents, and write census rows. Everything you write must cite a URL you actually opened.

Read `docs/classification_brief.md` first; its column rules, scope rubric and traps apply to every row you write.

## Inputs
- `text/enum/targets.csv` — your targets (look up each target_id). Columns include agency, city, state, program_name,
  appstore_apps (the branded app), first/last_known_year, status_hint, notes (may already cite a post-2025-12-16 news item).
- Local caches to check BEFORE searching the web (free):
  - `text/enum/via_news.csv` (Via press releases with date/title/lead) and `raw/via_news/*.html` — grep for the agency/program.
  - `text/enum/gnews.csv` — recent local headlines (links are Google redirect URLs; search the headline title to reach the article).
  - `text/enum/ntd_contractual_hits.csv` — if the agency is there, Via is a purchased-transportation contractor (turnkey) with dollars by year.
  - `text/enum/legistar_clients.csv` — 306 Legistar slugs with open APIs. If the agency's city/county is a client, query
    `https://webapi.legistar.com/v1/<slug>/matters?$filter=substringof('Via',MatterTitle)` (also try 'River North', 'microtransit',
    the program name) and pull attachments from `/matters/<MatterId>/attachments`.

## Search discipline (tokens are the budget)
- At most 4 WebSearch calls per target. Good queries: `"<agency>" Via microtransit contract`, `"<agency>" "River North Transit"`,
  `"<program name>" council agenda Via`, `"<agency>" Via "not to exceed"`, `"<agency>" microtransit RFP award`.
- Prefer agenda systems: legistar.com, granicus.com, civicclerk.com, boarddocs.com, primegov.com, novusagenda.com, escribemeetings.com,
  the agency's own board-packet PDFs. Then agency press releases. Then local news.
- PDFs: download with curl into `raw/cache/gap/<target_id>_<n>.pdf` (use a browser User-Agent), then run
  `/Users/kwu/Documents/VIA/.venv/bin/python scripts/gap_pdf.py <pdf> --terms "Via,River North,NoMad,Remix,Downtowner,\$,per hour,not to exceed"`
  which prints only matching pages. Never read a whole PDF. Never use WebFetch on a PDF.
- HTML pages (agenda item pages, news): WebFetch is fine. Save nothing from WebFetch as a number unless the page shows it verbatim.
- If a site returns 403 to curl, note it and move on; do not retry more than once.

## Output
1. Rows: append to your shard `shards/<batch_name>.csv` (header copied from `shards/HEADER.csv`) using Python csv. One row per
   contract action found. `source_url_1` = the document URL (or article URL for news-only rows, with source_type=news and
   confidence low/medium). Fill `signed_after_2025_12_16` from the approval date.
2. Log: append one line per target to `text/enum/gap_log.csv` (create with header if missing):
   `target_id,agency,outcome,docs_found,rows_written,queries_used,notes`
   where outcome is one of `found_contract` | `found_news_only` | `nothing_found`, docs_found is a `;`-separated list of URLs,
   queries_used is the count of WebSearch calls, notes is one line (e.g., "agenda system is Granicus but search returned no Via items").

## What matters most
- Who supplies drivers and vehicles, and the billing basis (per hour vs subscription). Quote the line.
- Ceilings vs annual amounts, exactly as written. Never derive.
- Post-2025-12-16 actions (awards, expansions, extensions, terminations, budget cuts, competitor awards) with their approval dates.
- The signing entity (River North Transit LLC, NoMad Transit LLC, Via Mobility LLC, Remix Technologies LLC, a Downtowner LLC).

## Traps
"Via Mobility Services" (Boulder CO nonprofit), "VIA Metropolitan Transit" (San Antonio agency), "Via Rail" (Canada), "Downtowner Saloon",
"Via" as a preposition in agenda titles. A rider app existing does not make a contract turnkey.

## Return message
Only: `targets: N; rows: R; found_contract: a; found_news_only: b; nothing_found: c`
