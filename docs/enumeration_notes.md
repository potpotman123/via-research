# Enumeration notes (2026-09-20)

## Apple App Store, developer Via Transportation, Inc. (artistId 657777018)
- Lookup API returned 200 apps and hit the cap; true count is somewhat higher. Data: `raw/appstore_via_apps_us_2026-09-20.json`, `text/appstore_via_apps_us_2026-09-20.csv`.
- Rough hand bucketing of the 200 names:
  - Clearly non-US (exclude): Abu Dhabi Link, Ajman VOD, BC Transit OnDemand, Dubai Bus on Demand, Rekab Solutions Company. Uncertain origin: MobiliD, Via2G, Mountain Climber by Via, Yellow Zone.
  - Via's own / private / non-public-sector: Via Driver, Downtowner (ONE app covers all ~94 Downtowner towns), Field Trips, May Mobility, Shuttle - powered by Via, Slidr Rides, Second Line Transit, Bayview Shuttle. Uncertain: Shuttle Connection, NTS (Horizons), GBM Transit, FirstTracks, Evening Shuttle, Zip Shuttle, Peery Park Rides.
  - Universities (in scope): ASOSU SafeRide, ECU Ride, EagleExpress Marquette, FSU Safe Ride, Harvard Van, NYU Safe Ride, NU Transit, UWYO SafeRide, Terp Ride, UTA Mav Mover, Stevens Shuttle, Go WakeForest. Uncertain: SpartaGo, HOWL-A-RIDE, Ride the GOAT.
  - Same customer, two apps: HRT Paratransit / Hampton Roads Transit OnDemand; MicroLink / MicroLink powered by NJT; WRTA On Demand / WRTA Rider; MICRO Arlington / Arlington Transportation.
  - Net: roughly 170–180 distinct US public-sector customers with a currently published branded app. NYC School Bus (NYC DOE) is present.
- Fields worth using: `releaseDate` (launch proxy), `currentVersionReleaseDate` (still maintained), `bundleId` (agency slug), description (often names operator/agency).

## Wayback coverage of the developer page
- 46 distinct year-months with snapshots, 2019-06 through 2026-09. Diffing app lists across snapshots gives add/remove dates (churn). Caveat: the developer web page itself may truncate; verify per snapshot.

## Google Play
- `google_play_scraper` (installed version) has no `developer()` function. The developer web page `play.google.com/store/apps/developer?id=Via+Transportation+Inc.` renders only 20 app IDs server-side; the rest lazy-load. Needs a Playwright scroll in Phase 1.

## Reconciliation to 847 reported customers (6/30/26)
- ~175 US branded on-demand deployments (Apple, current)
- + ~94 Downtowner towns (one app; enumerate from Downtowner's own city list)
- + Remix planning-software customers (Remix reported 350+ cities at the 2021 acquisition; software-only by construction; enumerate from Remix site / Wayback)
- + international customers (out of scope)
- ≈ 847. Rough, but it says the branded on-demand set is where turnkey dollars live, and the rest is mostly software by construction or Downtowner turnkey.

## What the list does NOT cover
- Churned deployments (use Wayback diff, NTD contractor table, Legistar sweep)
- Paratransit software with no rider app, phone-booked (Legistar sweep, RFP databases)
- Apps published under an agency's own developer account rather than Via's
- Remix and Downtowner (separate lists)
