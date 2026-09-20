"""Discover Legistar clients (Common Crawl host index + seeds), verify the API, sweep matter titles for entity terms,
then list attachments for every entity hit. substringof() is case-insensitive under Legistar's SQL collation; tolower() 500s."""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from common import COMPETITOR_TERMS, ENTITY_TERMS, ENUM, get, log, session, write_csv

s = session()
SEEDS = """metro milwaukeecounty baldwincountyal mobile arlingtontx arlington nyc sfmta sacrt denver rtd kingcounty seattle pierce
spokane columbus cota chattanooga nashville miamidade hillsborough palmbeach jta houston dallas dart capmetro sanantonio utah uta
lasvegas rtcsnv phoenix valleymetro mesa chandler jerseycity newark njtransit montgomerycountymd wilsonnc charlotte raleigh gwinnett
marta atlanta kansascity kcmo ridekc desmoines sanjose vta paloalto sunnyvale cupertino marin sonoma-county sfgov longmont boulder
portland trimet salem eugene richmondva grtc hampton norfolk virginiabeach gohrt tampa tampagov orlando lynx sarasota stpete pinellas
broward leecounty collier duval tallahassee omaha lincoln minneapolis stpaul metrocouncil madison milwaukee cincinnati cleveland toledo
dayton springfieldoh indianapolis fortwayne louisville lexington memphis littlerock rockregion tulsa okc norman albuquerque elpaso
austin fortworth plano grandprairie sugarland tyler lubbock sandiego sandiegocounty mts riverside sanbernardino omnitrans orangecounty
octa longbeach torrance glendale pasadena westcovina rosemead visalia tulare merced fresno bakersfield stockton modesto westsacramento
yolo solano napa santacruz monterey oakland alamedactc actransit contracosta sanmateo samtrans redding chico eureka reno rtcwashoe boise
vrt missoula billings bozeman cheyenne laramie casper spokanecounty tacoma everett snohomish kitsap olympia bft yakima wenatchee
bellingham anchorage honolulu maui lacity lacounty lametro sdmts sfbart bart sacramento sacramentocounty fresnocounty kerncounty
cityofmesa tempe scottsdale glendaleaz peoria tucson pima saltlakecity slc ogden provo stgeorge jackson jacksonwy tetoncounty parkcity
summitcounty aspen pitkincounty basalt carbondale glenwoodsprings steamboat crestedbutte gunnison leadville moab grandcounty idahofalls
twinfalls bigsky savannah chatham cobb cobbcounty gwinnettcounty dekalb fulton clayton henrycounty cherokee macon augusta columbusga
wilmington newcastle delaware dover kent sussex trenton camden passaic bergen monmouth middlesex essex hudson union morris ocean
suffolkcountyny nassau westchester putnam rockland dutchess orangecountyny ulster oswego syracuse rochester buffalo albany yonkers
newhaven hartford stamford norwalk bridgeport waterbury newlondon providence warwick worcester springfieldma lowell cambridge boston
burlingtonvt montpelier manchester nashua concord portlandme bangor""".split()


def cc_hosts():
    hosts = set()
    r = get(s, "https://index.commoncrawl.org/collinfo.json", timeout=60)
    if not r:
        return hosts
    for coll in r.json()[:2]:
        cid = coll["id"]
        base = f"https://index.commoncrawl.org/{cid}-index?url=*.legistar.com&output=json&fl=url"
        r = get(s, base + "&showNumPages=true", timeout=180)
        try:
            pages = int(r.json().get("pages", 0))
        except Exception:  # noqa: BLE001
            pages = 0
        log(f"{cid}: {pages} index pages")
        for p in range(min(pages, 40)):
            r = get(s, base + f"&page={p}", timeout=300)
            if not r or r.status_code != 200:
                continue
            for line in r.text.splitlines():
                try:
                    u = json.loads(line)["url"]
                except Exception:  # noqa: BLE001
                    continue
                m = re.match(r"https?://([a-z0-9\-]+)\.legistar\.com", u, re.I)
                if m:
                    hosts.add(m.group(1).lower())
            time.sleep(0.5)
    return hosts


hosts = cc_hosts()
log(f"common crawl hosts: {len(hosts)}")
hosts |= set(SEEDS)
hosts -= {"www", "webapi", "help", "support", "api", "legistar", "ftp", "mail", "cdn", "static"}
log(f"candidate clients: {len(hosts)}")


def check(c):
    r = get(s, f"https://webapi.legistar.com/v1/{c}/bodies?$top=1", tries=1, timeout=30)
    return c, (r.status_code if r else None)


valid = []
with ThreadPoolExecutor(8) as ex:
    for c, st in ex.map(check, sorted(hosts)):
        if st == 200:
            valid.append(c)
log(f"clients with open API: {len(valid)}")
write_csv(ENUM / "legistar_clients.csv", [dict(client=c) for c in sorted(valid)], ["client"])

TERMS = ENTITY_TERMS + COMPETITOR_TERMS + ["microtransit"]
FIELDS = ["client", "term", "MatterId", "MatterFile", "MatterTitle", "MatterTypeName", "MatterStatusName",
          "MatterIntroDate", "MatterPassedDate", "MatterBodyName", "url"]


def sweep(c):
    out = []
    for t in TERMS:
        r = get(s, f"https://webapi.legistar.com/v1/{c}/matters",
                params={"$filter": f"substringof('{t}',MatterTitle)", "$top": 500}, tries=2, timeout=90)
        if r is None or r.status_code != 200:
            continue
        try:
            items = r.json()
        except Exception:  # noqa: BLE001
            continue
        for m in items:
            out.append(dict(client=c, term=t, MatterId=m.get("MatterId"), MatterFile=m.get("MatterFile"),
                            MatterTitle=(m.get("MatterTitle") or "")[:400].replace("\n", " ").replace("\r", " "),
                            MatterTypeName=m.get("MatterTypeName"), MatterStatusName=m.get("MatterStatusName"),
                            MatterIntroDate=m.get("MatterIntroDate"), MatterPassedDate=m.get("MatterPassedDate"),
                            MatterBodyName=m.get("MatterBodyName"),
                            url=f"https://{c}.legistar.com/LegislationDetail.aspx?ID={m.get('MatterId')}"))
    return out


hits = []
with ThreadPoolExecutor(6) as ex:
    futs = {ex.submit(sweep, c): c for c in valid}
    for i, f in enumerate(as_completed(futs)):
        hits += f.result()
        if i % 50 == 0:
            log(f"swept {i + 1}/{len(valid)} clients, hits so far {len(hits)}")
write_csv(ENUM / "legistar_hits.csv", hits, FIELDS)

keys = sorted({(h["client"], h["MatterId"]) for h in hits if h["term"] != "microtransit"})
log(f"fetching attachments for {len(keys)} entity matters")


def attachments(k):
    c, mid = k
    r = get(s, f"https://webapi.legistar.com/v1/{c}/matters/{mid}/attachments", tries=2, timeout=60)
    if not r or r.status_code != 200:
        return []
    try:
        return [dict(client=c, MatterId=mid, name=a.get("MatterAttachmentName"), url=a.get("MatterAttachmentHyperlink"))
                for a in r.json()]
    except Exception:  # noqa: BLE001
        return []


att = []
with ThreadPoolExecutor(6) as ex:
    for res in ex.map(attachments, keys):
        att += res
write_csv(ENUM / "legistar_attachments.csv", att, ["client", "MatterId", "name", "url"])
