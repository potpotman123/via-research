"""GDELT DOC 2.0: US news articles mentioning Via entities or competitors in a transit context (launches and losses)."""
import time

from common import ENUM, get, log, session, write_csv

QUERIES = [
    '"River North Transit"', '"NoMad Transit"', '"Crosby Street Transit"',
    '"Via Transportation" microtransit', '"Via Transportation" contract', '"Via Transportation" paratransit',
    '"Via Transportation" transit', '"Remix Technologies"', '"Downtowner" shuttle',
    '"Spare Labs" transit', '"RideCo" transit', 'ridewithvia',
]
s = session()
rows = []
for q in QUERIES:
    r = get(s, "https://api.gdeltproject.org/api/v2/doc/doc",
            params={"query": q, "mode": "artlist", "maxrecords": 250, "format": "json",
                    "startdatetime": "20170101000000", "enddatetime": "20260920235959", "sourcecountry": "US"},
            timeout=120)
    time.sleep(6)
    if not r or r.status_code != 200:
        log(f"{q}: status {r.status_code if r else None} {(r.text[:120] if r else '')}")
        continue
    try:
        arts = r.json().get("articles", [])
    except Exception:  # noqa: BLE001
        log(f"{q}: non-JSON {r.text[:120]!r}")
        continue
    for a in arts:
        rows.append(dict(query=q, seendate=a.get("seendate"), title=a.get("title"), domain=a.get("domain"), url=a.get("url")))
    log(f"{q}: {len(arts)}")
seen, out = set(), []
for x in rows:
    if x["url"] not in seen:
        seen.add(x["url"])
        out.append(x)
write_csv(ENUM / "gdelt_articles.csv", sorted(out, key=lambda x: x["seendate"] or ""), ["query", "seendate", "title", "domain", "url"])
