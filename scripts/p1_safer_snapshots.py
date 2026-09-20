"""Fetch FMCSA SAFER company snapshots for Via-related USDOT numbers; parse fleet, drivers, address, status."""
import csv, re, time, html
from common import ENUM, RAW, get, log, session, write_csv
KEEP = re.compile(r"NOMAD TRANSIT|CROSBY STREET|^VIA TRANSPORTATION (INC|LLC)|VIA TRANSIT (LLC|USA|TWIN)|DOWNTOWNER|PORT CITY TRANSIT LLC|TIDEWATER TRANSIT LLC|RIVER NORTH", re.I)
FIELDS = ["Legal Name", "DBA Name", "Physical Address", "Phone", "USDOT Number", "MC/MX/FF Number(s)", "Entity Type", "Operating Status",
          "Out of Service Date", "Power Units", "Drivers", "MCS-150 Form Date", "MCS-150 Mileage (Year)", "Operation Classification",
          "Carrier Operation", "Cargo Carried"]
s = session(); rows = []
seen = set()
for r in csv.DictReader(open(ENUM / "safer_hits.csv")):
    if not KEEP.search(r["carrier"]) or r["usdot"] in seen: continue
    seen.add(r["usdot"])
    url = f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={r['usdot']}"
    resp = get(s, url, timeout=60); time.sleep(1.5)
    if not resp or resp.status_code != 200:
        log(f"{r['carrier']}: status {resp.status_code if resp else None}"); continue
    t = resp.text; (RAW / "safer" / f"usdot_{r['usdot']}.html").write_text(t)
    out = dict(search_carrier=r["carrier"], usdot=r["usdot"], url=url)
    for f in FIELDS:
        m = re.search(re.escape(f) + r":?\s*(?:</a>)?\s*</th>\s*<td[^>]*>(.*?)</td>", t, re.S | re.I)
        val = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""
        out[f] = val
    # operation classification / carrier operation are checkbox tables: capture the checked labels
    for f in ("Operation Classification", "Carrier Operation"):
        m = re.search(re.escape(f) + r":.*?</th>(.*?)</table>", t, re.S | re.I)
        if m:
            labels = re.findall(r"<td[^>]*class=\"queryfield\"[^>]*>\s*X\s*</td>\s*<td[^>]*>(.*?)</td>", m.group(1), re.S | re.I)
            if labels: out[f] = "; ".join(re.sub(r"<[^>]+>", "", x).strip() for x in labels)
    rows.append(out); log(f"{out['Legal Name'] or r['carrier']}: PU {out['Power Units']}, drivers {out['Drivers']}, {out['Operating Status'][:30]}, addr {out['Physical Address'][:50]}")
write_csv(ENUM / "safer_snapshots.csv", rows, ["search_carrier", "usdot", "url"] + FIELDS)
