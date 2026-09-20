"""Build text/enum/appstore_for_mapping.csv: name, bundleId, dates, seller, first 500 chars of description, for agency mapping."""
import csv, json, re
from common import ENUM, RAW, get, log, session, write_csv
s = session()
ids = [r["trackId"] for r in csv.DictReader(open(ENUM / "appstore_full.csv"))]
meta = {}
for i in range(0, len(ids), 100):
    r = get(s, "https://itunes.apple.com/lookup?id=" + ",".join(ids[i:i+100]) + "&country=us")
    for a in (r.json().get("results", []) if r else []):
        meta[str(a["trackId"])] = a
(RAW / "appstore_via_apps_full_meta.json").write_text(json.dumps(list(meta.values())))
rows = []
for t in ids:
    a = meta.get(t, {})
    d = re.sub(r"\s+", " ", a.get("description") or "")[:500]
    rows.append(dict(trackId=t, name=a.get("trackName"), bundleId=a.get("bundleId"), releaseDate=(a.get("releaseDate") or "")[:10],
                     lastUpdate=(a.get("currentVersionReleaseDate") or "")[:10], seller=a.get("sellerName"), description=d))
write_csv(ENUM / "appstore_for_mapping.csv", rows, ["trackId", "name", "bundleId", "releaseDate", "lastUpdate", "seller", "description"])
log(f"with description: {sum(1 for r in rows if r['description'])}")
