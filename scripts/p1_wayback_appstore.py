"""Timeline of apps on Via's App Store developer page from Wayback snapshots -> first/last seen per app (churn proxy)."""
import re
import time
import urllib.parse
from collections import defaultdict

from common import ENUM, RAW, get, log, session, write_csv

DEV = "apps.apple.com/us/developer/via-transportation-inc/id657777018"
OUT = RAW / "wayback_appstore"
OUT.mkdir(exist_ok=True)
s = session()
r = get(s, f"http://web.archive.org/cdx/search/cdx?url={DEV}*&output=json&fl=timestamp,original,statuscode"
           f"&filter=statuscode:200&collapse=timestamp:6", timeout=90)
snaps = r.json()[1:] if r else []
log(f"snapshots: {len(snaps)}")
seen = defaultdict(lambda: {"first": None, "last": None, "n": 0, "slug": None})
per_snap = []
for ts, orig, _ in snaps:
    p = OUT / f"{ts}.html"
    if p.exists():
        text = p.read_text(errors="ignore")
    else:
        r = get(s, f"http://web.archive.org/web/{ts}id_/{orig}", timeout=120)
        time.sleep(1.0)
        if not r or r.status_code != 200:
            per_snap.append(dict(ts=ts, url=orig, n_apps=None))
            continue
        text = r.text
        p.write_text(text)
    found = set(re.findall(r"/us/app/([a-z0-9\-%]+)/id(\d+)", text))
    per_snap.append(dict(ts=ts, url=orig, n_apps=len(found)))
    for slug, tid in found:
        e = seen[tid]
        e["slug"] = urllib.parse.unquote(slug)
        e["first"] = min(e["first"] or ts, ts)
        e["last"] = max(e["last"] or ts, ts)
        e["n"] += 1
write_csv(ENUM / "appstore_snapshots.csv", per_snap, ["ts", "url", "n_apps"])
rows = [dict(trackId=t, slug=e["slug"], first_seen=e["first"], last_seen=e["last"], n_snapshots=e["n"]) for t, e in seen.items()]
write_csv(ENUM / "appstore_timeline.csv", sorted(rows, key=lambda x: x["first_seen"] or ""),
          ["trackId", "slug", "first_seen", "last_seen", "n_snapshots"])
