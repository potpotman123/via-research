"""Fetch Via's own news/press pages from the sitemap; extract title, publish date, first paragraph -> text/enum/via_news.csv"""
import csv, re, html, time
from concurrent.futures import ThreadPoolExecutor
from common import ENUM, RAW, get, log, session, write_csv
urls = [r["url"] for r in csv.DictReader(open(ENUM / "sitemap_ridewithvia.csv")) if re.search(r"/(news|case-study|product-updates)/[^/]+/?$", r["url"])]
log(f"{len(urls)} news/case-study urls")
s = session(); OUT = RAW / "via_news"; OUT.mkdir(exist_ok=True)
def one(u):
    r = get(s, u, tries=2, timeout=60); time.sleep(0.3)
    if not r or r.status_code != 200: return dict(url=u, status=r.status_code if r else None)
    t = r.text; (OUT / (re.sub(r"[^a-z0-9]+", "_", u.lower())[-120:] + ".html")).write_text(t)
    title = re.search(r"<title>(.*?)</title>", t, re.S); h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    date = (re.search(r'property="article:published_time" content="([^"]+)"', t) or re.search(r'"datePublished"\s*:\s*"([^"]+)"', t)
            or re.search(r"<time[^>]*datetime=\"([^\"]+)\"", t) or re.search(r"<time[^>]*>([^<]+)</time>", t))
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    paras = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p))).strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)]
    paras = [p for p in paras if len(p) > 80]
    return dict(url=u, status=200, section=u.split("/")[3], title=html.unescape(re.sub(r"<[^>]+>", "", (h1 or title).group(1))).strip() if (h1 or title) else "",
                date=(date.group(1)[:10] if date else ""), lead=" ".join(paras[:2])[:700])
rows = []
with ThreadPoolExecutor(4) as ex:
    for i, r in enumerate(ex.map(one, urls)):
        rows.append(r)
        if i % 100 == 0: log(f"{i}/{len(urls)}")
write_csv(ENUM / "via_news.csv", rows, ["url", "status", "section", "title", "date", "lead"])
ok = [r for r in rows if r.get("status") == 200]; dated = [r for r in ok if r.get("date")]
log(f"ok {len(ok)}, with date {len(dated)}, post-2025-12-16: {sum(1 for r in dated if r['date'] > '2025-12-16')}")
