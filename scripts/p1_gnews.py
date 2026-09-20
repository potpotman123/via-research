"""Google News RSS (no key) for Via entity / competitor queries -> text/enum/gnews.csv (recent ~100 items per query)."""
import re, time, html, urllib.parse
from common import ENUM, get, log, session, write_csv
Q = ['"River North Transit"', '"Via Transportation" microtransit', '"Via Transportation" contract', '"Via Transportation" paratransit',
     '"Via Transportation" transit agency', '"NoMad Transit"', '"Spare Labs" transit', '"RideCo" transit agency', 'microtransit "Via" council approves',
     'microtransit "Via" board approves contract', '"powered by Via" transit', '"Downtowner" shuttle town', '"Remix" transit planning software Via']
s = session(); rows = []
for q in Q:
    r = get(s, "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en", timeout=60); time.sleep(2)
    if not r or r.status_code != 200: log(f"{q}: {r.status_code if r else None}"); continue
    items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
    for it in items:
        g = lambda tag: (re.search(f"<{tag}>(.*?)</{tag}>", it, re.S) or re.search(f"<{tag}[^>]*>(.*?)</{tag}>", it, re.S))
        t, l, d, src = g("title"), g("link"), g("pubDate"), g("source")
        rows.append(dict(query=q, pubDate=d.group(1).strip() if d else "", title=html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", t.group(1))).strip() if t else "",
                         source=html.unescape(re.sub(r"<[^>]+>", "", src.group(1))).strip() if src else "", link=l.group(1).strip() if l else ""))
    log(f"{q}: {len(items)}")
seen, out = set(), []
for x in rows:
    k = x["title"].lower()
    if k not in seen: seen.add(k); out.append(x)
write_csv(ENUM / "gnews.csv", out, ["query", "pubDate", "title", "source", "link"])
