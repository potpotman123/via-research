"""Full list of apps under Via's App Store developer account (artistId 657777018).
The lookup API caps at 200. Try the amp-api catalog endpoint using the page's media token; fall back to HTML links."""
import json
import re
import urllib.parse

from common import ENUM, RAW, get, log, session, write_csv

DEV_ID = "657777018"
DEV_URL = f"https://apps.apple.com/us/developer/via-transportation-inc/id{DEV_ID}"
s = session()
apps = {}

# 1. lookup API (cap 200)
r = get(s, f"https://itunes.apple.com/lookup?id={DEV_ID}&entity=software&limit=200&country=us")
for a in (r.json().get("results", []) if r else []):
    if a.get("wrapperType") == "software":
        apps[str(a["trackId"])] = dict(trackId=str(a["trackId"]), name=a["trackName"], bundleId=a.get("bundleId"),
                                       releaseDate=a.get("releaseDate"), lastUpdate=a.get("currentVersionReleaseDate"),
                                       source="lookup")
log(f"lookup API: {len(apps)}")

# 2. developer page HTML: links + media token
html = ""
r = get(s, DEV_URL + "?see-all=i-phone-apps")
if r and r.status_code == 200:
    html = r.text
    (RAW / "appstore_dev_page_seeall.html").write_text(html)
for slug, tid in set(re.findall(r"/us/app/([a-z0-9\-%]+)/id(\d+)", html)):
    if tid not in apps:
        apps[tid] = dict(trackId=tid, name=urllib.parse.unquote(slug).replace("-", " "), bundleId=None,
                         releaseDate=None, lastUpdate=None, source="html")
log(f"after HTML links: {len(apps)}")

token = None
m = re.search(r'name="web-experience-app/config/environment"\s+content="([^"]+)"', html)
if m:
    try:
        env = json.loads(urllib.parse.unquote(m.group(1)))
        token = env.get("MEDIA_API", {}).get("token")
    except Exception as e:  # noqa: BLE001
        log(f"env parse failed: {e}")
log(f"media token: {'yes' if token else 'no'}")

# 3. amp-api, paginated
if token:
    h = {"Authorization": f"Bearer {token}", "Origin": "https://apps.apple.com", "Referer": DEV_URL}
    url = f"https://amp-api.apps.apple.com/v1/catalog/us/developers/{DEV_ID}/apps?platform=web&limit=100&l=en-US"
    n = 0
    while url and n < 40:
        r = get(s, url, headers=h)
        if not r or r.status_code != 200:
            log(f"amp-api status {r.status_code if r else None}: {(r.text[:200] if r else '')}")
            break
        d = r.json()
        for a in d.get("data", []):
            at = a.get("attributes", {})
            tid = str(a.get("id"))
            prev = apps.get(tid, {})
            apps[tid] = dict(trackId=tid, name=at.get("name") or prev.get("name"), bundleId=at.get("bundleId") or prev.get("bundleId"),
                             releaseDate=at.get("releaseDate") or prev.get("releaseDate"), lastUpdate=prev.get("lastUpdate"),
                             source=(prev.get("source", "") + "+amp").lstrip("+"))
        nxt = d.get("next")
        url = ("https://amp-api.apps.apple.com" + nxt) if nxt else None
        n += 1
    log(f"after amp-api: {len(apps)} ({n} pages)")

# 4. fill missing metadata via lookup by id
missing = [t for t, a in apps.items() if not a.get("bundleId")]
for i in range(0, len(missing), 100):
    r = get(s, "https://itunes.apple.com/lookup?id=" + ",".join(missing[i:i + 100]) + "&country=us")
    for a in (r.json().get("results", []) if r else []):
        t = str(a.get("trackId"))
        if t in apps:
            apps[t].update(name=a.get("trackName"), bundleId=a.get("bundleId"), releaseDate=a.get("releaseDate"),
                           lastUpdate=a.get("currentVersionReleaseDate"))

rows = sorted(apps.values(), key=lambda x: (x["name"] or "").lower())
write_csv(ENUM / "appstore_full.csv", rows, ["trackId", "name", "bundleId", "releaseDate", "lastUpdate", "source"])
