"""FMCSA SAFER company-snapshot search by carrier name for each Via operating entity (fleet, drivers, insurance)."""
import re
import time
import urllib.parse

from common import ENTITY_TERMS, ENUM, RAW, get, log, session, write_csv

OUT = RAW / "safer"
OUT.mkdir(exist_ok=True)
s = session()
rows = []
for name in ENTITY_TERMS + ["Downtowner Transportation", "Downtowner App"]:
    q = urllib.parse.quote_plus(name.upper())
    url = (f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot"
           f"&query_param=NAME&query_string={q}")
    r = get(s, url, timeout=60)
    time.sleep(1.5)
    if not r or r.status_code != 200:
        log(f"{name}: status {r.status_code if r else None}")
        continue
    (OUT / f"{q}.html").write_text(r.text)
    n = 0
    for usdot, label in re.findall(r'query_string=(\d+)[^"]*"[^>]*>\s*([^<]+?)\s*<', r.text):
        rows.append(dict(search=name, carrier=label.strip(), usdot=usdot,
                         url=f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot"
                             f"&query_param=USDOT&query_string={usdot}"))
        n += 1
    single = re.search(r"USDOT Number:\s*</th>\s*<td[^>]*>\s*(\d+)", r.text)
    if single:
        rows.append(dict(search=name, carrier="(direct snapshot)", usdot=single.group(1), url=url))
        n += 1
    log(f"{name}: {n} carrier links, {len(r.text)} bytes")
write_csv(ENUM / "safer_hits.csv", rows, ["search", "carrier", "usdot", "url"])
