"""Via sitemap (case studies / city pages), Downtowner site (city list), Remix customers (live + Wayback)."""
import re
from collections import Counter

from common import ENUM, RAW, get, log, session, write_csv

s = session()


def sitemap_urls(url, depth=0):
    r = get(s, url)
    if not r or r.status_code != 200 or depth > 2:
        return []
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
    if "<sitemapindex" in r.text:
        out = []
        for loc in locs:
            out += sitemap_urls(loc, depth + 1)
        return out
    return locs


for name, url in [("ridewithvia", "https://ridewithvia.com/sitemap.xml"),
                  ("downtowner", "https://ridedowntowner.com/sitemap.xml"),
                  ("remix", "https://www.remix.com/sitemap.xml")]:
    urls = sorted(set(sitemap_urls(url)))
    write_csv(ENUM / f"sitemap_{name}.csv", [dict(url=u) for u in urls], ["url"])
    c = Counter(u.split("/")[3] if len(u.split("/")) > 3 else "" for u in urls)
    log(f"{name}: sections {c.most_common(8)}")

for name, url in [("downtowner_home", "https://ridedowntowner.com/"),
                  ("remix_customers_live", "https://www.remix.com/customers"),
                  ("via_customers_live", "https://ridewithvia.com/customers")]:
    r = get(s, url)
    if r and r.status_code == 200:
        (RAW / f"{name}.html").write_text(r.text)
        log(f"{name}: {len(r.text)} bytes")
    else:
        log(f"{name}: status {r.status_code if r else None}")

for ts in ("20210601", "20220601", "20230601"):
    r = get(s, f"http://archive.org/wayback/available?url=remix.com/customers&timestamp={ts}")
    snap = (r.json().get("archived_snapshots", {}).get("closest", {}) if r else {})
    if snap.get("url"):
        raw_url = snap["url"].replace(f"/web/{snap['timestamp']}/", f"/web/{snap['timestamp']}id_/")
        r2 = get(s, raw_url, timeout=120)
        if r2 and r2.status_code == 200:
            (RAW / f"remix_customers_wayback_{snap['timestamp']}.html").write_text(r2.text)
            log(f"remix customers {snap['timestamp']}: {len(r2.text)} bytes")
