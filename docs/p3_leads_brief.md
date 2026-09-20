# P3 leads brief (local-cache pass, no web)

You receive a batch of target_ids for app-only Via customers. For each, `text/enum/p3_leads.csv` lists Via press releases
(src=via_news, with date, title, url and a lead paragraph) and Google News headlines (src=gnews) that mention the agency,
program, app or city. The full press-release HTML is cached in `raw/via_news/` (file names are the URL slug); read it only if the
lead paragraph is not enough to date the action and describe who operates the service.

Apply `docs/classification_brief.md` column rules. Write rows ONLY from what the leads say:
- A launch or expansion announcement is a `pilot` (if called a pilot) or `award` row dated by the announcement date, source_type=news,
  confidence low or medium, source_url_1 = the press release URL.
- scope_type from explicit language only: "Via will provide/operate ... vehicles and drivers", "Via-operated", "turnkey" -> Turnkey;
  "operated by <agency or its contractor>", "using <agency>'s drivers/vehicles", "powered by Via" with the agency running service -> Software-only;
  otherwise Unknown. Fill drivers_supplied_by / vehicles_supplied_by accordingly.
- Numbers only if stated in the lead or cached page (fleet size, fares, grant amounts). Never infer contract values from news.
- Headlines about budget cuts, service ending, competitor selection or council votes become rows with contract_action
  termination / budget-exclusion / competitor-award / other, dated by the headline date, confidence low.
- Ignore leads that are false matches (a different city with the same word, scooters, unrelated "Via").
- If a target's leads are all false matches, write no row and list the target as no_valid_lead.

Output: append to your shard `shards/<batch_name>.csv` (header from `shards/HEADER.csv`), one row per action, using Python csv.
Return only: `targets: N; rows: R; no_valid_lead: K`
